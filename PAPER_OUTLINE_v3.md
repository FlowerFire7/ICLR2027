# 论文总大纲 v3（目标 ICML 2027 主赛道；备选 CoLLAs / TMLR）

*基于 week1–4 已确认的现象 + week5（词表修复后）三种可能结局的分支设计。*
*新颖性复核日期 2026-09-01；新增须引：Agentic TTT (2607.03441)、qTTT (Bansal 2025)、ETT (Zahirnia 2025)。*

---

## 0. 标题与一句话主张（按 week5 结局分支）

| week5 结局 | 标题候选 | 一句话主张 |
|---|---|---|
| A. persist 长尾消失（跨会话记忆≈0） | *All Memory Is Local: On the Horizon of Persistent Test-Time Training* | drop-in TTT 的记忆几乎全部活在会话内；跨会话持久只带来风险不带来记忆 → 会话粒度重置是正确默认 |
| B. persist 保有真实长尾 | *The Palimpsest Horizon: How Long Does Test-Time Training Remember?* | 持久 fast weights 是重写本（palimpsest）记忆：可量化的半衰期、可预测的干扰规律、悬崖前免费的收益 |
| C. 中间态 | 同 B，session 作为安全操作点写入 recipe | 同 B + "多数场景下会话重置拿走 x% 收益、0 风险" |

三种结局共享 90% 的正文结构；只有 §5.2 的解读和 §6 recipe 段落分支。**任何结局都不改指标、不改协议、不删负结果。**

---

## 1. 故事逻辑（Introduction 的段落级脚本）

P1 现状：TTT 已成为 LLM 适应流式输入的标准手段（In-Place TTT、TTT-NTP、LaCT、TTT-E2E、Titans）。但所有 drop-in 方法在**文档边界重置** fast weights。
P2 缺口：真实部署是文档**流**（同一个代码库、同一个用户、同一个领域）。重置丢弃跨文档信息；不重置则漂移。没有工作系统回答"持久的 fast weights 记得多久、该保留什么、何时崩溃"。
P3 障碍：为什么没人量过？因为测量本身全是坑——预训练污染（我们展示同一指标从 38% 掉到 1.7%）、上下文复制混淆（首次出现 vs 重复出现）、共享词表伪迹、评测因果泄漏（引 SR-TTT 撤稿）。
P4 我们做了什么：(i) Streaming-TTT 协议：混淆化仓库流 + 固定滞后重测 + 等预算门控 + 随机摆放对照 + 泄漏自检；(ii) 用它系统测量 8 种持久化策略 × 3 个模型规模；(iii) 一个线性联想记忆干扰模型，预测"以累计写入质量为横轴时衰减曲线坍缩到一条"，并被数据验证/证伪。
P5 发现（三条，按结局微调）：跨文档持久带来 15× 的召回收益；记忆按后续写入质量指数衰减（半衰期 ≈ N 个仓库）；参数统计门控在等预算下不优于随机摆放（消解一类流行直觉），激活子空间投影是唯一有效但有代价的旋钮；悬崖 η* 的位置及其前后的通用能力相变。
P6 贡献清单（4 条，动词开头，每条 ≤2 行）。

**故事的灵魂**：不是"我们的方法更好"，而是"我们第一次把 persistent TTT 变成一个可测量、有理论坐标的对象，并纠正了领域内三个会导致错误结论的评测陷阱"。测量型论文要中顶会，靠的是协议无懈可击 + 一个让人记住的理论钩子（palimpsest/scaling collapse）。

---

## 2. Related Work（分五节，每节末尾一句区分语）

2.1 TTT 与 fast weights：Sun'20/24、Hardt&Sun'24、LaCT、In-Place TTT、TTT-NTP、TTT-E2E、Titans、HOPE、DeltaNet/Gated DeltaNet、qTTT、ETT。区分：均为序列内/每文档重置，或需（元）训练。
2.2 连续 TTT 与代理内自训练：Agentic TTT (2607.03441，内生代理文本的 episode 内连续更新)、TTT-Discover。区分：我们研究外生文档流的跨会话记忆与遗忘视界，非 episode 内策略漂移。
2.3 上下文→权重的持久化：Temp-LoRA、StreamAdapter、InfiniteICL、SCoL、CaMeLS、MAC、sleep/consolidation 一线。区分：无"保留什么/记多久"的系统测量。
2.4 视觉持续 TTA：CoTTA、EATA、SAR、Elastic TTT。区分：分类/重建任务、无跨文档召回指标；Elastic TTT 的 Fisher 先验作为我们的策略族成员被检验。
2.5 记忆理论：palimpsest（Parisi 1986）、级联突触（Fusi et al. 2005）、Benna–Fusi 2016、线性联想记忆容量（Willshaw 1969；Hopfield 1982）。区分：我们把这套理论第一次对接到 LLM 的 TTT 实测衰减曲线。
（持续学习正则、signSGD/Lion、Geva/ROME/MEMIT、基准工具照 v2 引用清单。）

