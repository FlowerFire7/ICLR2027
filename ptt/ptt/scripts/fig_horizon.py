#!/usr/bin/env python
"""Fig 2 (horizon curves, clustered-bootstrap bands) and Fig 4 (interference collapse).
  python scripts/fig_horizon.py results/week5/*.json --collapse results/e4/*.json --out figs/"""
import argparse, glob, json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="+"); ap.add_argument("--collapse", nargs="*", default=[])
ap.add_argument("--out", default="figs"); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
rng = np.random.default_rng(0)
def curve(f):
    r = json.load(open(f)); pr = [e for e in r["per_repo"] if e.get("acc_lag") and e.get("xn")]
    sm = r["summary"]; name = f"{sm['policy']}{'*' if sm.get('alpha_norm') else ''}@{sm['eta']:.0e}"
    lags = sorted({int(k) for e in pr for k in e["acc_lag"] if k != "end"})
    pts = []
    for l in lags:
        es = [(e["acc_lag"][str(l)], e["xn"], e.get("tokens", 1)) for e in pr if str(l) in e["acc_lag"]]
        aa = np.array([x for x,_,_ in es]); w = np.array([n for _,n,_ in es], float)
        p = (aa*w).sum()/w.sum(); idx = rng.integers(0, len(es), (3000, len(es)))
        bs = (aa[idx]*w[idx]).sum(1)/w[idx].sum(1); lo, hi = np.percentile(bs, [2.5, 97.5])
        pts.append((l, p, lo, hi))
    return name, pts, r
plt.figure(figsize=(5,3.4))
for f in a.files:
    name, pts, _ = curve(f)
    x=[p[0] for p in pts]; y=[p[1] for p in pts]
    plt.plot(x, y, "-o", ms=3, label=name); plt.fill_between(x, [p[2] for p in pts], [p[3] for p in pts], alpha=.15)
plt.xlabel("lag (sessions after learning)"); plt.ylabel("first-mention recall"); plt.legend(fontsize=7); plt.tight_layout()
plt.savefig(f"{a.out}/fig2_horizon.pdf"); print("wrote fig2")
if a.collapse:
    plt.figure(figsize=(5,3.4))
    for f in a.collapse:
        name, pts, r = curve(f)
        pr = [e for e in r["per_repo"] if e.get("acc_lag") and e.get("xn")]
        mean_t = np.mean([e.get("tokens", 1) for e in pr])
        toks = {e["idx"]: e.get("tokens", mean_t) for e in pr}
        base = min(p[1] for p in pts)
        # P1 collapse variable: rho(k,L) = m_k^2 / sum_{j=k+1..k+L} m_j^2, m_j = tokens_j (eta cancels within a run
        # and is common across sessions of a run; kept out so runs with different eta test eta-invariance directly)
        buckets = {}
        for e in pr:
            for lk, acc in e["acc_lag"].items():
                if lk == "end": continue
                L = int(lk)
                if L == 0: continue
                mk = toks.get(e["idx"], mean_t) ** 2
                sub = sum(toks.get(j, mean_t) ** 2 for j in range(e["idx"] + 1, e["idx"] + 1 + L))
                rho = mk / (sub + 1e-9)
                buckets.setdefault(round(np.log10(rho), 1), []).append((acc, e["xn"]))
        xs = sorted(buckets)
        ys = [sum(a_ * n for a_, n in buckets[x]) / sum(n for _, n in buckets[x]) - base for x in xs]
        plt.plot([10 ** x for x in xs], ys, "-o", ms=3, label=name)
    plt.xscale("log"); plt.xlabel(r"mass ratio  $\rho = m_k^2 / \sum_{j>k}^{lag} m_j^2$"); plt.ylabel("excess recall")
    plt.legend(fontsize=7); plt.tight_layout(); plt.savefig(f"{a.out}/fig4_collapse.pdf"); print("wrote fig4")
