# Frontend Directory Restructure Migration Progress

Date: 2026-04-04
OpenSpec change: `restructure-frontend-directory`
Mongo work item: `2026-04-04-restructure-frontend-shared-target-inventory-main`

## Phase 2 Baseline Inventory

This record captures the actual repository baseline before any shared-asset extraction begins.

### Expected paths from the approved change

| Path | Expected role | Exists before this batch |
| --- | --- | --- |
| `web/frontend/src/shared/components/` | shared component target | No |
| `web/frontend/src/shared/composables/` | shared composable target | No |
| `web/frontend/src/views/shared/components/` | assumed extraction source | No |
| `web/frontend/src/views/shared/composables/` | assumed extraction source | No |

### Actual shared-like locations found in the repo

| Path | File count | Notes |
| --- | ---: | --- |
| `web/frontend/src/components/shared/` | 12 | Already acts as a canonical shared UI layer. Excludes `.claude` logs. |
| `web/frontend/src/composables/` | 49 | Already acts as a canonical shared composable layer. |
| `web/frontend/src/views/components/` | 5 | View-adjacent reusable fragments; candidate extraction sources. |
| `web/frontend/src/views/composables/` | 17 | View-adjacent composables; candidate extraction sources. |

### Import baseline

- No `@/views/shared/...` imports were found in the active frontend tree during this inventory pass.
- Current shared-style imports primarily use:
  - `@/components/shared/...`
  - `@/components/shared`
  - `@/composables/...`

## Merge / Keep Strategy

Because the approved source and target shared paths do not exist in the current repo baseline, there are no target-location conflicts to merge in this batch.

The extraction strategy for follow-up batches is:

1. Keep `src/components/shared/` as the canonical shared component base unless a specific file must move into `src/shared/components/`.
2. Keep `src/composables/` as the canonical shared composable base unless a specific file must move into `src/shared/composables/`.
3. Treat `src/views/components/` and `src/views/composables/` as the real candidate extraction sources that need classification before any `git mv`.
4. Do not execute `git mv` commands that reference `src/views/shared/*`, because that source tree does not exist in the repository baseline.

## Phase 2 Candidate Classification

The table below records the actual Phase 2 candidate boundary after checking file consumers, active route usage, and page ownership.

