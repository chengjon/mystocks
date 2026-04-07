# Phase 1 Governance Approval Package

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Purpose

This package is prepared for Phase 1 governance review of change `restructure-frontend-directory`.
It provides a PR-ready summary, explicit approval checklist, and sign-off templates.

## PR Summary (Ready to Paste)

### Title
`[OpenSpec][Phase-1 Approval] restructure-frontend-directory`

### Summary
- Introduce domain-driven front-end directory migration plan for `web/frontend/src/views`.
- Extract reusable assets from `src/views/shared/*` to `src/shared/*`.
- Enforce pre-flight freeze with a pre-commit gate:
  - blocks newly added `web/frontend/src/views/*.vue` files unless declared in migration table.
- Define phased migration execution and verification gates in OpenSpec tasks.

### Scope
- OpenSpec proposal/design/tasks/spec for `restructure-frontend-directory`.
- Phase 0 completed artifacts:
  - `scripts/hooks/check-views-migration-table.py`
  - `.pre-commit-config.yaml` hook integration (`views-migration-gate`)
  - `MIGRATION_PROGRESS.md`

### Non-Scope (This PR)
- No page moves.
- No route rewrites.
- No runtime behavior changes.

### Risk
- Medium (future migration is broad), low for this PR (documentation + gate only).

### Validation
- `python scripts/hooks/check-views-migration-table.py`
- `openspec validate restructure-frontend-directory --strict`

## Reviewer Checklist

### Architecture Board / Architecture Lead
- [ ] OpenSpec package is complete (`proposal.md`, `design.md`, `tasks.md`, delta spec).
- [ ] Domain split strategy is acceptable (market/data/strategy/trade/risk/watchlist/system/errors).
- [ ] Shared-asset extraction target (`src/shared/*`) is acceptable.
- [ ] Breaking-impact statement and migration sequencing are acceptable.
- [ ] Approval comment posted with keyword: `APPROVED`.

### Front-end Lead
- [ ] Migration task breakdown is executable and ordered correctly.
- [ ] Router and import-update strategy is acceptable.
- [ ] Validation gates (`lint`, `type-check`, smoke, e2e) are acceptable.
- [ ] Pre-commit freeze rule for new view pages is acceptable.
- [ ] Sign-off comment posted with keyword: `APPROVED`.

## Required Approval Comments

### Architecture Lead Comment Template
`APPROVED - restructure-frontend-directory: architecture scope, migration sequencing, and risk controls are accepted for Phase 2 execution.`

### Front-end Lead Comment Template
`APPROVED - restructure-frontend-directory: task decomposition and implementation gates are accepted. Ready for Review.`

## Go/No-Go Gate to Enter Phase 2

Proceed only when all are true:
- [ ] Architecture Lead comment contains `APPROVED`.
- [ ] Front-end Lead comment contains `APPROVED`.
- [ ] No conflicting active change blocks this migration scope.
- [ ] OpenSpec strict validation remains passing.

Otherwise: stay in Phase 1 and do not execute Phase 2 tasks.