---

## 3. 方法与理论（§3）

3.1 设定与统一框架：W_eff = W_base + G_slow + G_fast；chunk 级 clip 梯度写入；边界策略族 π（表 1：8 策略统一为 (γ, α) 的取值）。
3.2 测量协议（本文的方法学贡献，单独小节，含图 1 流程图）：
  - 混淆化（每仓库独立 RNG；报告我们自己踩过的共享词表伪迹作为 cautionary case）
  - 首次出现 vs 重复出现 vs 本地定义三掩码
  - 固定滞后重测（0/5/15/40/end），prequential、写入前打分
  - 等预算 α 归一化 + 随机摆放对照
  - 五条泄漏自检（附录单元测试；引 SR-TTT）
3.3 理论（四个命题，全部可证、全部可测）：
  - **P1（干扰衰减律）**：线性联想 fast weight 中，会话 k 的召回信噪比 SNR ∝ m_k / √(Σ_{j>k} m_j²)，m 为写入质量（随机方向假设）。推论：以"其后累计写入质量"为横轴，不同 η、不同策略的保持曲线应**坍缩**为一条。→ 图 4 直接检验。
  - **P2（一致性门期望）**：E[Π]=|2p−1|；单次方向在期望上被过滤 → 解释为什么它不帮助一次性标识符（诚实预告负结果）。
  - **P3（有界性/悬崖必要条件）**：‖G_slow‖ ≤ clip·T_write；结合 P1 给出"悬崖前收益免费"的非正式论证。
  - **P4（session 的零干扰）**：会话重置 = 把 P1 的求和截断在会话内，跨会话干扰恒为零（构造性，两行）。
  - 全部证明进附录 A；正文每个命题 ≤3 行 + 一句"数据如何检验它"。

---

## 4. 实验设计（§4–5；全部预先注册在附录 H）

### 4.1 指标定义（表 2）
| 指标 | 定义 | 统计处理 |
|---|---|---|
| Recall@lag L | 滞后 L 个会话时 held-out 首次出现标识符 top-1 准确率 | **按仓库聚类的 bootstrap 95% CI**（同仓库目标相关，逐目标 CI 会虚窄——审稿人必查） |
| 半衰期 λ | 对 Recall(lag)−base 拟合指数（横轴=累计后续写入质量） | 拟合参数报 CI；两种横轴（#会话 / 写入质量）都给 |
| Plasticity | Recall@0 − base；辅以 xfilePPL | 同上 |
| GCR | lm-eval（HellaSwag, ARC-E, MMLU-sub, 各 500 题, 固定 few-shot 种子）流前后差 | 3 seeds 均值±std |
| 悬崖 η* | GCR 跌破 −2pt 的最小 η | η 网格 {1,2,3,4,5,6}e-2 |
| 成本 | 额外显存 / 吞吐比 / 状态大小 | 实测表 |

### 4.2 实验矩阵
- **E1 主结果**（图 2+表 3）：Qwen3-1.7B，200 仓库流，{base, reset, persist, session, decay, consistency*, random*, fisher*, surprise}（*=等预算），3 seeds（seed 同时决定仓库顺序与混淆词表）。
- **E2 规模**（图 3）：0.6B / 1.7B / 4B 上 {persist, session, base}，1 seed + 主对比 3 seeds；结论必须写成"趋势"而非"定律"。
- **E3 泛化流**（表 4）：非代码流 —— 训练截止后（2026-02 之后）的维基/新闻实体页构成的实体流，held-out 实体填空，同一滞后协议。目的：证明视界现象非代码特有。若结论不一致，如实报告差异并分析。
- **E4 scaling collapse**（图 4）：persist@{2,3,4,6}e-2 的保持曲线按 P1 变换横轴后叠画。这是理论—实验闭环的核心图。
- **E5 placement**（图 5）：等预算 consistency vs random（3 seeds）+ projection p∈{32,64,128,256} 的 plasticity–retention 前沿。
- **E6 消融**（表 5）：chunk∈{128,256,1024}、clip 倍率、层子集（全/top⅓/mid⅓/bot⅓）、LoRA-r64 参数化 vs 全秩、Hebbian 写入 vs 梯度、ctx_len。
- **E7 污染与泄漏**（表 6）：混淆 on/off 差（38%→1.7% 这张牌）、共享词表伪迹复现（旧 seed 方案 vs 新方案的对比曲线——把我们的 bug 变成论文的论据）、五条自检通过记录。

