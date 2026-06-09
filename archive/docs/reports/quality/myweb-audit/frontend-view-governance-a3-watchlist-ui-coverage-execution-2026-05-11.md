# Frontend View Governance A3 Watchlist UI Coverage Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: `A3-watchlist-ui-coverage-minimal` for `openspec/changes/update-frontend-view-governance`.

## Executed Change

This batch does not archive `web/frontend/src/views/monitoring/WatchlistManagement.vue`.

It closes the canonical UI coverage gap in `/watchlist/manage` by updating:

- `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- `web/frontend/src/views/watchlist/__tests__/Manage.spec.ts`

Implemented coverage:

- Added a delete-current-watchlist UI affordance wired to `createMonitoringWatchlistActions().deleteWatchlist(activeWatchlistId)`.
- Added a minimal add-stock UI affordance that prompts only for `stock_code` and calls `createMonitoringWatchlistActions().addStock(activeWatchlistId, symbol)`.
- Kept the full legacy rich add-stock form out of scope; rich payload support remains available at the action layer from the prior absorption batch.
- Preserved verified snapshot, pending, stale, and first-load failure semantics already present in `WatchlistManager.vue`.

Non-scope:

- No archive move.
- No `router/index.ts` or `MenuConfig.ts` change.
- No `monitoring/WatchlistManagement.vue`, `useWatchlistManagement.ts`, or `WatchlistManagement.scss` mutation.
- No absorption of legacy `activeAlerts`, total value, day P&L, or win-rate cards.

## TDD Evidence

RED:

```bash
cd web/frontend && npx vitest run src/views/watchlist/__tests__/Manage.spec.ts
```

Result:

- Failed as expected: 3 new tests failed because the canonical route had no `删除组合` or `添加股票` UI controls.

GREEN:

```bash
cd web/frontend && npx vitest run src/views/watchlist/__tests__/Manage.spec.ts tests/unit/stores/watchlist-api-stores.spec.ts
```

Result:

- Passed: 2 files, 11 tests.

Note: sandboxed Vitest could not read `../../../package.json` through `vitest.config.mts`; the command was rerun outside the sandbox for RED and GREEN.

## Impact Evidence

```json
{
  "target": "web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue",
  "direction": "upstream",
  "risk": "LOW",
  "direct": 2,
  "processes_affected": 0
}
```

Direct importers:

- `web/frontend/src/views/watchlist/Manage.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoStockManagement.vue`

## Completion Decision

This closes the UI coverage portion that blocked a later Watchlist archive-prep decision.

`monitoring/WatchlistManagement.vue`, `useWatchlistManagement.ts`, and `WatchlistManagement.scss` should remain unarchived until a separate archive-prep package confirms direct guard retirement and active reference cleanup.
