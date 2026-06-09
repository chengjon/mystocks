# Strategy Management Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/StrategyManagement.vue`
- Synthetic route key: `/secondary/legacy-strategy-management-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy strategy management page still owned its own pseudo-live strategy workbench shell even though the router-backed canonical strategy-repo owner already exists at `web/frontend/src/views/strategy/List.vue`.
- The legacy shell exposed local workbench copy, create CTA semantics, and empty-state messaging with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/StrategyManagement.vue` into a thin wrapper over the canonical `/strategy/repo` owner.
- Remove the legacy page's forked pseudo-live strategy workbench shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/StrategyManagement.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `StrategyManagement.vue` now delegates entirely to the canonical `/strategy/repo` owner.
- The page no longer fabricates local strategy-management truth and now drops out of the high-priority secondary shortlist.
