# Frontend View Checklist: `views/artdeco-pages/trading-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/trading-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoSignalsView.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/trade/Signals.vue` | trade audit docs + guard-map | `compat-retained/trade-signals-wrapper` | `not-archive-approved` |
| `ArtDecoHistoryView.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/trade/History.vue` | `ArtDecoHistoryView.spec.ts`; secondary audit docs | `compat-retained/trade-history-wrapper` | `not-archive-approved` |
| `ArtDecoPositionMonitor.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/trade/Center.vue` | strategy/trade audit docs + guard-map | `compat-retained/trade-position-wrapper` | `not-archive-approved` |
| `ArtDecoPerformanceAnalysis.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/trade/Portfolio.vue` | `ArtDecoPerformanceAnalysis.spec.ts`; secondary audit docs | `compat-retained/trade-portfolio-wrapper` | `not-archive-approved` |
| `ArtDecoTradingHistory.vue` | Vue routed/support surface | no direct menu owner | wraps `views/trade/History.vue`; referenced by historical trade docs | guard-map + trade audit docs | `compat-retained/trade-history-surface` | `not-archive-approved` |
| `ArtDecoTradingPositions.vue` | Vue routed surface wrapper | `/strategy/pos` | router imports this file; wraps `views/trade/Center.vue`; `views/trading/Positions.vue` also wraps it | `trading/Positions.spec.ts`; strategy/trade audit docs | `canonical-route-wrapper/strategy-pos` | `not-archive-scope` |
| `ArtDecoTradingSignals.vue` | Vue active component asset | `/trade/signals` through `views/trade/Signals.vue` | imported by `views/trade/Signals.vue` | trade-batch manifests + guard-map | `canonical-support-asset/trade-signals-table` | `not-archive-scope` |
| `ArtDecoTradingStats.vue` | Vue stats card asset | no direct route/menu owner found | no current source importer found in focused scan | inventory + guard-map references | `candidate-review/trading-stats-asset` | `not-archive-approved` |
| `tradingDataTransform.ts` | helper module | canonical trade support | imported by `views/trade/Center.vue` and `views/trade/History.vue` | `tradingDataTransform.spec.ts`; trade audit docs | `canonical-support-asset/trade-data-transform` | `not-archive-scope` |

## Route And Menu Truth

- `router/index.ts`: `/strategy/pos` imports `ArtDecoTradingPositions.vue` directly, so that file is a current route wrapper and must be excluded from archive flow.
- `views/trade/Signals.vue`: imports `ArtDecoTradingSignals.vue` and `ArtDecoTradingSignalsControls.vue`, so the trading signals table is active route support.
- `views/trade/Center.vue` and `views/trade/History.vue`: import `tradingDataTransform.ts` for live positions and trade-history payload normalization.
- `ArtDecoTradingCenter.vue`: still maps function-tree keys `trade-signals`, `trade-history`, `trade-positions`, and `trade-portfolio` to the four compatibility wrappers in this directory.

## Hidden Reference And Guard Evidence

- `ArtDecoHistoryView.spec.ts` verifies `ArtDecoHistoryView.vue` reuses canonical `views/trade/History.vue` and does not keep the old placeholder shell.
- `ArtDecoPerformanceAnalysis.spec.ts` verifies `ArtDecoPerformanceAnalysis.vue` reuses canonical `views/trade/Portfolio.vue`.
- `tradingDataTransform.spec.ts` covers the shared transformation helpers used by canonical trade route pages.
- Historical myweb-audit docs identify `ArtDecoPositionMonitor.vue` and `ArtDecoTradingPositions.vue` as part of the `/trade/positions` and `/strategy/pos` compatibility chain.
- `frontend-view-guard-map-2026-05-10.json` includes references across all trading-tab wrappers, helper tests, and route/support imports.

## Functional Asset Assessment

- The first wrapper group is active compatibility infrastructure: they preserve `ArtDecoTradingCenter` function-tree behavior while canonical trade bodies live under `views/trade/*`.
- `ArtDecoTradingPositions.vue` is stronger than a normal compatibility wrapper because it is still imported directly by the router for `/strategy/pos`.
- `ArtDecoTradingSignals.vue` is a reusable table component currently used by the canonical `/trade/signals` page, so it is not a redundant view despite living under `artdeco-pages/trading-tabs`.
- `tradingDataTransform.ts` is active canonical trade support and should eventually be considered for relocation only through an approved helper-ownership refactor.
- `ArtDecoTradingStats.vue` has stats-strip semantics but no current source importer found in the focused scan; it may be an absorbable UI asset, but it is not archive-approved without comparing against canonical trade signal/portfolio summary coverage.

## Redundant Page Decision

No file in this batch is archive-approved.

- Active route wrappers and active helper/component assets are excluded from archive flow.
- `ArtDecoTradingStats.vue` remains `candidate-review/trading-stats-asset`, not `archive-approved`, because it has UI structure that may be absorbed or formally retired only after successor mapping.
- Any future cleanup must handle `ArtDecoTradingCenter`, `/strategy/pos`, `/trade/signals`, `views/trading/Positions.vue`, and the helper tests together; file-location alone is not evidence of redundancy.

## Follow-Up Notes

- If the project wants to move `tradingDataTransform.ts` out of `artdeco-pages`, update `views/trade/Center.vue`, `views/trade/History.vue`, tests, and guard-map references in one mutation batch.
- If retiring `ArtDecoTradingStats.vue`, record whether its metric cards are already covered by `/trade/signals`, `/trade/portfolio`, or another canonical route.
- Do not archive `ArtDecoTradingPositions.vue` while `/strategy/pos` still imports it directly.
