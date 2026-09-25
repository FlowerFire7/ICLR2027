# Revision Blueprint: All Memory Is Local

**核心原则**：让论文呈现真实的 scientific discovery path，而不是一个从一开始就知道答案、然后把所有实验排列成完美证据链的故事。

---

## 一、论文的中心问题

### 原始定位
> How long does persistent TTT remember?

### 建议提升为
> When persistent TTT appears to remember information across sessions, how much of that apparent memory is actually persistent information, and how much is adaptation or evaluation artifact?

### 核心 Contribution 重新定义

**不要定义成**：
> "我们测量了 memory horizon。"

**应该定义成**：
> "We discover that conventional delayed-recall measurements confound persistence with adaptation, and we develop a protocol that separates these effects."

然后才得到：
> 在这个更严格的 measurement 下，session-specific memory 衰减得很快。

这比单纯做一个 benchmark 更像顶会工作。

---

## 二、全篇推荐的新骨架

```text
1. Introduction
   1.1 Persistent TTT creates an apparent memory effect
   1.2 Why delayed retrieval does not establish persistence
   1.3 The central measurement question
   1.4 What we changed / what we found
   1.5 Contributions

2. Related Work

3. Persistent TTT and a Model of Interference
   3.1 TTT setup
   3.2 What does persistence mean? (measurement distinction)
   3.3 Linear-interference model + Propositions
   3.4 Testable predictions
   3.5 Scope of the model

4. Streaming-TTT Protocol
   4.1 Contamination-free targets
   4.2 First-mention evaluation
   4.3 Fixed-lag rescoring
   4.4 Never-streamed / fresh-session control
   4.5 Statistical protocol
   4.6 Unit-tested leakage controls

5. Results
   5.1 Persistent TTT strongly improves short-lag retrieval
   5.2 The apparent memory tail decays rapidly
   5.3 Fresh-session control changes the interpretation
   5.4 Persistence versus adaptation: what remains?
   5.5 Test of the write-mass prediction (η invariance)
   5.6 Persistence trades off against general capability
   5.7 Selective writing improves short-term retention, not horizon

6. Discussion
   6.1 What the experiments establish
   6.2 What they do not establish
   6.3 Why session reset is a practical operating point
   6.4 Limitations and open questions

7. Conclusion
```

**关键变化**：
- Method 不再只是"我们的方法是什么"，而是"我们如何定义和隔离 persistence"
- 理论保留在 §3，因为 Proposition 1 在 η sweep 之前写出，做了预测，数据后来验证
- 把"先预测后验证"的真实研究史保留，不伪造成"先观察后建模"

---

## 三、Introduction 重写逻辑

### 3.1 第一段：先提出现象

目标：Persistent TTT 看起来可以形成跨 session memory。

写一个非常简单的问题：
> TTT normally resets its fast weights at document boundaries. What happens if we do not reset them?

然后：
> If a model sees a repository/file/article and later predicts information from that earlier session, it is tempting to call this "memory."

**到这里不要马上讲贡献。**

### 3.2 第二段：提出真正的 scientific ambiguity

这是整篇最重要的 conceptual move。

写：
> But delayed retrieval is not, by itself, evidence of persistent memory.

然后列出 competing explanations：
```text
observed delayed gain
       │
       ├── persistent session-specific information
       ├── adaptation to the stream
       ├── in-context copying
       ├── pretraining contamination
       └── evaluation artifacts
```

**不要写六个 numbered list**。你们不是在展示 checklist，而是在提出 **measurement identification problem**。

### 3.3 必须突出"我们改变了 interpretation"

推荐逻辑：
```text
初始 observation: Persistent TTT 在 lag 40 还有 residual
        ↓
naive interpretation: "模型记住了早期 session"
        ↓
stricter control: never-streamed / fresh-session
        ↓
result: 大量 residual 也出现在没有见过目标 session 的模型上
        ↓
revised interpretation: 那部分不能被称为 session-specific memory
        ↓
central conclusion: 真正可归因于 persistence 的 component 比原始 delayed-recall 数字小得多，而且衰减很快
```

### 3.4 不要强调"我们解决了六个问题"

六个问题当然要保留，但建议改成：
> "Several controls became necessary because the naive measurement admits multiple confounds."

真正 contribution 是：
> **a measurement protocol that makes the persistence claim identifiable.**

### 3.5 Contributions 重新组织

**Contribution 1 — Measurement**
> We show that delayed retrieval alone does not identify persistent memory, and introduce Streaming-TTT with controls for contamination, copying, cross-session vocabulary overlap, evaluation leakage, and stream adaptation.

**Contribution 2 — Empirical finding**
> Using this protocol, we find that session-specific retention decays rapidly; the long-lag residual is not distinguishable from stream adaptation under our fresh-session control.

**Contribution 3 — Mechanistic/practical finding**
> We show that subsequent write mass, rather than learning rate alone, predicts interference, and that selective writing improves short-lag retrieval without extending the retention horizon.

---

## 四、Method/Theory 处理

### 4.1 理论位置：保留在 §3

**重要修正**：不要把理论写成"从数据里长出来的"。

