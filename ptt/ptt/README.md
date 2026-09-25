# ptt — Persistent Test-Time Training (week-1 package)

Drop-in, training-free test-time training on the MLP down-projections of a pretrained LLM,
with a family of **persistence policies** applied at document boundaries.

```
W_eff = W_base + G_slow + G_fast
G_fast : clipped gradient step on the NTP loss of each chunk (apply-then-update)
G_slow : written at document boundaries by --policy
D      : cross-document direction EMA (consistency policy)
```

| `--policy`   | boundary rule                                              |
|--------------|------------------------------------------------------------|
| base         | no writes at all (frozen lower bound)                      |
| reset        | G_fast ← 0 (In-Place TTT default)                          |
| persist      | G_slow += G_fast                                           |
| decay        | G_slow ← γ·G_slow + G_fast (default γ=0.9)                 |
| consistency  | D ← γ_d D + (1−γ_d) sign(G_fast); G_slow ← γG_slow + |D|⊙G_fast (first doc = warm-up) |
| fisher       | G_slow ← γG_slow + (1 − F̂/max F̂)⊙G_fast                   |
| surprise     | scalar gate σ((first-chunk loss − running mean)/τ)         |
| random       | same α histogram as consistency, randomly permuted (control) |

## Install
```
pip install -r requirements.txt
```
Qwen3 needs `transformers>=4.51`.

## Week-1 sanity (GPU1)
```
CUDA_VISIBLE_DEVICES=1 bash scripts/week1.sh        # clones repos, runs base / reset / persist × 3 etas
python scripts/summarize.py results/week1/*.json
```
What to look for (plan v2 §7, week 1 gate):
* `xfile>=2` column (cross-file identifier accuracy on files ≥ 2 of each repo): **persist ≫ reset ≈ base** by ≥ 3 points at some η.
* `local` column should be similar across policies (control).
* `docPPL` should be ≤ base for all TTT policies; if `persist` starts *above* base at large η, that is the drift we will study in week 2.

Single run:
```
python run.py --model Qwen/Qwen3-0.6B-Base --repos repos --policy consistency --eta 1e-3 --clip 1e-3 \
              --gamma_d 0.9 --chunk 1024 --ctx_len 1024 --out results/consistency.json
```
Useful flags: `--layers top3|mid3|bot3|0,5,11`, `--max_repos N`, `--max_docs N`, `--grad_ckpt` (4B), `--seed`.

## Tests (CPU, tiny random GPT-2, ~20 s)
```
python tests/test_causality.py
```
Guarantees the leak-freedom checklist (plan §F): eval-only never touches weights; every recorded chunk loss
is computed *before* that chunk is written; `reset` equals processing documents in isolation;
`persist == decay(γ=1)`; `random` has exactly the consistency gate's α histogram.

## Output JSON
* `records`: per chunk — loss, and for each mask `xfile`/`local`: correct, nll, n (prequential).
* `docs`: per document — ppl, mask accuracies, boundary stats (`b_alpha_mean`, `b_g_slow_norm`), repo/file index.
* `summary`, `config`, `wall_s`, `peak_mem_gb`.

## Layout
```
ptt/fastweight.py     fast-weight state + policies
ptt/runner.py         chunk-wise apply-then-update loop, prequential metrics
ptt/streams/repo.py   S-Repo stream (dependency-ordered files, cross-file identifier masks)
ptt/eval/general.py   lm-eval-harness wrapper for before/after general-capability retention (week 2)
run.py                CLI
scripts/week1.sh      week-1 sweep;  scripts/summarize.py  table
tests/                causality / policy-identity tests
```

## Week-2 hooks (not yet implemented)
* `ptt/streams/domain.py` — S-Domain (6 domains × 3M tokens) with held-out per-domain eval sets.
* `--general_eval` flag in `run.py` calling `ptt.eval.general.eval_general` before/after the stream.
* Hebbian write variant (`--write hebbian`) for the ablation.
