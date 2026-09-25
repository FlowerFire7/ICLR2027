#!/usr/bin/env bash
# Week 4 (fixed-lag retention protocol: every held-out file re-scored 0/5/15/40 repos later)
#   session      : persist within repo, reset at repo boundary   -> candidate recipe
#   persist_p64  : persist + GPM-style activation-subspace projection -> principled placement candidate
#   persist / consistency_norm / random_norm re-run under the new protocol to settle the placement question
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos200}
OUT=${OUT:-results/week4}
ETA=${ETA:-3e-2}
mkdir -p "$OUT"
C="--model $MODEL --repos $REPOS --eta $ETA --general_limit 500 --lags 0,5,15,40"
python scripts/week3_repo.py $C --policy session                    --out "$OUT/session.json"
python scripts/week3_repo.py $C --policy persist                    --out "$OUT/persist.json"
python scripts/week3_repo.py $C --policy consistency --alpha_norm   --out "$OUT/consistency_norm.json"
python scripts/week3_repo.py $C --policy random      --alpha_norm   --out "$OUT/random_norm.json"
python scripts/week3_repo.py $C --policy persist --project_k 64     --out "$OUT/persist_p64.json"
python scripts/week3_repo.py $C --policy persist --project_k 256    --out "$OUT/persist_p256.json"
python scripts/week3_repo.py $C --policy consistency --alpha_norm --seed 1 --out "$OUT/consistency_norm_s1.json"
python scripts/week3_repo.py $C --policy random      --alpha_norm --seed 1 --out "$OUT/random_norm_s1.json"
python scripts/horizon.py "$OUT"/*.json | tee "$OUT/horizon.txt"
