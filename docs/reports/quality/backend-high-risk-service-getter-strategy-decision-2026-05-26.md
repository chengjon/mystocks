# Backend High-Risk Service Getter Strategy Decision

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Date: 2026-05-26

Workline: G2.143 high-risk service getter strategy decision package

Boundary: this is a design-decision package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize implementation.

## Purpose

G2.142 closed the low-risk queue: after BacktestEngine retirement, there are no remaining zero-external-reference service getter definitions. The remaining service getter work is no longer a cleanup queue. It is a set of active runtime seams that must be split into smaller decision tracks before any source implementation lane is opened.

This package records that strategy split.

## Input Baseline

| Evidence | Value |
|---|---|
| Parent task | G2.142 Service lifecycle candidate refresh after BacktestEngine |
| Parent PR | #295 |
| Parent merge commit | `c11dfb858200aaed46beee50c15e022c86408b54` |
| Parent evidence | `docs/reports/quality/backend-service-lifecycle-candidate-refresh-after-backtest-2026-05-26.md` |
| Current HEAD checked for this package | `c11dfb858200aaed46beee50c15e022c86408b54` |
| Service Python files | 152 |
| Backend app Python files | 575 |
| Backend API Python files | 219 |
| Backend test Python files | 206 |
| `def get_*` definitions under services | 53 |
| Zero-external-reference getter definitions | 0 |

## Decision

No direct source implementation lane should be opened from G2.142.

The remaining high-risk getter work is split into six tracks:

1. Dashboard/TDX runtime seam.
2. Indicator/Data service seam.
3. Strategy adapter seam.
4. Realtime streaming/socket seam.
5. Root facade compatibility seam.
6. Route dependency/provider governance seam.

Only the first four are possible future implementation families. The root facade and dependency/provider tracks are locked governance surfaces unless a later compatibility or route-contract decision package explicitly unlocks them.

## Track Matrix

| Track | Primary getter/surface | Risk | Impact | Disposition |
|---|---|---:|---:|---|
| Dashboard/TDX | `get_tdx_service` | CRITICAL | impacted 6, direct 2, processes 5 | Hold for a dedicated Dashboard/TDX design and authorization package |
| Indicator/Data | `get_data_service` | CRITICAL | impacted 5, direct 3, processes 7 | Hold for a dedicated Indicator/Data design and authorization package |
| Strategy adapter | `get_strategy_service` | CRITICAL | impacted 13, direct 6, processes 0 | Hold for a dedicated Strategy adapter design and authorization package |
| Realtime streaming/socket | `get_streaming_service` | HIGH | impacted 9, direct 9, processes 0 | Recommended first downstream design track; not source-authorized here |
| Root facade compatibility | `web/backend/app/services/__init__.py` getters | locked | active references | Not a cleanup candidate without a compatibility-retirement decision record |
| Route dependency/provider governance | FastAPI dependency/provider getters | locked | active references | Not a singleton-retirement candidate; treat as route dependency contract |

## Track Details

### Dashboard/TDX Runtime Seam

`get_tdx_service` is CRITICAL. GitNexus reports impacted count 6, direct callers 2, and affected processes 5.

Direct callers:

- `web/backend/app/api/dashboard_data_source.py::_get_major_index_quotes`
- `web/backend/app/api/dashboard_data_source.py::_get_tdx_live_market_snapshot`

Required before any source lane:

- Dashboard consumer contract matrix.
- TDX unavailable/fallback behavior contract.
- Focused dashboard route tests or smoke.
- Route/OpenAPI drift check if route dependency surfaces change.
- Fresh GitNexus impact before editing.

### Indicator/Data Service Seam

`get_data_service` is CRITICAL. GitNexus reports impacted count 5, direct callers 3, and affected processes 7.

Direct callers:

- `web/backend/app/api/indicators/indicator_cache.py::calculate_indicators`
- `web/backend/app/api/indicators/indicator_cache.py::_calculate_single_indicator`
- `web/backend/app/api/v1/strategy/indicators.py::get_technical_indicators`

Required before any source lane:

- Indicator input/output contract matrix.
- Strategy indicator consumer parity check.
- Focused indicator cache tests.
- OpenAPI examples review if response contracts are touched.
- Fresh GitNexus impact before editing.

### Strategy Adapter Seam

`get_strategy_service` is CRITICAL. GitNexus reports impacted count 13, direct callers 6, and affected processes 0. The impact crosses adapters, data adapters, strategy management, and backtest tasks.

Direct callers:

