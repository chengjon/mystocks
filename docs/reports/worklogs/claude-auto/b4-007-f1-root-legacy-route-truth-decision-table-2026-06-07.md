# B4.007-F1 Root Legacy Route-Truth Decision Table

Date: 2026-06-07

Mode: no-source

Authority:

- Source edit authority: false
- Test edit authority: false
- Deletion-retirement authority: false
- Allowed output: this decision table only
- Forbidden output: route changes, Vue source changes, test changes, deletion, retirement, bulk staging

## Boundary

This F1 package closes the no-source decision-table item listed by `B4.007-F`.

It covers only the dirty root legacy view group under `web/frontend/src/views/*.vue` that is not the current canonical route truth. It does not touch:

- ST-HOLD strategy files:
  - `web/frontend/src/views/BacktestWizard.vue`
  - `web/frontend/src/views/strategy/BatchScan.vue`
  - `web/frontend/src/views/strategy/ResultsQuery.vue`
  - `web/frontend/src/views/strategy/SingleRun.vue`
  - `web/frontend/src/views/strategy/StatsAnalysis.vue`
- `marketKlineData` hold:
  - `web/frontend/src/views/artdeco-pages/market-tabs/marketKlineData.ts`
  - `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`
- Closed B4.003-B4.006 packages
- B4.007 A-E source/test packages already committed
- External dirty files outside this root legacy route-truth group

## Evidence Snapshot

Read-only evidence used for this table:

| Check | Result |
|---|---|
| Current branch | `wip/root-dirty-20260403` |
| Current HEAD | `2b3f5dd211` |
| Staged files before F1 | empty |
| Router/menu/navigation/config exact refs to the 23 root legacy views | `0` exact runtime refs |
| Current router source of truth | `web/frontend/src/router/index.ts` |
| Current frontend structure source | `docs/guides/frontend-structure.md` |
| Prior B4.007 no-source reports | `b4-007-artdeco-root-legacy-route-truth-preflight-2026-06-07.md`, `b4-007-root-legacy-disposition-2026-06-07.md` |

Route-truth reminders:

