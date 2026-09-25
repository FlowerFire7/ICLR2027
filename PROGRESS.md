# Persistent Test-Time Training 项目进度

**项目目标**：验证跨文档持久化 fast weights 的有效性，系统比较 7 种持久化策略

---

## 工作规矩

1. **实验监控**：确认实验正常运行后等待其结束即可，不需要一直监控。需告知预计所需时间。
2. **GPU 分配**：使用 GPU1 (`CUDA_VISIBLE_DEVICES=1`)
3. **进度记录**：所有待办和已完成事项都需记录在本文档

---

## 待办事项

### Week 1（已完成）
- [x] 解压代码包 ptt_week1.zip
- [x] 阅读代码结构和大纲
- [x] 运行因果性测试 (test_causality.py) — 5/5 通过
- [x] 清理磁盘空间（删除 medgemma-27b + 两个大数据集，释放 99GB）
- [x] 运行 week1.sh 实验（GPU1）— 完成，总耗时约 15 分钟
- [x] 分析结果 — **判据未通过**，persist vs reset 仅高 0.4 个点（预期 ≥3）
- [x] Week1b 诊断与修复（混淆、chunk=256、更大η范围）
- [x] 运行 week1b.sh 实验（GPU1）— 完成，总耗时约 50 分钟
- [x] 分析结果 — **✅ 判据通过**，persist vs reset 高 6.3 个点

### Week 2（已完成）
- [x] 解压 ptt_week2.zip
- [x] 安装 lm-eval
- [x] 运行因果性测试 — 5/5 通过
- [x] 抓取 50 个仓库（2025-06 后创建，降低污染）
- [x] 运行 week2.sh（7策略 × 2η + persist崩溃点）— 完成，总耗时约 8 小时
- [x] 分析结果（xfilePPL、dGen、BWT_x）— **✅ 完整 7 策略比较完成**

### Week 3（已完成）
- [x] 解压 ptt_week3.zip
- [x] 运行因果性测试 — 5/5 通过
- [x] 抓取 200 个仓库（2025-06 后创建）
- [x] 运行 week3.sh（等预算比较 + 遗忘测量）— 完成，总耗时约 15 小时
- [x] 分析结果 — **等预算下 placement 无显著差异；persist 在长流上确实遗忘**
- [x] 运行 horizon.py 生成半衰期表 — **persist 半衰期仅 ~5 个仓库**

### Week 4（进行中）
- [x] 解压 ptt_week4.zip
- [x] 运行 horizon.py 确认半衰期
- [x] 解压 ptt_week4b.zip（修正测量协议：固定滞后重测）
- [x] 运行 week4.sh（8 次运行）— **完成**
- [x] 分析结果 — **发现 session 测量 bug**
- [x] 解压 ptt_week4c.zip（修复 session 测量时机）
- [x] 重跑 session — **完成**
- [x] 分析结果 — ⚠️ **数据已作废**（见 Week 5 混淆器修复）

### Week 5（已完成 ✅）
- [x] 发现混淆器混杂因素：每个仓库用同一 seed，200 个仓库共享伪词表
- [x] 解压 ptt_week5_fix.zip（修复：每仓库 seed 由仓库名 CRC 派生）
- [x] 5 策略全部完成（base, persist, session, consistency_norm, random_norm）
- [x] 生成 horizon.txt 和 cluster CI
- [x] **裁决性结论**：走大纲结局 A — "All Memory Is Local"

### Week 5b（已完成 ✅）
- [x] 解压 ptt_week5b.zip（新增 cluster_ci.py、--fresh_repos）
- [x] 运行 cluster_ci.py — CI 确认长尾为噪声
- [x] 准备 repos_fresh（20 个仓库）和 repos180（180 个仓库）
- [x] 诊断 1：persist + fresh_repos — **完成**
- [x] 诊断 2：E4 坍缩数据（persist@η={2e-2, 4e-2}）— **完成**

### E1 主表（已完成 ✅）
- [x] 1.7B 测试运行完成：
  - base: 47 分钟，显存 7.7GB
  - persist: 116 分钟，显存 7.7GB
  - 不需要 --grad_ckpt
- [x] 解压 ptt_e1.zip（general_limit 提到 2000 + general_cache 缓存 BEFORE）
- [x] 解压 ptt_e1b.zip（5 任务 general_eval + fresh 逐仓库记录 + paired.py）
- [ ] **E1 全量运行中**（15 次，general_limit=2000）
  - seed 0（旧版本，2 任务）: ✅ base, persist, session, consistency 完成；**random 运行中**
  - seed 1（新版本，5 任务）: 待运行（5 次）→ `run_e1b_continue.sh`
  - seed 2（新版本，5 任务）: 待运行（5 次）→ `run_e1b_continue.sh`
- **预计剩余时间**：约 **22-26 小时**
- **配对检验挂起**：consistency − persist 在 lag0/5 有正差但 CI 擦零，等三 seed 合并
- 日志：`ptt/results/e1/run.log`
- 输出：`ptt/results/e1/ci.txt`、`ptt/results/e1/paired.txt`

### E3 实体流（✅ 已完成）
- [x] 解压 ptt_e3.zip
- [x] 新增 `ptt/streams/entity.py`（S-Entity 实体流）
- [x] 新增 `scripts/run_entity.py`（运行接口）
- [x] 新增 `scripts/fig_horizon.py`（图 2/4 绘图脚本）
- [x] week3_repo.py 补丁：per_repo 记录添加 `tokens` 字段
- [x] 因果性测试：5/5 通过
- [x] E3 seed 0 @ η=3e-2（5 策略）完成
- [x] NLL 分析：发现平坦曲线（11x→10x）= 音节分布适应伪迹（第 6 个）
- [x] E1 NLL 仪器校验：正常衰减（8x→3.7x）✅
- [x] 解压 ptt_e3fix.zip（fresh 记 PPL + 每会话独立音节池）
- [x] η 校准完成：η=3e-3（-2.3pt）, η=1e-2（-2.0pt）, η=3e-2（-5.2pt 过膝）
- [x] **η* = 1e-2 选定**（税负与 E1 的 3e-2 重合，保留更多可塑性）
- [x] E3v3 三 seed 完成（base, persist, consistency, random × 3 seeds）
- [x] **Placement 机制验证**：
  - 流内 c-r = -0.17~-0.22（全 lag 恒定）
  - Fresh c-r = **-0.17**（与流内相等）
  - **结论**：E3 placement 是纯适应型效应（vs E1 纯记忆型）

### 图表定案
- [x] **图 2 改为双面板**（accuracy + logPPL）
  - E1 NLL 曲线 8x→5x→4x→3.7x 衰减清晰
  - H2 主证据换用 NLL 面板
  - accuracy 长尾 +0.67pt vs NLL 长尾 3.7x

### 插空任务
- [ ] 4B 三次（base/persist/consistency_norm @ η=3e-2，代码流）— 最后一块数据
- [ ] 0.6B persist@5e-2（补悬崖右侧一点）
- [x] ~~Fresh 20 仓库聚类 CI：0.013 [0.004, 0.046]~~（CI 太宽，功效不够）
- [x] **Fresh 扩容到 65 个仓库**（提高归因段统计功效）

### 后续（Week 6+）
- [ ] E2 规模验证（0.6B/1.7B/4B）
- [ ] 论文写作

---

## 进度日志

### 2026-08-30

**09:38** - 项目初始化
- 解压 ptt_week1.zip 到 /data/ziming_workspace/kaiyi/ICLR/ptt/
- 阅读完成：
  - TTT_PAPER_OUTLINE_AND_CITATIONS.md（大纲、指标、引用）
  - fastweight.py（核心实现）
  - runner.py（apply-then-update 循环）
  - streams/repo.py（S-Repo 流）
  - test_causality.py（5 条因果性自检）
  - week1.sh（实验脚本）

**关键核验结论**：
1. 最近似工作：Elastic TTT（Fisher 弹性先验，视觉 LaCT）、SCoL（meta-RL 选择器，需训练）
2. SR-TTT 撤回警示：惊奇度门控有位置偏置，评测需因果自检
3. 指标：主用 Pareto 图，通用能力用 lm-eval HellaSwag/ARC-E/MMLU

**09:45** - 因果性测试
- 运行 test_causality.py（CPU）— 5/5 全部通过
  - test_eval_only_is_frozen
  - test_apply_then_update
  - test_policy_identities
  - test_random_matches_consistency_histogram
  - test_reset_equals_isolated_docs

**09:50** - 磁盘空间清理
- 问题：磁盘空间不足（仅剩 286MB），Qwen3-0.6B-Base 下载失败
- 解决：删除 medgemma-27b (51GB) + open-web-math (26GB) + openwebtext (23GB)
- 结果：释放 99GB 空间

**09:55** - Week1 实验启动
- 模型：Qwen/Qwen3-0.6B-Base
- GPU：CUDA_VISIBLE_DEVICES=1
- 流：544 docs, 1.35M tokens, 27364 xfile targets
- 实验配置：base + reset/persist × 3η (3e-4, 1e-3, 3e-3)

**10:10** - Week1 实验完成
- 总耗时：约 15 分钟
- 结果文件：`/data/ziming_workspace/kaiyi/ICLR/ptt/results/week1/summary.txt`

