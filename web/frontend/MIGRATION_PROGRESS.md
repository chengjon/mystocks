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