| Candidate | Current consumer(s) | Classification | Rationale |
| --- | --- | --- | --- |
| `web/frontend/src/views/components/RiskOverviewTab.vue` | `web/frontend/src/views/EnhancedRiskMonitor.vue` | Keep view-local | Legacy risk-tab component bundle; active router points to `artdeco-pages/risk-tabs/*`, not this bundle. |
| `web/frontend/src/views/components/StopLossMonitoringTab.vue` | `web/frontend/src/views/EnhancedRiskMonitor.vue` | Keep view-local | Page-specific stop-loss tab for the legacy root risk monitor page. |
| `web/frontend/src/views/components/composables/useStopLossMonitoringTab.ts` | `web/frontend/src/views/components/StopLossMonitoringTab.vue` | Keep view-local | Tight page-local orchestration for one tab component. |
| `web/frontend/src/views/components/styles/RiskOverviewTab.css` | `web/frontend/src/views/components/RiskOverviewTab.vue` | Keep view-local | Style asset coupled to the same legacy risk-tab component. |
| `web/frontend/src/views/components/styles/StopLossMonitoringTab.css` | `web/frontend/src/views/components/StopLossMonitoringTab.vue` | Keep view-local | Style asset coupled to the same stop-loss tab bundle. |
| `web/frontend/src/views/composables/useAnalysis.ts` | `web/frontend/src/views/Analysis.vue` | Keep view-local | Root-page helper for a legacy analysis page that is not the active router implementation. |
| `web/frontend/src/views/composables/useAdvancedAnalysis.ts` | `web/frontend/src/views/AdvancedAnalysis.vue` | Keep view-local | Root-page helper for a legacy advanced analysis page, not the current approved migration target. |
| `web/frontend/src/views/composables/useBacktestWizard.ts` | `web/frontend/src/views/BacktestWizard.vue` | Keep view-local | Active router uses `ArtDecoBacktestAnalysis.vue`, so this remains a legacy root-page bundle. |
| `web/frontend/src/views/composables/useEnhancedDashboard.ts` | `web/frontend/src/views/EnhancedDashboard.vue` | Keep view-local | Root-page dashboard helper, not the current routed dashboard implementation. |
| `web/frontend/src/views/composables/useIndustryConceptAnalysis.ts` | `web/frontend/src/views/IndustryConceptAnalysis.vue` | Keep view-local | Legacy root-page helper; approved market/data migration targets use ArtDeco pages instead. |
| `web/frontend/src/views/composables/usePhase4Dashboard.ts` | `web/frontend/src/views/Phase4Dashboard.vue` | Keep view-local | Single-page helper with a separate demo duplicate already present under `views/demo/`. |
| `web/frontend/src/views/composables/usePortfolioManagement.ts` | `web/frontend/src/views/PortfolioManagement.vue` | Keep view-local | Page-specific portfolio manager helper for a non-routed legacy page. |
| `web/frontend/src/views/composables/usePyprofilingDemo.ts` | `web/frontend/src/views/PyprofilingDemo.vue` | Keep view-local | Demo-oriented root page helper, not part of the approved migration spine. |
| `web/frontend/src/views/composables/useSettings.ts` | `web/frontend/src/views/Settings.vue` | Keep view-local | Active router uses `ArtDecoSystemSettings.vue`, so this stays with the legacy root settings page. |
| `web/frontend/src/views/composables/useTechnicalAnalysis.ts` | `web/frontend/src/views/TechnicalAnalysis.vue` | Keep view-local | Legacy root-page helper; active router uses `analysis-tabs/KLineAnalysis.vue`, and a separate `views/technical/` implementation already exists. |
| `web/frontend/src/views/composables/useTechnicalAnalysis.types.ts` | `web/frontend/src/views/composables/useTechnicalAnalysis.ts` | Keep view-local | Type companion for the same legacy technical-analysis bundle. |
| `web/frontend/src/views/composables/useTechnicalAnalysis.shortcuts.ts` | `web/frontend/src/views/composables/useTechnicalAnalysis.ts` | Keep view-local | Shortcut companion for the same legacy technical-analysis bundle. |
| `web/frontend/src/views/composables/usemonitor.ts` | `web/frontend/src/views/monitor.vue` | Keep view-local | Legacy monitoring page helper; routed monitoring entry is the ArtDeco implementation. |
| `web/frontend/src/views/composables/useTradingDashboard.ts` | `web/frontend/src/views/TradingDashboard.vue` | Future `src/shared/composables` candidate | Still backs an active routed trade page; only extract after task `8.5` resolves the final `TradingDashboard` / `DealingRoom` disposition. |
| `web/frontend/src/views/composables/tradingDashboardActions.ts` | `web/frontend/src/views/composables/useTradingDashboard.ts` | Canonical shared-layer candidate | Pure transport/helper module with CSRF and trading action calls; belongs outside `views/` if the trade page is retained. |
| `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts` | `web/frontend/src/views/composables/useTradingDashboard.ts` | Keep with owning module | Test asset should move only if the owning composable moves in task `8.5`. |
| `web/frontend/src/views/composables/__node_tests__/tradingDashboardActions.test.ts` | `web/frontend/src/views/composables/tradingDashboardActions.ts` | Keep with owning module | Test asset should follow the helper only if that helper leaves `views/`. |

### Phase 2 Remap Result

- No files under `web/frontend/src/views/components/` qualify for direct Phase 2 extraction into `src/shared/components/`.
- Most files under `web/frontend/src/views/composables/` are legacy root-page bundles and should remain view-local until their owning pages are explicitly migrated or deprecated.
- The only currently live follow-up from this tree is the `TradingDashboard` pair:
  - `useTradingDashboard.ts` remains a conditional future `src/shared/composables` candidate.
  - `tradingDashboardActions.ts` is the only clear canonical shared-layer candidate discovered in this pass.
- This means the next safe `git mv` wave must not be driven by raw folder location alone; it must follow routed page ownership and the domain migration tasks that are already approved.

## Phase 3a / 3b Repo Truth Baseline

This section records the current repository truth for the approved Market / Data migration tasks before any new page-level move is attempted.

