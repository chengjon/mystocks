# G2.261 Get Signal Statistics Route-Registration / Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-05-31T09:48:19+08:00`
- Branch: `g2-261-get-signal-statistics-route-ownership`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `efc579ad8558314568b6f03e97f1c12341105fa0`
- Parent closeout: G2.260, PR `#413`, merged at `efc579ad8558314568b6f03e97f1c12341105fa0`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: this report is a no-source route-registration / ownership
decision package. It does not authorize source edits, route registration,
OpenAPI changes, docs/api changes, test edits, frontend/config/script edits,
PM2 commands, or OpenSpec source/spec edits.

## Question

G2.260 closed the active app-route body `get_postgres_async()` queue. The only
remaining signal-monitoring item was
`web/backend/app/api/signal_monitoring/get_signal_statistics.py`, which looked
route-shaped but was not registered by `app.main`.

G2.261 answers one question:

Should `get_signal_statistics.py` be treated as an active route/provider
implementation candidate now?

Answer: no. It is a dormant route module / route ownership gap, not an active
route-body provider residual.

## Evidence

Candidate file:

| Evidence | Result |
|---|---:|
| File | `web/backend/app/api/signal_monitoring/get_signal_statistics.py` |
| Lines | 511 |
| Module-local `APIRouter` | `true` |
| Decorated route handlers | 3 |
| Direct `get_postgres_async()` calls in decorated handlers | 3 |
| Registered app routes from this file | 0 |
| `app.routes` | 548 |
| OpenAPI paths | 500 |

Decorated handlers:

| Handler | Decorator | Direct calls |
|---|---|---:|
| `get_signal_statistics` | `router.get('/signals/statistics', response_model=List[SignalStatisticsResponse])` | 1 |
| `get_active_signals` | `router.get('/signals/active', response_model=ActiveSignalsResponse)` | 1 |
| `get_strategy_detailed_health` | `router.get('/strategies/{strategy_id}/health/detailed', response_model=StrategyDetailedHealthResponse)` | 1 |

Runtime smoke:

| Path | Status |
|---|---:|
| `/api/signals/statistics` | 404 |
| `/api/signals/active` | 404 |
| `/api/strategies/test_strategy/health/detailed` | 404 |

Registration root cause:

- `web/backend/app/api/signal_monitoring/__init__.py` exports `router` from
  `signal_history_response.py`.
- The same package imports the three functions from `get_signal_statistics.py`.
- Importing those functions does not register the module-local router owned by
  `get_signal_statistics.py`.
- Therefore the file contains route decorators, but its router is not attached
  to the runtime app.

## Consumer Matrix

Exact consumer/documentation references:

| Path | Total references | Docs | Tests | Exact frontend refs |
|---|---:|---:|---:|---:|
| `/api/signals/statistics` | 18 | 17 | 1 | 0 |
| `/api/signals/active` | 14 | 13 | 1 | 0 |
| `/api/strategies/{strategy_id}/health/detailed` | 2 | 2 | 0 | 0 |

Important notes:

- `docs/api/openapi.yaml` contains historical entries for
  `/api/signals/statistics` and `/api/signals/active`, but current
  `app.openapi()` does not expose them.
- `tests/unit/test_signal_monitoring_integration.py` references
  `/api/signals/active`.
- Broad `health/detailed` references exist across docs/frontend/tests, but those
  are generic health surfaces and not exact references to
  `/api/strategies/{strategy_id}/health/detailed`.
- `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md` marks the
  signal statistics API endpoint family as unavailable.

## Decision

Classification:

- dormant route module / route ownership gap

G2.261 does not authorize provider injection. Provider injection is premature
because the runtime route and OpenAPI ownership are unresolved.

The active app-route body `get_postgres_async()` queue remains closed. The three
direct calls in `get_signal_statistics.py` are not active route-body residuals
at current HEAD.

## Allowed Future Options

A later approved lane may choose one of these outcomes:

- register the router and expose the endpoints with route/OpenAPI contract
  evidence, then migrate provider acquisition
- keep the module dormant and mark docs/tests as historical or deferred
- retire/archive the dormant module and stale docs/tests if product ownership
  rejects the surface

G2.261 does not choose implementation. It only blocks direct source work until a
route/OpenAPI reconciliation authorization exists.

## Tooling Notes

GitNexus staged check:

- MCP `detect_changes` failed with `Transport closed`.
- CLI fallback `npx gitnexus verify-staged ... --json` returned `ok=true`,
  `risk_level=low`, `changed_count=0`, `affected_count=0`, `changed_files=9`.
- CLI result carried a stale-index warning:
  `current_commit_differs_from_indexed_commit`.

Validation:

- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`:
  valid
- Markdown governance gate: 6 checked files, 0 errors
- Mainline scope gate: `pass=True`, problem count `0`, changed files `9`

## Next Gate

Start G2.262 as a no-source route/OpenAPI reconciliation authorization package:

- decide whether `get_signal_statistics.py` should become a registered runtime
  API surface
- reconcile current `app.openapi()` with `docs/api/openapi.yaml` and historical
  docs/test references
- define the exact future source/test/docs scope if implementation is approved
- do not edit source, route registration, OpenAPI, docs/api, tests, frontend,
  config, scripts, PM2, or OpenSpec from G2.262
