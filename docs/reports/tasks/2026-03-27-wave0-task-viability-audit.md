# 2026-03-27 Wave 0 任务价值审计

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


> 2026-04-06 补充说明：
> 本文档反映 `2026-03-27` 当日审计结论。
> 其中 `implement-api-file-level-testing` 后续已按“重建后的收口线”执行完主线 salvage，正式收口记录见 `reports/governance/2026-04-06-api-file-tests-salvage-closeout.md`。

> 目标：对历史“未完成任务”做现状价值判断，避免机械续做。
>
> 审计原则：
> - 以当前 `main` 分支已实现代码为准
> - 不以历史任务状态数字直接推导“应继续开发”
> - 若继续会导致功能倒退、与当前实现冲突，必须停止原任务续做

## 审计方法

每个候选任务按以下问题判断：

1. 当前代码是否已经以其他方式实现原任务目标？
2. 原任务范围是否已被后续重构、合并或替代？
3. 按原任务直接继续，是否会与现状冲突或造成功能倒退？
4. 若仍有价值，应该以什么“新范围”继续，而不是照搬旧任务？

## 审计范围

1. `add-artdeco-strategy-management-chain`
2. `optimize-web-menu-accessibility`
3. `implement-api-file-level-testing`
4. `restructure-frontend-directory`
5. `extend-frontend-config-model`

## 结论总表

| 任务 | 历史进度 | 现状结论 | 是否建议直接续做 |
|---|---:|---|---|
| `add-artdeco-strategy-management-chain` | `23/24` | `视为已完成（仅剩归档动作）` | 否 |
| `optimize-web-menu-accessibility` | `6/9` | `调整后执行` | 否 |
| `implement-api-file-level-testing` | `33/51` | `历史结论：调整后执行；现状：已收口` | 否 |
| `restructure-frontend-directory` | `7/92` | `调整后执行` | 否 |
| `extend-frontend-config-model` | `62/85` | `取消原任务并另立后续增强项` | 否 |

## 用户确认后的最终处理策略

用户已确认当前方针：

- 历史未完成状态本身不构成继续开发依据
- 旧任务包若已失去直接执行价值，可以关闭/放弃
- 只有在当前代码基线上仍然能发挥正向作用的目标，才保留并重建为新任务

### 最终决策

| 任务 | 最终处理 |
|---|---|
| `add-artdeco-strategy-management-chain` | 已归档旧任务包 |
| `optimize-web-menu-accessibility` | 已归档旧任务包 |
| `extend-frontend-config-model` | 已归档旧任务包 |
| `implement-api-file-level-testing` | 不沿用旧任务包；该重建线后续已完成主线 salvage 收口 |
| `restructure-frontend-directory` | 不沿用旧任务包，后续按当前目录现状重建新任务 |

### 已归档路径

- `openspec/changes/archive/2026-03-27-add-artdeco-strategy-management-chain`
- `openspec/changes/archive/2026-03-27-optimize-web-menu-accessibility`
- `openspec/changes/archive/2026-03-27-extend-frontend-config-model`

---

## 1. add-artdeco-strategy-management-chain

### 当前代码现状

- 当前路由仍直接使用：
  - `ArtDecoStrategyManagement.vue`
  - `StrategyParametersTab.vue`
  - `ArtDecoBacktestAnalysis.vue`
- 当前代码中已存在完整的跨 Tab 上下文链路与 `strategyId` handoff：
  - `web/frontend/src/composables/strategy/useStrategyCrossTabContext.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyCrossTabNavigation.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationWriteback.ts`
- 现有测试已覆盖策略管理主链：
  - `web/frontend/tests/e2e/strategy-management-chain.spec.ts`
  - `web/frontend/tests/e2e/strategy-crud.spec.ts`
  - `web/frontend/tests/unit/strategy-cross-tab-navigation.spec.ts`

### 判断

- 原任务描述中的核心能力已经在当前代码中落地。
- 当前剩余的“1 项未完成”更像 OpenSpec 任务归档/状态维护，不再是功能缺口。
- 继续按“功能开发任务”推进会重复实现已有能力，收益低且有回退风险。

### 结论

`视为已完成（仅剩归档动作）`

### 建议后续动作

- 不再继续开发此功能
- 仅执行：
  - 复核 tasks 状态
  - 归档该 change

---

## 2. optimize-web-menu-accessibility

### 当前代码现状

- 当前代码中已经存在大量无障碍语义改造：
  - `aria-expanded`
  - `aria-controls`
  - `aria-label`
  - `prefers-reduced-motion`
- 可见证据：
  - `web/frontend/src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue`
  - `web/frontend/src/components/artdeco/base/ArtDecoCollapsible.vue`
  - `web/frontend/src/styles/artdeco-global.scss`
  - `web/frontend/tests/e2e/accessibility-smoke.spec.ts`
- 但平台快捷键文案仍明显是硬编码 `Ctrl`：
  - `web/frontend/src/components/common/KeyboardShortcuts.vue`

### 判断

