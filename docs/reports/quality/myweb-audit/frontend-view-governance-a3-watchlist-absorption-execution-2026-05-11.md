# Frontend View Governance A3 Watchlist Absorption Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: `A3-watchlist-absorb-delete-and-rich-add` for `openspec/changes/update-frontend-view-governance`.

## Executed Change

This batch does not archive `web/frontend/src/views/monitoring/WatchlistManagement.vue`.

It absorbs the safe action-layer gap into the canonical `/watchlist/manage` chain by updating:

- `web/frontend/src/stores/apiStores.ts`
- `web/frontend/tests/unit/stores/watchlist-api-stores.spec.ts`

Implemented coverage:

- `createMonitoringWatchlistActions().deleteWatchlist(watchlistId)` now calls `/v1/monitoring/watchlists/:watchlistId`.
- `createMonitoringWatchlistActions().addStock(...)` now accepts either the previous symbol string or a rich stock payload with `entry_price`, `entry_reason`, `stop_loss_price`, `target_price`, and `weight`.
- Existing string-based add-stock callers remain compatible.

Non-scope:

- No archive move.
- No `router/index.ts` or `MenuConfig.ts` change.
- No legacy `monitoring/WatchlistManagement.vue` mutation.
- No absorption of legacy `activeAlerts`, because it is random-derived.
- No absorption of legacy total value, day P&L, or win-rate cards beyond existing verified stock-row summary behavior.

## TDD Evidence

RED:

```bash
cd web/frontend && npx vitest run tests/unit/stores/watchlist-api-stores.spec.ts
```

Result:

- Failed as expected: `actions.deleteWatchlist is not a function`.

GREEN:

```bash
cd web/frontend && npx vitest run tests/unit/stores/watchlist-api-stores.spec.ts
```

Result:

- Passed: 1 file, 3 tests.

Note: the sandboxed Vitest invocation failed before loading tests because `vitest.config.mts` could not read `../../../package.json`; the same command was rerun outside the sandbox for both RED and GREEN.

## Impact Evidence

```bash
gitnexus_impact(target="createMonitoringWatchlistActions", direction="upstream", includeTests=true)
```

Result:

- Risk: LOW.
- Direct impact: 3 references.
- Affected processes: 0.

## Completion Decision

This closes the action-helper portion of `A3-watchlist-absorb-delete-and-rich-add`.

`monitoring/WatchlistManagement.vue`, `useWatchlistManagement.ts`, and `WatchlistManagement.scss` should remain unarchived until a later batch explicitly decides whether the canonical UI should expose rich add-stock fields or keep them as API-only capability.
