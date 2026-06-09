# Backtest Wizard Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/BacktestWizard.vue`
- Synthetic route key: `/secondary/backtest-wizard-static-shell`
- Family: `secondary wrapper / honest static shell`

## Problem
- `BacktestWizard.vue` still rendered local strategy templates, stepper state, parameter comparisons, faux KPI cards, and a wrapper-local chart even though no routed or otherwise active canonical backtest-wizard owner existed to verify that truth.
- Keeping those wizard semantics in place would preserve pseudo-live backtest truth in a legacy page.

## Repair
- Replace `web/frontend/src/views/BacktestWizard.vue` with an honest static shell.
- Keep only handoff guidance to nearby canonical `/strategy/*` routes instead of preserving local wizard steps, template selection, comparison, or result/chart chrome.
- Retire the now-unused local pseudo-live chain in `web/frontend/src/views/composables/useBacktestWizard.ts` and `web/frontend/src/views/styles/BacktestWizard.scss`.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/BacktestWizard.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `BacktestWizard.vue` now renders an honest static shell.
- The legacy backtest wizard page no longer preserves pseudo stepper, template, comparison, KPI, or chart truth.
