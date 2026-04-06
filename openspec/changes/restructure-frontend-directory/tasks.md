# Implementation Tasks: Restructure Frontend Directory

## 1. Pre-flight (Phase 0 – Freeze & Planning)
- [x] 1.1 Add git pre-commit hook to block new `.vue` files under `src/views/` not in migration table
- [x] 1.2 Run `openspec validate restructure-frontend-directory --strict` to verify change package
- [x] 1.3 Create a tracking document (e.g., `MIGRATION_PROGRESS.md`) to log completed moves

## 2. Governance & Approval (Phase 1)
- [x] 2.1 Submit PR with OpenSpec change to Architecture Board for review
  - Submitted: 2026-03-02
  - Notification sent to Architecture Lead, Front-end Lead, Security Reviewer
- [x] 2.2 Obtain explicit sign-off (comment "APPROVED") from Architecture Lead
  - Status: ✅ APPROVED (2026-03-02)
- [x] 2.3 Obtain sign-off from Front-end Lead on the migration plan
  - Status: ✅ APPROVED (2026-03-02)
- [x] 2.4 Verify no conflicting changes in `openspec/changes/` (run `openspec list`)
  - Status: ✅ VERIFIED (2026-03-02)

## 3. Shared Asset Extraction (Phase 2)
- [x] 3.0 **Identify existing files at target locations**
  - Completed: 2026-04-04
  - Baseline recorded in `web/frontend/MIGRATION_PROGRESS.md`
  - [x] 3.0.1 List all files that already exist in `src/shared/components/` and `src/shared/composables/`
    - Result: no target files or directories existed in the repository baseline before this batch.
  - [x] 3.0.2 For each existing file, determine merge strategy:
    - Compare source and target file contents
    - Choose which version to keep (or merge both)
    - Run unit tests to verify functionality
    - Delete source file after merge
    - Result: no target-location conflicts existed, so no per-file merge was required in this batch.
    - Baseline drift found: the repo has no `src/views/shared/*` source tree; actual candidate extraction sources are `src/views/components/` and `src/views/composables/`.
- [x] 3.1 Create target directories: `src/shared/components/` and `src/shared/composables/`
  - Completed: 2026-04-04 via tracked `.gitkeep` placeholders
- Baseline note: tasks 3.2-3.4 still describe the approved target architecture, but execution must be remapped from actual current source locations recorded in `web/frontend/MIGRATION_PROGRESS.md` before any `git mv` starts.
  - 2026-04-04 remap result: candidate classification is now recorded in `web/frontend/MIGRATION_PROGRESS.md`.
  - Immediate scope conclusion: no files under `src/views/components/` qualify for direct Phase 2 shared extraction, and most `src/views/composables/` files are legacy root-page bundles that stay view-local.
  - Remaining live follow-up: only the `TradingDashboard` helper pair (`useTradingDashboard.ts` and `tradingDashboardActions.ts`) remains a conditional extraction candidate, pending task `8.5` trade-domain disposition.
- [ ] 3.2 Move all files from `src/views/shared/components/*` → `src/shared/components/` (use `git mv`)
- [ ] 3.3 Move all files from `src/views/shared/composables/*` → `src/shared/composables/` (use `git mv`)
- [ ] 3.4 Search for all imports of `@/views/shared/...` and update to `@/shared/...`
- [ ] 3.5 Run `npm run lint && npm run type-check` and fix any errors
- [ ] 3.6 Commit: "refactor: extract shared assets to src/shared/"

## 4. Page-by-Page Migration – Market Domain (Phase 3a)
- 2026-04-04 repo-truth note: tasks `4.1` through `4.6` are already structurally landed in the current repository.
  - Current router truth and generated `pageConfig.ts` already resolve the target domain pages under `src/views/market/` and `src/views/data/`.
  - The listed ArtDeco market/data source files now act as thin compatibility wrappers that forward into those routed target pages.
  - Remaining work in this area is compatibility-wrapper retirement and shared-layer normalization, not repeating the original literal `git mv`.
