# Draft §3–§4 (English, LaTeX-ready prose; v0.1, 2026-09-02)

## 3. Persistent Test-Time Training

### 3.1 Setup

We study a pretrained causal LM processing an ordered stream of *sessions* $S_1, S_2, \dots$, each session a short sequence of *documents* (files of one repository; sections of one article). Following In-Place TTT, the fast weights are the MLP down-projections: for each selected layer $\ell$, the effective weight is
$$W^{(\ell)}_{\text{eff}} = W^{(\ell)}_{\text{base}} + G^{(\ell)}_{\text{slow}} + G^{(\ell)}_{\text{fast}},$$
with $G_{\text{fast}}, G_{\text{slow}}$ initialized to zero. Within a document, every chunk of $C$ tokens is first *scored* under the current $W_{\text{eff}}$ (all metrics are prequential) and only then *written*:
$$\delta = \mathrm{clip}_{\pm m}\big({-\eta}\,\nabla_{W}\mathcal{L}_{\text{NTP}}(\text{chunk})\big), \qquad G_{\text{fast}} \leftarrow G_{\text{fast}} + \delta .$$
No optimizer state is kept; the method is training-free and drop-in. (A Hebbian write in the style of In-Place TTT is evaluated as an ablation; conclusions are unchanged.)

### 3.2 A family of persistence policies

At each *document* boundary the transition $G_{\text{slow}} \leftarrow \gamma\, G_{\text{slow}} + \alpha \odot G_{\text{fast}}$, $G_{\text{fast}} \leftarrow 0$ unifies the policies of Table 1: **reset** ($\alpha{=}0$), **persist** ($\alpha{=}1,\gamma{=}1$), **decay** ($\alpha{=}1,\gamma{<}1$), **consistency** ($\alpha = |\mathrm{EMA}_{\gamma_d}[\mathrm{sign}(G_{\text{fast}})]|$), **Fisher** ($\alpha = (1+\hat F/\mathrm{med}\,\hat F)^{-1}$), **surprise** (scalar $\alpha$ from first-chunk loss), and the control **random** ($\alpha$ = a random permutation of the consistency gate, matching its histogram exactly). **session** additionally zeroes $G_{\text{slow}}$ at *session* boundaries. For *equal-budget* comparisons, gates are normalized to mean one, so gated policies spend exactly the write mass of persist and differ only in *where* they write.

### 3.3 What should a persistent fast weight remember? A linear model

We model $G = \sum_k \Delta_k$ as a linear associative memory, where $\Delta_k$ (write mass $m_k = \lVert \Delta_k\rVert_F$) stores session $k$'s associations, and sessions are mutually isotropic: probe directions of session $k$ are independent of $\{\Delta_j\}_{j\neq k}$ (plausible here because each session carries a fresh synthetic vocabulary; §4.1).

**Proposition 1 (interference decay).** Probing session $k$ at lag $L$ with a unit input $v$ from its own subspace, the recall signal-to-interference ratio satisfies
$$\mathrm{SNR}(k, L) \;=\; \frac{\lVert \Delta_k v\rVert}{\sqrt{\mathbb{E}\,\lVert \sum_{j=k+1}^{k+L} \Delta_j v\rVert^2}} \;=\; \sqrt{d}\cdot\frac{c_k\, m_k}{\sqrt{\sum_{j=k+1}^{k+L} m_j^2}} \;=\; \sqrt{d}\, c_k\, \sqrt{\rho(k,L)},$$
where $\rho(k,L) = m_k^2 / \sum_{j=k+1}^{k+L} m_j^2$ and $c_k \le 1$ reflects within-session alignment.
*Proof.* Independence and isotropy give $\mathbb{E}\lVert\Delta_j v\rVert^2 = \lVert\Delta_j\rVert_F^2/d$ and zero cross terms; sum over $j$. ∎

Two falsifiable predictions follow. **(i) Mass-ratio collapse:** excess recall is a function of $\rho$ alone, so curves from different sessions and different streams should collapse when plotted against $\rho$. **(ii) $\eta$-invariance:** with roughly uniform per-session masses, $\rho = 1/L$ and $\eta$ cancels, so lag-curves at different $\eta$ should already coincide; a systematically *faster* decay at large $\eta$ indicates effects outside the linear model (saturation of the clipped write, or drift of the base computation), which we quantify via $\Delta$Gen. We state the model as a measurement instrument, not as a theory of transformers.

