#!/usr/bin/env bash
# Week 3: (a) 200-repo stream so interference can accumulate; (b) proper per-repo retention;
# (c) EQUAL-BUDGET gating (--alpha_norm): every gated policy spends the same write mass as persist,
#     so differences are about WHERE to write, not how much.
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos200}
OUT=${OUT:-results/week3}
ETA=${ETA:-3e-2}
mkdir -p "$OUT"
[ -d "$REPOS" ] || python scripts/fetch_repos.py --n 200 --out "$REPOS" --min_stars 30 --max_stars 1500
C="--model $MODEL --repos $REPOS --eta $ETA --general_limit 500"

python scripts/week3_repo.py $C --policy base        --out "$OUT/base.json"
python scripts/week3_repo.py $C --policy persist     --out "$OUT/persist.json"
python scripts/week3_repo.py $C --policy decay --gamma 0.98 --out "$OUT/decay.json"
for pol in consistency fisher random; do
  python scripts/week3_repo.py $C --policy $pol --alpha_norm --out "$OUT/${pol}_norm.json"
done
python scripts/week3_repo.py $C --policy surprise    --out "$OUT/surprise.json"
# cliff probe with and without a norm cap
python scripts/week3_repo.py $C --policy persist --eta 6e-2 --out "$OUT/persist_6e-2.json"
python - <<'PY'
import glob, json
rows=[]
for f in sorted(glob.glob("results/week3/*.json")):
    s=json.load(open(f))["summary"]
    g=(s.get("general_after") or {}); gb=(s.get("general_before") or {})
    dg=(sum(g.values())/len(g)-sum(gb.values())/len(gb)) if g and gb else float('nan')
    rows.append((s["policy"],s["eta"],s.get("alpha_norm"),s["acc_then"],s["acc_end"],s["retention"],s["retention_first_third"],dg))
print(f"{'policy':12s} {'eta':>6s} {'norm':>5s} {'then':>7s} {'end':>7s} {'reten':>7s} {'ret1/3':>7s} {'dGen':>7s}")
for r in rows: print(f"{r[0]:12s} {r[1]:6.0e} {str(r[2]):>5s} {r[3]:7.3f} {r[4]:7.3f} {r[5]:+7.3f} {r[6]:+7.3f} {r[7]:+7.3f}")
PY
