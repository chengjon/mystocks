# Backend Service Lifecycle DI Candidate Refresh After TDX Helper - 2026-05-23

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.37 service lifecycle DI candidate refresh after TDX dashboard
  helper closeout
- Status: review-ready
- Current HEAD: `6e940a7a5596b4256f63fec888c589777456d36a`
- Parent PR: `#176`, merged at `6e940a7a5596b4256f63fec888c589777456d36a`
- Parent issue: `#79`
- Scope: governance and evidence only

Boundary note: this packet performs a current-head candidate refresh after the
G2.35/G2.36 TDX dashboard helper provider migration and closeout. It does not
authorize backend source edits, tests, route changes, OpenAPI changes,
PM2/runtime gate execution, OpenSpec archive actions, compatibility getter
deletion, issue label movement, or a new implementation lane.

## Why This Refresh Exists

The steward tree gate after G2.36 says that after the TDX dashboard helper
provider migration is merged and closed out, the next step is a fresh
current-head service lifecycle DI candidate refresh before selecting another
source implementation lane.

This refresh confirms the meaningful delta from G2.33:

- `dashboard_data_source.py` direct `get_tdx_service()` helper calls moved from
  `2` to `0`.
- `tdx_service.py` now has an app-state installer seam:
  `install_tdx_service(app, service=None)`.
- `get_tdx_service()` remains public and active as a compatibility fallback.
- `/api/tdx` still has 5 `Depends(get_tdx_service)` sites and was intentionally
  outside G2.35.

## Current GitHub State

| Item | State |
|---|---|
| Issue `#79` | `OPEN`, labels=`needs-triage` |
| PR `#176` | `MERGED` |
| PR `#176` merge commit | `6e940a7a5596b4256f63fec888c589777456d36a` |

## Scan Method

- Service root: `web/backend/app/services`
- Service files scanned: `152`
- Narrow candidate criteria:
  - `get_*service*`, `install_*service*`, or `get_service_*` functions
  - `*_instance = None` or `_instance = None`
  - `app.state.*service` references
- Reference surfaces:
  - `web/backend/app/api`
  - `web/backend/tests`
  - other files under `web/backend/app/services`

## Scan Summary

| Bucket | Count | Interpretation |
|---|---:|---|
| `completed-route-provider-seam` | 5 | Previously completed route/provider seams remain closed |
| `tdx-route-dependency-surface` | 1 | TDX dashboard helpers are closed, but `/api/tdx` dependency surface remains |
| `route-surface-or-control-plane-review` | 2 | Route/control-plane adjacent candidates need separate decision packets |
| `broad-data-or-strategy-seam` | 3 | Broad seams are not suitable direct pilots |
| `process-runtime-singleton-or-streaming` | 2 | Runtime/streaming lifetime needs separate design |
| `service-internal-or-test-surface` | 2 | Internal/test surfaces are not route-provider pilots |
| `registry-integrated-seam` | 1 | Integrated registry remains a broad design seam |
| `ownership-usefulness-decision-needed` | 2 | No immediate active route/provider implementation lane selected |

Current narrow candidate/signal files: `18`.

## Candidate Inventory

