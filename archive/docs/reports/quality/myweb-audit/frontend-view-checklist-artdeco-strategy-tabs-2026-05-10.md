# Frontend View Checklist: `views/artdeco-pages/strategy-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/strategy-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoStrategyManagement.vue` | Vue canonical body | `/strategy/repo` through `views/strategy/List.vue` | `views/strategy/List.vue`; `ArtDecoTradingCenter.vue` function key `strategy-management` | component spec + strategy audit docs | `canonical-route-body/strategy-repo` | `not-archive-scope` |
| `StrategyParametersTab.vue` | Vue canonical body | `/strategy/parameters` through `views/strategy/Parameters.vue` | `views/strategy/Parameters.vue` | component spec + parameter data specs | `canonical-route-body/strategy-parameters` | `not-archive-scope` |
| `StrategySignalsTab.vue` | Vue active route body | `/strategy/signals`; `/watchlist/signals` wrapper | router imports this file directly; `views/watchlist/Signals.vue` wraps it | component spec + watchlist signals spec + store standardization spec | `canonical-route-body/strategy-signals` | `not-archive-scope` |
| `ArtDecoBacktestAnalysis.vue` | Vue canonical body | `/strategy/backtest` through `views/strategy/Backtest.vue` | `views/strategy/Backtest.vue`; `ArtDecoTradingCenter.vue` function key `backtest-analysis` | backtest specs + strategy audit docs | `canonical-route-body/strategy-backtest` | `not-archive-scope` |
| `ArtDecoStrategyOptimization.vue` | Vue canonical body | `/strategy/opt` through `views/strategy/Optimization.vue` | `views/strategy/Optimization.vue`; `ArtDecoTradingCenter.vue` function key `strategy-optimization` | component spec + source-policy node test | `canonical-route-body/strategy-optimization` | `not-archive-scope` |
| `BacktestHeader.vue` | Vue support component | canonical `/strategy/backtest` support | imported by `ArtDecoBacktestAnalysis.vue` | backtest component specs | `canonical-support-asset/backtest-header` | `not-archive-scope` |
| `BacktestKpiGrid.vue` | Vue support component | canonical `/strategy/backtest` support | imported by `ArtDecoBacktestAnalysis.vue` | `BacktestKpiGrid.spec.ts` + backtest specs | `canonical-support-asset/backtest-kpi-grid` | `not-archive-scope` |
| `BacktestWorkbenchTabs.vue` | Vue support component | canonical `/strategy/backtest` support | imported by `ArtDecoBacktestAnalysis.vue` | backtest specs | `canonical-support-asset/backtest-tabs` | `not-archive-scope` |
| `backtestAnalysisHelpers.ts` | helper module | canonical `/strategy/backtest` support | imported by `backtestAnalysisViewModel.ts` | `backtestModulePresence.test.ts` + audit docs | `canonical-support-asset/backtest-helpers` | `not-archive-scope` |
| `backtestAnalysisViewModel.ts` | composable/view model | canonical `/strategy/backtest` support | imported by `ArtDecoBacktestAnalysis.vue` | backtest specs + many strategy audit batches | `canonical-support-asset/backtest-view-model` | `not-archive-scope` |
| `backtestQuickRun.ts` | compatibility re-export | canonical backtest contract bridge | re-exports `@/composables/strategy/backtestContract` helpers | backtest module references | `compat-support-reexport/backtest-quick-run` | `not-archive-approved` |
| `strategyCrossTabNavigation.ts` | helper module | strategy cross-tab support | imported by management, parameters, signals, optimization, and backtest view model | strategy page specs | `canonical-support-asset/strategy-cross-tab-navigation` | `not-archive-scope` |
| `strategyLifecycleAvailability.ts` | helper module | strategy management support | imported by `ArtDecoStrategyManagement.vue` | node test | `canonical-support-asset/strategy-lifecycle-policy` | `not-archive-scope` |
| `strategyOptimizationSourcePolicy.ts` | helper module | strategy optimization support | imported by `ArtDecoStrategyOptimization.vue` and view model | node test | `canonical-support-asset/optimization-source-policy` | `not-archive-scope` |
| `strategyOptimizationViewModel.ts` | helper/view model | strategy optimization support | imported by `ArtDecoStrategyOptimization.vue` | optimization specs | `canonical-support-asset/optimization-view-model` | `not-archive-scope` |
| `strategyOptimizationWriteback.ts` | helper module | strategy optimization support | imported by `ArtDecoStrategyOptimization.vue` | optimization specs | `canonical-support-asset/optimization-writeback` | `not-archive-scope` |
| `strategyParametersData.ts` | data normalization module | strategy parameters support | imported by `StrategyParametersTab.vue` | strategy parameter specs | `canonical-support-asset/strategy-parameters-data` | `not-archive-scope` |
| `strategySignalsData.ts` | data normalization module | strategy, watchlist, and trade signal support | imported by `StrategySignalsTab.vue` and `views/trade/Signals.vue` | node test + signal specs | `canonical-support-asset/strategy-signals-data` | `not-archive-scope` |
| `styles/*.scss` and `components/styles/*.scss` | style support assets | strategy route body support | imported by owning Vue files | style references + audit docs | `canonical-support-asset/strategy-tab-styles` | `not-archive-scope` |

