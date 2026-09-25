"""S-Entity stream: natural-text analogue of the obfuscated repo stream.

A SESSION is one long article split into consecutive documents. Within a session, every salient
named entity (a capitalized phrase recurring >= min_count times) is consistently renamed to a
synthetic name drawn from a session-specific RNG. Masks over target tokens:

  xdoc : FIRST mention in the current doc of an entity introduced in an EARLIER doc of the session
         -> only cross-document memory (or fast weights) can predict the synthetic name
  xrep : later mentions of such entities in the same doc (in-context copy control)
  intro: mentions of entities first introduced in the current doc (control)

The last document of a session with >= min_holdout xdoc targets is HELD OUT for the lag protocol.
Contamination-free by construction: synthetic names never occur in pre-training data.
"""
from __future__ import annotations

import re
import zlib
import random
from typing import Dict, List, Set, Tuple

from ..runner import Doc

_SYL = ["ka", "ve", "lor", "min", "tas", "re", "dun", "sel", "mar", "obi", "zan", "eth",
        "qui", "fen", "ash", "bel", "cor", "dra", "gal", "hol", "ith", "jun", "kel", "lum",
        "nor", "os", "pel", "rin", "sor", "tal", "urn", "wex", "yor", "vim", "bram", "chet"]
_STOP_STARTERS = {"The", "A", "An", "In", "On", "At", "By", "For", "It", "He", "She", "They", "We",
                  "This", "That", "These", "Those", "But", "And", "Or", "As", "After", "Before",
                  "When", "While", "During", "However", "Although", "Since", "With", "From", "To", "Of"}


def _fake_name(rng: random.Random, n_words: int) -> str:
    def w():
        k = rng.randint(2, 3)
        s = "".join(rng.choice(_SYL) for _ in range(k))
        return s.capitalize()
    return " ".join(w() for _ in range(n_words))


def _find_entities(text: str, min_count: int = 4, min_len: int = 4) -> List[str]:
    """Capitalized phrases (1-3 words) recurring in the article, at least twice mid-sentence."""
    cand = re.findall(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]{2,}(?: [A-Z][a-z]{2,}){0,2})\b", text)
    counts: Dict[str, int] = {}
    for c in cand:
        if c.split()[0] in _STOP_STARTERS:
            continue
        counts[c] = counts.get(c, 0) + 1
    total = {p: len(re.findall(r"\b" + re.escape(p) + r"\b", text)) for p in counts}
    ents = [p for p in counts if len(p) >= min_len and counts[p] >= 2 and total[p] >= min_count]
    # drop phrases contained in a longer selected phrase
    ents.sort(key=len, reverse=True)
    keep: List[str] = []
    for e in ents:
        if not any(e in k for k in keep):
            keep.append(e)
    return keep


def _split_docs(text: str, tokenizer, target_tokens: int = 1200, min_tokens: int = 300) -> List[str]:
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    docs, cur, cur_n = [], [], 0
    for p in paras:
        n = len(tokenizer(p, add_special_tokens=False)["input_ids"])
        cur.append(p); cur_n += n
        if cur_n >= target_tokens:
            docs.append("\n\n".join(cur)); cur, cur_n = [], 0
    if cur and cur_n >= min_tokens:
        docs.append("\n\n".join(cur))
    return docs


def build_entity_sessions(articles: List[Tuple[str, str]], tokenizer, seed: int = 0,
                          min_docs: int = 3, max_docs: int = 12, min_holdout: int = 5,
                          max_tokens_per_doc: int = 4096):
    """articles: list of (title, text). Returns list of sessions: (stream_docs, holdout_doc_or_None)."""
    sessions = []
    for title, text in articles:
        ents = _find_entities(text)
        if len(ents) < 3:
            continue
        rng = random.Random((zlib.crc32(title.encode()) ^ (seed * 2654435761)) & 0x7FFFFFFF)
        mapping = {e: _fake_name(rng, len(e.split())) for e in ents}
        for e in sorted(mapping, key=len, reverse=True):
            text = re.sub(r"\b" + re.escape(e) + r"\b", mapping[e], text)
        fakes: Set[str] = set(mapping.values())
        raw_docs = _split_docs(text, tokenizer)
        if not (min_docs <= len(raw_docs)):
            continue
        raw_docs = raw_docs[:max_docs]
        introduced: Set[str] = set()
        docs: List[Doc] = []
        for di, dtext in enumerate(raw_docs):
            enc = tokenizer(dtext, return_offsets_mapping=True, add_special_tokens=False)
            ids = enc["input_ids"][:max_tokens_per_doc]
            offs = enc["offset_mapping"][:max_tokens_per_doc]
            starts = [o[0] for o in offs]
            import bisect
            xdoc = [False] * len(ids); xrep = [False] * len(ids); intro = [False] * len(ids)
            seen_here: Set[str] = set()
            occ = []
            for f in fakes:
                occ += [(m.start(), f) for m in re.finditer(r"\b" + re.escape(f) + r"\b", dtext)]
            for ch, f in sorted(occ):
                ti = bisect.bisect_right(starts, ch) - 1
                if ti < 0 or ti >= len(ids) or not (offs[ti][0] <= ch < offs[ti][1]):
                    continue
                if f in introduced:
                    (xrep if f in seen_here else xdoc)[ti] = True
                else:
                    intro[ti] = True
                seen_here.add(f)
            introduced |= seen_here
            docs.append(Doc(ids=ids, name=f"{title[:30]}/{di}",
                            masks={"xfile": xdoc, "xrep": xrep, "local": intro},
                            meta={"repo": title, "file_idx": di, "n_files": len(raw_docs)}))
        holdout = None
        for d in reversed(docs):
            if sum(d.masks["xfile"]) >= min_holdout:
                holdout = d; docs.remove(d); break
        if len(docs) >= min_docs - 1:
            sessions.append((docs, holdout))
    return sessions


def load_wikitext_articles(split: str = "train", max_articles: int = 400, min_chars: int = 8000):
    """WikiText-103 raw articles reconstructed from ' = Title = ' headers (needs `datasets`)."""
    from datasets import load_dataset
    ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split=split)
    arts, title, buf = [], None, []
    for line in ds["text"]:
        m = re.match(r"^ = ([^=].*?) = $", line)
        if m:
            if title and sum(len(x) for x in buf) >= min_chars:
                arts.append((title, "".join(buf)))
                if len(arts) >= max_articles:
                    break
            title, buf = m.group(1).strip(), []
        elif title is not None:
            buf.append(line)
    if title and sum(len(x) for x in buf) >= min_chars and len(arts) < max_articles:
        arts.append((title, "".join(buf)))
    return arts
