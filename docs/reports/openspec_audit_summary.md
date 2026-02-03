# OpenSpec Audit Summary (Workspace Evidence)

Generated: 2026-02-02
Scope: Task completion checks against repository state. Items below are fact-checked from the workspace; unverified items are listed as gaps.

---

## extend-frontend-config-model

Evidence found:
- Route/page config types and data: `web/frontend/src/types/pageConfig.ts`, `web/frontend/src/config/pageConfig.ts`
- Page config generation/check scripts: `scripts/tools/generate-page-config.js`, `scripts/hooks/check-page-config.mjs`
- Docs: `docs/guides/PAGE_CONFIG_USAGE_GUIDE.md`, `docs/architecture/PAGE_CONFIG_MODEL.md`
- Unit/E2E tests: `web/frontend/tests/unit/config/pageConfig.test.ts`, `web/frontend/tests/e2e/artdeco-config-integration.spec.ts`
- Config usage in ArtDeco pages: `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue`, `ArtDecoStockManagement.vue`, `ArtDecoTradingManagement.vue`, `ArtDecoTechnicalAnalysis.vue`, `ArtDecoRiskManagement.vue`

Gaps / mismatches:
- `openspec/changes/.../tasks.md` header says completed but checklist is 62/85; 1.1–1.3 still unchecked.
- TypeScript compile / full E2E runs not verifiable from repo alone.

---

## implement-optimized-html-vue-artdeco-conversion

Evidence found:
- ArtDeco components + styles exist: `web/frontend/src/components/artdeco/`, `web/frontend/src/styles/artdeco-*.scss`
- Conversion docs: `docs/reports/HTML_TO_VUE_CONVERSION_GAP_ANALYSIS.md`, `docs/guides/MYSTOCKS_HTML_TO_VUE_CONVERSION_STRATEGY.md`

Gaps / mismatches:
- Many task claims not reflected in code. Example: `web/frontend/src/views/Market.vue` still uses Element Plus, not ArtDeco tables; several ArtDeco pages are placeholders.
- Visual regression tooling exists but no evidence of baseline runs.

---

## frontend-optimization-six-phase

Evidence found:
- Layouts exist: `web/frontend/src/layouts/MainLayout.vue`, `MarketLayout.vue`, `DataLayout.vue`, `RiskLayout.vue`, `StrategyLayout.vue`
- TS migration in many views (script setup lang="ts").
- TS env: `web/frontend/tsconfig.json`, `web/frontend/vite.config.ts`, `web/frontend/eslint.config.js`
- Pro K-line chart exists (path mismatch): `web/frontend/src/components/market/ProKLineChart.vue`

Gaps / mismatches:
- `theme-dark.scss` exists but not imported in `web/frontend/src/main.js`.
- Router uses `ArtDecoLayoutEnhanced.vue`, not new layouts.
- Testing/validation steps not verifiable.

---

## refactor-web-frontend-menu-architecture

Evidence found:
- Tokens: `web/frontend/src/styles/theme-tokens.scss`
- WebSocket manager: `web/frontend/src/utils/websocket-manager.ts` + tests
- Vite manualChunks: `web/frontend/vite.config.ts`
- TS config strict/allowJs: `web/frontend/tsconfig.json`
- Tooling configs: `web/frontend/eslint.config.js`, `.prettierrc`, `.stylelintrc.json`

Gaps / mismatches:
- No explicit pre-commit hook for frontend linting found.

---

## implement-frontend-routing-optimization (Complete)

Evidence found:
- Auth guard + permissions: `web/frontend/src/router/guards.ts`, `web/frontend/src/stores/auth.ts`
- Routes with `requiresAuth`: `web/frontend/src/router/index.ts`
- API client/store factory: `web/frontend/src/api/unifiedApiClient.ts`, `web/frontend/src/stores/storeFactory.ts`, `web/frontend/src/stores/apiStores.ts`
- Tests: `web/frontend/src/stores/__tests__/auth-guard.spec.ts`

Gaps / mismatches:
- E2E/performance validation not verifiable from repo.

---

## implement-html5-migration-experience-optimization

Evidence found:
- Manifest + icons: `web/frontend/public/manifest.json`, `web/frontend/public/icons/*`
- SW registration: `web/frontend/src/main.js` and SW file `web/frontend/public/sw.js`
- PWA meta tags: `web/frontend/index.html`
- Vite PWA plugin: `web/frontend/vite.config.ts`
- IndexedDB utility + usage: `web/frontend/src/utils/indexedDB.ts`, `web/frontend/src/stores/marketData.ts`
- Web workers: `web/frontend/src/utils/workersManager.ts`, `web/frontend/public/workers/indicator-calculator.js`

Gaps / mismatches:
- Manifest screenshots paths not found in `web/frontend/public/screenshots/`.
- Push subscription handling / backend not found.
- HTML5 APIs (geo/vibration/battery/network/orientation) not found.
- ant-design-vue still in `web/frontend/package.json`.
- Performance targets/CI verification not verifiable.

