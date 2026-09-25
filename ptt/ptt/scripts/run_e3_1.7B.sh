#!/usr/bin/env bash
# E3 @ 1.7B: 实体流，seed 0，五策略
# 用于复现长尾和 placement 效应
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

C="--model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 30 --eta 3e-2 --lags 0,5,15,40 \
   --general_cache results/e3/gen_before_e3.json"

echo "=== E3 @ 1.7B (实体流, seed 0, 五策略) ==="
echo "开始时间: $(date)"

echo "[1/5] base..."
python scripts/run_entity.py $C --policy base --out results/e3/base_s0.json
echo "base_s0 完成: $(date)"

echo "[2/5] persist..."
python scripts/run_entity.py $C --policy persist --out results/e3/persist_s0.json
echo "persist_s0 完成: $(date)"

echo "[3/5] session..."
python scripts/run_entity.py $C --policy session --out results/e3/session_s0.json
echo "session_s0 完成: $(date)"

echo "[4/5] consistency_norm..."
python scripts/run_entity.py $C --policy consistency --alpha_norm --out results/e3/consistency_s0.json
echo "consistency_s0 完成: $(date)"

echo "[5/5] random_norm..."
python scripts/run_entity.py $C --policy random --alpha_norm --out results/e3/random_s0.json
echo "random_s0 完成: $(date)"

echo "=== E3 seed 0 完成 ==="
echo "结束时间: $(date)"

echo "--- 配对检验 ---"
python scripts/paired.py results/e3/consistency_s0.json results/e3/random_s0.json
python scripts/paired.py results/e3/persist_s0.json results/e3/base_s0.json
