# Trade Management Legacy Orchestration Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/TradeManagement.vue`
- Synthetic route key: `/secondary/legacy-trade-management-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy trade-management page still owned its own pseudo-live header, portfolio overview, positions, trade-history, and statistics shell even though the active trading orchestration shell already exists at `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`.
- The legacy shell exposed local trading-workbench semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/TradeManagement.vue` into a thin wrapper over the active trading orchestration shell.
- Remove the legacy page's forked pseudo-live trade-management shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/TradeManagement.spec.ts src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `TradeManagement.vue` now delegates entirely to the active trading orchestration shell.
- The page no longer fabricates local trading-workbench, positions, trade-history, or statistics truth and now drops out of the high-priority secondary shortlist.