**10:28** - Week1b 实验启动
- 解压 ptt_week1b.zip，覆盖更新代码
- 修复：标识符混淆、chunk=256、η ∈ {1e-3, 3e-3, 1e-2, 3e-2}
- 配置：base + reset×4η + persist×4η + base_noobf

**11:20** - Week1b 实验完成
- 总耗时：约 50 分钟
- 结果文件：`/data/ziming_workspace/kaiyi/ICLR/ptt/results/week1b/summary.txt`
- **判据通过**：persist(η=3e-2) xfile=8.1% vs reset(η=1e-3) xfile=1.8%，差 +6.3 点

**12:00** - Week2 实验启动
- 解压 ptt_week2.zip
- 安装 lm-eval（已安装）
- 因果性测试：5/5 通过
- 抓取 50 个仓库（2025-06 后创建）
- 配置：7策略 × 2η (1e-2, 3e-2) + persist η=1e-1 + base = 16 次运行
- 新增指标：xfilePPL、dGen（lm-eval 前后差）、BWT_x（backward transfer）

**20:29** - Week2 实验完成
- 总耗时：约 8.5 小时（16 次运行）
- 结果文件：`/data/ziming_workspace/kaiyi/ICLR/ptt/ptt/results/week2/summary.txt`
- **✅ 7 策略完整比较完成**

### 2026-08-31

**16:03** - Week3 实验启动
- 解压 ptt_week3.zip
- 因果性测试：5/5 通过
- 抓取 200 个仓库（2025-06 后创建，降低预训练污染）
- 配置：8 次运行（base, persist, decay γ=0.98, consistency_norm, fisher_norm, random_norm, surprise, persist η=6e-2）
- **关键修正**：
  1. **等预算比较**：`--alpha_norm` 把门控 α 归一化到均值 1，只比"写在哪"
  2. **正确遗忘测量**：每仓库留出最后一个文件作 holdout，仓库结束时测 acc_then，流结束后测 acc_end
  3. **fisher 修复**：从 max 归一化改成中位数相对的软门 `α = 1/(1+F/median(F))`
- 新指标：acc_then, acc_end, retention, retention_first_third
- 预计耗时：约 12-16 小时（200 仓库流约是 Week 2 的 4 倍长）

**07:02** - Week3 实验完成
- 总耗时：约 15 小时（8 次运行）
- 结果文件：`/data/ziming_workspace/kaiyi/ICLR/ptt/ptt/results/week3/`

### 2026-09-01

**10:55** - Week3 结果深度分析 & Week4 启动
- 运行 `horizon.py` 生成半衰期表
- **关键发现**：persist@3e-02 半衰期只有 ~5 个仓库，15 个仓库后完全归零
- **纠正之前的错误解读**：
  1. 不存在"最平衡的策略"——`end` 列几乎是常数（0.013-0.020），reten 排名只是 then 的倒序
  2. 等预算下 consistency ≈ random ≈ persist，DDL 门控假设正式证伪
- 解压 ptt_week4.zip
- 配置：session + GPM 投影（k=64/256）

**11:00** - Week4 测量协议修正
- **问题**：consistency_norm 在 5-15 区间有 0.052 vs random/persist 的 0.000，但这只覆盖十几个仓库，没有误差棒
- **修正**：固定滞后重测协议 `--lags 0,5,15,40`，200 个仓库全部贡献每个滞后点
- 解压 ptt_week4b.zip
- 启动 week4.sh（8 次运行）
  - session, persist, consistency_norm, random_norm
  - persist_p64, persist_p256（GPM 投影）
  - consistency_norm_s1, random_norm_s1（第二 seed，placement 结论主要证据）
- 预计耗时：与 Week 3 相当（每次约 2 小时，共约 16 小时）

### 2026-09-02

**09:30** - Week4 实验完成，发现 session 测量 bug
- 8 次运行全部完成
- **Bug**：`week3_repo.py` 把 `fw.end_session()` 放在 lag0 评测之前
  - session 策略在仓库边界清零 G_slow，然后才测 holdout
  - 测到的是 base 效果（0.007），不是 session 真实效果
  - **其他策略的 end_session 只更新投影基、不动权重，数字有效**
- 解压 ptt_week4c.zip（修复测量时机）
- 启动 session 重跑（单次运行）

**13:30** - Session 重跑完成
- lag0 = 0.071±0.011（比 persist 的 0.110 低 35%，但仍是 base 的 10 倍）
- lag5+ 全归零（仓库边界重置后无跨会话记忆）
- dGen = +0.000（完美保护通用能力）
- ⚠️ **数据已作废**：见下方混淆器 bug

### 2026-09-03

**10:00** - 发现混淆器系统性混杂因素
- **问题**：`_obfuscate_repo` 对每个仓库用同一 seed，RNG 序列每仓库重新开始
  - 按字母序第 k 的定义名 → 映射到同一随机串
  - 200 个仓库共享一套伪词表
- **后果**：persist 积累的是"共享词表先验"而非仓库特异记忆
- **解释了三个反常**：
  1. persist lag0 比 session 高 35%（session 重置丢掉词表先验）
  2. lag15≈lag40≈end≈0.019 的"长尾"太平（词表先验不衰减）
  3. 各策略 end 收敛到同一水平
- **修复**：每仓库 seed = CRC(仓库名) ^ 全局seed，词表跨仓库不再共享
- **验证**：旧方案两"不同"仓库共享 38 个假名，新方案互不相同；5 个测试全过

**10:30** - Week 5 启动（裁决性重跑）
- 5 次运行：base, persist, session, consistency_norm, random_norm
- 三种可能结局：
  1. persist 长尾消失 → session 成为干净 recipe，论文强度回升
  2. persist 仍有真实长尾 → 半衰期刻画主线保留
  3. 中间态 → 如实报告，"共享词表混杂"写进协议节作为反面案例
- 预计耗时：约 15-20 小时

**~01:09** - Week 5 实验中断
- **已完成**：base（39 分钟，197 个仓库）
  - acc_then = 0.0096（基线水平）
  - dGen = 0（无变化）
- **待运行**：persist, session, consistency_norm, random_norm（4 个策略）
- **状态**：实验进程已停止，GPU 空闲
- **预计剩余时间**：8-12 小时（每个策略约 2-3 小时）
- **需要**：手动重启实验继续运行

**09:56** - Week 5 实验重启
- 创建 `scripts/week5_continue.sh` 跳过已完成的 base
- 在 GPU1 后台启动剩余 4 个策略：persist, session, consistency_norm, random_norm
- 日志文件：`results/week5/run.log`

### 2026-09-04

**08:50** - Week 5 实验全部完成 ✅
- 5 个 JSON 文件：base, persist, session, consistency_norm, random_norm
- horizon.txt 自动生成

**09:00** - Week 5 裁决性分析

**Horizon 表（修复混淆器后）**：

| policy | lag0 | lag5 | lag15 | lag40 | end | dGen |
|--------|------|------|-------|-------|-----|------|
| base | 0.010 | 0.010 | 0.009 | 0.010 | 0.010 | +0.000 |
| persist | **0.088** | 0.030 | 0.019 | 0.012 | 0.014 | +0.009 |
| session | **0.072** | 0.010 | 0.009 | 0.010 | 0.010 | **+0.000** |
| consistency_norm | 0.086 | 0.034 | 0.019 | 0.015 | 0.019 | **-0.087** |
| random_norm | 0.084 | 0.028 | 0.017 | 0.014 | 0.015 | -0.001 |

**Cluster CI（聚类 bootstrap 95%）**：

| policy | lag0 CI | lag5 CI | lag15 CI | lag40 CI |
|--------|---------|---------|----------|----------|
| base | [0.006,0.014] | [0.006,0.014] | [0.006,0.014] | [0.006,0.015] |
| persist | [0.065,0.117] | [0.022,0.038] | [0.013,0.025] | [0.007,0.017] |
| session | [0.050,0.099] | [0.006,0.014] | [0.006,0.014] | [0.006,0.015] |
| consistency_norm | [0.063,0.113] | [0.023,0.046] | [0.013,0.025] | [0.009,0.020] |
| random_norm | [0.056,0.102] | [0.021,0.036] | [0.013,0.024] | [0.011,0.023] |

**三个决定性读数**：

1. **长尾确认为伪迹**：persist lag40 [0.007,0.017] 与 base [0.006,0.015] CI 重叠
   - 但 lag5 [0.022,0.038] 与 base 不重叠 — 短程记忆（半衰期 <5 会话）是真实的

2. **session 拿到 79% 峰值收益、零成本**：
   - (0.072−0.010)/(0.088−0.010) = 79%
   - dGen = 0，无悬崖暴露
   - 剩余 0.016 差距可能是流级风格迁移，需 fresh_repos 诊断

3. **consistency 门控从"无用"升级为"有害"**：
   - dGen = -0.087（三次运行全为负）
   - 保持率与 random 无异
   - 机制：把写入集中到方向一致的坐标 = 放大域漂移方向

**结论**：走大纲**结局 A** — *"All Memory Is Local"*

**09:30** - Week 5b 启动
- 解压 ptt_week5b.zip（新增 cluster_ci.py、--fresh_repos 选项）
- 运行 cluster_ci.py 完成
- 准备 repos_fresh（20 个仓库从 repos200 挪出，repos200 重命名为 repos180）

**09:14** - Week 5b 诊断实验启动
- 3 次运行：
  1. persist + fresh_repos（测风格迁移 vs 记忆）
  2. persist@η=2e-2（E4 坍缩数据）
  3. persist@η=4e-2（E4 坍缩数据）
