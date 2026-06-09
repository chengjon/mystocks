# Market Fund Flow And Concepts Legacy Canonical Wrapper Truth Audit

## Scope
- Pages:
  - `web/frontend/src/views/market/CapitalFlow.vue`
  - `web/frontend/src/views/market/Concepts.vue`
- Synthetic route keys:
  - `/secondary/market-capital-flow-canonical-wrapper`
  - `/secondary/market-concepts-canonical-wrapper`
- Family: `secondary wrapper / canonical delegation`

## Problem
- `market/CapitalFlow.vue` still fronted local market overview cards, refresh-all chrome, and movers tables even though the verified fund-flow truth already lives in the canonical `/data/fund-flow` owner.
- `market/Concepts.vue` still fronted local concept stats, refresh controls, hot-ranking shells, and concept-detail chrome even though the verified concept truth already lives in the canonical `/data/concept` owner.

## Repair
- Replace `web/frontend/src/views/market/CapitalFlow.vue` with a thin wrapper over the canonical `/data/fund-flow` owner.
- Replace `web/frontend/src/views/market/Concepts.vue` with a thin wrapper over the canonical `/data/concept` owner.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/market/__tests__/CapitalFlow.spec.ts src/views/market/__tests__/Concepts.spec.ts src/views/data/__tests__/FundFlow.spec.ts src/views/data/__tests__/Concepts.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `market/CapitalFlow.vue` now delegates directly to the canonical fund-flow owner.
- `market/Concepts.vue` now delegates directly to the canonical concepts owner.
- The legacy market-domain pages no longer preserve duplicate overview cards, refresh buttons, ranking shells, or detail truth in front of canonical `/data/*` owners.
