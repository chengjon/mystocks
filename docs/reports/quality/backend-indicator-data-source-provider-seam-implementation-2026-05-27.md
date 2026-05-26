# Backend Indicator/Data Source Provider Seam Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Ready for review

Scope: G2.162 narrow source implementation lane.

Boundary: this package changes only the authorized Indicator/Data consumer files, focused tests, and governance records. It does not edit `web/backend/app/services/data_service.py`, delete or privatize `get_data_service()`, change route paths, change OpenAPI exposure, edit frontend code, edit PM2 workflows, change OpenSpec state, or change GitHub issue labels.

Parent: G2.161, PR `#314`, merged as `9d31aec75dadf4e90cc438f342cdbe3c3778875b`.

Current HEAD before implementation: `9d31aec75dadf4e90cc438f342cdbe3c3778875b`.

Prepared at: `2026-05-27T01:41:49+08:00`.

## Decision

Implement the Indicator/Data source provider seam now authorized by G2.161.

The implementation replaces the three direct application-body `get_data_service()` calls in Indicator/Data consumers with consumer-local FastAPI dependency provider seams:

- `get_indicator_data_service()` in `web/backend/app/api/indicators/indicator_cache.py`
- `get_strategy_indicator_data_service()` in `web/backend/app/api/v1/strategy/indicators.py`

The public service getter remains available as the fallback used by those providers.

## Changed Source

| File | Change |
|---|---|
| `web/backend/app/api/indicators/indicator_cache.py` | Adds `get_indicator_data_service()`, injects `data_service` into `calculate_indicators` and `calculate_indicators_batch`, and passes that service into `_calculate_single_indicator`. |
| `web/backend/app/api/v1/strategy/indicators.py` | Adds `get_strategy_indicator_data_service()`, injects `data_service` into `get_technical_indicators`, and uses the injected service for `get_daily_ohlcv`. |
| `web/backend/tests/test_indicator_registry_route_provider.py` | Adds a route-provider guard asserting the calculation handlers expose the Indicator/Data data-service dependency. |
| `web/backend/tests/test_v1_indicators_regressions.py` | Converts direct v1 tests from monkeypatching the root getter to explicit fake-service injection, and adds a provider-dependency signature guard. |

## GitNexus Evidence

Pre-edit impact at current index:

| Symbol | Risk | Impacted | Direct callers | Processes |
|---|---:|---:|---:|---:|
| `get_data_service` | CRITICAL | 5 | 3 | 7 |
| `calculate_indicators` | LOW | 0 | 0 | 0 |
| `_calculate_single_indicator` | LOW | 3 | 1 | 0 |
| `get_technical_indicators` | LOW via exact context; direct impact lookup is ambiguous without uid | 0 incoming callers in symbol context | 0 | participates in 5 v1 strategy indicator processes |

`get_data_service` d1 callers before implementation:

- `indicator_cache.py::calculate_indicators`
- `indicator_cache.py::_calculate_single_indicator`
- `v1/strategy/indicators.py::get_technical_indicators`

## TDD Evidence

Red:

| Check | Expected failure |
|---|---|
| `test_v1_indicators_regressions.py` | `3 failed`: route did not accept `data_service`, and `get_strategy_indicator_data_service` was absent. |
| `test_indicator_registry_route_provider.py` | `1 failed, 2 passed`: `get_indicator_data_service` was absent. |

Green:

| Check | Result |
|---|---|
| `test_v1_indicators_regressions.py` | `3 passed in 1.53s` |
| `test_indicator_registry_route_provider.py` | `3 passed in 1.86s` |

## Static Closure

Before G2.162:

- Application body `get_data_service()` calls: `3`
- Direct sites:
  - `indicator_cache.py:343`
  - `indicator_cache.py:613`
  - `v1/strategy/indicators.py:201`

After G2.162:

- Application route/helper body `get_data_service()` calls: `0`
- Remaining `get_data_service()` calls are provider fallback bodies only:
  - `indicator_cache.py:get_indicator_data_service`
  - `v1/strategy/indicators.py:get_strategy_indicator_data_service`
- Import sites remain because the provider seams intentionally preserve the public service getter fallback.

## Verification

| Check | Result |
|---|---|
| `test_v1_indicators_regressions.py` | `3 passed in 1.53s` |
| `test_indicator_registry_route_provider.py` | `3 passed in 1.86s` |
| `test_health_route_conflicts.py --collect-only` | `120 tests collected in 13.74s` |
| `test_health_route_conflicts.py::test_v1_indicator_endpoints_have_examples_parameter_docs_and_descriptions` | `1 passed in 13.06s` |
| `ruff check` for touched backend source/tests | `All checks passed!` |
| OpenAPI smoke with non-secret minimal env | `routes=548`, `paths=500`, `duplicate_operation_ids=0` |
| Staged GitNexus detect-changes | `risk_level=high`, `changed_files=8`, `changed_symbols=23`, `affected_processes=7` |

OpenAPI smoke used dummy non-secret startup values for required environment variables. It did not read or disclose local secrets.

The staged GitNexus risk is expected for this lane because `get_data_service` was pre-classified as a CRITICAL seam. The affected processes remain the Indicator/Data and v1 strategy indicator processes recorded before implementation:

- `Calculate_indicators -> Warning`
- `Calculate_indicators -> _dataframe_to_ohlcv_arrays`
- `Get_technical_indicators -> Strip`
- `Get_technical_indicators -> ShouldAlwaysSelectNothing`
- `Get_technical_indicators -> ImplForWrapper`
- `Get_technical_indicators -> GetAttributeNS`
- `Get_technical_indicators -> _locationObjectNavigate`

## Rollback

Rollback is a normal PR revert. The public `get_data_service()` function is preserved, so reverting this implementation restores previous direct consumer calls without a compatibility restoration project.

## Next Gate

Review this package. If accepted, merge G2.162 and refresh the high-risk service getter inventory before selecting the next track. Do not start another source implementation lane directly from this package.