- High / Medium priority 目标大部分已经被当前代码吸收。
- 剩余价值集中在两点：
  1. 平台自适应快捷键文案
  2. 人工无障碍验证收口
- 直接照历史任务全文继续做，会把已经完成的部分重复实施。

### 结论

`调整后执行`

### 建议新范围

- 仅保留以下子范围：
  - 平台自适应快捷键文案（Mac `⌘` / Windows/Linux `Ctrl`）
  - 针对菜单导航和快捷键提示的人工验证清单

### 最终处理

关闭/归档旧任务包。

说明：
- 当前不再沿用原 `6/9` checklist 继续推进
- 若未来仍要处理快捷键平台适配或人工无障碍验证，应另建小型后续任务

---

## 3. implement-api-file-level-testing

### 当前代码现状

- 代码库中已经存在较完整的 file-level API 测试框架：
  - `tests/api/file_tests/`
  - `tests/api/file_tests/run_file_tests.py`
  - 大量 `test_*_api.py`
- 但当前 CI workflow 明确带着 readiness gate：
  - `.github/workflows/api-file-tests.yml`
  - 其中仍通过 grep 检测 placeholder/mock readiness 逻辑决定是否跳过

### 判断

- 这项任务不是“未开始”，而是“框架已建、治理未收口”。
- 当前仍然具有正向价值，因为它能继续提升 API 模块级测试治理。
- 但不能再按原始“62 文件 / 566 endpoint”历史口径机械推进，需要先重新基线化。

### 结论

`调整后执行`

### 建议新范围

- 重新核对当前真实 API 文件数和已覆盖测试数
- 删除/替换 workflow 中 placeholder readiness gate
- 以“现有测试框架收口”为目标，而不是追旧数字

### 最终处理

不继续执行旧任务包。

补充：
- 后续重建线已完成主线 salvage 收口。
- 当前唯一残留项是 root dirty worktree 内 `tests/api/file_tests/test_tradingview_api.py` 的格式等价差异，归类为 root-dirty hygiene。

---

## 4. restructure-frontend-directory

### 当前代码现状

- 当前 `web/frontend/src/views` 结构仍然远未达到该任务目标：
  - 存在 `artdeco-pages`
  - 存在 `demo` / `converted.archive` / `freqtrade-demo`
  - 存在大量非目标域目录
- 当前目录结构证据：
  - `find web/frontend/src/views -maxdepth 2 -type d`
- 同时，OpenSpec 目标要求：
  - 域目录化
  - `deprecated/`
  - `src/shared/` 提取
  - 路由与路径迁移

### 判断

- 该任务目标在当前代码基线上仍未实现，继续推进仍然有正向价值。
- 但原任务包过大、依赖广，且部分前提已经随代码演进发生漂移。
- 若直接按 `7/92` 后续编号硬做，极容易对当前稳定前端链路造成回退。

### 结论

`调整后执行`

### 建议新范围

- 不直接续跑历史 `92` 项 checklist
- 先基于当前目录结构重建批次：
  1. 目录现状盘点
  2. 活跃页 / 历史页 / shared 资产分类
  3. 先小批次迁移，再逐域推进

### 最终处理

不继续执行旧任务包，后续重建为新任务。

---

## 5. extend-frontend-config-model

### 当前代码现状

- 当前 `pageConfig.ts` 已是自动生成模型：
  - `Routes processed: 35`
  - 已存在：
    - `getPageConfig`
    - `getTabConfig`
    - `isMonolithicConfig`
- 类型层也已存在：
  - `web/frontend/src/types/pageConfig.ts`
- 但该 change 当前 `openspec show ... --deltas-only` 输出为 `deltaCount: 0`
- 同时 `TAB_CONFIGS` 当前为空，说明“monolithic tab 配置扩展”与现状已经发生明显漂移

### 判断

- 原任务的“基础配置模型扩展”目标，大部分已经被当前实现吸收。
- 历史 change 本身与现状不再对齐，继续按原 tasks 机械推进风险较高。
- 如果后续还要做配置模型增强，应以当前自动生成系统为基础重新定义新 change。

### 结论

`取消原任务并另立后续增强项`

### 建议后续动作

- 不继续执行旧 change
- 后续如需增强配置模型，另起新变更，明确当前真实问题：
  - `TAB_CONFIGS` 是否需要重新引入
  - 自动生成模型是否需要支持更复杂页面语义

---

## 下一步候选项

基于当前已确认的最终处理策略，后续真正值得进入实施审批的，不是旧任务包本身，而是新任务目标：

1. 重建 `implement-api-file-level-testing` 后续任务
   - 见：[2026-03-27-api-file-testing-replacement-task.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-api-file-testing-replacement-task.md)
2. 重建 `restructure-frontend-directory` 后续任务
   - 见：[2026-03-27-frontend-directory-restructure-replacement-task.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-restructure-replacement-task.md)

## 建议审批口径

下一步如果继续，建议审批的是以下二选一：

1. `同意创建 API file-level testing 收口新任务`
2. `同意创建 frontend directory restructure 现状盘点与新批次任务`
