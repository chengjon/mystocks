# Change: Sectioned System-Config Contract

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Why
The current `System-Config` page is explicitly degraded: frontend saves most values to local storage, datasource writes live in a different system page, and notification preferences already exist as a user-scoped backend contract. Reopening the closed frontend-mainline would violate the current closeout decision, but leaving the page in a permanently ambiguous state would continue the single-source-of-truth gap.

## What Changes
- Define a new `system-settings-contract` capability for a sectioned `System-Config` page contract.
- Preserve mixed ownership boundaries:
  - `general`, `datasource`, and `security` are system-scoped sections.
  - `notification` remains a user-scoped section.
- Standardize a unified page contract with explicit per-section ownership metadata rather than a fake monolithic backend truth.
- Reuse existing canonical datasource and notification backends instead of introducing duplicate storage or shim persistence layers.
- Define migration completion and exit criteria for retiring the current degraded local-storage behavior.
- Require metric/reporting separation between measured runtime values, inferred status, and historical baselines.

## Impact
- Affected specs: `system-settings-contract` (new)
- Affected code later: `web/frontend/src/views/system/Settings.vue`, `web/frontend/src/services/systemSettingsContract.ts`, `web/frontend/src/services/TradingApiManager.ts`, backend system/user settings APIs
- Affected governance: migration closeout, compatibility-layer retirement, metrics labeling
- No runtime behavior changes in this proposal batch
