#!/usr/bin/env bash
# Week-1 sanity on GPU1: does persistence buy cross-file recall, and does it cost anything?
# Usage: CUDA_VISIBLE_DEVICES=1 bash scripts/week1.sh
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos}
OUT=${OUT:-results/week1}
mkdir -p "$OUT"

# 1) clone a small, permissively-licensed set of Python repos (edit scripts/repos.txt to taste)
if [ ! -d "$REPOS" ] || [ -z "$(ls -A "$REPOS")" ]; then
  mkdir -p "$REPOS"
  while read -r url; do
    [ -z "$url" ] && continue
    name=$(basename "$url" .git)
    [ -d "$REPOS/$name" ] || git clone --depth 1 -q "$url" "$REPOS/$name"
  done < scripts/repos.txt
fi

# 2) frozen lower bound
python run.py --model "$MODEL" --repos "$REPOS" --policy base --out "$OUT/base.json"

# 3) reset vs persist across a small eta sweep (the motivation figure)
for eta in 3e-4 1e-3 3e-3; do
  python run.py --model "$MODEL" --repos "$REPOS" --policy reset   --eta $eta --clip $eta --out "$OUT/reset_eta${eta}.json"
  python run.py --model "$MODEL" --repos "$REPOS" --policy persist --eta $eta --clip $eta --out "$OUT/persist_eta${eta}.json"
done

python scripts/summarize.py "$OUT"/*.json | tee "$OUT/summary.txt"