事实是：Proposition 1 在 η sweep 之前写出 → 从命题得到 prediction → 后续 η sweep 验证 prediction。

把"先预测后验证"改成"先观察后建模"是**伪造研究史**，违反科学诚实原则。

理论真正有价值的地方，恰恰是**它不是 post-hoc explanation，而是 pre-specified prediction**。

### 4.2 §3 推荐结构

```text
3. Persistent TTT and a Model of Interference
   3.1 Setup
   3.2 What does persistence mean? (measurement distinction)
   3.3 Linear-interference model + Propositions
   3.4 Testable predictions  ← 关键新增
   3.5 Scope of the model
```

### 4.3 §3.4 Testable Predictions（关键新增）

明确写：
> **The model makes the following predictions before we examine the η sweep.**

**Prediction 1**
> If interference is governed primarily by cumulative write mass, changing η should alter the number of updates required to reach a given retention level, but should not substantially alter the normalized decay curve.

然后在 §5.5 开头直接：
> **We now test the prediction from §3.4.**

### 4.4 必须明确 Persistence 的 Operational Definition

区分三个概念：

**Within-session adaptation**
> 模型在当前 session 学会东西。

**Cross-session persistence**
> 模型离开 session 后，仍然保留 session-specific information。

**Stream adaptation**
> 模型没有记住某个具体 session，但由于长期接触相似 distribution，整体状态发生改变。

### 4.5 定义 Estimand（如果合适）

```
persistent effect = streamed-session performance − never-streamed transfer
```

核心思想：
- streamed session 上的 gain ≠ persistence
- streamed gain − general stream adaptation ≈ session-specific persistence

### 4.6 Scope Statement

保留并强化：
> "We use the model as a measurement instrument, not as a theory of transformers."

可以更强：
> "The purpose of this model is to generate falsifiable scaling predictions, not to model the full optimization dynamics of a transformer."

---

## 五、Results 重新组织

### 5.1 从"验证 hypothesis"改成"排除解释"

**不要**：
```text
5.1 Reset discards...
5.2 Fast decay...
5.3 Learning-rate invariance...
```

**应该**：
```text
5.1 Persistent TTT produces a strong short-lag effect
5.2 The apparent memory tail
5.3 Long-lag retrieval does not identify persistent memory  ← centerpiece
5.4 What remains after the fresh-session control?
5.5 Test of the write-mass prediction
5.6 Capability cost
5.7 Selective writing
```

### 5.2 每个 Subsection 的模板

1. What did we observe?
2. What would we normally conclude?
3. Why is that interpretation insufficient?
4. What alternative explanation exists?
5. What experiment distinguishes them?
6. What did we find?
7. What can we now claim?

### 5.3 §5.3 是全文 Centerpiece

标题可以非常直接：
> **5.3 Long-lag retrieval does not identify persistent memory**

展示：
- streamed vs never-streamed vs fresh-session
- lag 40: 0.67 pt vs never-streamed: 0.35 pt
- CI overlap

### 5.4 §5.5 标题建议

改为：
> **5.5 Testing the write-mass prediction**

而不是：
> Learning-rate invariance

因为后者只是 observation，前者强调这是对理论 prediction 的 test。

### 5.5 Prose 的定位

不要把 prose 写成"另一个 dataset"，而是：
> **A second domain exposes the same identification problem.**

code + prose 是在支持一个 general measurement insight：
> delayed improvement can be adaptation.

### 5.6 Consistency Gating 降级为 Secondary Result

核心只保留：
> consistency gating improves short-lag recall at equal write budget, but does not extend the horizon.

其他（Fisher、surprise、0.6B、prose、never-streamed）放 Appendix。

---

## 六、Discussion 结构

```text
6.1 What we establish
6.2 What we do not establish
6.3 Practical implication (session reset)
6.4 Limitations
```

不要写成 "limitations dump"。

---

## 七、Abstract 只回答四个问题

**Q1：Problem**
> Persistent TTT appears to create cross-session memory.

**Q2：Problem with existing measurement**
> Delayed retrieval confounds persistence with adaptation and leakage.

**Q3：What you did**
> Streaming-TTT separates these effects.

**Q4：What you found**
> Short-lag session-specific memory exists but decays rapidly; long-lag residual is not distinguishable from adaptation.

最后一句：
> Persistence also incurs capability cost, while session reset retains much of the short-lag benefit.

**Consistency gate 不必进 abstract。**

---

## 八、最重要的"不能写什么"

### ❌ 1. 不要写"我们证明没有长期记忆"

只能说：
> **not distinguishable from adaptation**

而不是：
> **does not exist**

### ❌ 2. 不要写"memory disappears after 15 sessions"

真正测到的是：
> session-specific excess is no longer distinguishable from the never-streamed transfer.

这是统计 inference，不是 ontological statement。

### ❌ 3. 不要写"our protocol eliminates all confounds"

应该：
> controls for the confounds we identify

### ❌ 4. 不要写"our theory explains TTT"

改：
> provides a simple model consistent with the observed decay pattern.

### ❌ 5. 不要把 isotropy 当成自然事实

