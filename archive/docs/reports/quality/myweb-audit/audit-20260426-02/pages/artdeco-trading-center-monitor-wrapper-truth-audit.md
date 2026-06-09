# ArtDeco Trading Center Monitor Wrapper Truth Audit

## Scope
- `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue`
- `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue`
- canonical verification references:
  - `web/frontend/src/views/market/Realtime.vue`
  - `web/frontend/src/views/risk/Center.vue`

## Defect Closed
- The live `ArtDecoTradingCenter.vue` shell still imported wrapper panels that rendered local `STATUS: PLACEHOLDER` migration shells for `realtime-monitor` and `risk-monitor`.
- Those wrappers blocked already-existing canonical `/market/realtime` and `/risk/management` truth, violating the secondary-phase rule that active embedded wrappers should delegate to canonical verified truth whenever it already exists.

## Repair
- Replaced `ArtDecoRealtimeMonitor.vue` with a thin wrapper that directly embeds canonical `@/views/market/Realtime.vue`.
- Replaced `ArtDecoRiskMonitor.vue` with a thin wrapper that directly embeds canonical `@/views/risk/Center.vue`.
- Added owner regression coverage for both wrappers and reran the canonical market/risk smoke subset.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoRealtimeMonitor.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskMonitor.spec.ts` passed `2/2`
- Extended canonical regression:
  - `npx vitest run src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoRealtimeMonitor.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskMonitor.spec.ts src/views/market/__tests__/Realtime.spec.ts src/views/risk/__tests__/Center.spec.ts` passed `9/9`
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- Low-heuristic embedded wrappers should be promoted immediately when a live parent shell imports them and canonical truth already exists behind the wrapper.
- In that case the correct repair is pure delegation, not preserving wrapper-local migration copy.
