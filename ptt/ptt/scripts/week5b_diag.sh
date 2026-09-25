#!/usr/bin/env bash
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos180}
OUT=${OUT:-results/week5b}
mkdir -p "$OUT"

echo "=== Week 5b 诊断实验 ==="
echo "开始时间: $(date)"

# 诊断 1: 风格迁移测试（用 persist 终态测 fresh repos）
echo "[1/3] 诊断 1: persist + fresh_repos (测风格迁移 vs 记忆)..."
python scripts/week3_repo.py \
    --model $MODEL --repos $REPOS --eta 3e-2 \
    --general_limit 500 --lags 0,5,15,40 \
    --policy persist --fresh_repos repos_fresh \
    --out "$OUT/persist_fresh.json"
echo "诊断 1 完成: $(date)"

# 诊断 2a: E4 坍缩数据 - persist@2e-2
echo "[2/3] E4: persist@eta=2e-2..."
python scripts/week3_repo.py \
    --model $MODEL --repos $REPOS --eta 2e-2 \
    --general_limit 500 --lags 0,5,15,40 \
    --policy persist \
    --out "$OUT/persist_2e-2.json"
echo "persist@2e-2 完成: $(date)"

# 诊断 2b: E4 坍缩数据 - persist@4e-2
echo "[3/3] E4: persist@eta=4e-2..."
python scripts/week3_repo.py \
    --model $MODEL --repos $REPOS --eta 4e-2 \
    --general_limit 500 --lags 0,5,15,40 \
    --policy persist \
    --out "$OUT/persist_4e-2.json"
echo "persist@4e-2 完成: $(date)"

echo "=== 生成分析 ==="
python scripts/horizon.py "$OUT"/*.json | tee "$OUT/horizon.txt"

echo "=== Week 5b 诊断完成 ==="
echo "结束时间: $(date)"
