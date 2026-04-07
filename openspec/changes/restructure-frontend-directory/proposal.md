# Change: Restructure Frontend Directory & Shared Asset Relocation

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why
The existing `web/frontend/src/views` directory contains >250 Vue pages spread across many loosely‑organized folders, causing duplication, routing complexity, and maintenance overhead. A comprehensive restructure is required to:
- Align with the domain‑driven architecture outlined in `frontend-directory-restructure-plan-revised.md`.
- Move shared components/composables out of `views/` to a true `src/shared/` layer, eliminating page/component blur.
- Ensure all migrations respect dependency relationships and project gate processes.

## What Changes
- Freeze new page additions (git hook).
- Approve and execute the migration plan (file moves, import updates, routing changes).
- Extract shared assets to `src/shared/`.
- Update routing definitions to new paths.
- Run full smoke and end‑to‑end tests.
- Archive the change after deployment.

## Impact
- **Specs affected**: `frontend-structure`, `routing`, `shared-assets`.
- **Code affected**: All Vue pages listed in the migration table, shared component/composable files, routing config, lint and test suites.
- **Risk**: Medium – requires coordinated file moves and import rewrites.

## BREAKING
- File paths for many pages change, breaking existing imports and route URLs until the migration is completed and the smoke test passes.

## Approval
- Requires sign‑off from Architecture Board and Front‑end Lead before implementation.
