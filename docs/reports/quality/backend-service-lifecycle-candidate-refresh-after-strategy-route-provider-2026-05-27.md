# Backend Service Lifecycle Candidate Refresh After Strategy Route Provider

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Ready for review

Scope: G2.167 governance-only candidate refresh after G2.166.

Boundary: this is an inventory refresh and routing package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize implementation.

Parent: G2.166, PR `#319`, merged as `03cff1a688337a170801add2dea52050b9bbea44`.

Current HEAD: `03cff1a688337a170801add2dea52050b9bbea44`.

Prepared at: `2026-05-27T08:58:04+08:00`.

## Purpose

Refresh the remaining service lifecycle getter/provider inventory after the Strategy route provider injection closed the route-handler body-call slice.

This refresh is intentionally not a source implementation plan. Its job is to record the new baseline, separate static route closure from remaining graph risk, and route the next step back through a decision package.

## Parent Verification

| Check | Result |
|---|---|
| PR `#319` state | `MERGED`, merge commit `03cff1a688337a170801add2dea52050b9bbea44` |
| `test_strategy_management_route_provider.py` | `5 passed in 3.32s` |
| Strategy route OpenAPI docs focused test | `1 passed in 12.57s` |
| OpenAPI smoke with non-secret minimal env | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `total_warnings_captured=121` |

The OpenAPI smoke reports duplicate-operation-id warnings separately from all captured warnings. The broader warning count includes unrelated import-time/runtime dependency warnings and is not treated as an operationId regression.

## Strategy Route Provider Closure

G2.166 changed the Strategy route surface from direct route-handler body calls to a local FastAPI dependency provider.

| Surface | Current state |
|---|---|
| Route-handler body calls to `get_strategy_service()` in `query_strategy_results` | 0 |
| Route-handler body calls to `get_strategy_service()` in `get_matched_stocks` | 0 |
| Route-handler body calls to `get_strategy_service()` in `get_strategy_summary` | 0 |
| Route-local provider fallback calls | 1, `get_strategy_service_dependency()` delegates to public `get_strategy_service()` |
| `Depends(get_strategy_service_dependency)` sites | 3 |
| Public `get_strategy_service()` fallback compatibility | preserved |

GitNexus still reports `query_strategy_results`, `get_matched_stocks`, and `get_strategy_summary` as direct upstream callers of `get_strategy_service`. That signal now reflects provider-mediated route participation in the graph, not direct body-call debt in the route handlers. For closure, use the static route-handler body-call count; for blast radius, keep the GitNexus CRITICAL risk signal.

## Remaining Strategy Surfaces

| Surface | Current call site | Interpretation |
|---|---|---|
| Route provider fallback | `web/backend/app/api/strategy_management/_strategy_execution_router.py:34` | Deliberate compatibility fallback introduced by G2.166. |
| Adapter/provider duplication | `web/backend/app/services/adapters/strategy_adapter.py:45` | Deferred adapter lane; should not be changed from a route-provider package. |
| Adapter/provider duplication | `web/backend/app/services/data_adapters/strategy.py:42` | Deferred adapter lane; should not be changed from a route-provider package. |
| Backtest task resolver | `web/backend/app/tasks/backtest_tasks.py:31` | Separate task/runtime contract lane; should not be bundled with adapter cleanup. |

## Refreshed High-Risk Getter Matrix

| Getter | GitNexus risk | Impacted | Direct | Processes | Static surface | Current interpretation |
|---|---:|---:|---:|---:|---|---|
| `get_strategy_service` | CRITICAL | 13 | 6 | 0 | 4 non-definition calls across route provider, two adapter modules, and backtest task resolver | Route-handler body debt closed; remaining residual must be split into adapter/provider duplication and backtest task resolution before source work. |
| `get_data_service` | CRITICAL | 5 | 3 | 7 | Provider-governed Indicator/Data seam plus tests | Indicator/Data route body debt already closed; keep as runtime-flow risk, not the next immediate source lane. |
| `get_streaming_service` | HIGH | 9 | 9 | 0 | Realtime/socket manager and streaming bridge | Realtime/socket lifecycle track remains separate. |
| `get_tdx_service` | CRITICAL | 6 | 2 | 5 | Dashboard/TDX service seam | Dashboard/TDX residual remains separate. |

## Token Surface

The following token counts cover `web/backend/app/api`, `web/backend/app/services`, `web/backend/app/tasks`, and `web/backend/app/core`; backend tests are excluded from this table.

| Token | Count | Files |
|---|---:|---:|
| `get_data_service` | 5 | 3 |
| `get_strategy_service` | 9 | 5 |
| `get_streaming_service` | 5 | 3 |
| `get_tdx_service` | 4 | 2 |
| `get_market_data_service` | 2 | 2 |
| `get_market_data_service_v2_dependency` | 17 | 3 |
| `get_indicator_data_service` | 3 | 1 |
| `get_strategy_indicator_data_service` | 2 | 1 |
| `get_indicator_registry_dependency` | 4 | 2 |

Token counts are navigation aids, not deletion queues. Business query helpers and compatibility providers must be classified by track before any source edit.

## Current Static Scan Notes

| Metric | Count |
|---|---:|
| Service Python files | 152 |
| API Python files | 219 |
| Backend test Python files | 208 |
| Top-level `def get_*` definitions under `web/backend/app/services` | 53 |
| Root facade getters in `web/backend/app/services/__init__.py` | 7 |
| Top-level API `def get_*` helpers/providers | 33 |
| API `Depends(get_*)` sites | 374 |

These broad counts are intentionally retained as rough trend signals only. They must not be used to infer singleton debt without per-symbol classification.

## Decision

No new source implementation lane is selected by G2.167.

Recommended next gate: G2.168 decision-only Strategy residual split package.

G2.168 should decide how to split the remaining `get_strategy_service` residual into separate tracks before any code is edited:

1. Strategy adapter/provider duplication: `web/backend/app/services/adapters/strategy_adapter.py` and `web/backend/app/services/data_adapters/strategy.py`.
2. Backtest task data-source resolution: `web/backend/app/tasks/backtest_tasks.py`.

The adapter/provider duplication and backtest task resolver should not be implemented in the same source PR unless a later reviewed authorization package explicitly proves shared tests, rollback, and runtime boundaries.

## Next Gate

Review this package. If accepted, start G2.168 as a decision-only Strategy residual track-split package. Do not start another source implementation lane directly from this refresh.
