# Backend Stock Search Service Lifecycle DI Implementation Authorization - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-authorization-prepared-for-review
- Workline: G2.18 stock-search route-surface service lifecycle DI
- Recorded at: 2026-05-23T09:20:07+08:00
- Current HEAD: `0285d1cbc29b`
- Parent issue: [#79](https://github.com/chengjon/mystocks/issues/79)
- Parent decision issue: [#92](https://github.com/chengjon/mystocks/issues/92)
- Source implementation authorized by this document: no

## Governance Boundary

This packet is an authorization request for a later implementation lane. It
does not edit backend source, route handlers, tests, OpenSpec changes, runtime
configuration, issue labels, or PM2/stateful gates.

If approved, a future implementation PR may modify only the files listed in the
allowed write scope below. Any broader market-data, strategy, data, adapter,
OpenAPI, or service-lifecycle cleanup must be proposed as a separate lane.

## Current Issue State

| Item | State | Notes |
|---|---|---|
| Issue `#79` | `OPEN`, `needs-triage` | Parent service singleton lifecycle DI issue remains open. |
| Issue `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` | Downstream governance remains a decision/control issue, not source authorization. |
| G2.17 candidate refresh | PR `#157` merged at `0285d1cbc29b` | Selected `stock_search_service` as the next authorization candidate only. |
| OpenSpec `migrate-backend-singletons-to-lifecycle-di` | Complete | Current work continues under downstream governance reports rather than reopening that completed change. |

## Evidence Inputs

| Evidence | Path / Source | Role |
|---|---|---|
| Candidate refresh report | `docs/reports/quality/backend-service-lifecycle-di-candidate-refresh-2026-05-23.md` | Selects `stock_search_service.py` as the conditional G2.18 authorization candidate. |
| Candidate refresh JSON | `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-2026-05-23.json` | Machine-readable candidate inventory and recommendation. |
| Existing DI pattern evidence | `email_service.py`, `announcement_service.py`, `watchlist_service.py` | App-state provider plus compatibility getter fallback pattern to reuse. |
| GitNexus impact | `StockSearchService`, `get_stock_search_service` | Confirms class-level LOW impact but getter-level CRITICAL route surface. |
| Route scan | current HEAD `0285d1cbc29b` | Confirms six direct `get_stock_search_service()` route calls. |

## Candidate Decision

Authorize `web/backend/app/services/stock_search_service/stock_search_service.py`
as the next route-surface service lifecycle DI implementation candidate after
human approval.

Rationale:

- It is the smallest practical remaining route-surface service candidate from
  the G2.17 scan: `175` LOC.
- The service class impact is LOW with no direct GitNexus callers or affected
  processes.
- The compatibility getter has a narrow but important route surface: five calls
  in stock-search routes and one call in market K-line data.
- Existing DI pilots have already established the app-state provider plus
  compatibility fallback pattern.
- The next larger candidates (`tdx`, `data`, `market_data_v2`, `strategy`) have
  broader route, adapter, external-client, or task implications.

## GitNexus Pre-Edit Snapshot

| Symbol | File | Risk | Direct callers | Processes affected | Disposition |
|---|---|---:|---:|---:|---|
| `StockSearchService` | `web/backend/app/services/stock_search_service/stock_search_service.py` | LOW | 0 | 0 | Class body is small enough for a focused app-state provider seam. |
| `get_stock_search_service` | `web/backend/app/services/stock_search_service/stock_search_service.py` | CRITICAL | 6 | 11 | Compatibility getter must remain as fallback; route call sites must be migrated deliberately. |

Direct GitNexus callers of `get_stock_search_service`:

| Caller | File | Future migration target |
|---|---|---|
| `search_stocks` | `web/backend/app/api/stock_search/stock_search_result.py` | Inject `StockSearchService` with FastAPI `Depends`. |
| `get_stock_quote` | `web/backend/app/api/stock_search/stock_search_result.py` | Inject `StockSearchService` with FastAPI `Depends`. |
| `get_stock_news` | `web/backend/app/api/stock_search/stock_search_result.py` | Inject `StockSearchService` with FastAPI `Depends`. |
| `get_market_news` | `web/backend/app/api/stock_search/stock_search_result.py` | Inject `StockSearchService` with FastAPI `Depends`. |
| `clear_search_cache` | `web/backend/app/api/stock_search/stock_search_result.py` | Inject `StockSearchService` with FastAPI `Depends`. |
| `get_kline_data` | `web/backend/app/api/market/market_data_request.py` | Inject `StockSearchService` with FastAPI `Depends`; do not broaden market service work. |

## Current Direct Caller Surface

| Route file | Function | Current access | Notes |
|---|---|---|---|
| `web/backend/app/api/stock_search/stock_search_result.py` | `search_stocks` | `get_stock_search_service()` at line 165 | Calls `service.unified_search(...)`. |
| `web/backend/app/api/stock_search/stock_search_result.py` | `get_stock_quote` | `get_stock_search_service()` at line 260 | Calls realtime quote helpers. |
| `web/backend/app/api/stock_search/stock_search_result.py` | `get_stock_news` | `get_stock_search_service()` at line 356 | Calls stock news helpers. |
| `web/backend/app/api/stock_search/stock_search_result.py` | `get_market_news` | `get_stock_search_service()` at line 398 | Calls market news helpers. |
| `web/backend/app/api/stock_search/stock_search_result.py` | `clear_search_cache` | `get_stock_search_service()` at line 488 | Calls `service.clear_cache()`. |
| `web/backend/app/api/market/market_data_request.py` | `get_kline_data` | `get_stock_search_service()` at line 603 | Calls A-stock K-line fallback path. |

## Future Allowed Write Scope

If this packet is approved, a future implementation lane may edit only:

| Path | Allowed change |
|---|---|
| `web/backend/app/services/stock_search_service/stock_search_service.py` | Add state key, install provider, FastAPI dependency provider, and keep compatibility getter fallback. |
| `web/backend/app/services/stock_search_service/__init__.py` | Re-export any new provider/install symbols if needed for route imports. |
| `web/backend/app/api/stock_search/stock_search_result.py` | Convert only the five direct route-local getter calls to dependency injection. |
| `web/backend/app/api/market/market_data_request.py` | Convert only the `get_kline_data` stock-search service call to dependency injection. |
| `web/backend/tests/test_stock_search_service_lifecycle_di.py` | Add focused provider, app-state override, and compatibility fallback tests. |
| `web/backend/tests/test_stock_search_service_logging.py` | Update only if direct service construction expectations need import-path adjustment. |
| `tests/api/test_stock_search_file.py` | Update only route-level dependency override coverage if required. |
| `docs/reports/quality/backend-stock-search-service-lifecycle-di-implementation-2026-05-23.md` | Record future implementation evidence. |
| `governance/mainline/task-cards/pr-<future>.yaml` | Future implementation PR task card. |

## Explicitly Forbidden Scope

The future implementation lane must not:

- edit any service outside `stock_search_service`;
- edit broader `market_data`, `data_service`, `strategy`, `tdx`, adapter, or
  task-running services;
- change route paths, HTTP methods, response models, OpenAPI exposure, or API
  examples except where unavoidable test-only dependency overrides are needed;
- remove `get_stock_search_service()`;
- remove or change runtime fallback behavior;
- execute PM2/stateful gates;
- move issue labels or publish a new GitHub implementation issue;
- treat the CRITICAL GitNexus getter risk as a blocker to all work. It is a
  reason for a narrow TDD implementation, not a reason to broaden scope.

## Future Implementation Shape

### Service Provider Pattern

The future implementation should follow the already merged service DI pattern:

- keep the current module-level `get_stock_search_service()` compatibility
  getter;
- add a stable state key such as `STOCK_SEARCH_SERVICE_STATE_KEY`;
- add `install_stock_search_service(app, service=None)` to install either a
  supplied test double or the compatibility getter result onto `app.state`;
- add `get_stock_search_service_dependency(request: Request)` to read from
  `request.app.state` and install fallback when missing;
- avoid changing `StockSearchService.__init__` semantics unless required for
  tests and explicitly justified.

### Route Injection Pattern

The future route change should:

- import the dependency provider from `app.services.stock_search_service`;
- add `service: StockSearchService = Depends(get_stock_search_service_dependency)`
  to each approved route signature;
- remove only the local `service = get_stock_search_service()` calls in the six
  approved functions;
- preserve existing current-user dependencies, validation, response wrappers,
  exception handling, and cache behavior.

## Required Future Tests

A future implementation PR must include TDD evidence for:

| Test | Required coverage |
|---|---|
| `web/backend/tests/test_stock_search_service_lifecycle_di.py` | Red/green provider install, app-state override, fallback install, and route dependency override. |
| `web/backend/tests/test_stock_search_service_logging.py` | Existing logging behavior remains valid. |
| `tests/api/test_stock_search_file.py` | Stock-search route smoke remains valid if dependency signatures change. |
| `web/backend/tests/test_runtime_regressions_p0.py` | Include only if route import/runtime regression coverage is already coupled to stock search. |

## Required Future Quality Gates

Before any future source edit:

- re-run GitNexus impact for `StockSearchService`;
- re-run GitNexus impact for the exact `get_stock_search_service` symbol;
- stop and return to review if a new HIGH/CRITICAL dependency appears outside
  the approved route-surface files.

Before future commit:

- focused pytest for the new lifecycle DI tests and existing stock-search
  service tests;
- `ruff check` on touched backend files;
- `git diff --check`;
- staged `gitnexus_detect_changes`;
- Mainline Governance Gate with a future PR task card.

## Rollback Plan

If the future implementation fails, revert the future implementation PR. The
rollback must restore the six direct route-local `get_stock_search_service()`
calls, remove the app-state provider dependency from route signatures, and
preserve the existing compatibility getter.

This authorization packet itself is rollback-safe: revert the governance report,
JSON artifact, PR task card, and steward-tree update.

## Review Decision Needed

Approve or reject G2.18 as the authorization package for a future
`stock_search_service` route-surface lifecycle DI implementation.

Approval authorizes only the future implementation scope and gates described
above. It does not authorize immediate source edits in this PR.
