# Backend Service Lifecycle DI Candidate Refresh - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: candidate-refresh-prepared-for-review
- Workline: G2.17 current-head service lifecycle DI candidate refresh
- Current branch: `g2-17-service-di-candidate-refresh`
- Current HEAD: `33e75acddf5c7c363a2e33ba4a3d01923b46edde`
- Parent issue: https://github.com/chengjon/mystocks/issues/92
- Service lifecycle issue: https://github.com/chengjon/mystocks/issues/79
- Refresh PR: https://github.com/chengjon/mystocks/pull/157
- Refresh PR checks at creation: Mainline Governance Gate passed;
  check-compliance passed
- Recorded at: `2026-05-23T03:38:20+08:00`

Boundary note: this packet refreshes candidate evidence only. It does not
authorize backend source edits, route edits, tests, OpenAPI changes, OpenSpec
changes, issue label movement, `ready-for-agent` movement, PM2/runtime work, or
a G2.18 implementation.

## Input State

| Item | Current state | Evidence |
|---|---|---|
| PR `#156` | `MERGED` | `33e75acddf5c7c363a2e33ba4a3d01923b46edde` |
| Issue `#79` | `OPEN`, `needs-triage` | Live GitHub status checked from this worktree |
| Issue `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` | Live GitHub status checked from this worktree |
| Prior route-surface pilots | Complete | `email_service.py`, `announcement_service.py`, `watchlist_service.py` |
| Prior helper cleanup | Complete | Watchlist adapter/data helper provider seam completed by PR `#154` and closed out by PR `#155` |

## Current-Head Inventory Summary

The refresh scanned `web/backend/app/services` at current HEAD.

| Metric | Value |
|---|---:|
| Service Python files scanned | 152 |
| Files with service getter or singleton shape | 15 |
| Route-surface related getter files | 11 |
| Files already using app-state provider pattern | 4 |

Completed app-state provider files:

