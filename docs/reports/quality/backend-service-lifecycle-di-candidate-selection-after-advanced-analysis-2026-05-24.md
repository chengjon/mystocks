# Backend Service Lifecycle DI Candidate Selection After AdvancedAnalysis - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Status: review-ready.

Boundary note: this packet records a G2.47 current-head service lifecycle DI
candidate selection only. It does not authorize backend source edits, test
edits, route behavior changes, OpenAPI exposure changes, docs/API updates,
generated client updates, frontend changes, PM2 execution, OpenSpec changes,
issue-label changes, compatibility getter retirement, or movement of any issue
to `ready-for-agent`.

## Source Snapshot

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-47-service-lifecycle-candidate-selection` |
| Branch | `g2-47-service-lifecycle-candidate-selection` |
| Current HEAD | `e09e6db4a6a85dc392c20a737e729bb6f123804d` |
| HEAD subject | `Merge pull request #186 from chengjon/g2-46-advanced-analysis-closeout-candidate-refresh` |
| Parent closeout PR | `#186`, `MERGED`, merge commit `e09e6db4a6a85dc392c20a737e729bb6f123804d` |
| Steward-tree guide PR | `#187`, `MERGED`, merge commit `02a4148c2b6edbb45dea6115a4ac9e57c4ba9b3e` |
| Issue `#79` state | `OPEN`, labels: `needs-triage` |
| Issue `#92` state | `OPEN`, labels: `enhancement`, `ready-for-human`, `ready-for-downstream` |

## Current-Head Scan Summary

| Metric | Value | Interpretation |
|---|---:|---|
| Service files scanned | `152` | Same broad service surface as recent G2 refreshes. |
| API files scanned | `219` | Route and API helper files included for dependency usage classification. |
| Provider modules detected | `8` | Completed service provider seam count after G2.45/G2.46. |
| Route provider dependency files | `11` | Route modules using `*_dependency` provider functions. |
| Route provider dependency sites | `72` | Current provider-based route injection footprint. |
| Route class `Depends()` files | `0` | No remaining `SomeService = Depends()` class injection pattern detected by this scan. |
| Route class `Depends()` sites | `0` | Confirms the AdvancedAnalysis class-dependency surface stayed closed. |
| Route getter dependency files | `51` | Mostly auth, DB, repository, and legacy dependency functions; not all are service lifecycle DI candidates. |
| Route getter dependency sites | `277` | Requires classification before any candidate can become implementation work. |
| Raw direct getter-call files | `112` | Noisy signal; includes helper methods and property-style getters that are not lifecycle singletons. |
| Raw direct getter-call sites | `707` | Planning signal only; not a deletion or implementation backlog. |
| Service getter definitions detected | `44` | Includes compatibility fallbacks, helpers, factories, and broad seams. |

## Completed Provider Seams

The scan detected these completed provider modules:

| Service module | Provider seam | State key |
|---|---|---|
| `web/backend/app/services/advanced_analysis_service.py` | `install_advanced_analysis_service`, `get_advanced_analysis_service_dependency` | `ADVANCED_ANALYSIS_SERVICE_STATE_KEY` |
| `web/backend/app/services/announcement_service.py` | `install_announcement_service`, `get_announcement_service_dependency` | `ANNOUNCEMENT_SERVICE_STATE_KEY` |
| `web/backend/app/services/email_service.py` | `install_email_service`, `get_email_service_dependency` | `EMAIL_SERVICE_STATE_KEY` |
| `web/backend/app/services/market_data_service_v2.py` | `install_market_data_service_v2`, `get_market_data_service_v2_dependency` | `MARKET_DATA_SERVICE_V2_STATE_KEY` |
| `web/backend/app/services/stock_search_service/stock_search_service.py` | `install_stock_search_service`, `get_stock_search_service_dependency` | `STOCK_SEARCH_SERVICE_STATE_KEY` |
| `web/backend/app/services/tdx_service.py` | `install_tdx_service`, `get_tdx_service_dependency` | `TDX_SERVICE_STATE_KEY` |
| `web/backend/app/services/tradingview_widget_service.py` | `install_tradingview_service`, `get_tradingview_service_dependency` | `TRADINGVIEW_SERVICE_STATE_KEY` |
| `web/backend/app/services/watchlist_service.py` | `install_watchlist_service`, `get_watchlist_service_dependency` | `WATCHLIST_SERVICE_STATE_KEY` |

Completed provider modules remain closed/retained. Their compatibility getters
must not be deleted from this packet.

