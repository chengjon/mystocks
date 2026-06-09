# Industry Concept Analysis Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/IndustryConceptAnalysis.vue`
- Synthetic route key: `/secondary/industry-concept-analysis-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `IndustryConceptAnalysis.vue` still rendered local tabs, selector filters, summary cards, charts, stock tables, and export actions even though no routed or otherwise active canonical industry-concept owner existed to verify that combined truth.
- Keeping those analysis semantics in place would preserve pseudo-live industry-concept truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/IndustryConceptAnalysis.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/data/*` routes instead of preserving local analysis, chart, or export chrome.
- Retire the now-unused local pseudo-live chain in `web/frontend/src/views/composables/useIndustryConceptAnalysis.ts` and `web/frontend/src/views/styles/IndustryConceptAnalysis.scss`.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/IndustryConceptAnalysis.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`

## Outcome
- `IndustryConceptAnalysis.vue` now renders an honest static shell.
- The legacy industry-concept analysis page no longer preserves pseudo tabs, filters, cards, charts, stock-table, or export truth.
