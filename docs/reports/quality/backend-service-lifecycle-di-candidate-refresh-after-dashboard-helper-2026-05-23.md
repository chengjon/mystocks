# Backend Service Lifecycle DI Candidate Refresh After Dashboard Helper - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.33 service lifecycle DI candidate refresh after dashboard helper provider migration
- Status: review-ready
- Base HEAD: `40a396fabcbafcc527d4d15af1eb81034a645d87`
- Parent PR: `#172`, merged at `40a396fabcbafcc527d4d15af1eb81034a645d87`
- Parent issues: `#92`, `#79`
- Scope: governance and evidence only

Boundary note: this packet performs a post-G2.32 candidate refresh. It does
not authorize backend source edits, route changes, OpenAPI changes, PM2/runtime
gate execution, OpenSpec archive actions, compatibility getter deletion, or a
new implementation lane.

## Governance Boundary

This packet executes the current-head refresh requested after the G2.32
dashboard helper provider migration. It does not authorize:

- Backend source, test, route, OpenAPI, generated-client, frontend, PM2, or
  runtime changes
- OpenSpec change/spec creation, modification, validation archive, or issue
  publication
- GitHub issue label movement
- Compatibility getter deletion or privatization
- A G2.34 implementation branch

## Why This Refresh Exists

The steward tree gate after G2.32 says that once the dashboard helper provider
migration is accepted and merged, the next step is to refresh service lifecycle
DI candidates before selecting any new implementation lane.

G2.32 closed the active `MarketDataServiceV2` dashboard-helper direct getter
surface:

- `dashboard_data_source.py` direct `get_market_data_service_v2()` calls: `0`
- `dashboard.py` route-body `get_data_source()` calls: `0`
- `market_v2.py` direct `get_market_data_service_v2()` route calls: `0`
- `get_market_data_service_v2()` remains public fallback behavior

## Current-Head Scan

Static scan input:

- `web/backend/app/services`: `152` Python service files
- Candidate files: `20`
- Criteria: `get_*service*`, `install_*service*`, `*_instance = None`, and
  `app.state.*service` signals
- Reference surfaces: `web/backend/app/api`, `web/backend/tests`, and other
  service files

Bucket counts:

| Bucket | Count | Interpretation |
|---|---:|---|
| `registry-integrated-seam` | 1 | Integrated services registry remains a broad design seam |
| `route-surface-candidate` | 6 | Route/API-visible candidates or completed route-provider seams |
| `active-public-fallback-after-dashboard-migration` | 1 | `MarketDataServiceV2` getter remains public fallback |
| `broad-data-or-strategy-seam` | 5 | Requires separate design lanes, not pilot selection |
| `service-internal-or-test-surface` | 3 | Internal/test-only signals, not route-provider pilots |
| `process-runtime-singleton-or-streaming` | 2 | Runtime/streaming/process-lifetime candidates |
| `ownership-usefulness-decision-needed` | 2 | No active route/test surface found |

The counts are unchanged from G2.29: `152` service files and `20` candidate
files. The meaningful delta is qualitative: the `MarketDataServiceV2` dashboard
helper direct getter surface is now closed, so it no longer blocks refreshing
the broader service lifecycle candidate set.

## Candidate Inventory

