# 2026-03-27 主线未完成任务清单

> 2026-04-06 补充说明：
> 本文档是 `2026-03-27` 的历史快照。
> 其中 `implement-api-file-level-testing` 后续已完成主线 salvage 收口，正式结论见 `docs/reports/tasks/2026-03-27-api-file-testing-replacement-task.md` 与 `reports/governance/2026-04-06-api-file-tests-salvage-closeout.md`。

> 目的：汇总当前仓库主线可见的未完成事项，形成后续执行审批依据。
>
> 盘点来源：
> - `openspec list`
> - `openspec list --specs`
> - [TASK.md](/opt/claude/mystocks_spec/TASK.md)
> - [docs/reports/tasks/NEXT_WORK_TASKS.md](/opt/claude/mystocks_spec/docs/reports/tasks/NEXT_WORK_TASKS.md)
> - [docs/reports/TODO_STATUS_INVESTIGATION_REPORT.md](/opt/claude/mystocks_spec/docs/reports/TODO_STATUS_INVESTIGATION_REPORT.md)
> - [docs/reports/TODO_STATUS_DISPLAY_ISSUE_INVESTIGATION_REPORT.md](/opt/claude/mystocks_spec/docs/reports/TODO_STATUS_DISPLAY_ISSUE_INVESTIGATION_REPORT.md)

## 当前基线

- 当前分支：`main`
- 工作区状态：干净
- 已完成收尾：PR `#16` 已合并，前端/视觉/E2E 主线检查已通过
- `Wave 0` 审计结果文档：
  - [2026-03-27-wave0-task-viability-audit.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-wave0-task-viability-audit.md)
- 用户已确认最终策略：
  - 关闭/放弃已失去直接执行价值的旧任务包
  - 仅保留仍有正向作用的目标，并在需要时重建为新任务
- 当前任务源优先级：
  - 第一优先级：`OpenSpec active changes`
  - 第二优先级：仓库内 handover / investigation 文档
  - 第三优先级：`TASK.md` 自动摘要（当前内容偏旧，仅作参考）

## 执行前置门禁：现状价值判断

在继续本文档中的任何“未完成任务”之前，必须先完成一次基础判断：

> 这些任务虽然处于未完成状态，但**不能**因为历史状态未清零就直接继续开发。
> 必须以**当前项目中已实现的代码和当前主线行为**为准，判断该任务是否仍然值得继续。

### 必须回答的判断问题

对每个候选任务，至少先回答以下问题：

1. 当前代码是否已经以其他方式实现了原任务目标？
2. 原任务范围是否已经被后续重构、合并、替代或取消？
3. 若继续按原任务推进，是否会与当前主线实现冲突，或造成功能倒退？
4. 继续执行该任务，是否仍能对当前项目发挥积极作用？
5. 若该任务仍有价值，它在当前代码基线上应该以什么“新范围”继续，而不是机械照搬旧任务描述？

### 判断结果分类

- `继续执行`
  - 当前代码仍存在真实缺口
  - 原任务目标仍有价值
  - 继续实施不会造成回退
- `调整后执行`
  - 原任务仍有部分价值
  - 但范围、路径、目标需要按现状重写
- `视为已完成`
  - 当前代码已通过其他实现路径满足目标
- `取消/归档`
  - 目标已失效、被替代，或继续做会引入倒退

### 审批规则

- 未经上述判断，**不得**直接对任何未完成任务进入实现阶段
- 审批顺序应为：
  1. 批准执行“现状价值判断”
  2. 输出任务判断结果
  3. 再批准其中被判定为“继续执行”或“调整后执行”的项

## Wave 0：任务价值审计（已完成）

在任何 Wave 1 / Wave 2 实施前，必须先完成 `Wave 0`。
当前已完成审计，详见：

- [2026-03-27-wave0-task-viability-audit.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-wave0-task-viability-audit.md)

### Wave 0 输出物

- 每个候选任务一条审计结论
- 审计结论必须包含：
  - 当前代码实现现状
  - 与原任务目标的差异
  - 风险判断
  - 最终归类：`继续执行 / 调整后执行 / 视为已完成 / 取消归档`

### Wave 0 已审计任务

1. `add-artdeco-strategy-management-chain`
2. `optimize-web-menu-accessibility`
3. `implement-api-file-level-testing`
4. `restructure-frontend-directory`
5. `extend-frontend-config-model`

### Wave 0 后的最终决策

#### 关闭/归档旧任务包

- `add-artdeco-strategy-management-chain`
- `optimize-web-menu-accessibility`
- `extend-frontend-config-model`

已归档到：

