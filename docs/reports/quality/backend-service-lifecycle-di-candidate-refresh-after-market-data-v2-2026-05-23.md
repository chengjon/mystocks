# Backend Service Lifecycle DI Candidate Refresh After MarketDataServiceV2 - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: candidate-refresh-prepared-for-review
- Workline: G2.29 current-head service lifecycle DI candidate refresh after
  `MarketDataServiceV2`
- Current HEAD: `e79029ff99e8c3ee674d07efd8b1601e7deb32e0`
- Remote base: `origin/wip/root-dirty-20260403` at
  `e79029ff99e8c3ee674d07efd8b1601e7deb32e0`
- Parent issue: `#92` OPEN with `enhancement`, `ready-for-human`,
  `ready-for-downstream`
- Service lifecycle issue: `#79` OPEN with `needs-triage`
- PR `#168`: MERGED at `2026-05-23T07:57:45Z`
- Execution mode: governance/evidence only
- Recorded at: `2026-05-23T16:05:54+08:00`

Boundary note: this packet refreshes candidate evidence only. It does not
authorize backend source edits, route edits, tests, OpenAPI changes, OpenSpec
changes, issue label movement, `ready-for-agent` movement, PM2/runtime work, or
a G2.30 implementation.

## Governance Boundary

This packet executes the current-head refresh requested by the G2.28 closeout.
It does not authorize:

- Backend source, test, route, OpenAPI, generated-client, frontend, PM2, or
  runtime changes
- OpenSpec change/spec creation, modification, validation archive, or issue
  publication
- GitHub issue label movement
- Selecting a direct next service DI implementation candidate
- Deleting, retiring, or modifying compatibility getters
- Migrating `dashboard_data_source.py` helper callers

## Input State

PR `#168` merged the G2.28 closeout into `wip/root-dirty-20260403` at
`e79029ff99e8c3ee674d07efd8b1601e7deb32e0`.

The immediately preceding `MarketDataServiceV2` route-provider sequence is the
relevant local context:

- G2.26 authorized a narrow future write scope limited to
  `market_data_service_v2.py`, `market_v2.py`, focused lifecycle tests,
  implementation evidence, and a task card.
- G2.27 implemented the route-provider seam.
- G2.28 confirmed the merged result: `market_v2.py` has `0` direct route getter
  calls, 13 provider-injected route handlers, and `dashboard_data_source.py`
  still has two intentionally retained helper callers.

## Current-Head Inventory

The refresh scanned `web/backend/app/services/**/*.py` at HEAD `e79029ff99e8`.
The scanner used two levels:

- Expanded broad heuristic: files with service getter/provider/state-key/singleton
  signals. This intentionally catches false positives and is not comparable to
  the earlier G2.22 broad count, so it is not used as a backlog count.
- Narrow service-lifecycle inventory: service files with `get_*service*`
  functions, `_instance = None`, or service app-state provider/dependency
  patterns. This is the candidate-selection input.

Snapshot:

| Metric | Value |
|---|---:|
| Service Python files scanned | 152 |
| Expanded broad heuristic hit files | 94 |
| Narrow service-lifecycle candidate files | 20 |

Bucket counts for the narrow inventory:

| Bucket | Count | Meaning |
|---|---:|---|
| completed-route-surface-di | 5 | Existing route-surface DI lanes already implemented or retained as reference |
| broad-market-data-strategy-seam | 9 | Active market/data/strategy or broad service seams; not low-risk direct picks |
| hold-no-clear-active-route-surface | 2 | No clear active route-surface candidate without more consumer proof |
| process-runtime-singleton-or-streaming | 2 | Runtime/streaming/process-level behavior; do not batch as ordinary service DI |
| registry-integrated-seam | 1 | Package registry/integrated service surface |
| reference-provider-pattern | 1 | Reference provider pattern evidence |

Narrow inventory:

