# Persistent Test-Time Training：新颖性核验、完整大纲、指标与引用

*核验日期：2026-08-30。所有"最近工作"均为 2026 年 8 月前 arXiv/会议可查。*

---

## A. 新颖性核验：与最近似工作的逐维对比

| 工作 | 场景 | 预训练 LLM 上 drop-in | 免额外训练 | fast weight 跨文档持久 | 持久化门控 | 评测跨文档收益 | 评测通用能力保持 | 与本文的差异 |
|---|---|---|---|---|---|---|---|---|
| In-Place TTT (Feng et al., ICLR'26 Oral) | 长上下文 LM | ✓ | ✗（需继续训练 ~35B token） | ✗（文档边界重置） | ✗ | ✗ | ✓（常识基准） | 我们研究"不重置"这一它明确留空的轴 |
| TTT-NTP (2026.06) | 同上 | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | 改内环监督目标，仍每文档重置 |
| LaCT / Test-Time Training Done Right (Zhang et al., 2025) | 长上下文、3D | ✗（从头训练） | ✗ | ✗ | ✗ | ✗ | – | 架构级方法 |
| Titans (Behrouz et al., NeurIPS'25) | 序列建模 | ✗（新架构） | ✗ | 序列内 | 惊奇度 + 学习到的遗忘门 | ✗ | ✓ | 门控是学出来的，需从头训练；我们免训练、drop-in |
| Nested Learning / HOPE (Behrouz et al., 2025) | 持续学习架构 | ✗ | ✗ | 多时间尺度（CMS） | 学习到的多频更新 | ✓（知识吸收任务） | ✓ | 同上；HOPE 自述遗忘"未被解决" |
| **Elastic TTT / Fast Spatial Memory (Ma et al., 2026.04)** | **4D 重建（视觉）** | ✗（LaCT 架构） | ✗ | ✓（跨 chunk 持续，EMA 锚点） | **Fisher 弹性先验（EWC 式）** | ✓（重建质量） | – | **最接近的机制**：但在视觉、从头训练；我们把"Fisher-importance"作为对照策略之一，并加入一致性/惊奇/随机对照 |
| Temp-LoRA (Wang et al., 2024) / StreamAdapter (2024) / InfiniteICL (Cao et al., 2025) | LM 长文本 / 上下文→权重 | ✓（LoRA） | ✗/部分 | 文档内持久 | ✗ | 部分 | 被指出损害通用能力 | 无"保留什么"的系统研究；作为 LoRA 参数化基线 |
| SCoL (2026.05) | 上下文知识吸收 | ✓ | ✗（meta-RL 训练选择器） | ✓ | 学习到的模块选择 | ✓（SQuAD/LongBench） | ✓ | 需要训练；我们免训练，且对比策略族 |
| CaMeLS (Hu et al., ICLR'23) / MAC (Tack et al., NeurIPS'24) | 文档流在线适应 | ✓ | ✗（元学习权重/编码器） | ✓ | 学习到的 token 权重 / 外部记忆 | ✓（StreamingQA） | 部分 | 提供 S-Fact 评测协议；方法需训练 |
| CoTTA (Wang et al., CVPR'22) / EATA (Niu et al., ICML'22) / SAR (Niu et al., ICLR'23) | 视觉持续 TTA | ✓ | ✓ | ✓ | 教师 EMA / 随机恢复 / Fisher 正则 | ✗ | ✓（抗遗忘） | 同问题在视觉分类上的版本；LM 上未系统研究，且没有"跨文档收益"指标 |
| SR-TTT (2026.03, v2 撤回) | 惊奇度门控 KV 缓存 | – | – | – | 惊奇度 | ✓（NIAH，结果因评测泄漏撤回） | – | 警示：惊奇度门控位置偏置 + 评测因果泄漏；我们需内置泄漏自检 |
| Fast-Slow Training (2026.05) | RL 后训练 | ✓ | ✗（RL） | 文本 fast 权重 | – | – | ✓ | 不同层面（文本 vs 参数） |

**核验结论**：
1. "drop-in、免训练、fast weight 跨文档持久、系统比较持久化策略（Reset / Persist / Decay / Consistency / Fisher / Surprise / Random）"——**未见有人做过**。
2. 最接近的两条线是 Elastic TTT（Fisher 弹性先验，但在视觉 LaCT 上）和视觉 CoTTA/EATA。它们证明问题成立，同时说明"Fisher 正则"必须作为强基线放进来，不能只比 decay。
3. SR-TTT 的撤回提醒：惊奇度门控在早期上下文有存储偏置，且评测泄漏很容易发生。我们的评测脚本必须带因果性自检（预测位置比答案早一位、fast weight 更新只用已见 chunk）。
4. 一致性门（你的 DDL）在 LM TTT 场景下没有先例；它与 signSGD/Lion 的符号统计、SI/MAS 的重要性估计有联系，需在 related work 中明说。

---

## B. 论文完整大纲（ICML 格式，8 页正文 + 附录）

| 节 | 小节 | 内容 | 图/表 | 支撑实验 / 证据 |
|---|---|---|---|---|
| **摘要** | – | 问题（reset 丢跨文档信息，persist 漂移）→ 框架（双时间尺度 + 持久化策略族）→ 协议（Streaming-TTT）→ 三条发现 → 开源 | – | – |
| **1 Introduction** | 1.1 动机 | drop-in TTT 已标准化在 W_down（In-Place TTT/TTT-NTP），但每文档重置；同用户/同仓库/同领域的流浪费跨文档信息 | Fig.1：三种处置（reset/persist/gated）在同一流上的示意 | – |
| | 1.2 问题 | "持久 fast weights 应保留什么？" | – | – |
| | 1.3 贡献 | (i) 双时间尺度持久 TTT 框架，统一 7 种策略；(ii) Streaming-TTT 协议与 benchmark；(iii) 系统实证 + recipe；(iv) 小理论：一致性门 = 方向重现概率的估计 | – | – |
| **2 Related Work** | 2.1 TTT 与 fast weights | Sun'20/24、Hardt&Sun、LaCT、In-Place TTT、TTT-NTP、Titans、HOPE、DeltaNet | – | – |
| | 2.2 上下文→权重的持久适应 | Temp-LoRA、StreamAdapter、InfiniteICL、SCoL、CaMeLS、MAC | – | – |
| | 2.3 持续测试时适应（视觉） | CoTTA、EATA、SAR、Elastic TTT | – | – |
| | 2.4 持续学习正则与符号统计 | EWC、SI、MAS、LwF；signSGD、Lion；CLS 理论 | – | – |
| **3 Persistent TTT** | 3.1 设定 | 文档流 x₁…x_N；W_eff = W_base + G_fast + G_slow；chunk-wise apply-then-update（沿用 In-Place TTT） | – | – |
| | 3.2 文档内更新 | δ = −η∇_{W_down} L_NTP(chunk)，clip；hook 实现；无优化器状态 | Alg.1 | – |
| | 3.3 边界持久化策略族 | 统一式 G_slow ← γG_slow + α⊙G_fast；表：Reset/Persist/Decay/Consistency/Fisher/Surprise/Random 的 (γ, α) | Tab.1：策略定义 | – |
| | 3.4 一致性门 | D ← γ_d D + (1−γ_d) sign(G_fast)，Π=|D|，α=Π；第一文档只更新 D | – | – |
| | 3.5 分析 | Prop.1：E[Π]=|2p−1|；Prop.2：交替两域流下干扰上界，Persist 线性累积 vs Consistency ≤(1−|2p−1|)倍；Remark：一次性事实被过滤（诚实指出） | – | 附录证明 |
| **4 Streaming-TTT Protocol** | 4.1 三条流 | S-Domain（6 域×3M）、S-Repo（50 仓库，文件按依赖序）、S-Fact（StreamingQA 协议） | Tab.2：流统计 | – |
| | 4.2 指标 | 见 §C | – | – |
| | 4.3 泄漏自检 | 因果性断言、评测位置、held-out 划分；引用 SR-TTT 教训 | – | 单元测试 |
| **5 Experiments** | 5.1 Setup | Qwen3-0.6B/1.7B/4B-Base；GPT-2 XL 附录；η 扫描；3 seeds | – | – |
| | 5.2 Reset vs Persist（motivation） | S-Repo 跨文件补全：Persist ≫ Reset；S-Domain：Persist 通用能力下降曲线 | Fig.2（两面板） | 第 1–2 周 |
| | 5.3 主结果 | 两张 Pareto：(跨文档收益 vs 通用能力保持)、(可塑性 vs 遗忘)，7 策略 × η | Fig.3；Tab.3 主表（1.7B，3 seeds） | 第 4–5 周 |
| | 5.4 重复知识 vs 一次性知识 | S-Repo/S-Domain 上 Consistency 占优；S-Fact 上 Persist/Surprise 占优 → 双存储 recipe | Fig.4 | 第 6 周 |
| | 5.5 消融 | Random-mask 对照；γ_d、clip、chunk size、层子集、Hebbian vs 梯度写入、LoRA 参数化 | Tab.4 | 第 6 周 |
| | 5.6 规模与开销 | 0.6B→4B 趋势；显存/吞吐表 | Tab.5 | 第 6 周 |
| **6 Discussion & Limitations** | – | 只测 LM 任务；门是统计量非学习；显存 +2×fast weight；与学习式门（Titans/SCoL）互补 | – | – |
| **7 Conclusion** | – | – | – | – |
| **附录** | A 证明；B 数据构造；C 超参；D 全部曲线；E GPT-2 XL；F 泄漏自检细节；G 生成样例 | | | |

---

## C. 指标表

| 维度 | 指标 | 定义 | 工具 / 数据 | 为什么需要 |
|---|---|---|---|---|
| 可塑性 | 当前域 PPL 改善 | (PPL_base − PPL_method)/PPL_base，滑动窗口 | 自实现 | 证明还在学 |
| 跨文档收益 | 跨文件补全 EM / Edit-Sim | 仅对"引用早期文件定义的标识符"的行 | RepoBench-P / CrossCodeEval 风格 | Reset 结构上得零分，排除"学得少" |
| 跨文档收益 | 一次性事实 QA F1/EM | 流入文档后回答其中事实 | StreamingQA（Liška et al., 2022）/ CaMeLS 协议 | 暴露一致性门的弱点 |
| 遗忘 | 早期域 held-out PPL 曲线；BWT | GEM 定义（Lopez-Paz & Ranzato, 2017）以 −ΔlogPPL 计 | 自实现 | 标准持续学习指标 |
| 遗忘 | Forgetting Measure | Chaudhry et al., 2018 | 自实现 | 同上 |
| 通用能力保持 | HellaSwag / ARC-E / MMLU 子集 流前 vs 流后 | 0-shot / 5-shot 准确率差 | lm-eval-harness | Titans / In-Place TTT 都报；最能说服审稿人 |
| 长上下文 | RULER 4k–32k 子集（可选） | 平均准确率 | RULER | 证明没丢 TTT 原本的收益 |
| 稳定性 | PPL 爆炸次数、NaN 次数、‖G_slow‖_F 轨迹 | – | 自实现 | 你 V32.2 的教训 |
| 开销 | 峰值显存、tok/s、额外状态大小 | – | torch.cuda | 诚实报告 D 矩阵开销 |
| 综合 | Pareto 前沿、S-P score | √(Stability×Plasticity) 仅作辅助 | – | 单一标量不可信，以 Pareto 为主 |

**必须遵守的统计规范**：主表 3 seeds（种子决定文档顺序）；报告 mean±std；每策略 ≥4 个 η；所有 held-out 集在流开始前固定；评测 prompt 与训练 chunk 无重叠。

---

## D. 引用清单（按用途分组；★ = 必引；? = 需核对确切题名/出处）

### D1. TTT 基础与 LM 上的 TTT
- ★ Sun, Wang, Liu, Miller, Efros, Hardt. *Test-Time Training with Self-Supervision for Generalization under Distribution Shifts.* ICML 2020.
- ★ Sun et al. *Learning to (Learn at Test Time): RNNs with Expressive Hidden States.* 2024 (TTT-Linear/MLP).
- ★ Hardt & Sun. *Test-Time Training on Nearest Neighbors for Large Language Models.* ICLR 2024.
- Hübotter et al. *Efficiently Learning at Test-Time: Active Fine-Tuning of LLMs (SIFT).* ICLR 2025.
- Akyürek et al. *The Surprising Effectiveness of Test-Time Training for Abstract Reasoning.* 2024.
- ★ Zhang et al. *Test-Time Training Done Right (LaCT).* 2025.
- ★ Feng, Luo, Hua, Zhang, He, Huang, Cai. *In-Place Test-Time Training.* ICLR 2026 (arXiv 2604.06169).
- ★ *Test-Time Training with Next-Token Prediction (TTT-NTP).* arXiv 2606.21803, 2026. ?（作者待核）
- Yuksekgonul et al. *Learning to Discover at Test Time (TTT-Discover).* 2026.
- Tandon et al. 2025 ?（TTT-NTP 引用的 in-place 更新工作，题名待核）
- Liu et al. *TTT++: When Does Self-Supervised Test-Time Training Fail or Thrive?* NeurIPS 2021.

### D2. Fast weights 与记忆架构
- ★ Schmidhuber. *Learning to Control Fast-Weight Memories.* Neural Computation 1992.
- ★ Ba, Hinton et al. *Using Fast Weights to Attend to the Recent Past.* NeurIPS 2016.
- Hinton & Plaut. *Using Fast Weights to Deblur Old Memories.* CogSci 1987.
- ★ Schlag, Irie, Schmidhuber. *Linear Transformers Are Secretly Fast Weight Programmers.* ICML 2021.
- ★ Behrouz, Zhong, Mirrokni. *Titans: Learning to Memorize at Test Time.* NeurIPS 2025.
- ★ Behrouz et al. *Nested Learning: The Illusion of Deep Learning Architectures (HOPE/CMS).* NeurIPS 2025 / arXiv 2512.24695.
- Yang et al. *Parallelizing Linear Transformers with the Delta Rule (DeltaNet).* NeurIPS 2024；*Gated Delta Networks.* ICLR 2025.
- Katharopoulos et al. *Transformers are RNNs.* ICML 2020；Gu & Dao. *Mamba.* 2023.
- Karami et al. *Lattice: Learning to Efficiently Compress the Memory.* 2025（可选）.

### D3. 持久适应 / 上下文→权重（LM）
- ★ Wang et al. *With Greater Text Comes Greater Necessity: Inference-Time Training Helps Long Text Generation (Temp-LoRA).* 2024.
- Muhtar et al. *StreamAdapter.* 2024.
- Cao et al. *InfiniteICL.* 2025.
- ★ *Self-Consolidating Language Models: Continual Knowledge Incorporation from Context (SCoL).* arXiv 2605.07076, 2026.
- ★ Hu, Mitchell, Manning, Finn. *Meta-Learning Online Adaptation of Language Models (CaMeLS).* ICLR 2023.
- ★ Tack et al. *Online Adaptation of Language Models with a Memory of Amortized Contexts (MAC).* NeurIPS 2024.
- Agrawal et al. *Learning, Fast and Slow: Towards LLMs That Adapt Continually (FST).* arXiv 2605.12484, 2026.
- *Latent Context Compilation.* arXiv 2602.21221, 2026（综述性引用 Temp-LoRA 一类损害通用能力）.

### D4. 持续测试时适应（视觉）— 同问题的先例
- ★ Wang et al. *Continual Test-Time Domain Adaptation (CoTTA).* CVPR 2022.
- ★ Niu et al. *Efficient Test-Time Model Adaptation without Forgetting (EATA).* ICML 2022.
- Niu et al. *Towards Stable Test-Time Adaptation in Dynamic Wild World (SAR).* ICLR 2023.
- ★ Ma et al. *Fast Spatial Memory with Elastic Test-Time Training.* arXiv 2604.07350, 2026（Fisher 弹性先验 + EMA 锚点，最接近的机制）.
- Swamynathan. *SR-TTT ... Correction and Post-Mortem.* arXiv 2603.06642v2, 2026（评测泄漏与惊奇度门控偏置的警示）.

### D5. 持续学习正则、指标与理论
- ★ Kirkpatrick et al. *Overcoming Catastrophic Forgetting (EWC).* PNAS 2017.
- ★ Zenke, Poole, Ganguli. *Continual Learning Through Synaptic Intelligence (SI).* ICML 2017.
- ★ Aljundi et al. *Memory Aware Synapses (MAS).* ECCV 2018.
- Li & Hoiem. *Learning without Forgetting.* TPAMI 2018.
- ★ Lopez-Paz & Ranzato. *Gradient Episodic Memory (BWT/FWT 定义).* NeurIPS 2017.
- ★ Chaudhry et al. *Riemannian Walk (Forgetting Measure).* ECCV 2018.
- ★ McClelland, McNaughton, O'Reilly. *Why There Are Complementary Learning Systems.* Psych. Review 1995；Kumaran, Hassabis, McClelland. TICS 2016.
- Luo et al. *An Empirical Study of Catastrophic Forgetting in LLMs during Continual Fine-tuning.* 2023.
- Kalajdzievski. *Scaling Laws for Forgetting when Fine-tuning LLMs.* 2024.

### D6. 符号统计与更新规则
- ★ Bernstein et al. *signSGD.* ICML 2018.
- ★ Chen et al. *Symbolic Discovery of Optimization Algorithms (Lion).* NeurIPS 2023.

### D7. 知识在 MLP 中的位置（支撑"只更新 down_proj"）
- ★ Geva et al. *Transformer Feed-Forward Layers Are Key-Value Memories.* EMNLP 2021.
- ★ Meng et al. *Locating and Editing Factual Associations in GPT (ROME).* NeurIPS 2022；*Mass-Editing Memory in a Transformer (MEMIT).* ICLR 2023.

### D8. 数据、基准、工具、模型
- ★ Hsieh et al. *RULER.* 2024.
- ★ Liu et al. *RepoBench.* ICLR 2024；Ding et al. *CrossCodeEval.* NeurIPS 2023.
- ★ Liška et al. *StreamingQA.* ICML 2022.
- Merity et al. *WikiText-103.* ICLR 2017；Rae et al. *PG-19.* ICLR 2020；Kocetkov et al. *The Stack.* 2022.
- ★ Gao et al. *lm-evaluation-harness.* 2023；Zellers et al. HellaSwag 2019；Clark et al. ARC 2018；Hendrycks et al. MMLU 2021.
- ★ Qwen Team. *Qwen3 Technical Report.* 2025；Radford et al. GPT-2 2019.

---

## E. 与最近似工作的"一句话区分"（写进 Related Work 用）

- vs In-Place TTT / TTT-NTP：它们固定了 fast weight 位置与写入机制、每文档重置；我们研究重置与否及"保留什么"，写入机制沿用它们的协议。
- vs Titans / HOPE / SCoL：门控是学出来的、需要（预）训练；我们的策略族免训练、可 drop-in 任何预训练 LLM，且把学习式门控视为互补方向。
- vs Elastic TTT：同样用 EWC 式先验稳定持久 fast weights，但在视觉 LaCT 上从头训练；我们在预训练 LLM 上将 Fisher 作为策略族成员与一致性/惊奇/随机对照并列，并引入跨文档收益指标。
- vs CoTTA/EATA/SAR：同问题在视觉分类上的版本；LM 场景下"跨文档收益"是新的评测维度。
- vs Temp-LoRA 等：证明了上下文可写入权重但也带来漂移；我们系统回答如何控制漂移。

---

## F. 评测泄漏自检清单（附录 F，也用于 CI）
1. 每个 chunk 的 fast weight 更新只使用该 chunk 及之前的 token（断言：更新前 forward 的 logits 与更新后对同一 chunk 的 logits 不参与评测）。
2. 补全/QA 的评测位置 = 答案前一位。
3. held-out 评测文档与流文档去重（MinHash）。
4. S-Repo 的"跨文件标识符"只统计在**早期文件定义、当前文件首次出现**的 token。
5. lm-eval 流前/流后使用完全相同的 few-shot 样例与随机种子。
