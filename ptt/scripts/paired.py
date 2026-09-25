#!/usr/bin/env python
"""Paired (same-holdout) comparison of two runs: per-repo acc differences with repo-clustered
bootstrap CI at each lag.   python scripts/paired.py runA.json runB.json"""
import json, sys
import numpy as np
rng = np.random.default_rng(0)
A, B = (json.load(open(f)) for f in sys.argv[1:3])
pa = {e["repo"]: e for e in A["per_repo"] if e.get("acc_lag")}
pb = {e["repo"]: e for e in B["per_repo"] if e.get("acc_lag")}
common = sorted(set(pa) & set(pb))
la = f"{A['summary']['policy']}"; lb = f"{B['summary']['policy']}"
print(f"paired {la} - {lb} over {len(common)} shared holdouts")
lags = sorted({int(k) for r in common for k in pa[r]["acc_lag"] if k != "end"})
for l in lags:
    rows = [(pa[r]["acc_lag"].get(str(l)), pb[r]["acc_lag"].get(str(l)), pa[r]["xn"]) for r in common]
    rows = [(x, y, n) for x, y, n in rows if x is not None and y is not None]
    d = np.array([x - y for x, y, _ in rows]); w = np.array([n for _, _, n in rows], float)
    point = float((d * w).sum() / w.sum())
    idx = rng.integers(0, len(rows), (5000, len(rows)))
    bs = (d[idx] * w[idx]).sum(1) / w[idx].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    sig = "*" if lo > 0 or hi < 0 else " "
    print(f"  lag{l:>3}: diff={point:+.4f} [{lo:+.4f},{hi:+.4f}] {sig} (n_repos={len(rows)})")
