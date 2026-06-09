# Backtest Analysis Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/BacktestAnalysis.vue`
- Synthetic route key: `/secondary/legacy-backtest-analysis-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy backtest analysis page still owned its own pseudo-live backtest workbench shell even though the router-backed canonical strategy-backtest owner already exists at `web/frontend/src/views/strategy/Backtest.vue`.
- The legacy shell exposed local configuration controls, run-backtest CTA semantics, metrics, and placeholder chart/trade-history surfaces with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/BacktestAnalysis.vue` into a thin wrapper over the canonical `/strategy/backtest` owner.
- Remove the legacy page's forked pseudo-live backtest workbench shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/BacktestAnalysis.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `BacktestAnalysis.vue` now delegates entirely to the canonical `/strategy/backtest` owner.
- The page no longer fabricates local backtest truth and now drops out of the high-priority secondary shortlist.