- 日志：`results/week5b/run.log`
- **状态**：运行中（20/180 仓库）
- **预计耗时**：约 9-12 小时（每次约 3-4 小时）

**09:28** - E3 代码包就绪
- 解压 ptt_e3.zip
- 新增文件：
  - `ptt/streams/entity.py`：S-Entity 实体流（WikiText-103 文章 → 会话，命名实体 → 合成假名）
  - `scripts/run_entity.py`：运行接口
  - `scripts/fig_horizon.py`：图 2（Recall-vs-lag 曲线）+ 图 4（坍缩图）绘图脚本
- week3_repo.py 补丁：per_repo 添加 `tokens` 字段（E4 坍缩图横轴需要）
- 因果性测试：5/5 通过
- **E3 设计要点**：
  - 会话 = 一篇长维基文章切成 3-12 个文档
  - 反复出现的命名实体 → 音节合成假名（"Kave Lorin"风格）
  - 每会话独立 RNG 词表（构造上杜绝污染）
  - 掩码：首次提及 / 重复提及 / 会话内引入（与 S-Repo 一致）
  - 30 个会话扣作 fresh 对照
- **优先级**：E3 可插在 1.7B 队列空隙，诊断 1 出来后立即排 E1 主表

**21:22** - E1 全量运行启动（已作废）
- 解压 ptt_e1.zip
- general_limit 从 500 提到 2000
- ⚠️ **问题**：fresh=20 仓库的 CI 太宽（0.003 [-0.006, 0.036]），功效不够

**21:29** - E1 重启（fresh 扩容后）
- **修正**：fresh repos 从 20 扩容到 **65 个**
- 目的：收窄 CI 到 ±0.01 内，提高归因段统计功效
- 论文口径：若 CI 仍含 0 → "generic transfer consistent with zero"；若 CI 离开 0 → 承认小量风格迁移
- 15 次运行，预计 ~24 小时
- 日志：`results/e1/run.log`

**收到 §1-§2 初稿**：`DRAFT_sec1_sec2.md`
- Introduction 把四个评测陷阱放在第三段（先于结果）
- 贡献 4 把负结果写成"有牙齿的负结果"
- Related Work 每小节末尾斜体句是预置审稿人问答
- 方括号数字待 E1 回填

**Fresh 聚类 CI 补充**：
```
Fresh acc: 0.0131 [0.0036, 0.0464]
vs base: excess = 0.0031 [-0.0064, 0.0364]
结论: CI 包含 0，风格迁移与零无显著差异
```

**17:38** - E1 测试运行
- 模型：Qwen/Qwen3-1.7B-Base
- 配置：η=3e-2, clip=3e-2, chunk=256, ctx=1024
- 策略：{base, persist, session, consistency_norm, random_norm}
- Seeds：{0, 1, 2}（同时重排仓库顺序与混淆词表）
- 总计 15 次运行
- **测试结果**：显存峰值 7.7GB，不需要 --grad_ckpt
- **速度**：~8 秒/仓库，每次运行约 30-35 分钟
- **预计总耗时**：约 8-9 小时
- 日志：`results/e1_test/`

### 2026-09-05

**16:14** - E1 实验进度检查
- **seed 0 完成情况**：
  - ✅ base_s0.json（完成）
  - ✅ persist_s0.json（完成）
  - ✅ session_s0.json（完成）
  - ✅ consistency_s0.json（完成）
  - 🔄 random_s0.json（运行中，140/180 仓库，约 78%）
- **GPU 状态**：A100-80GB GPU1 使用中（12.4GB/81.9GB）
- **预计剩余时间**：约 22-26 小时

**16:30** - 收到 ptt_e1b.zip 更新
- **三处更新**：
  1. fresh 逐仓库记录（`per_repo` 字段，可算聚类 CI）
  2. `--general_eval` 默认扩为 5 任务：hellaswag, arc_easy, arc_challenge, piqa, winogrande
  3. 新增 `scripts/paired.py`（配对比较脚本）
- **配对检验初步结果（seed 0）**：
  - consistency − persist: lag0 = +0.0103 [−0.0005, +0.0213], lag5 = +0.0056 [−0.0005, +0.0123]
  - 方向一致但 CI 下界擦零，单 seed 不显著
  - **结论挂起**：等三 seed 合并后再判断 "placement 在更大模型上起作用"
- **运行计划**：
  - random_s0（旧版本）继续完成
  - seed 1 & 2（10 次运行）用新版本：`scripts/run_e1b_continue.sh`
  - 已完成的 base_s0/persist_s0/consistency_s0 暂不重跑
  - 若 5 任务 dGen 必要，后补 persist_s0 和 consistency_s0
- **表注事项**：180 仓库中 124 个有合格 holdout（≥5 xfile 目标），lag40 仅 96 个可测

### 2026-09-06

**13:40** - E1 主表全部完成 ✅
- **15/15 运行完成**（5 策略 × 3 seeds）
- **结果文件**：`results/e1/ci.txt`、`results/e1/paired.txt`

**14:30** - E1 定案分析（3 seed 配对合并，聚类 CI）

**三条定案结论**：

1. **主效应**：persist−base lag0 = **+6.2 点 [+5.0, +7.5]**，7.5 倍于冻结基线

2. **长尾存在，标题分支改走 B**：
   - persist−base lag40 = **+0.67 点 [+0.28, +1.07]**，显著
   - 峰值超额的约 **11%** 存活超过 40 个会话
   - 0.6B 功效不足（CI 含零），措辞："1.7B 上可检出细长尾；0.6B 数据相容但功效不足"
   - **标题定 "The Palimpsest Horizon"**：快衰减 + 细残留 = 重写本记忆经典签名

3. **Placement 定案，H3 被推翻**：
   - consistency−random 合并：lag0 **+1.22 [+0.60, +1.91]**、lag5 **+1.00 [+0.49, +1.53]**
   - lag15 起归零
   - 等预算下一致性门买到短程召回，**仅在 1.7B 出现**
   - random−persist 全滞后 ≈0（week4 的 lag40 星号确认为多重比较噪声）

4. **session 收益比例修正**：**60%（45–72%）**，不是 87%
   - session−persist 四个滞后全部显著为负
   - fresh 迁移只 +0.5 点，解释差距的 ~20%；剩余 ~2 点 unattributed
   - session 的 dGen=0 是**结构性保证**（流在仓库边界结束，终态=原始权重）

**两条撤回**：

1. ~~"consistency 独有通用能力损害"~~：1.7B 不复现，hellaswag −3 是所有持久策略共付
2. ~~"膝点以下代价≈0"~~：1.7B 上 η=3e-2 一致付 hellaswag −3、换 arc_easy +5~+6（5 次复现）

**测量缺口修复**：
- 已运行 5 任务 BEFORE 评测：`results/e1/gen_before_1.7B_5task.json`
- arc_challenge/piqa/winogrande 差值和 acc/acc_norm 诊断现可计算

**acc vs acc_norm 诊断结果（§5.8 悬案了结）**：

| 运行 | arc_easy d_acc | arc_easy d_norm | hellaswag d_acc | hellaswag d_norm | piqa d_acc | piqa d_norm |
|------|----------------|-----------------|-----------------|------------------|------------|-------------|
| persist_s0 | +0.003 | +4.7 | -2.7 | -2.6 | -2.6 | -2.4 |
| persist_s1 | -0.003 | +5.5 | -2.5 | -2.5 | -3.5 | -3.4 |
| random_s0 | +0.012 | +5.9 | -3.8 | -3.9 | -2.6 | -2.3 |

**三条定案**：

1. **arc_easy +5~6 点是计分规则伪迹，不是能力提升**
   - 原始 acc 几乎不动（±0.02）
   - 只有 acc_norm 在跳（+4.7~+5.9）
   - TTT 改变 token 似然轮廓 → 被 acc_norm 放大
   - **协议贡献**：给 TTT 评测领域的警示（很多论文只报 acc_norm）

2. **真实代价浮出水面**：
   - hellaswag: −2~−4（d_acc 和 d_norm 同向同幅）
   - piqa: −2~−3.5（同向同幅）
   - **膝点以下就在支付的真实税**，所有持久策略均摊，consistency 不特殊

3. **recipe 两侧变实**：
   - persist = 多 40% lag0 召回 + 细长尾，代价 2–3.5 点常识任务税 + 悬崖暴露
   - session = 60% 召回、零税（结构保证）、零暴露
   - **"session 放弃收益换取本来就不存在的安全"的隐忧消除——税是真的**

**论文改动**：§5.4 与 §5.8 合并 → "The tax and the mirage: what persistence costs, and what it only appears to gain"

**16:36** - E3 @ 1.7B 启动（首次，数据为空）

**21:27** - E3 修复并重启
- **发现问题**：WikiText 用单换行分隔段落，`_split_docs` 期望双换行
- **修复**：`entity.py` 添加 fallback 逻辑处理单换行
- **验证**：201 stream sessions, 30 fresh; 1.1M tokens
- 当前运行：seed 0，五策略（base, persist, session, consistency, random）
- 预计耗时：~4-5 小时
- 日志：`results/e3/run.log`

**运行队列**：
1. ✅ E3 @ 1.7B seed 0（运行中）
   - 完成后先发配对结果（consistency−random、persist−base 的 lag40）
   - 方向一致则补 seeds 1/2