---

## implement-html-to-vue-conversion-merger

Evidence found:
- 9 HTML sources: `web/frontend/public/artdeco/*.html`, `web/frontend/artdeco-design/*.html`
- ArtDeco Vue pages exist: `web/frontend/src/views/artdeco-pages/ArtDeco*.vue`
- Routes configured: `web/frontend/src/router/index.ts`

Gaps / mismatches:
- Many routes point to placeholder components or reused pages rather than dedicated conversions.
- No clear merge of old Vue pages (e.g., `Dashboard.vue`) with converted pages.

---

## create-html-vue-conversion-analysis-docs

Evidence found:
- Multiple conversion reports/guides:
  - `docs/reports/HTML_TO_VUE_CONVERSION_GAP_ANALYSIS.md`
  - `docs/reports/MYSTOCKS_HTML_TO_VUE_CONVERSION_FINAL_REPORT.md`
  - `docs/guides/HTML_TO_ARTDECO_VUE_CONVERSION_PLAN.md`
  - `docs/guides/HTML_TO_ARTDECO_VUE_MERGE_PLAN.md`

Gaps / mismatches:
- Source directory `/opt/mydoc/design/example/` not verifiable in repo.
- Approval/formatting workflow not verifiable.

---

## update-web-design-system-v2

Evidence found:
- ArtDeco tokens: `web/frontend/src/styles/artdeco-tokens.scss`
- Global styles/animations: `web/frontend/src/styles/artdeco-global.scss`
- Density/quant styles: `web/frontend/src/styles/artdeco-quant-extended.scss`
- Menu styling: `web/frontend/src/styles/artdeco-menu.scss`

Gaps / mismatches:
- Chart theme still uses non-ArtDeco palette (`web/frontend/src/styles/chart-theme.ts`).
- Migration guide / docs for V2 not clearly present.
- Performance/verification steps not verifiable.

---

## implement-web-frontend-v2-navigation

Evidence found:
- ArtDeco domain routes exist: `web/frontend/src/router/index.ts`
- Menu config includes domain items: `web/frontend/src/layouts/MenuConfig.enhanced.ts`

Gaps / mismatches:
- Routes do not map to the expected v2 component names; many placeholders.
- Expected paths like `/market/overview` not present.
- Test/verification steps not verifiable.

---

## implement-pinia-api-standardization

Evidence found:
- Store factory and unified API client: `web/frontend/src/stores/storeFactory.ts`, `web/frontend/src/api/unifiedApiClient.ts`
- API stores: `web/frontend/src/stores/apiStores.ts`
- Auth store uses factory: `web/frontend/src/stores/auth.ts`
- Unit tests: `web/frontend/src/stores/__tests__/store-factory.spec.ts`

Gaps / mismatches:
- Migration of all stores not complete; cleanup and E2E/integration tests not verifiable.

---

## implement-typescript-type-extension-system

Evidence found:
- Extensions directory: `web/frontend/src/api/types/extensions/{index,market,strategy,common}.ts`
- Validator + scripts: `web/frontend/src/api/types/tools/validators/TypeValidator.ts`, `web/frontend/scripts/validate-types.js`
- Scripts in `web/frontend/package.json` (`type:validate`, `type:check:conflicts`)

Gaps / mismatches:
- `web/frontend/src/api/types/index.ts` does NOT export `./extensions` (validator would fail).
- Expected subdirectory structure under extensions not present.
- Pre-commit hook for type validation not found.

---

## implement-api-file-level-testing

Evidence found:
- Framework + CLI: `tests/api/file_tests/__init__.py`, `tests/api/file_tests/run_file_tests.py`
- Tests exist for many files: `tests/api/file_tests/test_*_api.py`
- Fixtures/standards: `tests/api/file_tests/conftest.py`, `docs/standards/API_FILE_TESTING_STANDARDS.md`
- CI workflow: `.github/workflows/api-file-tests.yml`

Gaps / mismatches:
- Runner/contract validator use placeholder logic; results are simulated.
- Full phase-4 validations not verifiable.

---

## implement-optimized-testing-strategy

Evidence found:
- ESM validation + tests: `scripts/test-runner/esm-validation.sh`, `web/frontend/tests/esm-dayjs-validation.test.ts`
- PM2/health check scripts: `scripts/automation/health_check.sh`, `scripts/test-runner/start-environment.sh`
- Schemathesis runner: `scripts/test-runner/run-schemathesis.sh`
- Playwright configs/tests: `web/frontend/playwright.config.ts`, `web/frontend/tests/**`
- Orchestration: `scripts/test-runner/run-orchestration.sh`
- Locust/perf scripts: `scripts/testing/load_test_locustfile.py`, `scripts/test-runner/run-performance-tests.sh`

