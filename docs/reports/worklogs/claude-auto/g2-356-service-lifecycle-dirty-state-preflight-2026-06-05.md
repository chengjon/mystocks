# G2.356 Service Lifecycle Dirty-State Preflight / No-Source

Date: 2026-06-05
Node: G2.356
Mode: service lifecycle dirty-state preflight / no-source
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `c3bf82211`
Parent report: `docs/reports/worklogs/claude-auto/g2-355-service-lifecycle-residual-cluster-inventory-2026-06-05.md`
Source edit authority: `false`

## Authorization Boundary

This node continues G2.355 without opening source authority. It is authorized only to classify dirty-state blockers and future authorization readiness for the service lifecycle residual cluster.

It is not authorized to edit source code, tests, generated governance files, route handlers, data-source providers, portfolio services, compatibility shims, or cache files. It does not reopen the cache line.

## Evidence Summary

- Current branch: `wip/root-dirty-20260403`.
- Current HEAD: `c3bf82211` (`refactor(web): split responsive sidebar styles`).
- G2.355 report recorded evidence at `c2b654288`; current HEAD has advanced. Any future source authorization must refresh evidence against the current HEAD.
- Staged changes: none.
- Worktree status is broadly dirty in the current environment: 840 modified entries, 113 deleted entries, and 467 untracked entries were detected by `git status --short`.
- G2.355 report remains untracked at this point:
  - `docs/reports/worklogs/claude-auto/g2-355-service-lifecycle-residual-cluster-inventory-2026-06-05.md`

## Dirty-State Findings

| Surface | Status | Dirty evidence | Preflight classification | Decision |
|---|---:|---|---|---|
| `web/backend/app/api/data_source_registry.py` | `M` | Diff stat: +1/-1. Changed area maps to `search_data_sources`. | Primary G2.355 target; dirty state blocks source authorization. | Do not edit. Future node must first reconcile whether this dirty change is intentional, stale, or belongs to another batch. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | `M` | Diff stat: +9/-9. Changed areas map to `get_strategy_data_source`, `get_strategy_definitions`, `run_strategy_single`, and `run_strategy_batch`. | Primary G2.355 target and strongest route-level residual candidate; dirty state blocks source authorization. | Do not edit. Future source work must start with dirty reconciliation plus impact analysis for touched symbols. |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | clean | Web backend factory implementation is clean. | Eligible for future preflight only if a concrete provider/import behavior is named. | No source work now. Keep as active implementation boundary. |
| `web/backend/app/services/data_source_factory.py` | clean | Compatibility import facade is clean. | Clean but compatibility-sensitive. | No retirement or rewrite without import-resolution proof. |
| `web/backend/app/services/data_source_factory/__init__.py` | clean | Package export boundary is clean. | Clean export surface. | No export contraction without consumer evidence. |
| `src/factories/data_source_factory.py` | clean | Core `src` factory surface is clean. | Separate ownership from web backend factory. | No consolidation. Future work requires separate core-factory preflight. |
| `src/data_sources/factory.py` | clean | Adjacent core data-source factory is clean. | Adjacent evidence only, not G2.355 source target. | Keep out of current service lifecycle source queue. |
| `service_registry.py` | absent | Exact basename still not found in tracked files. | No current target. | No edit/delete/migration decision possible. |
| `strategy_execution_router.py` | absent | Exact basename not found; concrete file is `_strategy_execution_router.py`. | Name-normalization issue only. | Future references should use the concrete current file path. |

## Adjacent Dirty Files

These dirty files are relevant to the service lifecycle cluster but are not source-authorization targets under G2.356.

| Adjacent file | Status | Cluster hit | Observed changed area | Boundary decision |
|---|---:|---|---|---|
| `web/backend/app/api/technical_analysis.py` | `M` | Web backend data-source factory | Diff stat: +17/-53; changed areas include `get_technical_analysis_data_source` and multiple indicator endpoints. | G2.330/G2.345-adjacent residual, not reopened by G2.356. Needs separate dirty reconciliation before any source work. |
| `web/backend/app/api/watchlist.py` | `M` | Web backend data-source factory | Diff stat: +0/-4; no current-definition mapping in this scan. | Prior residual surface; not reopened here. |
| `web/backend/app/api/data_quality.py` | `M` | Web backend data-source factory | Diff stat: +10/-1; changed area maps to `get_sources_health`. | Adjacent data-source lifecycle surface; no source work. |
| `web/backend/app/api/market/market_data_request.py` | `M` | Web backend data-source factory | Diff stat: +0/-2; no current-definition mapping in this scan. | Adjacent route consumer; no source work. |
| `tests/api/file_tests/test_strategy_management_api.py` | `M` | Strategy router and web backend data-source factory | Diff stat: +89/-4; changed areas include router module fixture and `TestStrategyManagementAPIFile`. | Test consumer is dirty. Future router source node must reconcile this first. |
| `tests/api/file_tests/test_data_source_registry_api.py` | `M` | Data-source registry | Diff stat: +0/-1. | Test consumer is dirty. Future registry source node must reconcile this first. |
| `web/backend/tests/_test_data_source_factory_management.py` | `M` | Web backend data-source factory | Diff stat: +0/-2. | Factory test-adjacent dirty state; no test edit authorized. |
| `web/backend/tests/_test_data_source_factory_convenience.py` | `M` | Web backend data-source factory | Diff stat: +0/-1. | Factory test-adjacent dirty state; no test edit authorized. |
| `scripts/watchlist_portfolio_demo.py` | `M` | Portfolio application service | Diff stat: +5/-8; changed areas include `demo_watchlist`, `demo_portfolio`, and `demo_prediction`. | Demo-adjacent only; not a portfolio service source blocker unless a future node targets demo/runtime behavior. |
| `scripts/test_strategy_portfolio_optimizer.py` | `M` | Strategy portfolio optimizer | Diff stat: +0/-2. | Script/test-adjacent only; not a primary service lifecycle source target. |
| `scripts/runtime/realtime_mtm_enhanced_demo.py` | `M` | Portfolio valuation services | Diff stat: +2/-6; changed areas include demo functions. | Demo-adjacent only; no portfolio service source work. |
| `tests/ddd/test_phase_5_validation.py` | `M` | Portfolio rebalancer service | Diff stat: +0/-2. | Dirty DDD test consumer; future portfolio service source work must account for it. |

