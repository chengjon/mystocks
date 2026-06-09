# Portfolio Management Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/PortfolioManagement.vue`
- Synthetic route key: `/secondary/portfolio-management-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `PortfolioManagement.vue` still rendered local score cards, watchlist tabs, alert summaries, stock-edit actions, and radar/detail dialogs even though no routed or otherwise active canonical portfolio-management owner existed to verify that combined truth.
- Keeping those management semantics in place would preserve pseudo-live portfolio and risk truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/PortfolioManagement.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/watchlist/*`, `/trade/*`, and `/risk/*` routes instead of preserving local watchlist, analysis, alert, or stock-edit chrome.
- Retire the now-unused local pseudo-live chain in `web/frontend/src/views/composables/usePortfolioManagement.ts` and `web/frontend/src/views/styles/PortfolioManagement.scss`.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/PortfolioManagement.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `PortfolioManagement.vue` now renders an honest static shell.
- The legacy portfolio-management page no longer preserves pseudo score cards, watchlist tabs, alert summaries, stock-edit actions, or radar/detail truth.
