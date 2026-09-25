"""S-Repo stream: files of a Python repository streamed in dependency order.

Masks produced per file (over target tokens):
  xfile : first sub-token of an identifier that was DEFINED in an earlier file of the same repo
          and is NOT defined anywhere in the current file  -> only cross-document memory can help
  local : first sub-token of an identifier defined earlier in the current file        -> control

Notes on leak-freedom (plan §F):
  * a name counts as "defined earlier" only if the defining file precedes the current one in the stream
  * each occurrence is evaluated at the position that predicts its FIRST sub-token
"""
from __future__ import annotations

import ast
import io
import keyword
import os
import tokenize
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from ..runner import Doc

import builtins as _bi
_BUILTINS = set(dir(_bi))


def _py_files(root: str) -> List[str]:
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in ("tests", "test", "docs", "examples", "build", "dist", "__pycache__")]
        for f in fn:
            if f.endswith(".py") and not f.startswith("test_"):
                out.append(os.path.join(dp, f))
    return sorted(out)


def _module_name(root: str, path: str) -> str:
    rel = os.path.relpath(path, root)[:-3].replace(os.sep, ".")
    return rel[:-9] if rel.endswith(".__init__") else rel


def _defs_and_imports(src: str) -> Tuple[Set[str], Set[str]]:
    """Top-level (and class-member) definitions, and imported module names."""
    defs, imps = set(), set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return defs, imps
    def _collect(body, allow_assign=True):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defs.add(node.name)
                _collect(node.body)  # methods and class attributes
            elif allow_assign and isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        defs.add(t.id)
    _collect(tree.body)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imps.add(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imps.add(node.module)
    return defs, imps


def _name_occurrences(src: str) -> List[Tuple[str, int]]:
    """(name, char_offset) for every NAME token (excluding keywords/builtins)."""
    occ = []
    lines = src.splitlines(keepends=True)
    line_start = [0]
    for ln in lines:
        line_start.append(line_start[-1] + len(ln))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.NAME and not keyword.iskeyword(tok.string) and tok.string not in _BUILTINS:
                r, c = tok.start
                occ.append((tok.string, line_start[r - 1] + c))
    except (tokenize.TokenError, IndentationError):
        pass
    return occ


def _order_files(root: str, files: List[str]) -> List[str]:
    """Topological order by intra-repo imports; ties broken alphabetically."""
    mod2file = {_module_name(root, f): f for f in files}
    deps: Dict[str, Set[str]] = {}
    for f in files:
        try:
            src = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        _, imps = _defs_and_imports(src)
        d = set()
        for m in imps:
            # match longest prefix present in repo
            parts = m.split(".")
            for k in range(len(parts), 0, -1):
                cand = ".".join(parts[:k])
                if cand in mod2file and mod2file[cand] != f:
                    d.add(mod2file[cand]); break
        deps[f] = d
    ordered, seen, temp = [], set(), set()

    def visit(f):
        if f in seen: return
        if f in temp: return  # cycle: ignore edge
        temp.add(f)
        for g in sorted(deps.get(f, ())):
            visit(g)
        temp.discard(f); seen.add(f); ordered.append(f)

    for f in files:
        visit(f)
    return ordered


_RENAME_SKIP = {"self", "cls", "__init__", "__name__", "__file__", "__all__", "main"}


def _obfuscate_repo(files: List[str], srcs: Dict[str, str], min_name_len: int, seed: int) -> Dict[str, str]:
    """Consistently rename every repo-defined identifier (len>=min_name_len, not dunder) to a random
    identifier across ALL files of the repo. Removes pre-training memorisation of popular repos and makes
    cross-file recall impossible without memory of the defining file. Returns {path: new_src}."""
    import random, string
    rng = random.Random(seed)
    names: Set[str] = set()
    for f in files:
        d, _ = _defs_and_imports(srcs[f])
        names |= {n for n in d if len(n) >= min_name_len and not (n.startswith("__") and n.endswith("__")) and n not in _RENAME_SKIP}
    used: Set[str] = set()

    def fresh():
        while True:
            n = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(5, 9)))
            if n not in used and not keyword.iskeyword(n) and n not in _BUILTINS:
                used.add(n); return n
    mapping = {n: fresh() for n in sorted(names)}
    out = {}
    for f in files:
        src = srcs[f]
        occ = [(n, c) for n, c in _name_occurrences(src) if n in mapping]
        buf = list(src)
        for n, c in sorted(occ, key=lambda x: -x[1]):  # replace from the end to keep offsets valid
            buf[c:c + len(n)] = list(mapping[n])
        out[f] = "".join(buf)
    return out