2. ⏳ 0.6B persist@5e-2（~2 小时，补膝点图）
3. ⏳ 4B seed0 四策略 {base, persist, consistency_norm, random_norm}（~18 小时，测 placement 是否随规模变大）

**下一步**：填 §5 数字，出图 2/3/4/6，合并 LaTeX（数据齐后 48 小时内交初稿）

---

### 2026-09-07

**00:08** - E3 η 校准启动
- 背景：η=3e-2 过膝点（hellaswag 跌 5.2 点 vs E1 的 2-3 点）
- 运行 persist @ η∈{3e-3, 1e-2}，找通用能力税落在 -2~3 点的 η*
- 日志：`results/e3/run.log`

**00:10** - E3 NLL 初步分析

**问题诊断**：base accuracy = 0.26%，完全贴地
- 实体流上预测"Wexre"是开放词表的无约束槽位（不像代码 `from x import `）
- 即便模型把概率从 0.05%→1%（20 倍似然比！），argmax 仍输给"the"，top-1 得 0 分
- 改用 NLL/PPL 作为读数仪

**00:30** - ⚠️ **第五个测量伪迹：音节分布适应（已内部拦截）**

**红牌**：E3 的 NLL 曲线**完全平坦**
| lag | E3 PPL ratio | E3 改善 |
|-----|--------------|---------|
| 0 | 0.09x | 11x |
| 5 | 0.11x | 9x |
| 15 | 0.11x | 9x |
| 40 | 0.10x | **10x（应该衰减！）** |

**对照：E1 代码流 NLL 正常衰减（仪器校验通过）**
| lag | E1 dlogPPL | E1 PPL ratio | E1 改善 |
|-----|------------|--------------|---------|
| 0 | -2.15 | 0.12x | **8x** |
| 5 | -1.61 | 0.20x | 5x |
| 15 | -1.40 | 0.25x | 4x |
| 40 | -1.31 | 0.27x | **3.7x** |

**E1 从 8x 衰减到 3.7x — 这才是重写本签名**
**E3 从 11x 到 10x — 平坦 = 全局分布适应，不是记忆**

**根因**：`entity.py` 用固定 36 音节表生成假名，所有会话共享
- 200 会话后模型学会"这类文本出现 Kave/Lor/Min 拼成的名字"
- **任何**合成名的似然全局抬升 10x，与 lag 无关
- 这是共享词表伪迹的软化版

**修复**（ptt_e3fix.zip）：
1. fresh 会话记录逐会话 PPL（分布适应 vs 记忆的裁决对照）
2. 每会话从 36 音节独立抽 12 个作专属池（名字分布不再同源）

**新判读标准**：
- **记忆量 = 流内 dlogPPL − fresh dlogPPL**（差值才是会话特异的）
- 真记忆必须**随滞后衰减**（平坦曲线一律判为残余分布伪迹）
- 长尾门槛：lag40 的（流内 − fresh）CI 离开零

**伪迹清单更新**（本项目第 5 个，全部内部拦截）：
1. BWT 归零（测量方式错）
2. session 测序（lag0 在 end_session 后测）
3. 共享词表（200 仓库共享伪词表）
4. acc_norm 幻影（arc_easy +5pt 是计分规则伪迹）
5. **音节分布适应**（36 音节共享表 → 全局似然抬升）

**§4 cautionary cases 现有 5 个真实案例可写——这一节会是审稿人记住我们的地方之一**

**00:28** - η 校准完成

| η | hellaswag | piqa | arc_easy | 判断 |
|---|-----------|------|----------|------|
| 3e-3 | -2.3pt | -2.5pt | -0.5pt | ✅ 可用 |
| **1e-2** | **-2.0pt** | **-2.2pt** | +1.3pt | ✅ **选定** |
| 3e-2 | -5.2pt | -4.0pt | -1.9pt | ❌ 过膝 |

**η* = 1e-2 确定**：税负与 E1 的 η=3e-2 几乎重合（hellaswag -2~3pt），比 3e-3 保留更多可塑性

**00:45** - E1 NLL 仪器校验 + 图 2 定案

E1 代码流 persist vs base NLL（124 holdouts）：
| lag | dlogPPL | PPL ratio | 改善 |
|-----|---------|-----------|------|
| 0 | -2.15 | 0.12x | **8x** |
| 5 | -1.61 | 0.20x | 5x |
| 15 | -1.40 | 0.25x | 4x |
| 40 | -1.31 | 0.27x | **3.7x** |

**→ 仪器校验通过：正常衰减（8x→3.7x）**
**→ 图 2 定为双面板**（accuracy + logPPL），H2 主证据换用 NLL 面板

**01:00** - E3v2 正式批次启动（PID 1998237）
- 使用 ptt_e3fix.zip（独立音节池 + fresh PPL）
- η* = 1e-2，五策略 seed 0
- 日志：`results/e3v2/run.log`
- **监控点**：persist 完成后检查 hellaswag 税，偏离 -2pt 超过 2pt 则重校准
- 预计耗时：~50 分钟

**判读标准**：
- 记忆量 = 流内 dlogPPL − fresh dlogPPL
- 必须随滞后衰减
- 长尾门槛：lag40 的（流内 − fresh）CI 离零

**合稿动作启动**：
- E1 全量出图 2/3 终版
- E4 四条 η 曲线出图 4
- LaTeX 工程落地
- §5 除 E3/4B 两格外全部填实数

**04:00** - E3v2 完成，发现第六个伪迹

**E3v2 persist−base 配对**（平坦曲线 = 红牌）：
| lag | dlogPPL | PPL ratio |
|-----|---------|-----------|
| 0 | -2.11 | 0.12x (8x) |
| 5 | -1.93 | 0.15x |
| 15 | -1.94 | 0.14x |
| 40 | -1.94 | 0.14x |

**诊断**：session 行揭示真相
- session lag0 = 19985（仅降 31%），persist lag0 = 3509（降 88%）
- session 清零后 lag5+ 回到 base；persist 多出的 20000→3509 对所有滞后一视同仁
- **这是全局分布适应的指纹**

**第六个伪迹**：12 音节池从 36 里抽，任意两会话平均共享 4 个音节 → 全局音节分布被学走

**04:30** - 解压 ptt_e3fix3.zip（per-session cipher）
- 每会话用字母置换的专属字母表
- 名字字符级分布跨会话相同（学不到可迁移的先验）
- 具体字符串会话间零重叠

**04:35** - E3v3 启动（per-session cipher）
- 213 stream sessions, 30 fresh; 1.2M tokens

**06:23** - E3v3 seed 0 完成，**裁决结果**

**persist−base 配对**：
| lag | dlogPPL | PPL ratio |
|-----|---------|-----------|
| 0 | -1.30 | 0.27x (3.7x) |
| 5 | -1.15 | 0.32x |
| 15 | -1.13 | 0.32x |
| 40 | -1.15 | 0.32x |

**Fresh log_ppl**：
- base: 8.79 → persist: 7.71
- **persist 在从未见过的会话上仍有 2.9x 改善** → 全局分布适应占 83%

**Memory Excess（扣减后真记忆）**：
```
fresh dlogPPL: -1.073 [-1.35, -0.86]
lag  0: excess -0.225 [-0.46, +0.06]  ← CI 含零
lag  5: excess -0.081 [-0.31, +0.22]
lag 15: excess -0.056 [-0.29, +0.23]
lag 40: excess -0.074 [-0.31, +0.22]
```
**所有 lag 的 CI 都含零** — 功效不足以检出

**consistency−random 配对**（placement 跨流复现）：
| lag | dlogPPL | 95% CI |
|-----|---------|--------|
| 0 | -0.14 | [-0.18, -0.10] * |
| 5 | -0.25 | [-0.28, -0.21] * |
| 15 | -0.20 | [-0.24, -0.17] * |
| 40 | -0.21 | [-0.26, -0.18] * |
**全部显著！** ✅

**E3 定稿口径**：
- 短程记忆：功效不足，未检出（CI 含零）
- 长尾：未检出，"not detected at this power"
- **placement 效应：跨流复现**（全局适应在差分里抵消）
- 长尾主张范围限定为代码流（E1，3 seeds，双读数）

**第六个 cautionary case**：prose 流上 83% 的"记忆"是槽位分布适应
- 合成重命名评测在自然文本上的固有问题
- **fresh 会话扣减是必需项，不是可选项**

**06:30** - E3v3 seeds 1/2 启动（PID 2617383）
- 四策略 × 2 seeds = 8 次，~8 小时
- 目的：placement 跨流复现要 3 seeds

**06:00** - 4B 启动（PID 2529715，GPU0）
- 四策略（base/persist/consistency/random），~24 小时
- 显存：16.4 GB ✅

**伪迹清单**（共 6 个，全部内部拦截）：
1. BWT 归零
2. session 测序
3. 共享词表
4. acc_norm 幻影
5. 音节分布适应（36 音节共享表）
6. **槽位分布适应**（prose 流 83% 是全局适应）

---

