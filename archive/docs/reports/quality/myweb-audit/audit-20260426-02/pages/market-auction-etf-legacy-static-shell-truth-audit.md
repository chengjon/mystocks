# Market Auction And ETF Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/market/Auction.vue`
- Page: `web/frontend/src/views/market/Etf.vue`
- Synthetic route key: `/secondary/market-auction-static-shell`
- Synthetic route key: `/secondary/market-etf-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `Auction.vue` still rendered hardcoded auction volume, participating-stock count, success rate, refresh simulation, status tags, and sample rows even though no semantically matching routed canonical auction owner exists.
- `Etf.vue` still rendered local ETF asset totals, product counts, volume metrics, category selectors, auto-refresh controls, top rankings, and hardcoded ETF sample rows even though no semantically matching verified canonical ETF owner exists.
- Nearby ETF or auction sibling modules are embedded/legacy surfaces, not independent route truth for these two legacy `views/market/*` pages.

## Repair
- Replace `Auction.vue` with an honest static shell that removes local auction metrics, refresh actions, delayed success messages, and sample rows.
- Replace `Etf.vue` with an honest static shell that removes local ETF metrics, category selectors, refresh controls, rankings, and hardcoded ETF rows.
- Point both shells back to verified market/data routes instead of creating a new secondary snapshot or store.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/market/__tests__/Auction.spec.ts src/views/market/__tests__/Etf.spec.ts`
- Same-domain regression:
  - `cd web/frontend && npx vitest run src/views/market/__tests__/*.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `Auction.vue` and `Etf.vue` now render honest static shells.
- The secondary inventory high-priority shortlist dropped from `24` to `22`.
- The legacy market auction and ETF pages no longer preserve pseudo-live auction, ETF, selector, ranking, refresh, or sample-row truth.
