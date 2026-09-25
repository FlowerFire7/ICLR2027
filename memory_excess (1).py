#!/usr/bin/env python
"""Session-specific retention P(L) = stream excess - fresh excess, with combined bootstrap CIs.
  --key ppl : log-PPL readout (prose);  --key acc : recall readout (code)
  python scripts/memory_excess.py --key acc results/e1/persist_s0.json results/e1/persist_s1.json results/e1/persist_s2.json \
      --base results/e1/base_s0.json results/e1/base_s1.json results/e1/base_s2.json
Multiple seeds are pooled; fresh per-session/per-repo records are required for the fresh bootstrap."""
import argparse, json
import numpy as np
ap = argparse.ArgumentParser()
ap.add_argument("policy", nargs="+"); ap.add_argument("--base", nargs="+", required=True)
ap.add_argument("--key", choices=["ppl", "acc"], default="ppl"); ap.add_argument("--B", type=int, default=5000)
a = ap.parse_args(); rng = np.random.default_rng(0)
P = [json.load(open(f)) for f in a.policy]; Bs = [json.load(open(f)) for f in a.base]
assert len(P) == len(Bs), "one base file per policy file (same seed order)"
lagkey = "ppl_lag" if a.key == "ppl" else "acc_lag"
val = (lambda x: np.log(x)) if a.key == "ppl" else (lambda x: x)
def boot(vals, w):
    vals = np.array(vals, float); w = np.array(w, float)
    idx = rng.integers(0, len(vals), (a.B, len(vals)))
    return float((vals * w).sum() / w.sum()), (vals[idx] * w[idx]).sum(1) / w[idx].sum(1)
# fresh excess (independent clusters: fresh sessions x seeds)
fd, fw = [], []
for rp, rb in zip(P, Bs):
    fp = rp.get("fresh", rp["summary"].get("fresh", {})); fb = rb.get("fresh", rb["summary"].get("fresh", {}))
    recp = fp.get("per_session") or fp.get("per_repo") or []; recb = fb.get("per_session") or fb.get("per_repo") or []
    kp = {(s.get("session") or s.get("repo")): s for s in recp}; kb = {(s.get("session") or s.get("repo")): s for s in recb}
    for k in set(kp) & set(kb):
        xp, xb = kp[k].get(a.key), kb[k].get(a.key)
        if xp is None or xb is None: continue
        if a.key == "ppl" and not (xp and xb and np.isfinite(xp) and np.isfinite(xb)): continue
        fd.append(val(xp) - val(xb)); fw.append(kp[k]["xn"])
if not fd: raise SystemExit("no per-session/per-repo fresh records with key '%s'" % a.key)
fpt, fbs = boot(fd, fw)
scale = 1.0 if a.key == "ppl" else 100.0
print(f"fresh excess ({len(fd)} clusters): {fpt*scale:+.2f} [{np.percentile(fbs,2.5)*scale:+.2f},{np.percentile(fbs,97.5)*scale:+.2f}]")
lags = sorted({int(k) for rp in P for e in rp["per_repo"] if e.get(lagkey) for k in e[lagkey] if k != "end"})
for l in lags:
    d, w = [], []
    for rp, rb in zip(P, Bs):
        A = {e["repo"]: e for e in rp["per_repo"] if e.get(lagkey) and e.get("xn")}
        Bq = {e["repo"]: e for e in rb["per_repo"] if e.get(lagkey) and e.get("xn")}
        for r in set(A) & set(Bq):
            x, y = A[r][lagkey].get(str(l)), Bq[r][lagkey].get(str(l))
            if x is None or y is None: continue
            if a.key == "ppl" and not (x and y and np.isfinite(x) and np.isfinite(y)): continue
            d.append(val(x) - val(y)); w.append(A[r]["xn"])
    spt, sbs = boot(d, w); ex = sbs - fbs; lo, hi = np.percentile(ex, [2.5, 97.5])
    print(f"lag{l:>3}: stream {spt*scale:+.2f}  P(L)={ (spt-fpt)*scale:+.2f} [{lo*scale:+.2f},{hi*scale:+.2f}]  clusters={len(d)}")
