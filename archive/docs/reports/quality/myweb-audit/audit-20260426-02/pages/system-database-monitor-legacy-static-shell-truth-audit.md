# System Database Monitor Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/system/DatabaseMonitor.vue`
- Synthetic route key: `/secondary/system-database-monitor-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `DatabaseMonitor.vue` still rendered hardcoded health counters, classification totals, routing-distribution counts, and architecture simplification summaries even though no routed or otherwise active canonical database-monitor owner existed to verify that truth.
- Keeping those shell semantics in place would preserve pseudo-live system database-monitor truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/system/DatabaseMonitor.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/system/*` routes instead of preserving local health counters, routing-distribution chrome, or migration-history summaries.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/system/__tests__/DatabaseMonitor.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `DatabaseMonitor.vue` now renders an honest static shell.
- The legacy database-monitor page no longer preserves pseudo health, routing, or migration-summary truth.
