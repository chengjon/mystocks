# Backend TDX Route Provider Migration Implementation - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- Workline: G2.40 TDX route provider migration implementation
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `e4dc9088cabfb4dba756beb109294980c047c327`
- Parent approval: G2.39 authorization packet, PR `#179`
- Scope: approved source implementation plus focused lifecycle DI tests and evidence

## Decision Boundary

This implementation applies the G2.39 authorization only.

Implemented:

- added `TDX_SERVICE_STATE_KEY = "tdx_service"`;
- kept `get_tdx_service()` as the compatibility fallback getter;
- updated `install_tdx_service(app, service=None)` to read/write the named app-state key;
- added `get_tdx_service_dependency(request: Request) -> TdxService`;
- converted exactly five `/api/v1/tdx` route handler dependencies from `Depends(get_tdx_service)` to `Depends(get_tdx_service_dependency)`;
- added focused tests for provider fallback installation, explicit installer override, route dependency wiring, and injected route use.

Not implemented:

- no deletion or retirement of `get_tdx_service()`;
- no changes to `dashboard_data_source.py`, `api/ml.py`, `main.py`, adapters, frontend, PM2, OpenSpec, issue labels, route paths, response models, or OpenAPI exposure;
- no compatibility wrapper cleanup.

## TDD Evidence

RED command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_tdx_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
```

RED result:

- `3 failed, 1 passed`
- expected failures: missing `get_tdx_service_dependency`, missing `TDX_SERVICE_STATE_KEY`, and route dependencies still pointing at `get_tdx_service`.

GREEN command:

```bash
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_tdx_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
```

GREEN result:

- `4 passed in 1.02s`

## Guard Evidence

Text guard result:

```json
{
  "api_depends_legacy": 0,
  "api_depends_provider": 5,
  "api_legacy_identifier_excluding_provider": 0,
  "service_provider_def": 1,
  "service_legacy_getter_def": 1,
  "service_installer_def": 1,
  "service_state_key_mentions": 4
}
```

OpenAPI smoke result:

```json
{
  "routes_total": 548,
  "openapi_paths_total": 500,
  "operation_ids": 536,
  "duplicate_operation_ids": 0,
  "tdx_paths_count": 7,
  "tdx_paths": [
    "/api/ml/tdx/data",
    "/api/ml/tdx/stocks/{market}",
    "/api/v1/tdx/health",
    "/api/v1/tdx/index/kline",
    "/api/v1/tdx/index/quote/{symbol}",
    "/api/v1/tdx/kline",
    "/api/v1/tdx/quote/{symbol}"
  ]
}
```

OpenAPI smoke notes:

- `app.main` imported successfully.
- The `Numba needs NumPy 2.2 or less. Got NumPy 2.4.` GPU warning is pre-existing fallback noise from optional GPU dependencies.
- Socket.IO initialization log was emitted during import.

## Static Verification

Commands:

```bash
ruff check web/backend/app/services/tdx_service.py web/backend/app/api/tdx.py web/backend/tests/test_tdx_service_lifecycle_di.py
black --check web/backend/app/services/tdx_service.py web/backend/app/api/tdx.py web/backend/tests/test_tdx_service_lifecycle_di.py
```

Results:

- Ruff: `All checks passed!`
- Black: `3 files would be left unchanged.`

## GitNexus Pre-Edit Evidence

Repository: `g2-40-tdx-route-provider-migration`

- `impact(get_tdx_service, upstream, includeTests=true)`: LOW; direct dependency `install_tdx_service`; no affected execution flows or modules.
- `impact(install_tdx_service, upstream, includeTests=true)`: LOW; no direct callers detected by graph.
- `context(get_stock_quote, file_path=web/backend/app/api/tdx.py)`: route symbol located; outgoing `get_real_time_quote`; no incoming process participation.
- `context(health_check, file_path=web/backend/app/api/tdx.py)`: route symbol located; outgoing `check_connection`; no incoming process participation.

## GitNexus Staged Scope Evidence

Command:

```bash
gitnexus detect-changes --scope staged
```

Result:

- changed files: `7`
- changed symbols: `18`
- affected count: `1`
- risk level: `medium`
- affected process: `Prewarm_dashboard_market_overview_cache -> Warning`
- no HIGH or CRITICAL risk verdict was reported.

## Rollback

Rollback is a single PR revert. Reverting restores the five route dependencies to `Depends(get_tdx_service)` and removes the new app-state dependency provider while preserving the pre-existing singleton fallback behavior.

## Next Gate

Human review of the implementation PR. If accepted and merged, run a G2.41 closeout or current-head candidate refresh before selecting the next service lifecycle DI lane.
