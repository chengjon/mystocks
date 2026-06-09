# Trading Orders And Execution Legacy Static Shell Truth Audit

## Scope
- Pages:
  - `web/frontend/src/views/trading/Orders.vue`
  - `web/frontend/src/views/trading/Execution.vue`
- Synthetic route keys:
  - `/secondary/legacy-trading-orders-static-shell`
  - `/secondary/legacy-trading-execution-static-shell`
- Family: `static-shell / no-one-to-one-canonical-owner`

## Problem
- Both nested legacy trading pages still rendered local `Coming Soon` placeholder shells even though the current router graph does not expose semantically matching canonical `/trade/orders` or `/trade/execution` owners.
- Keeping those placeholder shells would preserve duplicate, non-canonical execution/order surfaces and imply dynamic behavior that the project does not currently verify anywhere.

## Repair
- Collapse `web/frontend/src/views/trading/Orders.vue` into an honest static shell.
- Collapse `web/frontend/src/views/trading/Execution.vue` into an honest static shell.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/trading/__tests__/Orders.spec.ts src/views/trading/__tests__/Execution.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `web/frontend/src/views/trading/Orders.vue` now renders only an honest static shell.
- `web/frontend/src/views/trading/Execution.vue` now renders only an honest static shell.
- Both pages no longer imply local order-routing, execution, request, or sync truth.