- [ ] 4.1 Move `artdeco-pages/market-tabs/MarketRealtimeTab.vue` → `views/market/Realtime.vue`
  - [ ] 4.1.0 **Identify all relative imports** (composables, styles, components) in the source file
  - [ ] 4.1.1 Move dependency: `useMarketData.ts` → `src/shared/composables/`
  - [ ] 4.1.2 Move dependency: `market.scss` → `src/shared/styles/`
  - [ ] 4.1.3 Update all imports in the moved file to use `@/shared/...` absolute paths
  - [ ] 4.1.4 Run `npm run lint && npm run type-check`
- [ ] 4.2 Move `artdeco-pages/market-tabs/MarketKLineTab.vue` → `views/market/Technical.vue`
  - [ ] 4.2.0 **Identify all relative imports**
  - [ ] 4.2.1 Move dependency: `useKlineAnalysis.ts` → `src/shared/composables/`
  - [ ] 4.2.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 4.2.3 Run lint & type-check
- [ ] 4.3 Move `artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` → `views/market/LHB.vue`
  - [ ] 4.3.0 **Identify all relative imports**
  - [ ] 4.3.1 Move dependencies to `src/shared/`
  - [ ] 4.3.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 4.3.3 Run lint & type-check
- [ ] 4.4 Move `artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` → `views/data/Industry.vue`
  - [ ] 4.4.0 **Identify all relative imports**
  - [ ] 4.4.1 Move dependency: `useIndustry.ts` to `src/shared/composables/`
  - [ ] 4.4.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 4.4.3 Run lint & type-check
- [ ] 4.5 Move `artdeco-pages/market-tabs/MarketConceptTab.vue` → `views/data/Concepts.vue`
  - [ ] 4.5.0 **Identify all relative imports**
  - [ ] 4.5.1 Move dependency: `useConcepts.ts` to `src/shared/composables/`
  - [ ] 4.5.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 4.5.3 Run lint & type-check
- [ ] 4.6 Move `artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` → `views/data/FundFlow.vue`
  - [ ] 4.6.0 **Identify all relative imports**
  - [ ] 4.6.1 Move dependency: `useFundFlow.ts` to `src/shared/composables/`
  - [ ] 4.6.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 4.6.3 Run lint & type-check
- [ ] 4.7 Commit: "refactor: migrate market domain pages"

## 5. Page-by-Page Migration – Data Domain (Phase 3b)
- 2026-04-04 repo-truth note: `5.1 Data-Indicator` has now completed its implementation inversion.
  - The target route and pageConfig continue to point to `src/views/data/Advanced.vue`.
  - Current repo truth is now aligned with the intended end state: `Advanced.vue` owns the primary implementation and `artdeco-pages/ArtDecoDataAnalysis.vue` has been reduced to a compatibility wrapper.
- [x] 5.1 Move `artdeco-pages/ArtDecoDataAnalysis.vue` → `views/data/Advanced.vue`
  - [x] 5.1.1 Remap dependency truth: the current repo uses `@/composables/market/useDataAnalysis`; no `useAdvancedData.ts` file exists to move in this batch.
  - [x] 5.1.2 Update imports
  - [ ] 5.1.3 Run lint & type-check
  - [ ] 5.1.4 Run unit tests for Advanced.vue
- [ ] 5.2 Commit: "refactor: migrate data domain pages"

## 6. Page-by-Page Migration – Watchlist Domain (Phase 3c)
- 2026-04-04 repo-truth note: the watchlist target pages did not exist in the repository baseline, so this batch lands the missing target entrypoints and retargets router/pageConfig to them.
  - `src/views/watchlist/Manage.vue` now fronts the existing `WatchlistManager.vue` implementation.
  - `src/views/watchlist/Signals.vue` now fronts the existing `StrategySignalsTab.vue` implementation for the watchlist route while preserving the strategy-domain reuse.
  - `src/views/watchlist/Screener.vue` now fronts the existing `stocks/Screener.vue` implementation.
  - Remaining work in this area is compatibility-wrapper retirement and dependency normalization, not leaving the watchlist domain on non-domain entry files.
