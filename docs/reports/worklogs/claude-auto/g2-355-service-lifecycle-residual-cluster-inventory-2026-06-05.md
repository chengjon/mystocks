# G2.355 Service Lifecycle Residual Cluster Inventory / No-Source

Date: 2026-06-05
Node: G2.355
Mode: service lifecycle residual cluster inventory / no-source
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `c2b654288`
Parent queue: G2.330 service lifecycle residual candidates
Source edit authority: `false`

## Authorization Boundary

This node is an inventory-only governance pass. It is authorized to identify the remaining service lifecycle residual cluster, classify surfaces, and record a decision table. It is not authorized to edit source code, tests, route handlers, service modules, compatibility shims, data-source providers, portfolio services, or cache files.

This node does not reopen any closed cache batch. The cache modernization line is treated as closed before G2.355 starts.

## Evidence Commands

- Loaded the function-tree governance rules for G-node work.
- Recalled the G2.330 residual queue from context memory.
- Ran local static inventory scripts over git-tracked files and untracked names using `git ls-files`, `git ls-files --others --exclude-standard`, and derived summaries only.
- No source files or tests were edited.

## Requested Scope Result

| Requested item | Current repo match | Git status | Inventory result |
|---|---:|---:|---|
| `data_source_registry.py` | `web/backend/app/api/data_source_registry.py` | `M` | Active API registry surface with router handlers plus startup/shutdown lifecycle hooks. Existing dirty state blocks source authorization. |
| `data_source_factory.py` | `src/factories/data_source_factory.py` | clean | Core `src` factory surface with `DataSourceFactory` and module-level `get_data_source`. Separate from web backend factory ownership. |
| `data_source_factory.py` | `web/backend/app/services/data_source_factory.py` | clean | Three-line compatibility import facade. Inventory only; no retirement or rewrite authorized. |
| `data_source_factory.py` | `web/backend/app/services/data_source_factory/data_source_factory.py` | clean | Web backend data-source factory implementation with async factory helpers and global factory accessors. Active service lifecycle owner. |
| `service_registry.py` | none found by exact basename in tracked or untracked files | n/a | No current file target located. No edit/delete/migration decision can be inferred. |
| `strategy_execution_router.py` | none found by exact basename | n/a | Exact name absent; current concrete match is `_strategy_execution_router.py`. |
| `_strategy_execution_router.py` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | `M` | Active strategy router residual surface. Contains direct `DataSourceFactory()` construction and `.get_data_source(...)` use. Existing dirty state blocks source authorization. |
| `portfolio_*.py` related lifecycle files | multiple portfolio service, repository, router, optimizer, tracker, and backtest surfaces | mixed clean/dirty adjacent scripts | Batch classified below; no portfolio source/test work authorized. |

## Service Lifecycle Surface Inventory

### A. Data-Source Registry And Factory Band

| Surface | Evidence | Lifecycle classification | Decision | Future authorization condition |
|---|---|---|---|---|
| `web/backend/app/api/data_source_registry.py` | 583 lines; `router = APIRouter`; 7 route decorators; async handlers including `search_data_sources`, `get_data_source`, `update_data_source`, health checks; `startup_event` and `shutdown_event`; status `M`. | API registry lifecycle surface. It combines route contract, registry reads/writes, health checks, auth guard, and startup/shutdown lifecycle hooks. | Keep in inventory as an active lifecycle surface. Do not edit under G2.355. Dirty state must be treated as pre-existing workspace state. | A separate source node must first reconcile existing dirty diff, identify a concrete defect or target behavior, run route impact analysis, and define tests. |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | 344 lines; class `DataSourceFactory`; async `get_data_source_factory`, `get_data_source`, `get_market_data`, `get_dashboard_data`, `get_technical_analysis_data`; imports config and data adapters; clean. | Canonical web-backend data-source factory lifecycle implementation. | Keep as active service owner. No provider rewrite, singleton rewrite, or API behavior change authorized. | Source work requires named consumer behavior, impact analysis, and route/service tests. |
| `web/backend/app/services/data_source_factory/__init__.py` | 20 lines; re-exports mode/config/source classes plus `DataSourceFactory` and `get_data_source_factory`; clean. | Package export boundary for the web-backend factory package. | Keep as package surface. No export contraction authorized. | Only eligible if a future source node proves unused export or broken import contract with tests. |
| `web/backend/app/services/data_source_factory.py` | 3 lines; `from data_source_factory import *`; clean. | Compatibility import facade / ambiguous legacy surface. | Record as a residual compatibility candidate, not a deletion candidate. | Retirement requires import-resolution proof, runtime import checks, and explicit compatibility-layer authorization. |
| `src/factories/data_source_factory.py` | 89 lines; class `DataSourceFactory`; module-level `get_data_source`; imported by maintenance scripts and validators; clean. | Separate `src` factory surface, not the same ownership boundary as web backend `app.services.data_source_factory`. | Keep separate from web backend lifecycle decisions. No consolidation authorized. | Any consolidation requires a dedicated architecture/source proposal because it crosses `src` and `web/backend` boundaries. |
| `src/data_sources/factory.py` | 515 lines; class `DataSourceFactory`; singleton helper; typed source getters; clean. | Adjacent core data-source factory, discovered through DataSourceFactory references but not an exact requested `data_source_factory.py` basename. | Adjacent evidence only. Do not add it to G2.355 source scope. | If it becomes target, open a separate core data-source factory inventory/source preflight. |