## Route And Menu Truth

- `router/index.ts`: `/strategy/signals` directly imports `StrategySignalsTab.vue`; `/strategy/repo`, `/strategy/parameters`, `/strategy/backtest`, and `/strategy/opt` route through thin wrappers in `views/strategy/*`.
- `views/strategy/List.vue`, `Parameters.vue`, `Backtest.vue`, and `Optimization.vue` delegate to this directory, so these ArtDeco bodies are current strategy route implementations rather than redundant views.
- `views/watchlist/Signals.vue` wraps `StrategySignalsTab.vue` with `surface-variant="watchlist"`, so the file also owns `/watchlist/signals` body behavior.
- `views/trade/Signals.vue` imports `strategySignalsData.ts` to share signal payload normalization.
- `ArtDecoTradingCenter.vue` still imports `ArtDecoStrategyManagement.vue`, `ArtDecoBacktestAnalysis.vue`, and `ArtDecoStrategyOptimization.vue` into legacy function keys.

## Hidden Reference And Guard Evidence

- `ArtDecoBacktestAnalysis.spec.ts`, `ArtDecoBacktestAttribution.spec.ts`, `ArtDecoStrategyManagement.spec.ts`, `ArtDecoStrategyOptimization.spec.ts`, `StrategyParametersTab.spec.ts`, and `StrategySignalsTab.spec.ts` guard the primary pages.
- `components/__tests__/BacktestKpiGrid.spec.ts` guards the KPI component used by the canonical backtest page.
- Node tests cover backtest module presence, lifecycle availability, optimization source policy, and strategy signal data normalization.
- Historical strategy audit batches document repeated repairs for provenance, freshness, selector state, writeback, and backtest attribution across these files.
- `frontend-view-guard-map-2026-05-10.json` and the menu-view structure audit both record strategy tab route/support references.

## Functional Asset Assessment

- This directory currently acts as the real implementation layer for multiple strategy routes; `views/strategy/*` is mostly a route-wrapper layer.
- Backtest support files are not disposable local helpers: they encode task status, quick-run handoff, strategy context sync, report freshness, KPI display, and workbench tabs.
- Strategy management, parameters, signals, and optimization share cross-tab navigation and strategy context semantics. Splitting or moving these files requires a coordinated ownership refactor.
- `StrategySignalsTab.vue` is multi-surface by design: strategy route plus watchlist signal route. Its data normalizer is also reused by trade signals.
- Existing mock fallback and embedded-source policy should be treated as runtime behavior to audit in code batches, not archive evidence.

## Redundant Page Decision

No file in this batch is archive-approved.

- Current route bodies and directly imported helpers/components are excluded from archive flow.
- Compatibility import through `ArtDecoTradingCenter.vue` increases retention pressure for the three embedded strategy modules.
- Style files are tied to owning route bodies and must not be moved or archived independently.
- `backtestQuickRun.ts` is only a re-export bridge, but it still requires import retirement proof before any cleanup; it is not approved for archive by this checklist.

## Follow-Up Notes

- If the long-term goal is a cleaner directory shape, plan a mutation batch that moves canonical strategy route bodies under `views/strategy/` and updates wrappers, tests, route docs, and `ArtDecoTradingCenter` compatibility imports together.
- If retiring `ArtDecoTradingCenter` strategy function keys, update function-key tests and historical guard expectations in the same approved batch.
- Keep `strategySignalsData.ts` migration coupled with `/strategy/signals`, `/watchlist/signals`, and `/trade/signals`; it is shared data truth, not a page-only asset.