| File | Getter / signal | API hits | Test hits | Non-route service hits | Bucket |
|---|---|---:|---:|---:|---|
| `web/backend/app/services/__init__.py` | `get_integrated_services`, `get_market_data_service`, `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, `get_cache_service` | 8 | 11 | 6 | registry-integrated-seam |
| `web/backend/app/services/advanced_analysis_service.py` | `get_advanced_analysis_service` | 0 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/announcement_service.py` | `get_announcement_service`, `get_announcement_service_dependency`, `install_announcement_service`, `ANNOUNCEMENT_SERVICE_STATE_KEY` | 12 | 2 | 0 | completed-route-surface-di |
| `web/backend/app/services/data_service_enhanced.py` | `get_service_health`, `get_enhanced_data_service` | 1 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/data_service.py` | `get_data_service` | 5 | 6 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/email_notification_service.py` | `get_email_service` | 0 | 3 | 2 | hold-no-clear-active-route-surface |
| `web/backend/app/services/email_service.py` | `get_email_service`, `get_email_service_dependency`, `install_email_service`, `EMAIL_SERVICE_STATE_KEY` | 7 | 6 | 1 | completed-route-surface-di |
| `web/backend/app/services/market_data_service_v2.py` | `get_market_data_service_v2`, `get_market_data_service_v2_dependency`, `install_market_data_service_v2`, `MARKET_DATA_SERVICE_V2_STATE_KEY` | 17 | 3 | 0 | completed-route-surface-di |
| `web/backend/app/services/market_data_service/get_market_data_service.py` | `get_market_data_service` | 8 | 11 | 6 | broad-market-data-strategy-seam |
| `web/backend/app/services/monitoring_service.py` | `_instance = None` | 0 | 0 | 0 | process-runtime-singleton-or-streaming |
| `web/backend/app/services/realtime_streaming_service.py` | `get_streaming_service` | 0 | 19 | 2 | process-runtime-singleton-or-streaming |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `get_stock_search_service`, `get_stock_search_service_dependency`, `install_stock_search_service`, `STOCK_SEARCH_SERVICE_STATE_KEY` | 8 | 8 | 6 | completed-route-surface-di |
| `web/backend/app/services/strategy_service.py` | `get_strategy_service`, `_instance = None` | 4 | 1 | 4 | broad-market-data-strategy-seam |
| `web/backend/app/services/tdx_service.py` | `get_tdx_service`, `_instance = None` | 9 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/technical_analysis_service.py` | `_instance = None` | 0 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/tradingview_widget_service.py` | `get_tradingview_service`, `get_tradingview_service_dependency`, `install_tradingview_service`, `TRADINGVIEW_SERVICE_STATE_KEY` | 7 | 9 | 0 | reference-provider-pattern |
| `web/backend/app/services/unified_data_service.py` | `get_unified_data_service` | 0 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/watchlist_service.py` | `get_watchlist_service`, `get_watchlist_service_dependency`, `install_watchlist_service`, `WATCHLIST_SERVICE_STATE_KEY` | 8 | 3 | 4 | completed-route-surface-di |
| `web/backend/app/services/websocket_service.py` | `get_service_stats` | 0 | 0 | 0 | broad-market-data-strategy-seam |
| `web/backend/app/services/wencai_service.py` | `get_wencai_service` | 0 | 0 | 0 | hold-no-clear-active-route-surface |

## GitNexus Spot Checks

GitNexus was used as risk evidence, not as the sole source of truth.

| Target | GitNexus risk | Direct impact | Processes / modules | Current interpretation |
|---|---:|---:|---|---|
| `get_market_data_service_v2` | CRITICAL | 15 | 6 processes, 2 modules | Route surface is migrated, but dashboard helper callers remain active and the compatibility getter remains a live seam |
| `get_data_service` | CRITICAL | 3 | 7 processes, 2 modules | Indicator/strategy data seam; needs design packet before edits |
| `get_wencai_service` | LOW | 0 | 0 processes, 0 modules | No active route/test surface found; this is not a route-surface DI pilot without an ownership/usefulness decision |
| `get_unified_data_service` | MEDIUM | 5 | 0 processes, 1 module | Service-internal helper seam, not a route-provider migration candidate |

## MarketDataServiceV2 Compatibility Boundary

Current text guard for the `MarketDataServiceV2` seam:

| File | Direct compatibility getter refs | Dependency provider refs | Installer refs | State key refs | Interpretation |
|---|---:|---:|---:|---:|---|
| `web/backend/app/api/market_v2.py` | 0 | 14 | 0 | 0 | 13 route params plus import; route surface migrated |
| `web/backend/app/api/dashboard_data_source.py` | 3 | 0 | 0 | 0 | import plus 2 non-route helper calls; intentionally unchanged |
| `web/backend/app/services/market_data_service_v2.py` | 2 | 1 | 2 | 3 | service-owned provider and compatibility surface |
| `web/backend/tests/test_market_data_service_v2_lifecycle_di.py` | 1 | 1 | 1 | 2 | focused compatibility/provider test coverage |

This means route-surface DI migration is closed for `market_v2.py`, but the
module-level compatibility getter is still an intentional surface until a later
decision packet classifies dashboard helper, service-owned, and test references.

## Decision

No direct next service DI implementation candidate is selected by G2.29.

Rationale:

- The broad market/data/strategy/dashboard seams remain HIGH or CRITICAL by
  GitNexus, or are text-scan active across API/test/non-route surfaces.
- Completed route-surface DI files still appear in scans because their
  compatibility getters and dependency providers are intentionally retained.
- `get_wencai_service` and similar zero-route-hit files are not automatically
  safe implementation candidates; they need ownership/usefulness decisions
  before route-provider work.
- The narrowest actionable follow-up after G2.28 is the
  `MarketDataServiceV2` compatibility getter and dashboard helper consumer
  boundary.

Selected next lane:

**G2.30 `MarketDataServiceV2` compatibility getter / dashboard helper consumer
matrix packet.**

This is a decision-only next lane. It should decide whether
`get_market_data_service_v2()` remains:

- active dashboard-helper compatibility,
- test-only fallback,
- package-internal fallback,
- future dashboard provider migration candidate,
- or future retire/delete candidate.

## Required G2.30 Scope

The G2.30 packet should:

1. Enumerate all `MarketDataServiceV2` getter, dependency-provider, installer,
   state-key, import, route, dashboard helper, and test references at current
   HEAD.
2. Separate route dependency-provider references from direct compatibility
   getter calls.
3. Classify the two `dashboard_data_source.py` helper callers as active
   compatibility, future provider migration, or intentionally retained
   non-route helper surface.
4. Confirm `market_v2.py` stays at route direct getter calls=`0`.
5. Decide whether a future implementation packet is warranted.
6. If future implementation is warranted, require a separate authorization
   packet with GitNexus impact, exact write scope, tests, rollback plan, and
   forbidden scope.

## Non-Goals

- No backend source, test, route, OpenAPI, generated-client, frontend, PM2, or
  runtime changes
- No OpenSpec change or archive operation
- No issue label movement or `ready-for-agent` movement
- No dashboard helper migration
- No compatibility getter deletion
- No broad market/data/strategy seam implementation
- No direct implementation selection for `wencai_service`,
  `unified_data_service`, or `advanced_analysis_service`

## Next Gate

Human review of this G2.29 refresh packet.

If accepted, prepare G2.30 as a decision-only `MarketDataServiceV2`
compatibility getter / dashboard helper consumer matrix packet. Source edits
remain locked until a later implementation authorization packet is approved.
