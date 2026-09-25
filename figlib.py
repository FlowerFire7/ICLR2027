import json, glob, numpy as np
rng = np.random.default_rng(0)
LAGS = [0, 5, 15, 40]
def load(f): return json.load(open(f))
def recs(r): return [e for e in r["per_repo"] if e.get("acc_lag") and e.get("xn")]
def boot(vals, w, n=4000):
    vals = np.array(vals, float); w = np.array(w, float)
    idx = rng.integers(0, len(vals), (n, len(vals)))
    return (vals[idx] * w[idx]).sum(1) / w[idx].sum(1)
def pooled(runs, key="acc_lag", lags=LAGS):
    """runs: list of loaded jsons (seeds). returns array [(pt,lo,hi)] per lag; ppl in log space"""
    out = []
    for l in lags:
        es = []
        for r in runs:
            for e in recs(r):
                v = e[key].get(str(l))
                if v is None or not np.isfinite(v): continue
                es.append((np.log(v) if key == "ppl_lag" else v, e["xn"]))
        a = np.array([x for x, _ in es]); w = np.array([n for _, n in es], float)
        pt = (a * w).sum() / w.sum(); bs = boot(a, w)
        out.append((pt, *np.percentile(bs, [2.5, 97.5])))
    return np.array(out)
def paired(runsA, runsB, key="acc_lag", lags=LAGS):
    out = []
    for l in lags:
        d, w = [], []
        for ra, rb in zip(runsA, runsB):
            A = {e["repo"]: e for e in recs(ra)}; B = {e["repo"]: e for e in recs(rb)}
            for r in set(A) & set(B):
                x, y = A[r][key].get(str(l)), B[r][key].get(str(l))
                if x is None or y is None: continue
                if key == "ppl_lag":
                    if not (x and y and np.isfinite(x) and np.isfinite(y)): continue
                    d.append(np.log(x) - np.log(y))
                else: d.append(x - y)
                w.append(A[r]["xn"])
        d = np.array(d); w = np.array(w, float); pt = (d * w).sum() / w.sum(); bs = boot(d, w)
        out.append((pt, *np.percentile(bs, [2.5, 97.5])))
    return np.array(out)
def gen_diff(r, before):
    ga = r["summary"].get("general_after") or {}
    return {k: ga[k] - before[k] for k in ga if k in before}
