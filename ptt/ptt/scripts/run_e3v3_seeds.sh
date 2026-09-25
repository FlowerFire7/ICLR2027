#!/usr/bin/env bash
# E3v3 seeds 1/2：四策略（base, persist, consistency, random）
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

echo "=== E3v3 seeds 1/2 ==="
echo "开始时间: $(date)"

for seed in 1 2; do
    echo "--- seed $seed ---"
    C="--model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 30 --eta 1e-2 --lags 0,5,15,40 --seed $seed --general_cache results/e3v3/gen_before_e3.json"
    
    for p in base persist; do
        echo "[$p @ seed$seed]..."
        python scripts/run_entity.py $C --policy $p --out results/e3v3/${p}_s${seed}.json
    done
    
    python scripts/run_entity.py $C --policy consistency --alpha_norm --out results/e3v3/consistency_s${seed}.json
    python scripts/run_entity.py $C --policy random --alpha_norm --out results/e3v3/random_s${seed}.json
    
    echo "seed $seed 完成: $(date)"
done

echo "=== E3v3 seeds 1/2 完成 ==="
echo "结束时间: $(date)"
