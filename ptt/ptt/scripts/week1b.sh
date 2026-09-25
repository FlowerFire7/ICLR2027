#!/usr/bin/env bash
# Week-1 rerun after diagnosis: obfuscated identifiers (no pre-training leakage), first-occurrence-only
# cross-file metric, chunk=256 so that within-document writes actually apply.
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos}
OUT=${OUT:-results/week1b}
mkdir -p "$OUT"
COMMON="--model $MODEL --repos $REPOS --chunk 256 --ctx_len 1024"

python run.py $COMMON --policy base --out "$OUT/base.json"
for eta in 1e-3 3e-3 1e-2 3e-2; do
  python run.py $COMMON --policy reset   --eta $eta --clip $eta --out "$OUT/reset_eta${eta}.json"
  python run.py $COMMON --policy persist --eta $eta --clip $eta --out "$OUT/persist_eta${eta}.json"
done
# sanity: same stream WITHOUT obfuscation, to quantify pre-training contamination
python run.py $COMMON --policy base --no_obfuscate --out "$OUT/base_noobf.json"
python scripts/summarize.py "$OUT"/*.json | tee "$OUT/summary.txt"