**Proposition 2 (what the consistency gate keeps).** If a coordinate's write sign is $+1$ i.i.d. across documents w.p. $p$, the direction-EMA $D$ has $\mathbb{E}[D] = 2p-1$ and $\mathbb{E}[\Pi] = \mathbb{E}|D| \ge |2p-1|$, with equality as $\gamma_d \to 1$. Hence the gate passes systematically repeated directions and suppresses one-shot ones — by design it cannot protect episodic (single-mention) content, and it concentrates write mass along the stream's *systematic drift* direction. *Proof:* stationarity of the EMA and Jensen. ∎ (§5 shows the empirical footprint: no retention benefit over the random control, and a reproducible general-capability penalty.)

**Proposition 3 (boundedness and the cliff).** Element-wise clipping gives $\lVert G_{\text{slow}}\rVert_F \le m\sqrt{N}\,T$ after $T$ chunk writes ($N$ = parameters per layer), and $\le m\sqrt{N}\,T_s/(1-\gamma)$ under boundary decay. Degradation of general capability is therefore controlled by *cumulative written mass*, predicting a load-dependent, not time-dependent, cliff. ∎

**Proposition 4 (session policy).** Zeroing $G_{\text{slow}}$ at session boundaries sets $\rho(k, L) $'s numerator to zero for all $L \ge 1$: cross-session interference *and* cross-session recall are both identically zero, while within-session behavior equals persist. Session is thus the $L{=}0$ endpoint of the persistence-risk trade-off, not a competitor on the same axis. ∎

## 4. The Streaming-TTT Measurement Protocol

### 4.1 Contamination-free recall targets
Popular corpora are memorized: on unmodified repositories, the frozen base model already "recalls" 38.1% of cross-file identifiers; after renaming, 1.7% (Table 6). We therefore rename every session-defined symbol (repo-defined identifiers; article entities) to a synthetic name drawn from a **session-specific RNG**. We document a subtle failure mode we initially hit: sharing the RNG across sessions creates a shared fake vocabulary whose gradual acquisition *masquerades as cross-session memory* (it inflated our lag-40 recall by 2×; Fig. 6). Per-session seeds remove it.

### 4.2 Recall masks
Only the **first mention per document** of a symbol introduced in an *earlier* document tests memory; later mentions are in-context copying and are scored separately (xrep), as are first introductions (control). Targets are scored at the position predicting the symbol's first sub-token.

### 4.3 Fixed-lag re-scoring
Each session's held-out document (its last symbol-rich one, never streamed) is scored at lags $\{0, 5, 15, 40\}$ sessions after learning and at stream end. Lag 0 is scored *before* any boundary transition. Every session contributes to every lag, unlike end-of-stream-only designs whose late bins are underpowered.

### 4.4 Controls
(i) **Equal budget:** gates normalized to mean 1. (ii) **Random placement:** identical gate histogram, permuted coordinates. (iii) **Fresh-session transfer:** the final state is scored on held-out sessions never streamed; excess over base here measures generic style adaptation, and is subtracted when attributing lag-0 gains to memory. (iv) **Frozen baseline** throughout.

### 4.5 Leak-freedom and statistics
Five invariants are enforced by unit tests: eval-only passes never mutate state; each recorded chunk loss equals a frozen model holding the pre-write state; reset equals processing documents in isolation; persist $\equiv$ decay($\gamma{=}1$); the random gate's histogram matches consistency's exactly. Targets within a session are correlated, so all intervals are **session-clustered bootstrap** 95% CIs; per-target binomial CIs are shown in App. E to be up to 2× too narrow. Three hypotheses are pre-registered (persist > reset at lag 0; persist > base at lag 40; consistency $=$ random by TOST at $\pm 2$pt), Holm-corrected; all else is labeled exploratory. Seeds (3) resample stream order *and* synthetic vocabularies.

---
*Порt notes:* Table 1 = policy family; Fig. 1 = protocol diagram; numbers cited (38.1/1.7, 2×) to be finalized from week5/E7 JSONs. §5 branches per outline v3 outcome A.