- `openspec/changes/archive/2026-03-27-add-artdeco-strategy-management-chain`
- `openspec/changes/archive/2026-03-27-optimize-web-menu-accessibility`
- `openspec/changes/archive/2026-03-27-extend-frontend-config-model`

#### 保留目标，但不沿用旧任务包

- `implement-api-file-level-testing`
- `restructure-frontend-directory`

替代任务说明：

- [2026-03-27-api-file-testing-replacement-task.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-api-file-testing-replacement-task.md)
- [2026-03-27-frontend-directory-restructure-replacement-task.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-restructure-replacement-task.md)

## 执行优先级定义

- `P0`：可快速收口，完成收益高，建议优先执行
- `P1`：当前主线高优先级，适合作为下一批正式实施
- `P2`：中期治理项，体量大，需分批推进
- `P3`：需要先澄清范围或先补 proposal/spec 的事项

## P0：已决定关闭/归档的旧任务包

| 任务 | 当前进度 | 原因 | 建议动作 |
|---|---:|---|---|
| `add-artdeco-strategy-management-chain` | `23/24` | 当前代码和测试已基本闭环 | 关闭/归档旧任务包 |
| `optimize-web-menu-accessibility` | `6/9` | 旧任务包范围已不适配当前状态 | 关闭/归档旧任务包，未来如需处理则另起小任务 |
| `extend-frontend-config-model` | `62/85` | 当前配置模型已实现较多，旧 change 与现状漂移 | 关闭/归档旧任务包 |

## P1：保留价值、等待重建的新任务目标

| 任务 | 当前进度 | 风险/说明 | 建议动作 |
|---|---:|---|---|
| `implement-api-file-level-testing` | `33/51` | 历史判断为“需重建”；后续已完成 mainline salvage 收口 | 保留此行仅作历史记录，现行结论见 2026-04-06 closeout |
| `restructure-frontend-directory` | `7/92` | 与当前目录治理主线最相关，但旧 checklist 不适合直接续跑 | 重建为“目录现状盘点与新批次任务” |

## P2：暂不处理的其他活跃变更

| 任务 | 当前进度 | 说明 |
|---|---:|---|
| `implement-web-frontend-v2-navigation` | `17/223` | 暂不处理 |
| `refactor-web-frontend-menu-architecture` | `20/153` | 暂不处理 |
| `consolidate-technical-debt-remediation` | `16/142` | 暂不处理 |
| `enhance-api-contract-management-integration` | `17/44` | 暂不处理 |
| `expand-akshare-data-sources` | `49/105` | 暂不处理 |
| `implement-pinia-api-standardization` | `4/20` | 暂不处理 |
| `optimize-data-source-v2` | `0/121` | 暂不处理 |
| `add-smart-quant-monitoring` | `0/137` | 暂不处理 |
| `add-quantitative-trading-algorithms` | `0/140` | 暂不处理 |
| `add-comprehensive-risk-management-system` | `0/64` | 暂不处理 |

## P3：执行前需澄清或补齐定义

| 项目 | 当前状态 | 建议 |
|---|---|---|
| `extend-frontend-config-model` | `tasks` 有进度，但 `deltas` 为空 | 执行前先核对 change 是否缺 spec delta 或已漂移 |
| `TASK.md` Auto Layer 1 | 摘要内容明显过时 | 不作为执行真值源，后续可单独整理 |
| `docs/reports/tasks/NEXT_WORK_TASKS.md` | 内容仍停在旧 `P1` 阶段 | 建议降级为历史参考，不作为现行计划 |
| OpenCode TODO 状态显示异常 | 已有调查报告，但未闭环 | 作为低优先级独立调查项，不建议与主线目录治理混做 |

## 当前不建议立即执行的事项

- `implement-optimized-testing-strategy`
- `implement-typescript-type-extension-system`
- `implement-html5-migration-experience-optimization`
- `audit-data-db-runtime`
- `tech-debt-governance-2026q1`

原因：
- 完成度低
- 依赖面较广
- 与当前“目录治理 / 前端主线收口”相比，不是最短路径

## 建议执行波次

### Wave 1：只创建新任务，不直接实施旧任务包

1. `API file-level testing` 线已完成收口，后续仅剩 root-dirty hygiene（如需）
2. 创建 `frontend directory restructure 现状盘点与新批次任务`

当前已完成：
- 替代任务说明文档已创建
- 旧任务包已归档

## 建议审批口径

如果按当前最终策略推进，建议审批的是以下二选一：

1. `同意归档/关闭这 3 个旧任务包`
2. `同意创建 2 个替代性新任务`

## 备注

- 本文档是“执行清单”，不是新的 OpenSpec proposal。
- 后续若继续实施，只应围绕新任务目标展开，不应回到旧 checklist 逐条续跑。
