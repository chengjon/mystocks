# Backend Service Lifecycle DI Candidate Refresh After TDX Route Provider - 2026-05-24

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Workline: G2.42 service lifecycle DI candidate refresh after TDX route
  provider closeout
- Status: review-ready
- Current HEAD: `41b0d4db7f2c644cea9abf1ddd4112e695325dcc`
- Parent PR: `#181`, merged at `41b0d4db7f2c644cea9abf1ddd4112e695325dcc`
- Parent issue: `#79`
- Scope: governance and evidence only

Boundary note: this packet performs a current-head candidate refresh after the
G2.40/G2.41 TDX route provider migration and closeout. It does not authorize
backend source edits, tests, route changes, OpenAPI changes, PM2/runtime gate
execution, OpenSpec archive actions, compatibility getter deletion, issue label
movement, or a new implementation lane.

## Why This Refresh Exists

The steward tree gate after G2.41 says that after the TDX route provider
migration is merged and closed out, the next step is a fresh current-head service
lifecycle DI candidate refresh before selecting another source implementation
lane.

This refresh confirms the meaningful delta from G2.37:

- `/api/v1/tdx` dependency sites moved from five `Depends(get_tdx_service)`
  sites to five `Depends(get_tdx_service_dependency)` sites.
- `tdx_service.py` now has the complete app-state route-provider seam:
  `TDX_SERVICE_STATE_KEY`, `install_tdx_service(app, service=None)`,
  `get_tdx_service_dependency(request)`, and the retained compatibility
  fallback `get_tdx_service()`.
- `get_tdx_service()` remains public and active as a compatibility fallback.
- TDX route-provider migration is closed, but no compatibility getter retirement
  is authorized.

## Current GitHub State

- Issue `#79`: `OPEN`, label `needs-triage`.
- Issue `#92`: `OPEN`, labels `enhancement`, `ready-for-human`,
  `ready-for-downstream`.

No issue labels were changed by this refresh.

## Scan Method

- Service root: `web/backend/app/services`
- Service files scanned: `152`
- Narrow candidate criteria:
  - `get_*service*`, `install_*service*`, or `get_service_*` functions
  - `*_instance = None` or `_instance = None`
  - `app.state.*service` references or explicit `SERVICE_STATE_KEY` usage
- Reference surfaces:
  - `web/backend/app/api`
  - `web/backend/tests`
  - other files under `web/backend/app/services`
- Normalization rule:
  - package `__init__.py` re-export surfaces are recorded separately from
    route/provider implementation candidates;
  - zero-reference service getters are not treated as implementation-ready
    without an ownership/usefulness decision packet.

## Scan Summary

| Bucket | Count | Interpretation |
|---|---:|---|
| `completed-route-provider-seam` | 7 | Previously completed route/provider seams remain closed; TDX is now included here |
| `route-surface-or-control-plane-review` | 1 | Route/control-plane adjacent candidate needs a separate decision packet |
| `broad-data-or-strategy-seam` | 4 | Broad seams are not suitable direct pilots |
| `process-runtime-singleton-or-streaming` | 2 | Runtime/streaming lifetime needs separate design |
| `service-internal-or-test-surface` | 2 | Internal/test surfaces are not route-provider pilots |
| `registry-integrated-seam` | 1 | Integrated registry remains a broad design seam |
| `ownership-usefulness-decision-needed` | 3 | Zero/low-reference surfaces need usefulness and ownership triage before implementation |
| `package-reexport-surface` | 1 | Package re-export surface is not an implementation candidate |

Current narrow candidate/signal files: `21`.

## Candidate Inventory

