# Backend Service Lifecycle DI Candidate Refresh After Stock Search - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: candidate-refresh-prepared-for-review
- Workline: G2.22 current-head service lifecycle DI candidate refresh after
  stock-search
- Base HEAD: `d2e799cd2c1c`
- Remote base: `origin/wip/root-dirty-20260403` at
  `d2e799cd2c1cbeb00b70d5cf64897b7c8a8a3b11`
- Parent issue: `#92` OPEN with `enhancement`, `ready-for-human`,
  `ready-for-downstream`
- Service lifecycle issue: `#79` OPEN with `needs-triage`
- Execution mode: governance/evidence only

Boundary note: this packet refreshes candidate evidence only. It does not
authorize backend source edits, route edits, tests, OpenAPI changes, OpenSpec
changes, issue label movement, `ready-for-agent` movement, PM2/runtime work, or
a G2.23 implementation.

## Governance Boundary

This packet executes the G2.22 current-head refresh requested by G2.21. It does
not authorize:

- Backend source, test, route, OpenAPI, generated-client, frontend, PM2, or
  runtime changes
- OpenSpec change/spec creation, modification, validation archive, or issue
  publication
- GitHub issue label movement
- Selecting a direct next service DI implementation candidate
- Deleting, retiring, or modifying compatibility getters

## Input State

PR `#161` was merged into `wip/root-dirty-20260403` at
`d2e799cd2c1cbeb00b70d5cf64897b7c8a8a3b11`. That packet selected this G2.22
refresh before any further service lifecycle DI source edit or stock-search
compatibility cleanup.

The immediately preceding stock-search route-surface implementation and closeout
remain the relevant local context:

- G2.19 added the `stock_search_service` app-state provider seam and injected
  `StockSearchService` into the approved route-local consumers.
- G2.20 confirmed the approved route files no longer call
  `get_stock_search_service()` directly.
- G2.21 deliberately did not select another implementation candidate. It asked
  for this current-head refresh first.

## Current-Head Inventory

The refresh scanned `web/backend/app/services/**/*.py` at HEAD `d2e799cd2c1c`.
The scanner used two levels:

- Broad heuristic: files with getter/singleton/provider signals. This catches
  storage helpers, app-state providers, registry surfaces, and other false
  positives, so it is not used as a backlog count by itself.
- Narrow service-lifecycle inventory: service files with `get_*service*`
  functions, `_instance = None`, or service app-state provider/dependency
  patterns. This is the candidate-selection input.

Snapshot:

| Metric | Value |
|---|---:|
| Service Python files scanned | 152 |
| Broad heuristic hit files | 42 |
| Narrow service-lifecycle candidate files | 17 |

Bucket counts for the narrow inventory:

| Bucket | Count | Meaning |
|---|---:|---|
| completed-route-surface-di | 4 | Existing route-surface DI lanes already implemented or retained as reference |
| broad-market-data-strategy-seam | 7 | Active market/data/strategy seams; not a low-risk direct implementation pick |
| hold-no-clear-active-route-surface | 2 | No clear active route-surface candidate without more consumer proof |
| process-runtime-singleton-or-streaming | 2 | Runtime/streaming/process-level behavior; do not batch as ordinary service DI |
| registry-integrated-seam | 1 | Package registry/integrated service surface |
| reference-provider-pattern | 1 | Reference provider pattern evidence |

Narrow inventory:

| File | Getter / signal | API hits | Test hits | Non-route service hits | Bucket |
|---|---|---:|---:|---:|---|
| `web/backend/app/services/__init__.py` | `get_integrated_services`, `get_market_data_service`, `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, `get_cache_service` | 8 | 11 | 6 | registry-integrated-seam |
| `web/backend/app/services/announcement_service.py` | `get_announcement_service`, `get_announcement_service_dependency` | 12 | 2 | 0 | completed-route-surface-di |
| `web/backend/app/services/data_service.py` | `get_data_service` | 5 | 6 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/data_service_enhanced.py` | `get_enhanced_data_service` | 0 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/email_notification_service.py` | `get_email_service` | 0 | 3 | 2 | hold-no-clear-active-route-surface |
| `web/backend/app/services/email_service.py` | `get_email_service`, `get_email_service_dependency` | 7 | 6 | 1 | completed-route-surface-di |
| `web/backend/app/services/market_data_service/get_market_data_service.py` | `get_market_data_service` | 8 | 11 | 6 | broad-market-data-strategy-seam |
| `web/backend/app/services/market_data_service_v2.py` | `get_market_data_service_v2` | 17 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/monitoring_service.py` | `_instance = None` | 0 | 0 | 0 | process-runtime-singleton-or-streaming |
| `web/backend/app/services/realtime_streaming_service.py` | `get_streaming_service` | 0 | 19 | 2 | process-runtime-singleton-or-streaming |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `get_stock_search_service`, `get_stock_search_service_dependency` | 8 | 7 | 4 | completed-route-surface-di |
| `web/backend/app/services/strategy_service.py` | `get_strategy_service` | 4 | 1 | 4 | broad-market-data-strategy-seam |
| `web/backend/app/services/tdx_service.py` | `get_tdx_service` | 9 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/technical_analysis_service.py` | `_instance = None` | 0 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/tradingview_widget_service.py` | `get_tradingview_service`, `get_tradingview_service_dependency` | 7 | 5 | 0 | reference-provider-pattern |
| `web/backend/app/services/watchlist_service.py` | `get_watchlist_service`, `get_watchlist_service_dependency` | 8 | 3 | 4 | completed-route-surface-di |
| `web/backend/app/services/wencai_service.py` | `get_wencai_service` | 0 | 0 | 0 | hold-no-clear-active-route-surface |