Gaps / mismatches:
- Vite ESM alias claimed but mainly in `web/frontend/vitest.config.ts`.
- Full chain execution and CI confirmation not verifiable.

---

## comprehensive-testing-solution

Evidence found:
- Core modules exist: `tests/ai/*`, `tests/contract/models.py`, `tests/contract/test_executor.py`,
  `tests/performance/*`, `tests/data/quality_metrics.py`, `tests/chaos/*`, `tests/security/*`,
  `tests/test_runner.py`, `tests/test_report_generator.py`
- Reports exist: `reports/comprehensive_test_report.*`
- CI workflow exists: `.github/workflows/comprehensive-testing.yml`

Gaps / mismatches:
- `tests/contract/test_suites.py` missing though listed in tasks.
- Training/demo materials not clearly tied to this change.

---

## refactor-large-code-files

Evidence found:
- Duplicate files removed: `src/interfaces/adapters/akshare/market_data.py` absent; `src/domain/monitoring/` absent;
  `src/gpu/acceleration/gpu_acceleration_engine.py` absent; kept `src/adapters/akshare/market_data.py` and
  `src/gpu/api_system/utils/gpu_acceleration_engine.py`.
- Reports exist: `docs/reports/duplicate_code_analysis_report.md`, `docs/reports/import_path_migration_report.md`.
- Baselines exist: `tests/test_inventory_baseline.json`, `tests/duplicate_code_baseline.md`.

Gaps / mismatches:
- `openspec/changes/refactor-large-code-files/check-report.md` says 0% complete; tasks.md says many complete.
- Major splits not done: `web/backend/app/api/risk_management.py` (2112 lines), `web/backend/app/api/data.py` (1786),
  `src/database/database_service.py` (1392), `src/data_access.py` (1385).
- Large ArtDeco pages not split: `ArtDecoMarketData.vue` (3238), `ArtDecoDataAnalysis.vue` (2425).
- Claimed front-end component splits and pre-commit checks not found.
- Test file splits not found; large test files remain.

---

## mysql-to-postgresql-migration (ad hoc request)

Evidence found:
- MySQL compatibility mapped to PostgreSQL in core connection paths:
  `src/storage/database/connection_manager.py`, `src/storage/database/connection_context.py`,
  `src/core/config_driven_table_manager.py`, `src/storage/database/database_manager.py`
- Monitoring DB uses PostgreSQL with lazy MySQL import fallback: `src/monitoring/monitoring_service.py`
- DB utilities and health check updated to PostgreSQL: `src/storage/database/db_utils.py`, `src/utils/check_db_health.py`
- Example/maintenance scripts updated to PostgreSQL:
  `src/storage/database/execute_example_mysql_only.py`, `src/storage/database/fixed_example.py`,
  `src/storage/database/init_db_monitor.py`, `src/storage/database/fix_database_connections.py`,
  `src/storage/database/test_database_menu.py`, `src/storage/database/test_simple.py`
- Documentation/notes cleanup:
  `docs/architecture/DATABASE_ARCHITECTURE.md`, `docs/architecture/ARCHITECTURE_COMPARISON.md`,
  `docs/architecture/ARCHITECTURE_REVIEW_FIRST_PRINCIPLES.md`, `docs/tdx_integration/INTEGRATION_ANALYSIS.md`,
  `docs/WENCAI_INTEGRATION_QUICKREF.md`, `docs/design/20251121-spec优化建议.md`,
  `src/data_sources/README_TDX.md`, `src/data_sources/tdx_importer.py`,
  `src/core/batch_failure_strategy.py`, `src/storage/database/execute_example.py`
- Legacy doc cleanup (notes + targeted updates):
  `docs/legacy/archived/README_realtime_stock_saver.md`, `docs/legacy/archived/SAVE_REALTIME_DATA_USAGE.md`,
  `docs/legacy/archived/REALTIME_MARKET_SAVER.md`, `docs/legacy/archived/DATA_ROUTING_EXPLANATION.md`,
  `docs/legacy/archived/START_HERE.md`, `docs/legacy/archived/DB_FIX_README.md`,
  `docs/legacy/archived/QUANT_DATA_MANAGEMENT_GUIDE.md`, `docs/legacy/archived/改进意见1.md`,
  plus note injection for MySQL references under `docs/legacy/archived/` and `docs/architecture/legacy-cn/`
- Bulk replacement in legacy archived markdown: standardized MySQL/MariaDB references to PostgreSQL, leaving
  the legacy notice line intact for context.

Gaps / remaining MySQL references:
- MySQL-specific access module and compatibility enums remain in core interfaces/docs (non-runtime):
  `src/data_access/interfaces/i_data_access.py`, docs/legacy references
