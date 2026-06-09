# Trading Decision Active Panel Canonical Wrapper Truth Audit

## Scope
- Pages:
  - `web/frontend/src/views/trading-decision/DecisionPortfolio.vue`
  - `web/frontend/src/views/trading-decision/DecisionPositions.vue`
- Synthetic route keys:
  - `/secondary/trading-decision-portfolio-canonical-wrapper`
  - `/secondary/trading-decision-positions-canonical-wrapper`
- Family: `secondary wrapper / canonical delegation`

## Problem
- `TradingDecisionCenter.vue` still fronted two active embedded panels that preserved their own pseudo-live portfolio and positions shells even though semantically matching canonical `/trade/*` owners already exist.
- Keeping those local cards, refresh actions, and empty-state shells in place would preserve duplicate non-canonical truth inside an otherwise live parent workbench.

## Repair
- Replace `web/frontend/src/views/trading-decision/DecisionPortfolio.vue` with a thin wrapper over the canonical `/trade/portfolio` owner.
- Replace `web/frontend/src/views/trading-decision/DecisionPositions.vue` with a thin wrapper over the canonical `/trade/positions` owner via the current route entrypoint.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/trading-decision/__tests__/DecisionPortfolio.spec.ts src/views/trading-decision/__tests__/DecisionPositions.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Center.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `DecisionPortfolio.vue` now delegates directly to the canonical trade-portfolio owner.
- `DecisionPositions.vue` now delegates directly to the canonical trade-positions owner.
- The active trading-decision workbench no longer preserves local pseudo-live portfolio cards, positions refresh chrome, or empty-state shells in front of canonical trade truth.