- [ ] 6.1 Move `artdeco-pages/stock-management-tabs/WatchlistManager.vue` → `views/watchlist/Manage.vue`
  - [ ] 6.1.1 Move dependency: `useWatchlist.ts`
  - [ ] 6.1.2 Update imports
  - [ ] 6.1.3 Run lint & type-check
- [ ] 6.2 Move `stocks/Screener.vue` → `views/watchlist/Screener.vue`
  - [ ] 6.2.1 No dependencies to move
  - [ ] 6.2.2 Update imports
  - [ ] 6.2.3 Run lint & type-check
- [ ] 6.3 Move `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` → `views/watchlist/Signals.vue`
  - [ ] 6.3.1 Move dependency: `useStrategySignals.ts`
  - [ ] 6.3.2 Update imports
  - [ ] 6.3.3 Run lint & type-check
- [ ] 6.4 Commit: "refactor: migrate watchlist domain pages"

## 7. Page-by-Page Migration – Strategy Domain (Phase 3d)
- 2026-04-04 repo-truth note: the strategy target pages for tasks `7.1` through `7.4` did not exist in the repository baseline, so this batch lands the missing target entrypoints and retargets router/pageConfig to them.
  - `src/views/strategy/List.vue` now fronts the existing `ArtDecoStrategyManagement.vue` implementation.
  - `src/views/strategy/Parameters.vue` now fronts the existing `StrategyParametersTab.vue` implementation.
  - `src/views/strategy/Backtest.vue` now fronts the existing `ArtDecoBacktestAnalysis.vue` implementation.
  - `src/views/strategy/Optimization.vue` now fronts the existing `ArtDecoStrategyOptimization.vue` implementation.
  - Remaining work in this area is compatibility-wrapper retirement and dependency normalization, not leaving the strategy domain on non-domain entry files.
- [ ] 7.1 Move `artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` → `views/strategy/List.vue`
  - [ ] 7.1.1 Move dependency: `useStrategyList.ts`
  - [ ] 7.1.2 Update imports
  - [ ] 7.1.3 Run lint & type-check
- [ ] 7.2 Move `artdeco-pages/strategy-tabs/StrategyParametersTab.vue` → `views/strategy/Parameters.vue`
  - [ ] 7.2.1 Move dependency: `useStrategyParams.ts`
  - [ ] 7.2.2 Update imports
  - [ ] 7.2.3 Run lint & type-check
- [ ] 7.3 Move `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` → `views/strategy/Backtest.vue`
  - [ ] 7.3.1 Move dependency: `useBacktest.ts`
  - [ ] 7.3.2 Update imports
  - [ ] 7.3.3 Run lint & type-check
  - [ ] 7.3.4 Run unit tests for Backtest.vue
- [ ] 7.4 Move `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` → `views/strategy/Optimization.vue`
  - [ ] 7.4.1 Move dependency: `useOptimization.ts`
  - [ ] 7.4.2 Update imports
  - [ ] 7.4.3 Run lint & type-check
  - [ ] 7.4.4 Run unit tests for Optimization.vue
- [ ] 7.5 Commit: "refactor: migrate strategy domain pages"

## 8. Page-by-Page Migration – Trade Domain (Phase 3e)
- 2026-04-04 repo-truth note: the trade target pages for tasks `8.1` through `8.4` did not exist in the repository baseline, so this batch lands the missing target entrypoints and retargets the trade router/pageConfig entries to them.
  - `src/views/trade/Center.vue` now fronts the existing `ArtDecoTradingPositions.vue` implementation.
  - `src/views/trade/Signals.vue` now fronts the existing `ArtDecoSignalsView.vue` implementation.
  - `src/views/trade/Portfolio.vue` now fronts the existing `PortfolioOverviewTab.vue` implementation.
  - `src/views/trade/History.vue` now fronts the existing `ArtDecoTradingHistory.vue` implementation.
  - `trade-terminal` remains on `TradingDashboard.vue` per task `8.5` Option C; task `8.6` is now closed via `reconcile-dashboard-dealingroom-truth`.