### ❌

> Sessions are isotropic.

### ✅

> We construct session-specific vocabularies to approximate isotropic interference, allowing the model's prediction to be tested.

### ❌ 6. 不要把单 seed 的 4B 结果写成 scaling law

### ❌

> The effect increases with model scale.

### 更安全：

> The observed effect is larger at 4B, although the 4B result is single-seed.

### ❌ 7. 不要把"significant"写成"important"

> statistically significant ≠ practically large

### ❌ 8. 不要把 AI involvement 写成"human merely verified"

### ❌ 9. 不要为了"人味"编造虚假的研究过程

不要编：
- "Initially, we were surprised..."（如果没这么想）
- "After weeks of experiments..."
- "We initially hypothesized X, but..."（除非确实发生）
- 假的失败实验

### ❌ 10. 不要把 post-hoc interpretation 写成 prediction

如果一个结果是在看到数据以后才提出解释，就**不能**写成：
> "Our model predicted..."

### ❌ 11. 不要为了 human-like narrative 改写真实研究史

尤其**不能把 genuine prospective prediction 改写成 post-hoc explanation**。

Proposition 1 → prediction → η sweep 恰恰应该成为论文里最明确的一条"预测—验证"链。

---

## 九、最重要的"必须突出什么"

### S-tier
1. **Delayed retrieval ≠ persistence**
2. **Fresh-session control**
3. **Interpretation changed because of the control**
4. **Rapid decay of session-specific component**
5. **Adaptation explains long-lag residual**

### A-tier
6. contamination / vocabulary controls
7. capability cost
8. write-mass theory (as pre-specified prediction)

### B-tier
9. session-reset practical policy
10. consistency gating

### C-tier
11. Fisher
12. surprise
13. extra policy comparisons
14. detailed implementation details

---

## 十、最值得保留的"人类痕迹"

### ① Shared vocabulary bug

> shared fake vocabulary caused lag-40 recall to be inflated 2× before being fixed.

写成：
> A control experiment exposed an unintended shortcut...

这是非常强的 validity evidence。

### ② H2 interpretation 被改变

建议改成：
> **The raw lag-40 result supports H2 as originally formulated, but the fresh-session control shows that H2 is not a clean test of persistence. We therefore revise the interpretation rather than treating H2 as evidence for long-term session memory.**

### ③ "unattributed remainder"

> "the remainder is unattributed."

不要为了让故事完整而解释它。

---

## 十一、真正可以写的"人类研究痕迹"

如果事实属实：
- "Our initial interpretation was..."
- "This control changed our interpretation..."
- "We therefore do not use X as evidence for Y."
- "The remaining difference is not explained by the current controls."
- "We have not isolated this effect."
- "This result motivated the following experiment."
- "We derive this prediction before evaluating the η sweep."

---

## 十二、写作风格注意事项

### 12.1 少用连续的 "We show / We demonstrate / We establish"

换成：
- We observe...
- This suggests...
- The control indicates...
- This result is consistent with...
- We therefore interpret...

### 12.2 少用 "Taken together"

### 12.3 少用"完美三段式"

> First,... Second,... Finally,...

重要 conceptual argument 尽量自然展开。

### 12.4 不要每段最后都写一个"因此贡献"

> This demonstrates X. This highlights Y. This suggests Z.

让 evidence 有时候自己说话。

### 12.5 数字不要每个都变成 punchline

让数字承担不同角色：
- 7.6× = magnitude
- 60% = practical tradeoff
- 96% = adaptation evidence
- 0.67 vs 0.35 = identification problem
- 1.22 = secondary effect

### 12.6 适当保留"不确定性"

> "the remainder is unattributed."
> "We suspect... but we have not isolated it."

千万不要把这种东西润色掉。

---

## 十三、理论验证的正确写法

### ❌ 不要说

> Our theory is validated.

### ❌ 不要说

> These results prove Proposition 1.

### ✅ 应该说

> The observed scaling is consistent with Proposition 1.

或：
> The η sweep supports the prediction derived from the model.

或：
> The η sweep provides a test of the model's write-mass prediction.

---

## 十四、两条主线的明确区分

### 主线 A：Measurement / empirical discovery

```text
Delayed retrieval
      ↓
Could be memory OR adaptation
      ↓
Controls
      ↓
Fresh-session experiment
      ↓
Long-lag signal largely attributable to adaptation
      ↓
True session-specific persistence decays rapidly
```

### 主线 B：Theory / predictive mechanism

```text
Interference model
      ↓
Proposition 1
      ↓
Write-mass prediction
      ↓
η sweep
      ↓
Observed η invariance
      ↓
Supports write-mass interpretation
```

**不要把 A 和 B 强行串成一条线。**

---

## 十五、作者修改 Checklist

### A. Scientific story

- [ ] 核心问题从 "memory lasts how long?" 改成 "delayed retrieval 是否真的能证明 persistence？"
- [ ] 明确 competing explanations
- [ ] fresh-session control 成为 central experiment
- [ ] 明确说 interpretation 被实验改变
- [ ] 不把 negative results 当附属结果
- [ ] 不过度声称"没有 memory"
- [ ] 把 adaptation 与 persistence 明确定义分开

