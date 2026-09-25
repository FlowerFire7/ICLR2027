#!/usr/bin/env python
"""Week 3a: proper forgetting measurement on a LONG repo stream.

Protocol (fixes the broken BWT_x of week 2):
  * the last identifier-rich file of every repo is HELD OUT (never streamed)
  * right after a repo's files have been streamed, its held-out file is scored (eval-only)  -> acc_then
  * at the end of the whole stream every held-out file is scored again                      -> acc_end
  * retention(repo) = acc_end - acc_then ; averaged over repos, weighted by xfile_n
A policy that keeps writing without protection should show acc_end < acc_then for EARLY repos.

  CUDA_VISIBLE_DEVICES=1 python scripts/week3_repo.py --model Qwen/Qwen3-0.6B-Base --repos repos200 \
      --policy persist --eta 3e-2 --out results/week3/persist.json [--alpha_norm]
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from ptt.fastweight import FastWeightManager, FWConfig
from ptt.runner import RunConfig, run_stream
from ptt.streams.repo import build_repo_stream


def mask_acc(docs, key="xfile"):
    n = sum(d[f"{key}_n"] for d in docs)
    c = sum((d.get(f"{key}_acc") or 0) * d[f"{key}_n"] for d in docs)
    return (c / n if n else None), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B-Base")
    ap.add_argument("--repos", default="repos200")
    ap.add_argument("--policy", default="persist")
    ap.add_argument("--eta", type=float, default=3e-2)
    ap.add_argument("--clip", type=float, default=None)
    ap.add_argument("--gamma", type=float, default=None)
    ap.add_argument("--gamma_d", type=float, default=0.9)
    ap.add_argument("--alpha_norm", action="store_true")
    ap.add_argument("--project_k", type=int, default=0, help="GPM-style protected activation subspace (per layer, per session)")
    ap.add_argument("--project_energy", type=float, default=0.95)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--ctx_len", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--general_eval", default="hellaswag,arc_easy,arc_challenge,piqa,winogrande")
    ap.add_argument("--lags", default="0,5,15,40", help="re-score each repo's held-out file this many repos later")
    ap.add_argument("--fresh_repos", default=None,
                    help="directory of NEVER-streamed repos; their holdouts are scored with the final state. "
                         "Excess over base here = generic style transfer, not memory.")
    ap.add_argument("--general_limit", type=int, default=2000)
    ap.add_argument("--general_cache", default=None, help="json path; BEFORE eval reused across runs of the same model")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bf16")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    clip = args.clip if args.clip is not None else args.eta
    gamma = args.gamma if args.gamma is not None else (0.9 if args.policy == "decay" else 1.0)

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16 if args.dtype=="bf16" else torch.float32, trust_remote_code=True,
                                                 attn_implementation="sdpa").to(args.device)
    repo_dirs = sorted(os.path.join(args.repos, d) for d in os.listdir(args.repos)
                       if os.path.isdir(os.path.join(args.repos, d)))
    fw_policy = "reset" if args.policy == "base" else args.policy
    fw = FastWeightManager(model, FWConfig(eta=args.eta, clip=clip, policy=fw_policy, gamma=gamma,
                                           gamma_d=args.gamma_d, alpha_norm=args.alpha_norm,
                                           project_k=args.project_k, project_energy=args.project_energy,
                                           dtype=torch.bfloat16 if args.dtype=="bf16" else torch.float32, seed=args.seed))
    rcfg = RunConfig(chunk=args.chunk, ctx_len=args.ctx_len, log_every=50)

    tasks = args.general_eval.split(",") if args.general_eval else None
    gen_before = None
    if tasks:
        from ptt.eval.general import eval_general
        cache = getattr(args, "general_cache", None)
        if cache and os.path.exists(cache):
            gen_before = json.load(open(cache))
            print("general BEFORE (cached):", gen_before, flush=True)
        else:
            gen_before = eval_general(model, tok, tasks, limit=args.general_limit)
            if cache:
                os.makedirs(os.path.dirname(cache) or ".", exist_ok=True); json.dump(gen_before, open(cache, "w"))
        print("general BEFORE:", gen_before, flush=True)

    per_repo, stream_docs_all = [], []
    lags = sorted(int(x) for x in args.lags.split(","))
    pending = []   # (due_repo_index, lag, entry, holdout_doc)
    t0 = time.time()
    for ri, root in enumerate(repo_dirs):
        got = build_repo_stream([root], tok, obfuscate=True, seed=args.seed, holdout_last=True)
        docs, holdouts = got
        if not docs:
            continue
        eval_only = args.policy == "base"
        res = run_stream(model, fw, docs, rcfg, device=args.device, eval_only=eval_only)
        stream_docs_all += res["docs"]
        entry = {"repo": os.path.basename(root), "idx": ri, "n_docs": len(docs),
                 "tokens": sum(d["tokens"] for d in res["docs"])}
        if holdouts:
            h = list(holdouts.values())
            entry["holdout"] = h[0].name
            entry["acc_lag"], entry["ppl_lag"] = {}, {}
            if 0 in lags:  # lag 0 = while the session is still active (before any boundary reset)
                rh = run_stream(model, fw, h, rcfg, device=args.device, eval_only=True)
                acc, xn = mask_acc(rh["docs"])
                entry["acc_lag"]["0"] = acc; entry["ppl_lag"]["0"] = rh["docs"][0]["xfile_ppl"]
                entry["xn"] = xn; entry["acc_then"], entry["ppl_then"] = acc, rh["docs"][0]["xfile_ppl"]
            for lag in lags:
                if lag > 0:
                    pending.append((ri + lag, lag, entry, h))
        if not eval_only:
            fw.end_session()
        entry["basis_k"] = fw.basis_size()
        per_repo.append(entry)
        # score every held-out file whose lag is due now (eval-only; fast-weight state untouched)
        still = []
        for due, lag, e, h in pending:
            if due <= ri:
                rh = run_stream(model, fw, h, rcfg, device=args.device, eval_only=True)
                acc, _ = mask_acc(rh["docs"])
                e["acc_lag"][str(lag)] = acc; e["ppl_lag"][str(lag)] = rh["docs"][0]["xfile_ppl"]
            else:
                still.append((due, lag, e, h))
        pending = still
        if (ri + 1) % 10 == 0:
            print(f"--- repo {ri+1}/{len(repo_dirs)} t={time.time()-t0:.0f}s", flush=True)

    # final pass: everything still pending is scored at the end of the stream (lag = whatever remains)
    hold_cache = {}
    for due, lag, e, h in pending:
        hold_cache[e["repo"]] = h
    for entry in per_repo:
        if "holdout" not in entry:
            continue
        h = hold_cache.get(entry["repo"])
        if h is None:
            got = build_repo_stream([os.path.join(args.repos, entry["repo"])], tok, obfuscate=True,
                                    seed=args.seed, holdout_last=True)
            h = list(got[1].values())
        rh = run_stream(model, fw, h, rcfg, device=args.device, eval_only=True)
        entry["acc_end"], _ = mask_acc(rh["docs"])
        entry["ppl_end"] = rh["docs"][0]["xfile_ppl"]

    fresh = None
    if args.fresh_repos:
        fdirs = sorted(os.path.join(args.fresh_repos, d) for d in os.listdir(args.fresh_repos)
                       if os.path.isdir(os.path.join(args.fresh_repos, d)))
        accs, ns, per_fresh = 0.0, 0, []
        for fr in fdirs:
            got = build_repo_stream([fr], tok, obfuscate=True, seed=args.seed + 10007, holdout_last=True)
            h = list(got[1].values())
            if not h:
                continue
            rh = run_stream(model, fw, h, rcfg, device=args.device, eval_only=True)
            a, n = mask_acc(rh["docs"])
            if a is not None:
                accs += a * n; ns += n
                per_fresh.append({"repo": os.path.basename(fr), "acc": a, "xn": n})
        fresh = {"acc": accs / ns if ns else None, "n": ns, "repos": len(fdirs), "per_repo": per_fresh}
        print("fresh-repo transfer:", fresh, flush=True)

    gen_after = None
    if tasks:
        from ptt.eval.general import eval_general
        gen_after = eval_general(model, tok, tasks, limit=args.general_limit)
        print("general AFTER :", gen_after, flush=True)

    ok = [e for e in per_repo if e.get("acc_then") is not None and e.get("acc_end") is not None]
    W = sum(e["xn"] for e in ok) or 1
    summary = {
        "policy": args.policy, "eta": args.eta, "alpha_norm": args.alpha_norm, "gamma": gamma,
        "project_k": args.project_k, "basis_k_final": fw.basis_size(),
        "acc_then": sum(e["acc_then"] * e["xn"] for e in ok) / W,
        "acc_end": sum(e["acc_end"] * e["xn"] for e in ok) / W,
        "retention": sum((e["acc_end"] - e["acc_then"]) * e["xn"] for e in ok) / W,
        "retention_first_third": (lambda es: sum((e["acc_end"] - e["acc_then"]) * e["xn"] for e in es) / (sum(e["xn"] for e in es) or 1))
                                 ([e for e in ok if e["idx"] < len(repo_dirs) // 3]),
        "lags": {str(l): (lambda es: (sum(e["acc_lag"][str(l)] * e["xn"] for e in es) / (sum(e["xn"] for e in es) or 1), len(es)))
                          ([e for e in per_repo if str(l) in e.get("acc_lag", {})]) for l in lags},
        "fresh": fresh,
        "general_before": gen_before, "general_after": gen_after,
        "wall_min": (time.time() - t0) / 60,
    }
    print(json.dumps(summary, indent=2))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump({"summary": summary, "per_repo": per_repo, "config": vars(args)}, open(args.out, "w"))


if __name__ == "__main__":
    main()