**22:00** - E1 seed 0 全部完成 + seed 1 分析
- **已完成**：base_s0, persist_s0, session_s0, consistency_s0, random_s0, base_s1, persist_s1
- **random_s0 性能 bug**：跑了 864 分钟（persist 122 分钟），原因是 randperm 在 CPU 上生成
- **关键发现**：
  1. **主结论 seed1 复现**：persist_s1 曲线 0.075→0.024→0.017→0.019，base 0.008，形状一致
  2. **consistency vs random**：lag0 = +0.0093 [+0.0000, +0.0188]，下界触零，§5.6(a) 第一块砖
  3. **random lag40 反超 persist**：+0.0052 [+0.0012, +0.0095]，但 12 次检验 Holm 校正后可能不存活
  4. **arc_easy 效应三次复现**：persist_s1 +6.0, random_s0 +6.4, persist_s0 +4.4 → 升级为"很可能真实"
- **协议层面注意**：random 门不是纯零对照（E[α²]>1 改变写入谱结构），§4.4 需说明
- **general.py 已更新**：同时记录 `__acc` 和 `__acc_norm`（排除 arc_easy 伪迹通道）

**22:05** - 解压 ptt_e1c.zip + 重启实验
- **修复**：random 门置换改为 GPU 端生成，单次从 ~14 小时降到 ~2 小时
- **停掉旧包 session_s1**，启动 `run_e1c_continue.sh`
- **剩余 8 次**：session_s1, consistency_s1, random_s1, base_s2, persist_s2, session_s2, consistency_s2, random_s2
- **预计耗时**：约 16-20 小时（random 修复后 ~2 小时/次）
- **待补**：seed0 的 5 任务终态（persist_s0, consistency_s0）—— 若时间紧，接受混合报告

**17:00** - 收到 §5-§7 骨架 + 附录 A 全量证明
- 文件：`DRAFT_sec5_sec7_appA.md`
- **§5 结构**（9 小节，"结论句 + 图表 + 统计方法"格式）：
  - §5.1 Reset vs Persist（H1 检验）
  - §5.2 Horizon 衰减曲线（H2 检验，跨流复现）
  - §5.3 质量比坍缩（P1 验证，η-invariance）
  - §5.4 膝点/悬崖（**分任务报 dGen，不做跨任务平均**）
  - §5.5 Session 操作点（87% 收益，零风险）
  - §5.6 Placement（**(a)/(b) 双分支**，等三 seed 配对结果定）
  - §5.7 投影（plasticity-retention 前沿）
  - §5.8 ARC-Easy 意外观察（待 5 任务 × 3 seeds 确认）
  - §5.9 开销表
- **§6 局限**：
  - ρ 坍缩只在工程化各向同性流上验证，自然流未测（主动交代）
  - 门控只测参数统计启发式，learned gates 不在范围内
- **§7 结论**：三句话 + 收尾句
- **附录 A**：
  - A1/A2 明写为 benchmark 设计属性（每会话独立词表制造各向同性）
  - P1 加 remark：准确率只需是 SNR 单调函数，坍缩检验单调性本身
  - 留 App. B 钩子：跨会话 Δ 余弦分布（堵"假设未验证"）
- **至此正文六节全部有稿**：§1-§2、§3-§4、§5-§7 + 附录 A

**待 E1 完成后**：
1. 填 §5 全部数字
2. 定 §5.6 分支（consistency vs random 配对结果）
3. 出图 2/3/4/6 终版
4. 合并完整 LaTeX（ICML 模板）

**插空任务**：
- E3 三次运行（§5.2 跨流复现）
- 0.6B@5e-2（§5.4 膝点图右侧一点）

---

### 2026-09-04

**09:51** - 论文仓库初始化
- 克隆 Overleaf 模板到 `/data/ziming_workspace/kaiyi/ICLR/paper/`
- 模板：ICLR 2027 Conference
- 文件：`iclr2027_conference.tex`, `iclr2027_conference.sty`, `math_commands.tex`, etc.

**16:47** - Week 5b 诊断全部完成
- persist_fresh.json（诊断 1）
- persist_2e-2.json（E4）
- persist_4e-2.json（E4）

**Fresh 诊断结果（修正口径）**：
- Fresh acc = **0.013 [0.004, 0.046]**（Wilson 95% CI）
- Base = 0.010
- 风格迁移 excess = **0.003 [-0.006, 0.036]**（CI 包含 0，与零无显著差异）

**正确解读（三句话，论文口径）**：
1. 风格迁移贡献很小（0.003，CI 包含 0）
2. Session 拿到记忆收益的 **87%**（0.062/0.071）
3. 剩余 13% 差距在置信区间内，**无法与零区分**——不宣称 persist 有跨仓库记忆优势，也不宣称完全没有

**⚠️ 旧假设被否定**：原假设"persist 比 session 高的 0.016 来自风格迁移"被 fresh 诊断否定（风格迁移只有 0.003）。但 0.016 本身在噪声边缘（CI ±0.011-0.013）。

**E4 坍缩数据（η 不变性检验）**：

| η | lag0 | lag5 | lag15 | lag40 | dGen | lag5/lag0 归一化 |
|---|------|------|-------|-------|------|------------------|
| 2e-2 | 0.069 | 0.026 | 0.019 | 0.013 | -0.004 | 0.27 |
| 3e-2 | 0.084 | 0.028 | 0.020 | 0.011 | -0.008 | 0.24 |
| 4e-2 | 0.091 | 0.027 | 0.022 | 0.015 | -0.069 | 0.21 |

**E4 正确读法**：
- 归一化衰减（超额/lag0超额）近乎重合 → **η 不变性在噪声内成立**
- 大 η 相对衰减略快 → 正是 P1 预告的饱和项方向
- **悬崖定位**：dGen 从 3e-2 的 -0.008 跳到 4e-2 的 **-0.069**
- **膝点在 3e-2 与 4e-2 之间**：边际收益 0.007 换边际损失 0.06（这是 recipe 的一部分）

**10:00** - 收到论文 §3-§4 初稿 + 图 4 修正
- `DRAFT_sec3_sec4.md`：§3-§4 英文初稿（LaTeX-ready）
- 解压 ptt_e3b.zip（图 4 横轴修正）

**§3-§4 初稿要点**：
- **P1（干扰衰减律）**：坍缩变量 ρ = m_k²/Σm_j²，两个可证伪预测：
  1. 质量比坍缩：不同会话/流的曲线按 ρ 重合
  2. η 不变性：等质量会话下 ρ=1/L，η 消掉，不同 η 的 lag 曲线应直接重合
  - 若大 η 衰减更快 → 指示线性模型外的饱和/漂移项（预先写成诊断而非弱点）
- **P2（consistency 门）**：理论化负结果——门只放行跨文档重复方向，无法保护单次内容，且把写入集中到流的系统漂移方向 → 解释三次运行 dGen 均为负
- **P4（session）**：定位为"持久—风险权衡的 L=0 端点"，避免伪问题
- **§4 协议**：共享词表坑作为 cautionary case（lag40 虚高 2×），38.1%→1.7% 污染牌

**图 4 修正**：
- 横轴：ρ = m_k²/Σm_j²（log₁₀ρ 分桶聚合）
- E4 意义变化：若 2e-2/4e-2 与 3e-2 直接重合 → η 不变性成立（P1 通过）；若 6e-2 更快 → 量化偏差项

---

## 实验结果

### Week 1 结果

| policy | eta | xfile_acc | xfile>=2 | local_acc | doc_ppl | |G_slow| |
|--------|-----|-----------|----------|-----------|---------|---------|
| base   | -   | 67.8%     | 67.8%    | 78.0%     | 2.97    | 0.000   |
| reset  | 3e-4| 67.8%     | 67.8%    | 78.0%     | 2.97    | 0.000   |
| reset  | 1e-3| 67.8%     | 67.8%    | 78.2%     | 2.97    | 0.000   |
| reset  | 3e-3| 67.7%     | 67.7%    | 78.1%     | 2.97    | 0.000   |
| persist| 3e-4| 68.0%     | 68.0%    | 77.8%     | 2.88    | 0.017   |
| persist| 1e-3| 68.2%     | 68.2%    | 77.8%     | 2.84    | 0.046   |
| persist| 3e-3| 68.2%     | 68.2%    | 77.6%     | 2.82    | 0.115   |

**判据**：xfile>=2 列 persist 比 reset 高 ≥3 个点 → **未通过**（仅高 0.4 个点）

**结果分析**：
1. persist 确实比 reset 有提升，但仅 **+0.4 个点**（68.2% vs 67.8%）
2. docPPL 方面 persist 有显著改善（2.82 vs 2.97，降低 5%）
3. local_acc 基本持平，说明 persist 没有损害文档内补全
4. reset 与 base 完全相同，说明 TTT 在文档内写入后重置没有帮助

**可能原因**：
- xfile 掩码定义过于严格（要求标识符在早期文件定义且当前文件未定义）
- 12 个仓库可能不够多样化
- η 范围可能需要扩大

**下一步建议**：
- 检查 xfile 掩码的实际分布
- 考虑使用更大的 η（如 1e-2）
- 或扩展到 S-Domain 流看是否有更大差异

---

### Week 1b 诊断与修复

**诊断（来自结果分析）**：

1. **xfile 掩码问题**：标记了所有出现而非文件内首次出现 → 后续出现靠 induction 复制，不需要跨文档记忆
2. **chunk=1024 太大**：大多数 Python 文件不到 1024 token → 一个文件一个 chunk，写完就重置，等于没写
3. **clip=η 饱和**：需要把 η 和 clip 一起往上推到 1e-2、3e-2
4. **预训练污染**：这 12 个仓库几乎肯定在 Qwen3 预训练数据里（docPPL=2.97 极低）

