# Backend StockSearchService Getter Retirement Authorization Amendment - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

This is an amendment-only governance packet. It does not edit backend source or
tests. It corrects the future implementation scope approved in G2.125 by adding
the package re-export file that must be updated when the legacy getter is
retired.

## Parent State

| Field | Value |
|---|---|
| Parent node | G2.125 StockSearchService getter-retirement authorization |
| Parent PR | `#278` |
| Parent state | `MERGED` |
| Parent merge commit | `d2f5a952740db94c382534b0810ba11588660132` |
| Parent merged at | `2026-05-26T01:30:40Z` |
| Current HEAD | `d2f5a952740db94c382534b0810ba11588660132` |

## Amendment

G2.125 omitted:

- `web/backend/app/services/stock_search_service/__init__.py`

That file currently re-exports `get_stock_search_service`. If the future
implementation removes the getter from
`web/backend/app/services/stock_search_service/stock_search_service.py` without
updating the package re-export, imports from `app.services.stock_search_service`
will fail.

Evidence:

| Check | Result |
|---|---|
| Legacy import | line `9`, `from .stock_search_service import get_stock_search_service` |
| Legacy `__all__` entry | line `20`, `"get_stock_search_service"` |

## Amended Future Scope

A future G2.127 implementation may edit only:

- `web/backend/app/services/stock_search_service/stock_search_service.py`
- `web/backend/app/services/stock_search_service/__init__.py`
- `web/backend/tests/test_stock_search_service_lifecycle_di.py`
- `web/backend/tests/test_runtime_regressions_p0.py`
- `web/backend/tests/test_stock_search_service_getter_retirement.py`
- steward tree, generated implementation evidence, implementation report, and
  task card

The future implementation must preserve:

- `StockSearchService`
- `install_stock_search_service`
- `get_stock_search_service_dependency`
- stock search route paths
- market kline route path
- response contracts
- OpenAPI exposure

The future implementation may retire:

- `_stock_search_service`
- `get_stock_search_service`
- package re-export of `get_stock_search_service`

## Verification

| Check | Command | Result |
|---|---|---|
| Parent PR state | `gh pr view 278 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,url,title` | `MERGED`, merge commit `d2f5a952740db94c382534b0810ba11588660132` |
| Package re-export evidence | scripted scan of `web/backend/app/services/stock_search_service/__init__.py` | legacy import line=`9`; legacy `__all__` line=`20` |
| Stock search lifecycle baseline | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| Health route conflicts baseline | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`0`; changed files=`4`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

- No backend source or test files are edited in this amendment packet.
- No route path, response model, response shape, or OpenAPI exposure is changed.
- No frontend, PM2, OpenSpec, issue-label, or runtime configuration file is changed.
- No getter deletion is performed here.
- Future source work must happen in G2.127 after this amendment is reviewed and
  accepted.

## Next Gate

Review and merge this amendment. If accepted, create G2.127 StockSearchService
getter-retirement implementation with TDD red, package re-export update,
explicit CRITICAL-risk handling, d=1 route/test acceptance criteria, staged
GitNexus scope check, and post-commit mainline gate.