- `web/backend/app/services/email_service.py`
- `web/backend/app/services/announcement_service.py`
- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/services/tradingview_widget_service.py`

## Candidate Classification

| Class | Files | Disposition |
|---|---|---|
| Completed route-surface DI | `email_service.py`, `announcement_service.py`, `watchlist_service.py` | No further service DI source work required in this lane |
| Reference provider pattern | `tradingview_widget_service.py` | Keep as reference; route already uses app-state dependency provider |
| Recommended next authorization candidate | `stock_search_service/stock_search_service.py` | Prepare a separate G2.18 authorization packet before any source edit |
| Defer: market/dashboard/external data surface | `tdx_service.py`, `market_data_service_v2.py`, `market_data_service/get_market_data_service.py`, `data_service.py` | Broader market/data paths; do not select before stock-search candidate review |
| Defer: strategy/helper/task surface | `strategy_service.py` | Route plus adapter/task callers; needs separate adapter-aware decision if selected later |
| Hold: no active route surface in this scan | `email_notification_service.py`, `wencai_service.py`, `realtime_streaming_service.py`, `data_service_enhanced.py` | Not a route-surface DI pilot candidate from this refresh |
| Registry / integrated seam | `services/__init__.py` | Treat as package registry/integration seam, not a G2.18 pilot |

## Route-Surface Getter Evidence

| Getter | Service file | API files | API hits | Notes |
|---|---|---:|---:|---|
| `get_stock_search_service` | `stock_search_service/stock_search_service.py` | 2 | 8 | Smallest practical remaining route-surface candidate; direct calls in stock-search routes plus one market kline path |
| `get_tdx_service` | `tdx_service.py` | 2 | 9 | External/live-market surface; defer |
| `get_data_service` | `data_service.py` | 2 | 5 | Indicator/strategy data surface; defer |
| `get_market_data_service_v2` | `market_data_service_v2.py` | 2 | 17 | Broad market-v2/dashboard surface; defer |
| `get_market_data_service` | `market_data_service/get_market_data_service.py` and package exports | 1 | 8 | Scanner sees active route dependency; GitNexus graph currently reports 0 impact, so treat as graph/name-ambiguity evidence rather than LOW-risk proof |
| `get_strategy_service` | `strategy_service.py` | 1 | 4 | Route plus adapter/task callers; defer |
| `get_email_service_dependency` | `email_service.py` | 1 | 7 | Completed pattern |
| `get_announcement_service_dependency` | `announcement_service.py` | 1 | 12 | Completed pattern |
| `get_watchlist_service_dependency` | `watchlist_service.py` | 1 | 8 | Completed pattern |
| `get_tradingview_service_dependency` | `tradingview_widget_service.py` | 1 | 7 | Existing reference pattern |

## GitNexus Evidence

| Target | File | Risk | Direct impact | Affected processes | Disposition |
|---|---|---:|---:|---:|---|
| `StockSearchService` | `stock_search_service/stock_search_service.py` | LOW | 0 | 0 | Class shape is low blast radius |
| `get_stock_search_service` | `stock_search_service/stock_search_service.py` | CRITICAL | 6 | 11 | Candidate only with explicit G2.18 authorization, TDD, route dependency override tests, and rollback |
| `get_tdx_service` | `tdx_service.py` | CRITICAL | 2 | 5 | Defer; dashboard/live data path |
| `get_data_service` | `data_service.py` | CRITICAL | 3 | 7 | Defer; indicators/strategy path |
| `get_market_data_service_v2` | `market_data_service_v2.py` | CRITICAL | 15 | 6 | Defer; broad market-v2/dashboard path |
| `get_market_data_service` | `market_data_service/get_market_data_service.py` | LOW | 0 | 0 | Do not rely on graph risk alone because text scan finds active route dependency |
| `get_strategy_service` | `strategy_service.py` | CRITICAL | 6 | 0 | Defer; adapter/task callers present |

GitNexus CRITICAL risk on `get_stock_search_service` is not ignored. It means
the next packet, if accepted, must be an implementation authorization packet with
exact changed files, TDD red/green plan, route dependency override tests,
GitNexus pre-edit impact, staged `detect_changes`, and rollback instructions.
This G2.17 packet does not authorize those edits.

## Recommendation

Select `web/backend/app/services/stock_search_service/stock_search_service.py`
as the conditional G2.18 authorization candidate.

Rationale:

- It is the smallest practical remaining route-surface service file from the
  current scan (`175` LOC).
- `StockSearchService` class impact is LOW with no affected symbols or
  processes.
- Existing tests already reference stock-search behavior:
  `test_stock_search_service_logging.py`,
  `test_stock_search_runtime_fallback.py`, plus runtime/regression guards.
- The remaining alternatives are broader market, dashboard, data, strategy,
  external-client, adapter, or task surfaces.

G2.18 should be authorization-only unless a human explicitly approves source
implementation after reviewing the G2.18 packet.

## Required G2.18 Authorization Scope

If this recommendation is accepted, prepare a separate G2.18 authorization
packet with these boundaries:

- Allowed future source candidates:
  - `web/backend/app/services/stock_search_service/stock_search_service.py`
  - `web/backend/app/api/stock_search/stock_search_result.py`
  - `web/backend/app/api/market/market_data_request.py`
  - focused tests for stock-search service lifecycle DI
- Required future design:
  - add an app-state provider dependency while preserving
    `get_stock_search_service()` as compatibility fallback;
  - convert only approved route call sites to dependency injection;
  - avoid market/data/strategy service changes outside the two named route
    files;
  - include rollback that restores direct getter calls and removes provider
    override tests.
- Required future gates:
  - GitNexus impact for `StockSearchService` and exact
    `get_stock_search_service` symbol before editing;
  - TDD red/green for provider injection and compatibility fallback;
  - focused route tests or dependency override tests;
  - `ruff check` on touched files;
  - staged `gitnexus_detect_changes`;
  - Mainline Governance Gate for the implementation PR.

## Explicit Non-Goals

This refresh packet does not authorize:

- editing `web/backend/app/services/**`;
- editing `web/backend/app/api/**`;
- editing tests;
- creating or modifying OpenSpec changes/specs;
- changing issue `#79` or issue `#92` labels;
- moving any issue to `ready-for-agent`;
- creating a GitHub implementation issue;
- executing PM2/stateful gates;
- treating `get_market_data_service` GitNexus LOW result as proof that the
  market-data route dependency is safe.

## Next Gate

Human review of this G2.17 candidate refresh packet.

If accepted, create a separate G2.18 authorization packet for the conditional
`stock_search_service` route-surface service DI candidate. Source edits remain
locked until that later authorization packet is explicitly approved.
