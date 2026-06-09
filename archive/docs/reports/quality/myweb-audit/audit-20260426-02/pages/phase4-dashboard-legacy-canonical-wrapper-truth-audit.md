# Phase4 Dashboard Legacy Canonical Wrapper Truth Audit

## Scope
- Page:
  - `web/frontend/src/views/Phase4Dashboard.vue`
- Synthetic route key:
  - `/secondary/legacy-phase4-dashboard-wrapper`
- Family: `canonical-wrapper / dashboard-shell`

## Problem
- `Phase4Dashboard.vue` still rendered a local pseudo-live dashboard shell with its own stats cards, market overview tabs, watchlist panel, and risk-alert table.
- A semantically matching canonical dashboard owner already existed at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- Keeping the phase-4 shell would preserve another forked dashboard truth source in the secondary backlog.

## Repair
- Collapse `web/frontend/src/views/Phase4Dashboard.vue` into a thin wrapper over the canonical dashboard owner.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/Phase4Dashboard.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `web/frontend/src/views/Phase4Dashboard.vue` now renders only the canonical dashboard owner.
- The page no longer implies local dashboard stats, watchlist, market overview, or alert truth.