- MySQL patterns remain in docs/legacy and reports; not runtime-critical but still present in repo.
- Archived JSON snapshots still include MySQL strings (e.g. `docs/legacy/archived/database_assessment_20251019_165817.json`).
- Archived JSON/YAML snapshots under `docs/legacy/**` normalized to PostgreSQL; legacy notice lines remain in markdown.
- Architecture review/first-principles docs still contain historical MySQL comparisons (annotated with notes).

---

## refactor-large-files

Evidence found:
- API v1 structure exists: `web/backend/app/api/v1/**`, `web/backend/app/api/v1/router.py`.
- Type generation script supports multi-file output: `scripts/generate_frontend_types.py`.
- Some trading components exist: `web/frontend/src/views/artdeco-pages/components/ArtDecoTradingStats.vue`.

Gaps / mismatches:
- `web/backend/app/api/akshare_market.py` still 1377 lines; `mystocks_complete.py` still 1253 lines.
- Trading split incomplete: missing `ArtDecoTradingOrders.vue`, `ArtDecoStrategyForm.vue`, `ArtDecoTradingFilter.vue`,
  `ArtDecoTradingExport.vue`, `useTradingData.ts`, `api/trading.ts`, `api/orders.ts`, `styles/.../trading-management.scss`.
- Risk split not done: `web/backend/app/api/risk_management.py` still 2112 lines; no new services/models found.
- Large ArtDeco advanced components remain 1500–2400 lines.
- Quant strategy validator not split: `scripts/ci/quant_strategy_validation.py` is 4046 lines; no `scripts/ci/validators/`.
- Test file splits not done.
- File size hooks/CI checks not found.

---

## integrate-fullstack-platform

Evidence found:
- Router uses ArtDeco layout + lazy loading; `/` redirects to `/dashboard`: `web/frontend/src/router/index.ts`.
- CORS configured in backend: `web/backend/app/main.py` (allow_origins = ["*"]).
- API v1 routers exist: `web/backend/app/api/v1/**`.
- API client with JWT/CSRF interceptors: `web/frontend/src/api/apiClient.ts`, `web/frontend/src/utils/request.ts`.
- Startup script exists: `scripts/runtime/run_platform.sh`.

Gaps / mismatches:
- Task routes like `/market-quotes`, `/analysis`, `/backtest`, `/stock-management`, `/settings` not in router.
- Global menu uses legacy paths (e.g., `/tdx-market`): `web/frontend/src/config/menu.config.js`.
- `.env.development` / `.env.production` not present in repo (generated at runtime).
- `run_platform.sh` is not at repo root.
- JWT refresh not implemented (401 clears token + redirect).
- Integration/performance tests not verifiable from repo.

---

## optimize-data-source-v2

Evidence found:
- Core modules exist: `src/core/data_source/smart_cache.py`, `circuit_breaker.py`, `data_quality_validator.py`,
  `smart_router.py`, `metrics.py`, `batch_processor.py`.
- DataSourceManagerV2 creates SmartCache/LRU per endpoint and CircuitBreaker per endpoint: `src/core/data_source/base.py`.
- Unit tests exist: `tests/unit/test_smart_cache.py`, `tests/unit/test_circuit_breaker.py`,
  `tests/unit/test_data_quality_validator.py`, `tests/unit/test_smart_router.py`.
- Grafana dashboard config exists: `grafana/dashboards/data-source-metrics.json`.
- Prometheus alert rules exist: `monitoring-stack/config/rules/data-source-alerts.yml`.
- Docs/reports exist: `docs/reports/DATA_SOURCE_OPTIMIZATION_PHASE1_COMPLETION_REPORT.md`,
  `docs/reports/DATA_SOURCE_OPTIMIZATION_FINAL_SUMMARY.md`,
  `docs/guides/DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md`.

Gaps / mismatches:
- SmartCache/CircuitBreaker not actually used in DataSourceManagerV2 calls; `_call_endpoint` does not reference cache
  or circuit breakers: `src/core/data_source/handler.py`.
- CircuitBreaker integration for each endpoint is unused; no call wrapping in `_call_endpoint`.
- SmartRouter is not wired into routing; `get_best_endpoint` is simple priority/score sort, no SmartRouter weights:
  `src/core/data_source/router.py`.
- DataQualityValidator not integrated into governance GPU validator: `src/governance/engine/gpu_validator.py`.
- Prometheus metrics collector exists but is not wired into `_call_endpoint` or `/metrics` endpoint; current `/metrics`
  is from performance middleware: `src/core/data_source/metrics.py`,
  `web/backend/app/core/middleware/performance.py`, `web/backend/app/main.py`.
- Tests missing: `tests/unit/test_metrics.py` and `tests/integration/test_batch_processing.py` not found.
- BatchProcessor not integrated into governance fetcher bridge; no thread pool or batch flow in
  `src/governance/core/fetcher_bridge.py`.
- Performance/acceptance benchmarks and A/B tests are not verifiable from repo artifacts.

---

## expand-akshare-data-sources

