# Backend StockSearchService Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

This packet authorizes only a future G2.126 implementation branch. It does not
edit source or tests in this PR. The target is higher risk than the recent
AnnouncementService and EmailService getter retirements, so this authorization
records the CRITICAL GitNexus impact and d=1 acceptance criteria before any
source edit is allowed.

## Parent State

| Field | Value |
|---|---|
| Parent node | G2.124 Service lifecycle candidate refresh after EmailService |
| Parent PR | `#277` |
| Parent state | `MERGED` |
| Parent merge commit | `4ce4abf60fec2719644d9f64cd657bb0b7d3c8c5` |
| Parent merged at | `2026-05-26T01:17:26Z` |
| Current HEAD | `4ce4abf60fec2719644d9f64cd657bb0b7d3c8c5` |

## Authorization Decision

A future G2.126 implementation branch may retire only:

- `web/backend/app/services/stock_search_service/stock_search_service.py`
  `_stock_search_service`
- `web/backend/app/services/stock_search_service/stock_search_service.py`
  `get_stock_search_service`

The future implementation must preserve:

- `StockSearchService`
- `install_stock_search_service`
- `get_stock_search_service_dependency`
- stock search route paths
- market kline route path
- response contracts
- OpenAPI exposure

## Current-Head Evidence

| Check | Result |
|---|---:|
| Target getter definitions | `1` |
| Target singleton variable tokens | `5` |
| API direct getter calls | `0` |
| App direct getter calls | `2` service self-calls |
| Route dependency handlers | `6` |
| Dependency refs | `12` |

Route dependency files:

- `web/backend/app/api/stock_search/stock_search_result.py`
- `web/backend/app/api/market/market_data_request.py`

Existing tests that reference the legacy singleton/getter and must be rewritten
in the future implementation:

- `web/backend/tests/test_stock_search_service_lifecycle_di.py`
- `web/backend/tests/test_runtime_regressions_p0.py`

## GitNexus Risk

| Field | Value |
|---|---|
| Target | `web/backend/app/services/stock_search_service/stock_search_service.py:get_stock_search_service` |
| Context lines | `168-173` |
| Risk | `CRITICAL` |
| Impacted count | `6` |
| Direct callers | `6` |
| Affected processes | `11` |
| Affected modules | `2` |

d=1 route callers:

- `search_stocks`
- `get_stock_quote`
- `get_stock_news`
- `get_market_news`
- `clear_search_cache`
- `get_kline_data`

This CRITICAL risk is accepted only for preparing a future implementation
authorization. It is not approval to edit source in this packet.

## Future G2.126 Acceptance Criteria

The future implementation must:

- Start with a TDD red test proving `get_stock_search_service` and
  `_stock_search_service` are absent before implementation.
- Update existing tests that still assert legacy singleton/getter behavior.
- Keep `get_stock_search_service_dependency` importable and route-compatible.
- Preserve all route paths, response contracts, and OpenAPI exposure.
- Verify the d=1 route callers listed above through focused tests or route-table
  evidence.
- Run focused tests:
  `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_getter_retirement.py web/backend/tests/test_stock_search_service_lifecycle_di.py web/backend/tests/test_runtime_regressions_p0.py -q --no-cov --tb=short`
- Run route conflict guard:
  `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short`
- Run touched-file lint/format checks.
- Run staged GitNexus `detect_changes(scope="staged")`.
- Run post-commit mainline scope gate.

## Verification

| Check | Command | Result |
|---|---|---|
| Parent PR state | `gh pr view 277 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,url,title` | `MERGED`, merge commit `4ce4abf60fec2719644d9f64cd657bb0b7d3c8c5` |
| Stock search lifecycle baseline | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_stock_search_service_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| Health route conflicts baseline | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| GitNexus context / impact | `context` and `impact(direction="upstream")` | target found; risk=`CRITICAL`, impacted=`6`, affected processes=`11` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`0`; changed files=`4`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

- No backend source or test files are edited in this authorization packet.
- No route path, response model, response shape, or OpenAPI exposure is changed.
- No frontend, PM2, OpenSpec, issue-label, or runtime configuration file is changed.
- No getter deletion is performed here.
- Future source work must happen in G2.126 after this authorization is reviewed
  and accepted.

## Next Gate

Review and merge this authorization. If accepted, create G2.126
StockSearchService getter-retirement implementation with TDD red, explicit
CRITICAL-risk handling, d=1 route/test acceptance criteria, staged GitNexus
scope check, and post-commit mainline gate.
