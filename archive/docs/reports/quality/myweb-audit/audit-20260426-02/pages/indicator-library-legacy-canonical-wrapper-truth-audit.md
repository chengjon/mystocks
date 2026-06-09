# Indicator Library Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/IndicatorLibrary.vue`
- Synthetic route key: `/secondary/legacy-indicator-library-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy indicator-library page still owned its own pseudo-live registry totals, filter shell, and indicator cards even though the router-backed canonical data-indicator owner already exists at `web/frontend/src/views/data/Advanced.vue`.
- The legacy shell exposed local registry counts and faux filter semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/IndicatorLibrary.vue` into a thin wrapper over the canonical `/data/indicator` owner.
- Remove the legacy page's forked pseudo-live indicator-library shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/IndicatorLibrary.spec.ts src/views/data/__tests__/Advanced.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `IndicatorLibrary.vue` now delegates entirely to the canonical `/data/indicator` owner.
- The page no longer fabricates local indicator registry, filtering, or card truth and now drops out of the high-priority secondary shortlist.
