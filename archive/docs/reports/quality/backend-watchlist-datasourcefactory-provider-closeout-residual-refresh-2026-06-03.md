# Backend Watchlist DataSourceFactory Provider Closeout / Residual Refresh - 2026-06-03

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: `G2.322`
- Status: completed no-source governance closeout / residual refresh
- Prepared at: `2026-06-03T03:49:12+08:00`
- Base branch: `wip/root-dirty-20260403`
- PR #474 merge commit checked: `2ebff6d7ded33403c691a60fc43f87dabf90a975`
- Parent node: `G2.321`

G2.321 was accepted/merged by PR `#474`. G2.322 closes that source lane and
refreshes residual-call observations. It does not authorize business source,
test, route-contract, frontend, config, script, OpenSpec, docs/api, PM2, or
runtime-state changes.

## Closed Parent

| Field | Value |
|---|---|
| Parent node | `G2.321 watchlist DataSourceFactory provider implementation` |
| PR | `#474` |
| State | `MERGED` |
| Merge commit | `2ebff6d7ded33403c691a60fc43f87dabf90a975` |
| Merged at | `2026-06-02T16:23:25Z` |

Accepted G2.321 state:

- `get_watchlist_data_source()` exists as the route-local provider.
- Eight authorized watchlist handlers receive `watchlist_adapter` through `Depends(get_watchlist_data_source)`.
- Handler-body direct `DataSourceFactory()` calls are `0`.
- Handler-body direct `get_data_source("watchlist")` calls are `0`.
- Provider backing `DataSourceFactory()` / `get_data_source("watchlist")` calls are `1/1`.
- `watchlist_adapter` dependency parameters are `8`.

The retained provider backing call is expected infrastructure, not a route-body
residual.

## Residual Refresh

Read-only scan anchor:

- commit: `2ebff6d7ded33403c691a60fc43f87dabf90a975`
- method: `git ls-tree` / `git show` over the accepted PR #474 merge commit
- write scope: none; no source files were written

Observation summary:

| Metric | Result |
|---|---:|
| API Python files scanned | 219 |
| API route decorator observations | 566 |
| Parent route/OpenAPI smoke | 548/500/0 |
| Watchlist authorized handlers | 8 |
| Watchlist handler direct `DataSourceFactory()` calls | 0 |
| Watchlist handler direct `get_data_source("watchlist")` calls | 0 |
| Watchlist retained provider backing calls | 1/1 |

The route decorator count is observation-only and is not a replacement for the
parent route/OpenAPI smoke metric.

Remaining DataSourceFactory / `.get_data_source(...)` observations outside the
closed watchlist route-body lane:

| File | `DataSourceFactory()` | `get_data_source` observations | Classification |
|---|---:|---:|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 3 | 3 | residual observation |
| `web/backend/app/api/technical_analysis.py` | 8 | 8 | largest active route-body residual candidate |
| `web/backend/app/api/watchlist.py` | 1 | 1 | retained provider backing |

## Boundary

G2.322 is a pure governance node. It may update only steward-tree state,
generated evidence, the human-readable report, and the governance task card.

Future source candidates selected from the refreshed residual queue require a
new no-source ownership / authorization node first, and any source PR must stop
for human review before merge.

## Next Gate

G2.323 starts the no-source `technical_analysis.py` DataSourceFactory ownership
/ route-provider decision. It does not authorize source edits.
