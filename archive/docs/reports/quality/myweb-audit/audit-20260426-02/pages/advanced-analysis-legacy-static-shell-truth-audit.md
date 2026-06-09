# Advanced Analysis Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/AdvancedAnalysis.vue`
- Synthetic route key: `/secondary/advanced-analysis-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `AdvancedAnalysis.vue` still rendered a local analysis form, batch-run controls, Kronos prediction area, system health cards, and result panels even though no routed or otherwise active canonical advanced-analysis owner existed to verify that combined truth.
- Keeping those analysis semantics in place would preserve pseudo-live advanced-analysis truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/AdvancedAnalysis.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/data/*`, `/detail/*`, and `/strategy/*` routes instead of preserving local analysis, prediction, or health chrome.
- Retire the now-unused local pseudo-live chain in `web/frontend/src/views/composables/useAdvancedAnalysis.ts`.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/AdvancedAnalysis.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`

## Outcome
- `AdvancedAnalysis.vue` now renders an honest static shell.
- The legacy advanced-analysis page no longer preserves pseudo analysis configuration, batch-run, Kronos prediction, health, or result truth.