| Service file | Bucket | API refs | Test refs | Service refs | Signals |
|---|---|---:|---:|---:|---|
| `web/backend/app/services/__init__.py` | `registry-integrated-seam` | 1 | 4 | 3 | `get_integrated_services`, `get_market_data_service`, `get_trading_data_service`, `get_analysis_data_service`, `get_data_api_service`, `get_database_service`, `get_websocket_service`, `get_cache_service` |
| `web/backend/app/services/advanced_analysis_service.py` | `ownership-usefulness-decision-needed` | 0 | 0 | 0 | `get_advanced_analysis_service` |
| `web/backend/app/services/announcement_service.py` | `completed-route-provider-seam` | 1 | 1 | 0 | `get_announcement_service`, `get_announcement_service_dependency`, `install_announcement_service`, app-state service |
| `web/backend/app/services/data_service_enhanced.py` | `route-surface-or-control-plane-review` | 1 | 0 | 0 | `get_service_health`, `get_enhanced_data_service` |
| `web/backend/app/services/data_service.py` | `broad-data-or-strategy-seam` | 2 | 2 | 0 | `get_data_service` |
| `web/backend/app/services/email_notification_service.py` | `service-internal-or-test-surface` | 0 | 2 | 1 | `get_email_service` |
| `web/backend/app/services/email_service.py` | `completed-route-provider-seam` | 1 | 2 | 1 | `get_email_service`, `get_email_service_dependency`, `install_email_service`, app-state service |
| `web/backend/app/services/market_data_service_v2.py` | `completed-route-provider-seam` | 2 | 2 | 0 | `get_market_data_service_v2`, `get_market_data_service_v2_dependency`, `install_market_data_service_v2` |
| `web/backend/app/services/market_data_service/get_market_data_service.py` | `ownership-usefulness-decision-needed` | 1 | 4 | 3 | `get_market_data_service` |
| `web/backend/app/services/monitoring_service.py` | `service-internal-or-test-surface` | 0 | 0 | 0 | `_instance` |
| `web/backend/app/services/realtime_streaming_service.py` | `process-runtime-singleton-or-streaming` | 0 | 2 | 1 | `get_streaming_service` |
| `web/backend/app/services/stock_search_service/__init__.py` | `package-reexport-surface` | 0 | 0 | 0 | app-state service |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `completed-route-provider-seam` | 2 | 4 | 1 | `get_stock_search_service`, `get_stock_search_service_dependency`, `install_stock_search_service`, app-state service |
| `web/backend/app/services/strategy_service.py` | `broad-data-or-strategy-seam` | 1 | 1 | 2 | `get_strategy_service`, `_instance` |
| `web/backend/app/services/tdx_service.py` | `completed-route-provider-seam` | 2 | 2 | 0 | `get_tdx_service`, `get_tdx_service_dependency`, `install_tdx_service`, `_instance`, app-state service |
| `web/backend/app/services/technical_analysis_service.py` | `broad-data-or-strategy-seam` | 0 | 0 | 0 | `_instance` |
| `web/backend/app/services/tradingview_widget_service.py` | `completed-route-provider-seam` | 1 | 1 | 0 | `get_tradingview_service`, `get_tradingview_service_dependency`, `install_tradingview_service`, app-state service |
| `web/backend/app/services/unified_data_service.py` | `broad-data-or-strategy-seam` | 0 | 0 | 0 | `get_unified_data_service` |
| `web/backend/app/services/watchlist_service.py` | `completed-route-provider-seam` | 1 | 2 | 2 | `get_watchlist_service`, `get_watchlist_service_dependency`, `install_watchlist_service`, app-state service |
| `web/backend/app/services/websocket_service.py` | `process-runtime-singleton-or-streaming` | 0 | 0 | 0 | `get_service_stats` |
| `web/backend/app/services/wencai_service.py` | `ownership-usefulness-decision-needed` | 0 | 0 | 0 | `get_wencai_service` |

## Direct Getter Matrix

| Surface | Count |
|---|---:|
| `dashboard_data_source.py` direct `get_tdx_service()` calls | 0 |
| `dashboard_data_source.py` private `_get_tdx_service()` calls | 3 |
| `tdx.py` `Depends(get_tdx_service)` sites | 0 |
| `tdx.py` `Depends(get_tdx_service_dependency)` sites | 5 |
| `tdx.py` direct `get_tdx_service()` calls | 0 |
| `tdx_service.py` `get_tdx_service()` definitions | 1 |
| `tdx_service.py` `get_tdx_service_dependency()` definitions | 1 |
| `tdx_service.py` `install_tdx_service()` definitions | 1 |
| `market_v2.py` direct `get_market_data_service_v2()` calls | 0 |
| `dashboard_data_source.py` direct `get_market_data_service_v2()` calls | 0 |

## OpenAPI Smoke

The current-head `app.main` / OpenAPI smoke produced:

| Field | Value |
|---|---:|
| Runtime routes | 548 |
| OpenAPI paths | 500 |
| Operation IDs | 536 |
| Duplicate operation IDs | 0 |
| TDX paths | 7 |

The smoke emitted the known optional GPU dependency warning:
`Numba needs NumPy 2.2 or less. Got NumPy 2.4.` The command still exited
successfully and produced the expected route/OpenAPI results.

## Interpretation

G2.42 does not select a new implementation target.

The strongest current-head delta is that the TDX route dependency surface is now
closed and belongs in `completed-route-provider-seam`. The remaining candidate
pool is not a clean direct implementation queue:

- broad data/strategy seams remain too wide for direct migration;
- runtime/streaming services need lifetime design before source edits;
- zero-reference service getters need ownership/usefulness triage before being
  promoted, retained, or deprecated;
- package re-export surfaces are not service lifecycle migration targets.

Recommended next gate:

- Prepare a decision-only G2.43 service candidate usefulness and ownership
  triage packet.
- Scope it to zero/low-reference surfaces such as
  `advanced_analysis_service.py`, `wencai_service.py`, and
  `market_data_service/get_market_data_service.py`, plus any broad seam that
  needs explicit exclusion.
- Keep source edits locked until that triage packet is accepted and a separate
  implementation authorization packet defines exact write scope.

## Decision

Record G2.42 as a current-head refresh only.

- Do not retire `get_tdx_service()` from this packet.
- Do not reopen the completed route-provider seams.
- Do not move issue `#79` to implementation-ready state.
- Do not create or modify OpenSpec changes from this packet.
- Do not select the next service implementation target from this packet.