### B. Introduction

- [ ] 不要一开头列六个 artifacts
- [ ] 先讲现象
- [ ] 再讲 ambiguity
- [ ] 再讲 measurement problem
- [ ] 再讲 protocol
- [ ] 最后讲 findings
- [ ] Contributions 以 measurement / empirical finding / mechanistic-practical finding 为主

### C. Method

- [ ] 明确 persistence 的 operational definition
- [ ] 明确 adaptation 的定义
- [ ] 明确 streamed vs never-streamed 的区别
- [ ] 解释每一个 control 为什么存在
- [ ] 不要只说"we use X"
- [ ] 要说"without X, interpretation would be ambiguous"

### D. Theory

- [ ] 理论保留在 §3（因为是 pre-specified prediction）
- [ ] 明确写出 Testable Predictions
- [ ] §5.5 明确这是对 prediction 的 test
- [ ] 明确 assumptions
- [ ] 不把 isotropy 当自然事实
- [ ] 不声称解释整个 transformer
- [ ] prediction 必须对应 experiment
- [ ] negative/partial agreement 也要报告

### E. Results

每个 subsection 问：
- [ ] What did we observe?
- [ ] What could explain it?
- [ ] What alternative explanation exists?
- [ ] What control distinguishes them?
- [ ] What changed after the control?
- [ ] What can we now claim?

### F. Statistics

- [ ] 不把 non-significant 当 evidence of equality
- [ ] 不把 CI overlap 当正式 equivalence test
- [ ] equivalence / superiority 分开
- [ ] single-seed scaling claim 降级
- [ ] practical significance 与 statistical significance 分开
- [ ] "not distinguishable" 不写成 "absent"

### G. Writing

- [ ] 少一点 "We demonstrate..."
- [ ] 少一点 "Taken together..."
- [ ] 少一点完美三段式
- [ ] 不要每段最后都总结 contribution
- [ ] 不要每个数字都变成 headline
- [ ] 保留真正的 uncertainty
- [ ] 保留真正的 unresolved result
- [ ] 不要为了"像人"故意写差
- [ ] 不要制造不存在的 research history
- [ ] 不要把 post-hoc 写成 prediction

---

## 十六、如果只能改 5 件事

### ① 重写 Introduction

从 "six artifacts" 变成 **"delayed retrieval does not identify persistence."**

### ② 把 fresh-session control 提升为全篇 centerpiece

它不是一个 control，它是 **决定 paper interpretation 的 experiment。**

### ③ 重排 Results

从：hypothesis 1 → hypothesis 2 → theory → gating

变成：observation → alternative explanation → control → revised interpretation → mechanism → practical tradeoff

### ④ 在 §3.4 明确写出 Testable Predictions

让 reviewer 清楚看到 prediction → test 的链条。

### ⑤ 大幅压缩 secondary results

把 Fisher、surprise、过多 gating details 放 Appendix。

把 main paper 的 attention 留给 **persistence vs adaptation**。

---

## 十七、最终应该形成的"人类研究轨迹"

Reviewer 从第一页读到最后，脑中的故事应该是：

> **"作者看到 TTT 在跨 session 后似乎还能 recall。"**
>
> ↓
>
> **"他们意识到这可能不是 memory。"**
>
> ↓
>
> **"他们发现 contamination / copying / vocabulary 等问题。"**
>
> ↓
>
> **"他们设计了更严格的 protocol。"**
>
> ↓
>
> **"长尾仍然存在。"**
>
> ↓
>
> **"但是 fresh-session control 表明其中相当一部分是 adaptation。"**
>
> ↓
>
> **"所以作者修改了原来的 memory interpretation。"**
>
> ↓
>
> **"剩下的真正 session-specific effect 衰减很快。"**
>
> ↓
>
> **"理论预测 decay 由 subsequent write mass 控制，η sweep 验证了这一预测。"**
>
> ↓
>
> **"但 persistent writing 有 capability cost。"**
>
> ↓
>
> **"因此 session reset 是一个合理的 practical operating point。"**
>
> ↓
>
> **"selective writing 可以改善短期 retention，但不能创造更长的 horizon。"**

---

## 十八、核心原则总结

> **不要把"降低 AI 感"作为独立目标。**
>
> 真正应该优化的是 **scientific agency + causal/identification logic + honest uncertainty**。
>
> **不要为了 human-like narrative 改写真实研究史。**
>
> **让论文准确地暴露真实的 epistemic structure。**

---

*文档创建时间：2026-09-11*
*基于 13 天论文修订过程的完整讨论记录整理*

---

## 十九、具体修改指令（第1-2步）

### 第1步：摘要与引言重写

#### 新摘要