Evidence found:
- AkShare market adapter mixins implement new endpoints:
  `src/adapters/akshare/market_adapter/market_overview.py`,
  `stock_profile.py`, `stock_sentiment.py`, `fund_flow.py`,
  `forecast_analysis.py`, `board_sector.py`.
- API endpoints exist for market overview, stock info, fund flow, forecast, board/sector:
  `web/backend/app/api/akshare_market.py`.
- Data source registry includes new endpoints with quality rules:
  `config/data_sources_registry.yaml` (e.g., `akshare.stock_sse_summary`,
  `akshare.stock_hsgt_fund_flow_summary_em`, `akshare.stock_profit_forecast_em`,
  `akshare.stock_board_concept_cons_em`).
- Tests exist for adapter and API surface:
  `tests/adapters/test_akshare_adapter.py`,
  `tests/api/test_akshare_market_file.py`,
  `tests/api/file_tests/test_akshare_market_api.py`.

Gaps / mismatches:
- Router prefix is `/api/akshare/market`, but tests call `/api/akshare-market/...` paths, likely causing 404s
  unless an alias exists: `web/backend/app/api/akshare_market.py`, `tests/api/test_akshare_market_file.py`.
- Task section 6 (stock_news_main_em, zt/dt pools, strong/weak pools, stock_changes_em, stock_new_em)
  not implemented in adapter or API (no matches in code).
- Unchecked task variants (stock_hot_follow_xq, stock_board_change_em) are not implemented.
- Caching and batch request optimizations for AkShare market endpoints are not present in
  `src/adapters/akshare/market_adapter/*`.
- Execution of integration/performance/data quality tests is not verifiable from repo artifacts.

---

## enhance-api-contract-management-integration

Evidence found:
- Zod is installed; runtime contract validator and OpenAPI-to-Zod converter exist in
  `web/frontend/src/api/unifiedApiClient.ts`.
- Contract validation interceptor wired into unified API client; global error handling for
  ContractValidationError in `web/frontend/src/main.js`.
- Frontend tests for runtime validation: `web/frontend/src/api/__tests__/unifiedApiClient.contract.test.ts`.
- Contract CI workflow exists with type generation + breaking change reporting:
  `.github/workflows/api-contract-validation.yml`.
- Backend contract services and routes exist: `web/backend/app/api/contract/*`.
- Contract test tooling and failure analysis scripts exist:
  `tests/contract/test_api_contract_schemathesis.py`,
  `tests/contract/report_generator.py`,
  `scripts/analyze_contract_test_failures.py`.

Gaps / mismatches:
- Frontend validator fetches `/api/contracts/{name}/active`, but backend exposes
  `/api/contracts/versions/{name}/active`; contract fetch likely fails unless another route exists.
- Breaking change detection in CI is placeholder (no base-branch diff; report notes TODO).
- Contract tests were not moved out of `tests/contract/` (task 3.2 incomplete).
- Version negotiator lacks migration path calculation and auto-adaptation; no tests found.
- Contract impact analysis service/UI not implemented (no ContractImpactAnalyzer in code).
- Prometheus/Grafana metrics and health checks for contract validation not found.
- Documentation updates for runtime validation/impact analysis/best practices not evident.
- End-to-end, performance, and security validation runs not verifiable from repo.

---

## consolidate-technical-debt-remediation

Evidence found:
- Ruff fix reports and summaries exist: `docs/code_quality/ruff_fix_report.md`,
  `docs/code_quality/backend_code_quality_final_summary.md`.
- Pre-commit config present: `.pre-commit-config.yaml`, `.pre-commit-hooks.yaml`.
- CSRF testing mode wiring exists in backend settings and middleware:
  `web/backend/app/core/config.py`, `web/backend/app/main.py`.
- E2E auth helper implemented with CSRF flow + tests:
  `web/frontend/tests/e2e/helpers/auth.ts`, `web/frontend/tests/e2e/helpers/auth.spec.ts`.
- Test configuration files exist: `pytest.ini`, `mypy.ini`, `pyproject.toml`.

Gaps / mismatches:
- Pylint cleanup not verifiable; error reports still present (e.g., `reports/pylint-errors.json`).
- MyPy fixes claimed but no verifiable run output; only config/report docs exist.
- Test coverage targets and integration/E2E coverage improvements not verifiable from repo artifacts.
- Planned file splits not completed: `src/data_access.py`, `src/adapters/tdx/tdx_adapter.py`,
  `src/adapters/financial_adapter.py` still monolithic.
- TODO/FIXME cleanup, complexity reduction, and security/performance remediation not evidenced in code.

---

## add-smart-quant-monitoring

Evidence found:
- DB schema + indices + advanced risk columns + latest-score view: `scripts/migrations/001_monitoring_tables.sql`.
- Async DB access layer exists (v1 + v3): `src/monitoring/infrastructure/postgresql_async.py`,
  `src/monitoring/infrastructure/postgresql_async_v3.py`.