- [x] 8.1 Move `artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` → `views/trade/Center.vue`
  - Completed: 2026-04-05 via repo-truth-aligned micro-batch `2026-04-05-restructure-trade-center-main`.
  - Result: `src/views/trade/Center.vue` now hosts the canonical positions implementation; `ArtDecoTradingPositions.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 8.1.0 **Identify all relative imports**
    - Evidence: the only local relative dependency in the original file was `./tradingDataTransform`.
  - [x] 8.1.1 Move dependency: `usePositions.ts` to `src/shared/composables/`
    - Repo-truth note: not applicable as written. The current positions page uses `apiClient` + `useArtDecoApi`, and the shared `usePositions()` helper already exists centrally in `src/composables/useTrading.ts`.
  - [x] 8.1.2 Update imports to use `@/shared/...` absolute paths
    - Evidence: the canonical page no longer depends on relative imports; `tradingDataTransform` now resolves through an absolute `@/views/...` import until the shared helper migration is executed in a later batch.
  - [x] 8.1.3 Run lint & type-check
  - [x] 8.1.4 Run unit tests for Center.vue
- [x] 8.2 Move `artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` → `views/trade/Signals.vue`
  - Completed: 2026-04-05 via repo-truth-aligned micro-batch `2026-04-05-restructure-trade-signals-main`.
  - Result: `src/views/trade/Signals.vue` now hosts the canonical signals implementation; `ArtDecoSignalsView.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 8.2.0 **Identify all relative imports**
    - Evidence: the original file depended on `../strategy-tabs/strategySignalsData`, `./ArtDecoTradingSignals.vue`, and three `../components/*` imports.
  - [x] 8.2.1 Move dependency: `useSignals.ts` to `src/shared/composables/`
    - Repo-truth note: not applicable as written. The current signals page fetches through `strategyApi.getSignals()` and does not own a local `useSignals.ts` composable to relocate.
  - [x] 8.2.2 Update imports to use `@/shared/...` absolute paths
    - Evidence: the canonical page now resolves its reused ArtDeco helpers through stable absolute `@/views/...` paths; shared-layer extraction remains a later batch.
  - [x] 8.2.3 Run lint & type-check
- [x] 8.3 Move `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` → `views/trade/Portfolio.vue`
  - Completed: 2026-04-05 via repo-truth-aligned micro-batch `2026-04-05-restructure-trade-portfolio-main`.
  - Result: `src/views/trade/Portfolio.vue` now hosts the canonical portfolio implementation; `PortfolioOverviewTab.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 8.3.0 **Identify all relative imports**
    - Evidence: the only local relative dependency in the original file was `./portfolioOverviewData`.
  - [x] 8.3.1 Move dependency: `usePortfolio.ts` to `src/shared/composables/`
    - Repo-truth note: not applicable as written. The current portfolio page does not own a local `usePortfolio.ts`; it uses `apiClient` + `useArtDecoApi` and the local helper pair in `portfolioOverviewData.ts`.
  - [x] 8.3.2 Update imports to use `@/shared/...` absolute paths
    - Evidence: the canonical page now resolves `portfolioOverviewData.ts` through a stable absolute `@/views/...` import until the shared helper migration is executed in a later batch.
  - [x] 8.3.3 Run lint & type-check
- [x] 8.4 Move `artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` → `views/trade/History.vue`
  - Completed: 2026-04-05 via repo-truth-aligned micro-batch `2026-04-05-restructure-trade-history-main`.
  - Result: `src/views/trade/History.vue` now hosts the canonical trade history implementation; `ArtDecoTradingHistory.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 8.4.0 **Identify all relative imports**
    - Evidence: the only local relative dependency in the original file was `./tradingDataTransform`.
  - [x] 8.4.1 Move dependency: `useHistory.ts` to `src/shared/composables/`
    - Repo-truth note: not applicable as written. The current history page does not own a local `useHistory.ts`; it uses `apiClient` + `useArtDecoApi` and the local `tradingDataTransform.ts` helper.
  - [x] 8.4.2 Update imports to use `@/shared/...` absolute paths
    - Evidence: the canonical page now resolves `tradingDataTransform.ts` through a stable absolute `@/views/...` import until the shared helper migration is executed in a later batch.
  - [x] 8.4.3 Run lint & type-check