def build_repo_stream(repo_dirs: List[str], tokenizer, max_tokens_per_file: int = 8192,
                      min_tokens_per_file: int = 64, min_name_len: int = 3, max_files_per_repo: int = 200,
                      obfuscate: bool = True, seed: int = 0, holdout_last: bool = False):
    """If holdout_last, additionally return {repo_name: Doc} where the held-out doc is the last file of the
    repo with at least 5 xfile targets (never streamed; used to measure per-repo retention)."""
    docs: List[Doc] = []
    holdouts = {}
    for root in repo_dirs:
        files = _order_files(root, _py_files(root))[:max_files_per_repo]
        srcs: Dict[str, str] = {}
        for f in files:
            try:
                srcs[f] = open(f, encoding="utf-8", errors="ignore").read()
            except OSError:
                srcs[f] = ""
        files = [f for f in files if srcs[f].strip()]
        if obfuscate:
            # per-repo RNG stream: without this, every repo draws the SAME sequence of fake names,
            # so the k-th definition of every repo maps to one shared token -- a cross-repo vocabulary
            # prior that masquerades as cross-repo memory (found 2026-09-01; invalidates earlier runs).
            import zlib as _z
            repo_seed = (_z.crc32(os.path.basename(root).encode()) ^ (seed * 2654435761)) & 0x7FFFFFFF
            srcs = _obfuscate_repo(files, srcs, min_name_len, repo_seed)
        earlier: Set[str] = set()
        for fi, path in enumerate(files):
            src = srcs[path]
            enc = tokenizer(src, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"][:max_tokens_per_file]
            offs = enc["offset_mapping"][:max_tokens_per_file]
            if len(ids) < min_tokens_per_file:
                continue
            cur_defs, _ = _defs_and_imports(src)
            # char offset -> first token index covering it
            starts = [o[0] for o in offs]
            import bisect
            xmask = [False] * len(ids)   # first occurrence in this file of an earlier-file name  (cross-doc memory)
            rmask = [False] * len(ids)   # repeated occurrences of such names                     (in-context copy)
            lmask = [False] * len(ids)   # repeated occurrences of names defined in this file      (control)
            seen_local: Set[str] = set()
            seen_x: Set[str] = set()
            for name, ch in _name_occurrences(src):
                if len(name) < min_name_len:
                    continue
                ti = bisect.bisect_right(starts, ch) - 1
                if ti < 0 or ti >= len(ids):
                    continue
                if offs[ti][0] > ch or offs[ti][1] <= ch:
                    # token boundary does not line up exactly (e.g. leading space merged) -> try next token
                    if ti + 1 < len(ids) and offs[ti + 1][0] <= ch < offs[ti + 1][1]:
                        ti += 1
                    else:
                        continue
                if name in earlier and name not in cur_defs:
                    if name in seen_x:
                        rmask[ti] = True
                    else:
                        xmask[ti] = True; seen_x.add(name)
                elif name in cur_defs and name in seen_local:
                    lmask[ti] = True
                if name in cur_defs:
                    seen_local.add(name)
            docs.append(Doc(ids=ids, name=f"{os.path.basename(root)}/{os.path.relpath(path, root)}",
                            masks={"xfile": xmask, "xrep": rmask, "local": lmask},
                            meta={"repo": os.path.basename(root), "file_idx": fi, "n_files": len(files)}))
            earlier |= {d for d in cur_defs if len(d) >= min_name_len}
        if holdout_last:
            repo = os.path.basename(root)
            mine = [d for d in docs if d.meta.get("repo") == repo]
            cands = [d for d in mine if sum(d.masks["xfile"]) >= 5]
            if cands:
                h = cands[-1]
                docs.remove(h)
                holdouts[repo] = h
    return (docs, holdouts) if holdout_last else docs