- Event bus includes `metric_update` type and batch save via v3: `src/monitoring/async_monitoring.py`.
- FastAPI startup/shutdown initializes/closes async pool: `web/backend/app/main.py`.
- API endpoints implemented for watchlists + analysis: `web/backend/app/api/monitoring_watchlists.py`,
  `web/backend/app/api/monitoring_analysis.py`.
- Migration script exists: `scripts/migrations/migrate_watchlist_to_monitoring.py`.
- Domain calculators present: `src/monitoring/domain/market_regime.py`, `calculator_cpu.py`,
  `calculator_gpu.py`, `calculator_factory.py`, `risk_metrics.py`.
- Frontend monitoring views/components exist: `web/frontend/src/views/monitoring/WatchlistManagement.vue`,
  `web/frontend/src/views/monitoring/RiskDashboard.vue`, `web/frontend/src/components/chart/HealthRadarChart.vue`,
  `web/frontend/src/api/monitoring.ts`.

Gaps / mismatches:
- Phase 1.2 mismatch: `src/monitoring/infrastructure/postgresql_async.py` defines `PostgreSQLAsyncAccess`
  (not `MonitoringPostgreSQLAccess`), lacks `get_watchlist_with_stocks()` / `get_health_score_history()`, no
  async health check, and `batch_save_health_scores()` omits advanced risk fields; v3 has these but duplicates
  the contract and both layers are referenced.
- Phase 1.3 retry mechanism not implemented; `MonitoringEvent.retry_count` exists but no retry handling in
  `MonitoringEventWorker` (only fallback cache for publisher).
- Phase 1.4 health check endpoint for async pool not found (pool monitoring uses SQLAlchemy); config updates for
  required env vars not evident.
- Phase 2.1: `DYNAMIC_WEIGHTS` constant not present in `market_regime.py`; no backtest report or unit tests
  (`tests/unit/test_market_regime_identifier.py` missing).
- Phase 2.2: CPU calculator uses per-stock loop + synthetic data generation, not vectorized; no unit test
  (`tests/unit/test_vectorized_calculator.py` missing) or performance report.
- Phase 2.3: GPU calculator does not reuse `src/gpu/core/hardware_abstraction/resource_manager.py`, lacks cuDF
  integration, and no GPU unit test (`tests/unit/test_gpu_calculator.py` missing).
- Phase 2.4: Advanced risk metrics implemented in `risk_metrics.py` but not integrated into CPU/GPU calculators;
  `tests/unit/test_advanced_risk_metrics.py` missing.
- Phase 2.5: Factory exists, but `tests/unit/test_calculator_factory.py` missing.
- Phase 2.6: E2E/perf/stress/backtest tests and reports missing (`tests/integration/test_health_calculation_e2e.py`).
- Phase 3: `monitoring_analysis` does not publish `metric_update` events; watchlist API lacks batch add endpoint;
  `web/backend/app/models/monitoring.py` contains SQLAlchemy models unrelated to the Pydantic models described
  in tasks.
- Phase 3.4: Admin endpoint `/admin/migrate-watchlists` not found; `scripts/migrations/verify_migration.py` missing.
- Phase 4: PortfolioAnalysis view + `StockHealthCard.vue` / `RiskMetricsCard.vue` components not found; radar
  chart exists under `components/chart/` rather than `components/monitoring/`.
- Test coverage for async DB access and metric update workflow not found:
  `tests/unit/test_postgresql_async.py`, `tests/integration/test_metric_update_events.py`.

---

## add-unit-tests-ci-cd

Evidence found:
- Pytest deps present: `requirements-dev.txt` (pytest, pytest-cov, pytest-asyncio).
- Pytest config with coverage outputs: `pytest.ini` (htmlcov + json + cov-fail-under).
- Test structure + core unit tests exist:
  `tests/unit/test_data_classification.py`,
  `tests/unit/test_core_components.py`,
  `tests/unit/core/test_config_driven_table_manager.py`,
  `tests/unit/core/test_unified_manager_*`.
- API tests exist (mostly file-level + smoke): `tests/api/test_*`, `tests/api/file_tests/test_*`.
- Mypy config + pre-commit hook: `mypy.ini`, `.pre-commit-config.yaml`.
- Frontend test tooling installed: `web/frontend/package.json` (vitest, @vue/test-utils, jsdom/happy-dom, vue-tsc),
  with `web/frontend/vitest.config.ts`.
- Frontend test structure exists: `web/frontend/tests/unit/**`, `web/frontend/tests/e2e/**`,
  Playwright configs (`web/frontend/playwright.config.ts`, root `playwright*.config.ts`).
- CI/CD workflows exist for quality, tests, coverage, security, type checking, and deploy:
  `.github/workflows/code-quality.yml`, `frontend-testing.yml`, `python-type-check.yml`,
  `typescript-type-check.yml`, `test-coverage.yml`, `security-testing.yml`, `deploy.yml`.
