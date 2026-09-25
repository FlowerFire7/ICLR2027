#!/usr/bin/env bash
set -e

CACHE=results/e1/gen_before_1.7B.json
C="--model Qwen/Qwen3-1.7B-Base --repos repos180 --eta 3e-2 --lags 0,5,15,40 \
   --fresh_repos repos_fresh --general_limit 2000 --general_cache $CACHE"

echo "=== E1 主表 (1.7B × 5策略 × 3seeds, general_limit=2000) ==="
echo "开始时间: $(date)"

for s in 0 1 2; do
  echo "=== Seed $s ===" 
  echo "[s${s}.1/5] base..."
  python scripts/week3_repo.py $C --seed $s --policy base --out results/e1/base_s$s.json
  echo "base_s$s 完成: $(date)"
  
  echo "[s${s}.2/5] persist..."
  python scripts/week3_repo.py $C --seed $s --policy persist --out results/e1/persist_s$s.json
  echo "persist_s$s 完成: $(date)"
  
  echo "[s${s}.3/5] session..."
  python scripts/week3_repo.py $C --seed $s --policy session --out results/e1/session_s$s.json
  echo "session_s$s 完成: $(date)"
  
  echo "[s${s}.4/5] consistency_norm..."
  python scripts/week3_repo.py $C --seed $s --policy consistency --alpha_norm --out results/e1/consistency_s$s.json
  echo "consistency_s$s 完成: $(date)"
  
  echo "[s${s}.5/5] random_norm..."
  python scripts/week3_repo.py $C --seed $s --policy random --alpha_norm --out results/e1/random_s$s.json
  echo "random_s$s 完成: $(date)"
done

echo "=== 生成 CI 分析 ==="
python scripts/cluster_ci.py results/e1/*.json | tee results/e1/ci.txt

echo "=== E1 全部完成 ==="
echo "结束时间: $(date)"