### 4.3 统计规范
主假设族只有三个（预注册）：H1 persist>reset@lag0；H2 persist 长尾>base@lag40；H3 consistency=random（等预算，等价性检验 TOST，边界 ±2pt）。Holm 校正只作用于这三个；其余全部标注 exploratory。所有图带 CI；所有表带 seed 数。

---

## 5. 审稿人攻击 → 预置防御（写作时逐条自查）

| 预期攻击 | 防御 |
|---|---|
| "就是在线微调，不是 TTT" | §3.1 沿用 In-Place TTT 的 chunk 协议与 fast-weight 位置；TTT-E2E/Hardt&Sun 均以 NTP 梯度为 TTT；消融含 Hebbian 写入 |
| "只是学得少/学得多" | 等预算归一化 + 随机对照 + Pareto 前沿；Recall@0 与 lag 曲线分开报 |
| "污染" | 混淆化 + 训练截止后语料 + 表 6 定量 |
| "CI 造假/相关样本" | 聚类 bootstrap，附录给逐目标 vs 聚类两种 CI 的对比 |
| "只在代码上成立" | E3 |
| "只在 0.6B 上成立" | E1 主表就是 1.7B；E2 到 4B |
| "为什么不比 Titans/HOPE" | 需从头训练，非 drop-in；related work 明说，并把其门控思想（surprise/decay）纳入策略族 |
| "理论是玩具" | 理论只做可检验预测（scaling collapse），图 4 直接对质；不宣称超出线性模型的普适性 |
| "负结果没价值" | 随机对照使负结果成为"消解一类直觉"的证据；引 Elastic TTT/DDL 式门控的流行度说明该直觉确实流行 |
| "显存翻倍" | 成本表如实报告；session/decay 不需要 D/F 状态 |
| "novelty 不足" | §2 逐条一句话区分 + 协议与 benchmark 开源作为独立贡献 |

---

## 6. 写作与提交清单

- 结构：8 页正文 = Intro 1.2 / RW 0.8 / 方法+理论 1.8 / 协议 0.8 / 实验 2.8 / 讨论+局限 0.6；附录 A 证明、B 流构造、C 超参全表、D 全曲线、E 泄漏测试、F cautionary cases、G 生成样例、H 预注册。
- 图规范：每图单独可读（标题句式=结论句）；图 2（主 horizon 曲线）和图 4（collapse）要能撑起 talk 的前两张 slide。
- 可复现：代码 + 流构造脚本 + 全部 JSON 结果开源（MIT 仓库列表附 license 清单——fetch 脚本已过滤 MIT）；ICML checklist 逐项；算力披露（单 A100，总 GPU 时）。
- 伦理/许可：仓库均 MIT；维基/新闻流注明许可与去 PII；无人类受试。
- Limitations 必写：仅语言建模类指标；单一架构家族为主；理论为线性近似;门控结论限于参数统计类门。
- 时间表：week5 重跑（1 天）→ E1/E4（4 天）→ E3 构造+运行（4 天）→ E2/E5/E6（4 天）→ 写作（7 天）→ 内审+补图（3 天）→ arXiv（~10 月上旬）→ ICML 摘要注册与全文（2027-01）。缓冲 2 周。

---

## 7. 新颖性复核结论（2026-09-01）

新增检索确认：Agentic TTT（episode 内连续更新，内生文本）、FST（文本作 fast weights）、sleep/consolidation 线均不做外生文档流的跨会话保持测量；qTTT/ETT 为单输入适应。**"drop-in 免训练 + 外生文档流 + 持久化策略族 + 随机对照 + 滞后保持曲线 + 干扰理论对接"的组合仍无先例。** 风险登记：该领域月更，投稿前两周需再复核一次；若被抢先，差异点退守协议严谨性 + scaling collapse + 负结果对照。
