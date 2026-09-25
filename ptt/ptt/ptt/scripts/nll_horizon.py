#!/usr/bin/env python
"""Log-likelihood-based horizon for floor-level tasks: pooled per-lag xfile log-PPL with clustered
bootstrap, plus paired log-PPL differences between two runs.
  python scripts/nll_horizon.py results/e3/*.json --paired consistency_s0.json random_s0.json"""
import argparse, glob, json
import numpy as np
ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--paired", nargs=2, default=None, metavar=("A","B"))
a = ap.parse_args(); rng = np.random.default_rng(0)

def rows(f):
    r = json.load(open(f))
    return r["summary"], [e for e in r["per_repo"] if e.get("ppl_lag") and e.get("xn")]

for f in a.files:
    sm, pr = rows(f)
    name = f"{sm['policy']}{'_norm' if sm.get('alpha_norm') else ''}@{sm['eta']:.0e}"
    lags = sorted({int(k) for e in pr for k in e["ppl_lag"] if k != "end"})
    cells = []
    for l in lags:
        es = [(np.log(e["ppl_lag"][str(l)]), e["xn"]) for e in pr
              if str(l) in e["ppl_lag"] and e["ppl_lag"][str(l)] and np.isfinite(e["ppl_lag"][str(l)])]
        v = np.array([x for x, _ in es]); w = np.array([n for _, n in es], float)
        pt = (v * w).sum() / w.sum()
        idx = rng.integers(0, len(es), (3000, len(es)))
        bs = (v[idx] * w[idx]).sum(1) / w[idx].sum(1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        cells.append(f"lag{l}: PPL {np.exp(pt):8.0f} [{np.exp(lo):.0f},{np.exp(hi):.0f}]")
    print(f"{name:22s} " + "  ".join(cells))

if a.paired:
    A, B = (json.load(open(f)) for f in a.paired)
    pa = {e["repo"]: e for e in A["per_repo"] if e.get("ppl_lag")}
    pb = {e["repo"]: e for e in B["per_repo"] if e.get("ppl_lag")}
    common = sorted(set(pa) & set(pb))
    print(f"\npaired log-PPL diff {A['summary']['policy']} - {B['summary']['policy']} "
          f"(negative = first remembers more), {len(common)} holdouts")
    lags = sorted({int(k) for r in common for k in pa[r]["ppl_lag"] if k != "end"})
    for l in lags:
        d, w = [], []
        for r in common:
            x, y = pa[r]["ppl_lag"].get(str(l)), pb[r]["ppl_lag"].get(str(l))
            if x and y and np.isfinite(x) and np.isfinite(y):
                d.append(np.log(x) - np.log(y)); w.append(pa[r]["xn"])
        d = np.array(d); w = np.array(w, float)
        pt = (d * w).sum() / w.sum()
        idx = rng.integers(0, len(d), (4000, len(d)))
        bs = (d[idx] * w[idx]).sum(1) / w[idx].sum(1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"  lag{l}: dlogPPL {pt:+.3f} [{lo:+.3f},{hi:+.3f}] {'*' if lo>0 or hi<0 else ''} "
              f"(PPL ratio {np.exp(pt):.2f}x)")
