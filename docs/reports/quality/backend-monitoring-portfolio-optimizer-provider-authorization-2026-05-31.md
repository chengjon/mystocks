# Backend Monitoring Portfolio Optimizer Provider Authorization - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.268`
- Branch: `g2-268-monitoring-portfolio-optimizer-provider-authorization`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `772e4a3ac8e05edaa243d660d67c7e5df18158f9`
- Parent PR: `#420`, merged at `772e4a3ac8e05edaa243d660d67c7e5df18158f9`
- Source edit authority in this PR: none

Boundary note: this report is a no-source authorization package. It does not
modify backend source, route registration, OpenAPI artifacts, tests, frontend,
config, scripts, OpenSpec state, PM2 state, or runtime state.

## Candidate

G2.267 selected the concentrated active route-body candidate:

| Item | Evidence |
|---|---|
| Definition | `src/monitoring/domain/portfolio_optimizer.py:383` defines `get_portfolio_optimizer(...)` |
| Active route call sites | `web/backend/app/api/_monitoring_portfolio_router.py:171`, `:239`, `:309` |
| Active target handlers | `get_portfolio_summary`, `get_portfolio_alerts`, `get_rebalance_suggestions` |
| Current target module route count | 3 |
| Source authority in G2.268 | none |

The selected route handlers map to:

| Handler | Method | Path | Current acquisition |
|---|---|---|---|
| `get_portfolio_summary` | `GET` | `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary` | direct route-body `get_portfolio_optimizer()` |
| `get_portfolio_alerts` | `GET` | `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts` | direct route-body `get_portfolio_optimizer()` |
| `get_rebalance_suggestions` | `GET` | `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance` | direct route-body `get_portfolio_optimizer()` |

## Runtime / OpenAPI Evidence

`app.main` imported successfully in a subprocess with the local runtime
environment injected. Secrets were not written to repository artifacts.

Current snapshot:

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |
| `_monitoring_portfolio_router.py` active routes | 3 |

OpenAPI currently contains four portfolio-analysis paths. Three belong to the
selected `_monitoring_portfolio_router.py` target and one belongs to
`app.api.monitoring_analysis::analyze_portfolio`:

| Path | Handling |
|---|---|
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}` | Related non-target route; not part of the future G2.269 source lane |
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary` | Selected target |
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts` | Selected target |
| `/api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance` | Selected target |

## Existing Test Anchors

G2.268 does not edit tests. It records the test anchors that a future source lane
must use or extend:

| Test artifact | Current relevance |
|---|---|
| `tests/api/file_tests/test_monitoring_analysis_api.py` | Existing file-level provider-pattern checks for monitoring calculator and postgres async providers; portfolio endpoint file tests exist for summary, alerts, and rebalance |
| `web/backend/tests/test_health_route_conflicts.py` | OpenAPI/parameter guard covers the three selected portfolio paths |

A future implementation should add or update focused file-level checks proving
that the three selected route handlers no longer call `get_portfolio_optimizer()`
directly and instead acquire it through a route-local dependency provider.

## GitNexus Result

GitNexus MCP was retried for G2.268:

| Query | Result |
|---|---|
| `context(get_portfolio_optimizer)` | tool call failed: `Transport closed` |
| `impact(get_portfolio_optimizer)` | tool call failed: `Transport closed` |
| `npx gitnexus verify-staged ... --json` | exit `0`; `0` changed symbols; `0` affected processes; index stale from `41c18309a555` to `772e4a3ac8e0` |

G2.267 had already recorded `context` and `impact` timeouts after 120 seconds.
Because GitNexus did not return a blast radius, this PR must stay no-source.
A future G2.269 source lane must retry GitNexus context/impact, or record a
GitNexus CLI fallback failure, before editing.

## Authorization Decision

G2.268 authorizes only the next gate, after this PR is accepted:

`G2.269 path-limited monitoring portfolio optimizer route provider implementation`

Future G2.269 allowed paths:

- `web/backend/app/api/_monitoring_portfolio_router.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`
- `web/backend/tests/test_health_route_conflicts.py`

Future G2.269 required acceptance:

- Three selected route handlers acquire the optimizer through a route-local
  FastAPI dependency provider.
- Route/OpenAPI path, method, parameter, response, and operationId contracts
  remain unchanged.
- No source edits occur outside `web/backend/app/api/_monitoring_portfolio_router.py`.
- Focused tests prove direct route-body `get_portfolio_optimizer()` calls are
  removed.
- The health route conflict/OpenAPI parameter guard remains green.

## Non-Goals

G2.268 does not authorize:

- editing `src/monitoring/domain/portfolio_optimizer.py`
- editing non-target backend API files
- route registration or path changes
- OpenAPI artifact edits
- docs/api cleanup
- frontend, config, script, or OpenSpec edits
- PM2 or other stateful runtime gates

## Rollback

Revert the future PR carrying this report and steward updates. No runtime code,
route registration, provider binding, test contract, docs/api artifact, frontend
state, database state, or OpenSpec state is changed by G2.268.
