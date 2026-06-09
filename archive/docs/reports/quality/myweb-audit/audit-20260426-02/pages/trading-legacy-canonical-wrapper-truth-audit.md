# Trading Legacy Canonical Wrapper Truth Audit

## Scope
- Pages:
  - `web/frontend/src/views/trading/History.vue`
  - `web/frontend/src/views/trading/Positions.vue`
- Synthetic route keys:
  - `/secondary/legacy-trading-history-wrapper`
  - `/secondary/legacy-trading-positions-wrapper`
- Family: `secondary wrapper / canonical delegation`

## Problem
- Both nested legacy trading pages still rendered local `Coming Soon` placeholder shells even though semantically matching canonical trade owners already exist in the current router graph.
- Keeping the placeholder shells in place would preserve duplicate, non-canonical UI surfaces and block the canonical `/trade/*` truth from becoming the only active representation.

## Repair
- Replace `web/frontend/src/views/trading/History.vue` with a thin wrapper over the canonical `/trade/history` owner.
- Replace `web/frontend/src/views/trading/Positions.vue` with a thin wrapper over the canonical `/trade/positions` owner.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/trading/__tests__/History.spec.ts src/views/trading/__tests__/Positions.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `web/frontend/src/views/trading/History.vue` now delegates directly to the canonical trade-history owner.
- `web/frontend/src/views/trading/Positions.vue` now delegates directly to the canonical trade-positions owner.
- The nested legacy trading pages no longer render standalone `Coming Soon` shells.
