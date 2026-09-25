#!/usr/bin/env bash
# E3 η 校准：找出通用能力税落在 -2~3 点的 η*
set -e
cd /data/ziming_workspace/kaiyi/ICLR/ptt/ptt

echo "=== E3 η 校准 ==="
echo "开始时间: $(date)"

echo "[1/2] persist @ η=3e-3..."
python scripts/run_entity.py --model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 30 \
    --eta 3e-3 --lags 0,5,15,40 --policy persist \
    --general_cache results/e3/gen_before_e3.json \
    --out results/e3/persist_eta3e-3.json
echo "persist@3e-3 完成: $(date)"

echo "[2/2] persist @ η=1e-2..."
python scripts/run_entity.py --model Qwen/Qwen3-1.7B-Base --n_articles 300 --fresh 30 \
    --eta 1e-2 --lags 0,5,15,40 --policy persist \
    --general_cache results/e3/gen_before_e3.json \
    --out results/e3/persist_eta1e-2.json
echo "persist@1e-2 完成: $(date)"

echo "=== η 校准完成 ==="
echo "结束时间: $(date)"

# 输出 general 对比
python3 << 'PYEOF'
import json
print("\n=== General 对比 (BEFORE vs AFTER) ===")
before = json.load(open('results/e3/gen_before_e3.json'))
for eta in ['3e-3', '1e-2', '3e-2']:
    fname = f'results/e3/persist_eta{eta}.json' if eta != '3e-2' else 'results/e3/persist_s0.json'
    try:
        d = json.load(open(fname))
        after = d['summary']['general_after']
        dh = after['hellaswag'] - before['hellaswag']
        da = after['arc_easy'] - before['arc_easy']
        print(f"η={eta}: hellaswag {dh*100:+.1f}pt, arc_easy {da*100:+.1f}pt")
    except:
        pass
PYEOF
