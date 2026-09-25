#!/usr/bin/env bash
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos200}
OUT=${OUT:-results/week5}
ETA=${ETA:-3e-2}
mkdir -p "$OUT"
C="--model $MODEL --repos $REPOS --eta $ETA --general_limit 500 --lags 0,5,15,40"

echo "=== Week 5 继续运行 (跳过已完成的 base) ==="
echo "开始时间: $(date)"

echo "[1/4] Running persist..."
python scripts/week3_repo.py $C --policy persist --out "$OUT/persist.json"
echo "persist 完成: $(date)"

echo "[2/4] Running session..."
python scripts/week3_repo.py $C --policy session --out "$OUT/session.json"
echo "session 完成: $(date)"

echo "[3/4] Running consistency_norm..."
python scripts/week3_repo.py $C --policy consistency --alpha_norm --out "$OUT/consistency_norm.json"
echo "consistency_norm 完成: $(date)"

echo "[4/4] Running random_norm..."
python scripts/week3_repo.py $C --policy random --alpha_norm --out "$OUT/random_norm.json"
echo "random_norm 完成: $(date)"

echo "=== 生成 horizon 分析 ==="
python scripts/horizon.py "$OUT"/*.json | tee "$OUT/horizon.txt"

echo "=== Week 5 全部完成 ==="
echo "结束时间: $(date)"
