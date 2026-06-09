# Frontend View Checklist: `views/artdeco-pages/components/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/components/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `AnalysisIndicators.vue` | Vue support component | `/data/advanced` support | imported by `views/data/Advanced.vue` | data advanced specs + data audit docs | `canonical-support-asset/data-advanced-indicators` | `not-archive-scope` |
| `AnalysisScreener.vue` | Vue support component | `/data/advanced` support | imported by `views/data/Advanced.vue` | data advanced specs + data audit docs | `canonical-support-asset/data-advanced-screener` | `not-archive-scope` |
| `AnalysisResults.vue` | Vue support component | `/data/advanced` support | imported by `views/data/Advanced.vue` | data advanced specs + data audit docs | `canonical-support-asset/data-advanced-results` | `not-archive-scope` |
| `AnomalyAlerts.vue` | Vue support component | advanced anomaly support | imported by `components/artdeco/advanced/ArtDecoAnomalyTracking.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/anomaly-alerts` | `not-archive-scope` |
| `AnomalyPatterns.vue` | Vue support component | advanced anomaly support | imported by `components/artdeco/advanced/ArtDecoAnomalyTracking.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/anomaly-patterns` | `not-archive-scope` |
| `BuffettModel.vue` | Vue support component | advanced decision-model support | imported by `components/artdeco/advanced/ArtDecoDecisionModels.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/decision-model-buffett` | `not-archive-scope` |
| `OneilModel.vue` | Vue support component | advanced decision-model support | imported by `components/artdeco/advanced/ArtDecoDecisionModels.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/decision-model-oneil` | `not-archive-scope` |
| `LynchModel.vue` | Vue support component | advanced decision-model support | imported by `components/artdeco/advanced/ArtDecoDecisionModels.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/decision-model-lynch` | `not-archive-scope` |
| `FinancialMetrics.vue` | Vue support component | advanced valuation support | imported by `components/artdeco/advanced/ArtDecoFinancialValuation.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/financial-metrics` | `not-archive-scope` |
| `DupontAnalysis.vue` | Vue support component | advanced valuation support | imported by `components/artdeco/advanced/ArtDecoFinancialValuation.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/dupont-analysis` | `not-archive-scope` |
| `PanoramaIndices.vue` | Vue support component | advanced market-panorama support | imported by `components/artdeco/advanced/ArtDecoMarketPanorama.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/panorama-indices` | `not-archive-scope` |
| `PanoramaCapitalFlow.vue` | Vue support component | advanced market-panorama support | imported by `components/artdeco/advanced/ArtDecoMarketPanorama.vue` | inventory + guard-map + advanced component import | `canonical-support-asset/panorama-capital-flow` | `not-archive-scope` |
| `ArtDecoTradingSignalsControls.vue` | Vue support component | `/trade/signals` support | imported by `views/trade/Signals.vue` | trade signals specs + trading-tabs checklist | `canonical-support-asset/trade-signals-controls` | `not-archive-scope` |
| `ArtDecoAttributionAnalysis.vue` | Vue static/local-data component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/attribution-static-asset` | `not-archive-approved` |
| `ArtDecoAttributionControls.vue` | Vue local-state control component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/attribution-control-asset` | `not-archive-approved` |
| `ArtDecoPerformanceOverview.vue` | Vue static metrics component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/performance-static-asset` | `not-archive-approved` |
| `ArtDecoSignalHistory.vue` | Vue signal history component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/signal-history-asset` | `not-archive-approved` |
| `ArtDecoSignalMonitoringMetrics.vue` | Vue signal metrics component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/signal-metrics-asset` | `not-archive-approved` |
| `ArtDecoSignalMonitoringOverview.vue` | Vue signal overview component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/signal-overview-asset` | `not-archive-approved` |
| `ArtDecoTradingHistoryControls.vue` | Vue trade-history control component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/trade-history-controls-asset` | `not-archive-approved` |
| `MarketConcepts.vue` | Vue market concept component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/market-concepts-asset` | `not-archive-approved` |
| `MarketFundFlow.vue` | Vue market fund-flow component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/market-fund-flow-asset` | `not-archive-approved` |
| `MarketPlaceholder.vue` | Vue placeholder component | no current source importer found | no active source import in focused scan | inventory + guard-map only | `candidate-review/market-placeholder-asset` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts` does not directly import files in this directory, but multiple routed canonical pages/components import them as body support.
- `views/data/Advanced.vue` imports `AnalysisIndicators.vue`, `AnalysisScreener.vue`, and `AnalysisResults.vue` for the `/data/advanced` implementation.
- `components/artdeco/advanced/*` imports anomaly, decision-model, valuation, and panorama subcomponents from this directory.
- `views/trade/Signals.vue` imports `ArtDecoTradingSignalsControls.vue`, while `ArtDecoTradingSignals.vue` lives in `trading-tabs/*`.
- No current source importer was found for the attribution, performance overview, signal history/metrics/overview, trading history controls, and market placeholder/concept/fund-flow components in the focused scan.

## Hidden Reference And Guard Evidence

- `web/frontend/tests/unit/views/data-advanced-screening-truth.spec.ts`, `data-indicator-details.spec.ts`, `data-advanced-cutover.spec.ts`, and `views/data/__tests__/Advanced.spec.ts` stub or assert the `Analysis*` component boundary.
- Historical `audit-20260425-01` data batch docs identify `AnalysisIndicators.vue`, `AnalysisScreener.vue`, and `AnalysisResults.vue` as shared data-analysis owners during prior repairs.
- `frontend-view-guard-map-2026-05-10.json` records every component in this directory, including those without current source importers.
- Inventory marks several inactive components with selector/stats-strip signals, so they require asset absorption or explicit successor decisions before any archive move.

## Functional Asset Assessment

- The `Analysis*` group is active canonical `/data/advanced` support and must be excluded from archive flow.
- The anomaly, decision-model, valuation, and panorama groups are active advanced ArtDeco support components, even though they are not route pages themselves.
- `ArtDecoTradingSignalsControls.vue` is active trade signals support. It should be considered together with `/trade/signals` and `trading-tabs/ArtDecoTradingSignals.vue`.
- The attribution/performance/signal-monitoring/trading-history/market placeholder group has no current source importer in the focused scan. These are candidate assets, not deletion-approved files, because they still may contain reusable UI fragments or historical guard-map references.
- Several candidate files contain hardcoded local data, placeholder copy, or static metrics. That lowers their retention strength but does not satisfy archive approval without successor mapping.

## Redundant Page Decision

No file in this batch is archive-approved.

- Active support components are excluded from archive flow.
- Candidate components without current importers remain `candidate-review/*`, not `archive-approved`, because they still need successor mapping and asset absorption review.
- `MarketPlaceholder.vue` is the closest retirement candidate because it is an explicit placeholder shell, but it still requires a formal `no-successor-needed` rationale and hidden-reference check in an approved mutation batch.

## Follow-Up Notes

- If consolidating this directory, first move active support components toward their owning domains: `/data/advanced`, `components/artdeco/advanced`, and `/trade/signals`.
- For inactive signal/attribution/performance components, compare against current canonical `/trade/signals`, `/trade/history`, `/trade/portfolio`, and shared attribution components before archive approval.
- Do not bulk archive `components/*`; it contains both current route support and candidate assets with different owners.
