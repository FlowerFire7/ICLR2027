#!/usr/bin/env bash
# E3v3 seed 2 ONLY - with --fresh 100 for tighter CI
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

echo "=== E3v3 seed 2 (fresh=100) ==="
echo "开始时间: $(date)"

C="--model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 100 --eta 1e-2 --lags 0,5,15,40 --seed 2 --general_cache results/e3v3/gen_before_e3.json"

for p in base persist; do
    echo "[$p @ seed2]..."
    python scripts/run_entity.py $C --policy $p --out results/e3v3/${p}_s2.json
done

python scripts/run_entity.py $C --policy consistency --alpha_norm --out results/e3v3/consistency_s2.json
python scripts/run_entity.py $C --policy random --alpha_norm --out results/e3v3/random_s2.json

echo "=== E3v3 seed 2 完成 ==="
echo "结束时间: $(date)"
