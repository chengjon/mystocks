# Frontend View Checklist: `views/artdeco-pages/risk-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/risk-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoRiskMonitor.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/risk/Center.vue` | `ArtDecoRiskMonitor.spec.ts`; secondary audit docs | `compat-retained/risk-center-wrapper` | `not-archive-approved` |
| `ArtDecoAnnouncementMonitor.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/risk/News.vue` | risk audit docs + guard-map | `compat-retained/risk-news-wrapper` | `not-archive-approved` |
| `ArtDecoRiskAlerts.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/risk/Alerts.vue` | risk audit docs + guard-map | `compat-retained/risk-alerts-wrapper` | `not-archive-approved` |
| `RiskOverviewTab.vue` | Vue legacy wrapper | no direct route/menu owner | wraps `views/risk/Overview.vue` | `risk-wrapper-retention.spec.ts`; risk audit docs | `compat-retained/risk-overview-wrapper` | `not-archive-approved` |
| `StopLossMonitorTab.vue` | Vue legacy wrapper | no direct route/menu owner | wraps `views/risk/StopLoss.vue` | `risk-wrapper-retention.spec.ts`; risk audit docs | `compat-retained/risk-stop-loss-wrapper` | `not-archive-approved` |
| `ArtDecoRiskOverviewPanel.vue` | Vue active support component | canonical `/risk/center` support | imported by `views/risk/Center.vue` and `_templates/ExampleRiskManagement.vue` | component spec + risk-center template retention spec | `canonical-support-asset/risk-center-overview-panel` | `not-archive-scope` |
| `ArtDecoRiskStatsGrid.vue` | Vue active stats component | canonical `/risk/center` support | imported by `views/risk/Center.vue` and `_templates/ExampleRiskManagement.vue` | component spec + risk audit docs | `canonical-support-asset/risk-center-stats-grid` | `not-archive-scope` |
| `ArtDecoRiskStockPanel.vue` | Vue active support component | canonical `/risk/center` support | imported by `views/risk/Center.vue` and `_templates/ExampleRiskManagement.vue` | component spec + risk audit docs | `canonical-support-asset/risk-center-stock-panel` | `not-archive-scope` |
| `riskManagementHelpers.ts` | helper/types/config module | canonical `/risk/center` support | imported by `views/risk/Center.vue`, risk panel components, and template example | node tests + module presence test | `canonical-support-asset/risk-center-helpers` | `not-archive-scope` |
| `riskManagementData.ts` | data normalization module | canonical `/risk/center` support | imported by `views/risk/Center.vue`; depends on `riskManagementHelpers.ts` types | node tests + risk audit docs | `canonical-support-asset/risk-center-data-transform` | `not-archive-scope` |
| `stopLossMonitorData.ts` | data normalization module | canonical `/risk/stop-loss` support | imported by `views/risk/StopLoss.vue` | node tests + risk wrapper retention spec | `canonical-support-asset/risk-stop-loss-data-transform` | `not-archive-scope` |

## Route And Menu Truth

- `router/index.ts` owns the canonical risk routes under `views/risk/*`; this directory does not currently own direct menu route truth.
- `ArtDecoTradingCenter.vue` still imports `ArtDecoRiskMonitor.vue`, `ArtDecoAnnouncementMonitor.vue`, and `ArtDecoRiskAlerts.vue` for function keys `risk-monitor`, `announcement-monitor`, and `risk-alerts`.
- `views/risk/Center.vue` directly imports `ArtDecoRiskOverviewPanel.vue`, `ArtDecoRiskStatsGrid.vue`, `ArtDecoRiskStockPanel.vue`, `riskManagementHelpers.ts`, and `riskManagementData.ts`.
- `views/risk/StopLoss.vue` directly imports `buildStopLossRows`, `pickPrimaryStopLossWatchlist`, and `StopLossRow` from `stopLossMonitorData.ts`.
- `RiskOverviewTab.vue` and `StopLossMonitorTab.vue` are thin legacy wrappers around canonical risk route pages, not independent data owners.

## Hidden Reference And Guard Evidence

- `web/frontend/tests/unit/views/risk-wrapper-retention.spec.ts` explicitly retains the legacy wrapper chain for `RiskOverviewTab.vue`, `StopLossMonitorTab.vue`, `ArtDecoRiskAlerts.vue`, and `ArtDecoAnnouncementMonitor.vue`.
- `web/frontend/tests/unit/views/risk-center-template-retention.spec.ts` checks that the canonical risk center continues to import the ArtDeco risk center support components.
- Component tests exist for `ArtDecoRiskMonitor.vue`, `ArtDecoRiskOverviewPanel.vue`, `ArtDecoRiskStatsGrid.vue`, and `ArtDecoRiskStockPanel.vue`.
- Node tests cover `riskManagementData.ts`, `riskManagementHelpers.ts`, `riskManagementModulePresence.test.ts`, and `stopLossMonitorData.ts`.
- Historical risk batches `risk-batch-02/03/04/06/09/10/11/13/14/15/16/17/18` document prior repairs and explicitly treat these files as canonical support assets or compatibility consumers, not standalone archive candidates.
- `frontend-view-guard-map-2026-05-10.json` records references to wrappers, support components, helper modules, and tests in this directory.

## Functional Asset Assessment

- The compatibility wrappers are intentionally thin and preserve legacy ArtDeco function-tree or tab entry points while canonical risk bodies live under `views/risk/*`.
- The risk center panel components and helpers are active canonical support even though they physically live under `artdeco-pages/risk-tabs`; moving them would be a helper-ownership refactor, not redundant-page cleanup.
- `riskManagementData.ts` and `stopLossMonitorData.ts` are data truth normalization assets. They parse unknown payloads into verified UI rows and avoid replacing failed or missing runtime state with fake snapshots.
- `ArtDecoRiskStockPanel.vue` is a deliberately static/pending single-name entry, not a fake live tab. Its current value is honest feature boundary communication.
- The initial constants in `riskManagementHelpers.ts` still include historical sample defaults, but canonical `views/risk/Center.vue` initializes from `toRiskManagementMetrics(null)` and API-loaded transforms. Treat any cleanup of sample defaults as a targeted code batch, not archive evidence.

## Redundant Page Decision

No file in this batch is archive-approved.

- Canonical support assets are excluded from archive flow because current risk route pages import them directly.
- Compatibility wrappers are retained until their legacy `ArtDecoTradingCenter` and wrapper-retention guards are retired in an approved mutation batch.
- Data-transform helpers are retained with their tests because they encode current verified snapshot and no-fake-data behavior.
- File location under `artdeco-pages/risk-tabs` is not sufficient evidence of redundancy.

## Follow-Up Notes

- If the project wants cleaner ownership, consider relocating risk center components/helpers beside `views/risk/Center.vue` only through an approved refactor that updates imports, tests, guard-map docs, and historical wrapper expectations together.
- If retiring legacy wrappers, first update `ArtDecoTradingCenter.vue` function-key mappings and `risk-wrapper-retention.spec.ts`; do not remove wrappers by static orphan search alone.
- Keep `stopLossMonitorData.ts` tied to `/risk/stop-loss` verification semantics unless a canonical risk-domain helper location is approved.