**修复（ptt_week1b.zip）**：

- 标识符混淆：每个仓库内把所有自定义名字一致地重命名为随机串
- 掩码拆分：`xfile`（文件内首次出现）、`xrep`（后续重复）、`local`（同文件定义）
- chunk=256
- η ∈ {1e-3, 3e-3, 1e-2, 3e-2}

**预期**：

- 混淆后 base 的 xfile 掉到接近随机（几个百分点）
- persist 应明显高于 reset

**实验状态**：✅ 已完成

### Week 1b 结果

| policy  | eta   | xfile | xrep  | local | docPPL | |Gslow| |
|---------|-------|-------|-------|-------|--------|---------|
| base(obf)| -    | 1.7%  | 59.7% | 58.9% | 6.44   | 0.000   |
| base(原) | -    | 38.1% | 75.6% | 76.7% | 3.00   | 0.000   |
| reset   | 1e-3  | 1.8%  | 60.3% | 59.4% | 6.42   | 0.000   |
| reset   | 3e-3  | 1.8%  | 60.6% | 59.6% | 6.47   | 0.000   |
| reset   | 1e-2  | 1.7%  | 59.8% | 57.9% | 7.06   | 0.000   |
| reset   | 3e-2  | 1.0%  | 41.3% | 40.0% | 31.5   | 0.000   |
| persist | 1e-3  | 3.4%  | 62.7% | 61.0% | 5.02   | 0.142   |
| persist | 3e-3  | 4.4%  | 63.7% | 61.3% | 4.62   | 0.340   |
| persist | 1e-2  | 7.0%  | 64.8% | 61.8% | 4.11   | 0.945   |
| persist | 3e-2  | 8.1%  | 61.5% | 58.6% | 4.92   | 4.026   |

**判据**：xfile 列 persist 比 reset 高 ≥3 个点 → **✅ 通过**

**关键发现**：

1. **预训练污染确认**：
   - 混淆前 base xfile=38.1%（week1的67.8%是因为掩码定义不同）
   - 混淆后 base xfile=1.7%（接近随机）
   - 说明这12个仓库确实在Qwen3预训练数据中

2. **persist vs reset 差距**：
   - 最佳 persist (η=3e-2): xfile=8.1%
   - 最佳 reset (η=1e-3): xfile=1.8%
   - **差距 = +6.3 个点**，显著超过3点阈值

3. **η 趋势**：
   - persist 随 η 增大，xfile 从 3.4% → 8.1%（单调递增）
   - reset 随 η 增大，xfile 从 1.8% → 1.0%（过大反而有害）

4. **PPL 意外改善**：
   - persist η=1e-2 的 docPPL=4.11 优于 base(obf)=6.44
   - 说明 TTT 写入不仅帮助 xfile，还改善了整体语言建模

5. **局限性**：
   - reset η=3e-2 严重崩溃（PPL=31.5），说明单文档内大 η 有害
   - persist 在 η=3e-2 时 |Gslow|=4.0，可能已接近饱和

**结论**：persist 策略有效验证，可进入 Week 2 完整策略比较

---

### Week 2 结果

**实验配置**：
- 7 策略：base, reset, persist, decay, fisher, consistency, surprise, random
- η ∈ {1e-2, 3e-2} + persist η=1e-1（崩溃点测试）
- 50 个仓库（2025-06 后创建，降低预训练污染）
- 21066 个 xfile 目标

| policy      | eta   | xfile | xfilePPL | xrep  | local | docPPL |  dGen  | |Gslow| |
|-------------|-------|-------|----------|-------|-------|--------|--------|---------|
| base        | -     | 0.9%  | 4843.52  | 65.2% | 59.3% |  6.29  | +0.000 |  0.000  |
| reset       | 1e-2  | 1.0%  | 4323.15  | 64.9% | 57.8% |  6.88  | +0.000 |  0.000  |
| reset       | 3e-2  | 0.8%  | 23139.56 | 46.3% | 35.8% | 41.74  | +0.000 |  0.000  |
| decay       | 1e-2  | 1.8%  | 1780.49  | 67.1% | 59.0% |  6.28  | +0.011 |  0.132  |
| decay       | 3e-2  | 2.4%  | 1491.25  | 66.4% | 57.3% |  7.34  | -0.043 |  0.341  |
| random      | 1e-2  | 3.0%  |  887.81  | 69.8% | 62.0% |  5.08  | +0.012 |  0.550  |
| random      | 3e-2  | 4.8%  |  602.87  | 70.9% | 62.5% |  4.51  | +0.006 |  1.374  |
| consistency | 1e-2  | 3.9%  |  690.47  | 70.8% | 62.5% |  4.73  | +0.003 |  0.904  |
| consistency | 3e-2  | 6.3%  |  466.84  | 71.9% | 63.2% |  4.02  | +0.004 |  2.104  |
| surprise    | 1e-2  | 4.6%  |  591.05  | 71.2% | 62.7% |  4.51  | +0.004 |  1.076  |
| surprise    | 3e-2  | 7.6%  |  386.26  | 72.2% | 63.0% |  3.87  | +0.014 |  2.441  |
| persist     | 1e-2  | 6.7%  |  439.76  | 71.8% | 62.9% |  4.08  | -0.003 |  1.738  |
| persist     | 3e-2  |**10.1%**| 286.96 | 72.8% | 62.9% |  3.72  | +0.003 |  3.829  |
| fisher      | 1e-2  | 6.7%  |  437.41  | 71.9% | 62.9% |  4.06  | +0.001 |  1.726  |
| fisher      | 3e-2  | 9.9%  |  291.49  | 72.8% | 62.9% |  3.71  | +0.002 |  3.828  |
| persist     | 1e-1  | 3.1%  | 1093.36  |  8.9% |  2.9% |153.22  | -0.253 | 10.047  |

**策略排名（按 xfile 准确率）**：

1. **persist** η=3e-2: **10.1%** (最佳)
2. **fisher** η=3e-2: 9.9%
3. **surprise** η=3e-2: 7.6%
4. persist η=1e-2: 6.7%
5. fisher η=1e-2: 6.7%
6. consistency η=3e-2: 6.3%
7. random η=3e-2: 4.8%
8. surprise η=1e-2: 4.6%
9. consistency η=1e-2: 3.9%
10. random η=1e-2: 3.0%
11. decay η=3e-2: 2.4%
12. decay η=1e-2: 1.8%
13. reset η=1e-2: 1.0%
14. base: 0.9%
15. reset η=3e-2: 0.8%

**关键发现**：

1. **persist 和 fisher 效果最好且几乎持平**：
   - persist η=3e-2: xfile=10.1%, xfilePPL=286.96
   - fisher η=3e-2: xfile=9.9%, xfilePPL=291.49
   - 两者差距仅 0.2 个点，说明 Fisher 正则化没有显著额外收益

2. **surprise 次之**：
   - surprise η=3e-2: xfile=7.6%
   - 惊奇度门控有效但不如持续写入

3. **consistency 和 random 中等**：
   - consistency 强制低一致性时写入，random 随机写入
   - 效果低于 persist/fisher/surprise

4. **decay 效果较差**：
   - 指数衰减（γ=0.9）导致旧知识被过度遗忘
   - 且 η=3e-2 时 dGen=-0.043，有轻微灾难性遗忘

5. **reset 与 base 几乎相同**：
   - 每文档重置等于没有跨文档记忆
   - reset η=3e-2 严重崩溃（docPPL=41.74）

6. **persist η=1e-1 崩溃确认**：
   - xfile: 3.1%（从 10.1% 大幅下降）
   - xrep: 8.9%（从 72.8% 崩溃）
   - docPPL: 153.22（严重崩溃）
   - dGen: -0.253（严重灾难性遗忘）
   - |Gslow|: 10.047（过度学习）

7. **dGen（通用能力变化）**：
   - 大多数策略 dGen ≈ 0（无显著影响）
   - surprise η=3e-2 有最佳 dGen=+0.014
   - persist η=1e-1 有最差 dGen=-0.253

8. **BWT_x 全为 0**：
   - backward transfer 未能检测到，可能需要不同的数据流设计

**初步结论**：
- persist 在 xfile 上表现最佳
- fisher 效果相当但增加了计算开销
- 崩溃点在 η ≈ 1e-1，实际使用应控制在 η ≤ 3e-2

**⚠️ Week 2 局限性（需 Week 3 修正）**：

1. **排名几乎完全是 ‖G_slow‖ 的函数** — xfile 从 decay(0.34)→random(1.37)→consistency(2.10)→surprise(2.44)→persist(3.83) 单调随写入总量上升。目前所有策略只是同一条"有效学习率曲线"上的不同点，门控唯一做的事就是少写。

2. **fisher ≈ persist 是实现瑕疵** — 用 max 归一化 grad²，而 grad² 的 max 是离群值，导致 α 几乎处处 ≈1，fisher 门形同虚设。

3. **BWT_x 全零是测量方式错了** — 前 20 个文档在流早期本来就没学到什么，流末重测当然没变化。

4. **流太温和** — 50 个仓库、纯 Python、约几 M token，persist 到 3e-2 都没漂（dGen≈0），干扰还没发生。

**真信号**：consistency > random（3.9 vs 3.0、6.3 vs 4.8），同样的 α 直方图、不同的摆放位置，说明**写入位置确实有信息**。

