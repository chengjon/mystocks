# Frontend View Governance A3 Watchlist Archive Selection

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: next-batch selection after `A3-watchlist-ui-coverage-minimal` for `openspec/changes/update-frontend-view-governance`.

This review does not move files, edit runtime code, update tests, or change routes.

## Decision

Select the next narrow batch as:

```text
A3-watchlist-archive-prep
```

Do not execute the archive move in this selection batch.

## Why Archive Prep Is Now Eligible

The previous blockers have been closed in separate batches:

- Action layer gap closed by `A3-watchlist-absorb-delete-and-rich-add`.
- Canonical UI gap closed by `A3-watchlist-ui-coverage-minimal`.
- Legacy random/fallback-derived stats remain explicitly unabsorbed.
- `/watchlist/manage` remains the canonical route truth for watchlist management.

Current remaining active references to the legacy monitoring page group are direct lifecycle guards and self-references:

- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/views/monitoring/composables/useWatchlistManagement.ts`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`

Historical E2E label strings and demo OpenStock components are not route/menu ownership evidence for the monitoring Watchlist page.

## Proposed Archive-Prep Scope

Prepare an approval package that names:

- exact archive candidates
- exact direct guard retirements
- post-move active reference checks
- targeted Vitest validation
- OpenSpec and markdown governance gates
- staged GitNexus detection requirement

The archive-prep package must continue to exclude:

- `web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue`
- `web/frontend/src/views/demo/OpenStockDemo.vue`
- `web/frontend/src/views/OpenStockDemo.vue`
- `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- canonical `/watchlist/manage` route files

## Recommended Next Placeholder

```text
A3-watchlist-archive-prep
```

Only after that approval package is accepted should a later `A3-watchlist-archive` mutation move:

- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/views/monitoring/composables/useWatchlistManagement.ts`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`

Target archive directory should be:

- `archive/web/frontend/src/views/monitoring/watchlist-management/`
