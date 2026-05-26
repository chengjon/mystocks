# Backend Unused IntegratedServices Facade Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Implementation prepared for review.

This implementation follows the accepted G2.135 authorization boundary. It removes only six unused IntegratedServices service-facade getters from `web/backend/app/services/__init__.py` and adds one focused regression test file.

## Parent Authorization

| Field | Value |
|---|---|
| Parent PR | `#288` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-26T04:24:06Z` |
| Parent merge commit | `4aaa5a88eafa6d43df383a083c15642e88205e4d` |
| Parent title | `G2.135 Authorize unused IntegratedServices facade getter retirement` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/288` |

## Source Changes

Changed runtime file:

- `web/backend/app/services/__init__.py`

Added focused test:

- `web/backend/tests/test_integrated_services_facade_getter_retirement.py`

Removed only these authorized facade getters:

- `get_trading_data_service`
- `get_analysis_data_service`
- `get_data_api_service`
- `get_database_service`
- `get_websocket_service`
- `get_cache_service`

Preserved locked facade getters:

- `get_integrated_services`
- `get_market_data_service`
- `get_risk_calculator`
- `get_risk_monitoring`
- `get_risk_alerts`
- `get_risk_settings`
- `get_risk_dashboard`

The implementation also adds `TYPE_CHECKING`-only imports for retained annotations and removes the runtime `RiskProfile` import from `IntegratedServices.__init__`, which keeps Ruff F821/F401 checks clean without changing runtime construction.

## Pre-Edit GitNexus Impact

| Symbol | Risk | Impacted | Direct | Processes |
|---|---|---:|---:|---:|
| `get_trading_data_service` | LOW | `0` | `0` | `0` |
| `get_analysis_data_service` | LOW | `0` | `0` | `0` |
| `get_data_api_service` | LOW | `0` | `0` | `0` |
| `get_database_service` | LOW | `0` | `0` | `0` |
| `get_websocket_service` | LOW | `0` | `0` | `0` |
| `get_cache_service` | LOW | `0` | `0` | `0` |

## TDD Evidence

| Phase | Result |
|---|---|
| Red | `1 failed, 1 passed`; failure confirmed `get_trading_data_service` still existed on `app.services` |
| Green | `2 passed in 0.28s` |

## Exact Scan

| Removed symbol | Definition count |
|---|---:|
| `get_trading_data_service` | `0` |
| `get_analysis_data_service` | `0` |
| `get_data_api_service` | `0` |
| `get_database_service` | `0` |
| `get_websocket_service` | `0` |
| `get_cache_service` | `0` |

| Locked symbol | Definition count |
|---|---:|
| `get_integrated_services` | `1` |
| `get_market_data_service` | `1` |
| `get_risk_calculator` | `1` |
| `get_risk_monitoring` | `1` |
| `get_risk_alerts` | `1` |
| `get_risk_settings` | `1` |
| `get_risk_dashboard` | `1` |

## Verification

| Gate | Result |
|---|---|
| Focused tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_integrated_services_facade_getter_retirement.py -q --no-cov --tb=short` -> `2 passed in 0.28s` |
| Import smoke | `{'removed_absent': True, 'locked_callable': True}` |
| Ruff | `All checks passed` |
| Black | `2 files would be left unchanged` |
| Staged GitNexus | Risk `low`, changed files `6`, changed symbols `20`, affected count `0`, affected processes `0` |

## Boundary

No route/API files, OpenAPI exposure, PM2 workflow, frontend files, OpenSpec changes, GitHub issue labels, `get_integrated_services`, `get_market_data_service`, risk helper facades, or HIGH/CRITICAL service getters were changed.
