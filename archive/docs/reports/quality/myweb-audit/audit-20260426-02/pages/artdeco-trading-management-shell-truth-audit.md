# ArtDeco Trading Management Shell Truth Audit

## Scope
- `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`
- direct canonical dependency: `web/frontend/src/views/trade/Portfolio.vue`

## Defect Closed
- The secondary embedded shell still rendered fake live runtime surfaces such as shell-level `REQ_ID`, `SYNC`, `市场状态`, `今日盈亏`, and hardcoded signal counts even though it did not own any verified snapshot contract.
- The same owner also rendered local fake trading panels instead of reusing canonical `/trade/*` pages, which violated the secondary-phase rule that all live truth must come from existing canonical owners or degrade to a static shell.

## Repair
- Rewrote `ArtDecoTradingManagement.vue` into a pure orchestration shell:
  - shell header now shows only static focus/source copy
  - shell no longer exposes live provenance, freshness, market status, or P&L chrome
  - supported tabs embed canonical `/trade/*` pages directly
  - unsupported `绩效归因` falls back to a static explanatory shell instead of fake live data
- Added an embedded mode to `web/frontend/src/views/trade/Portfolio.vue` so canonical portfolio truth can be reused inside an outer shell without duplicating its own route-level hero and stats strip.
- Added owner regression coverage for shell demotion and canonical embedded reuse.

## Verification Evidence
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts src/views/trade/__tests__/Portfolio.spec.ts` passed
- Extended canonical trade regression:
  - `npx vitest run src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/History.spec.ts` passed `20/20`
- Type-check:
  - `timeout 180s npm run type-check` still failed only on existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
- Runtime services:
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online

## Rule Feedback
- Secondary embedded shells without their own verified live-truth contract should be repaired by orchestration demotion, not by adding shell-local snapshots or shared stores.
- Canonical page reuse is acceptable only when the embedded owner inherits the exact verified truth of the canonical page and removes duplicate route-level hero/stats chrome.
