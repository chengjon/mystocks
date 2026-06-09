# Page Audit: Advanced Analysis Child Static Shells

## Scope
- Batch: `secondary-batch-40`
- Execution surface: `code-review-only`
- Owners:
  - `web/frontend/src/views/advanced-analysis/FundamentalAnalysisView.vue`
  - `web/frontend/src/views/advanced-analysis/MarketPanoramaView.vue`
  - `web/frontend/src/views/advanced-analysis/RadarAnalysisView.vue`
  - `web/frontend/src/views/advanced-analysis/TechnicalAnalysisView.vue`
  - `web/frontend/src/views/advanced-analysis/TimeSeriesView.vue`
  - `web/frontend/src/views/advanced-analysis/TradingSignalsView.vue`

## Finding
The six high-priority `advanced-analysis/*` child pages were no longer active route truth, but several still rendered local pseudo-analysis surfaces:

- financial ratios, profitability tables, and Dupont analysis from nullable props
- technical indicator cards with default signal labels
- radar dimensions with hardcoded scores, investment advice, and insight rows
- trading signal counters with default strength and confidence values

Because the parent `AdvancedAnalysis.vue` had already been degraded to an honest static shell and no independent canonical owner exists for these children, preserving local analysis state would reintroduce a secondary advanced-analysis truth surface.

## Repair
Each child page now renders an honest static shell that states it is not connected to canonical verified truth and points users to the closest verified route family:

- `/data/indicator`
- `/data/fund-flow`
- `/market/technical`
- `/detail/graphics/600519`
- `/detail/kline/600519`
- `/strategy/signals`

No new route, store, snapshot, selector shell, request provenance badge, freshness strip, or execution state was introduced.

## Verification
- RED: `cd web/frontend && npx vitest run src/views/advanced-analysis/__tests__/legacyStaticShells.spec.ts` failed on `6/6` before repair because the pages did not render `legacy-static-shell`.
- GREEN: `cd web/frontend && npx vitest run src/views/advanced-analysis/__tests__/legacyStaticShells.spec.ts` passed `6/6`.
- Same-family regression: `cd web/frontend && npx vitest run src/views/__tests__/AdvancedAnalysis.spec.ts src/views/advanced-analysis/__tests__/legacyStaticShells.spec.ts` passed `7/7`.
- Secondary inventory: `npm run generate:myweb-audit:secondary-inventory` passed and reduced high-priority items from `20` to `14`.

## Residual Risk
No live browser proof was added because these are unrouted secondary inventory pages with no independent routed proof surface in the current router graph.
