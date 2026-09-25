#!/usr/bin/env bash
# E3v2 正式批次：η*=1e-2，修复后的实体流（独立音节池 + fresh PPL）
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

echo "=== E3v2 正式批次 (η=1e-2) ==="
echo "开始时间: $(date)"

C="--model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 30 --eta 1e-2 --lags 0,5,15,40 --general_cache results/e3v2/gen_before_e3.json"

echo "[1/5] base..."
python scripts/run_entity.py $C --policy base --out results/e3v2/base_s0.json
echo "base 完成: $(date)"

echo "[2/5] persist..."
python scripts/run_entity.py $C --policy persist --out results/e3v2/persist_s0.json
echo "persist 完成: $(date)"
# 检查 hellaswag 税
python3 -c "
import json
d = json.load(open('results/e3v2/persist_s0.json'))
b = json.load(open('results/e3v2/gen_before_e3.json'))
dh = (d['summary']['general_after']['hellaswag'] - b['hellaswag']) * 100
print(f'>>> persist hellaswag 税: {dh:+.1f}pt (目标: -2±2pt)')
if abs(dh + 2) > 2:
    print('>>> ⚠️ 警告：税偏离超过 2pt，考虑重校准')
"

echo "[3/5] session..."
python scripts/run_entity.py $C --policy session --out results/e3v2/session_s0.json
echo "session 完成: $(date)"

echo "[4/5] consistency_norm..."
python scripts/run_entity.py $C --policy consistency --alpha_norm --out results/e3v2/consistency_s0.json
echo "consistency 完成: $(date)"

echo "[5/5] random_norm..."
python scripts/run_entity.py $C --policy random --alpha_norm --out results/e3v2/random_s0.json
echo "random 完成: $(date)"

echo "=== E3v2 seed 0 完成 ==="
echo "结束时间: $(date)"