```latex
\begin{abstract}
Test-time training (TTT) lets a language model update a small set of fast weights as it reads. The drop-in methods considered here reset those weights at document boundaries, so nothing carries across documents. When the reset is removed, the model recalls symbols from earlier documents well after they have left the context, which looks like persistent memory. We ask how much of this signal is memory. Delayed recall has at least three other sources: information the model already had (pre-training contamination, in-context copying, synthetic vocabularies shared across sessions), properties of the evaluation (scoring order, length-normalized accuracy), and adaptation to the stream as a whole. We build a protocol, Streaming-TTT, that separates them: per-session obfuscated vocabularies, first-mention targets, fixed-lag re-scoring, and a control of sessions that were never streamed. On 180 code repositories and 200 prose sessions with Qwen3 models from 0.6B to 4B, persistence raises first-mention recall to \foldLagZero\ times the frozen model's immediately after a session, but the estimated session-specific component halves within five sessions; by lag~15 what remains cannot be distinguished from the gain on never-streamed sessions. A linear-interference model predicts that this decay depends on subsequent write mass rather than on the learning rate, and the measured curves collapse accordingly. Resetting at session boundaries keeps \sessionCapture\% of the immediate benefit and avoids the general-capability cost that unrestricted persistence incurs. In this setting, delayed recall alone did not establish persistent memory; the relevant quantity is what remains after adaptation is subtracted.
\end{abstract}
```

#### 新引言

```latex
\section{Introduction}
Test-time training adapts a language model by updating fast weights, typically the MLP down-projections, as tokens arrive. It appears both in architectures trained for it (Titans, \citealp{behrouz2025titans}; LaCT, \citealp{zhang2025lact}; TTT-E2E, \citealp{tandon2025ttte2e}) and in drop-in variants applied to pretrained models (In-Place TTT, \citealp{feng2026inplace}; TTT-NTP, \citealp{ouyang2026tttntp}). The drop-in methods considered here reset the fast weights at document boundaries.

Real workloads are streams: a coding assistant reads one repository file after another; an enterprise assistant reads one organization's documents for months. If the reset is simply removed, the model does something that looks like remembering. It recalls identifiers defined in a file it read several files ago, long after that file has left the context window. This paper asks how much of that signal is memory, and how far it reaches.

The question is harder than it sounds, because delayed recall has other sources. Some of the information was never learned at test time at all: on unmodified public repositories, a frozen model already recalls 38.1\% of cross-file identifiers, and every mention of a symbol after the first can be copied from context. Some of the signal comes from the evaluation rather than the model: scoring a chunk after it has been written, or using length-normalized accuracy, both move the numbers. And some of it is adaptation to the stream as a whole rather than to any particular session; on prose, this component accounts for \eThreeShare\% of the apparent likelihood gain. These sources did not all become visible at the same stage of the study, and our protocol was refined as they did. Its final form (\S\ref{sec:protocol}) renames every session-defined symbol with a session-specific vocabulary, scores only first mentions, re-scores held-out documents at fixed lags after learning, and compares against sessions that were never streamed.

With these controls, the measurement gives a consistent picture across code and prose, with the same qualitative pattern across the model sizes we evaluate. Persistence raises first-mention recall to \foldLagZero\ times the frozen model's immediately after a session. The session-specific part of that gain halves within five sessions; by lag~15 the remaining excess ($\persistExcessLagFifteen\pt$) lies within the interval of the gain on never-streamed repositories ($\freshTransfer\pt$, CI \freshTransferCI), and by lag~40 the two coincide. The control therefore turns delayed recall into a measurement of session-specific retention. A linear-interference model (Prop.~\ref{prop:snr}) predicts that the decay depends on how much is written afterwards and not on the learning rate; curves at three learning rates collapse when normalized (Fig.~\ref{fig:collapse}). Unrestricted persistence also costs $2$--$3\pt$ on HellaSwag and PIQA. Resetting at session boundaries keeps \sessionCapture\% of the immediate benefit with no cross-session exposure. Finally, at equal write budget, gating writes by cross-document sign consistency beats random placement by about one point at lag~0; the effect grows with model size and disappears by lag~15.

Our contributions are: (1) a protocol for measuring persistent TTT that separates prior knowledge, evaluation effects, and stream adaptation from session-specific memory, with unit tests and a never-streamed control; (2) measurements on code and prose streams at three model sizes showing that session-specific memory decays within a few sessions and that the long-lag residual is not distinguishable from adaptation; (3) evidence that sign-consistency gating improves short-lag retrieval at equal write budget, with a larger effect on larger models.
```

#### 第1步六处微调

1. `All of those we know of` → `The drop-in methods considered here`（摘要与§1首段）
2. `session-specific part` → `estimated session-specific component`（摘要）
3. `grew as they did` → `was refined as they did`（§1第三段）
4. `consistent picture across three model sizes` → `consistent picture across code and prose, with the same qualitative pattern across the model sizes we evaluate`（§1第四段首句）
5. fresh与理论之间加桥：`The control therefore turns delayed recall into a measurement of session-specific retention.`
6. 贡献(3)：`evidence that sign-consistency gating improves short-lag retrieval at equal write budget, with a larger effect on larger models.`

### 第2步(a)：新增 §3.2 "What counts as persistence?"

放在 3.1 Setup 之后、策略族之前；原 3.2 变 3.3，理论变 3.4。