- `/dashboard` is served by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- `/system/config` is served by `web/frontend/src/views/system/Settings.vue`.
- `/trade/terminal` remains served by `web/frontend/src/views/TradingDashboard.vue`.
- `/stock/graphics` is served by `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.
- Root legacy files listed below are not direct router components in current route truth.

Reference caveat:

- Some root legacy names still appear in E2E PageObject/helper files as class names, page-object labels, or legacy test vocabulary. That is not a runtime route import, but it is a deletion-retirement risk. Any future deletion package must include a focused test-reference cleanup plan and must not treat "no router import" as sufficient deletion authority.

## Decision Categories

| Category | Meaning | Source package implication |
|---|---|---|
| Preserve as compatibility wrapper | Dirty source is already a thin bridge to a canonical view/component or is small enough to review as a compatibility bridge. | May be considered by a future source-authorized wrapper package, split by domain. |
| Archive-only | Dirty source is a non-active legacy/static shell that points users toward canonical pages but is not current route truth. | Do not bulk-accept as active source. Preserve evidence here; future source acceptance requires per-domain approval. |
| Deletion-retirement candidate | Non-active demo/test shell with no current route truth role. | Requires explicit deletion-retirement approval, recovery evidence, GitNexus/OPENDOG gates, and focused tests. |
| Move to canonical route | Dirty source carries behavior that should migrate into an active canonical route. | No files were selected for this category in F1; no business payload was proven suitable for migration in this no-source pass. |

## Decision Table

| File | Current route truth | Evidence | F1 decision | Next package |
|---|---|---|---|---|
| `web/frontend/src/views/Dashboard.vue` | Not active; `/dashboard` uses `ArtDecoDashboard.vue`. | Thin wrapper importing `@/views/artdeco-pages/ArtDecoDashboard.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 dashboard-wrapper source package, if approved. |
| `web/frontend/src/views/EnhancedDashboard.vue` | Not active; `/dashboard` uses `ArtDecoDashboard.vue`. | Thin wrapper importing `@/views/artdeco-pages/ArtDecoDashboard.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 dashboard-wrapper source package, if approved. |
| `web/frontend/src/views/Phase4Dashboard.vue` | Not active; `/dashboard` uses `ArtDecoDashboard.vue`. | Thin wrapper importing `@/views/artdeco-pages/ArtDecoDashboard.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 dashboard-wrapper source package, if approved. |
| `web/frontend/src/views/EnhancedRiskMonitor.vue` | Not active; risk routes use `web/frontend/src/views/risk/*.vue`. | Thin wrapper importing `@/views/risk/Center.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 risk-wrapper source package, if approved. |
| `web/frontend/src/views/RiskMonitor.vue` | Not active; risk routes use `web/frontend/src/views/risk/*.vue`. | Thin wrapper importing `@/views/risk/Center.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 risk-wrapper source package, if approved. |
| `web/frontend/src/views/IndicatorLibrary.vue` | Not active; data indicator route uses `web/frontend/src/views/data/Advanced.vue`. | Thin wrapper importing `@/views/data/Advanced.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 data-wrapper source package, if approved. |
| `web/frontend/src/views/Market.vue` | Not active; current market/trade routes use canonical domain views. | Thin wrapper importing `@/views/trade/Portfolio.vue`; no exact router/menu ref. Mapping needs source review before acceptance because file name and target domain differ. | Preserve as compatibility-wrapper candidate, with domain-mapping review required. | F2 market/trade wrapper package, if approved. |
| `web/frontend/src/views/Settings.vue` | Not active; `/system/config` uses `web/frontend/src/views/system/Settings.vue`. | Thin wrapper importing `@/views/system/Settings.vue`; no exact router/menu ref. | Preserve as compatibility wrapper. | F2 system-wrapper source package, if approved. |
| `web/frontend/src/views/Wencai.vue` | Not active in current router. | Small wrapper importing `@/components/market/WencaiPanel.vue`; no exact router/menu ref. | Preserve as compatibility-wrapper candidate, with component/route role review required. | F2 market-wrapper source package, if approved. |
| `web/frontend/src/views/AdvancedAnalysis.vue` | Not active. | Static legacy analysis shell; no imports; no exact router/menu ref. | Archive-only. | F3 archive/deletion review only after explicit approval. |
| `web/frontend/src/views/Analysis.vue` | Not active. | Static legacy analysis shell; no imports; no exact router/menu ref. Legacy test vocabulary exists outside runtime route truth. | Archive-only. | F3 archive review plus test-vocabulary review. |
| `web/frontend/src/views/IndustryConceptAnalysis.vue` | Not active. | Static legacy industry/concept shell; no imports; no exact router/menu ref. | Archive-only. | F3 archive/deletion review only after explicit approval. |
| `web/frontend/src/views/MarketData.vue` | Not active. | Static legacy market-data shell; no imports; no exact router/menu ref. | Archive-only. | F3 archive review plus scan-menu test vocabulary review. |
| `web/frontend/src/views/monitor.vue` | Not active. | Static lowercase legacy monitor shell; no imports; no exact router/menu ref. Lowercase filename remains a platform/case-sensitivity risk. | Archive-only. | F3 archive review plus case-sensitive path/test review. |
| `web/frontend/src/views/PortfolioManagement.vue` | Not active. | Static legacy portfolio shell; no imports; no exact router/menu ref. | Archive-only. | F3 portfolio archive review only after explicit approval. |
| `web/frontend/src/views/RealTimeMonitor.vue` | Not active. | Static legacy realtime-monitor shell; no imports; no exact router/menu ref. | Archive-only. | F3 monitor archive review only after explicit approval. |
| `web/frontend/src/views/StockDetail.vue` | Not active. | Static legacy stock-detail shell; no imports; no exact router/menu ref. | Archive-only. | F3 market/detail archive review only after explicit approval. |
| `web/frontend/src/views/Stocks.vue` | Not active. | Static legacy stock-list shell; no imports; no exact router/menu ref. Legacy test vocabulary exists outside runtime route truth. | Archive-only. | F3 archive review plus test-vocabulary review. |
| `web/frontend/src/views/TaskManagement.vue` | Not active. | Static legacy task shell; no imports; no exact router/menu ref. | Archive-only. | F3 task archive review only after explicit approval. |
| `web/frontend/src/views/TdxMarket.vue` | Not active. | Static legacy TDX shell; no imports; no exact router/menu ref. | Archive-only. | F3 market archive review only after explicit approval. |
| `web/frontend/src/views/TechnicalAnalysis.vue` | Not active. | Static legacy technical-analysis shell; no imports; no exact router/menu ref. Legacy test vocabulary exists outside runtime route truth. | Archive-only. | F3 archive review plus test-vocabulary review. |
| `web/frontend/src/views/StockAnalysisDemo.vue` | Not active. | Demo-named static shell; no imports; no exact router/menu ref. | Deletion-retirement candidate. | F3 deletion-retirement package only with explicit approval. |
| `web/frontend/src/views/TestPage.vue` | Not active. | Test/sandbox-named static shell; no imports; no exact router/menu ref. | Deletion-retirement candidate. | F3 deletion-retirement package only with explicit approval. |

## Counts

| F1 decision | Count |
|---|---:|
| Preserve as compatibility wrapper/candidate | 9 |
| Archive-only | 12 |
| Deletion-retirement candidate | 2 |
| Move to canonical route | 0 |
| Total | 23 |

## Future Package Split

Recommended source-authorized queue after F1:

1. `B4.007-F2a dashboard/system/risk thin wrappers`
   - Candidate files: `Dashboard.vue`, `EnhancedDashboard.vue`, `Phase4Dashboard.vue`, `Settings.vue`, `EnhancedRiskMonitor.vue`, `RiskMonitor.vue`
   - Required gates: GitNexus fresh, impact/detect, OPENDOG verification, frontend type-check, focused shell/wrapper tests.

2. `B4.007-F2b data/market thin wrappers`
   - Candidate files: `IndicatorLibrary.vue`, `Market.vue`, `Wencai.vue`
   - Required gates: GitNexus fresh, impact/detect, OPENDOG verification, frontend type-check, focused data/market route tests.
   - Extra caution: `Market.vue` maps to `trade/Portfolio.vue`; source acceptance must verify that this is intentional compatibility, not a wrong-domain bridge.

3. `B4.007-F3 archive/deletion-retirement`
   - Candidate files: all archive-only rows and the two deletion-retirement candidates.
   - Required authority: explicit deletion-retirement approval before any file deletion, restoration, or full-file retirement.
   - Required evidence: exact route/import/runtime string checks, test vocabulary impact, GitNexus fresh, OPENDOG, focused E2E where legacy names are referenced.

## Closeout

This report is not source authorization. It only records route-truth disposition for the 23 root legacy dirty files.

No root legacy source file is staged by F1. No test file is staged by F1. No deletion-retirement action is authorized by F1.
