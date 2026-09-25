#!/usr/bin/env bash
set -e
MODEL=Qwen/Qwen3-1.7B-Base
REPOS=repos180
FRESH=repos_fresh
OUT=results/e1
ETA=3e-2
mkdir -p "$OUT"

run_seed() {
    local SEED=$1
    local C="--model $MODEL --repos $REPOS --fresh_repos $FRESH --eta $ETA --seed $SEED"
    C="$C --general_limit 500 --lags 0,5,15,40"
    
    echo "=== Seed $SEED ===" 
    echo "[${SEED}.1] base..."
    python scripts/week3_repo.py $C --policy base --out "$OUT/base_s${SEED}.json"
    echo "base_s${SEED} 完成: $(date)"
    
    echo "[${SEED}.2] persist..."
    python scripts/week3_repo.py $C --policy persist --out "$OUT/persist_s${SEED}.json"
    echo "persist_s${SEED} 完成: $(date)"
    
    echo "[${SEED}.3] session..."
    python scripts/week3_repo.py $C --policy session --out "$OUT/session_s${SEED}.json"
    echo "session_s${SEED} 完成: $(date)"
    
    echo "[${SEED}.4] consistency_norm..."
    python scripts/week3_repo.py $C --policy consistency --alpha_norm --out "$OUT/consistency_norm_s${SEED}.json"
    echo "consistency_norm_s${SEED} 完成: $(date)"
    
    echo "[${SEED}.5] random_norm..."
    python scripts/week3_repo.py $C --policy random --alpha_norm --out "$OUT/random_norm_s${SEED}.json"
    echo "random_norm_s${SEED} 完成: $(date)"
}

echo "=== E1 主表 (1.7B × 5策略 × 3seeds = 15次) ==="
echo "开始时间: $(date)"

run_seed 0
run_seed 1
run_seed 2

echo "=== 生成 horizon 分析 ==="
python scripts/horizon.py "$OUT"/*.json | tee "$OUT/horizon.txt"

echo "=== E1 全部完成 ==="
echo "结束时间: $(date)"
