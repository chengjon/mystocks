# Frontend View Governance A3 Watchlist UI Coverage Decision

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: next-batch selection evidence for `openspec/changes/update-frontend-view-governance` after `A3-risk-dashboard-archive`.

This review does not move files, edit runtime code, update tests, or change routes.

## Decision

Select the next narrow batch as:

```text
A3-watchlist-ui-coverage-decision
```

Do not approve `A3-watchlist-archive` yet.

Reason: the action-helper gap from legacy `monitoring/WatchlistManagement.vue` has already been absorbed into `createMonitoringWatchlistActions()`, but the canonical `/watchlist/manage` UI does not yet expose all useful user-facing controls that the legacy page contained.

## Current Successor State

Canonical route:

- `/watchlist/manage` -> `web/frontend/src/views/watchlist/Manage.vue` -> `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`

Previously absorbed action layer:

- `createMonitoringWatchlistActions().deleteWatchlist(watchlistId)`
- `createMonitoringWatchlistActions().addStock(watchlistId, richPayload)`
- `createMonitoringWatchlistActions().removeStock(watchlistId, symbol)`
- Compatibility with the previous symbol-only add-stock call

## UI Coverage Matrix

| Legacy UI capability in `monitoring/WatchlistManagement.vue` | Current `/watchlist/manage` UI coverage | Decision |
| --- | --- | --- |
| List watchlists | Covered by watchlist tabs and verified store snapshots | Covered |
| Select watchlist | Covered by watchlist tab selection and per-watchlist stock snapshots | Covered |
| Create watchlist | Covered with a prompt-based minimal flow | Covered enough |
| Delete watchlist | Action helper exists, but no canonical UI control currently calls it | UI gap |
| Add stock with rich fields | Action helper accepts rich payload, but no canonical UI form currently calls it | UI gap |
| Remove stock | Covered by table row action | Covered |
| Import/export local JSON | Covered by canonical import/export helpers | Covered |
| Total value/day P&L/win rate cards | Legacy derives from partial stock values and fallbacks | Do not absorb as runtime truth |
| Active alerts count | Legacy uses `Math.random()` | Do not absorb |
| Edit watchlist | Legacy explicitly warns it is not wired | No absorption needed |

## Recommended Next Profile

Prepare a runtime decision package:

```text
A3-watchlist-ui-coverage-minimal
```

Recommended scope:

- Add a conservative delete-watchlist UI affordance to `/watchlist/manage`, using the already absorbed `deleteWatchlist` action.
- Add either:
  - a minimal add-stock UI that only posts `stock_code`, or
  - an explicit product decision that rich add-stock remains API-only for now and legacy rich-form UI is not retained.
- Preserve existing verified snapshot and stale-state semantics in `WatchlistManager.vue`.
- Do not absorb legacy total value, day P&L, win rate, or random active-alert stats.
- Do not archive `monitoring/WatchlistManagement.vue` in the same batch; archive remains a later separate approval after UI decision is closed.

## Archive Preconditions

Only after the UI decision batch is complete should a later archive-prep batch consider moving:

- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/views/monitoring/composables/useWatchlistManagement.ts`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`

Before that archive-prep, re-run:

```bash
rg -n "WatchlistManagement|useWatchlistManagement|WatchlistManagement.scss|monitoring/WatchlistManagement|src/views/monitoring/WatchlistManagement" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "deleteWatchlist|addStock|removeStock|entry_price|entry_reason|stop_loss_price|target_price|weight" web/frontend/src/views/artdeco-pages/stock-management-tabs web/frontend/src/views/watchlist web/frontend/src/stores web/frontend/tests --glob '!**/.claude/**'
```

## Approval Needed

Recommended approval wording:

```text
批准准备 A3-watchlist-ui-coverage-minimal，只在 /watchlist/manage canonical UI 决定并补齐删除清单和添加股票的最小覆盖；不归档 monitoring/WatchlistManagement，不吸收旧页随机/兜底统计。
```

Without explicit approval, no runtime code or archive move should occur.