```latex
\subsection{What counts as persistence?}\label{sec:estimand}
Three quantities are easy to conflate. \emph{Within-session adaptation} is the gain on a session's held-out document scored immediately after the session (lag~0). \emph{Stream adaptation} is the gain the final fast-weight state produces on sessions that were never streamed; it reflects what the model has absorbed about the stream as a whole (vocabulary shape, domain style) and cannot be memory of any particular session. \emph{Session-specific persistence} at lag $L$ is what is left of a session's gain, $L$ sessions after it was learned, once stream adaptation is accounted for. We estimate it as
\[
P(L) \;=\; \big[R_{\text{streamed}}(L) - R_{\text{frozen}}\big] \;-\; \big[R_{\text{fresh}} - R_{\text{frozen}}^{\text{fresh}}\big],
\]
where $R$ is first-mention recall (or, on prose, log-likelihood), each excess is taken against the frozen model on the same documents, and the second bracket is measured on never-streamed sessions with the state at the end of the stream. The first bracket alone is what a delayed-recall experiment reports; $P(L)$ is the quantity our conclusions are about. Intervals for $P(L)$ combine a session-clustered bootstrap over streamed sessions with an independent one over never-streamed sessions.
```

### 第2步(b)：§5 重排

```latex
\section{Results}\label{sec:results}

\subsection{Persistent TTT produces a strong short-lag effect}
At lag~0, persist reaches \persistAccZero\% first-mention recall against \baseAccZero\% for the frozen model (paired excess $\persistExcessLagZero\pt$, CI \persistExcessLagZeroCI; H1), a \foldLagZero$\times$ ratio; the likelihood gap is $\basePplZero\to\persistPplZero$ PPL (Fig.~\ref{fig:horizon}). Per-document reset is indistinguishable from frozen (Table~\ref{tab:main}). Whatever persistence provides, it is provided across documents, not within them.

\subsection{The apparent memory tail}
The excess falls to $\persistExcessLagFive\pt$ at lag~5, $\persistExcessLagFifteen\pt$ at lag~15, and $\persistExcessLagForty\pt$ at lag~40 (CI \persistExcessLagFortyCI), still above frozen; H2 as stated is confirmed. Read on its own, this curve suggests a memory that decays quickly and then persists at a low level for at least forty sessions. That reading is the one a delayed-recall experiment invites, and it is the one we test next.

\subsection{The never-streamed control changes the interpretation}\label{sec:fresh}
The final persist state, scored on repositories that were never streamed, exceeds the frozen model by $\freshTransfer\pt$ (CI \freshTransferCI). This gain cannot be memory of any session; it is adaptation to the stream. It is of the same size as the lag-40 residual, and each interval contains the other's point estimate. On prose the same comparison is sharper: the lag-0 likelihood gain of $\eThreeStreamZero$ log-PPL is \eThreeShare\% matched by never-streamed sessions ($\eThreeFresh$, CI \eThreeFreshCI). We therefore do not use the long-lag result as evidence for session-specific memory. H2 holds in the form in which it was stated; what changed is what it measures. Fig.~\ref{fig:horizon} shows the never-streamed level as a band; the persist curve enters it between lag~5 and lag~15.

\subsection{What remains: session-specific retention}
Subtracting stream adaptation (\S\ref{sec:estimand}) gives $P(0)=\memZero\pt$, $P(5)=\memFive\pt$, $P(15)=\memFifteen\pt$ (CI \memFifteenCI), and $P(40)=\memForty\pt$ (CI \memFortyCI) on code; the last two intervals include zero. On prose, $P(L)$ includes zero at every lag. Session-specific retention is therefore real and large immediately after a session, halves within five sessions, and is not distinguishable from zero beyond fifteen. We do not conclude that it is absent; we conclude that our measurement cannot separate it from adaptation past that point. Lag-0 and lag-5 excess follow the same pattern at 0.6B and 4B (Fig.~\ref{fig:scale}a).

\subsection{Write load, not learning rate, predicts the decay}\label{sec:eta}
Prop.~\ref{prop:snr} was formulated before the learning-rate sweep and predicts that lag curves at different $\eta$ coincide once normalized by their lag-0 excess. At 0.6B, $\eta\in\{2,3,4\}\times10^{-2}$ give normalized lag-5 retention of $\normTwo$, $\normThree$, $\normFour$ (Fig.~\ref{fig:collapse}). The slight ordering is in the direction one would expect from clip saturation; we did not test this directly. The decay is governed by how much is written afterwards, the signature of the palimpsest model of \citet{parisi1986memory}.

\subsection{Persistence has a capability cost}
We use $\eta=3\times10^{-2}$, the largest value before general capability collapses at 0.6B (between $3$ and $4\times10^{-2}$ the mean HellaSwag/ARC-Easy delta drops from $+0.9$ to $-6.9\pt$; 500 items per task). Even below that point, persistent policies at 1.7B lose $\taxHSRaw\pt$ on HellaSwag \citep{zellers2019hellaswag} and $\taxPIQARaw\pt$ on PIQA \citep{bisk2020piqa} under raw accuracy, and the same under length normalization (Fig.~\ref{fig:tax}a). ARC-Easy \citep{clark2018arc} moves $+\taxARCENorm\pt$ under length normalization but only $\taxARCERaw\pt$ in raw accuracy: the adaptation reshapes per-token likelihood in a way the normalized rule rewards without changing which answers are correct. We report both rules. At 4B the HellaSwag cost is comparable (Fig.~\ref{fig:tax}b; single seed).

\subsection{Session-level reset as an operating point}
Session keeps \sessionCapture\% (\sessionCaptureMin--\sessionCaptureMax\% across seeds) of persist's lag-0 excess in recall and \sessionLogCapture\% in log-likelihood, has no cross-session exposure (Remark~\ref{rem:session}), and returns the model to its base state at stream end; within a session it carries the same exposure as persist. The paired persist advantage at lag~0 is $\spZero\pt$ (CI \spZeroCI), of which stream adaptation explains $\freshTransfer\pt$; the remainder is not explained by our current controls. For the setting studied here, session reset keeps most of the short-lag benefit while avoiding the cost above and the cliff. Persistence adds two to three fast-weight-sized buffers and reduces throughput to $\approx0.4\times$ frozen inference; session needs no gate state.

\subsection{Selective writing improves short-lag recall, not the horizon}
At equal write budget, consistency gating beats random placement by $\crZero\pt$ at lag~0 (CI \crZeroCI) and $\crFive\pt$ at lag~5, and not beyond; random equals persist throughout. H3 as stated (equivalence within $\pm2\pt$) is not rejected at 1.7B, so the effect is real and small. It is absent at 0.6B and larger at 4B (Fig.~\ref{fig:scale}b; single seeds). On never-streamed repositories consistency and random tie, so on code the gate improves session-specific retention rather than adaptation; on prose it improves adaptation instead (App.~\ref{app:extra}), as Prop.~\ref{prop:gate} would predict for a gate that keeps whatever recurs. Decay, Fisher, and surprise gates are in App.~\ref{app:extra}.
```

