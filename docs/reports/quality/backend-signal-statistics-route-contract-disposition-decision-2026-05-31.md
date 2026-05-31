# G2.263 Signal Statistics Route Contract Disposition Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review input
- Prepared at: `2026-05-31T10:26:58+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `15bebd4de48059fb5bf35efef81aabb9040cf6ea`
- Parent: G2.262 / PR `#415` merged at `15bebd4de48059fb5bf35efef81aabb9040cf6ea`
- Scope: no-source route contract disposition decision for `web/backend/app/api/signal_monitoring/get_signal_statistics.py`

Boundary note: this document records a governance disposition only. It does not authorize source edits, route registration, provider injection, docs/api edits, test edits, OpenSpec changes, PM2 commands, or PR merges.

## Executive Decision

G2.263 selects: **retain dormant source and reconcile stale contract artifacts**.

Do not register the three dormant signal-statistics routes now. Do not retire `web/backend/app/api/signal_monitoring/get_signal_statistics.py` now. Do not start provider migration in this module.

The reason is concrete: the target paths have no exact frontend or backend runtime consumers, are absent from current runtime routes, and are absent from current `app.openapi()`. The remaining references are stale or historical contract artifacts in docs/api, design/operations docs, and one unit test file. Registering the routes would expand the public API surface before ownership is proven; deleting the source requires a separate product ownership decision.

## Current Runtime Contract

| Field | Value |
|---|---:|
| Runtime routes | 548 |
| Current `app.openapi()` paths | 500 |
| Duplicate operation IDs | 0 |
| Exact target runtime routes | 0 |
| Exact target OpenAPI paths | 0 |
| Registered routes from target module | 0 |

## Target Module Evidence

| Handler | Decorator line | Decorator | Direct DB calls |
|---|---:|---|---:|
| `get_signal_statistics` | 113 | `@router.get("/signals/statistics", response_model=List[SignalStatisticsResponse])` | 1 |
| `get_active_signals` | 230 | `@router.get("/signals/active", response_model=ActiveSignalsResponse)` | 1 |
| `get_strategy_detailed_health` | 364 | `@router.get("/strategies/{strategy_id}/health/detailed", response_model=StrategyDetailedHealthResponse)` | 1 |

Summary:

- `web/backend/app/api/signal_monitoring/get_signal_statistics.py` contains 3 route-decorated handlers.
- The file contains 3 direct `get_postgres_async()` calls.
- These calls are not active app-route body residuals because the module contributes 0 registered runtime routes.

## Product Consumer Matrix

This matrix excludes governance reports, steward-tree files, generated evidence, and PR task cards so that the numbers represent product/test/documentation references rather than this workline's own audit trail.

| Path | Total refs | docs/api | other docs | tests | frontend | backend |
|---|---:|---:|---:|---:|---:|---:|
| `/api/signals/statistics` | 10 | 2 | 7 | 1 | 0 | 0 |
| `/api/signals/active` | 7 | 2 | 4 | 1 | 0 | 0 |
| `/api/strategies/{strategy_id}/health/detailed` | 0 | 0 | 0 | 0 | 0 | 0 |

Observed artifact categories:

- `docs/api/openapi.yaml` contains stale entries for `/api/signals/statistics` and `/api/signals/active` that are absent from current `app.openapi()`.
- `tests/unit/test_signal_monitoring_integration.py` references the first two signal paths and should be treated as stale or historical until G2.264 proves otherwise.
- `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md` and `docs/api/task_plan_signal_monitoring_phase2_extended.md` are design/planning artifacts, not current runtime truth.
- No exact frontend or backend runtime consumer was found for any target path.

## Disposition

| Option | Decision | Rationale |
|---|---|---|
| Register runtime routes now | Reject | Would add public API surface without active consumer proof or ownership approval. |
| Retire/archive source now | Reject | Source removal needs explicit product ownership and compatibility approval. |
| Keep dormant without follow-up | Reject | Stale docs/api and test artifacts would continue to mislead future agents. |
| Retain dormant source and reconcile stale contract artifacts | Select | Keeps runtime stable while authorizing the next no-source cleanup-planning gate. |

## Next Gate

Start G2.264 as a no-source stale signal statistics contract cleanup authorization package.

G2.264 should decide exact cleanup or annotation scope for these artifacts before any edit happens:

- `docs/api/openapi.yaml`
- `docs/api/task_plan_signal_monitoring_phase2_extended.md`
- `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md`
- `docs/architecture/DESIGN_METHODOLOGY_AND_TOOLCHAIN_ANALYSIS.md`
- `tests/unit/test_signal_monitoring_integration.py`

G2.264 must not register routes, inject providers, retire `web/backend/app/api/signal_monitoring/get_signal_statistics.py`, edit frontend, edit OpenSpec, or run stateful PM2 gates.

## Verification Notes

Planned verification for this PR:

- markdown governance gate on changed Markdown files
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`
- mainline scope gate with this PR task card
- GitNexus detect-changes attempt, with CLI fallback if MCP transport remains unavailable
- `git diff --check`
