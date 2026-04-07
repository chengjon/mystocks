# Planning Docs Review

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现、验证结果与主线文档使用。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


**Date:** 2026-04-06  
**Scope:**
- `.planning/phases/01-python-lint-baseline/01-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/ROADMAP-REVIEW-2026-04-06.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`

## Overall

这组文档已经比上一版更接近可执行状态，但当前最大问题不是“内容不够多”，而是“修订后的 `ROADMAP` 没有同步回灌到 `REQUIREMENTS`、`STATE` 和历史评审文档”。结果是：主路线图更新了，配套控制文件还停留在旧口径，后续 planner / executor 很容易拿到互相冲突的输入。

## Findings

### 1. [High] `REQUIREMENTS.md` 仍是旧版口径，已经不再匹配修订后的 `ROADMAP.md`

`ROADMAP.md` 已明确完成多项口径修正：

- Phase 1 只覆盖 `LINT-01..03`，前端大小写目录合并移到 Phase 3：`.planning/ROADMAP.md:41-43`, `.planning/ROADMAP.md:140`
- `src/database_optimization/` 的归宿改为 `src/data_access/`：`.planning/ROADMAP.md:21`, `.planning/ROADMAP.md:105-106`
- Frontend entry 改为先验证真相源，暂不写死 `main.js`：`.planning/ROADMAP.md:23`, `.planning/ROADMAP.md:142-149`, `.planning/ROADMAP.md:175`
- Adapter layer 结论改成“full deletion, no Protocol conversion”：`.planning/ROADMAP.md:24`, `.planning/ROADMAP.md:47`, `.planning/phases/01-python-lint-baseline/01-CONTEXT.md:17`

但 `REQUIREMENTS.md` 仍保留旧要求：

- `LINT-01` 仍写“deleted or converted to Protocol stubs”：`.planning/REQUIREMENTS.md:10`
- `LINT-04` 仍放在 Lint Baseline 段落且 traceability 仍映射到 Phase 1：`.planning/REQUIREMENTS.md:13`, `.planning/REQUIREMENTS.md:59`
- `DEAD-05` 仍写 merge into `src/database/`：`.planning/REQUIREMENTS.md:21`
- `STRU-03` 仍写“exactly one entry point (`main.js`)”：`.planning/REQUIREMENTS.md:28`

这不是文字小漂移，而是 phase boundary、canonical target、requirement semantics 都已经分叉。由于 Phase 1 context 还把 `REQUIREMENTS.md` 列为下游 agent 的 canonical ref，冲突会直接污染后续 planning input：`.planning/phases/01-python-lint-baseline/01-CONTEXT.md:55-60`

**建议：** 先修 `REQUIREMENTS.md`，再继续 phase 级计划。否则 traceability 表和 “100% covered” 都不可信。

### 2. [High] Phase 1 的 `<50` ruff 目标缺乏一致证据支持，当前属于口径冲突

多份文档把 Phase 1 目标写成“从 ~1,456 降到 <50”：

- `.planning/ROADMAP.md:46`
- `.planning/REQUIREMENTS.md:11`
- `.planning/phases/01-python-lint-baseline/01-CONTEXT.md:9`, `.planning/phases/01-python-lint-baseline/01-CONTEXT.md:30`
- `.planning/PROJECT.md:28`
- `.planning/research/ARCHITECTURE.md:14`

但它们引用的基础证据并不支持这个门槛：

- duplicate adapters 只被明确表述为消掉 **500+** F821，而不是 1000+：`.planning/codebase/CONCERNS.md:12`, `.planning/codebase/ARCHITECTURE.md:50`
- `CONCERNS.md` 的 metrics summary 给出的预测是 `~1,456 -> <500 -> ~200`，不是 `<50`：`.planning/codebase/CONCERNS.md:143-145`
- `FEATURES.md` 也写的是修复 duplicate adapters 后掉到 `~300`：`.planning/research/FEATURES.md:60-65`
- 但 Phase 1 context 又把删除 duplicate adapters 描述为能消掉 `~1,000+` F821：`.planning/phases/01-python-lint-baseline/01-CONTEXT.md:28`, `.planning/phases/01-python-lint-baseline/01-CONTEXT.md:86`

这已经触及 `STANDARDS.md` 的“指标与审计口径标准”：如果数字没有统一口径或实测支撑，就不能直接写成硬门禁。  
参考：`architecture/STANDARDS.md:113-118`

