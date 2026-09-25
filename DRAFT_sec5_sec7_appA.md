# Draft §5–§7 skeleton + Appendix A (v0.1, 2026-09-05; fill-ins keyed to results/e1, e3, e4)

## 5. Results

*(Every subsection: claim sentence first; figure/table; statistics. All intervals are session-clustered
bootstrap 95% CIs; paired comparisons use shared holdouts. Numbers in ⟨⟩ from seed-0 only, to be
replaced by 3-seed values.)*

### 5.1 Reset discards nearly everything persistence provides
Claim: at lag 0, persistence yields ⟨7.1×⟩ the frozen baseline's first-mention recall, while
per-document reset is indistinguishable from frozen. — Fig. 2 (left); Table 3 rows base/reset/persist.
Stats: H1 (persist > reset @ lag 0), paired, Holm.

### 5.2 The horizon: fast, load-dependent decay
Claim: excess recall halves within 5 sessions and is indistinguishable from baseline by lag 40
(⟨0.073→0.027→0.019→0.013⟩ vs base ⟨0.010⟩); the shape replicates across 0.6B→1.7B→[4B] and across
code and entity streams. — Fig. 2; Fig. 3 (scale); Table 4 (E3). Stats: H2 at lag 40 (expected *not*
rejected → reported as an equivalence statement with the CI, not as "proof of zero").

### 5.3 Interference, not time: the mass-ratio collapse
Claim: plotted against ρ = m_k²/Σ_{j>k}^{lag} m_j², curves from η ∈ {2,3,4}·10⁻² and from both
stream types collapse onto one function; lag-curves are η-invariant as P1 predicts
(normalized lag-5 retention ⟨0.27/0.24/0.21⟩). — Fig. 4. Stats: exploratory; report R² of the pooled
fit and the per-η deviation.

### 5.4 The knee: benefits are linear, costs are not
Claim: raising η from 3·10⁻² to 4·10⁻² buys ⟨+0.007⟩ lag-0 recall and costs ⟨−0.069⟩ mean general
capability (0.6B; [1.7B pending]); below the knee, per-task movements are within ±[x] pt across 5
tasks. — Fig. 5 (η sweep, per-task panels). Stats: per-task CIs at 2000 items; no averaging across
tasks in headline claims (App. D shows task-opposite movements that averaging would hide).

### 5.5 Session-granularity reset: the operating point
Claim: session-level persistence captures ⟨~87%⟩ of the memory excess (after subtracting
fresh-session transfer, itself ⟨0.0084⟩ against the matched base-fresh reference) with general
capability movements within noise on all 5 tasks; the residual persist−session gap at lag 0 is
⟨+0.0016⟩ [CI], unattributed. — Table 3; Fig. 2. Stats: paired session vs persist; fresh-transfer CI
from per-fresh-repo clusters.

