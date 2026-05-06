# Change: Add Trade Reconciliation Statement

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
`FUNCTION_TREE` still marks `5.2 对账单` as unfinished, while the current trade-domain surface only provides history and execution-oriented flows. The repository therefore lacks a dedicated reconciliation statement capability with its own account descriptors, import surface, deterministic matching, and export contract.

## What Changes
- Add a dedicated trade reconciliation statement capability under the existing trade domain.
- Add first-batch account descriptors, internal statement projection, CSV import, deterministic matching, and CSV export.
- Add a dedicated `/trade/reconciliation` frontend route and a matching navigation label.
- Keep the reconciliation statement surface separate from `History.vue` and from broker-lifecycle reconciliation.

## Impact
- Affected specs:
  - `trade-reconciliation-statement`
  - `frontend-routing`
- Affected code:
  - `web/backend/app/api/trade/*`
  - `web/backend/app/services/statement_reconciliation/*`
  - `web/frontend/src/views/trade/*`
  - `web/frontend/src/router/index.ts`