| Approved task | Current route / pageConfig target | Legacy ArtDeco source role | Current verdict |
| --- | --- | --- | --- |
| `4.1 Market-Realtime` | `/market/realtime` already resolves `web/frontend/src/views/market/Realtime.vue` in both router and pageConfig truth. | `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` is now a thin compatibility wrapper that forwards attrs into `Realtime.vue`. | Structural move already landed; do not repeat the original literal `git mv`. |
| `4.2 Market-Technical` | `/market/technical` already resolves `web/frontend/src/views/market/Technical.vue`. | `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` is a thin compatibility wrapper around `Technical.vue`. | Structural move already landed. |
| `4.3 Market-LHB` | `/market/lhb` already resolves `web/frontend/src/views/market/LHB.vue`. | `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` is a thin compatibility wrapper around `LHB.vue`. | Structural move already landed. |
| `4.4 Data-Industry` | `/data/industry` already resolves `web/frontend/src/views/data/Industry.vue`. | `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` is a thin compatibility wrapper around `Industry.vue`. | Structural move already landed. |
| `4.5 Data-Concept` | `/data/concept` already resolves `web/frontend/src/views/data/Concepts.vue`. | `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue` is a thin compatibility wrapper around `Concepts.vue`. | Structural move already landed. |
| `4.6 Data-FundFlow` | `/data/fund-flow` already resolves `web/frontend/src/views/data/FundFlow.vue`. | `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` is a thin compatibility wrapper around `FundFlow.vue`. | Structural move already landed. |
| `5.1 Data-Indicator` | `/data/indicator` already resolves `web/frontend/src/views/data/Advanced.vue` in router and pageConfig truth. | `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` is now the thin compatibility wrapper, while `web/frontend/src/views/data/Advanced.vue` owns the primary implementation. | Completed in the 2026-04-04 cutover batch. |

### Phase 3a / 3b Immediate Consequence

- Do not spend a future batch repeating the original literal `git mv` steps for `4.1` through `4.6`; the routed target files already exist and are already the active entrypoints.
- Treat the remaining ArtDeco market/data source files in those six tasks as compatibility wrappers, not as the primary routed implementation.
- The routed Market / Data target pages are now structurally aligned through `web/frontend/src/views/data/Advanced.vue`; future work in this area is compatibility-wrapper retirement or shared-layer normalization, not target-file ownership inversion.

## Phase 3c Repo Truth Baseline

This section records the current repository truth for the approved Watchlist migration tasks after landing the missing target entrypoints.

| Approved task | Current route / pageConfig target | Current implementation behind target | Current verdict |
| --- | --- | --- | --- |
| `6.1 Watchlist-Manage` | `/watchlist/manage` now resolves `web/frontend/src/views/watchlist/Manage.vue` in router truth; pageConfig now points to `Manage.vue`. | `Manage.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `6.2 Watchlist-Screener` | `/watchlist/screener` now resolves `web/frontend/src/views/watchlist/Screener.vue`; pageConfig points to `Screener.vue`. | `Screener.vue` is a thin compatibility wrapper around `web/frontend/src/views/stocks/Screener.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `6.3 Watchlist-Signals` | `/watchlist/signals` now resolves `web/frontend/src/views/watchlist/Signals.vue`; pageConfig now points to `Signals.vue`. | `Signals.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`. | Target entrypoint landed while preserving strategy-domain reuse. |

### Phase 3c Immediate Consequence

- The watchlist domain no longer depends on legacy source file paths as its primary routed entrypoints.
- Remaining watchlist work is implementation ownership and dependency normalization, not target-path creation.

## Phase 3d Repo Truth Baseline

This section records the current repository truth for the approved Strategy migration tasks after landing the missing target entrypoints.

| Approved task | Current route / pageConfig target | Current implementation behind target | Current verdict |
| --- | --- | --- | --- |
| `7.1 Strategy-Repo` | `/strategy/repo` now resolves `web/frontend/src/views/strategy/List.vue` in router truth; pageConfig now points to `List.vue`. | `List.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `7.2 Strategy-Parameters` | `/strategy/parameters` now resolves `web/frontend/src/views/strategy/Parameters.vue`; pageConfig points to `Parameters.vue`. | `Parameters.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `7.3 Strategy-Backtest` | `/strategy/backtest` now resolves `web/frontend/src/views/strategy/Backtest.vue`; pageConfig points to `Backtest.vue`. | `Backtest.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `7.4 Strategy-Optimization` | `/strategy/opt` now resolves `web/frontend/src/views/strategy/Optimization.vue`; pageConfig points to `Optimization.vue`. | `Optimization.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`. | Target entrypoint landed; compatibility retirement still pending. |

### Phase 3d Immediate Consequence

- The strategy domain no longer depends on legacy ArtDeco file paths as its primary routed entrypoints for repo, parameters, backtest, and optimization.
- Remaining strategy work is implementation ownership and dependency normalization, not target-path creation for tasks `7.1` through `7.4`.

## Phase 3e Repo Truth Baseline

This section records the current repository truth for the approved Trade migration tasks after landing the missing target entrypoints for tasks `8.1` through `8.4`.

| Approved task | Current route / pageConfig target | Current implementation behind target | Current verdict |
| --- | --- | --- | --- |
| `8.1 Trade-Center` | `/trade/positions` now resolves `web/frontend/src/views/trade/Center.vue` in router truth; pageConfig now points to `Center.vue`. | `Center.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `8.2 Trade-Signals` | `/trade/signals` now resolves `web/frontend/src/views/trade/Signals.vue`; pageConfig points to `Signals.vue`. | `Signals.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `8.3 Trade-Portfolio` | `/trade/portfolio` now resolves `web/frontend/src/views/trade/Portfolio.vue`; pageConfig points to `Portfolio.vue`. | `Portfolio.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `8.4 Trade-History` | `/trade/history` now resolves `web/frontend/src/views/trade/History.vue`; pageConfig points to `History.vue`. | `History.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue`. | Target entrypoint landed; compatibility retirement still pending. |

