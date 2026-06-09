# System Architecture Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/system/Architecture.vue`
- Synthetic route key: `/secondary/system-architecture-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `Architecture.vue` still rendered hardcoded migration progress cards, topology counts, stack summaries, and retirement percentages even though no routed or otherwise active canonical architecture owner existed to verify that truth.
- Keeping those shell semantics in place would preserve pseudo-live system architecture truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/system/Architecture.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/system/*` routes instead of preserving local migration, topology, or stack-summary chrome.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/system/__tests__/Architecture.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `Architecture.vue` now renders an honest static shell.
- The legacy architecture page no longer preserves pseudo migration, topology, or stack-summary truth.
