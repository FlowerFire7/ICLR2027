#!/usr/bin/env bash
# E3v3: per-session cipher (字母置换)，fresh PPL 记录
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

echo "=== E3v3 (per-session cipher) ==="
echo "开始时间: $(date)"

C="--model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 30 --eta 1e-2 --lags 0,5,15,40 --general_cache results/e3v3/gen_before_e3.json"

for p in base persist session; do 
    echo "[$p]..."
    python scripts/run_entity.py $C --policy $p --out results/e3v3/${p}_s0.json
    echo "$p 完成: $(date)"
done

python scripts/run_entity.py $C --policy consistency --alpha_norm --out results/e3v3/consistency_s0.json
echo "consistency 完成: $(date)"

python scripts/run_entity.py $C --policy random --alpha_norm --out results/e3v3/random_s0.json
echo "random 完成: $(date)"

echo "=== E3v3 完成 ==="
echo "结束时间: $(date)"
