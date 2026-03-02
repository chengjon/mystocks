# Implementation Tasks: Restructure Frontend Directory

## 1. Pre-flight (Phase 0 – Freeze & Planning)
- [x] 1.1 Add git pre-commit hook to block new `.vue` files under `src/views/` not in migration table
- [x] 1.2 Run `openspec validate restructure-frontend-directory --strict` to verify change package
- [x] 1.3 Create a tracking document (e.g., `MIGRATION_PROGRESS.md`) to log completed moves

## 2. Governance & Approval (Phase 1)
- [x] 2.1 Submit PR with OpenSpec change to Architecture Board for review
  - Submitted: 2026-03-02
  - Notification sent to Architecture Lead, Front-end Lead, Security Reviewer
- [ ] 2.2 Obtain explicit sign-off (comment "APPROVED") from Architecture Lead
  - Status: Awaiting approval
  - Approval criteria: Design aligns with architecture principles, STANDARDS.md compliance, effort estimate reasonable, risk assessment sufficient
- [ ] 2.3 Obtain sign-off from Front-end Lead on the migration plan
  - Status: Awaiting approval
  - Approval criteria: Plan feasibility confirmed, resources available, no conflicts with existing work, effort estimate reasonable
- [ ] 2.4 Verify no conflicting changes in `openspec/changes/` (run `openspec list`)
  - Status: Pending (will execute after approvals received)

## 3. Shared Asset Extraction (Phase 2)
- [ ] 3.0 **Identify existing files at target locations**
  - [ ] 3.0.1 List all files that already exist in `src/shared/components/` and `src/shared/composables/`
  - [ ] 3.0.2 For each existing file, determine merge strategy:
    - Compare source and target file contents
    - Choose which version to keep (or merge both)
    - Run unit tests to verify functionality
    - Delete source file after merge
- [ ] 3.1 Create target directories: `src/shared/components/` and `src/shared/composables/`
- [ ] 3.2 Move all files from `src/views/shared/components/*` → `src/shared/components/` (use `git mv`)
- [ ] 3.3 Move all files from `src/views/shared/composables/*` → `src/shared/composables/` (use `git mv`)
- [ ] 3.4 Search for all imports of `@/views/shared/...` and update to `@/shared/...`
- [ ] 3.5 Run `npm run lint && npm run type-check` and fix any errors
- [ ] 3.6 Commit: "refactor: extract shared assets to src/shared/"

## 4. Page-by-Page Migration – Market Domain (Phase 3a)
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
- [ ] 5.1 Move `artdeco-pages/ArtDecoDataAnalysis.vue` → `views/data/Advanced.vue`
  - [ ] 5.1.1 Move dependency: `useAdvancedData.ts`
  - [ ] 5.1.2 Update imports
  - [ ] 5.1.3 Run lint & type-check
  - [ ] 5.1.4 Run unit tests for Advanced.vue
- [ ] 5.2 Commit: "refactor: migrate data domain pages"

## 6. Page-by-Page Migration – Watchlist Domain (Phase 3c)
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
- [ ] 8.1 Move `artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` → `views/trade/Center.vue`
  - [ ] 8.1.0 **Identify all relative imports**
  - [ ] 8.1.1 Move dependency: `usePositions.ts` to `src/shared/composables/`
  - [ ] 8.1.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 8.1.3 Run lint & type-check
  - [ ] 8.1.4 Run unit tests for Center.vue
- [ ] 8.2 Move `artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` → `views/trade/Signals.vue`
  - [ ] 8.2.0 **Identify all relative imports**
  - [ ] 8.2.1 Move dependency: `useSignals.ts` to `src/shared/composables/`
  - [ ] 8.2.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 8.2.3 Run lint & type-check
- [ ] 8.3 Move `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` → `views/trade/Portfolio.vue`
  - [ ] 8.3.0 **Identify all relative imports**
  - [ ] 8.3.1 Move dependency: `usePortfolio.ts` to `src/shared/composables/`
  - [ ] 8.3.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 8.3.3 Run lint & type-check
