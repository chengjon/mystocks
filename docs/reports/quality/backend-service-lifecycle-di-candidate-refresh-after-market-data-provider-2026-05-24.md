# Backend Service Lifecycle DI Candidate Refresh After MarketDataService - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为参考。

## Status

Status: review-ready.

Workline: G2.51 current-head service lifecycle DI candidate refresh after
G2.49/G2.50 `MarketDataService` route-provider merge and closeout.

This packet is candidate refresh only. It does not authorize backend source
edits, tests, OpenSpec changes, route changes, or the next implementation
target.

## Source Snapshot

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-51-service-lifecycle-candidate-refresh` |
| Branch | `g2-51-service-lifecycle-candidate-refresh` |
| Current HEAD | `047f483dd70a5234ca3a128342511a56779194d3` |
| HEAD subject | `Merge pull request #191 from chengjon/g2-50-market-data-service-closeout` |
| Parent closeout PR | `#191`, `MERGED`, merge commit `047f483dd70a5234ca3a128342511a56779194d3` |
| Issue `#79` state | `OPEN`, labels: `needs-triage` |
| Issue `#92` state | `OPEN`, labels: `enhancement`, `ready-for-human`, `ready-for-downstream` |

## Current-Head Scan Summary

| Metric | Value | Interpretation |
|---|---:|---|
| Service files scanned | `152` | Same broad service package surface as recent G2 refreshes. |
| API files scanned | `219` | Route and API helper files included for dependency usage classification. |
| Provider modules detected | `8` | Completed service provider seam count after G2.49/G2.50. |
| Provider dependency functions detected | `8` | Current app-state provider function count under `web/backend/app/services`. |
| Route provider dependency files | `11` | API files using `*_dependency` provider functions. |
| Route provider dependency sites | `79` | Increased from `72` after the seven `MarketDataService` route sites moved to provider dependency. |
| Route getter dependency files | `51` | Mostly auth, DB, repository, and historical route-local provider dependencies. |
| Route getter dependency sites | `270` | Down from `277` after G2.49; not all are service lifecycle DI candidates. |
| Raw direct getter-call files | `236` | Noisy signal; includes factories, compatibility fallbacks, helpers, and property-style getters. |
| Raw direct getter-call sites | `1664` | Planning signal only, not a deletion or implementation backlog. |
| Service getter definitions detected | `68` | Includes compatibility fallbacks, helpers, factories, broad seams, and provider functions. |

Configured app/OpenAPI smoke:

| Field | Value |
|---|---:|
| Runtime routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Warnings captured | `121` |

The OpenAPI path count is a current schema-exposure snapshot. It must not be
treated as a permanent path-count baseline.

## Completed Provider Seams

| Provider function | Notes |
|---|---|
| `get_announcement_service_dependency` | Completed earlier in G2. |
| `get_email_service_dependency` | Completed earlier in G2. |
| `get_market_data_service_dependency` | Added by G2.49 and closed by G2.50. |
| `get_market_data_service_v2_dependency` | Completed in the separate `MarketDataServiceV2` lane. |
| `get_stock_search_service_dependency` | Completed earlier in G2. |
| `get_tdx_service_dependency` | Completed in the TDX route-provider lane. |
| `get_tradingview_service_dependency` | Completed earlier in G2. |
| `get_watchlist_service_dependency` | Completed earlier in G2. |

## MarketDataService Closure State

| Surface | Current value | Disposition |
|---|---:|---|
| `Depends(get_market_data_service)` in `/api/v1/market` route file | `0` | Route-provider surface closed. |
| `Depends(get_market_data_service_dependency)` in `/api/v1/market` route file | `7` | Authorized G2.49 conversion preserved. |
| Raw `get_market_data_service()` calls | `4` | Compatibility/fallback/internal surface, not a deletion candidate here. |

Residual `get_market_data_service()` references are limited to:

- `web/backend/app/services/market_data_service/get_market_data_service.py`
- `web/backend/app/services/__init__.py`
- `web/backend/app/services/market_data_adapter.py`

These references remain intentionally outside the G2.51 implementation scope.

## Candidate Classification