- [ ] 8.5 **CLARIFICATION: Terminal.vue and DealingRoom.vue**
  - [x] 8.5.0 Determine final disposition:
    - Completed: 2026-04-04
    - Decision: Option C (`keep in current location`) for the current approved change scope.
    - Evidence: active `/trade/terminal` route and `trade-terminal` pageConfig still point to `TradingDashboard.vue`; no `DealingRoom.vue` or `Terminal.vue` implementation currently exists; `DealingRoom` is already used by the mainline `ArtDecoDashboard.vue` page inventory.
    - Option A: Move `trading/TradingDashboard.vue` → `views/trade/DealingRoom.vue` (add to trade domain)
    - Option B: Move to `deprecated/` (remove from active pages)
    - Option C: Keep in current location (no migration)
  - [ ] 8.5.1 If Option A: Move `trading/TradingDashboard.vue` → `views/trade/DealingRoom.vue`
    - Not applicable in the current repo state because Option C was selected.
    - [ ] 8.5.1.0 **Identify all relative imports**
    - [ ] 8.5.1.1 Move dependencies: `useTrade.ts`, `trading.scss` → `src/shared/`
    - [ ] 8.5.1.2 Update imports to use `@/shared/...` absolute paths
    - [ ] 8.5.1.3 Run lint & type-check
    - [ ] 8.5.1.4 Run unit tests for DealingRoom.vue
  - [x] 8.5.2 If Option B or C: Document decision and rationale
    - Documented in `web/frontend/MIGRATION_PROGRESS.md`.
- [x] 8.6 Reconcile dashboard truth and retain `ArtDecoDashboard.vue` as the canonical dashboard shell
  - Completed: 2026-04-05 via change `reconcile-dashboard-dealingroom-truth`.
  - Repo truth: `/dashboard` is canonical and remains backed by `ArtDecoDashboard.vue`; `/dealing-room` is legacy compatibility only.
  - `ArtDecoDashboard.vue` MUST NOT move to `deprecated/` under the current approved restructure scope.
  - `TradingDashboard.vue` remains exclusive to `/trade/terminal`.
- [ ] 8.7 Commit: "refactor: migrate trade domain pages"

## 9. Page-by-Page Migration – Risk Domain (Phase 3f)
- 2026-04-04 repo-truth note: tasks `9.2` through `9.6` required a mixed landing batch because the repo already contained placeholder target files under `src/views/risk/`.
  - `src/views/risk/Center.vue`, `src/views/risk/StopLoss.vue`, and `src/views/risk/News.vue` are now landed as target entry wrappers.
  - `src/views/risk/Overview.vue` and `src/views/risk/Alerts.vue` have been inverted from placeholder pages into compatibility wrappers around the current ArtDeco implementations.
  - The `ArtDecoPageTemplate.vue` dependency chain remains preserved through `ArtDecoRiskManagement.vue`.
  - `risk-pnl` remains outside this micro-batch and still points to `PortfolioOverviewTab.vue` in current repo truth.
- [x] 9.1 Verify `ArtDecoPageTemplate.vue` is retained (not deleted)
  - Completed: 2026-04-05 via verification batch `2026-04-05-verify-risk-template-retention-main`.
  - Result: `src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue` remains present, and `ArtDecoRiskManagement.vue` still imports it through `./_templates/ArtDecoPageTemplate.vue` in current repo truth.
  - [x] 9.1.1 Check that `src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue` exists
  - [x] 9.1.2 Verify `ArtDecoRiskManagement.vue` imports it correctly
