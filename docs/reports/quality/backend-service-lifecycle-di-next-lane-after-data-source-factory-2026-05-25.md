# Backend Service Lifecycle DI Next-Lane After DataSourceFactory - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.86 service lifecycle DI next-lane decision

Status: ready for review

Branch: `g2-86-service-lifecycle-next-lane-decision`

Current HEAD: `ed033a45552a22b6ce4027a04029ea0764d191cf`

Prepared at: `2026-05-25T16:18:43+08:00`

## Purpose

Select the next service lifecycle DI lane after the DataSourceFactory public
compatibility getter retirement was closed by PR `#238`.

This packet is decision-only. It does not authorize backend source edits, test
edits, route/API edits, OpenAPI changes, frontend changes, runtime/PM2 work,
OpenSpec changes, issue-label changes, public getter deletion, dependency
provider removal, or private initializer creation.

## Input State

| Item | Current state |
|---|---|
| PR `#238` | `MERGED` at `ed033a45552a22b6ce4027a04029ea0764d191cf` |
| Issue `#79` | `OPEN`, `needs-triage` |
| Issue `#92` | `OPEN`, `enhancement`, `ready-for-human`, `ready-for-downstream` |
| DataSourceFactory public compatibility getter | Retired and closed |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

## Current-Head Candidate Scan

The scan below is a current-head planning signal. It is not a deletion backlog.

| Candidate | Current-head evidence | GitNexus spot check | Disposition |
|---|---|---|---|
| `get_advanced_analysis_service` / `AdvancedAnalysisService` | Python hits=`4`; production hits=`2`; route/API direct hits=`0`; test hits=`2`; provider refs=`19`; route provider refs=`15`; lifecycle tests `4 passed` | LOW / impacted count `0` | Select as the next authorization candidate for Phase 1 service-internal decoupling only |
| `get_stock_search_service` / `StockSearchService` | Production exact hits=`4`; route/API direct hits=`0`; package export lines=`2`; prior G2.23 matrix says keep as active compatibility surface | CRITICAL / impacted count `6`, stale-aware route-process noise from route provider sites | Do not reopen cleanup here; requires a fresh dedicated compatibility decision before any deletion |
| `get_data_service` / `DataService` | Production hits=`6`; route/API hits=`5` in indicator and strategy surfaces | CRITICAL / impacted count `4`; modules: Indicators, Strategy | Broad data seam; hold for separate design, not ordinary cleanup |
| `get_strategy_service` / `StrategyService` | Production hits=`11`; route/API hits=`4`; adapter/task consumers remain | CRITICAL / impacted count `11`; modules: Data_adapters, Strategy_management, Adapters, Tasks | Broad strategy seam; hold for separate design, not ordinary cleanup |
| `get_market_data_service_v2` / `MarketDataServiceV2` | Dashboard helper route/provider fallback still has route/API hits=`2` | Not rerun in this packet | Hold; dashboard helper consumer surface remains distinct |
| `get_tdx_service` / `TdxService` | Dashboard helper provider fallback still has route/API hits=`2` | Not rerun in this packet | Hold; dashboard helper consumer surface remains distinct |

## Selected Next Lane

Select `AdvancedAnalysisService` compatibility getter Phase 1 service-internal
decoupling as the next authorization candidate.

The future G2.87 authorization packet may define a source-capable implementation
lane with this intended shape:

- add a private async initializer such as
  `_get_or_create_advanced_analysis_service()`;
- retarget `get_advanced_analysis_service_dependency()` so its fallback no
  longer calls the public compatibility getter;
- keep public `get_advanced_analysis_service()` in Phase 1;
- keep `get_advanced_analysis_service_dependency()`,
  `install_advanced_analysis_service()`, and
  `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- update focused lifecycle tests only;
- run GitNexus impact before source edits;
- run focused lifecycle, health route, ruff/black, OpenAPI, staged GitNexus,
  and mainline gates before commit.

Any public getter deletion, rename, package-surface removal, route/API edit, or
OpenAPI exposure change must remain locked until a later closeout plus separate
final-retirement authorization.

## Verification Evidence

| Check | Result |
|---|---|
| `test_advanced_analysis_service_lifecycle_di.py` | 4 passed in 4.20s |
| `test_health_route_conflicts.py` | 120 passed in 78.00s |
| OpenAPI smoke with root `.env` loaded | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |
| `get_advanced_analysis_service` current-head scan | production hits=`2`, route/API hits=`0`, tests=`2` |
| GitNexus `get_advanced_analysis_service` impact | LOW, impacted count=`0` |
| GitNexus `get_data_service` impact | CRITICAL, impacted count=`4` |
| GitNexus `get_strategy_service` impact | CRITICAL, impacted count=`11` |
| GitNexus `get_stock_search_service` impact | CRITICAL, impacted count=`6`; treated as stale-aware against current text scan |
| GitNexus `detect_changes(scope=staged)` | LOW, changed files=`4`, changed symbols=`0`, affected processes=`0` |

## Boundary Confirmation

This G2.86 packet does not authorize:

- backend source edits;
- test edits;
- route/API edits;
- route path, response model, response shape, or OpenAPI exposure changes;
- frontend edits;
- runtime or PM2 changes;
- OpenSpec changes;
- GitHub issue-label changes;
- public `get_advanced_analysis_service()` deletion;
- `get_advanced_analysis_service_dependency()` removal;
- `install_advanced_analysis_service()` removal;
- any broad `DataService` or `StrategyService` migration.

## Next Gate

Human review / PR merge decision for this G2.86 decision packet.

If accepted, create a separate G2.87 source-capable authorization packet for
`AdvancedAnalysisService` Phase 1 service-internal decoupling before any source
edit.
