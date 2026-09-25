#!/usr/bin/env python
"""Memory excess on prose streams = (stream paired dlogPPL vs base) - (fresh dlogPPL vs base),
with a combined bootstrap CI (stream: session clusters; fresh: fresh-session clusters, independent).
  python scripts/memory_excess.py results/e3v3/persist_s0.json results/e3v3/base_s0.json"""
import json, sys
import numpy as np
rng = np.random.default_rng(0)
P, B = (json.load(open(f)) for f in sys.argv[1:3])
pa = {e["repo"]: e for e in P["per_repo"] if e.get("ppl_lag")}
pb = {e["repo"]: e for e in B["per_repo"] if e.get("ppl_lag")}
common = sorted(set(pa) & set(pb))

def boot(vals, w, n=4000):
    vals = np.array(vals); w = np.array(w, float)
    idx = rng.integers(0, len(vals), (n, len(vals)))
    return (vals[idx] * w[idx]).sum(1) / w[idx].sum(1)

# fresh: per-session log-ppl for both runs (requires fresh.per_session from e3fix3+)
fp = {s["session"]: s for s in P["fresh"].get("per_session", [])}
fb = {s["session"]: s for s in B["fresh"].get("per_session", [])}
fc = sorted(set(fp) & set(fb))
if not fc:
    sys.exit("no per-session fresh records: rerun with the e3fix3 package")
fd = [np.log(fp[s]["ppl"]) - np.log(fb[s]["ppl"]) for s in fc]; fw = [fp[s]["xn"] for s in fc]
fresh_bs = boot(fd, fw); fresh_pt = float((np.array(fd) * np.array(fw)).sum() / np.sum(fw))
print(f"fresh dlogPPL ({len(fc)} sessions): {fresh_pt:+.3f} [{np.percentile(fresh_bs,2.5):+.3f},{np.percentile(fresh_bs,97.5):+.3f}]")

lags = sorted({int(k) for r in common for k in pa[r]["ppl_lag"] if k != "end"})
for l in lags:
    d, w = [], []
    for r in common:
        x, y = pa[r]["ppl_lag"].get(str(l)), pb[r]["ppl_lag"].get(str(l))
        if x and y and np.isfinite(x) and np.isfinite(y):
            d.append(np.log(x) - np.log(y)); w.append(pa[r]["xn"])
    s_bs = boot(d, w); s_pt = float((np.array(d) * np.array(w)).sum() / np.sum(w))
    ex_bs = s_bs - fresh_bs; ex_pt = s_pt - fresh_pt
    lo, hi = np.percentile(ex_bs, [2.5, 97.5])
    print(f"lag{l:>3}: stream {s_pt:+.3f}  memory excess {ex_pt:+.3f} [{lo:+.3f},{hi:+.3f}] {'*' if hi < 0 else ''}")