### §3.3 命题1之后加

```latex
This model yields a testable prediction for the learning-rate sweep in \S\ref{sec:eta}.
```

### 需要生成的新宏

用 `memory_excess.py` 的逻辑对 E1 的 accuracy 算 $P(L)$ 及合并 CI：
- `\memZero`, `\memFive`, `\memFifteen`, `\memForty`
- `\memFifteenCI`, `\memFortyCI`

---

## 二十、第 2 步完成记录（2026-09-11）

### P(L) 宏已计算并写入 numbers.tex

```latex
\newcommand{\memZero}{5.8}      \newcommand{\memZeroCI}{[4.5,\,7.3]}
\newcommand{\memFive}{1.2}      \newcommand{\memFiveCI}{[0.5,\,2.0]}
\newcommand{\memFifteen}{0.6}   \newcommand{\memFifteenCI}{[-0.1,\,1.2]}
\newcommand{\memForty}{0.3}     \newcommand{\memFortyCI}{[-0.4,\,1.0]}
```

计算方式：流内配对超额按"仓库×seed"聚类 bootstrap，fresh 超额按 fresh 仓库聚类 bootstrap，两者独立相减。

### 关键发现

- P(0)=5.8 → P(5)=1.2：五个会话内掉了约 80%，不是一半
- "halves within five sessions" 全部改为 "falls by (about/roughly) four fifths within five sessions"
- lag 15 和 lag 40 的 P(L) 区间都含零，支撑 "not distinguishable from zero beyond fifteen"
- P(5) 的区间 [0.5, 2.0] 不含零，"五个会话时仍可检出"

### 五处措辞修改已应用

1. `do not use` → `do not treat ... as evidence`（§5.3）
2. `signature of the palimpsest model` → `consistent with the palimpsest picture`（§5.5）
3. `largest value before ... collapses` → `just below the capability cliff observed`（§5.6）
4. §5.8 H3 措辞改为：`The difference is significantly nonzero (CI excludes zero) but lies within the prespecified $\pm2\pt$ equivalence margin, so H3 as stated is not rejected at 1.7B.`
5. `random equals persist` → `random is indistinguishable from persist`（§5.8）

### §3.2 estimate 限定已加入

原句：
> Stream adaptation is the gain the final fast-weight state produces on sessions that were never streamed; it reflects what the model has absorbed...

改为：
> Stream adaptation is what the model has absorbed about the stream as a whole (vocabulary shape, domain style); we use the gain the final fast-weight state produces on sessions that were never streamed as an estimate of this quantity, since that gain cannot be memory of any particular session.

### "subtracted" 的说明

摘要中 "what remains after adaptation is subtracted" 在我们的设计里是准确的——估计量确实是"流内会话上的超额减去 fresh 会话上的超额"，`memory_excess.py` 算的就是这个差。§3.2 先把估计量定义清楚，摘要里的 "subtracted" 就有了依据。

---

**第 2 步状态：✅ 已完成**

---

## 二十一、第 3 步完成记录（2026-09-11）

### 图 1 更新为 identification 三面板

