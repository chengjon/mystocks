# ArtDeco Trading Center Wrapper Canonical Truth Audit

## Scope
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue`
- direct canonical dependency with new regression coverage: `web/frontend/src/views/trade/History.vue`

## Defect Closed
- The live `ArtDecoTradingCenter.vue` shell still imported wrapper panels that rendered local `STATUS: PLACEHOLDER` migration cards for `trade-history` and `trade-portfolio`.
- Those placeholder shells blocked already-existing canonical `/trade/history` and `/trade/portfolio` truth, violating the secondary-phase rule that active embedded wrappers must either reuse canonical verified truth or downgrade honestly when no such truth exists.

## Repair
- Replaced `ArtDecoHistoryView.vue` with a thin wrapper that directly embeds canonical `@/views/trade/History.vue` in embedded mode.
- Replaced `ArtDecoPerformanceAnalysis.vue` with a thin wrapper that directly embeds canonical `@/views/trade/Portfolio.vue`.
- Added owner regression coverage for both wrappers and explicit canonical embedded coverage for `History.vue`.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts src/views/trade/__tests__/History.spec.ts` passed `7/7`
- Extended canonical trade regression:
  - `npx vitest run src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Center.spec.ts` passed `22/22`
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- Low-heuristic embedded wrappers can still be high-priority repairs when they sit behind a live import chain and mask already-existing canonical truth with placeholder migration copy.
- Once a canonical owner already exposes verified truth, active wrapper panels should become pure embedded orchestration rather than maintain local placeholder shells.