### 5.6 Placement: parameter-statistic gates, and a scale-dependent surprise
Claim (branch pending 3 seeds + random):
(a) If consistency−random paired diffs at lag 0/5 exclude zero at 1.7B: "equal-budget consistency
gating buys ⟨+0.010/+0.006⟩ short-lag recall at 1.7B but not at 0.6B — placement information emerges
with scale; the gate still does not extend the horizon (lag 15/40 diffs ≈ 0) and still costs
HellaSwag (⟨−3.8⟩ vs persist's ⟨−2.6⟩), consistent with Prop. 2's drift-concentration account.
H3's pre-registered equivalence is rejected — in the direction opposite to the folk intuition it
was designed to test."
(b) If CIs include zero: H3 equivalence affirmed at ±2pt; consistency reported as
no-better-than-random with the general-capability penalty. — Fig. 6; Table 5. Stats: TOST or its
rejection; three paired families, Holm.

### 5.7 What the gates cannot do, the projection does — at a price
Claim: activation-subspace projection is the only intervention that raises mid-lag retention
(⟨0.025 vs 0.020⟩ at lag 15/40, 0.6B), but halves lag-0 plasticity at k=64 and eliminates it at
k=256: a knob on the plasticity–retention frontier, not a free win. — Fig. 6 (frontier). Exploratory.

### 5.8 An unexpected observation [keep only if it survives 5 tasks × 3 seeds]
Streaming obfuscated code reliably moves ARC-Easy up (⟨+4.4⟩ pt at 1.7B) while HellaSwag moves down.
[If consistent across seeds and sibling tasks: report as an open observation with format-drift
controls (logit-margin analysis; choice-order shuffle); do not claim a mechanism. If not: App. D
footnote.]

### 5.9 Costs
Extra memory = 2× fast-weight footprint (G_fast+G_slow; +D for consistency, +basis for projection);
throughput ⟨0.40×⟩ of frozen inference (121 vs 53 min/stream at 1.7B); table with per-policy states.

## 6. Discussion and Limitations
- Scope: language-model recall/PPL-style measures; one architecture family (+GPT-2 XL appendix);
  training-free gradient writes (Hebbian ablation App. [x]).
- The linear model is a measurement instrument; its assumptions (isotropic sessions) are engineered
  into the benchmark by per-session vocabularies and need not hold for natural streams — natural-
  stream ρ-collapse is untested and flagged as open.
- Gates studied are parameter-statistic heuristics; learned gates (Titans, SCoL) and replay are out
  of scope — our claim is about what training-free gating cannot do, not what gating cannot do.
- Fresh-transfer control has 65 sessions; residual persist−session gap remains unattributed.
- Societal: persistent adaptation on user streams raises retention/privacy questions; session-reset
  is also the privacy-conservative default.

## 7. Conclusion
Three sentences: measured horizon; interference law; session-reset recipe + gate negative result.
Close with: "the right question for persistent TTT is not *whether* to remember but *how much load*
a memory can survive — and that question now has a measurement."

---

# Appendix A. Proofs

**Setup.** Fast weight G ∈ R^{d_out×d}, sessions write Δ_1, Δ_2, …, m_k = ‖Δ_k‖_F. Assumption A1
(independence): {Δ_j} mutually independent, E[Δ_j]=0 across the vocabulary randomization. Assumption
A2 (isotropy): a probe v of session k satisfies E[vvᵀ]=I_d/d and v ⫫ {Δ_j}_{j≠k}. (Both are *design
properties of the benchmark*: per-session RNG vocabularies make session writes exchangeable with
random rotations; App. B quantifies residual cross-session correlation ⟨r²=...⟩.)

**Prop. 1.** For j≠k: E‖Δ_j v‖² = E tr(Δ_jᵀΔ_j vvᵀ) = tr(E[Δ_jᵀΔ_j]·E[vvᵀ]) = m_j²/d (A2, then A1).
Cross terms E⟨Δ_i v, Δ_j v⟩ = 0 for i≠j (A1, zero mean). Hence the interference power at lag L is
Σ_{j=k+1}^{k+L} m_j²/d and SNR(k,L) = ‖Δ_k v‖ / √(Σ m_j²/d) = √d·c_k m_k/√(Σ_{j>k}^{L} m_j²) with
c_k := ‖Δ_k v‖/m_k ≤ 1 by Cauchy–Schwarz. ∎
*Remark (link to accuracy).* Recall accuracy is a monotone function of SNR under a Gaussian-
interference, fixed-margin readout; we do not rely on the specific form, only on monotonicity, which
is what the collapse test checks.
*Remark (η-invariance and its failure mode).* If m_j = η·t_j·κ(η) with κ capturing clipping, ρ is
η-free whenever κ is; systematic extra decay at large η therefore isolates non-write-mass effects
(clip saturation; drift of W_base's computation, observable as ΔGen).

**Prop. 2.** D_t = γ_d D_{t−1} + (1−γ_d)s_t, s_t iid, P(s_t=+1)=p. Stationarity: E[D]=2p−1;
Var[D] = (1−γ_d)/(1+γ_d)·(1−(2p−1)²). E[Π]=E|D| ≥ |E D| = |2p−1| (Jensen), → equality as γ_d→1 since
Var→0. Corollary: coordinates with p≈½ (one-shot content) get Π→0 as γ_d→1; coordinates with
persistent sign (systematic drift) get Π→1, so the normalized gate re-allocates write mass toward
the drift direction. ∎

**Prop. 3.** Each chunk write is element-wise clipped by m over N parameters: ‖δ‖_F ≤ m√N. Triangle
inequality over T writes: ‖G‖_F ≤ m√N·T; with boundary decay γ, the geometric series gives
m√N·T_s/(1−γ) for T_s writes per session. ∎

**Prop. 4.** Under session policy, G at the start of session k+1 is 0, so for any probe of session k
at lag ≥ 1 both signal and interference vanish identically; within a session the update sequence is
identical to persist. Hence session realizes the (plasticity, cross-session-risk) pair
(persist@lag0, 0). ∎

*App. B note-to-self: measure A1/A2 empirically — cosine of Δ_k between sessions; report the
distribution to preempt "assumptions unverified".*