## Candidate Classification

| Candidate | Evidence | GitNexus spot check | Classification | Disposition |
|---|---|---|---|---|
| `get_market_data_service` | `web/backend/app/api/market/market_data_request.py` has `7` `Depends(get_market_data_service)` route sites; tests already use dependency overrides; service package has direct getter and re-export; `market_data_adapter.py` also imports it as fallback | LOW / impacted count `0` for the indexed function | Active route dependency with compatibility and package-surface considerations | Select as next decision packet target: G2.48 consumer matrix / authorization candidate, not source edits in G2.47 |
| `get_data_service` | Direct API callers in indicator and strategy surfaces | CRITICAL / impacted count `4`; affected modules include Indicators and Strategy | Broad data seam | Exclude from immediate service lifecycle DI batch; requires separate broad data-seam design |
| `get_strategy_service` | Direct strategy-management, adapter, and task callers | CRITICAL / impacted count `11`; direct callers in strategy adapters, strategy management routes, and backtest tasks | Broad strategy seam | Exclude from immediate service lifecycle DI batch; requires separate strategy service design |
| `get_kronos_client` | Three direct route calls in `web/backend/app/api/v1/analysis/kronos.py`; regression tests monkeypatch it | CRITICAL / impacted count `3`; affects Kronos prediction/encoding/status flows | External-client seam | Exclude from ordinary service lifecycle DI batch; requires external-client provider gate |
| `get_indicator_registry` | Two direct calls in `indicator_cache.py`, internal indicator defaults/TALib jobs, many unit tests | LOW / impacted count `4`; affected modules Indicators and Jobs | Indicator-internal registry seam | Do not pick before a dedicated indicator registry/provider design; not a route-provider batch |
| `get_current_user`, `get_current_active_user`, `get_db`, repository getters | Many `Depends(...)` sites | Not evaluated as service lifecycle DI targets | Auth/DB/repository dependency functions | Out of this lane |

## Selected Next Gate

G2.47 selects **a decision packet target**, not an implementation target:

`get_market_data_service` should receive a G2.48 route dependency consumer matrix
and route-provider authorization candidate packet.

The G2.48 packet should answer:

- Which exact public route handlers in `market/market_data_request.py` use
  `Depends(get_market_data_service)`.
- Whether a future provider seam belongs in
  `web/backend/app/services/market_data_service/` or a narrower bridge module.
- How to preserve `get_market_data_service()` compatibility for tests,
  re-exports, and `market_data_adapter.py`.
- Whether `web/backend/tests/test_market_api_integration.py` can be the focused
  route dependency override test base.
- Whether this package-level `MarketDataService` lane must stay separate from
  `MarketDataServiceV2`.
- Which route/OpenAPI smoke and route dependency count guards are required.

## Non-Goals

This packet does not authorize:

- Adding `get_market_data_service_dependency`.
- Rewiring `market/market_data_request.py`.
- Removing or renaming `get_market_data_service`.
- Consolidating `MarketDataService` and `MarketDataServiceV2`.
- Changing route paths, response models, OpenAPI schema exposure, frontend code,
  docs/API examples, generated clients, PM2 workflows, or OpenSpec state.
- Moving issue `#79` or issue `#92` to `ready-for-agent`.

## Decision

G2.47 should be accepted as a candidate-selection packet if reviewers agree that:

- G2.46 is closed after PR `#186` merge.
- The next step is a `get_market_data_service` consumer matrix / authorization
  candidate packet.
- No new source implementation target is authorized yet.
- Broad or external-client seams remain excluded from the ordinary route-provider
  conveyor.

## Verification Notes

Fresh evidence used for this packet:

```text
service_files_scanned=152
api_files_scanned=219
provider_modules_count=8
route_provider_dependency_sites=72
route_class_dependency_sites=0
route_getter_dependency_sites=277
getter_defs_count=44
```

GitNexus spot checks:

| Target | Risk | Impacted count | Notes |
|---|---|---:|---|
| `get_market_data_service` | LOW | `0` | Still needs consumer matrix because route dependency and fallback surfaces are active. |
| `get_data_service` | CRITICAL | `4` | Broad data/indicator/strategy seam. |
| `get_strategy_service` | CRITICAL | `11` | Broad strategy/adapters/tasks seam. |
| `get_indicator_registry` | LOW | `4` | Indicator-internal registry/jobs seam. |
| `get_kronos_client` | CRITICAL | `3` | External-client route seam. |
