# Backend MarketDataService Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.112 MarketDataService getter-retirement implementation
Status: ready for review

## Purpose

Implement the G2.111 authorization by retiring the package-level
`MarketDataService` lazy singleton getter in
`web/backend/app/services/market_data_service/get_market_data_service.py`.

This implementation is intentionally narrow. It does not change market routes,
OpenAPI exposure, PM2 workflows, OpenSpec changes, frontend code, GitHub issue
labels, service consolidation, or the root-level
`web/backend/app/services/__init__.py:get_market_data_service` surface.

## Parent Gate

| Gate | Result |
|---|---|
| Parent authorization | G2.111 accepted in PR `#264` |
| Parent merge commit | `88a8ae4e50ca29c21580db2e0c3f33c0a303ad2d` |
| Current implementation base | `88a8ae4e50ca29c21580db2e0c3f33c0a303ad2d` |
| Authorized provider target | `web/backend/app/services/market_data_service/get_market_data_service.py` |
| Authorized adapter target | `web/backend/app/services/market_data_adapter.py` |
| Authorized package target | `web/backend/app/services/market_data_service/__init__.py` |
| Authorized removals | package-level `_market_data_service`, package-level `get_market_data_service`, package export for package-level getter |
| Required preservation | `MarketDataService`, `install_market_data_service`, `get_market_data_service_dependency`, route/API contracts, OpenAPI exposure, root-level services getter |

## Pre-Edit Evidence

| Evidence | Result |
|---|---|
| `architecture/STANDARDS.md` | Read before source edit; deletion requires explicit closure and evidence |
| `openspec/AGENTS.md` | Read before continuing architecture implementation work |
| GitNexus analyze | `gitnexus analyze --with-gitignore`; indexed successfully before edit |
| File-path GitNexus context | `market_data_service/get_market_data_service.py:get_market_data_service` has no incoming graph callers, no outgoing graph calls, and no process participation |
| Target GitNexus impact | `get_market_data_service`; LOW / `0` impacted symbols |
| Adapter class GitNexus impact | `MarketDataSourceAdapter`; LOW / `0` impacted symbols |
| Adapter method GitNexus impact | `_get_market_service`; LOW / `6` impacted symbols, all within `market_data_adapter.py` |
| Exact pre-change target evidence | direct API refs=`0`; package export and `market_data_adapter.py` were the expected implementation consumers |

## Change

Removed the package-level lazy singleton surface from
`web/backend/app/services/market_data_service/get_market_data_service.py`:

- `_market_data_service`
- `get_market_data_service`

Kept the route dependency seam and app-state installer:

- `MARKET_DATA_SERVICE_STATE_KEY`
- `install_market_data_service`
- `get_market_data_service_dependency`

Adjusted the authorized consumers:

- `web/backend/app/services/market_data_service/__init__.py` no longer exports
  package-level `get_market_data_service`
- `web/backend/app/services/market_data_adapter.py` no longer imports or calls
  the package getter; it now lazily creates an adapter-local
  `MarketDataService` instance for non-mock mode

Added focused regression coverage:

- `web/backend/tests/test_market_data_service_getter_retirement.py`

Updated existing lifecycle coverage:

- `web/backend/tests/test_market_data_service_lifecycle_di.py`

## Verification

| Check | Command | Result |
|---|---|---|
| TDD red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_service_getter_retirement.py -q --no-cov --tb=short` | `2 failed`; failures proved package getter export and adapter getter dependency still existed |
| Focused green | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_market_data_service_getter_retirement.py web/backend/tests/test_market_data_service_lifecycle_di.py -q --no-cov --tb=short` | `7 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Ruff touched files | `ruff check web/backend/app/services/market_data_service/get_market_data_service.py web/backend/app/services/market_data_service/__init__.py web/backend/app/services/market_data_adapter.py web/backend/tests/test_market_data_service_lifecycle_di.py web/backend/tests/test_market_data_service_getter_retirement.py` | passed |
| Black touched files | `black --check web/backend/app/services/market_data_service/get_market_data_service.py web/backend/app/services/market_data_service/__init__.py web/backend/app/services/market_data_adapter.py web/backend/tests/test_market_data_service_lifecycle_di.py web/backend/tests/test_market_data_service_getter_retirement.py` | passed |
| Exact post-change scan | scripted text scan | target getter definition=`0`; target singleton token=`0`; package getter imports=`0`; adapter getter calls=`0`; root-level services getter preserved |
| Raw `app.main` import | `PYTHONPATH=web/backend python -c 'import app.main'` | blocked by missing required environment variables, not by this change |
| Env-complete `app.main` import | same import with required dummy env vars | passed |

## Post-Change Scan

| Surface | Result |
|---|---|
| `market_data_service/get_market_data_service.py:def get_market_data_service` | `0` |
| `market_data_service/get_market_data_service.py:_market_data_service` | `0` |
| `from app.services.market_data_service import get_market_data_service` | `0` |
| `market_data_adapter.py` calls to `get_market_data_service()` | `0` |
| `web/backend/app/services/__init__.py:get_market_data_service` | preserved; explicitly out of scope |
| `MarketDataService` | preserved |
| `install_market_data_service` | preserved |
| `get_market_data_service_dependency` | preserved |

## Boundary

This PR does not:

- modify market route handlers
- modify route paths, response models, response shapes, or OpenAPI exposure
- modify frontend code
- modify PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state
- delete or rename `MarketDataService`
- delete or alter `install_market_data_service`
- delete or alter `get_market_data_service_dependency`
- modify root-level `web/backend/app/services/__init__.py:get_market_data_service`
- perform broader market-data service consolidation

## Next Gate

Human review / PR merge decision for G2.112.

If accepted, create G2.113 closeout/current-head refresh before selecting another
service getter candidate.
