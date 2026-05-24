# Backend MarketDataService Route Provider Implementation - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为参考。

## Status

Status: review-ready.

Workline: G2.49 `get_market_data_service` route-provider implementation.

Recorded at: 2026-05-24T11:41:28+08:00.

Base HEAD: `7daf74ce0c3210defc2ad283583a335037daa500`.

Base branch: `origin/wip/root-dirty-20260403`.

Parent PR: `#189`, merged at `7daf74ce0c3210defc2ad283583a335037daa500`.

Parent issue: `#79`.

Parent decision issue: `#92`.

## Decision Boundary

This implementation follows the G2.48 authorization boundary. It changes only:

- `web/backend/app/services/market_data_service/get_market_data_service.py`
- `web/backend/app/services/market_data_service/__init__.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/backend/tests/test_market_data_service_lifecycle_di.py`
- `web/backend/tests/test_market_api_integration.py`
- this implementation report
- generated implementation evidence JSON
- steward tree
- task card

It does not change route paths, response models, OpenAPI exposure, docs/API,
frontend, PM2/runtime process state, OpenSpec files, issue labels, unrelated
service seams, `market_data_adapter.py`, `web/backend/app/services/__init__.py`,
or `MarketDataServiceV2`.

## Implementation Summary

| Area | Change |
|---|---|
| Service provider | Added `MARKET_DATA_SERVICE_STATE_KEY`, `install_market_data_service(app, service=None)`, and `get_market_data_service_dependency(request)`. |
| Compatibility getter | Preserved `get_market_data_service()` and its module-level fallback singleton. |
| Package exports | Re-exported the state key, installer, provider dependency, and compatibility getter from `app.services.market_data_service`. |
| Route dependencies | Converted exactly seven `/api/v1/market` route handler `service` parameters from `Depends(get_market_data_service)` to `Depends(get_market_data_service_dependency)`. |
| Focused tests | Added lifecycle DI tests and updated the existing market API integration fixture to override the new provider dependency. |

Converted route handlers:

| Handler | Route | Result |
|---|---|---|
| `refresh_fund_flow` | `POST /api/v1/market/fund-flow/refresh` | Provider dependency |
| `get_etf_list` | `GET /api/v1/market/etf/list` | Provider dependency |
| `refresh_etf_data` | `POST /api/v1/market/etf/refresh` | Provider dependency |
| `get_chip_race` | `GET /api/v1/market/chip-race` | Provider dependency |
| `refresh_chip_race` | `POST /api/v1/market/chip-race/refresh` | Provider dependency |
| `get_lhb_detail` | `GET /api/v1/market/lhb` | Provider dependency |
| `refresh_lhb_detail` | `POST /api/v1/market/lhb/refresh` | Provider dependency |

## TDD Evidence

RED command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_service_lifecycle_di.py -q --tb=short --no-cov
```

RED result:

```text
4 failed, 1 passed in 2.16s
```

Expected failing reasons:

- package did not re-export `MARKET_DATA_SERVICE_STATE_KEY`
- getter module did not define `install_market_data_service`
- getter module did not define `get_market_data_service_dependency`
- route handlers still depended on `get_market_data_service`

GREEN command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_service_lifecycle_di.py -q --tb=short --no-cov
```

GREEN result:

```text
5 passed in 2.97s
```

## Guard Evidence

Route dependency guard:

```text
old_depends=0
new_depends=7
provider_import=true
```

This confirms the seven authorized route dependency parameters were migrated and
no `Depends(get_market_data_service)` call remains in
`market/market_data_request.py`.

## Focused Integration Verification

Command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_api_integration.py -q --tb=short --no-cov
```

Result:

```text
18 passed in 15.41s
```

## App And OpenAPI Smoke

The configured `app.main` / OpenAPI smoke used non-sensitive placeholder
environment variables and produced:

| Field | Value |
|---|---:|
| Runtime routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Selected `/api/v1/market` routes | `7` |

The smoke exited with status `0`.

## Static Verification

Commands:

```bash
ruff check web/backend/app/services/market_data_service/get_market_data_service.py web/backend/app/services/market_data_service/__init__.py web/backend/app/api/market/market_data_request.py web/backend/tests/test_market_data_service_lifecycle_di.py web/backend/tests/test_market_api_integration.py
black --check web/backend/app/services/market_data_service/get_market_data_service.py web/backend/app/services/market_data_service/__init__.py web/backend/app/api/market/market_data_request.py web/backend/tests/test_market_data_service_lifecycle_di.py web/backend/tests/test_market_api_integration.py
```

Results:

- `ruff`: `All checks passed!`
- `black --check`: `5 files would be left unchanged`

## GitNexus Evidence

Pre-edit GitNexus checks:

| Target | Risk | Impacted count | Notes |
|---|---|---:|---|
| `get_market_data_service` | LOW | `0` | Package compatibility getter remains public. |
| `web/backend/app/api/market/market_data_request.py` | LOW | `3` | Direct importer is package `api/market/__init__.py`; test imports are expected. |
| selected route handlers | LOW / no process impact | `0` for unambiguous handlers | Some handler names are shared with mock modules, so file-level impact was used as the reliable route-surface guard. |

Staged GitNexus detect changes:

```text
risk_level=high
changed_files=9
changed_count=39
affected_count=6
```

The high staged verdict is retained as an explicit review signal. The affected
processes are reported through `market_data_request.py` file-level symbol
mapping and name `get_kline_data` flows even though this implementation changes
only the authorized provider import and seven route dependency parameters in
that file. The risk is therefore handled through the focused lifecycle test,
market API integration test, route dependency count guard, ruff/black, and
configured route/OpenAPI smoke rather than suppressed.

## Compatibility Boundary

The following compatibility surfaces are preserved:

- `get_market_data_service()` remains public
- package re-export remains public
- `market_data_adapter.py` fallback surface remains unchanged
- `web/backend/app/services/__init__.py` IntegratedServices accessor remains unchanged
- `MarketDataServiceV2` remains separate

## Rollback

If this implementation causes a regression:

1. Revert this implementation PR.
2. The seven route handlers will return to `Depends(get_market_data_service)`.
3. `get_market_data_service()` compatibility fallback remains available before,
   during, and after rollback.
4. The G2.48 consumer matrix remains historical authorization evidence unless
   separately superseded.

## Next Gate

After review and merge, run a G2.50 closeout / current-head candidate refresh
before selecting another service lifecycle implementation lane.