### B. Strategy Execution Router Band

| Surface | Evidence | Lifecycle classification | Decision | Future authorization condition |
|---|---|---|---|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 550 lines; `router = APIRouter`; 6 route decorators; async `get_strategy_data_source`; direct `DataSourceFactory()` construction and `.get_data_source(...)`; status `M`. | Active route-level strategy execution lifecycle residual. It is the concrete current match for the requested strategy execution router item. | Keep as the primary non-cache service lifecycle residual candidate from this batch. No source edit authorized because the file is already dirty. | A future source node must start by reconciling the existing dirty diff, confirming the intended provider seam, running GitNexus impact for touched symbols, and defining focused API tests. |
| `web/backend/app/api/strategy_management/__init__.py` | Imports `_strategy_execution_router` by module name; clean. | Router composition/registration consumer. | Consumer evidence only. No action. | Include as impact evidence if the router is later changed. |
| `tests/api/file_tests/test_strategy_management_api.py` | References the router module; status `M`. | Existing dirty test consumer / local workspace state. | Do not edit or normalize under G2.355. | Any future test changes require explicit source/test authorization and dirty-state reconciliation. |

### C. Portfolio Lifecycle Band

| Surface | Evidence | Lifecycle classification | Decision | Future authorization condition |
|---|---|---|---|---|
| `src/application/portfolio/portfolio_app_service.py` | `PortfolioApplicationService`; factory helper `create_portfolio_service`; clean. | Application service boundary for portfolio use cases. | In scope as portfolio service lifecycle inventory only. No source edit. | Source work requires a named application-service behavior or dependency lifecycle problem. |
| `src/domain/portfolio/service/portfolio_valuation_service.py` | `PortfolioValuationService`; repository dependency; clean. | Domain valuation service. | Keep as active domain service. No optimization or merge decision. | Any change must prove valuation behavior and concurrency impact with tests. |
| `src/domain/portfolio/service/portfolio_valuation_service_optimized.py` | `OptimizedPortfolioValuationService`; imports base valuation service and incremental calculator; clean. | Parallel optimized domain service surface. | Record as a parallel service candidate, not a duplicate-removal candidate. | Retirement or merge requires usage proof, performance/behavior comparison, and explicit source authorization. |
| `src/domain/portfolio/service/rebalancer.py` | `RebalancerService`; clean. | Domain rebalancing service surface. | Keep as active or legacy-unknown domain surface pending future evidence. | Needs caller/runtime evidence before any consolidation with `rebalancer_service.py`. |
| `src/domain/portfolio/service/rebalancer_service.py` | `RebalancerService`; imported by a dirty DDD test; clean. | Parallel rebalancing service surface. | Record as parallel service candidate. No merge or deletion authorized. | Future node must resolve consumer expectations and test coverage before touching either rebalancer file. |
| `src/infrastructure/persistence/portfolio_repository_impl.py` | `PortfolioRepositoryImpl`; application model/repository imports; clean. | Persistence lifecycle surface for portfolio application service. | Keep as infrastructure boundary. No repository rewrite. | Source work requires persistence contract evidence and database/test scope. |
| `web/backend/app/services/portfolio_tracker.py` | 623 lines; `PortfolioTracker`; async lifecycle-like methods; imports `db_service`; clean. | Web backend portfolio tracking service. | Keep as active web service surface. No lifecycle refactor authorized. | Future change requires service consumer inventory and async/database tests. |
| `web/backend/app/backtest/portfolio_manager.py` | `PortfolioManager`; imported by backtest engine/risk manager/tests; clean. | Backtest portfolio lifecycle surface, separate from app/domain portfolio services. | Keep separate; do not fold into domain portfolio services under this node. | Any consolidation requires backtest behavior tests and explicit architecture authorization. |
| `src/monitoring/domain/portfolio_optimizer.py` | `PortfolioOptimizer`; module-level `get_portfolio_optimizer`; consumed by monitoring portfolio router; clean. | Monitoring-domain optimizer lifecycle surface. | Keep as monitoring surface, not portfolio service rewrite scope. | Future work needs monitoring route behavior and optimizer lifecycle evidence. |
| `src/portfolio/strategy_portfolio_optimizer.py` | `StrategyPortfolioOptimizer`; imported by dirty script only in this scan; clean. | Standalone strategy portfolio optimizer surface. | Adjacent portfolio lifecycle candidate, not active web service owner by current evidence. | Promote only with runtime caller evidence beyond scripts/demo use. |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 346 lines; router with 3 async endpoints; imports calculator factory and portfolio optimizer; clean. | Portfolio monitoring API consumer of monitoring-domain lifecycle services. | Consumer evidence only. No route edit. | Include if optimizer lifecycle changes are later proposed. |