- [ ] 8.4 Move `artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` → `views/trade/History.vue`
  - [ ] 8.4.0 **Identify all relative imports**
  - [ ] 8.4.1 Move dependency: `useHistory.ts` to `src/shared/composables/`
  - [ ] 8.4.2 Update imports to use `@/shared/...` absolute paths
  - [ ] 8.4.3 Run lint & type-check
- [ ] 8.5 **CLARIFICATION: Terminal.vue and DealingRoom.vue**
  - [ ] 8.5.0 Determine final disposition:
    - Option A: Move `trading/TradingDashboard.vue` → `views/trade/DealingRoom.vue` (add to trade domain)
    - Option B: Move to `deprecated/` (remove from active pages)
    - Option C: Keep in current location (no migration)
  - [ ] 8.5.1 If Option A: Move `trading/TradingDashboard.vue` → `views/trade/DealingRoom.vue`
    - [ ] 8.5.1.0 **Identify all relative imports**
    - [ ] 8.5.1.1 Move dependencies: `useTrade.ts`, `trading.scss` → `src/shared/`
    - [ ] 8.5.1.2 Update imports to use `@/shared/...` absolute paths
    - [ ] 8.5.1.3 Run lint & type-check
    - [ ] 8.5.1.4 Run unit tests for DealingRoom.vue
  - [ ] 8.5.2 If Option B or C: Document decision and rationale
- [ ] 8.6 Move `artdeco-pages/ArtDecoDashboard.vue` → `src/views/deprecated/ArtDecoDashboard.vue`
  - [ ] 8.6.1 No import updates needed (deprecated)
  - [ ] 8.6.2 Verify file moved
- [ ] 8.7 Commit: "refactor: migrate trade domain pages"

## 9. Page-by-Page Migration – Risk Domain (Phase 3f)
- [ ] 9.1 Verify `ArtDecoPageTemplate.vue` is retained (not deleted)
  - [ ] 9.1.1 Check that `src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue` exists
  - [ ] 9.1.2 Verify `ArtDecoRiskManagement.vue` imports it correctly
- [ ] 9.2 Move `artdeco-pages/ArtDecoRiskManagement.vue` → `views/risk/Center.vue`
  - [ ] 9.2.1 Move dependency: `useRisk.ts`
  - [ ] 9.2.2 Update imports (including template import)
  - [ ] 9.2.3 Run lint & type-check
  - [ ] 9.2.4 Run unit tests for Center.vue
- [ ] 9.3 Move `artdeco-pages/risk-tabs/RiskOverviewTab.vue` → `views/risk/Overview.vue`
  - [ ] 9.3.1 Move dependency: `useRiskOverview.ts`
  - [ ] 9.3.2 Update imports
  - [ ] 9.3.3 Run lint & type-check
- [ ] 9.4 Move `artdeco-pages/risk-tabs/StopLossMonitorTab.vue` → `views/risk/StopLoss.vue`
  - [ ] 9.4.1 Move dependency: `useStopLoss.ts`
  - [ ] 9.4.2 Update imports
  - [ ] 9.4.3 Run lint & type-check
- [ ] 9.5 Move `artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` → `views/risk/Alerts.vue`
  - [ ] 9.5.1 Move dependency: `useRiskAlerts.ts`
  - [ ] 9.5.2 Update imports
  - [ ] 9.5.3 Run lint & type-check
- [ ] 9.6 Move `artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` → `views/risk/News.vue`
  - [ ] 9.6.1 Move dependency: `useRiskNews.ts`
  - [ ] 9.6.2 Update imports
  - [ ] 9.6.3 Run lint & type-check
- [ ] 9.7 Commit: "refactor: migrate risk domain pages"

## 10. Page-by-Page Migration – System Domain (Phase 3g)
- [ ] 10.1 Move `artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` → `views/system/Settings.vue`
  - [ ] 10.1.1 Move dependency: `useSystemSettings.ts`
  - [ ] 10.1.2 Update imports
  - [ ] 10.1.3 Run lint & type-check
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
