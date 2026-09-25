#!/usr/bin/env bash
set -e
MODEL=${MODEL:-Qwen/Qwen3-1.7B-Base}
REPOS=${REPOS:-repos180}
FRESH=${FRESH:-repos_fresh}
OUT=${OUT:-results/e1}
ETA=${ETA:-3e-2}
SEED=${SEED:-0}
mkdir -p "$OUT"

C="--model $MODEL --repos $REPOS --fresh_repos $FRESH --eta $ETA --seed $SEED"
C="$C --general_limit 500 --lags 0,5,15,40"

echo "=== E1 主表 seed=$SEED ==="
echo "开始时间: $(date)"

echo "[1/5] base..."
python scripts/week3_repo.py $C --policy base --out "$OUT/base_s${SEED}.json"
echo "base 完成: $(date)"

echo "[2/5] persist..."
python scripts/week3_repo.py $C --policy persist --out "$OUT/persist_s${SEED}.json"
echo "persist 完成: $(date)"

echo "[3/5] session..."
python scripts/week3_repo.py $C --policy session --out "$OUT/session_s${SEED}.json"
echo "session 完成: $(date)"

echo "[4/5] consistency_norm..."
python scripts/week3_repo.py $C --policy consistency --alpha_norm --out "$OUT/consistency_norm_s${SEED}.json"
echo "consistency_norm 完成: $(date)"

echo "[5/5] random_norm..."
python scripts/week3_repo.py $C --policy random --alpha_norm --out "$OUT/random_norm_s${SEED}.json"
echo "random_norm 完成: $(date)"

echo "=== E1 seed=$SEED 全部完成 ==="
echo "结束时间: $(date)"
