# Backend MarketDataServiceV2 Route Provider Implementation - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-prepared-for-review
- Workline: G2.27 MarketDataServiceV2 route-provider lifecycle DI
- Recorded at: 2026-05-23T14:53:05+08:00
- Base HEAD: `76a1e271fa602e692553acf2760f100ca88030aa`
- Parent authorization: `backend-market-data-service-v2-route-provider-implementation-authorization-2026-05-23.md`
- Parent authorization PR: `#166`, merged at `76a1e271fa602e692553acf2760f100ca88030aa`
- Parent issue: `#79`
- Parent decision issue: `#92`

## Governance Boundary

This implementation follows the G2.26 authorization packet. It changes only the
approved `MarketDataServiceV2` service seam, the approved `market_v2.py` route
surface, one focused lifecycle DI test file, this evidence report, the steward
tree, and this PR task card.

It does not change `dashboard_data_source.py`, `market_data_adapter.py`, the
`market_data_service` package, services `__init__`, route paths, HTTP methods,
response models, OpenAPI schema exposure, docs/API examples, frontend code,
PM2/stateful gates, OpenSpec changes/specs, issue labels, or service
consolidation.

## Implementation Summary

| Area | Change |
|---|---|
| Service seam | Added `MARKET_DATA_SERVICE_V2_STATE_KEY`, `install_market_data_service_v2`, and `get_market_data_service_v2_dependency`. |
| Compatibility | Preserved `get_market_data_service_v2()` as the fallback singleton getter. |
| Route surface | Converted the 13 approved `market_v2.py` route-local getter calls to injected `MarketDataServiceV2` parameters. |
| Exclusions | Left the 2 `dashboard_data_source.py` helper/class getter calls unchanged. |
| Tests | Added focused lifecycle DI tests for provider install, explicit install, route signatures, and injected ETF refresh behavior. |

## GitNexus Pre-Edit Evidence

| Symbol / file | Risk | Impacted count | Direct callers | Processes affected | Action |
|---|---:|---:|---:|---:|---|
| `get_market_data_service_v2` | CRITICAL | 18 | 15 | 6 | Preserved as compatibility fallback; only the 13 authorized `market_v2.py` route callers were migrated. |
| `web/backend/app/api/market_v2.py` | LOW | 0 | 0 | 0 | Allowed route-surface target for dependency injection. |

The CRITICAL getter-level risk was handled by preserving the compatibility
getter and excluding the two `dashboard_data_source.py` helper callers from this
route-provider implementation.

## Route Consumer Closure

| Function | Previous access | New access |
|---|---|---|
| `get_fund_flow` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_fund_flow` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `get_etf_list` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_etf_spot` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `get_lhb_detail` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_lhb_detail` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `get_sector_fund_flow` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_sector_fund_flow` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `get_stock_dividend` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_stock_dividend` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `get_stock_blocktrade` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_stock_blocktrade` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |
| `refresh_all_market_data` | `get_market_data_service_v2()` | `service: MarketDataServiceV2 = Depends(get_market_data_service_v2_dependency)` |

Current scan result:

- approved `market_v2.py` route signatures with `service`: `13`
- approved `market_v2.py` route-local `get_market_data_service_v2()` calls: `0`
- excluded `dashboard_data_source.py` helper/class getter calls: `2`, unchanged

## TDD Evidence

RED:

```text
env PYTHONPATH=web/backend pytest -q -o addopts= web/backend/tests/test_market_data_service_v2_lifecycle_di.py --no-cov --tb=short
FFFF
```

Failures were the intended missing behavior:

- missing `get_market_data_service_v2_dependency`
- missing `install_market_data_service_v2`
- missing `service` parameters on `market_v2.py` route handlers
- `refresh_etf_spot()` rejected an injected service argument

GREEN:

```text
env PYTHONPATH=web/backend pytest -q -o addopts= web/backend/tests/test_market_data_service_v2_lifecycle_di.py --no-cov --tb=short
4 passed in 1.31s
```

## Verification Snapshot

| Gate | Command | Result |
|---|---|---|
| Focused lifecycle DI tests | `env PYTHONPATH=web/backend pytest -q -o addopts= web/backend/tests/test_market_data_service_v2_lifecycle_di.py --no-cov --tb=short` | `4 passed` |
| Ruff touched files | `ruff check web/backend/app/services/market_data_service_v2.py web/backend/app/api/market_v2.py web/backend/tests/test_market_data_service_v2_lifecycle_di.py` | passed |
| Black check touched files | `black --check web/backend/app/services/market_data_service_v2.py web/backend/app/api/market_v2.py web/backend/tests/test_market_data_service_v2_lifecycle_di.py` | passed |
| App import smoke | minimal test env plus `python -c "import app.main"` | `app-main-import-ok` |
| OpenAPI targeted smoke | minimal test env plus `app.openapi()` | `paths=500`, `market_v2_paths=13`, `duplicate_operation_ids=0` |
| Staged GitNexus detect changes | `detect_changes(scope="staged")` | medium risk, 6 changed files, 1 affected process: `Refresh_all_market_data -> Rename` |

Notes:

- An initial `app.main` import without required environment variables failed on
  existing environment validation. The quiet import smoke above supplied the
  required minimal test environment and passed.
- OpenSpec was inspected for active context; this implementation does not modify
  OpenSpec changes or specs.

## Rollback Plan

If this implementation causes regressions:

- revert this PR
- restore the 13 `market_v2.py` route functions to direct
  `get_market_data_service_v2()` calls
- remove `MARKET_DATA_SERVICE_V2_STATE_KEY`, `install_market_data_service_v2`,
  and `get_market_data_service_v2_dependency`
- remove the focused lifecycle DI test file
- keep G2.26 authorization evidence as historical decision input unless it is
  explicitly superseded

## Next Gate

Human review of this G2.27 implementation. If accepted and merged, run a
post-merge closeout packet that records final route-surface scan, PR number,
merge commit, and whether another service lifecycle DI lane should be selected.
