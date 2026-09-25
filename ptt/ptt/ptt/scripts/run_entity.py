#!/usr/bin/env python
"""E3: lag protocol on the S-Entity stream (mirrors week3_repo.py; sessions instead of repos).

  CUDA_VISIBLE_DEVICES=1 python scripts/run_entity.py --model Qwen/Qwen3-0.6B-Base \
      --policy persist --eta 3e-2 --n_articles 300 --fresh 30 --out results/entity/persist.json
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from ptt.fastweight import FastWeightManager, FWConfig
from ptt.runner import RunConfig, run_stream
from ptt.streams.entity import build_entity_sessions, load_wikitext_articles

def mask_acc(docs, key="xfile"):
    n = sum(d[f"{key}_n"] for d in docs); c = sum((d.get(f"{key}_acc") or 0) * d[f"{key}_n"] for d in docs)
    return (c / n if n else None), n

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen3-0.6B-Base")
ap.add_argument("--policy", default="persist")
ap.add_argument("--eta", type=float, default=3e-2)
ap.add_argument("--clip", type=float, default=None)
ap.add_argument("--gamma", type=float, default=None)
ap.add_argument("--alpha_norm", action="store_true")
ap.add_argument("--chunk", type=int, default=256)
ap.add_argument("--ctx_len", type=int, default=1024)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--n_articles", type=int, default=300)
ap.add_argument("--fresh", type=int, default=30, help="hold this many sessions out entirely (style-transfer control)")
ap.add_argument("--lags", default="0,5,15,40")
ap.add_argument("--general_eval", default="hellaswag,arc_easy,arc_challenge,piqa,winogrande")
ap.add_argument("--general_limit", type=int, default=2000)
ap.add_argument("--general_cache", default=None)
ap.add_argument("--device", default="cuda")
ap.add_argument("--out", required=True)
a = ap.parse_args()
clip = a.clip if a.clip is not None else a.eta
gamma = a.gamma if a.gamma is not None else (0.9 if a.policy == "decay" else 1.0)
torch.manual_seed(a.seed); np.random.seed(a.seed)

tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, trust_remote_code=True,
                                             attn_implementation="sdpa").to(a.device)
arts = load_wikitext_articles(max_articles=a.n_articles + a.fresh)
rng = np.random.default_rng(a.seed); order = rng.permutation(len(arts))
arts = [arts[i] for i in order]
sessions = build_entity_sessions(arts, tok, seed=a.seed)
fresh_sessions, sessions = sessions[:a.fresh], sessions[a.fresh:]
print(f"{len(sessions)} stream sessions, {len(fresh_sessions)} fresh; "
      f"{sum(len(d.ids) for s,_ in sessions for d in s)/1e6:.1f}M tokens", flush=True)

fw_policy = "reset" if a.policy == "base" else a.policy
fw = FastWeightManager(model, FWConfig(eta=a.eta, clip=clip, policy=fw_policy, gamma=gamma,
                                       alpha_norm=a.alpha_norm, dtype=torch.bfloat16, seed=a.seed))
rcfg = RunConfig(chunk=a.chunk, ctx_len=a.ctx_len, log_every=100)
tasks = a.general_eval.split(",") if a.general_eval else None
gen_before = None
if tasks:
    from ptt.eval.general import eval_general
    cache = getattr(a, "general_cache", None)
    if cache and os.path.exists(cache):
        gen_before = json.load(open(cache))
        print("general BEFORE (cached):", gen_before, flush=True)
    else:
        gen_before = eval_general(model, tok, tasks, limit=a.general_limit, device=a.device)
        if cache:
            os.makedirs(os.path.dirname(cache) or ".", exist_ok=True); json.dump(gen_before, open(cache, "w"))
    print("general BEFORE:", gen_before, flush=True)

lags = sorted(int(x) for x in a.lags.split(",")); pending = []; per = []; t0 = time.time()
eval_only = a.policy == "base"
for si, (docs, hold) in enumerate(sessions):
    res = run_stream(model, fw, docs, rcfg, device=a.device, eval_only=eval_only)
    e = {"repo": docs[0].meta["repo"], "idx": si, "tokens": sum(d["tokens"] for d in res["docs"])}
    if hold is not None:
        e["acc_lag"], e["ppl_lag"] = {}, {}
        rh = run_stream(model, fw, [hold], rcfg, device=a.device, eval_only=True)
        acc, xn = mask_acc(rh["docs"]); e["acc_lag"]["0"] = acc; e["xn"] = xn
        e["ppl_lag"]["0"] = rh["docs"][0]["xfile_ppl"]
        for lag in lags:
            if lag > 0: pending.append((si + lag, lag, e, hold))
    if not eval_only:
        fw.end_session()
    per.append(e)
    still = []
    for due, lag, ee, h in pending:
        if due <= si:
            rh = run_stream(model, fw, [h], rcfg, device=a.device, eval_only=True)
            acc, _ = mask_acc(rh["docs"]); ee["acc_lag"][str(lag)] = acc
            ee["ppl_lag"][str(lag)] = rh["docs"][0]["xfile_ppl"]
        else: still.append((due, lag, ee, h))
    pending = still
    if (si + 1) % 25 == 0: print(f"--- session {si+1}/{len(sessions)} t={time.time()-t0:.0f}s", flush=True)

for due, lag, ee, h in pending:  # score leftovers at stream end
    rh = run_stream(model, fw, [h], rcfg, device=a.device, eval_only=True)
    ee["acc_lag"].setdefault("end", mask_acc(rh["docs"])[0])
accs, ns = 0.0, 0
for docs, hold in fresh_sessions:
    if hold is None: continue
    rh = run_stream(model, fw, [hold], rcfg, device=a.device, eval_only=True)
    x, n = mask_acc(rh["docs"])
    if x is not None: accs += x * n; ns += n
fresh = {"acc": accs / ns if ns else None, "n": ns}
gen_after = None
if tasks:
    from ptt.eval.general import eval_general
    gen_after = eval_general(model, tok, tasks, limit=a.general_limit, device=a.device)
    print("general AFTER :", gen_after, flush=True)
summary = {"policy": a.policy, "eta": a.eta, "alpha_norm": a.alpha_norm, "fresh": fresh,
           "general_before": gen_before, "general_after": gen_after, "wall_min": (time.time()-t0)/60}
print(json.dumps(summary, indent=2))
os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
json.dump({"summary": summary, "per_repo": per, "fresh": fresh, "config": vars(a)}, open(a.out, "w"))
