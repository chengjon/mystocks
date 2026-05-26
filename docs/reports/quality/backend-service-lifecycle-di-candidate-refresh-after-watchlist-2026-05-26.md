# Backend Service Lifecycle DI Candidate Refresh After Watchlist - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Candidate refresh prepared for review.

This packet refreshes the remaining service lifecycle getter candidate pool after the WatchlistService getter-retirement closeout. It is governance-only and does not authorize source edits, tests edits, OpenSpec changes, PM2 execution, route changes, OpenAPI exposure changes, or issue-label movement.

## Parent State

| Field | Value |
|---|---|
| Parent PR | `#285` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-26T03:50:09Z` |
| Parent merge commit | `f0e0e37726140499b2e6b25cdad96739fc8f5462` |
| Parent title | `G2.132 Close out WatchlistService getter retirement` |
| Parent URL | `https://github.com/chengjon/mystocks/pull/285` |

## Current-Head Scan

Current HEAD: `f0e0e37726140499b2e6b25cdad96739fc8f5462`.

| Metric | Value |
|---|---:|
| Service Python files | `152` |
| Backend app Python files | `575` |
| Backend API Python files | `219` |
| Backend test Python files | `204` |
| Remaining service getter definitions | `11` |
| `get_announcement_service` definitions | `0` |
| `get_email_service` definitions | `0` |
| `get_stock_search_service` definitions | `0` |
| `get_watchlist_service` definitions | `0` |
| `_announcement_service` tokens | `0` |
| `_email_service` tokens | `0` |
| `_stock_search_service` tokens | `0` |
| `_watchlist_service` singleton assignments | `0` |
| `_watchlist_service` residual private helper tokens | `10` |

The residual `_watchlist_service` tokens are adapter private provider/helper names and local variables. They are not a module-level singleton and do not reintroduce the public `get_watchlist_service` compatibility getter.

## Candidate Inventory

| Candidate | Definition | Text-scan surface | GitNexus risk | Disposition |
|---|---|---:|---|---|
| `get_analysis_data_service` | `web/backend/app/services/__init__.py:272` | API direct `0`, app direct `1`, tests `0`, dependency refs `0` | LOW, impacted `0`, direct `0`, processes `0` | IntegratedServices facade hold |
| `get_cache_service` | `web/backend/app/services/__init__.py:296` | API direct `0`, app direct `1`, tests `0`, dependency refs `0` | LOW, impacted `0`, direct `0`, processes `0` | IntegratedServices facade hold |
| `get_data_api_service` | `web/backend/app/services/__init__.py:278` | API direct `0`, app direct `1`, tests `0`, dependency refs `0` | LOW, impacted `0`, direct `0`, processes `0` | IntegratedServices facade hold |
| `get_database_service` | `web/backend/app/services/__init__.py:284` | API direct `0`, app direct `1`, tests `0`, dependency refs `0` | LOW, impacted `0`, direct `0`, processes `0` | IntegratedServices facade hold |
| `get_trading_data_service` | `web/backend/app/services/__init__.py:266` | API direct `0`, app direct `1`, tests `0`, dependency refs `0` | LOW, impacted `0`, direct `0`, processes `0` | IntegratedServices facade hold |
| `get_websocket_service` | `web/backend/app/services/__init__.py:290` | API direct `0`, app direct `1`, tests `0`, dependency refs `0` | LOW, impacted `0`, direct `0`, processes `0` | IntegratedServices facade hold |
| `get_market_data_service` | `web/backend/app/services/__init__.py:260` | API direct `0`, app direct `1`, tests `1`, dependency refs `11` | LOW, impacted `0`; graph resolves to `web/backend/app/services/market_data_service/get_market_data_service.py` | Hold for graph/text symbol disambiguation |
| `get_data_service` | `web/backend/app/services/data_service.py:466` | API direct `3`, app direct `4`, tests `2`, dependency refs `0` | CRITICAL, impacted `4`, direct `3`, processes `7` | Hold: indicators/strategy data seam |
| `get_strategy_service` | `web/backend/app/services/strategy_service.py:455` | API direct `3`, app direct `7`, tests `0`, dependency refs `0` | CRITICAL, impacted `11`, direct `6`, modules `5` | Hold: strategy route/adapter/task seam |
| `get_streaming_service` | `web/backend/app/services/realtime_streaming_service.py:424` | API direct `0`, app direct `10`, tests `16`, dependency refs `0` | HIGH, impacted `9`, direct `9`, modules `4` | Hold: Socket.IO streaming seam |
| `get_tdx_service` | `web/backend/app/services/tdx_service.py:275` | API direct `0`, app direct `2`, tests `0`, dependency refs `7` | CRITICAL, impacted `4`, direct `2`, processes `5` | Hold: dashboard live-market seam |

## Recommendation

No direct implementation lane is selected by this refresh.

The only LOW graph-risk remaining candidates are shared IntegratedServices facade getters in `web/backend/app/services/__init__.py`. They are not equivalent to the already completed route-surface getter retirements because each delegates through `get_integrated_services()` and represents a shared composition-root ownership question.

Recommended next gate:

- Prepare an IntegratedServices facade getter ownership decision packet.
- Do not authorize deletion or migration of any `services/__init__.py` facade getter until that decision packet classifies whether the facade should be retained, wrapped, split, or retired as a group.
- Keep `get_market_data_service` on hold until graph/text symbol disambiguation is resolved.
- Keep `get_tdx_service`, `get_data_service`, `get_strategy_service`, and `get_streaming_service` on hold because their GitNexus risk is HIGH or CRITICAL.

## Verification

| Gate | Result |
|---|---|
| Parent PR state | `#285` is `MERGED` at `f0e0e37726140499b2e6b25cdad96739fc8f5462` |
| Current-head scan | Service getter definitions `11`; retired public getter definitions for Announcement, Email, StockSearch, and Watchlist remain `0` |
| GitNexus impact sampling | Six IntegratedServices facade getters LOW; `get_market_data_service` graph/text mismatch; `get_data_service`, `get_strategy_service`, `get_tdx_service` CRITICAL; `get_streaming_service` HIGH |

## Boundary

This refresh is not an implementation authorization. Future source work requires a separate authorization packet, explicit allowed paths, pre-edit GitNexus impact for edited symbols, TDD red/green proof, staged GitNexus scope check, mainline scope gate, and PR review.