| Service file | Bucket | API refs | Test refs | Service refs | Signals |
|---|---|---:|---:|---:|---|
| `web/backend/app/services/__init__.py` | `registry-integrated-seam` | 3 | 6 | 4 | `get_integrated_services`, `get_market_data_service`, `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, `get_cache_service` |
| `web/backend/app/services/announcement_service.py` | `completed-route-provider-seam` | 1 | 1 | 0 | `get_announcement_service`, `install_announcement_service`, `get_announcement_service_dependency` |
| `web/backend/app/services/data_service_enhanced.py` | `route-surface-or-control-plane-review` | 1 | 0 | 0 | `get_service_health`, `get_enhanced_data_service` |
| `web/backend/app/services/data_service.py` | `broad-data-or-strategy-seam` | 4 | 2 | 0 | `get_data_service` |
| `web/backend/app/services/email_notification_service.py` | `service-internal-or-test-surface` | 1 | 2 | 1 | `get_email_service` |
| `web/backend/app/services/email_service.py` | `completed-route-provider-seam` | 1 | 2 | 1 | `get_email_service`, `install_email_service`, `get_email_service_dependency` |
| `web/backend/app/services/market_data_service_v2.py` | `completed-route-provider-seam` | 2 | 2 | 0 | `get_market_data_service_v2`, `install_market_data_service_v2`, `get_market_data_service_v2_dependency` |
| `web/backend/app/services/market_data_service/get_market_data_service.py` | `ownership-usefulness-decision-needed` | 3 | 6 | 4 | `get_market_data_service` |
| `web/backend/app/services/monitoring_service.py` | `service-internal-or-test-surface` | 0 | 0 | 0 | `_instance` |
| `web/backend/app/services/realtime_streaming_service.py` | `process-runtime-singleton-or-streaming` | 0 | 2 | 1 | `get_streaming_service` |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `completed-route-provider-seam` | 2 | 4 | 1 | `get_stock_search_service`, `install_stock_search_service`, `get_stock_search_service_dependency` |
| `web/backend/app/services/strategy_service.py` | `broad-data-or-strategy-seam` | 1 | 3 | 2 | `get_strategy_service`, `_strategy_service_instance` |
| `web/backend/app/services/tdx_service.py` | `tdx-route-dependency-surface` | 3 | 2 | 0 | `get_tdx_service`, `install_tdx_service`, `_tdx_service_instance`, `tdx_service` |
| `web/backend/app/services/technical_analysis_service.py` | `broad-data-or-strategy-seam` | 0 | 0 | 0 | `_instance` |
| `web/backend/app/services/tradingview_widget_service.py` | `route-surface-or-control-plane-review` | 1 | 1 | 0 | `get_tradingview_service`, `install_tradingview_service`, `get_tradingview_service_dependency` |
| `web/backend/app/services/watchlist_service.py` | `completed-route-provider-seam` | 1 | 4 | 2 | `get_watchlist_service`, `install_watchlist_service`, `get_watchlist_service_dependency` |
| `web/backend/app/services/websocket_service.py` | `process-runtime-singleton-or-streaming` | 0 | 0 | 0 | `get_service_stats` |
| `web/backend/app/services/wencai_service.py` | `ownership-usefulness-decision-needed` | 0 | 0 | 0 | `get_wencai_service` |

## Direct Getter Matrix

| Surface | Count |
|---|---:|
| `dashboard_data_source.py` direct `get_tdx_service()` calls | 0 |
| `dashboard_data_source.py` private `_get_tdx_service()` calls | 3 |
| `tdx.py` `Depends(get_tdx_service)` sites | 5 |
| `tdx.py` direct `get_tdx_service()` calls | 0 |
| `tdx_service.py` `get_tdx_service()` definitions | 1 |
| `tdx_service.py` `install_tdx_service()` definitions | 1 |
| `market_v2.py` direct `get_market_data_service_v2()` calls | 0 |
| `dashboard_data_source.py` direct `get_market_data_service_v2()` calls | 0 |

## GitNexus Spot Checks

GitNexus was refreshed for repo
`g2-37-service-lifecycle-di-candidate-refresh-after-tdx-helper` at HEAD
`6e940a7a5596b4256f63fec888c589777456d36a`.

| Target | Risk | Direct impact | Processes | Modules | Interpretation |
|---|---:|---:|---:|---:|---|
| `get_tdx_service` | LOW | 1 | 0 | 0 | Dashboard helper callers are closed; graph sees installer fallback, while text scan still shows `/api/tdx` dependency surface |
| `get_market_data_service_v2` | LOW | 1 | 0 | 0 | Market route and dashboard helper direct callers remain closed; public fallback remains |
| `get_stock_search_service` | LOW | 1 | 0 | 0 | Completed route-provider DI seam |
| `get_watchlist_service` | LOW | 3 | 0 | 2 | Route seam completed; remaining adapter/helper consumers stay separate |
| `get_strategy_service` | HIGH | 6 | 2 | 4 | Broad strategy seam; not a direct pilot |
| `get_tradingview_service` | LOW | 1 | 0 | 0 | Route/control-plane adjacent candidate, needs decision packet before source work |
| `get_integrated_services` | MEDIUM | 13 | 0 | 0 | Broad registry seam; not a direct pilot |
| `get_enhanced_data_service` | LOW | 1 | 0 | 0 | Health/control-plane adjacent, not a generic service pilot |
| `get_wencai_service` | LOW | 0 | 0 | 0 | No active route/test surface found |

## Interpretation

G2.37 does not select a new implementation target.

The strongest current-head delta is that the TDX dashboard helper surface is now
closed, but the TDX service still has a live public compatibility dependency
surface in `/api/tdx`. That should not be cleaned up or rewritten from this
refresh packet.

Recommended next gate:

- Prepare a decision-only G2.38 TDX route dependency consumer matrix.
- Scope it to `/api/tdx` dependency sites, `tdx_service.py` public fallback
  semantics, existing TDX tests, app-state installer behavior, and rollback
  boundaries.
- Keep source edits locked until that matrix is accepted and a separate
  implementation authorization packet defines exact write scope.

## Decision

- Source edits authorized: no
- Implementation lane selected: no
- Issue `#79` label movement authorized: no
- Compatibility getter deletion authorized: no
- Next recommended packet: G2.38 TDX route dependency consumer matrix
