# Market Legacy Portfolio Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/Market.vue`
- Synthetic route key: `/secondary/legacy-market-portfolio-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy market page still owned its own pseudo-live asset summary cards, positions/history tabs, and refresh shell even though the router-backed canonical trade-portfolio owner already exists at `web/frontend/src/views/trade/Portfolio.vue`.
- The legacy shell exposed local asset counts and faux refresh semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/Market.vue` into a thin wrapper over the canonical `/trade/portfolio` owner.
- Remove the legacy page's forked pseudo-live asset and trade-history shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/Market.spec.ts src/views/trade/__tests__/Portfolio.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `Market.vue` now delegates entirely to the canonical `/trade/portfolio` owner.
- The page no longer fabricates local asset, position, or trade-history truth and now drops out of the high-priority secondary shortlist.
