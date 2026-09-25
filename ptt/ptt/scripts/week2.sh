#!/usr/bin/env bash
# Week 2: all seven policies on a 50-repo obfuscated S-Repo stream, with
#   * general-capability retention (lm-eval hellaswag + arc_easy, 500 items, before/after)
#   * backward transfer on the first 20 documents (re-scored at the end of the stream)
# Usage: CUDA_VISIBLE_DEVICES=1 bash scripts/week2.sh
set -e
MODEL=${MODEL:-Qwen/Qwen3-0.6B-Base}
REPOS=${REPOS:-repos50}
OUT=${OUT:-results/week2}
mkdir -p "$OUT"
[ -d "$REPOS" ] || python scripts/fetch_repos.py --n 50 --out "$REPOS"
COMMON="--model $MODEL --repos $REPOS --chunk 256 --ctx_len 1024 --general_eval hellaswag,arc_easy --general_limit 500 --retest_first_k 20"

python run.py $COMMON --policy base --out "$OUT/base.json"
for eta in 1e-2 3e-2; do
  for pol in reset persist decay consistency fisher surprise random; do
    python run.py $COMMON --policy $pol --eta $eta --clip $eta --out "$OUT/${pol}_eta${eta}.json"
  done
done
# where does persist collapse?
python run.py $COMMON --policy persist --eta 1e-1 --clip 1e-1 --out "$OUT/persist_eta1e-1.json"
python scripts/summarize.py "$OUT"/*.json | tee "$OUT/summary.txt"
