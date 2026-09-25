#!/usr/bin/env python
"""Run one persistence policy over a document stream.

Example (week-1 sanity, S-Repo):
  python run.py --model Qwen/Qwen3-0.6B-Base --stream repo --repos repos/ --policy reset   --eta 1e-3 --out results/reset.json
  python run.py --model Qwen/Qwen3-0.6B-Base --stream repo --repos repos/ --policy persist --eta 1e-3 --out results/persist.json
  python run.py ... --policy base   # frozen model, no writes (lower bound)
"""
import argparse, json, os, random, time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from ptt.fastweight import FastWeightManager, FWConfig
from ptt.runner import RunConfig, run_stream
from ptt.streams.repo import build_repo_stream


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B-Base")
    ap.add_argument("--stream", choices=["repo"], default="repo")
    ap.add_argument("--repos", default="repos", help="directory containing cloned repos (one sub-dir each)")
    ap.add_argument("--max_repos", type=int, default=None)
    ap.add_argument("--max_docs", type=int, default=None)
    ap.add_argument("--policy", default="reset",
                    choices=["base", "reset", "persist", "decay", "consistency", "fisher", "surprise", "random"])
    ap.add_argument("--eta", type=float, default=1e-3)
    ap.add_argument("--clip", type=float, default=1e-3)
    ap.add_argument("--gamma", type=float, default=None, help="G_slow decay at boundary (default: 1.0, or 0.9 for decay)")
    ap.add_argument("--gamma_d", type=float, default=0.9)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--ctx_len", type=int, default=1024)
    ap.add_argument("--max_tokens_per_file", type=int, default=8192)
    ap.add_argument("--no_obfuscate", action="store_true", help="keep original identifiers (contaminated by pre-training)")
    ap.add_argument("--alpha_norm", action="store_true", help="equal write budget: normalise gate to mean 1")
    ap.add_argument("--layers", default=None, help="comma list of layer indices, or 'top3' / 'mid3' / 'bot3'")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="bf16", choices=["bf16", "fp32"])
    ap.add_argument("--grad_ckpt", action="store_true")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--general_eval", default=None,
                    help="comma list of lm-eval tasks to run before and after the stream, e.g. hellaswag,arc_easy")
    ap.add_argument("--general_limit", type=int, default=500)
    ap.add_argument("--retest_first_k", type=int, default=0,
                    help="after the stream, re-score the first K documents (eval-only) to measure backward transfer")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float32

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype, trust_remote_code=True,
                                                 attn_implementation="sdpa").to(args.device)
    if args.grad_ckpt:
        model.gradient_checkpointing_enable()
        model.config.use_cache = False

    # ---- stream ----
    if args.stream == "repo":
        repo_dirs = sorted(os.path.join(args.repos, d) for d in os.listdir(args.repos)
                           if os.path.isdir(os.path.join(args.repos, d)))
        if args.max_repos: repo_dirs = repo_dirs[:args.max_repos]
        docs = build_repo_stream(repo_dirs, tok, max_tokens_per_file=args.max_tokens_per_file,
                                 obfuscate=not args.no_obfuscate, seed=args.seed)
    n_x = sum(sum(d.masks["xfile"]) for d in docs)
    print(f"stream: {len(docs)} docs, {sum(len(d.ids) for d in docs)/1e6:.2f}M tokens, xfile targets={n_x}")

    # ---- fast weights ----
    n_layers = len([n for n, _ in model.named_modules() if n.endswith("mlp.down_proj") or n.endswith("mlp.c_proj")])
    layer_subset = None
    if args.layers:
        if args.layers == "top3": layer_subset = list(range(n_layers - 3, n_layers))
        elif args.layers == "mid3": layer_subset = list(range(n_layers // 2 - 1, n_layers // 2 + 2))
        elif args.layers == "bot3": layer_subset = [0, 1, 2]
        else: layer_subset = [int(x) for x in args.layers.split(",")]
    gamma = args.gamma if args.gamma is not None else (0.9 if args.policy == "decay" else 1.0)
    fw_policy = "reset" if args.policy == "base" else args.policy
    fw = FastWeightManager(model, FWConfig(eta=args.eta, clip=args.clip, policy=fw_policy, gamma=gamma,
                                           gamma_d=args.gamma_d, layer_subset=layer_subset, dtype=dtype, seed=args.seed,
                                           alpha_norm=args.alpha_norm))

    rcfg = RunConfig(chunk=args.chunk, ctx_len=args.ctx_len, max_docs=args.max_docs)
    tasks = args.general_eval.split(",") if args.general_eval else None
    general_before = general_after = None
    if tasks:
        from ptt.eval.general import eval_general
        general_before = eval_general(model, tok, tasks, limit=args.general_limit, device=args.device)
        print("general BEFORE:", general_before, flush=True)
    t0 = time.time()
    res = run_stream(model, fw, docs, rcfg, device=args.device, eval_only=(args.policy == "base"))
    res["wall_s"] = time.time() - t0
    if tasks:
        general_after = eval_general(model, tok, tasks, limit=args.general_limit, device=args.device)
        print("general AFTER :", general_after, flush=True)
    res["general_before"], res["general_after"] = general_before, general_after
    if args.retest_first_k:
        k = args.retest_first_k
        re = run_stream(model, fw, docs[:k], RunConfig(chunk=args.chunk, ctx_len=args.ctx_len), device=args.device, eval_only=True)
        res["retest_first_k"] = {"k": k, "docs": re["docs"]}
        def _agg(D, key):
            n = sum(d[f"{key}_n"] for d in D); c = sum((d.get(f"{key}_acc") or 0) * d[f"{key}_n"] for d in D)
            return c / n if n else None
        res["retest_summary"] = {"xfile_acc_end": _agg(re["docs"], "xfile"), "xfile_acc_stream": _agg(res["docs"][:k], "xfile"),
                                 "local_acc_end": _agg(re["docs"], "local"), "local_acc_stream": _agg(res["docs"][:k], "local")}
        print("retest first", k, res["retest_summary"], flush=True)
    res["config"] = vars(args) | {"gamma_eff": gamma, "n_layers_total": n_layers, "layer_subset": layer_subset}
    if args.device.startswith("cuda"):
        res["peak_mem_gb"] = torch.cuda.max_memory_allocated() / 1e9

    # ---- summary ----
    D = res["docs"]
    def agg(key):
        c = sum(d.get(f"{key}_acc", 0) * d[f"{key}_n"] for d in D if d.get(f"{key}_acc") is not None)
        n = sum(d[f"{key}_n"] for d in D)
        return (c / n if n else None), n
    def agg_ppl(key):
        nl = sum(r[f"{key}_nll"] for r in res["records"]); n = sum(r[f"{key}_n"] for r in res["records"])
        return float(np.exp(nl / n)) if n else None
    xa, xn = agg("xfile"); ra, rn = agg("xrep"); la, ln = agg("local")
    mean_ppl = float(np.exp(np.mean([np.log(d["ppl"]) for d in D])))
    res["summary"] = {"xfile_acc": xa, "xfile_n": xn, "xfile_ppl": agg_ppl("xfile"), "xrep_acc": ra, "xrep_n": rn,
                      "local_acc": la, "local_n": ln, "local_ppl": agg_ppl("local"), "geo_mean_doc_ppl": mean_ppl}
    print(f"\n== {args.policy} eta={args.eta}: xfile_first={xa} (n={xn}) xrep={ra} (n={rn}) local={la} (n={ln}) "
          f"doc_ppl={mean_ppl:.2f} wall={res['wall_s']:.0f}s peak={res.get('peak_mem_gb', 0):.1f}GB")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(res, open(args.out, "w"))


if __name__ == "__main__":
    main()
