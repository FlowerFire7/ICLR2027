#!/usr/bin/env bash
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos200}
OUT=${OUT:-results/week5}
ETA=${ETA:-3e-2}
mkdir -p "$OUT"
C="--model $MODEL --repos $REPOS --eta $ETA --general_limit 500 --lags 0,5,15,40"
python scripts/week3_repo.py $C --policy base                    --out "$OUT/base.json"
python scripts/week3_repo.py $C --policy persist                 --out "$OUT/persist.json"
python scripts/week3_repo.py $C --policy session                 --out "$OUT/session.json"
python scripts/week3_repo.py $C --policy consistency --alpha_norm --out "$OUT/consistency_norm.json"
python scripts/week3_repo.py $C --policy random      --alpha_norm --out "$OUT/random_norm.json"
python scripts/horizon.py "$OUT"/*.json | tee "$OUT/horizon.txt"
