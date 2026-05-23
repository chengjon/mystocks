# Backend MarketDataServiceV2 Route Provider Implementation Authorization - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-authorization-prepared-for-review
- Workline: G2.26 MarketDataServiceV2 route-provider implementation authorization
- Recorded at: 2026-05-23T13:59:20+08:00
- Current HEAD: `46507955f77a3166491bd4510c56ef034b6ff1cb`
- Base branch: `origin/wip/root-dirty-20260403`
- Parent PR: `#165`, merged at `46507955f77a3166491bd4510c56ef034b6ff1cb`
- Parent issue: `#79`
- Parent decision issue: `#92`
- Source implementation authorized by this document: no

## Governance Boundary

This packet is an authorization request for a later implementation lane. It
does not edit backend source, route handlers, tests, OpenSpec changes, runtime
configuration, issue labels, or PM2/stateful gates.

If approved, a future implementation PR may modify only the files listed in the
allowed write scope below. Any dashboard, adapter, `MarketDataService` package,
OpenAPI, frontend, generated-client, PM2, or service-consolidation work must be
proposed as a separate lane.

## Current Issue State

| Item | State | Notes |
|---|---|---|
| Issue `#79` | `OPEN`, `needs-triage` | Parent service singleton lifecycle DI issue remains open. |
| Issue `#92` | downstream decision accepted in this thread | Human maintainer accepted downstream split decisions; this packet remains decision/authorization only. |
| G2.24 broad service seam design | PR `#164` merged at `f97ca070853a77afc80c226d53948e805ba33c8e` | Rejected a mixed broad implementation batch and selected a market-data design packet first. |
| G2.25 market-data provider design | PR `#165` merged at `46507955f77a3166491bd4510c56ef034b6ff1cb` | Rejected service consolidation and selected this G2.26 authorization packet before source edits. |

## Evidence Inputs

| Evidence | Path / Source | Role |
|---|---|---|
| Broad service seam design | `docs/reports/quality/backend-broad-service-seam-design-2026-05-23.md` | Records that broad market/data/strategy seams are too large for one implementation batch. |
| Market-data provider design | `docs/reports/quality/backend-market-data-provider-design-2026-05-23.md` | Selects `MarketDataServiceV2` route-provider authorization as the next market-data lane. |
| Market-data provider JSON | `.planning/codebase/generated/market-data-provider-design-2026-05-23.json` | Machine-readable G2.25 consumer and lane-ordering evidence. |
| Existing DI pattern evidence | `email_service.py`, `announcement_service.py`, `watchlist_service.py`, `stock_search_service` route-provider work | App-state provider plus compatibility getter fallback pattern to reuse. |
| Route-provider reference pattern | `web/backend/app/services/email_service.py` | Uses `EMAIL_SERVICE_STATE_KEY`, `install_email_service(...)`, and `get_email_service_dependency(...)`. |
| Current route scan | current HEAD `46507955f` | Confirms 13 direct `get_market_data_service_v2()` route-local calls in `market_v2.py`. |
| GitNexus impact | `get_market_data_service_v2` | Confirms CRITICAL impact, 18 impacted symbols, 15 direct callers, 6 affected processes, and 2 affected modules. |

## Candidate Decision

Authorize a future `MarketDataServiceV2` route-provider implementation lane only
after human approval of this packet.

The future lane should standardize how `market_v2.py` route handlers obtain
`MarketDataServiceV2`, while preserving the compatibility getter and leaving
runtime behavior unchanged.

Rationale:

- G2.25 rejected consolidating `MarketDataService` and `MarketDataServiceV2`.
- `market_v2.py` has a clear route-surface seam: 13 route-local calls to
  `get_market_data_service_v2()`.
- `dashboard_data_source.py` has 2 non-route helper/class consumers and should
  not be mixed into a route-provider implementation batch.
- `MarketDataService` package routes already use `Depends(get_market_data_service)`
  in `market/market_data_request.py` and should stay in a separate lane.
- GitNexus classifies the getter surface as CRITICAL, so the write scope must be
  narrow and test-first.

## GitNexus Pre-Edit Snapshot

| Symbol | File | Risk | Impacted count | Direct callers | Processes affected | Disposition |
|---|---|---:|---:|---:|---:|---|
| `get_market_data_service_v2` | `web/backend/app/services/market_data_service_v2.py` | CRITICAL | 18 | 15 | 6 | Compatibility getter must remain; route call sites require deliberate migration. |

Direct d=1 callers recorded by GitNexus:

