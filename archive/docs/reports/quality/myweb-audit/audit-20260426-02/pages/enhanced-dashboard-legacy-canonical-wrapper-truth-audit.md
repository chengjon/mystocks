# Enhanced Dashboard Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/EnhancedDashboard.vue`
- Synthetic route key: `/secondary/enhanced-dashboard-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The enhanced top-level dashboard still owned its own pseudo-live shell even though the router-backed canonical dashboard owner already exists at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The legacy shell exposed local stats, watchlist, market-overview, and sector-performance surfaces with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/EnhancedDashboard.vue` into a thin wrapper over the canonical dashboard owner.
- Remove the enhanced legacy page's forked pseudo-live dashboard shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/EnhancedDashboard.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `EnhancedDashboard.vue` now delegates entirely to the canonical dashboard owner.
- The page no longer fabricates local dashboard truth and now drops out of the high-priority secondary shortlist.