### D. Adjacent But Out Of G2.355 Source Scope

| Surface | Evidence | Boundary decision |
|---|---|---|
| `scripts/test_strategy_portfolio_optimizer.py` | Dirty script importing `src.portfolio.strategy_portfolio_optimizer`. | Script/demo/test-adjacent only. Not a service lifecycle source target in this node. |
| `scripts/watchlist_portfolio_demo.py` | Dirty demo script importing portfolio application service. | Demo-adjacent only. Not a source target in this node. |
| `openspec/changes/.../portfolio-optimization/spec.md` and `tests/changes/.../portfolio-optimization/spec.md` | Portfolio text specs, not runtime service lifecycle files. | Out of scope. |
| `web/frontend/src/api/portfolioAttribution.ts` and its test | Frontend API client/test, not backend service lifecycle source. | Out of scope. |
| Cache reports, cache helper files, cache tests, cache routes | Closed G2.346-G2.354 line. | Explicitly out of scope; not reopened. |

## Clean Boundary

G2.355 establishes this boundary:

1. Data-source registry/factory lifecycle surfaces are active and split across web backend, `src/factories`, and adjacent `src/data_sources`. They must not be treated as one interchangeable ownership surface.
2. `_strategy_execution_router.py` is the concrete strategy execution router residual found in the current tree, but it is already dirty and therefore cannot receive source authorization here.
3. Portfolio files form a broad lifecycle cluster across application, domain, infrastructure, monitoring, web service, and backtest layers. The evidence supports inventory and separation, not consolidation.
4. `service_registry.py` is not present by exact basename in tracked or untracked files. It cannot be a source-edit target until a concrete current file is identified.
5. Existing dirty files are evidence constraints, not authorization to modify them.

## Final Decision Table

| Band | Primary files | Current state | Decision | Authorized next action |
|---|---|---|---|---|
| Data-source registry | `web/backend/app/api/data_source_registry.py` | Active API lifecycle surface, dirty | Inventory only; no source work | Dirty-state reconciliation and named behavior preflight only |
| Web backend data-source factory | `web/backend/app/services/data_source_factory/data_source_factory.py`, package `__init__.py`, facade `data_source_factory.py` | Active implementation plus compatibility/export surfaces, clean | Keep separated; no rewrite/retirement | Dedicated source preflight if a concrete import/provider problem is proven |
| Core `src` data-source factory | `src/factories/data_source_factory.py`; adjacent `src/data_sources/factory.py` | Active/adjacent core factory surfaces, clean | Separate ownership from web backend | Separate core factory inventory if needed |
| Service registry | no `service_registry.py` found | Absent by exact current-file evidence | No target, no source decision | Identify a concrete file before any future node |
| Strategy execution router | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Active router residual, dirty | Primary route residual candidate; no source work | Dirty-state reconciliation, impact analysis, focused API tests |
| Portfolio lifecycle services | application/domain/infrastructure/web/backtest/monitoring portfolio files listed above | Broad layered cluster, mostly clean with dirty adjacent scripts/tests | Keep boundaries distinct; no consolidation | Future node must select one band and provide runtime/caller evidence |
| Cache line | closed G2.346-G2.354 reports | Closed | Do not reopen | None under G2.355 |

## Closeout

G2.355 is complete as a no-source inventory. It produces a single report, a single decision table, and a clean boundary. It authorizes no code or test edits.

Cache line formally remains closed. Service lifecycle residual governance is now separated into a new, lightweight inventory line.
