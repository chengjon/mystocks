# Stocks Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/Stocks.vue`
- Synthetic route key: `/secondary/stocks-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `Stocks.vue` still rendered a local filter bar, stock list, refresh chrome, and detail-analysis actions even though no routed or otherwise active canonical stocks owner existed to verify that combined truth.
- Keeping those list-management semantics in place would preserve pseudo-live stock-list truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/Stocks.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/watchlist/*`, `/market/*`, and `/detail/*` routes instead of preserving local filter, list, refresh, or analysis chrome.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/Stocks.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`

## Outcome
- `Stocks.vue` now renders an honest static shell.
- The legacy stocks page no longer preserves pseudo filter, stock-list, refresh, or detail-analysis truth.