| Candidate | Current evidence | GitNexus spot check | Classification | Disposition |
|---|---|---|---|---|
| Ordinary route-provider candidate | No unhandled low-risk service route dependency comparable to `get_market_data_service` was found. Remaining `Depends(get_...)` sites are mostly auth, DB, repository, or historical route-local provider dependencies. | Not applicable | No immediate ordinary route-provider target | Do not start source implementation from G2.51. |
| `get_technical_pattern_detection_service` | One route-local `Depends(get_technical_pattern_detection_service)` in `web/backend/app/api/_technical_patterns_router.py`; this is the historical D2.1a technical-pattern DI surface, not a service-package app-state provider seam. | GitNexus symbol lookup did not index this route-local function. | Route-local historical provider surface | Do not reopen D2.1a here; if desired, create a separate route-local provider modernization decision packet. |
| `get_indicator_registry` | `0` legacy route `Depends(...)` sites; `8` raw calls across indicator API/service/defaults/TALib surfaces. | LOW / impacted count `4`; affected modules Indicators and Jobs. | Indicator-internal registry/jobs seam | Candidate for a dedicated indicator registry/provider design packet, not direct source implementation from G2.51. |
| `get_data_service` | `0` legacy route `Depends(...)` sites; `4` raw calls in indicator/strategy API and service surfaces. | CRITICAL / impacted count `5`; direct modules include Indicators and Strategy. | Broad data seam | Exclude from immediate service lifecycle DI implementation. Requires separate data-seam design. |
| `get_strategy_service` | `0` legacy route `Depends(...)` sites; `6` raw calls across strategy management routes, adapters, and tasks. | CRITICAL / impacted count `13`; modules include Data_adapters, Adapters, Strategy_management, Tasks. | Broad strategy seam | Exclude from immediate service lifecycle DI implementation. Requires separate strategy-seam design. |
| `get_kronos_client` | `0` legacy route `Depends(...)` sites; `4` raw calls in Kronos API and external client surfaces. | CRITICAL / impacted count `3`; affected module Analysis. | External-client route seam | Exclude from ordinary provider conveyor; requires dedicated external-client design. |

## Current Decision

No next source implementation target is selected in G2.51.

The route-provider conveyor has closed the currently authorized narrow
`MarketDataService` surface. The remaining interesting seams are either broad
data/strategy seams, external-client seams, indicator-internal registry design,
or a route-local historical provider surface. Each needs a separate human
decision or design packet before implementation.

## Recommended Next Gate

Create one of the following decision packets after G2.51 review:

1. `IndicatorRegistry` provider design packet, if the next goal is to handle the
   LOW-risk but indicator-internal registry/jobs seam.
2. Technical-pattern route-local provider modernization packet, if the next goal
   is to normalize the D2.1a route-local provider shape.
3. Broad data/strategy seam design packet, if the next goal is to handle
   CRITICAL `get_data_service` or `get_strategy_service` safely.

Do not start source edits until one of those packets is reviewed and explicitly
converted into an implementation authorization.

## Verification Notes

Fresh evidence used for this packet:

```text
service_files_scanned=152
api_files_scanned=219
provider_modules_count=8
provider_functions_count=8
route_provider_dependency_files=11
route_provider_dependency_sites=79
route_getter_dependency_files=51
route_getter_dependency_sites=270
raw_direct_getter_files=236
raw_direct_getter_sites=1664
service_getter_definitions=68
```

GitHub state:

| Item | State |
|---|---|
| PR `#191` | `MERGED`, merge commit `047f483dd70a5234ca3a128342511a56779194d3` |
| Issue `#79` | `OPEN`, label `needs-triage` |
| Issue `#92` | `OPEN`, labels `enhancement`, `ready-for-human`, `ready-for-downstream` |

GitNexus spot checks:

| Target | Risk | Impacted count | Notes |
|---|---|---:|---|
| `get_data_service` | CRITICAL | `5` | Broad data/indicator/strategy seam. |
| `get_strategy_service` | CRITICAL | `13` | Broad strategy/adapters/tasks seam. |
| `get_indicator_registry` | LOW | `4` | Indicator-internal registry/jobs seam. |
| `get_kronos_client` | CRITICAL | `3` | External-client route seam. |
| `get_technical_pattern_detection_service` | Not indexed | Not available | Route-local D2.1a surface; do not treat missing index as implementation approval. |