- Security scans include bandit/safety/npm audit: `.github/workflows/security-testing.yml`.
- Performance/Lighthouse scripts and config exist: `scripts/cicd_pipeline.sh`,
  `scripts/tests/web-usability-runner.sh`, `config/lighthouse.config.json`.

Gaps / mismatches:
- Root `package.json` lacks pytest/coverage scripts (only frontend has `npm run test`); task 1.1 callout not met.
- Mypy not configured for full strict mode (`disallow_untyped_defs` remains false): `mypy.ini`.
- Specific frontend component unit tests named in tasks not found (ArtDecoCard/StatCard/Button/Table/Input/Select).
- Backend API integration tests for JWT/CORS/WebSocket not clearly present; many API tests are file-level placeholders.
- Coverage targets in tasks (>80%) not enforced; pytest.ini sets `--cov-fail-under=30`.
- Codecov badges / PR coverage comments not evident in repo artifacts.
- Workflow naming differs (no explicit `python-tests.yml` / `vue-tests.yml`), though equivalents exist.

---

## add-quantitative-trading-algorithms

Evidence found:
- Algorithm directory structure exists: `src/algorithms/` with subfolders
  `classification/`, `pattern_matching/`, `markov/`, `bayesian/`, `ngram/`, `neural/`.
- Base framework + config + results + metadata models exist:
  `src/algorithms/base.py`, `config.py`, `results.py`, `metadata.py`, `types.py`.
- Algorithm implementations exist:
  `classification/svm_algorithm.py`, `decision_tree_algorithm.py`, `naive_bayes_algorithm.py`,
  `pattern_matching/{brute_force,kmp,bmh,ac}_algorithm.py`,
  `markov/hmm_algorithm.py`, `bayesian/bayesian_network_algorithm.py`,
  `ngram/ngram_algorithm.py`, `neural/neural_network_algorithm.py`.
- Managers for category-level integration exist:
  `src/algorithms/classification/__init__.py` (ClassificationManager),
  `src/algorithms/pattern_matching/__init__.py` (PatternMatchingManager).
- API/service layer exists (from API change): `web/backend/app/api/algorithms.py`,
  `web/backend/app/services/algorithm_service.py`, `web/backend/app/schemas/algorithm_schemas.py`.
- SQLAlchemy models/repository for algorithm model storage exist:
  `web/backend/app/repositories/algorithm_model_repository.py`.
- GPU resource manager used by several algorithms (SVM/DT/NB/HMM/N-gram/Neural) with cuML in
  classification/HMM implementations.

Gaps / mismatches:
- Database migration scripts for algorithm tables not found; no TDengine supertables; no
  `ConfigDrivenTableManager` updates or `MyStocksUnifiedManager` access methods for algorithms.
- GPU kernel engine extensions and cuDF integration not evident; GPU memory management is minimal.
- Cross-validation framework and performance metric aggregation not implemented (only config fields).
- Algorithm API coverage is partial; algorithm-specific routes described in tasks are not clearly present
  (general `/api/v1/algorithms/train/predict` exists; limited per-algorithm helpers).
- Frontend components for algorithm selection/config/results dashboards not found
  (no `web/frontend/src/components/algorithms/`).
- Monitoring/alerting integration for algorithm performance not found.
- Unit/integration/performance tests for algorithms not present in `tests/`.
- Caching/versioning/rollback/benchmark validation steps not evidenced.

---

## add-comprehensive-risk-management-system

Evidence found:
- Risk management domain structure exists: `src/governance/risk_management/` with
  `core`, `calculators/gpu_calculator.py`, and services (`stop_loss_engine.py`,
  `stop_loss_execution_service.py`, `stop_loss_history_service.py`,
  `alert_rule_engine.py`, `risk_alert_notification_manager.py`).
- Integration points with monitoring stack:
  `StopLossEngine` uses `src.monitoring.signal_recorder`,
  `GPURiskCalculator` uses `MonitoringEventPublisher` + enhanced cache manager.
- Risk management APIs are implemented:
  `web/backend/app/api/risk_management.py` and v1 routes in `web/backend/app/api/v1/risk/*`
  (alerts + stop-loss + health).
- Backend risk services exist:
  `web/backend/app/services/risk_management/*` (risk_base, risk_calculator,
  risk_monitoring, risk_dashboard, risk_alerts, risk_settings).
- Frontend risk views/components exist:
  `web/frontend/src/views/monitoring/RiskDashboard.vue`,
  `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`,
  `web/frontend/src/views/artdeco-pages/components/risk/*`.

Gaps / mismatches:
- No migration scripts found for `stop_loss_strategies` or `risk_alerts` tables;
  no explicit schema extension for monitoring tables in `scripts/migrations/`.
