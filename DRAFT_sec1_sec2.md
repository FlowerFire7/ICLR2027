# Draft §1–§2 (English, LaTeX-ready prose; v0.1, 2026-09-02; outcome-A framing, [x.x] = fill from E1)

## 1. Introduction

Test-time training (TTT) has become a standard way to adapt language models to their input stream:
fast weights — most commonly the MLP down-projections — are updated on the fly as tokens arrive, and
the approach now spans architectures trained for it (Titans, LaCT, TTT-E2E) and drop-in variants that
retrofit pretrained models (In-Place TTT, TTT-NTP). All of these share one quiet design decision: fast
weights are **reset at document boundaries**. The model may adapt within a context, but remembers
nothing across contexts.

Real workloads are not isolated documents. A coding assistant sees file after file of the same
repository; an enterprise assistant sees the same organization's reports for months. Between "reset
every document" and "never reset" lies a question that, to our knowledge, has not been measured:
**if fast weights persist, what do they actually remember, for how long, and at what cost?**

Measuring this is harder than it looks, which may explain why it has not been done. We document four
traps that each silently corrupt the answer. (i) *Pre-training contamination*: on unmodified popular
repositories, a frozen model already "recalls" 38.1% of cross-file identifiers; renaming symbols drops
this to 1.7%. (ii) *In-context copying*: all but the first mention of a symbol in a document can be
predicted by induction from context, not memory. (iii) *Shared-vocabulary artifacts*: we show how a
subtle correlated-renaming bug manufactures a phantom long-term memory (2× inflated recall at lag 40)
— a cautionary case we believe generalizes to other synthetic-memory evaluations. (iv) *Evaluation
leakage*, whose consequences the community has already seen in a retracted TTT result. Our first
contribution is a protocol — obfuscated session streams, first-mention targets, fixed-lag re-scoring,
equal-budget gating with a random-placement control, a fresh-session transfer control, and
unit-tested leak-freedom — that closes all four.

Our second contribution is the measurement itself. Across 200-session code streams and article-entity
streams, on models from 0.6B to [4B], persistent fast weights deliver a large recall benefit at short
range — [8.8]× over the frozen model at lag 0 — that decays with a half-life of *under five sessions*
and is statistically indistinguishable from baseline by lag 40. A simple linear-interference model
predicts that excess recall depends only on the ratio of a session's write mass to the mass written
after it; the measured curves collapse accordingly, and are invariant to the learning rate over a 2×
range, as the model predicts. Meanwhile the costs are sharply nonlinear: general capability is intact
up to a knee (η between 3·10⁻² and 4·10⁻²) and collapses beyond it.

The practical conclusion is almost embarrassingly simple, and we verify it head-to-head:
**resetting at session rather than document granularity captures [87]% of the memory benefit with
zero measured drift** — while every parameter-statistic gate we tested (consistency, Fisher,
surprise, decay), granted the *same write budget* as unrestricted persistence, fails to beat a
random-placement control at extending the horizon, and the consistency gate reproducibly *harms*
general capability, an effect our analysis explains: gating by cross-document agreement concentrates
writes along the stream's systematic drift direction (Prop. 2).

Contributions. **(1)** The Streaming-TTT protocol and benchmark (code, streams, and unit tests
released), including two documented evaluation traps we believe the field will otherwise rediscover
the hard way. **(2)** The first systematic measurement of the persistence horizon of drop-in TTT:
policies × lags × scales × two stream types, with pre-registered hypotheses and session-clustered
intervals. **(3)** A linear-interference account whose two falsifiable predictions (mass-ratio
collapse; η-invariance) the data confirm, connecting TTT memory to classical palimpsest theories of
synaptic consolidation. **(4)** A negative result with teeth: equal-budget parameter-statistic gating
does not extend the horizon, and its most popular instantiation is actively harmful — evidence we
hope redirects effort toward mechanisms that operate in activation space or learn their gates.

## 2. Related Work

**TTT and fast weights.** Fast weight memories date to Schmidhuber (1992) and Ba et al. (2016);
linear attention is their modern form (Katharopoulos et al., 2020; Schlag et al., 2021). Contemporary
TTT instantiates them as inner-loop learners: TTT-Linear/MLP (Sun et al., 2024), LaCT (Zhang et al.,
2025), TTT-E2E (Tandon et al., 2025), Titans (Behrouz et al., 2025), HOPE (Behrouz et al., 2025),
DeltaNet variants (Yang et al., 2024; 2025), and drop-in retrofits In-Place TTT (Feng et al., 2026)
and TTT-NTP (Ouyang et al., 2026), plus single-input adaptation (Hardt & Sun, 2024; Hübotter et al.,
2025; qTTT; ETT). *All reset per sequence or per document, or require (meta-)training; none measures
cross-session retention.* We adopt In-Place TTT's fast-weight location and chunk-wise schedule, and
study precisely the axis it holds fixed.

**Continuous TTT inside agent episodes.** Concurrent work updates fast weights continuously within
multi-turn agent rollouts (Agentic TTT, 2026) or across search iterations (TTT-Discover, 2026). *The
stream there is the model's own text within one episode; ours is an exogenous document stream across
sessions, and our object of study is retention, not policy drift.*

**Context-to-weights persistence.** Temp-LoRA (Wang et al., 2024), StreamAdapter (2024), InfiniteICL
(Cao et al., 2025), SCoL (2026), CaMeLS (Hu et al., 2023), and MAC (Tack et al., 2024) write context
into parameters, several requiring meta-training, and several noted to erode general capability.
*They propose mechanisms; we contribute the measurement framework such mechanisms should be judged
by, and apply it to the training-free case.*

**Continual test-time adaptation in vision.** CoTTA (Wang et al., 2022), EATA (Niu et al., 2022),
SAR (Niu et al., 2023), and Elastic TTT (Ma et al., 2026) stabilize non-reset adaptation for
classification and reconstruction — EATA and Elastic TTT with Fisher-weighted penalties. *We evaluate
the same idea as one member of our policy family and find that in the LM setting it does not beat
random placement at equal budget; the recall-with-lag axis has no analogue in this literature.*

**Memory theory.** Palimpsest models (Parisi, 1986), cascade synapses (Fusi et al., 2005), and
Benna–Fusi (2016) analyze memories overwritten by ongoing plasticity, predicting decay governed by
subsequent write load rather than elapsed time. *Our mass-ratio collapse is, to our knowledge, the
first measurement of this signature in a large language model's fast weights.* Classical continual
learning contributes the regularizers we gate with (EWC, SI, MAS) and our transfer metrics
(Lopez-Paz & Ranzato, 2017; Chaudhry et al., 2018).

*Port note: keep each italicized distinction sentence — they are the anticipated-reviewer-question
answers. Citation keys per outline v2 §D; verify TTT-NTP author list and Agentic TTT venue at camera-ready.*
