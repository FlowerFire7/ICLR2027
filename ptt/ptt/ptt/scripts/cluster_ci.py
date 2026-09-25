#!/usr/bin/env python
"""Repo-clustered bootstrap CIs for Recall@lag (targets within a repo are correlated, so
per-target binomial CIs are too narrow).   python scripts/cluster_ci.py results/week5/*.json"""
import json, sys, glob
import numpy as np
rng = np.random.default_rng(0)
B = 5000
files = sys.argv[1:] or sorted(glob.glob("results/week5/*.json"))
for f in files:
    r = json.load(open(f)); sm = r["summary"]
    pr = [e for e in r["per_repo"] if e.get("acc_lag")]
    name = f"{sm['policy']}{'_norm' if sm.get('alpha_norm') else ''}@{sm['eta']:.0e}"
    lags = sorted({int(k) for e in pr for k in e["acc_lag"]})
    out = [name]
    for l in lags:
        es = [(e["acc_lag"][str(l)], e["xn"]) for e in pr if str(l) in e["acc_lag"] and e.get("xn")]
        if not es:
            out.append(f"lag{l}: -"); continue
        a = np.array([x for x, _ in es]); w = np.array([n for _, n in es], float)
        point = float((a * w).sum() / w.sum())
        idx = rng.integers(0, len(es), size=(B, len(es)))
        bs = (a[idx] * w[idx]).sum(1) / w[idx].sum(1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out.append(f"lag{l}: {point:.3f} [{lo:.3f},{hi:.3f}]")
    if r.get("fresh") and r["fresh"].get("acc") is not None:
        out.append(f"fresh: {r['fresh']['acc']:.3f} (n={r['fresh']['n']})")
    print("  ".join(out))
