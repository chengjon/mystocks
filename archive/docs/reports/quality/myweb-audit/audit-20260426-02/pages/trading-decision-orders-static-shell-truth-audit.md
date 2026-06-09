# Trading Decision Orders Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/trading-decision/DecisionOrders.vue`
- Synthetic route key: `/secondary/trading-decision-orders-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `TradingDecisionCenter.vue` still fronted a local order-entry panel with pseudo-live search, submit, refresh, and order-history semantics even though the current router exposes no semantically matching canonical `/trade/orders` or `/trade/execution` owner.
- Keeping those controls in place would preserve a fake trading-execution surface in front of live trade routes that own different semantics.

## Repair
- Replace `web/frontend/src/views/trading-decision/DecisionOrders.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical trade routes instead of preserving local search, submit, refresh, or order-history chrome.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/trading-decision/__tests__/DecisionOrders.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `DecisionOrders.vue` now renders an honest static shell.
- The active trading-decision workbench no longer preserves pseudo-live order-entry semantics where no matching canonical owner exists.