- Risk tables referenced in APIs (`risk_metrics`, `risk_alerts`) lack confirmed
  table definitions/migrations in repo.
- WebSocket real-time risk push not found (only SSE risk_alert events in
  `web/backend/app/api/sse_endpoints.py`).
- Grafana/Prometheus risk dashboards/alert rules not located.
- Tests for risk management modules (unit/integration/performance) not found.
- `RiskManagementCore` lacks `_publish_risk_event` but API calls it (potential integration gap).

---

## implement-file-directory-migration

Evidence found:
- File organizer script exists with dry-run support: `scripts/maintenance/organize-files.sh`.
- Tree linting script exists: `scripts/tree-lint.sh`.
- Pre-commit hook for tree-lint is configured: `.pre-commit-config.yaml` (tree-lint entry).
- Doc hooks exist for organizer usage: `.claude/hooks/post-tool-use-document-organizer.sh`,
  `docs/目录管理解决方案总结.md`, `docs/guides/task_plan.md`.

Gaps / mismatches:
- Root directory is far from minimal (dozens of files/dirs in repo root), violating the
  “≤5 core files” requirement.
- No evidence of completed `tree-lint` runs or enforcement results; root remains non-compliant.
- Scripts/doc relocation phases (P1–P3) not reflected; many legacy/extra directories remain at root.
- Phase 4 src boundary tightening not complete (duplicate/temporary dirs still present).

---

## mysql-to-postgresql-cleanup (follow-up)

Evidence found:
- Reference/meta tables now use PostgreSQL in `config/table_config.yaml` (MySQL block removed).
- Monitoring DB now enforces PostgreSQL only in `src/monitoring/monitoring_service.py`.
- Security scan connection-string pattern updated to PostgreSQL in `src/storage/database/security_check.py`.
- Removed MySQL/MariaDB aliases from runtime database managers:
  `src/storage/database/database_manager.py`,
  `src/storage/database/connection_manager.py`,
  `src/storage/database/connection_context.py`,
  `src/storage/database/db_utils.py`,
  `src/data_access/interfaces/i_data_access.py`.
- Core table-manager tests updated for PostgreSQL-only configs:
  `tests/unit/core/test_config_driven_table_manager.py`,
  `tests/unit/core/test_config_driven_table_manager_complete.py`.
- Monitoring service tests updated for PostgreSQL URLs and psycopg2 usage:
  `tests/unit/monitoring/test_monitoring_service.py`.
- MySQL-focused tests converted or removed in favor of PostgreSQL:
  `tests/unit/test_mysql_table_creation.py`,
  `tests/test_database_manager.py`,
  `tests/unit/storage/test_database_manager.py`,
  `tests/unit/storage/database/test_connection_manager*.py`,
  `tests/data_access/test_database_connection_manager.py`,
  `tests/test_security_encryption.py`,
  `tests/e2e/test_architecture_optimization_e2e.py`,
  `tests/acceptance/test_us2_config_driven.py`.

Gaps / mismatches:
- MySQL removal notices remain in runtime error messaging (`src/core.py`,
  `src/core/config_driven_table_manager.py`, `src/storage/database/connection_context.py`).
- Legacy/backup artifacts still contain MySQL references:
  `src/core/config_driven_table_manager.py.backup_20251108`,
  `src/adapters/financial_adapter.py.backup_1767777515`,
  `config/table_config.yaml.backup_20251108`,
  merge artifacts `config/merge`, `config/latest_wins`, `config/reject`.
- Generated reports still include MySQL strings (e.g. `config/coverage.json`, `config/pylint_report.json`).

---

## Pending (not audited yet)
None.

---

## Verification Runs (2026-02-03)

Actions taken (post-audit fixes):
- Fixed logging string syntax errors in `web/backend/app/main.py`,
  `web/backend/app/core/database.py`, `web/backend/app/core/socketio_manager.py`.
- Converted `tests/file_level/test_runner.py` to a valid module-level docstring (no syntax errors).
- Added package marker `tests/metrics/__init__.py` for metrics tests.
- Fixed E2E imports in `tests/e2e/test_dashboard_page.py` (relative package imports).
- Added `DataManager` alias in `tests/ai/test_data_manager.py` for monitoring tests.
- Fixed unmatched parentheses in `web/backend/app/services/risk_management/risk_base.py`.

Latest `pytest` status:
- Still failing due to external MySQL connectivity to `192.168.123.104`
  in `tests/integration/test_us1_acceptance.py` (permission/connection error).
- Additional syntax/import issues may remain; re-run required after MySQL handling.

Additional fixes since last run:
- Added missing `BaseModel` import in `tests/monitoring/test_monitoring_alerts.py`.
- Fixed extra parenthesis in `web/backend/app/services/risk_management/risk_base.py`.

Current `pytest -x` status:
- Stops immediately at MySQL connectivity failure in `tests/integration/test_us1_acceptance.py`.
