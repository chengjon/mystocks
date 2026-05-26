# Backend StockSearchService Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

This implementation retires the StockSearchService module-level singleton getter
under the G2.125 authorization and G2.126 authorization amendment. The work
keeps the app-state dependency boundary and does not edit route/API files.

## Parent Authorization

| Field | Value |
|---|---|
| Parent node | G2.126 StockSearchService getter-retirement authorization amendment |
| Parent PR | `#279` |
| Parent state | `MERGED` |
| Parent merge commit | `d23a4cf1de28972f3880495cce659540064b2576` |
| Parent merged at | `2026-05-26T01:44:33Z` |
| Current HEAD | `d23a4cf1de28972f3880495cce659540064b2576` |

## Risk Confirmation

GitNexus pre-edit impact for `get_stock_search_service` remained CRITICAL:

| Field | Value |
|---|---|
| Target | `web/backend/app/services/stock_search_service/stock_search_service.py:get_stock_search_service` |
| Risk | `CRITICAL` |
| Impacted count | `6` |
| Direct callers | `6` |
| Affected processes | `11` |
| Affected modules | `2` |

d=1 route callers remain route-dependency consumers and were not edited:

- `search_stocks`
- `get_stock_quote`
- `get_stock_news`
- `get_market_news`
- `clear_search_cache`
- `get_kline_data`

## Implementation

Retired:

- `web/backend/app/services/stock_search_service/stock_search_service.py`
  `_stock_search_service`
- `web/backend/app/services/stock_search_service/stock_search_service.py`
  `get_stock_search_service`
- `web/backend/app/services/stock_search_service/__init__.py`
  `get_stock_search_service` package re-export

Preserved:

- `StockSearchService`
- `STOCK_SEARCH_SERVICE_STATE_KEY`
- `install_stock_search_service`
- `get_stock_search_service_dependency`
- stock search route paths
- market kline route path
- response contracts
- OpenAPI exposure

`install_stock_search_service(app, service=None)` now constructs
`StockSearchService()` directly when an explicit service is not supplied. The
route dependency still reads and installs the app-state service through
`get_stock_search_service_dependency`.

## Post-Change Evidence

| Check | Result |
|---|---:|
| Target getter definitions | `0` |
| Target singleton variable tokens | `0` |
| Exact package getter import | `false` |
| Exact package `__all__` getter entry | `false` |
| API direct getter calls | `0` |
| App direct getter calls | `0` |
| Test direct getter calls | `0` |
| Dependency refs | `14` |
| Route dependency handlers | `6` |
| Installer refs | `7` |

## Verification

| Check | Command | Result |
|---|---|---|
| TDD red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_getter_retirement.py -q --no-cov --tb=short` | `1 failed` before implementation |
| Focused green | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_getter_retirement.py web/backend/tests/test_stock_search_service_lifecycle_di.py web/backend/tests/test_runtime_regressions_p0.py -q --no-cov --tb=short` | `12 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Touched-file lint | `ruff check ...` | passed |
| Touched-file format | `black --check ...` | `5 files would be left unchanged` |
| Package import smoke | `PYTHONPATH=web/backend python ...` | passed |
| Exact scan | scripted text scan | getter=`0`, singleton=`0`, package re-export=`0`, direct getter calls=`0`, route dependency handlers=`6` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`22`; changed files=`9`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

- No route/API files are edited.
- No route path, response model, response shape, or OpenAPI exposure is changed.
- No frontend, PM2, OpenSpec, issue-label, or runtime configuration file is changed.
- `StockSearchService`, `install_stock_search_service`, and
  `get_stock_search_service_dependency` remain present.
- This does not authorize the next service lifecycle lane.

## Next Gate

Review and merge this implementation. If accepted, create G2.128
StockSearchService getter-retirement closeout before selecting another service
lifecycle getter lane.
