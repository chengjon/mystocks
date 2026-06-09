# Market Data Legacy Aggregate Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/MarketData.vue`
- Page: `web/frontend/src/views/market/MarketDataView.vue`
- Synthetic route key: `/secondary/market-data-static-shell`
- Synthetic route key: `/secondary/market-data-view-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `MarketData.vue` still rendered a local market-data aggregate shell with fund-flow, ETF, chip-race, and LHB tabs backed by legacy components.
- `market/MarketDataView.vue` still rendered similar aggregate semantics plus local runtime chrome such as a realtime badge, clock, and back action.
- The aggregate semantics span multiple canonical route families and have no one-to-one verified owner, so keeping the pages dynamic would preserve a second market-data truth surface.

## Repair
- Replace `MarketData.vue` with an honest static shell that points users to verified `/market/*` and `/data/*` routes.
- Replace `market/MarketDataView.vue` with an honest static shell that removes local runtime chrome, Tab state, and legacy market component mounting.
- Do not create an aggregate snapshot, store, freshness badge, request provenance badge, or wrapper-local selector truth.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/MarketData.spec.ts src/views/market/__tests__/MarketDataView.spec.ts`
- Same-domain regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/MarketData.spec.ts src/views/market/__tests__/*.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`

## Outcome
- Both legacy aggregate market-data pages now render honest static shells.
- The secondary inventory high-priority shortlist dropped from `22` to `20`.
- The pages no longer mount legacy market widgets or expose duplicate aggregate market-data truth.
