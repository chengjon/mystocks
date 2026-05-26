# Backend Service Lifecycle Candidate Refresh After Indicator/Data

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Ready for review

Scope: G2.163 governance-only candidate refresh after G2.162.

Boundary: this is a candidate refresh and routing package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize implementation.

Parent: G2.162, PR `#315`, merged as `c9dc5de905e351c4675ee62201edfa1ce4e7ce97`.

Current HEAD: `c9dc5de905e351c4675ee62201edfa1ce4e7ce97`.

Prepared at: `2026-05-27T01:58:47+08:00`.

## Purpose

Refresh the remaining service lifecycle getter/provider inventory after the Indicator/Data source provider seam implementation closed.

This refresh is intentionally not a source implementation plan. Its job is to record the new baseline, distinguish static closure from remaining graph risk, and route the next step back through a decision package.

## Parent Verification

| Check | Result |
|---|---|
| PR `#315` state | `MERGED`, merge commit `c9dc5de905e351c4675ee62201edfa1ce4e7ce97` |
| `test_v1_indicators_regressions.py` | `3 passed in 1.71s` |
| `test_indicator_registry_route_provider.py` | `3 passed in 2.18s` |
| OpenAPI smoke with non-secret minimal env | `routes=548`, `paths=500`, `duplicate_operation_ids=0` |
| GitNexus analyze | `62,910 nodes`, `146,092 edges`, `3,287 clusters`, `300 flows` |

## Scan Snapshot

| Metric | Count |
|---|---:|
| Service Python files | 152 |
| API Python files | 219 |
| Backend test Python files | 207 |
| Top-level `def get_*` definitions under `web/backend/app/services` | 53 |
| Root facade getters in `web/backend/app/services/__init__.py` | 7 |
| Service dependency/provider getter definitions | 9 |
| Top-level API `def get_*` helpers/providers | 32 |
| API local provider-like getters | 13 |
| API `Depends(get_*)` sites | 371 |
| API non-provider service-getter body call sites | 19 |

The broad `def get_*` count includes business query methods such as stock-search or profile getters. It is not a deletion queue and must not be interpreted as direct singleton debt.

## Indicator/Data Closure

G2.162 changed the Indicator/Data seam from direct body calls to provider fallbacks.

| Surface | Current state |
|---|---|
| Direct application route/helper body `get_data_service()` calls in the G2.162 scope | 0 |
| Remaining `get_data_service()` hits in `indicator_cache.py` | import plus `get_indicator_data_service()` provider fallback |
| Remaining `get_data_service()` hits in `api/v1/strategy/indicators.py` | import plus `get_strategy_indicator_data_service()` provider fallback |
| `get_indicator_data_service` token surface | 4 hits across 2 files |
| `get_strategy_indicator_data_service` token surface | 3 hits across 2 files |

GitNexus still reports `get_data_service` as CRITICAL with `5` impacted symbols, `3` direct callers, and `7` affected processes. This is expected because the provider seam still participates in the same Indicator/Data and v1 strategy indicator execution flows. The static closure metric is therefore the implementation closure signal; the GitNexus risk remains the runtime flow risk signal.

## Refreshed High-Risk Getter Matrix

| Getter | GitNexus risk | Impacted | Direct | Processes | Current interpretation |
|---|---:|---:|---:|---:|---|
| `get_data_service` | CRITICAL | 5 | 3 | 7 | Indicator/Data direct body debt closed; keep as provider-governed runtime seam, not a new immediate source lane. |
| `get_strategy_service` | CRITICAL | 13 | 6 | 0 | Strong next decision candidate; crosses strategy adapters, strategy-management routes, and backtest task resolution. |
| `get_streaming_service` | HIGH | 9 | 9 | 0 | Realtime/socket lifecycle track; should remain separate from strategy adapter work. |
| `get_tdx_service` | CRITICAL | 6 | 2 | 5 | Dashboard/TDX residual graph risk; prior Dashboard/TDX lane closed direct helper debt, so this needs a residual decision packet before source work. |

## Token Surface

| Token | Count | Files |
|---|---:|---:|
| `get_data_service` | 9 | 4 |
| `get_strategy_service` | 10 | 5 |
| `get_streaming_service` | 23 | 5 |
| `get_tdx_service` | 6 | 4 |
| `get_market_data_service` | 19 | 8 |
| `get_market_data_service_v2_dependency` | 18 | 4 |
| `get_indicator_data_service` | 4 | 2 |
| `get_strategy_indicator_data_service` | 3 | 2 |
| `get_indicator_registry_dependency` | 5 | 3 |

## Non-Provider API Body Call Sample

Current API non-provider service-getter body call sites include:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py:399`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py:461`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py:503`
- `web/backend/app/api/dashboard_data_source.py:137`
- `web/backend/app/api/dashboard_data_source.py:247`
- `web/backend/app/api/dashboard_data_source.py:499`
- `web/backend/app/api/dashboard_data_source.py:730`
- `web/backend/app/api/v1/strategy/ml_runtime_helpers.py:59`
- `web/backend/app/api/v1/analysis/backtest.py:338`
- `web/backend/app/api/v1/system/health.py:232`

These are not all the same kind of debt. Some are route-local private helpers, some are dashboard/TDX residuals, and some are strategy-management service calls. They should be split by track before any source edits.

## Decision

No new source implementation lane is selected by G2.163.

Recommended next gate: G2.164 high-risk service getter track selection after Indicator/Data.

G2.164 should be decision-only and choose one next track from the refreshed matrix. The most likely candidates are:

- Strategy adapter / strategy-management `get_strategy_service` decision path.
- Realtime streaming/socket `get_streaming_service` decision path.
- Dashboard/TDX residual `get_tdx_service` decision path.
- Route dependency/provider governance path for private route-local helpers.

## Next Gate

Review this package. If accepted, start G2.164 as a decision-only track-selection package. Do not start another source implementation lane directly from this refresh.