## GitNexus Spot Checks

GitNexus was used as risk evidence, not as the sole source of truth. Where graph
results conflict with current text guards, this report records the conflict
instead of treating it as implementation authorization.

| Target | GitNexus risk | Direct impact | Processes / modules | Current interpretation |
|---|---:|---:|---|---|
| `get_market_data_service_v2` | CRITICAL | 15 | 6 processes, 2 modules | Active `market_v2.py` and dashboard surface; not a direct next pilot |
| `get_data_service` | CRITICAL | 3 | 7 processes, 2 modules | Indicator/strategy data seam; needs design packet before edits |
| `get_stock_search_service` | CRITICAL | 6 | 11 processes, 2 modules | Graph still reports route callers at confidence `0.5`; text guard shows route direct calls are now `0`, so cleanup requires a separate consumer-matrix packet |
| `get_strategy_service` | HIGH | 6 | 4 modules | Strategy route/adapter/task surface; not a direct next pilot |
| `get_tdx_service` | HIGH | 2 | 3 processes, 1 module | Dashboard live-market surface; not a direct next pilot |
| `get_market_data_service` | LOW | 0 | 0 | Text scan still finds API/test/non-route refs; treat as graph-name ambiguity, not safe-proof |
| `get_email_service` | MEDIUM | 6 | 1 module | Completed route DI lane; remaining evidence is graph/compatibility cleanup, not a new candidate |

## Stock-Search Compatibility Getter Boundary

Current text guard for the approved route files:

| File | Direct `get_stock_search_service()` calls | Dependency provider refs |
|---|---:|---:|
| `web/backend/app/api/stock_search/stock_search_result.py` | 0 | 6 |
| `web/backend/app/api/market/market_data_request.py` | 0 | 2 |

Current test references:

| File | Direct getter calls | Dependency provider refs |
|---|---:|---:|
| `web/backend/tests/test_runtime_regressions_p0.py` | 3 | 0 |
| `web/backend/tests/test_stock_search_service_lifecycle_di.py` | 0 | 1 |

This means route-surface DI migration is closed for the approved route-local
consumers, but the module-level compatibility getter is still an intentional
surface until a later decision packet classifies all remaining service, test,
and package re-export references.

## Decision

No next route-surface service DI implementation candidate is selected by G2.22.

Rationale:

- The remaining market/data/strategy/dashboard seams are HIGH or CRITICAL by
  GitNexus or are text-scan active across broad API/test/non-route surfaces.
- Completed route-surface DI files still appear in scans because their
  compatibility getters and dependency providers are intentionally retained.
- `stock_search_service` is the narrowest actionable follow-up, but its next
  step is not deletion or source editing. It needs a compatibility getter
  cleanup authorization and consumer-matrix packet first.

Selected next lane:

**G2.23 stock-search compatibility getter cleanup authorization / consumer
matrix packet.**

This is a decision-only next lane. It should decide whether
`get_stock_search_service()` remains:

- active public compatibility,
- test-only fallback,
- package-internal fallback,
- or a future retire/delete candidate.

## Required G2.23 Scope

The G2.23 packet should:

1. Enumerate all `stock_search_service` getter, dependency-provider, installer,
   package re-export, route, and test references at current HEAD.
2. Separate route dependency-provider references from direct compatibility
   getter calls, including the current eight route-level
   `get_stock_search_service_dependency` provider references.
3. Record GitNexus graph freshness or graph/text divergence for
   `get_stock_search_service`.
4. Define any future allowed write scope, tests, rollback plan, and explicit
   forbidden paths if cleanup is later approved.
5. Keep source deletion and source edits locked until the G2.23 decision packet
   is reviewed and a separate implementation authorization is approved.

## Explicit Non-Goals

- No backend source edits
- No test edits
- No compatibility getter deletion or rename
- No route/OpenAPI/docs/API/generated client edits
- No issue label movement
- No OpenSpec proposal creation or archive
- No PM2/runtime verification

## Next Gate

Human review of this G2.22 refresh packet. If accepted, create G2.23 as a
stock-search compatibility getter cleanup authorization / consumer-matrix packet
before any stock-search compatibility getter source edit or broader service DI
implementation selection.