| File | Bucket | API | Tests | Other services | Signals |
|---|---|---:|---:|---:|---|
| `web/backend/app/services/__init__.py` | `registry-integrated-seam` | 8 | 11 | 6 | `get_integrated_services`, `get_market_data_service`, `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, `get_cache_service` |
| `web/backend/app/services/advanced_analysis_service.py` | `ownership-usefulness-decision-needed` | 0 | 0 | 0 | `get_advanced_analysis_service` |
| `web/backend/app/services/announcement_service.py` | `route-surface-candidate` | 12 | 2 | 0 | `get_announcement_service`, `get_announcement_service_dependency`, `install_announcement_service` |
| `web/backend/app/services/data_service_enhanced.py` | `route-surface-candidate` | 1 | 0 | 0 | `get_service_health`, `get_enhanced_data_service` |
| `web/backend/app/services/data_service.py` | `broad-data-or-strategy-seam` | 5 | 6 | 0 | `get_data_service` |
| `web/backend/app/services/email_notification_service.py` | `service-internal-or-test-surface` | 0 | 3 | 2 | `get_email_service` |
| `web/backend/app/services/email_service.py` | `route-surface-candidate` | 7 | 6 | 1 | `get_email_service`, `get_email_service_dependency`, `install_email_service` |
| `web/backend/app/services/market_data_service_v2.py` | `active-public-fallback-after-dashboard-migration` | 18 | 4 | 0 | `get_market_data_service_v2`, `get_market_data_service_v2_dependency`, `install_market_data_service_v2` |
| `web/backend/app/services/market_data_service/get_market_data_service.py` | `broad-data-or-strategy-seam` | 8 | 11 | 6 | `get_market_data_service` |
| `web/backend/app/services/monitoring_service.py` | `service-internal-or-test-surface` | 0 | 0 | 12 | `_instance` |
| `web/backend/app/services/realtime_streaming_service.py` | `process-runtime-singleton-or-streaming` | 0 | 19 | 2 | `get_streaming_service` |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `route-surface-candidate` | 8 | 8 | 6 | `get_stock_search_service`, `get_stock_search_service_dependency`, `install_stock_search_service` |
| `web/backend/app/services/strategy_service.py` | `broad-data-or-strategy-seam` | 4 | 1 | 4 | `get_strategy_service`, `_strategy_service_instance` |
| `web/backend/app/services/tdx_service.py` | `route-surface-candidate` | 9 | 0 | 0 | `get_tdx_service`, `_tdx_service_instance` |
| `web/backend/app/services/technical_analysis_service.py` | `service-internal-or-test-surface` | 0 | 0 | 12 | `_instance` |
| `web/backend/app/services/tradingview_widget_service.py` | `broad-data-or-strategy-seam` | 7 | 9 | 0 | `get_tradingview_service`, `get_tradingview_service_dependency`, `install_tradingview_service` |
| `web/backend/app/services/unified_data_service.py` | `broad-data-or-strategy-seam` | 0 | 0 | 0 | `get_unified_data_service` |
| `web/backend/app/services/watchlist_service.py` | `route-surface-candidate` | 8 | 3 | 4 | `get_watchlist_service`, `get_watchlist_service_dependency`, `install_watchlist_service` |
| `web/backend/app/services/websocket_service.py` | `process-runtime-singleton-or-streaming` | 0 | 0 | 0 | `get_service_stats` |
| `web/backend/app/services/wencai_service.py` | `ownership-usefulness-decision-needed` | 0 | 0 | 0 | `get_wencai_service` |

## Route Usage Matrix

| Candidate | Direct API/helper calls | Dependency provider use | Interpretation |
|---|---:|---|---|
| `announcement_service` | 0 | `web/backend/app/api/announcement/routes.py` | Completed route-surface DI seam |
| `email_service` | 0 | `web/backend/app/api/notification.py` | Completed route-surface DI seam |
| `stock_search_service` | 0 | `stock_search_result.py`, `market_data_request.py` | Completed route-surface DI seam |
| `watchlist_service` | 0 | `web/backend/app/api/watchlist.py` | Route seam exists; adapter-side callers make further edits high-risk |
| `market_data_service_v2` | 0 | `market_v2.py`, `dashboard_data_source.py` | G2.27 and G2.32 closed route/helper direct calls |
| `tdx_service` | 2 | none | Remaining narrow route/helper direct getter candidate |

The two TDX direct calls are both in
`web/backend/app/api/dashboard_data_source.py`.

## GitNexus Current-Head Spot Checks

GitNexus indexing note: the first `gitnexus analyze` run in the linked
worktree failed while trying to mutate `.git/info`, because a Git worktree uses
`.git` as a file. Re-running `gitnexus analyze --no-gitignore` succeeded and
registered repo `g2-33-service-lifecycle-di-candidate-refresh-after-dashboard-helper`
at HEAD `40a396fabcbafcc527d4d15af1eb81034a645d87`.

| Target | Risk | Direct impact | Processes | Modules | Interpretation |
|---|---|---:|---:|---:|---|
| `get_market_data_service_v2` | LOW | 1 | 0 | 0 | Dashboard/helper direct calls are closed; public fallback remains |
| `get_tdx_service` | CRITICAL | 2 | 8 | 2 | Narrow next decision candidate, but dashboard flows require authorization first |
| `get_watchlist_service` | HIGH | 3 | 0 | 3 | Route provider seam exists; adapter-side callers require separate design |
| `get_enhanced_data_service` | LOW | 1 | 0 | 0 | Health/control-plane adjacent, not a generic service DI pilot |
| `get_stock_search_service` | LOW | 1 | 0 | 0 | Completed route-provider DI seam |

## Decision

Do not open another implementation lane directly from this refresh.

The recommended next step is a decision-only G2.34 authorization packet for
the TDX dashboard helper provider seam. That packet should decide whether a
future source branch may touch:

- `web/backend/app/services/tdx_service.py`
- `web/backend/app/api/dashboard_data_source.py`
- focused dashboard/TDX tests
- implementation evidence report
- a future mainline task card

The future packet must explicitly continue to exclude route path changes,
OpenAPI contract changes, frontend work, PM2/runtime stateful gates, broad
market/data/strategy service consolidation, and compatibility getter deletion
unless a later approved plan says otherwise.

## Verification

| Check | Result |
|---|---|
| Static service candidate scan | `152` service files, `20` candidate files |
| Route usage matrix | MarketDataServiceV2 direct route/helper calls `0`; TDX helper direct calls `2` |
| GitNexus current-head index | Registered worktree repo at `40a396fabcbafcc527d4d15af1eb81034a645d87` |
| GitNexus spot checks | `get_tdx_service` is CRITICAL; `get_market_data_service_v2` is LOW |

## Next Gate

Human review of this G2.33 packet. If accepted, create G2.34 as a
decision-only TDX dashboard helper provider migration authorization packet.
Do not edit source code from this packet.