- [x] 9.2 Move `artdeco-pages/ArtDecoRiskManagement.vue` → `views/risk/Center.vue`
  - Completed: 2026-04-06 via repo-truth-aligned micro-batch `2026-04-06-restructure-risk-center-main`.
  - Result: `src/views/risk/Center.vue` now hosts the canonical risk center implementation; `ArtDecoRiskManagement.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 9.2.1 Move dependency: `useRisk.ts`
    - Repo-truth note: not applicable as written. The current risk center page does not own a local `useRisk.ts`; it composes `ArtDecoPageTemplate`, local `riskManagementHelpers.ts`, and `riskManagementData.ts`.
  - [x] 9.2.2 Update imports (including template import)
    - Evidence: the canonical page now resolves `ArtDecoPageTemplate.vue` and risk-tab helpers through stable absolute `@/views/...` imports.
  - [x] 9.2.3 Run lint & type-check
  - [x] 9.2.4 Run unit tests for Center.vue
- [x] 9.3 Move `artdeco-pages/risk-tabs/RiskOverviewTab.vue` → `views/risk/Overview.vue`
  - Completed: 2026-04-06 via repo-truth-aligned micro-batch `2026-04-06-restructure-risk-overview-main`.
  - Result: `src/views/risk/Overview.vue` now hosts the canonical risk overview implementation; `RiskOverviewTab.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 9.3.1 Move dependency: `useRiskOverview.ts`
    - Repo-truth note: not applicable as written. The current risk overview page does not own a local `useRiskOverview.ts`; it already uses stable absolute imports and pulls risk rule data through `monitoringApi.getAlertRules()`.
  - [x] 9.3.2 Update imports
    - Evidence: the legacy ArtDeco path now imports `@/views/risk/Overview.vue`, while the canonical page retains the repo-truth implementation imports from `@/api/index`, `@/api/types/common`, `@/composables/artdeco/useArtDecoApi`, and `@/components/artdeco`.
  - [x] 9.3.3 Run lint & type-check
  - [x] 9.3.4 Run unit tests for Overview.vue
- [x] 9.4 Move `artdeco-pages/risk-tabs/StopLossMonitorTab.vue` → `views/risk/StopLoss.vue`
  - Completed: 2026-04-06 via repo-truth-aligned micro-batch `2026-04-06-restructure-risk-stop-loss-main`.
  - Result: `src/views/risk/StopLoss.vue` now hosts the canonical risk stop-loss implementation; `StopLossMonitorTab.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 9.4.1 Move dependency: `useStopLoss.ts`
    - Repo-truth note: not applicable as written. The current risk stop-loss page does not own a local `useStopLoss.ts`; it composes `useArtDecoApi`, `apiClient`, and `stopLossMonitorData.ts`.
  - [x] 9.4.2 Update imports
    - Evidence: the canonical page now resolves `apiClient` and `stopLossMonitorData.ts` through stable absolute `@/...` imports, while the legacy ArtDeco path imports `@/views/risk/StopLoss.vue`.
  - [x] 9.4.3 Run lint & type-check
  - [x] 9.4.4 Run unit tests for StopLoss.vue
- [x] 9.5 Move `artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` → `views/risk/Alerts.vue`
  - Completed: 2026-04-06 via repo-truth-aligned micro-batch `2026-04-06-restructure-risk-alerts-main`.
  - Result: `src/views/risk/Alerts.vue` now hosts the canonical risk alerts implementation; `ArtDecoRiskAlerts.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 9.5.1 Move dependency: `useRiskAlerts.ts`
    - Repo-truth note: not applicable as written. The current risk alerts page does not own a local `useRiskAlerts.ts`; it composes `useArtDecoApi`, `monitoringApi`, and inline normalization / formatting helpers.
  - [x] 9.5.2 Update imports
    - Evidence: the canonical page keeps the repo-truth imports from `@/api/index`, `@/api/types/common`, `@/composables/artdeco/useArtDecoApi`, and `@/components/artdeco`, while the legacy ArtDeco path now imports `@/views/risk/Alerts.vue`.
  - [x] 9.5.3 Run lint & type-check
  - [x] 9.5.4 Run unit tests for Alerts.vue
