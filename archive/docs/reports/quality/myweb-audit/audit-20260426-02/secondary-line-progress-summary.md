# MyWeb Audit Secondary Line Progress Summary

> Date: 2026-05-10
>
> Scope: `myweb-audit` canonical route closure plus secondary inventory page-quality line.
>
> Source of truth:
> - `.claude/skills/myweb-audit/references/secondary-view-inventory.md`
> - `.claude/skills/myweb-audit/references/secondary-view-inventory.json`
> - `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
> - `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/*.yaml`

## Current State

- Current secondary inventory snapshot: `2026-05-09T16:52:33.680Z`.
- Current inventory totals: `271` view files, `42` routed views, `229` unrouted views.
- Current classification counts: `候选待审=69 / 内嵌壳层=104 / Demo废弃=56`.
- Current priority counts: `H=0 / M=123 / L=106`.
- High-priority shortlist is currently empty: `H=0`.
- The active working mode has already shifted away from matrix-first canonical routing into secondary-inventory triage.
- Current quality gate status remains consistent: structural syntax checks for recent batches pass; frontend `type-check` is still blocked by pre-existing debt in `dashboardService.ts` and `useKLinePatternOverlays.ts`, with no new errors reported in recent secondary batch files.

## Completed Work

### Canonical Route Line

The canonical route matrix has been worked through enough that the campaign switched to secondary inventory. The already covered canonical families include these route classes:

- Dashboard and shell routes: `/dashboard`, `/login`, unmatched `404`.
- Market routes: `/market/realtime`, `/market/technical`, `/market/lhb`.
- Data routes: `/data/industry`, `/data/concept`, `/data/fund-flow`, `/data/indicator`.
- Watchlist routes: `/watchlist/manage`, `/watchlist/signals`, `/watchlist/screener`.
- Strategy routes: `/strategy/repo`, `/strategy/parameters`, `/strategy/signals`, `/strategy/backtest`, `/strategy/gpu`, `/strategy/opt`, `/strategy/pos`.
- Trade routes and related embedded owners: `/trade/*` canonical owners, including trade portfolio, history, positions, signals, terminal/orchestration, and reconciliation-family work.
- Risk routes: `/risk/management`, risk overview/news/alerts/position-related flows.
- System routes: `/system/settings`, `/system/data`, `/system/health`, `/system/api`, `/system/resources`.
- Detail routes: stock/news/graphics style detail routes with symbol or period switching.

The important closure point is not that every visual variant was made perfect. The closure point is that the main canonical pages now have stable route-truth guardrails for request provenance, freshness, selector-scoped snapshots, partial slices, pending labels, local execution state, and enrichment slices.

### Blank Layout Batch

`blank-batch-01` covered `/login` and the catch-all 404 route as a lightweight blank-layout batch.

Checks completed:

- Layout isolation from the ArtDeco application shell.
- No request badge, trace badge, stats strip, or readiness chrome on blank pages.
- Same-tab transition from `/login` to unmatched route did not leak login or shell state.
- `npx vitest run tests/unit/config/shell-route-runtime-guardrails.spec.ts` passed.
- `npx playwright test tests/e2e/blank-layout-smoke.spec.ts` passed on Chromium.

### Secondary Inventory Setup

The secondary inventory workflow was created and wired into `myweb-audit v2.1`.

Permanent operating assets now include:

- `secondary-view-inventory.md`
- `secondary-view-inventory.json`
- fixed three-way classification: `候选待审 / 内嵌壳层 / Demo废弃`
- fixed fields: page path, layer, selector, stats-strip/indicator-card, shared composable, priority
- fixed heuristics: stats/hero surfaces, selector switching, fallback literals, shared composables
- skill self-check integration through `npm run test:myweb-audit:skill`

## Completed Secondary Batches

### Wrapper Delegation And Static-Shell Closure

The following secondary batches are closed in the audit line:

- `secondary-batch-02`: `ArtDecoTradingCenter.vue` wrappers for canonical trade history and portfolio.
- `secondary-batch-03`: live monitor wrappers for market realtime and risk center.
- `secondary-batch-04`: market wrappers without matching canonical owners degraded to static shells.
- `secondary-batch-05`: `monitoring/MonitoringDashboard.vue` degraded from pseudo-live monitoring shell.
- `secondary-batch-06`: `Dashboard.vue` delegated to canonical ArtDeco dashboard.
- `secondary-batch-07`: `Analysis.vue` degraded from pseudo-live analysis workbench.
- `secondary-batch-10`: `StrategyManagement.vue` delegated to `/strategy/repo`.
- `secondary-batch-11`: `BacktestAnalysis.vue` delegated to `/strategy/backtest`.
- `secondary-batch-12`: `RiskMonitor.vue` delegated to `/risk/management`.
- `secondary-batch-13`: `Market.vue` delegated to `/trade/portfolio`.
- `secondary-batch-14`: `IndicatorLibrary.vue` delegated to `/data/indicator`.
- `secondary-batch-15`: `TradeManagement.vue` delegated to active ArtDeco trading orchestration.
- `secondary-batch-16`: `strategy/StrategyList.vue` delegated to `strategy/List.vue`.
- `secondary-batch-17`: `TechnicalAnalysis.vue` degraded to static shell.
- `secondary-batch-18`: `technical/TechnicalAnalysis.vue` degraded to static shell.
- `secondary-batch-19`: `StockDetail.vue` degraded to static shell.
- `secondary-batch-20`: `trading/{History,Positions}.vue` delegated to canonical trade owners.
- `secondary-batch-21`: `trading/{Orders,Execution}.vue` degraded to static shells.
- `secondary-batch-22`: `TdxMarket.vue` degraded to static shell.
- `secondary-batch-23`: `Phase4Dashboard.vue` delegated to canonical dashboard.
- `secondary-batch-24`: `EnhancedRiskMonitor.vue` delegated to `/risk/management`.
- `secondary-batch-25`: `trading-decision/{DecisionPortfolio,DecisionPositions}.vue` delegated to canonical trade owners.
- `secondary-batch-26`: `trading-decision/DecisionOrders.vue` degraded to static shell.
- `secondary-batch-27`: `Wencai.vue` reduced to thin wrapper over live `WencaiPanel.vue`.
- `secondary-batch-28`: `system/Architecture.vue` degraded to static shell.
- `secondary-batch-29`: `system/DatabaseMonitor.vue` degraded to static shell.
- `secondary-batch-30`: `system/PerformanceMonitor.vue` degraded to static shell.
- `secondary-batch-31`: `TaskManagement.vue` degraded to static shell.
- `secondary-batch-49`: `trade-management/components/{PortfolioOverview,PositionsTab,StatisticsTab,TradeHistoryTab,TradeDialog}.vue` degraded to static shells.
- `secondary-batch-50`: `stocks/{Activity,Concept,Industry,Watchlist}.vue` degraded to static shells.
- `secondary-batch-51`: `stocks/Portfolio.vue` degraded to static shell.
- `secondary-batch-52`: `risk/{Portfolio,Positions}.vue` degraded to static shells.
- `secondary-batch-53`: `artdeco-pages/ArtDecoTechnicalAnalysis.vue` degraded to static shell.

### Recently Confirmed By Direct Inspection

These pages were inspected during the latest continuation cycle and intentionally not changed:

- `web/frontend/src/views/stocks/Screener.vue`: not an orphan; it is imported by `watchlist/Screener.vue` and should not be degraded as a secondary shell.
- `web/frontend/src/views/market/CapitalFlow.vue`: already a thin wrapper over `data/FundFlow.vue`; current file also has pre-existing dirty changes, so it was not touched.
- `web/frontend/src/views/market/Concepts.vue`: already a thin wrapper over `data/Concepts.vue`; current file also has pre-existing dirty changes, so it was not touched.
- `web/frontend/src/views/trading-decision/DecisionPortfolio.vue`: currently imported by `TradingDecisionCenter.vue`; not an orphan.
- `web/frontend/src/views/trading-decision/DecisionPositions.vue`: currently imported by `TradingDecisionCenter.vue`; not an orphan, though it deserves a later focused review because it passes an empty positions prop to a canonical trade page.
- `web/frontend/src/views/advanced-analysis/*.vue`: inspected as a group; already converted to `legacy-static-shell` style pages, so no new repair was made in the latest pass.

## Remaining Inventory

The remaining inventory should not be treated as "all are defects." It is a backlog that still needs owner classification and heuristic triage.

### Current M Priority Count

There are `123` remaining `M` priority assets in the latest inventory.

The most important remaining M classes are:

- Top-level legacy or wrapper candidates still listed as `候选待审`.
- Embedded ArtDeco shells with selectors, stats strips, fallback literals, or shared composables.
- Monitoring and stock-management embedded shells with selector/state surfaces.
- Demo-deprecated pages that still contain selectors or fallback literals but are lower priority unless they are routed or imported by active shells.

### Candidate Pages Still Listed As M

The following candidate groups remain in `M`, but several are already known static shells or thin wrappers and need classification refinement rather than automatic repair:

- `web/frontend/src/views/advanced-analysis/*.vue`
- `web/frontend/src/views/AdvancedAnalysis.vue`
- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/BacktestAnalysis.vue`
- `web/frontend/src/views/BacktestWizard.vue`
- `web/frontend/src/views/Dashboard.vue`
- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/EnhancedRiskMonitor.vue`
- `web/frontend/src/views/IndicatorLibrary.vue`
- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/Market.vue`
- `web/frontend/src/views/market/{Auction,CapitalFlow,Concepts,Etf,MarketDataView,Tdx}.vue`
- `web/frontend/src/views/MarketData.vue`
- `web/frontend/src/views/monitor.vue`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/PortfolioManagement.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/risk/{Portfolio,Positions}.vue`
- `web/frontend/src/views/RiskMonitor.vue`
- `web/frontend/src/views/Settings.vue`
- `web/frontend/src/views/settings/{General,Notifications,Security,Theme}.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/Stocks.vue`
- `web/frontend/src/views/strategy/{BatchScan,ResultsQuery,SingleRun,StatsAnalysis,StrategyList}.vue`
- `web/frontend/src/views/StrategyManagement.vue`
- `web/frontend/src/views/system/{Architecture,DatabaseMonitor,PerformanceMonitor}.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TdxMarket.vue`
- `web/frontend/src/views/technical/TechnicalAnalysis.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/TestPage.vue`
- `web/frontend/src/views/TradeManagement.vue`
- `web/frontend/src/views/trading-decision/{DecisionHeader,DecisionOrders,DecisionPortfolio,DecisionPositions}.vue`
- `web/frontend/src/views/trading/{Execution,History,Orders,Positions}.vue`
- `web/frontend/src/views/TradingDecisionCenter.vue`
- `web/frontend/src/views/Wencai.vue`

The inventory generator still marks many already-repaired static shells as `M` because they remain view files under candidate paths. For follow-up planning, direct code inspection and route-owner checks must override raw priority labels.

### Embedded M Backlog

The embedded backlog still deserves targeted review because it contains the highest chance of selector-owned state or sibling enrichment slice leakage:

- `web/frontend/src/views/ai/components/*`
- `web/frontend/src/views/artdeco-pages/_templates/*`
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoStockManagement.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`
- `web/frontend/src/views/artdeco-pages/components/*` entries still marked `M`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/*` entries still marked `M`
- `web/frontend/src/views/artdeco-pages/market-tabs/MarketETFTab.vue`
- `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue`
- `web/frontend/src/views/artdeco-pages/settings/*`
- `web/frontend/src/views/artdeco-pages/stock-management-tabs/*`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/*`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`
- `web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/{ArtDecoTradingSignals,ArtDecoTradingStats}.vue`
- `web/frontend/src/views/components/{RiskOverviewTab,StopLossMonitoringTab}.vue`
- `web/frontend/src/views/monitoring/{AlertRulesManagement,RiskDashboard,WatchlistManagement}.vue`
- `web/frontend/src/views/stocks/Screener.vue`

## Recommended Next Task Order

### Step 1: Normalize Inventory Classification

Before fixing more pages, run a small inventory-quality batch:

- Reclassify already-static-shell pages that still appear as `M` candidates.
- Distinguish `already closed static shell`, `thin canonical wrapper`, `active embedded component`, and `true candidate`.
- Add generator or post-processing rules so `legacy-static-shell` pages no longer consume the same queue priority as unreviewed pages.

This will reduce noise and prevent repeated manual rediscovery.

### Step 2: Review Active Embedded Owners Before Orphans

Prioritize embedded components that are still imported by active routed owners and have one of the four heuristic signals:

- selector state
- stats-strip or metric cards
- fallback literals
- shared composables

Recommended next targets:

- `ArtDecoTradingManagement.vue` and directly imported panels that still own selector/account/tab state.
- `ArtDecoMarketData.vue` and market-data tabs with selector or fallback literals.
- `ArtDecoMarketQuotes.vue` because it still has selector-like quote and analysis controls.
- `TechnicalScannerTab.vue` because it still appears in M with stats-strip, selector, and shared-composable signals.
- `monitoring/RiskDashboard.vue` and `monitoring/WatchlistManagement.vue` because they combine selectors, stats strips, fallback literals, and shared composables.

### Step 3: Focused Triage For Known Active Wrappers

Do not degrade these without first checking live import chains:

- `stocks/Screener.vue`
- `trading-decision/DecisionPortfolio.vue`
- `trading-decision/DecisionPositions.vue`
- `market/CapitalFlow.vue`
- `market/Concepts.vue`

These should be reviewed as wrapper-truth or prop-boundary issues, not orphan-page cleanup.

### Step 4: Only Then Process Demo Deprecated Pages

Demo pages should stay lower priority unless one is routed, imported by a live shell, or leaking fake live data into a production route. The current `Demo废弃=56` bucket should remain a later cleanup lane.

## Operating Rules For The Next Session

- Start each new repair with route/import owner verification.
- Run GitNexus impact before editing any page or component symbol.
- Use TDD guard tests for behavior changes, even for source-only static shell conversions.
- Prefer static shell when no canonical truth exists.
- Prefer thin wrapper when a semantically matching canonical owner already exists.
- Never add a new snapshot/store/API to make a secondary page look live.
- Do not treat raw inventory `M` as proof of an unfixed defect.
- Record each batch in findings, merged findings, approval, page report, manifest, closeout, and casebook when the rule is reusable.

## Validation Baseline

Recent batches consistently used:

- `npx vitest run <owner regression>`
- targeted `rg` residual scans
- `npm run generate:myweb-audit:secondary-inventory`
- `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id <batch>`
- `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest <manifest>`
- `npm run test:myweb-audit:skill`
- `git diff --check -- <batch paths>`
- `pm2 list`
- `timeout 180s npm run type-check`
- `gitnexus_detect_changes({ scope: "staged" })`

Known type-check debt remains outside recent secondary batches:

- `src/api/services/dashboardService.ts(331,43)`
- `src/api/services/dashboardService.ts(331,66)`
- `src/components/technical/composables/useKLinePatternOverlays.ts`

Current staged GitNexus detects are polluted by a large pre-existing dirty index. Treat staged detect as mixed observation until the current accumulated staged work is split or committed.
