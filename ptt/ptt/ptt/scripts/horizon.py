#!/usr/bin/env python
"""Retention vs lag with binomial 95% CIs.   python scripts/horizon.py results/week4/*.json
Uses the fixed-lag protocol (acc_lag) when present, else falls back to distance-from-end bins."""
import json, sys, glob, math
def ci(c, n):
    if not n: return float("nan"), float("nan")
    p = c / n; h = 1.96 * math.sqrt(p * (1 - p) / n); return p, h
files = sys.argv[1:] or sorted(glob.glob("results/week4/*.json"))
hdr = None
for f in files:
    r = json.load(open(f)); sm = r["summary"]; pr = [e for e in r["per_repo"] if e.get("acc_lag")]
    name = f"{sm['policy']}{'_norm' if sm.get('alpha_norm') else ''}{'_p'+str(sm['project_k']) if sm.get('project_k') else ''}@{sm['eta']:.0e}"
    if not pr:
        print(f"{name:22s} (no fixed-lag data; rerun with --lags)"); continue
    lags = sorted({int(k) for e in pr for k in e["acc_lag"]})
    if hdr is None:
        hdr = f"{'policy':22s} " + " ".join(f"{'lag'+str(l):>16s}" for l in lags) + f" {'end':>16s} {'dGen':>7s}"
        print(hdr); print("-" * len(hdr))
    cells = []
    for l in lags:
        es = [e for e in pr if str(l) in e["acc_lag"]]
        n = sum(e["xn"] for e in es); c = sum(e["acc_lag"][str(l)] * e["xn"] for e in es)
        p, h = ci(c, n); cells.append(f"{p:6.3f}±{h:5.3f}({len(es):3d})")
    es = [e for e in pr if e.get("acc_end") is not None]
    n = sum(e["xn"] for e in es); c = sum(e["acc_end"] * e["xn"] for e in es); p, h = ci(c, n)
    gb, ga = sm.get("general_before") or {}, sm.get("general_after") or {}
    dg = (sum(ga.values()) / len(ga) - sum(gb.values()) / len(gb)) if ga and gb else float("nan")
    print(f"{name:22s} " + " ".join(cells) + f" {p:6.3f}±{h:5.3f}({len(es):3d}) {dg:+7.3f}")
