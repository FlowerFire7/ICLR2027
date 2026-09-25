#!/usr/bin/env bash
# E1c: 剩余 9 次运行 (ptt_e1c.zip - random GPU 修复版)
# 已完成: base_s0, persist_s0, session_s0, consistency_s0, random_s0, base_s1, persist_s1
# 待跑: session_s1, consistency_s1, random_s1, base_s2, persist_s2, session_s2, consistency_s2, random_s2
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

CACHE=results/e1/gen_before_1.7B.json
C="--model Qwen/Qwen3-1.7B-Base --repos repos180 --eta 3e-2 --lags 0,5,15,40 \
   --fresh_repos repos_fresh --general_limit 2000 --general_cache $CACHE"

echo "=== E1c 继续运行 (ptt_e1c.zip - random GPU修复版) ==="
echo "开始时间: $(date)"

# Seed 1 剩余
echo "=== Seed 1 (剩余 3 次) ==="

echo "[s1.3/5] session..."
python scripts/week3_repo.py $C --seed 1 --policy session --out results/e1/session_s1.json
echo "session_s1 完成: $(date)"

echo "[s1.4/5] consistency_norm..."
python scripts/week3_repo.py $C --seed 1 --policy consistency --alpha_norm --out results/e1/consistency_s1.json
echo "consistency_s1 完成: $(date)"

echo "[s1.5/5] random_norm..."
python scripts/week3_repo.py $C --seed 1 --policy random --alpha_norm --out results/e1/random_s1.json
echo "random_s1 完成: $(date)"

# Seed 2 全部
echo "=== Seed 2 (全部 5 次) ==="

echo "[s2.1/5] base..."
python scripts/week3_repo.py $C --seed 2 --policy base --out results/e1/base_s2.json
echo "base_s2 完成: $(date)"

echo "[s2.2/5] persist..."
python scripts/week3_repo.py $C --seed 2 --policy persist --out results/e1/persist_s2.json
echo "persist_s2 完成: $(date)"

echo "[s2.3/5] session..."
python scripts/week3_repo.py $C --seed 2 --policy session --out results/e1/session_s2.json
echo "session_s2 完成: $(date)"

echo "[s2.4/5] consistency_norm..."
python scripts/week3_repo.py $C --seed 2 --policy consistency --alpha_norm --out results/e1/consistency_s2.json
echo "consistency_s2 完成: $(date)"

echo "[s2.5/5] random_norm..."
python scripts/week3_repo.py $C --seed 2 --policy random --alpha_norm --out results/e1/random_s2.json
echo "random_s2 完成: $(date)"

echo "=== 生成分析 ==="
echo "--- cluster_ci ---"
python scripts/cluster_ci.py results/e1/*.json | tee results/e1/ci.txt

echo "--- paired comparisons (per seed) ---"
> results/e1/paired.txt
for s in 0 1 2; do
  echo "=== Seed $s paired ===" | tee -a results/e1/paired.txt
  echo "consistency vs random:" | tee -a results/e1/paired.txt
  python scripts/paired.py results/e1/consistency_s$s.json results/e1/random_s$s.json 2>/dev/null | tee -a results/e1/paired.txt || echo "skipped (file missing)"
  echo "consistency vs persist:" | tee -a results/e1/paired.txt
  python scripts/paired.py results/e1/consistency_s$s.json results/e1/persist_s$s.json 2>/dev/null | tee -a results/e1/paired.txt || echo "skipped (file missing)"
  echo "session vs persist:" | tee -a results/e1/paired.txt
  python scripts/paired.py results/e1/session_s$s.json results/e1/persist_s$s.json 2>/dev/null | tee -a results/e1/paired.txt || echo "skipped (file missing)"
done

echo "=== E1c 全部完成 ==="
echo "结束时间: $(date)"
