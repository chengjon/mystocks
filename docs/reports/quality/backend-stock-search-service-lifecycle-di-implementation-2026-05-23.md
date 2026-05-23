# Backend Stock Search Service Lifecycle DI Implementation - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-prepared-for-review
- Workline: G2.19 stock-search route-surface service lifecycle DI
- Recorded at: 2026-05-23T09:43:31+08:00
- Base HEAD: `d63b18ab9841`
- Parent authorization: `backend-stock-search-service-lifecycle-di-implementation-authorization-2026-05-23.md`
- Parent issue: [#79](https://github.com/chengjon/mystocks/issues/79)
- Parent decision issue: [#92](https://github.com/chengjon/mystocks/issues/92)

## Governance Boundary

This implementation follows the G2.18 authorization packet. It changes only the
approved `stock_search_service` service seam, two approved route files, one
focused test file, this evidence report, the steward tree, and this PR task
card.

It does not change route paths, HTTP methods, response models, OpenAPI exposure,
docs/API examples, frontend code, PM2/stateful gates, issue labels, or any
service outside `stock_search_service`.

## Implementation Summary

| Area | Change |
|---|---|
| Service seam | Added `STOCK_SEARCH_SERVICE_STATE_KEY`, `install_stock_search_service`, and `get_stock_search_service_dependency`. |
| Compatibility | Preserved `get_stock_search_service()` as the fallback singleton getter. |
| Package exports | Re-exported the state key, install function, and dependency provider from `app.services.stock_search_service`. |
| Stock-search routes | Converted five approved direct route-local getter calls to injected `StockSearchService`. |
| Market K-line route | Converted the approved `get_kline_data` stock-search fallback call to injected `StockSearchService`. |
| Tests | Added focused lifecycle DI tests for provider install, explicit install, route signatures, and injected cache-clear behavior. |

## GitNexus Pre-Edit Evidence

| Symbol | File | Risk | Direct callers | Processes affected | Action |
|---|---|---:|---:|---:|---|
| `StockSearchService` | `web/backend/app/services/stock_search_service/stock_search_service.py` | LOW | 0 | 0 | Allowed as service seam target. |
| `get_stock_search_service` | `web/backend/app/services/stock_search_service/stock_search_service.py` | CRITICAL | 6 | 11 | Preserved as compatibility fallback; six approved route callers were migrated. |

The CRITICAL getter-level risk was handled by keeping the compatibility getter
and limiting route edits to the six callers listed in the authorization packet.

## Route Consumer Closure

| Route file | Function | Previous access | New access |
|---|---|---|---|
| `web/backend/app/api/stock_search/stock_search_result.py` | `search_stocks` | `get_stock_search_service()` | `service: StockSearchService = Depends(get_stock_search_service_dependency)` |
| `web/backend/app/api/stock_search/stock_search_result.py` | `get_stock_quote` | `get_stock_search_service()` | `service: StockSearchService = Depends(get_stock_search_service_dependency)` |
| `web/backend/app/api/stock_search/stock_search_result.py` | `get_stock_news` | `get_stock_search_service()` | `service: StockSearchService = Depends(get_stock_search_service_dependency)` |
| `web/backend/app/api/stock_search/stock_search_result.py` | `get_market_news` | `get_stock_search_service()` | `service: StockSearchService = Depends(get_stock_search_service_dependency)` |
| `web/backend/app/api/stock_search/stock_search_result.py` | `clear_search_cache` | `get_stock_search_service()` | `service: StockSearchService = Depends(get_stock_search_service_dependency)` |
| `web/backend/app/api/market/market_data_request.py` | `get_kline_data` | local import plus `get_stock_search_service()` | module import plus `service: StockSearchService = Depends(get_stock_search_service_dependency)` |

Current scan result:

- direct `get_stock_search_service()` calls in the two approved route files:
  `none`
- injected stock-search service parameters:
  - stock-search routes: `5`
  - market K-line route: `1`

## TDD Evidence

RED:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_lifecycle_di.py -q --no-cov --tb=short
FFFF
```

Failures were the intended missing behavior:

- missing `get_stock_search_service_dependency`
- missing `install_stock_search_service`
- missing route `service` parameters
- `clear_search_cache()` rejecting injected `service`

GREEN:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_lifecycle_di.py -q --no-cov --tb=short
4 passed in 2.11s
```

Focused suite after implementation and ruff cleanup:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_lifecycle_di.py web/backend/tests/test_stock_search_service_logging.py tests/api/test_stock_search_file.py -q --no-cov --tb=short
31 passed in 1.46s
```

## Verification Snapshot

| Gate | Result |
|---|---|
| Focused lifecycle DI test | `4 passed in 2.11s` |
| Focused stock-search suite | `31 passed in 1.46s` |
| `ruff check` touched files | Passed after auto-fixing two lint issues and rerunning. |
| `black --check` touched files | Passed after manual formatting. |
| app/main OpenAPI smoke | `routes=548 paths=500` |
| Markdown governance | 2 files checked, 0 errors. |
| `git diff --check` | Passed. |
| Direct getter call scan | `none` in the two approved route files. |
| staged GitNexus detection | HIGH, 8 files, 37 changed symbols, 11 affected processes. |

The staged GitNexus result is HIGH because the approved implementation changes
route entrypoints that were already identified by the G2.18 authorization packet:
`get_stock_quote` and `get_kline_data` process chains. No affected process was
reported outside the authorized stock-search / market K-line route surface.

Additional pre-commit gates still required after staging:

- Mainline Governance Gate
- cached diff check

## Rollback Plan

Revert the future PR as one unit. The revert restores the six route-local
`get_stock_search_service()` calls, removes the new app-state dependency
provider exports, and removes the focused lifecycle DI test.

## Next Gate

Human review of the G2.19 implementation PR. If accepted, merge it and then
create a separate closeout packet before selecting any next service lifecycle DI
candidate.
