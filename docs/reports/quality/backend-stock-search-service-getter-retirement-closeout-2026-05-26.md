# Backend StockSearchService Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

This is a closeout-only governance packet for the merged G2.127
StockSearchService getter retirement implementation. It records the parent
merge, verifies current-head state, and preserves the next-gate boundary.

## Parent Merge

| Field | Value |
|---|---|
| Parent node | G2.127 StockSearchService getter-retirement implementation |
| Parent PR | `#280` |
| Parent state | `MERGED` |
| Parent merge commit | `edf6c2673c6b38b614e43bb78b0ace8696990777` |
| Parent merged at | `2026-05-26T02:00:56Z` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/280` |
| Closeout branch | `g2-128-stock-search-service-getter-retirement-closeout` |
| Current HEAD | `edf6c2673c6b38b614e43bb78b0ace8696990777` |

## Closeout Decision

G2.127 is accepted as the implementation-complete parent for the
StockSearchService getter retirement lane.

The current checkout verifies that `web/backend/app/services/stock_search_service`
no longer exposes the legacy module-level `get_stock_search_service` getter,
standalone `_stock_search_service` singleton, or package re-export of the getter.

The preserved service boundary remains:

- `StockSearchService`
- `STOCK_SEARCH_SERVICE_STATE_KEY`
- `install_stock_search_service`
- `get_stock_search_service_dependency`
- stock search route paths
- market kline route path
- response contracts
- OpenAPI exposure

This packet does not authorize the next implementation lane. After this closeout
is reviewed and merged, the service lifecycle candidate pool should be refreshed
before selecting another getter-retirement lane.

## Current-Head Evidence

| Check | Result |
|---|---:|
| Backend app/test Python files scanned | `778` |
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
| Parent PR state | `gh pr view 280 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,url,title` | `MERGED`, merge commit `edf6c2673c6b38b614e43bb78b0ace8696990777` |
| Focused tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_getter_retirement.py web/backend/tests/test_stock_search_service_lifecycle_di.py web/backend/tests/test_runtime_regressions_p0.py -q --no-cov --tb=short` | `12 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Current-head scan | scripted text scan | getter=`0`, singleton=`0`, package re-export=`0`, direct getter calls=`0`, route dependency handlers=`6` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`0`; changed files=`4`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

- No backend source or test files are edited in this closeout.
- No route path, response model, response shape, or OpenAPI exposure is changed.
- No frontend, PM2, OpenSpec, issue-label, or runtime configuration file is changed.
- No next service lifecycle getter lane is authorized here.
- No `StockSearchService`, `install_stock_search_service`, or
  `get_stock_search_service_dependency` deletion is authorized here.

## Next Gate

Review and merge this closeout. After acceptance, refresh the service lifecycle
candidate pool before selecting another getter-retirement lane.