### Phase 3e Immediate Consequence

- The trade domain no longer depends on legacy ArtDeco file paths as its primary routed entrypoints for positions, signals, portfolio, and history.
- `trade-terminal` intentionally remains on `web/frontend/src/views/TradingDashboard.vue` per task `8.5` Option C, and task `8.6` stays blocked by the dashboard / dealing-room truth split.

## Phase 3f Repo Truth Baseline

This section records the current repository truth for the approved Risk migration tasks after landing the missing target entrypoints and inverting the existing placeholders for tasks `9.2` through `9.6`.

| Approved task | Current route / pageConfig target | Current implementation behind target | Current verdict |
| --- | --- | --- | --- |
| `9.2 Risk-Center` | `/risk/management` and alias `/risk-management` now resolve `web/frontend/src/views/risk/Center.vue` in router truth. No `risk-management` pageConfig entry exists in the current repo truth. | `Center.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`, which still imports `ArtDecoPageTemplate.vue`. | Target entrypoint landed; template retention preserved; pageConfig gap remains pre-existing truth. |
| `9.3 Risk-Overview` | `/risk/overview` now resolves `web/frontend/src/views/risk/Overview.vue`; pageConfig now points to `Overview.vue`. | `Overview.vue` is now a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `9.4 Risk-StopLoss` | `/risk/stop-loss` now resolves `web/frontend/src/views/risk/StopLoss.vue`; pageConfig now points to `StopLoss.vue`. | `StopLoss.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `9.5 Risk-Alerts` | `/risk/alerts` now resolves `web/frontend/src/views/risk/Alerts.vue`; pageConfig now points to `Alerts.vue`. | `Alerts.vue` is now a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `9.6 Risk-News` | `/risk/news` now resolves `web/frontend/src/views/risk/News.vue`; pageConfig now points to `News.vue`. | `News.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue`. | Target entrypoint landed; compatibility retirement still pending. |

### Phase 3f Immediate Consequence

- The approved risk routes for center, overview, stop-loss, alerts, and news no longer depend on legacy ArtDeco file paths as their primary routed entrypoints.
- The `ArtDecoPageTemplate.vue` dependency chain remains intact through `ArtDecoRiskManagement.vue`.
- `risk-pnl` remains an active extra route outside this micro-batch and still resolves `PortfolioOverviewTab.vue` in current repo truth.

## Phase 3g Repo Truth Baseline

This section records the current repository truth for the approved System migration tasks after landing the missing target entrypoints for tasks `10.1` through `10.4`.

| Approved task | Current route / pageConfig target | Current implementation behind target | Current verdict |
| --- | --- | --- | --- |
| `10.1 System-Config` | `/system/config` now resolves `web/frontend/src/views/system/Settings.vue`; pageConfig now points to `Settings.vue`. | `Settings.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `10.2 System-Health` | `/system/health` now resolves `web/frontend/src/views/system/Health.vue`; pageConfig now points to `Health.vue`. | `Health.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `10.3 System-API` | `/system/api` now resolves `web/frontend/src/views/system/API.vue`; pageConfig now points to `API.vue`. | `API.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue`. | Target entrypoint landed; compatibility retirement still pending. |
| `10.4 System-Data` | `/system/data` now resolves `web/frontend/src/views/system/DataSource.vue`; pageConfig now points to `DataSource.vue`. | `DataSource.vue` is a thin compatibility wrapper around `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`. | Target entrypoint landed; compatibility retirement still pending. |

### Phase 3g Immediate Consequence

- The approved system routes for config, health, API, and data no longer depend on legacy ArtDeco file paths as their primary routed entrypoints.
- The current batch only lands canonical target entry wrappers; deeper dependency extraction and legacy compatibility retirement remain future work.

## Trade-Domain Clarification For Task 8.5

This section records the repo-backed clarification for `openspec/changes/restructure-frontend-directory/tasks.md` task `8.5`.

| Evidence source | Finding |
| --- | --- |
| `web/frontend/src/router/index.ts` | `/trade/terminal` is an active child route and currently resolves `@/views/TradingDashboard.vue`. |
| `web/frontend/src/config/pageConfig.ts` | `trade-terminal` still declares `component: 'TradingDashboard.vue'`. |
| `web/frontend/src/views/` filesystem | There is no `DealingRoom.vue` or `Terminal.vue`; the only live implementation is `web/frontend/src/views/TradingDashboard.vue`. |
| `web/frontend/src/views/trading/` filesystem | The trade directory exists but currently contains `Execution.vue`, `Orders.vue`, `Positions.vue`, and `History.vue` only. |
| `docs/plans/frontend-page-optimization-list.md` | `DealingRoom` and `Trade-Terminal` are tracked as different pages: `DealingRoom` maps to `artdeco-pages/ArtDecoDashboard.vue`, while `Trade-Terminal` maps to `TradingDashboard.vue`. |
| `openspec/changes/restructure-frontend-directory/specs/frontend-structure/spec.md` | The trade-domain target anchor is `src/views/trade/Center.vue`, not `DealingRoom.vue`. |

### Task 8.5 Recommendation

- Recommended branch for the current approved change: `Option C` (`keep in current location`).
- Why `Option A` is not safe right now:
  - Renaming `TradingDashboard.vue` to `DealingRoom.vue` would collide with the existing mainline `DealingRoom` concept that already points to `ArtDecoDashboard.vue`.
  - The approved spec delta names the trade anchor `Center.vue`, so `DealingRoom.vue` is not the current spec-aligned target name either.
- Why `Option B` is not safe right now:
  - `TradingDashboard.vue` is still an active routed page with a verified `trade-terminal` API family.
  - Deprecating it now would remove a live route without a replacement implementation under `views/trade/`.
- Practical consequence for the next migration wave:
  - Keep `web/frontend/src/views/TradingDashboard.vue`, `web/frontend/src/views/composables/useTradingDashboard.ts`, `web/frontend/src/views/composables/tradingDashboardActions.ts`, and their paired test/style assets in place for now.
  - Do not execute a trade-domain `git mv` for this page until the naming conflict between `DealingRoom`, `Trade-Terminal`, and the spec target `trade/Center.vue` is reconciled.

## Dashboard / DealingRoom Blocker For Task 8.6

This section records why `openspec/changes/restructure-frontend-directory/tasks.md` task `8.6` cannot safely proceed today.

| Evidence source | Finding |
| --- | --- |
| `web/frontend/src/router/index.ts` | The live root route is `/dashboard`, and it renders `@/views/artdeco-pages/ArtDecoDashboard.vue`. |
| `web/frontend/src/config/pageConfig.ts` | The generated `dashboard` page config still binds `component: 'ArtDecoDashboard.vue'`, with title `交易室`. |
| `docs/plans/frontend-page-optimization-list.md` | The same component is tracked as the mainline `DealingRoom` page at `/dealing-room`, with verified P0 status. |
| `openspec/changes/restructure-frontend-directory/tasks.md` | Task `8.6` currently proposes deprecating `ArtDecoDashboard.vue`. |

### Task 8.6 Blocker Conclusion

- `ArtDecoDashboard.vue` is still a live mainline page under current router truth and current page-inventory truth.
- The repo currently has a naming drift, not a dead page:
  - router / pageConfig truth says `dashboard`
  - page-optimization truth says `DealingRoom`
  - both truths still point to `ArtDecoDashboard.vue`
- Because the same file is still the live mainline shell, task `8.6` must stay blocked.
- Safe next action is not a `git mv` to `deprecated/`; it is a truth-reconciliation step that decides whether:
  - `dashboard` and `DealingRoom` are aliases for one surviving page, or
  - one of those names should be formally retired in a separately reconciled change.
- Follow-up result: no existing approved OpenSpec change currently reconciles that truth, so a new proposal has been scaffolded as `reconcile-dashboard-dealingroom-truth` and now awaits approval before further implementation.
- Follow-up result: no existing approved OpenSpec change currently reconciles that truth, so a new proposal has been scaffolded as `reconcile-dashboard-dealingroom-truth` and now awaits approval before further implementation.

## Immediate Next Boundary

- Establish tracked target directories under `src/shared/`.
- Re-scope Phase 2 micro-batches against actual source locations:
  - `src/views/components/`
  - `src/views/composables/`
- Only start file moves after each candidate is classified as either:
  - keep in current canonical shared layer
  - move to `src/shared/*`
  - keep view-local