- `web/backend/app/services/data_adapters/strategy.py::_get_strategy_service`
- `web/backend/app/services/adapters/strategy_adapter.py::_get_strategy_service`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py::query_strategy_results`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py::get_matched_stocks`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py::get_strategy_summary`
- `web/backend/app/tasks/backtest_tasks.py::_resolve_backtest_data_source`

Required before any source lane:

- Adapter wrapper ownership decision.
- Strategy execution router consumer matrix.
- Backtest task fallback contract.
- Strategy adapter health-check tests.
- Fresh GitNexus impact before editing.

### Realtime Streaming/Socket Seam

`get_streaming_service` is HIGH. GitNexus reports impacted count 9, direct callers 9, and affected processes 0.

Direct callers are concentrated in:

- `web/backend/app/services/aggregation_streaming_bridge.py`
- `web/backend/app/core/socketio_manager.py`

This is the preferred first downstream design track because it is HIGH rather than CRITICAL and has no process-flow participation in the current GitNexus evidence. It is not safe to implement directly from this package because it touches Socket.IO lifecycle and stream subscription behavior.

Required before any source lane:

- Socket.IO lifecycle behavior matrix.
- Stream subscription/unsubscription contract.
- Streaming bridge ownership decision.
- Focused socket/streaming tests or import-safe test double plan.
- Fresh GitNexus impact before editing.

### Root Facade Compatibility Seam

The following root package facades remain active compatibility surfaces in `web/backend/app/services/__init__.py`:

| Getter | Current token count |
|---|---:|
| `get_integrated_services` | 10 |
| `get_risk_calculator` | 2 |
| `get_market_data_service` | 19 |
| `get_risk_monitoring` | 2 |
| `get_risk_alerts` | 2 |
| `get_risk_settings` | 3 |
| `get_risk_dashboard` | 3 |

Disposition: locked. Do not classify these as unused getter debt. Any future retirement requires a compatibility-retirement decision record with import consumers, replacement paths, tests, and rollback plan.

### Route Dependency/Provider Governance Seam

The following FastAPI dependency/provider getters are active route dependency contracts:

| Provider | Current token count |
|---|---:|
| `get_market_data_service_v2_dependency` | 18 |
| `get_market_data_service_dependency` | 16 |
| `get_indicator_registry_dependency` | 5 |
| `get_tdx_service_dependency` | 9 |
| `get_announcement_service_dependency` | 15 |
| `get_email_service_dependency` | 12 |
| `get_watchlist_service_dependency` | 12 |
| `get_stock_search_service_dependency` | 14 |
| `get_tradingview_service_dependency` | 11 |

Disposition: locked. Treat these as route dependency/provider contracts, not singleton-retirement candidates. Any change here requires route-level dependency override tests and OpenAPI drift review where the public contract can change.

## Recommended Sequence

1. Review and accept or revise this G2.143 strategy package.
2. If accepted, open G2.144 as a Realtime streaming/socket authorization package.
3. Keep G2.144 source-closed until it defines exact files, tests, rollback, and fresh impact evidence.
4. Only after G2.144 is explicitly approved should a narrow source implementation lane be opened.
5. Handle Dashboard/TDX, Indicator/Data, and Strategy adapter as separate later tracks, each with its own design and authorization package.

## Blocked Actions

- Do not delete or rename any remaining getter from this package.
- Do not edit backend source or tests under G2.143.
- Do not treat root facade getters as unused functions.
- Do not treat FastAPI dependency/provider getters as singleton-retirement candidates.
- Do not open a source implementation lane until a separate single-track authorization package is approved.

## Verification

Fresh checks performed for this package:

- Current worktree HEAD: `c11dfb858200aaed46beee50c15e022c86408b54`.
- Parent PR #295: `MERGED`, merged at `2026-05-26T05:47:30Z`.
- Scripted inventory: service files 152, backend app files 575, API files 219, backend tests 206, service getter definitions 53, zero-external-reference getters 0.
- GitNexus impact: `get_tdx_service` CRITICAL, impacted 6, direct 2, processes 5.
- GitNexus impact: `get_data_service` CRITICAL, impacted 5, direct 3, processes 7.
- GitNexus impact: `get_strategy_service` CRITICAL, impacted 13, direct 6, processes 0.
- GitNexus impact: `get_streaming_service` HIGH, impacted 9, direct 9, processes 0.

## Non-Goals

- No backend source or test edits.
- No implementation authorization.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label changes.
- No selection of a concrete source lane beyond recommending the next design track.
- No compatibility facade or provider getter retirement.
