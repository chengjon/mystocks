# Backend Service Lifecycle Candidate Refresh After BacktestEngine

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Current HEAD: `32d0cfb1e02d1207301e632b44a94e74efdddf69`

Parent closeout: G2.141 / PR `#294`

Boundary note: this is a governance-only candidate refresh. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or other service lifecycle candidates. It does not authorize implementation.

## Purpose

Refresh the remaining service lifecycle DI candidate pool after the BacktestEngine singleton/getter retirement lane closed.

## Scan Snapshot

| Metric | Value |
|---|---:|
| Service Python files | 152 |
| Backend app Python files | 575 |
| Backend API Python files | 219 |
| Backend test Python files | 206 |
| `def get_*` definitions under `web/backend/app/services` | 53 |
| Root facade getters in `web/backend/app/services/__init__.py` | 7 |
| FastAPI dependency/provider getters | 9 |
| Zero-external-reference getter definitions | 0 |

BacktestEngine retired state:

| Token | Count under `web/backend/app/services` |
|---|---:|
| `get_backtest_engine` | 0 |
| `_backtest_engine` | 0 |

## Current Interpretation

The prior low-risk queue is exhausted. There is no remaining `def get_*` service getter with zero external references.

Remaining service lifecycle surfaces now fall into three categories:

- Active root/composition compatibility facades.
- Active FastAPI dependency/provider seams.
- HIGH/CRITICAL service getters that need design decomposition before any implementation.

## Held High-Risk Getters

| Getter | Risk | Impacted | Direct | Processes | Disposition |
|---|---:|---:|---:|---:|---|
| `get_tdx_service` | CRITICAL | 6 | 2 | 5 | Hold for design package |
| `get_data_service` | CRITICAL | 5 | 3 | 7 | Hold for design package |
| `get_strategy_service` | CRITICAL | 13 | 6 | 0 | Hold for design package |
| `get_streaming_service` | HIGH | 9 | 9 | 0 | Hold for design package |

Root facade current references:

| Facade | Reference count |
|---|---:|
| `get_integrated_services` | 1 |
| `get_risk_calculator` | 1 |
| `get_market_data_service` | 18 |
| `get_risk_monitoring` | 1 |
| `get_risk_alerts` | 1 |
| `get_risk_settings` | 2 |
| `get_risk_dashboard` | 2 |

FastAPI dependency/provider current references:

| Provider | Reference count |
|---|---:|
| `get_market_data_service_v2_dependency` | 17 |
| `get_market_data_service_dependency` | 15 |
| `get_indicator_registry_dependency` | 4 |
| `get_tdx_service_dependency` | 8 |
| `get_announcement_service_dependency` | 14 |
| `get_email_service_dependency` | 11 |
| `get_watchlist_service_dependency` | 11 |
| `get_stock_search_service_dependency` | 13 |
| `get_tradingview_service_dependency` | 10 |

## Decision

No direct implementation candidate is selected by this refresh.

The next step should be a design decision package for the remaining high-risk service getter cluster. That package should decide whether to split work by:

- Dashboard/TDX runtime seam.
- Indicator/data service seam.
- Strategy service adapter seam.
- Realtime streaming/socket seam.
- Root facade compatibility seam.
- Route dependency/provider governance seam.

## Next Gate

Recommended next lane:

G2.143 high-risk service getter strategy decision package.

Expected mode:

- Decision-only.
- No backend source/test edit.
- No getter deletion.
- No route/API or OpenAPI change.

## Non-Goals

- No source or test edit.
- No implementation authorization.
- No selection of a concrete source implementation lane.
- No route/API, OpenAPI, frontend, PM2, OpenSpec, or issue-label change.
