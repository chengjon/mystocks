# Old Main Migration Shortlist

Date: 2026-03-17

## Scope

- Source of candidates:
  `/tmp/mystocks_spec-old-main-untracked-2026-03-17.txt`
- Target baseline:
  `/opt/claude/mystocks_spec/.worktrees/origin-main-2026-03-17`
- Candidate count under `web/`, `src/`, `tests/`:
  `109`
- Existing overlap in clean worktree:
  `0`

This means the migration problem is primarily **new-file triage**, not merge conflict resolution.

## Recommend Migrate First

These files look directly aligned with the cleaned post-rewrite baseline and appear to represent missing feature slices rather than local scratch work.

- `web/frontend/src/api/services/dragonTigerService.ts`
- `web/frontend/src/api/services/fundFlowPageService.ts`
- `web/frontend/src/api/services/strategyPositionService.ts`
- `web/frontend/src/api/services/watchlistService.ts`
- `web/frontend/src/views/artdeco-pages/dashboardContract.ts`
- `web/frontend/src/views/artdeco-pages/dashboardViewModel.ts`
- `web/frontend/src/views/artdeco-pages/market-tabs/marketConceptContract.ts`
- `web/frontend/src/views/artdeco-pages/market-tabs/marketConceptViewModel.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyManagementHelpers.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyManagementViewModel.ts`
- `web/frontend/src/views/data/DataFundFlowPage.vue`
- `web/frontend/src/views/market/MarketDragonTigerPage.vue`
- `web/frontend/src/views/strategy/StrategyPositionPage.vue`
- `web/backend/app/api/strategy_management/backtest_status_contract.py`
- `web/backend/tests/test_strategy_backtest_contract.py`
- `web/backend/tests/test_dashboard_market_overview_path_regression.py`
- `tests/unit/api/test_dashboard_market_overview.py`

Reasoning:

- These files form recognizable vertical slices:
  dashboard, fund-flow, dragon-tiger, strategy-position, watchlist, and backtest-status contract.
- The names are coherent and mostly contract/view-model/service focused.
- The sample contents looked intentional and production-directed, not temporary scaffolding.

## Recommend Migrate With Their Tests

If the corresponding feature files above are moved, these tests should move in the same batch:

- `web/frontend/tests/e2e/dashboard.spec.ts`
- `web/frontend/tests/e2e/data-concept.spec.ts`
- `web/frontend/tests/e2e/data-fund-flow.spec.ts`
- `web/frontend/tests/e2e/market-lhb.spec.ts`
- `web/frontend/tests/e2e/strategy-pos.spec.ts`
- `web/frontend/tests/e2e/watchlist-manage.spec.ts`
- `web/frontend/tests/unit/config/dashboard-page-config.spec.ts`
- `web/frontend/tests/unit/config/data-concept-page-config.spec.ts`
- `web/frontend/tests/unit/config/data-fund-flow-page-config.spec.ts`
- `web/frontend/tests/unit/config/market-lhb-page-config.spec.ts`
- `web/frontend/tests/unit/config/strategy-pos-page-config.spec.ts`
- `web/frontend/tests/unit/config/watchlist-manage-page-config.spec.ts`
- `web/frontend/tests/unit/dashboard-service.spec.ts`
- `web/frontend/tests/unit/data-fund-flow-service.spec.ts`
- `web/frontend/tests/unit/market-concept-service.spec.ts`
- `web/frontend/tests/unit/market-lhb-service.spec.ts`
- `web/frontend/tests/unit/strategy-position-service.spec.ts`
- `web/frontend/tests/unit/watchlist-management-service.spec.ts`

## Review Before Migrating

These files may be valuable, but they look more like infrastructure refactors or large-file-splitting follow-ups. They should be reviewed in smaller batches.

- `src/adapters/efinance_adapter/efinance_data_source_methods/part3.py`
- `src/core/deduplication_strategy_methods/part3.py`
- `src/data_sources/real/postgresql_relational/postgre_sql_relational_data_source_methods/part3.py`
- `src/governance/risk_management/calculators/gpu_calculator/gpu_risk_calculator_methods/part3.py`
- `src/governance/risk_management/services/stop_loss_engine/stop_loss_engine_methods/part3.py`
- `src/gpu/accelerated/_cpu_fallback_components.py`
- `src/gpu/accelerated/_data_processor_gpu_batch.py`
- `src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/part3.py`
- `src/gpu/acceleration/optimization_gpu_methods/part3.py`
- `src/gpu/api_system/services/_integrated_backtest_service_stats.py`
- `src/gpu/api_system/services/_integrated_ml_service_stats.py`
- `src/gpu/api_system/services/resource_scheduler/resource_scheduler_methods/part3.py`
- `src/monitoring/gpu_performance_optimizer/_gpu_performance_optimizer_reporting.py`
- `src/storage/database/database_manager/database_table_manager_methods/part3.py`
- `tests/test_large_file_split_regressions.py`
- `tests/_large_file_split_regression_guards_legacy.py`

Reasoning:

- These look like incomplete split tails or helper shards.
- They may depend on neighboring tracked files that already changed in rewritten history.
- Blind migration here would be higher-risk than the frontend/backend vertical slices above.

## Probably Skip

These look like low-signal or archival additions unless you know they contain required business behavior:

- `web/frontend/src/views/demo/stock-analysis/code-examples.backtests.ts`
- `web/frontend/src/views/demo/stock-analysis/code-examples.monitors.ts`
- `web/frontend/src/views/demo/stock-analysis/code-examples.parsers.ts`
- `web/frontend/src/views/demo/stock-analysis/code-examples.strategies.ts`
- `web/frontend/src/views/converted.archive/README.md`
- `web/frontend/docs/worklogs/claude-auto/2026-03-07.md`
- `web/frontend/tests/templates/artdeco-test-template.ts`

## Recommended Migration Order

1. Frontend service + contract/view-model files
2. Matching backend contract/test files
3. Matching frontend unit/e2e tests
4. Split-tail Python files only after targeted review

## Next Safe Action

Copy only the `Recommend Migrate First` group into the clean worktree, review the diff there, and run targeted tests before touching the split-tail Python files.