---

### Week 3 核心问题

Week 3 要回答两个更能撑起论文的问题：

**1. 等预算下，写入位置有没有信息？**
- `--alpha_norm` 把门控 α 归一化到均值 1（上限 4 防单点爆写）
- consistency/fisher/random 与 persist 花完全相同的写入质量
- 如果归一化后 consistency ≥ persist > random，则"placement matters"
- 如果大家都 ≈ persist，则走"don't reset until the cliff"

**2. 长流上 persist 到底会不会遗忘？**
- 每个仓库留出最后一个标识符最多的文件
- 仓库结束时测 acc_then，全流结束后测 acc_end
- retention = acc_end - acc_then
- retention_first_third 单看前 1/3 仓库（被后面 130+ 个仓库冲刷最久）
- 如果 persist 的 ret1/3 明显为负而某个门控策略不掉，稳定性故事成立

---

### Week 3 结果

**实验配置**：
- 8 次运行：base, persist, decay(γ=0.98), consistency_norm, fisher_norm, random_norm, surprise, persist(η=6e-2)
- 200 个仓库（2025-06 后创建）
- 等预算比较：`--alpha_norm` 使门控策略与 persist 花同样的写入质量

| policy      | eta  | norm  | then  | end   | reten  | ret1/3 | dGen   |
|-------------|------|-------|-------|-------|--------|--------|--------|
| base        | 3e-2 | False | 0.007 | 0.007 | +0.000 | +0.000 | +0.000 |
| persist     | 3e-2 | False | 0.101 | 0.017 | -0.085 | -0.074 | -0.004 |
| persist     | 6e-2 | False | 0.115 | 0.013 | -0.102 | -0.085 | -0.099 |
| decay       | 3e-2 | False | 0.056 | 0.015 | -0.040 | -0.044 | -0.009 |
| surprise    | 3e-2 | False | 0.079 | 0.016 | -0.063 | -0.068 | +0.009 |
| fisher      | 3e-2 | True  | 0.040 | 0.015 | -0.025 | -0.027 | -0.000 |
| consistency | 3e-2 | True  | 0.105 | 0.020 | -0.085 | -0.090 | -0.035 |
| random      | 3e-2 | True  | 0.104 | 0.017 | -0.087 | -0.082 | -0.003 |

**指标说明**：
- `then`: 仓库结束时 holdout 文件的 xfile 准确率
- `end`: 全流结束后重测 holdout 的准确率
- `reten`: end - then，负值表示遗忘
- `ret1/3`: 前 1/3 仓库的 retention（被后面 130+ 仓库冲刷最久）
- `dGen`: 通用能力变化（lm-eval 前后差）

**关键发现**：

1. **等预算下，placement 没有显著差异**：
   - consistency_norm: then=0.105, reten=-0.085
   - random_norm: then=0.104, reten=-0.087
   - persist: then=0.101, reten=-0.085
   - 三者几乎相同，说明在等写入量下，"写在哪里"并不比"随机写"更好
   - **⚠️ consistency 的 dGen（−0.035）比 random（−0.003）还差**：把写入集中到"方向一致"的坐标上，等于放大了代码域整体漂移的方向

2. **fisher 门修复后过于严格**：
   - then=0.040（远低于 persist 的 0.101）
   - 中位数归一化导致门控太紧，筛掉了太多有价值的写入
   - reten=-0.025 看似稳定，但代价是学习能力大幅下降

3. **persist 在长流上确实遗忘**：
   - η=3e-2: reten=-0.085，ret1/3=-0.074
   - η=6e-2: reten=-0.102，ret1/3=-0.085，dGen=-0.099（灾难性）
   - 早期仓库的知识被后续 130+ 仓库的写入冲刷

4. **⚠️ 不存在"最平衡的策略"（之前分析有误）**：
   - 看 `end` 列：所有策略流末的 holdout 准确率都在 0.013–0.020，base 是 0.007
   - **200 个仓库之后，谁都没记住早期仓库的东西**，差别只剩 1 个百分点
   - `reten = end − then` 里 end 几乎是常数
   - 所以 reten 的排名就是 then 的倒序：fisher "遗忘最少"和 surprise "最平衡"都只是因为它们**学得少，不是保护得好**

5. **悬崖位置确认**：
   - η=3e-2: dGen=-0.004（可接受）
   - η=6e-2: dGen=-0.099（灾难性遗忘）
   - 悬崖在 3e-2 到 6e-2 之间

---

### Week 3 半衰期分析（horizon.py）

> ⚠️ **SUPERSEDED**：以下数据受混淆器 bug 污染（所有仓库共享伪词表），定量结论不可信。见 Week 5 修复。

| policy | then | end@0-5 | end@5-15 | end@15-40 | end@40-80 | end@80-140 | end@140+ | half-life |
|--------|------|---------|----------|-----------|-----------|------------|----------|-----------|
| base@3e-02 | 0.007 | 0.000 | 0.000 | 0.012 | 0.002 | 0.009 | 0.007 | ~5 |
| persist@3e-02 | 0.101 | 0.044 | 0.000 | 0.018 | 0.009 | 0.023 | 0.012 | **~5** |
| persist@6e-02 | 0.115 | 0.067 | 0.000 | 0.015 | 0.014 | 0.013 | 0.009 | ~15 |
| decay@3e-02 | 0.056 | 0.022 | 0.000 | 0.009 | 0.019 | 0.019 | 0.012 | ~5 |
| surprise@3e-02 | 0.079 | 0.044 | 0.000 | 0.015 | 0.014 | 0.023 | 0.007 | ~15 |
| fisher_norm@3e-02 | 0.040 | 0.044 | 0.000 | 0.012 | 0.014 | 0.023 | 0.004 | ~15 |
| consistency_norm@3e-02 | 0.105 | 0.111 | 0.052 | 0.012 | 0.012 | 0.026 | 0.011 | ~15 |
| random_norm@3e-02 | 0.104 | 0.089 | 0.000 | 0.009 | 0.014 | 0.023 | 0.012 | ~15 |

~~**关键发现**~~：
- ~~persist@3e-02 的半衰期只有 ~5 个仓库~~
- ~~所有策略在 15 个仓库后基本都回到基线~~
- ~~记忆是短时的，不是长期的~~

**结论（修正后）**：

Week 3 回答了两个核心问题：

1. **等预算下写入位置有信息吗？** → **没有**。consistency ≈ random ≈ persist，门控策略的优势完全来自"少写"而非"写得更聪明"。这是一个带随机对照的干净负结果。

2. **persist 会遗忘吗？** → **会，而且很快**。半衰期只有 ~5 个仓库，15 个仓库后完全归零。

**论文可行主线**："How far should test-time training persist?"

三条可靠发现：
- 跨文档持久确实带来收益（then 0.10 vs reset 0.01，10 倍），但这份记忆是**短时的**
- 存在悬崖（3e-2 → 6e-2），且悬崖前的通用能力不受影响
- 参数级门控（一致性/Fisher/惊奇/衰减）在等预算下与随机无异

**Week 4 候选**（把负结果变成有 recipe 的论文）：
1. **session 策略**：仓库内持久、仓库边界重置 → 如果拿到全部 then 收益（≈0.10）且零漂移风险，结论就是"重置的正确粒度是会话而不是文档"
2. **激活子空间投影（GPM 式）**：把每次写入 δ 投到过去会话激活子空间的正交补上 → 唯一还有理由期待"写在哪里"起作用的机制

---

### Week 4 结果（固定滞后协议）

> ⚠️ **SUPERSEDED**：以下数据受混淆器 bug 污染（所有仓库共享伪词表）。persist 的"长尾"实为词表先验，非仓库特异记忆。见 Week 5 修复。

| policy | lag0 | lag5 | lag15 | lag40 | end | dGen |
|--------|------|------|-------|-------|-----|------|
| persist | 0.110±0.013 | 0.033±0.008 | 0.022±0.006 | 0.020±0.006 | 0.019 | -0.012 |
| consistency_norm (s0) | 0.109±0.013 | 0.040±0.008 | 0.021±0.006 | 0.017±0.006 | 0.017 | -0.032 |
| consistency_norm (s1) | 0.100±0.013 | 0.032±0.007 | 0.019±0.006 | 0.015±0.006 | 0.016 | -0.030 |
| random_norm (s0) | 0.105±0.013 | 0.030±0.007 | 0.019±0.006 | 0.020±0.006 | 0.015 | -0.011 |
| random_norm (s1) | 0.075±0.011 | 0.020±0.006 | 0.019±0.006 | 0.014±0.005 | 0.013 | -0.089 |
| persist_p64 | 0.049±0.009 | 0.032±0.007 | 0.025±0.007 | 0.025±0.007 | 0.018 | -0.006 |
| persist_p256 | 0.013±0.005 | 0.013±0.005 | 0.013±0.005 | 0.015±0.006 | 0.019 | +0.011 |
| session | 0.071±0.011 | 0.007±0.004 | 0.008±0.004 | 0.007±0.004 | 0.007 | **+0.000** |

~~**关键发现**~~：（已作废，待 Week 5 数据）

1. ~~placement 问题：有微弱信号但 CI 重叠~~
2. ~~GPM 投影的权衡~~
3. ~~random seed1 的 dGen = -0.089 说明乱写有实害~~

---

## 论文进度评估

