# Backend Postgres Async Monitoring Watchlists Provider Authorization - 2026-05-30

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a governance evidence artifact. It does not
authorize code changes, test changes, route/OpenAPI changes, OpenSpec proposal
creation, issue label changes, PM2 commands, or PR merges.

## Status

- Status: for review
- G2 node: G2.255
- Branch: `g2-255-monitoring-watchlists-postgres-provider-authorization`
- Base: `wip/root-dirty-20260403`
- Current HEAD checked: `c64260f1795b39c82903fa7fd370b0ccaee3ac36`
- Parent: G2.254 / PR `#407`, merged at `c64260f1795b39c82903fa7fd370b0ccaee3ac36`
- Source edit authority: no

This report is a no-source authorization packet. It does not modify backend
source, tests, OpenAPI, frontend, config, scripts, PM2 state, or OpenSpec files.

## Decision Request

Approve a future G2.256 path-limited implementation lane for
`web/backend/app/api/monitoring_watchlists.py`.

The future implementation may move only the seven current route-body
`get_postgres_async()` lookups behind a route-local dependency provider, named
`get_monitoring_watchlists_postgres_async` unless the implementation review
finds a better local name.

## Candidate Snapshot

Current HEAD has eight `monitoring_watchlists.py` route handlers. Seven of them
still call `get_postgres_async()` directly in the route body.

| Handler | Route | Response model | Direct calls | Authorized for future G2.256 |
|---|---|---|---:|---|
| `create_watchlist` | `POST /api/v1/monitoring/watchlists` | `UnifiedResponse[WatchlistResponse]` | 1 | yes |
| `list_watchlists` | `GET /api/v1/monitoring/watchlists` | `UnifiedResponse[List[WatchlistResponse]]` | 1 | yes |
| `get_watchlist` | `GET /api/v1/monitoring/watchlists/{watchlist_id}` | `UnifiedResponse[WatchlistResponse]` | 1 | yes |
| `update_watchlist` | `PUT /api/v1/monitoring/watchlists/{watchlist_id}` | `UnifiedResponse[WatchlistResponse]` | 0 | no |
| `delete_watchlist` | `DELETE /api/v1/monitoring/watchlists/{watchlist_id}` | `UnifiedResponse[None]` | 1 | yes |
| `add_stock_to_watchlist` | `POST /api/v1/monitoring/watchlists/{watchlist_id}/stocks` | `UnifiedResponse[WatchlistStockResponse]` | 1 | yes |
| `list_watchlist_stocks` | `GET /api/v1/monitoring/watchlists/{watchlist_id}/stocks` | `UnifiedResponse[List[WatchlistStockResponse]]` | 1 | yes |
| `remove_stock_from_watchlist` | `DELETE /api/v1/monitoring/watchlists/{watchlist_id}/stocks/{stock_code}` | `UnifiedResponse[None]` | 1 | yes |

`add_stock_to_watchlist` imports `StockToAdd` from the same infrastructure
module. G2.256 must preserve that model import/use while moving only the
`get_postgres_async()` lookup behind the provider.

## Residual Context

G2.254 closed `monitoring_analysis.py` route-body use and selected this file as
the next bounded route-consumer candidate.

Current `get_postgres_async()` residuals in `web/backend/app/api`:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Select for this no-source authorization |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Defer |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Defer |
| `web/backend/app/api/monitoring_analysis.py` | 1 | Retained route-local provider seam after G2.253 |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 1 | Retained route-local provider seam after G2.250 |
| `web/backend/app/api/_data_source_config_responses.py` | 1 | Helper/facade, not route-body consumer |
| `web/backend/app/api/v1/system/settings.py` | 1 | Repository constructor dependency |
| `web/backend/app/api/data_source_config.old.py` | 1 | Legacy `.old` file excluded from active route selection |

## Authorized Future Shape

If this packet is approved and merged, G2.256 may implement:

- a route-local provider in `web/backend/app/api/monitoring_watchlists.py`
- dependency injection parameters for the seven authorized handlers
- focused tests that prove route handlers no longer perform route-body
  `get_postgres_async()` lookup
- focused fallback tests to preserve runtime fallback behavior

Allowed future G2.256 paths:

- `web/backend/app/api/monitoring_watchlists.py`
- `tests/api/file_tests/test_watchlist_api.py`
- `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`

The future implementation must preserve:

- all route paths, methods, summaries, response models, and OpenAPI exposure
- `UnifiedResponse` response contracts
- runtime fallback behavior via `_runtime_fallback_enabled()` and runtime helper
  functions
- `StockToAdd` import/use in `add_stock_to_watchlist`
- established route-local provider pattern from G2.250 and G2.253

## Forbidden For G2.255

G2.255 forbids:

- backend source edits
- test edits
- route or OpenAPI changes
- provider implementation
- `signal_monitoring/*` migration
- `_monitoring_portfolio_router.py`, `monitoring_analysis.py`,
  `_data_source_config_responses.py`, or `v1/system/settings.py` changes
- infrastructure/provider reset changes
- frontend, config, scripts, PM2, OpenSpec, or FUNCTION_TREE changes

## Future G2.256 Gates

Before any source edit in G2.256:

1. Re-run GitNexus impact/context for `monitoring_watchlists.py` route handlers.
2. Stop if GitNexus reports HIGH or CRITICAL risk.
3. Add or update a focused red test proving route-body lookup still exists.
4. Implement only the route-local provider seam and handler dependency
   parameters.
5. Run focused watchlist API and runtime fallback tests.
6. Run ruff on touched source/test files.
7. Run app/OpenAPI smoke and preserve `548` routes / `500` paths unless a
   separately approved route/OpenAPI change exists.
8. Run `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`.
9. Run GitNexus detect_changes before commit.

## Verification

| Check | Result |
|---|---|
| Focused tests | `28 passed` for `tests/api/file_tests/test_watchlist_api.py` and `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py` |
| Candidate source ruff | `ruff check web/backend/app/api/monitoring_watchlists.py` passed |
| Full future touched-set ruff | Existing `PT018` remains in `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`; do not treat as G2.255 source authority |
| App/OpenAPI smoke | `548` routes, `500` paths, `8` watchlist routes with non-sensitive placeholder required env vars |
| OpenSpec validate | `migrate-backend-singletons-to-lifecycle-di` valid; PostHog telemetry emitted ECONNREFUSED noise |
| Git status | Clean before authoring governance files |

During the broad ruff probe, ruff attempted one safe-fix in
`tests/api/file_tests/test_watchlist_api.py`. That tool side effect was restored
before this no-source package was authored.

## GitNexus Gate

GitNexus MCP degraded during this package:

- MCP `impact` / `context`: transport closed
- CLI `context`: resolved
  `Function:web/backend/app/api/monitoring_watchlists.py:create_watchlist`
- CLI `impact`: ambiguous / `UNKNOWN` because the CLI impact command does not
  accept file-path or UID disambiguation

Because G2.255 is no-source, this does not authorize bypassing GitNexus for the
future implementation. G2.256 must rerun GitNexus impact before editing and stop
on HIGH or CRITICAL risk.

## Decision

Recommended review decision: approve G2.255 as a no-source authorization packet
for a future G2.256 path-limited implementation.

Do not migrate `signal_monitoring/*`, route-adjacent helpers, infrastructure,
frontend, config, scripts, OpenSpec, PM2 state, or broader route consumers from
this packet.
