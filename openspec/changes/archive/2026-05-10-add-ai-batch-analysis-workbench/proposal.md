# Change: Add AI batch analysis workbench

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Why
`7.2 批量分析` currently has implementation evidence across backtest, screener, and scheduler modules, but lacks a canonical AI-domain workbench and v1 aggregation contract. A single observation surface is needed to show batch universe, task status, result summaries, and safety boundaries without replacing existing engines.

## What Changes
- Add canonical v1 batch analysis routes under `/api/v1/strategies/batch-analysis/*`.
- Add `/ai/batch` as the AI-domain batch analysis workbench for batch backtest, screening, and monitoring summaries.
- Keep existing strategy/backtest/screener implementations as underlying evidence; this change only adds a first-batch aggregation and observation surface.
- Update frontend routing/menu and FUNCTION_TREE evidence for `7.2 批量分析`.

## Impact
- Affected specs: `ai-batch-analysis`, `frontend-routing`, `function-tree-governance`
- Affected code: `web/backend/app/api/v1/strategy/*`, `web/frontend/src/api/*`, `web/frontend/src/views/ai/*`, router/menu configuration
