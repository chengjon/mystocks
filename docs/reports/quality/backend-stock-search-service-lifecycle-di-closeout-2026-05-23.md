# Backend Stock Search Service Lifecycle DI Closeout - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: closeout-prepared-for-review
- Workline: G2.20 service lifecycle DI implementation closeout
- Completed pilot: `web/backend/app/services/stock_search_service/stock_search_service.py`
- Implementation PR: https://github.com/chengjon/mystocks/pull/159
- Implementation merge commit: `25db762ae6484ad4638baf0f8ab42b94a978a403`
- Implementation commit: `3fc46c0d8ae17db4c4e911e303023dea7648b7af`
- Authorization PR: https://github.com/chengjon/mystocks/pull/158
- Authorization merge commit: `d63b18ab98417d9051dfbf177a975ac7470c96d3`
- Closeout branch: `g2-19-stock-search-service-di-closeout`
- Recorded at: `2026-05-23T10:10:26+08:00`

## Governance Boundary

This closeout is governance bookkeeping only. It records that the G2.19
stock-search route-surface DI implementation was reviewed through PR checks and
merged.

It does not authorize another service lifecycle DI candidate, adapter/data-layer
migration, route/OpenAPI contract changes, OpenSpec changes, issue label
movement, PM2/runtime work, frontend work, docs/API changes, or additional
source edits.

## Completed Scope

PR `#159` implemented the G2.18-authorized route-surface-only scope:

- `web/backend/app/services/stock_search_service/stock_search_service.py`
  - added `STOCK_SEARCH_SERVICE_STATE_KEY`
  - added `install_stock_search_service(app, service=None)`
  - added `get_stock_search_service_dependency(request)`
  - retained `get_stock_search_service()` as the compatibility getter
- `web/backend/app/services/stock_search_service/__init__.py`
  - re-exported the new provider and install symbols
- `web/backend/app/api/stock_search/stock_search_result.py`
  - injected `StockSearchService` into five stock-search route handlers
  - removed route-body direct `get_stock_search_service()` calls from those
    five handlers
- `web/backend/app/api/market/market_data_request.py`
  - injected `StockSearchService` into `get_kline_data`
  - removed the route-body local import and direct getter call
- `web/backend/tests/test_stock_search_service_lifecycle_di.py`
  - added focused TDD coverage for provider installation, route signatures,
    fake-service injection, and compatibility fallback
- `docs/reports/quality/backend-stock-search-service-lifecycle-di-implementation-2026-05-23.md`
  - recorded implementation evidence and rollback boundaries
- `governance/mainline/task-cards/pr-159.yaml`
  - recorded implementation scope and gates
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
  - recorded G2.19 as implementation prepared for review

## Preserved Compatibility Boundary

The implementation preserved `get_stock_search_service()` as the legacy
compatibility getter. Any non-route consumer or future service cleanup that
still depends on the compatibility getter must be routed through a separate
packet with its own impact evidence, exact write scope, tests, rollback plan,
and review gate.

## Verification Recorded Before Merge

Local verification from the implementation packet:

| Check | Result |
|---|---|
| TDD red run | 4 expected failures before implementation |
| focused stock-search lifecycle and existing regression tests | 31 passed |
| `ruff check` on touched Python files | passed |
| `black --check` on touched Python files | passed |
| `app.main` / `app.openapi()` smoke | routes=548, paths=500 |
| Markdown governance | checked_files=2, errors=0 |
| Mainline scope gate | passed |
| GitNexus staged/compare checks | HIGH, expected and authorized for the `get_stock_quote` / `get_kline_data` route surface |

GitHub PR `#159` checks:

| Check | Result |
|---|---|
| `Validate API Contracts` | pass |
| `Generate TypeScript Types` | pass |
| `Detect Breaking Changes` | pass/skipped according to workflow matrix |
| `Generate Contract Validation Report` | pass |
| `Mainline Governance Gate` | pass |
| `check-compliance` | pass |
| weekly/notify jobs | skipped as expected |

Post-merge route-surface scan in the closeout worktree:

| File | Direct `get_stock_search_service()` calls | Injected route params |
|---|---:|---:|
| `web/backend/app/api/stock_search/stock_search_result.py` | 0 | 5 |
| `web/backend/app/api/market/market_data_request.py` | 0 | 1 |

## Current State After Merge

- `stock_search_service` is now a merged route-surface service lifecycle DI
  pilot after `email_service.py`, `announcement_service.py`, and
  `watchlist_service.py`.
- `get_stock_search_service()` remains the legacy compatibility getter.
- Five stock-search route handlers and the market `get_kline_data` fallback
  route use injected `StockSearchService`.
- Issue `#79` remains the parent service lifecycle DI issue and should not be
  moved to implementation-ready state by this closeout.
- No next service lifecycle DI candidate is selected by this closeout.

## Next Gate

Human review of this closeout packet.

If accepted, decide in a separate packet whether to:

1. run a fresh service lifecycle DI candidate refresh,
2. select a next route-surface service DI candidate,
3. create a compatibility-getter cleanup packet for stock-search non-route
   consumers, or
4. pause the service lifecycle DI sequence and return to another architecture
   workline.

This closeout does not itself authorize any of those follow-up actions.
