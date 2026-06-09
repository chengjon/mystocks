# ArtDeco Trading Center Static Market Shell Truth Audit

## Scope
- `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue`
- `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue`
- live parent shell:
  - `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`

## Defect Closed
- The live `ArtDecoTradingCenter.vue` shell still imported two market panels that did not own a semantically matching canonical market truth contract.
- `ArtDecoMarketOverview.vue` rendered a raw `Component Not Implemented` shell and `ArtDecoMarketAnalysis.vue` rendered a `STATUS: PLACEHOLDER` migration panel, which violated the secondary-phase rule that active wrappers must either delegate to canonical truth or degrade honestly.

## Repair
- Replaced `ArtDecoMarketOverview.vue` with an honest static shell that explains no canonical market-overview truth currently exists.
- Replaced `ArtDecoMarketAnalysis.vue` with an honest static shell that explains no canonical market-analysis truth currently exists.
- Both shells now avoid request IDs, freshness copy, sync banners, and summary-strip metrics.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoMarketOverview.spec.ts src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoMarketAnalysis.spec.ts` passed `2/2`
- Secondary tooling:
  - `npm run test:myweb-audit:skill` passed
  - `npm run generate:myweb-audit:secondary-inventory` passed
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- If an active embedded wrapper has no semantically matching canonical owner, do not remap it to an unrelated live route just to keep motion on screen.
- The correct repair is an honest static shell with explicit capability boundaries and no fake live semantics.