- [x] 9.6 Move `artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` → `views/risk/News.vue`
  - Completed: 2026-04-06 via repo-truth-aligned micro-batch `2026-04-06-restructure-risk-news-main`.
  - Result: `src/views/risk/News.vue` now hosts the canonical risk news implementation; `ArtDecoAnnouncementMonitor.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 9.6.1 Move dependency: `useRiskNews.ts`
    - Repo-truth note: not applicable as written. The current risk news page does not own a local `useRiskNews.ts`; it composes `useArtDecoApi`, `monitoringApi`, and inline announcement formatting / source-link helpers.
  - [x] 9.6.2 Update imports
    - Evidence: the canonical page keeps the repo-truth imports from `@/api/index`, `@/api/types/common`, `@/composables/artdeco/useArtDecoApi`, and `@/components/artdeco`, while the legacy ArtDeco path now imports `@/views/risk/News.vue`.
  - [x] 9.6.3 Run lint & type-check
  - [x] 9.6.4 Run unit tests for News.vue
- [x] 9.7 Commit: "refactor: migrate risk domain pages"
  - Repo-truth note: the approved mainline execution replaced the original single-commit expectation with repo-truth-aligned micro-batches.
  - Completed: 2026-04-06 via commit chain `4bdd5611a`, `377134dee`, `ff85fd3cb`, `1861a6825`, and `0690d94e7`.
  - Result: risk domain canonical entrypoints now live under `src/views/risk/`, while legacy ArtDeco paths remain thin compatibility wrappers.

## 10. Page-by-Page Migration – System Domain (Phase 3g)
- 2026-04-04 repo-truth note: the system target pages for tasks `10.1` through `10.4` did not exist in the repository baseline, so this batch lands the missing target entrypoints and retargets the system router/pageConfig entries to them.
  - `src/views/system/Settings.vue` now fronts the existing `ArtDecoSystemSettings.vue` implementation.
  - `src/views/system/Health.vue` now fronts the existing `SystemHealthTab.vue` implementation.
  - `src/views/system/API.vue` now fronts the existing `ArtDecoMonitoringDashboard.vue` implementation.
  - `src/views/system/DataSource.vue` now fronts the existing `ArtDecoDataManagement.vue` implementation.
  - Remaining work in this area is compatibility-wrapper retirement and dependency normalization, not leaving the system domain on non-domain entry files.
- [x] 10.1 Move `artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` → `views/system/Settings.vue`
  - Completed: 2026-04-06 via repo-truth-aligned micro-batch `2026-04-06-restructure-system-settings-main`.
  - Result: `src/views/system/Settings.vue` now hosts the canonical system settings implementation; `ArtDecoSystemSettings.vue` is retained as a legacy compatibility wrapper into the canonical route entrypoint.
  - [x] 10.1.1 Move dependency: `useSystemSettings.ts`
    - Repo-truth note: not applicable as written. The current system settings page does not own a local `useSystemSettings.ts`; it composes `useArtDecoApi`, `monitoringApi`, local storage helpers, and `systemSettingsMonitorData.ts`.
  - [x] 10.1.2 Update imports
    - Evidence: the canonical page now resolves `monitoringApi` and `systemSettingsMonitorData.ts` through stable absolute imports, while the legacy ArtDeco path imports `@/views/system/Settings.vue`.
  - [x] 10.1.3 Run lint & type-check
  - [x] 10.1.4 Run unit tests for Settings.vue
- [ ] 10.2 Move `artdeco-pages/system-tabs/SystemHealthTab.vue` → `views/system/Health.vue`
  - [ ] 10.2.1 Move dependency: `useSystemHealth.ts`
  - [ ] 10.2.2 Update imports
  - [ ] 10.2.3 Run lint & type-check
- [ ] 10.3 Move `artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` → `views/system/API.vue`
  - [ ] 10.3.1 Move dependency: `useApiMonitoring.ts`
  - [ ] 10.3.2 Update imports
  - [ ] 10.3.3 Run lint & type-check
  - [ ] 10.3.4 Run unit tests for API.vue
- [ ] 10.4 Move `artdeco-pages/system-tabs/ArtDecoDataManagement.vue` → `views/system/DataSource.vue`
  - [ ] 10.4.1 Move dependency: `useDataSource.ts`
  - [ ] 10.4.2 Update imports
  - [ ] 10.4.3 Run lint & type-check
  - [ ] 10.4.4 Run unit tests for DataSource.vue
- [ ] 10.5 Commit: "refactor: migrate system domain pages"

## 11. Routing & Layout Adjustments (Phase 4)
- [ ] 11.1 Edit `src/router/index.ts` to update all route paths to new locations
- [ ] 11.2 Remove stale route entries pointing to files under `deprecated/`
- [ ] 11.3 Verify no duplicate route paths exist
- [ ] 11.4 Run `npm run dev` and manually test navigation to each domain
- [ ] 11.5 Verify no 404 errors in browser console
- [ ] 11.6 Commit: "refactor: update router paths for new directory structure"

## 12. Testing – Smoke Suite (Phase 5)
- [ ] 12.1 Run `npm run test:smoke` locally
- [ ] 12.2 Fix any failing smoke tests
- [ ] 12.3 Verify all tests pass
- [ ] 12.4 Generate test report and attach to PR

## 13. Testing – End-to-End (Phase 5)
- [ ] 13.1 Run `npm run test:e2e` (Cypress full suite)
- [ ] 13.2 Fix any failing E2E tests
- [ ] 13.3 Verify all critical user flows pass (login → dashboard → trade)
- [ ] 13.4 Generate E2E report and attach to PR

## 14. Code Review & Sign-off (Phase 6)
- [ ] 14.1 Front-end Lead posts "Ready for Review" comment on PR
- [ ] 14.2 Run `oh-my-claudecode:code-reviewer` agent for comprehensive review
- [ ] 14.3 Run `oh-my-claudecode:security-reviewer` agent for security check
- [ ] 14.4 Address all review feedback
- [ ] 14.5 Obtain final approval from Architecture Board

## 15. Merge & Deploy (Phase 7)
- [ ] 15.1 Merge PR to `main` (all checks must pass)
- [ ] 15.2 Trigger CI pipeline (should deploy to staging automatically)
- [ ] 15.3 Verify staging deployment succeeds

## 16. Post-Deployment Validation (Phase 7)
- [ ] 16.1 Run smoke suite against staging environment
- [ ] 16.2 Verify all URLs resolve (no 404s)
- [ ] 16.3 Perform quick UI sanity check on main navigation
- [ ] 16.4 Verify that all domain pages load correctly
- [ ] 16.5 Post deployment verification report to PR

## 17. Archiving the Change (Phase 8)
- [ ] 17.1 Run `openspec archive restructure-frontend-directory --yes`
- [ ] 17.2 Verify change moved to `openspec/changes/archive/YYYY-MM-DD-restructure-frontend-directory/`
- [ ] 17.3 Run `openspec validate --strict` on archived change
- [ ] 17.4 Commit archive changes

## 18. Documentation Updates (Phase 8)
- [ ] 18.1 Add migration summary to `docs/guides/frontend-structure.md`
- [ ] 18.2 Update routing diagram in `docs/architecture/routing.md` (if exists)
- [ ] 18.3 Record final effort (≈ 26 person-days) in project status report
- [ ] 18.4 Update `AGENTS.md` with new directory structure reference
- [ ] 18.5 Commit: "docs: update frontend structure documentation"

## 19. Cleanup & Verification (Phase 9)
- [ ] 19.1 Verify no stale imports remain (run `npm run lint` one final time)
- [ ] 19.2 Verify no broken routes (run `npm run dev` and spot-check)
- [ ] 19.3 Update `MIGRATION_PROGRESS.md` with final status
- [ ] 19.4 Close any related GitHub issues
- [ ] 19.5 Post final summary to project channel

---

## Summary

**Total tasks**: 19 major phases with 100+ sub-tasks
**Estimated effort**: 26 person-days (≈ 3.5 weeks)
**Critical path**: Phases 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9
**Parallel opportunities**: Phases 3a–3g (market, data, watchlist, strategy, trade, risk, system) can be parallelized if multiple developers are available.

**Key verification gates**:
- ✅ `npm run lint && npm run type-check` after each file move
- ✅ `npm run test:smoke` before merge
- ✅ `npm run test:e2e` before merge
- ✅ Architecture Board approval before implementation
- ✅ Post-deployment smoke test on staging