新图 `fig1_identification.pdf`，label 改为 `fig:ident`：
- (a) 代码流上 persist 的超额与 fresh 水平带
- (b) 扣减后的 P(L)，区间合并两个 bootstrap
- (c) 散文流上的识别问题

原 `fig2_horizon_E1.pdf` 移至附录（horizon in both readouts）。

### §4 按三类来源重写

从七个加粗段落合并为四个：
1. **Information the model already has** — 预训练污染、上下文复制、共享词表
2. **Properties of the evaluation** — 先评分后写入、固定lag重评分、两种评分规则
3. **Adaptation to the stream** — fresh control、P(L) 估计量、等预算比较
4. **Statistics** — 聚类bootstrap、预注册假设

关键改进：
- 每类都写明对应的控制**和为什么没有它解释会含糊**
- "我们的 bug"变成设计要求："随机源必须逐会话独立，否则……"
- 单元测试细节、96/124 计数移到附录

### 新增 label

- `\label{sec:setup}` 在 §3.1
- `\label{sec:cost}` 在 §5.6
- `\label{fig:vocab}` 在附录共享词表图

### 图引用更新

- `fig:horizon` → `fig:ident`（全部替换）
- `fig:caution` → 删除，(a)移至附录`fig:vocab`，(b)改引`fig:ident(c)`
- `sec:horizon` → `sec:fresh`（附录中）

### 附录更新

- app:caution (Six artifacts) 更新引用
- 添加共享词表图 `fig:vocab`（`fig_vocab_artifact.pdf`）

**第 3 步状态：✅ 已完成**

---

## 二十二、第 4 步完成记录（2026-09-11）

### §6 四段重组

新结构：
1. **What the experiments establish** — 只陈述数据真正支持的结果，每条带估计量
2. **What they do not establish** — 主动划定 inference boundary
3. **Practical implication** — deployment recommendation，明确不是 universal prescription
4. **Limitations** — 样本、seed、scope 的边界

关键句子：
- `cannot separate it from stream adaptation`
- `not isotropic, and we have not tested the collapse on them`
- `not explained by our current controls`
- `Which side of that trade is right depends on the deployment`

### 结论首句限定

```latex
For the training-free, fast-weight TTT setting studied here, memory is local.
```

### 第 3 步遗留的三处小改已应用

1. `five such invariants` → `these invariants`
2. `H3 consistency $=$ random` → `H3 consistency and random are equivalent`
3. 图注加 `control`：`for persistent TTT and the session-reset control`

### 理论句更新

```latex
The decay is predicted by subsequent write mass rather than learning rate, as Prop.~\ref{prop:snr} predicted before the sweep was run.
```

**第 4 步状态：✅ 已完成**

---

## 二十三、第 5 步：全文自查清单

1. 三处禁用表述全文 grep：`no memory` / `disappears` / `eliminates all` — 应为零
2. 三个 P(L) 相关句子与宏一致：摘要 "four fifths"、§5.4 数字、§6 首段
3. label 完整：`sec:setup`, `sec:cost`, `sec:eta`, `sec:estimand`, `sec:fresh`, `fig:ident`, `fig:vocab`
4. 旧引用已清理：`fig:horizon`, `fig:caution` → 0
5. "pre-registered" 全文为零；H3 全文统一为 equivalence 措辞
6. 4B 相关句子都带 "single seed"
7. 数字宏：`numbers.tex` 八个 `\mem*` 宏与 `memory_excess.py --key acc` 逐位一致
8. 页数 ≤ 9
9. 附录新增两张图有 caption 和引用
10. AI 声明不动

### 已完成验证

**图片已复制到 figs/：**
- ✅ `fig1_identification.pdf`
- ✅ `fig_vocab_artifact.pdf`

**fig:vocab caption 已更新：**
```latex
\caption{A shared random source for synthetic names across sessions (0.6B, pre-fix stream) inflates recall at every lag and roughly doubles it at lag~40; a session-specific source removes the effect. Frozen model dashed.}
```

**memory_excess.py --key acc 验证通过：**
```
fresh excess (86 clusters): +0.35 [-0.16,+0.92]
lag  0: stream +6.19  P(L)=+5.84 [+4.54,+7.28]  clusters=372
lag  5: stream +1.57  P(L)=+1.22 [+0.46,+1.95]  clusters=360
lag 15: stream +0.92  P(L)=+0.57 [-0.11,+1.25]  clusters=339
lag 40: stream +0.67  P(L)=+0.32 [-0.36,+0.97]  clusters=288
```

与 numbers.tex 宏逐位一致（四舍五入差异）。

**第 5 步状态：✅ 已完成**

---

## 最终状态

| 步骤 | 内容 | 状态 |
|------|------|------|
| 第1步 | 摘要、引言重写 | ✅ |
| 第2步 | §3.2 P(L)估计量、§5重排 | ✅ |
| 第3步 | §4三类来源、图1 identification | ✅ |
| 第4步 | §6四段重组 | ✅ |
| 第5步 | 全文自查、宏验证 | ✅ |

**待完成：**
- Overleaf 编译确认页数 ≤ 9 且无 undefined reference

---

*最终更新于 2026-09-11*