**建议：** 先重新测一遍当前基线，并把 Phase 1 gate 改成“实测值 + 日期 + 命令”。如果还没有重新测量，`<50` 应降级为 stretch goal 或后续 phase 目标。

### 3. [Medium] Phase 1 的 adapter 删除验证命令比风险研究文档更窄，存在漏检风险

`ROADMAP.md` 和 Phase 1 context 当前采用的验证模式主要是：

- `grep "from src.interfaces.adapters|import src.interfaces.adapters"`：`.planning/ROADMAP.md:47`, `.planning/ROADMAP.md:53`, `.planning/phases/01-python-lint-baseline/01-CONTEXT.md:33`

但风险研究文档要求的范围更大：

- 还应覆盖 `from src.interfaces ...`
- 还应覆盖 `src.interfaces.adaptors`
- 核心思想是不只查最显眼的 import 形式  
参考：`.planning/research/PITFALLS.md:112-127`

这意味着当前 Phase 1 的删除证明链比它自己引用的风险规避文档更弱，容易出现“验证通过但漏掉间接引用”的假阳性。

**建议：** 把 Phase 1 的验证命令升级到与 `P-07` 同级别，再把结果写入 context / plan，而不是只保留当前的窄 grep。

### 4. [Medium] `ROADMAP-REVIEW-2026-04-06.md` 已经变成“历史评审快照”，但文档本身没有标明已部分失效

`ROADMAP.md` 现在已经声明自己是 revised 版本：`.planning/ROADMAP.md:4`

但 `ROADMAP-REVIEW-2026-04-06.md` 仍然按旧版问题给出结论，例如：

- 认为 case-conflict 还在 Phase 1：`.planning/ROADMAP-REVIEW-2026-04-06.md:88-113`
- 认为 data access canonical target 仍前后矛盾：`.planning/ROADMAP-REVIEW-2026-04-06.md:41-63`
- 认为 frontend entry 仍被写死成 `main.js`：`.planning/ROADMAP-REVIEW-2026-04-06.md:65-86`

这些意见在“当时”是对的，但 `ROADMAP` 已做修订，review 文件没有任何 `superseded` / `resolved in revision` 标记。把它和新版路线图并列放在 `.planning/` 下，会让后续阅读者误以为这些问题仍全部未处理。

**建议：** 给该文档加一个明显头部说明，例如：

- `Status: historical review snapshot`
- `Resolved by ROADMAP revision dated 2026-04-06: findings 1,2,3,4,6`
- `Remaining open findings: ...`

否则它会持续制造二次歧义。

### 5. [Medium] `STATE.md` 没有同步反映“roadmap 仍待审批”的当前门禁状态

`ROADMAP.md` 当前明确写的是：

- `Status: Review draft — pending approval`：`.planning/ROADMAP.md:5`
- `Execution begins only after user signs off`：`.planning/ROADMAP.md:13`

但 `STATE.md` 的表述更像已经可以直接往下推进：

- `Current Phase: None (ready to start Phase 1)`：`.planning/STATE.md:5`
- `Current focus: Phase 1 — Lint Baseline`：`.planning/STATE.md:14`
- Resume 建议直接给到 `/gsd:plan-phase 1`：`.planning/STATE.md:22-23`
- Phase 1 progress 已写成 `5%`：`.planning/STATE.md:31`

这会让状态文件在流程层面给出一个偏激进的信号：像是可以按现有输入继续推进，而不是先完成跨文档同步和审批确认。

**建议：** 把 `STATE.md` 改成更接近当前真实门禁的状态，例如：

- `Current Phase: None (roadmap under review)`
- `Current blocker: synchronize requirements/state with revised roadmap`
- 把 `Progress` 调整为“context gathered / approval pending”，不要给出容易被误解为已进入执行的百分比。

## Recommended Next Step

建议不要直接进入 Phase 1 计划编写。更稳妥的顺序是：

1. 先同步 `REQUIREMENTS.md`
2. 给 `ROADMAP-REVIEW-2026-04-06.md` 标注历史状态或 resolution matrix
3. 更新 `STATE.md` 反映当前审批门禁
4. 重新核定 Phase 1 的 ruff 目标口径
5. 完成上述同步后，再进入 `/gsd:plan-phase 1`

## Final Assessment

当前这组文档已经形成了一个相对完整的治理骨架，但还没有达到“文档间单一真相源”的状态。真正阻塞后续规划的，不是缺少内容，而是同一件事在不同文档里仍有不同答案。