**总体完成度**：离可提交论文约 40%；离有竞争力的 ICML 投稿约 30-35%

| 部分 | 完成度 | 说明 |
|------|--------|------|
| 基础设施 | ~90% | 流构造、混淆、固定滞后协议、泄漏测试、7策略+投影，benchmark 可开源 |
| 核心实证结论 | ~60% | 主要发现已定型，但 session 需重跑、全部主数在 0.6B 单 seed |
| 规模验证 | 0% | 1.7B 主表、3 seeds，约 2-3 天 GPU |
| 第二种流 | 0% | 非代码域，证明结论不是代码特有，约 3-4 天 |
| 写作 | 0% | 约 1 周 |

**论文实际拥有的四条结论**（都有对照和置信区间）：

1. **跨文档持久收益**：lag0 = 0.110 vs reset ≈ base 0.007，15 倍
2. **记忆半衰期**：约 5 个仓库（0.110→0.033），但有长尾（lag40 = 0.020，约 3 倍 base）
3. **悬崖刻画**：η 3e-2 → 6e-2 之间通用能力从无损变灾难
4. **门控负结果**：参数统计门控在等预算下 ≈ 随机摆放；投影是权衡旋钮而非免费午餐

**关键路径**：
1. ⚠️ ~~session 重跑~~ — 数据已作废（混淆器 bug）
2. ✅ Week 5 裁决性重跑（5 策略，修复混淆器）— **进行中**
3. 根据 Week 5 结果定 1.7B 主表策略清单（2-3 天）
4. 非代码第二流（3-4 天）
5. 论文写作（1 周）

**论文定位**：待 Week 5 结果裁决
- 若 persist 长尾消失 → session 成为 recipe，论文强度回升
- 若 persist 仍有长尾 → characterization + benchmark
- 若中间态 → 报告混杂因素作为评测陷阱教训

**已发现的三个测量问题**（全部内部抓住，未流入论文）：
1. BWT 全零：测量方式错误
2. session 测量顺序：lag0 在 end_session 之后测
3. 词表泄漏：所有仓库共享伪词表

---

## 重要文件位置

- 代码：`/data/ziming_workspace/kaiyi/ICLR/ptt/`
- Week1 结果：`/data/ziming_workspace/kaiyi/ICLR/ptt/results/week1/`
- Week1b 结果：`/data/ziming_workspace/kaiyi/ICLR/ptt/results/week1b/`
- Week2 结果：`/data/ziming_workspace/kaiyi/ICLR/ptt/ptt/results/week2/`
- Week3 结果：`/data/ziming_workspace/kaiyi/ICLR/ptt/ptt/results/week3/`
- Week4 结果：`/data/ziming_workspace/kaiyi/ICLR/ptt/ptt/results/week4/`（待生成）
- 大纲：`/data/ziming_workspace/kaiyi/ICLR/TTT_PAPER_OUTLINE_AND_CITATIONS.md`

---

## 当前运行状态（2026-09-07 09:10 更新）

### E3v3 实体流 ✅ 已完成
**日志**：`results/e3v3/seeds_run.log`

| Seed | base | persist | consistency | random |
|------|------|---------|-------------|--------|
| 0 | ✅ | ✅ | ✅ | ✅ |
| 1 | ✅ | ✅ | ✅ | ✅ |
| 2 | ✅ | ✅ | ✅ | ✅ |

### E3 Placement 机制验证（关键发现）

| 指标 | E3 实体流 | E1 代码流 |
|------|-----------|-----------|
| 流内 c-r | -0.17~-0.22 (全 lag 恒定) | lag0/5 显著, lag15+ 归零 |
| Fresh c-r | **-0.17** [-0.22, -0.12] | ≈0 [−0.37, +0.54] |
| 机制 | **纯适应型** | **纯记忆型** |

**解释**：同一规则，两种载体，两种收益
- 代码流：一致性门把当前仓库的标识符摆得更好（短程记忆效应）
- 实体流：一致性门把整条流共享的槽位统计写得更好（全局适应效应）

### 4B 规模实验 ✅ 已完成（2026-09-07 19:52）
**日志**：`results/e2_4B/run.log`

| 运行 | 完成时间 |
|------|----------|
| base | 07:40 |
| persist | 11:33 |
| consistency | 15:32 |
| random | 19:52 |

#### 4B 结果

**Lag Accuracy:**
| Policy | lag0 | lag5 | lag15 | lag40 |
|--------|------|------|-------|-------|
| base | 0.014 | 0.014 | 0.014 | 0.014 |
| persist | 0.091 (6.6x) | 0.034 | 0.026 | 0.018 |
| consistency | **0.108 (7.9x)** | 0.051 | 0.032 | 0.015 |
| random | 0.092 (6.7x) | 0.034 | 0.026 | 0.014 |

**Placement Effect (consistency - random):**
| Lag | Diff | 95% CI |
|-----|------|--------|
| 0 | +1.6pt | [+0.6, +2.7] ✓ |
| 5 | +1.7pt | [+0.8, +3.0] ✓ |
| 15 | +0.6pt | [0.0, +1.2] |
| 40 | +0.2pt | [-0.4, +0.8] |

**Hellaswag 退化:**
| Policy | dHS |
|--------|-----|
| persist | -4.0pt |
| consistency | -2.7pt |
| random | -5.3pt |

**4B 关键发现:**
1. **Placement 跨规模复现** ✓：lag0/5 显著，lag15+ 归零（与 1.7B 模式一致）
2. **Consistency 税更低**：-2.7pt vs random -5.3pt（省 2.6pt）
3. **4B 税更重**：persist -4.0pt vs 1.7B 约 -2pt（规模越大税越重）

---

## 实验结论定型（§5 五句话）

1. **跨会话持久收益**：带来 7.5 倍的会话内召回（E1）；每文档重置 ≈ 冻结。

2. **记忆半衰期**：会话特异记忆半衰期 <5 个会话，~15 个会话后不可检出（E1）；lag40 的残留与 fresh 迁移同量级，归为流级适应；实体流上会话记忆在任何滞后都不可检出，似然增益 83% 以上是槽位适应——**fresh 对照必需**。

3. **Session 粒度重置**：60% 的会话内收益、结构性零税、零悬崖暴露；persist 多出的 40% 伴随 hellaswag/piqa 各 −2~3 点的真实税（两种计分一致）和 acc_norm 上 +5 点的幻影增益。

4. **Placement 效应双机制**：等预算一致性门优于随机摆放，两条流均显著，**跨规模复现（4B 已验证）**：
   - 代码流：短程记忆效应（lag0/5 显著，fresh 上为零）
   - 实体流：适应质量效应（全 lag 恒定 ≈ fresh 差）
   - 均不延长记忆视界
   - **Consistency 税更低**：4B 上 -2.7pt vs random -5.3pt

5. **悬崖**：η 3e-2→4e-2 之间；**规模越大税越重**（4B persist -4.0pt vs 1.7B -2pt）。

---

### 待收数据
- [x] 4B 四次 ✅ 已完成
- [ ] 两个 fresh-PPL 补测（1.7B base --fresh_only / persist with fresh PPL）

---

## 论文 v0.9 整合完成（2026-09-09）

**已推送到 Overleaf**: https://git.overleaf.com/6a9acbd90977ca61eff27960

### 文件结构
```
/data/ziming_workspace/kaiyi/ICLR/paper/
├── main.tex          # 论文正文（ICLR 2027 模板）
├── numbers.tex       # 107 个自动生成的宏
├── table3.tex        # 主表
├── CROSSCHECK.md     # 数字→源文件对照表
├── figlib.py         # 图表渲染工具
├── figs/
│   ├── fig2_horizon_E1.pdf
│   ├── fig3_scale.pdf
│   ├── fig4_collapse.pdf
│   ├── fig5_tax.pdf
│   ├── fig6_placement_E1.pdf
│   └── fig7_cautionary.pdf
└── iclr2027_conference.* # ICLR 模板文件
```

### 待核对项（用户指定）✅ 已完成
1. [x] 38.1% → 1.7% 污染数字 ✅ 核对通过
2. [x] 悬崖位置 ✅ 已修正为 "3 and 4×10⁻²"（dGen +0.9→-6.9pt）
3. [x] 吞吐 0.4× ✅ 1.7B 0.43×, 4B 0.42×
4. [x] 单 seed 标注 ✅ 论文已正确标注
5. [x] H2 措辞 ✅ 已添加 rebuttal 堵塞句

### v1.0 更新（2026-09-09）
- [x] 悬崖修正：§5.4 "collapses between 3 and 4×10⁻²"
- [x] H2 段落：添加 "statistically indistinguishable" 句
- [x] 附录 F：添加 6e-2 pre-fix 说明
- [x] §2 引用：全部替换为 natbib \citep/\citet
- [x] references.bib：46 条文献（标 VERIFY 的需确认 arXiv ID）
- [x] 推送到 Overleaf

### 投稿前还缺
- [x] `.bib` 文件 ✅ 已添加
- [ ] 附录 F 额外策略表
- [ ] 投稿前新颖性复扫（本周）
- [ ] VERIFY 标记的 arXiv ID 核实

### 补丁状态
- [x] `week3_repo.py` 已更新：添加 per-session fresh PPL 记录
- [x] `memory_excess.py` 已就绪：计算真实记忆 = stream dlogPPL − fresh dlogPPL
