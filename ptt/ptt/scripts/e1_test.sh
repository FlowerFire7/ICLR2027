#!/usr/bin/env bash
set -e
MODEL=Qwen/Qwen3-1.7B-Base
REPOS=repos180
FRESH=repos_fresh
OUT=results/e1_test
ETA=3e-2
mkdir -p "$OUT"

C="--model $MODEL --repos $REPOS --fresh_repos $FRESH --eta $ETA --seed 0"
C="$C --general_limit 500 --lags 0,5,15,40"

echo "=== E1 测试运行（1.7B, seed0, base+persist）==="
echo "开始时间: $(date)"

echo "[1/2] base..."
START=$(date +%s)
python scripts/week3_repo.py $C --policy base --out "$OUT/base_s0.json"
END=$(date +%s)
echo "base 完成: $(date), 耗时: $((END-START))s"

echo "[2/2] persist..."
START=$(date +%s)
python scripts/week3_repo.py $C --policy persist --out "$OUT/persist_s0.json"
END=$(date +%s)
echo "persist 完成: $(date), 耗时: $((END-START))s"

echo "=== E1 测试完成 ==="
