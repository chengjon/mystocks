# Technical Analysis Module Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/technical/TechnicalAnalysis.vue`
- Synthetic route key: `/secondary/legacy-technical-module-static-shell`
- Family: `static-shell / no-canonical-owner`

## Problem
- The nested legacy technical-analysis page still owned its own pseudo-live search form, indicator overview cards, chart shell, indicator table, and batch-calculation controls even though there is no active semantically matching canonical owner for direct delegation.
- The legacy shell exposed local technical-analysis semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/technical/TechnicalAnalysis.vue` into an honest static shell.
- Remove the legacy page's forked pseudo-live technical-analysis shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/technical/__tests__/TechnicalAnalysis.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `web/frontend/src/views/technical/TechnicalAnalysis.vue` now renders only an honest static shell.
- The page no longer fabricates local technical-analysis, indicator, signal, chart, or batch-calculation truth and now drops out of the high-priority secondary shortlist.
