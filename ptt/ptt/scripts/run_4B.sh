#!/usr/bin/env bash
# 4B 四策略：base, persist, consistency_norm, random_norm @ 代码流 η=3e-2
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

echo "=== 4B 规模验证 ==="
echo "开始时间: $(date)"

C="--model Qwen/Qwen3-4B-Base --repos repos180 --fresh_repos repos_fresh --eta 3e-2 --clip 3e-2 --chunk 256 --ctx_len 1024 --seed 0 --lags 0,5,15,40 --general_cache results/e2_4B/gen_before_4B.json"

echo "[1/4] base..."
python scripts/week3_repo.py $C --policy base --out results/e2_4B/base_s0.json
echo "base 完成: $(date)"

echo "[2/4] persist..."
python scripts/week3_repo.py $C --policy persist --out results/e2_4B/persist_s0.json
echo "persist 完成: $(date)"

echo "[3/4] consistency_norm..."
python scripts/week3_repo.py $C --policy consistency --alpha_norm --out results/e2_4B/consistency_s0.json
echo "consistency 完成: $(date)"

echo "[4/4] random_norm..."
python scripts/week3_repo.py $C --policy random --alpha_norm --out results/e2_4B/random_s0.json
echo "random 完成: $(date)"

echo "=== 4B 完成 ==="
echo "结束时间: $(date)"