| Caller | File | Future disposition |
|---|---|---|
| `get_fund_flow` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_fund_flow` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `get_etf_list` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_etf_spot` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `get_lhb_detail` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_lhb_detail` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `get_sector_fund_flow` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_sector_fund_flow` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `get_stock_dividend` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_stock_dividend` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `get_stock_blocktrade` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_stock_blocktrade` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `refresh_all_market_data` | `web/backend/app/api/market_v2.py` | Convert route-local getter call to an injected `MarketDataServiceV2`. |
| `_get_market_overview_data` | `web/backend/app/api/dashboard_data_source.py` | Excluded from first implementation scope; non-route helper/class consumer. |
| `prewarm_dashboard_market_overview_cache` | `web/backend/app/api/dashboard_data_source.py` | Excluded from first implementation scope; non-route helper consumer. |

## Current Text Scan

| Surface | Current fact | Disposition |
|---|---:|---|
| `web/backend/app/services/market_data_service_v2.py` LOC | 668 | Large enough to keep implementation scope minimal. |
| `_market_data_service_v2 = None` | present | Keep compatibility singleton fallback. |
| `get_market_data_service_v2()` | present | Keep public compatibility getter. |
| `market_v2.py` route-local getter calls | 13 | Future implementation target. |
| `dashboard_data_source.py` getter calls | 2 | Excluded from first route-provider batch. |

## Future Allowed Write Scope

If this authorization packet is approved, a future implementation branch may
modify only:

| Path | Future allowed change |
|---|---|
| `web/backend/app/services/market_data_service_v2.py` | Add state key, installer, and FastAPI dependency provider; preserve `get_market_data_service_v2()` compatibility fallback. |
| `web/backend/app/api/market_v2.py` | Convert only the 13 route-local `get_market_data_service_v2()` calls to injected `MarketDataServiceV2` parameters. |
| `web/backend/tests/test_market_data_service_v2_lifecycle_di.py` or an equivalent focused test file | Cover provider install, app-state override, fallback behavior, route dependency override, and representative route call behavior. |
| `docs/reports/quality/backend-market-data-service-v2-route-provider-implementation-2026-05-23.md` | Record future implementation evidence and verification results. |
| future PR task card | Bind the implementation PR to the authorized source/test/report paths. |

## Future Implementation Shape

The future implementation should follow the established app-state provider plus
compatibility fallback shape:

- keep `get_market_data_service_v2()` as the compatibility getter
- add a stable state key, for example `MARKET_DATA_SERVICE_V2_STATE_KEY`
- add `install_market_data_service_v2(app, service=None)` that stores the
  selected service on `app.state`
- add `get_market_data_service_v2_dependency(request: Request)` that reads from
  `app.state` and falls back to the installer/getter when absent
- inject `MarketDataServiceV2` into `market_v2.py` route handlers with
  `Depends(get_market_data_service_v2_dependency)`
- preserve existing route paths, HTTP methods, response envelopes, OpenAPI
  operation IDs, validation behavior, and exception behavior

## Explicit Non-Goals

The future implementation lane must not:

- modify `web/backend/app/api/dashboard_data_source.py`
- modify `web/backend/app/services/market_data_adapter.py`
- modify `web/backend/app/services/market_data_service/**`
- modify `web/backend/app/services/__init__.py` integrated-services accessors
- consolidate `MarketDataService` and `MarketDataServiceV2`
- remove `get_market_data_service_v2()`
- change route paths, HTTP methods, response models, response envelopes, or
  OpenAPI schema exposure
- change docs/API, generated clients, frontend code, PM2 scripts, runtime config,
  OpenSpec changes/specs, or GitHub issue labels
- expand into dashboard/source-factory provider design

## Required Future Gates

Before any future source implementation commit:

1. Run GitNexus impact/context for `get_market_data_service_v2` and the selected
   `market_v2.py` route symbols.
2. Add failing focused tests for provider install/app-state override/fallback and
   at least one route dependency override path.
3. Implement the smallest route-provider seam that satisfies those tests.
4. Run focused pytest for the new lifecycle test and any representative
   `market_v2.py` route smoke chosen in the implementation packet.
5. Run `ruff check` on touched backend source/test files.
6. Run an `app.main` import or targeted OpenAPI smoke if route signatures change.
7. Stage only the authorized paths and run GitNexus `detect_changes` on the staged
   scope before committing.

## Rollback Plan For Future Implementation

If the future implementation causes regressions:

- revert the future implementation PR
- restore direct route-local getter calls in `market_v2.py`
- remove the new route-provider dependency from route signatures
- keep `get_market_data_service_v2()` compatibility getter available
- keep this authorization packet as historical governance evidence unless the
  decision itself is explicitly superseded

## Review Checklist

This packet should be accepted only if reviewers agree that:

- `MarketDataServiceV2` route-provider DI is the next market-data implementation
  candidate after G2.25
- the first implementation scope is limited to `market_data_service_v2.py`,
  `market_v2.py`, focused lifecycle tests, implementation evidence, and a future
  task card
- dashboard, adapter, `MarketDataService` package, OpenAPI, frontend, PM2, and
  service-consolidation work remain out of scope
- this PR does not itself authorize or perform source implementation
