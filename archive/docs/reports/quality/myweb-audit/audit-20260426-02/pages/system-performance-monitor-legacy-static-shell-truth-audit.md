# System Performance Monitor Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/system/PerformanceMonitor.vue`
- Synthetic route key: `/secondary/system-performance-monitor-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `PerformanceMonitor.vue` still rendered hardcoded Core Web Vitals, performance-budget bars, trend placeholders, and suggestion summaries even though no routed or otherwise active canonical performance-monitor owner existed to verify that truth.
- Keeping those shell semantics in place would preserve pseudo-live system performance-monitor truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/system/PerformanceMonitor.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/system/*` routes instead of preserving local performance cards, budget bars, trend placeholders, or suggestion chrome.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/system/__tests__/PerformanceMonitor.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `PerformanceMonitor.vue` now renders an honest static shell.
- The legacy performance-monitor page no longer preserves pseudo Core Web Vitals, budget, trend, or suggestion truth.
