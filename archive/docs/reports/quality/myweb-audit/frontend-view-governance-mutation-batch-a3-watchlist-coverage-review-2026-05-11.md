# Frontend View Governance A3 Watchlist Coverage Review

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: next-batch selection evidence for `openspec/changes/update-frontend-view-governance` after `A3-static-shell-archive`.

This review does not move files, edit runtime code, update tests, or change routes.

## Decision

Select the next narrow batch as:

```text
A3-watchlist-coverage-review
```

Do not approve `A3-watchlist-archive` yet.

Reason: `web/frontend/src/views/monitoring/WatchlistManagement.vue` is not an active route owner, but it still contains functional assets that are only partially covered by the current `/watchlist/manage` canonical implementation. The next safe batch is an absorption/coverage decision package, not an archive move.

## Function Tree Position

Primary function-tree domains:

- `06-监控与告警`: legacy source path is `web/frontend/src/views/monitoring/WatchlistManagement.vue`, under the monitoring view family.
- `04-风险管理与监控`: watchlist data is consumed by risk/stop-loss and portfolio monitoring flows through `/api/v1/monitoring/watchlists/*`.
- `05-交易管理`: `FUNCTION_TREE.md` also lists `/api/v1/monitoring/watchlists/*` in the trading domain API prefix because positions, watchlists, and execution/risk views share the same watchlist substrate.

Canonical frontend successor:

- `/watchlist/manage` -> `web/frontend/src/views/watchlist/Manage.vue` -> `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`

## Coverage Matrix

| Legacy capability in `monitoring/WatchlistManagement.vue` | Current canonical coverage | Decision |
| --- | --- | --- |
| List watchlists | Covered by `useWatchlistsStore` and `/v1/monitoring/watchlists` in `apiStores.ts` | Covered |
| Select watchlist and load stocks | Covered by `useWatchlistStocksStore`, verified snapshots, and `WatchlistManager.vue` selector state | Covered |
| Create watchlist | Covered by `createMonitoringWatchlistActions().createWatchlist`, but canonical UI currently uses a prompt and only passes `name` | Partially covered |
| Delete watchlist | Legacy has `deleteWatchlist`; canonical action set does not expose delete in `createMonitoringWatchlistActions` | Gap |
| Add stock | Legacy supports symbol, entry price, entry reason, stop-loss, target price, and weight | Partially covered; canonical action only posts `stock_code` |
| Remove stock | Covered by `createMonitoringWatchlistActions().removeStock` and table action | Covered |
| Edit watchlist | Legacy explicitly warns that edit is not wired | No absorption needed |
| Import/export local JSON | Canonical provides import/export helpers in `stockManagementRouteActions.ts` | Covered |
| Derived stats: watchlist count, stock count, up/down count | Canonical covers count and up/down stats with verified snapshot gating | Covered |
| Derived stats: total value, day P&L, win rate, active alerts | Legacy derives from partial stock fields and `Math.random()` for active alerts | Do not absorb as truth |
| Style asset `WatchlistManagement.scss` | Only supports legacy page and is guarded by monitoring style specs | Move only after page decision |
| Local composable `useWatchlistManagement.ts` | Page-local helper, single consumer | Move or retire with page after useful gaps are absorbed |

## Current Active Blockers

Active code/test references still include:

- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/views/monitoring/composables/useWatchlistManagement.ts`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`

Historical or non-current route references still mention `/monitoring/watchlists`, but current active route/menu truth is `/watchlist/manage`.

## Recommended Next Profile

Prepare an absorption-first batch:

```text
A3-watchlist-absorb-delete-and-rich-add
```

Proposed scope:

- Add or confirm canonical support for deleting a watchlist from `/watchlist/manage`.
- Decide whether `/watchlist/manage` should absorb rich add-stock fields: `entry_price`, `entry_reason`, `stop_loss_price`, `target_price`, and `weight`.
- Do not absorb legacy `activeAlerts` because it is `Math.random()`-derived.
- Do not absorb legacy total value, day P&L, or win-rate cards unless backed by verified canonical stock snapshots and route-level provenance.

Only after that absorption decision is complete should a later archive batch move:

- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/views/monitoring/composables/useWatchlistManagement.ts`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`

## Required Pre-Mutation Checks For Any Later Archive

```bash
rg -n "WatchlistManagement|useWatchlistManagement|WatchlistManagement.scss|monitoring/WatchlistManagement|src/views/monitoring/WatchlistManagement" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "createWatchlist|deleteWatchlist|addStock|removeStock|entry_price|stop_loss_price|target_price|weight" web/frontend/src/views/artdeco-pages/stock-management-tabs web/frontend/src/views/watchlist web/frontend/src/stores web/frontend/tests --glob '!**/.claude/**'
```

## Approval Needed

Recommended approval wording:

```text
批准执行 A3-watchlist-absorb-delete-and-rich-add，只在 /watchlist/manage canonical 链路补齐 watchlist 删除与 rich add-stock 覆盖判断；不归档 monitoring/WatchlistManagement，除非后续单独审批 archive batch。
```

Without explicit approval, no runtime code or archive move should occur.