## Portfolio Readiness Split

| Portfolio band | Primary files | Current readiness | Decision |
|---|---|---|---|
| Application service | `src/application/portfolio/portfolio_app_service.py` | Clean primary file, dirty demo consumer present. | Eligible only for future no-source caller inventory; not source-ready. |
| Domain valuation | `src/domain/portfolio/service/portfolio_valuation_service.py`, `portfolio_valuation_service_optimized.py` | Clean primary files, dirty realtime demo and DDD test consumers present. | Keep split. No merge/optimization authorization. |
| Domain rebalancing | `src/domain/portfolio/service/rebalancer.py`, `rebalancer_service.py` | Clean primary files, dirty DDD validation test consumer present. | Parallel service surfaces remain unresolved. No consolidation authorization. |
| Persistence | `src/infrastructure/persistence/portfolio_repository_impl.py` | Clean primary file. | Not dirty-blocked, but no named repository defect exists. |
| Web tracking | `web/backend/app/services/portfolio_tracker.py` | Clean primary file. | Not source-ready without consumer inventory and async/database test plan. |
| Backtest manager | `web/backend/app/backtest/portfolio_manager.py` | Clean primary file. | Separate backtest lifecycle surface; no domain merge authorization. |
| Monitoring optimizer | `src/monitoring/domain/portfolio_optimizer.py`, `web/backend/app/api/_monitoring_portfolio_router.py` | Clean primary files. | Monitoring-specific lifecycle surface; not part of data-source provider queue. |

## Authorization Readiness Table

| Candidate | Readiness for source node | Blocking evidence | Required next gate |
|---|---|---|---|
| Data-source registry route lifecycle | Not ready | Primary file and test consumer are dirty; current HEAD differs from G2.355 evidence HEAD. | Dirty-state reconciliation report for `data_source_registry.py` and `test_data_source_registry_api.py`; then impact analysis and focused API test plan. |
| Strategy execution router provider seam | Not ready | Primary file and route test consumer are dirty; changed areas include the provider helper and execution endpoints. | Dirty-state reconciliation report for `_strategy_execution_router.py` and `test_strategy_management_api.py`; then GitNexus impact for touched symbols. |
| Web backend factory implementation | Conditionally preflight-ready | Primary implementation is clean, but many route/test consumers are dirty. | Consumer inventory plus concrete provider/import defect statement. |
| Web backend factory compatibility facade | Not ready | Clean file, but compatibility role is ambiguous and import consumers are broad. | Import-resolution proof and explicit compatibility-retirement authorization. |
| Core `src` factories | Not ready | Separate ownership boundary; adjacent dirty consumers exist. | Separate core factory inventory, not mixed with web backend route lifecycle. |
| Portfolio lifecycle cluster | Not ready for source work | Primary files mostly clean, but cluster spans application/domain/infrastructure/web/backtest/monitoring and dirty demo/test consumers exist. | Select one portfolio band and gather caller/runtime evidence. |
| Service registry | No target | `service_registry.py` absent by exact basename. | Identify a concrete current file path before opening a gate. |

## Clean Continuation Boundary

G2.356 confirms that the next source-authorized service lifecycle work should not start from the broad cluster. The immediate safe continuation remains no-source:

1. Reconcile dirty primary targets before touching them.
2. Refresh evidence because `HEAD` advanced after G2.355.
3. Treat route/provider/test dirty state as a blocker, not as implicit permission.
4. Keep portfolio lifecycle work split by band instead of merging it into the data-source provider queue.
5. Keep cache closed.

## Closeout

G2.356 is complete as a no-source dirty-state preflight. It authorizes no code or test edits. It narrows the next eligible work to dirty-state reconciliation and evidence refresh, not source modification.
