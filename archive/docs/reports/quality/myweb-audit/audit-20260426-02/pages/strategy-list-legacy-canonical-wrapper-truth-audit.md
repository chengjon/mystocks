# Strategy List Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/strategy/StrategyList.vue`
- Synthetic route key: `/secondary/legacy-strategy-list-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The nested legacy strategy-list page still owned its own pseudo-live strategy-definition grid, refresh button, filter bar, and action shell even though the canonical strategy-repo owner already exists at `web/frontend/src/views/strategy/List.vue`.
- The legacy shell exposed local strategy-definition semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/strategy/StrategyList.vue` into a thin wrapper over the canonical strategy-repo owner.
- Remove the legacy page's forked pseudo-live strategy-definition shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/strategy/__tests__/StrategyList.spec.ts src/views/__tests__/StrategyManagement.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `StrategyList.vue` now delegates entirely to the canonical strategy-repo owner.
- The page no longer fabricates local strategy-definition, refresh, filter, or action truth and now drops out of the high-priority secondary shortlist.
