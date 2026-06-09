# Stock Detail Legacy Static Shell Truth Audit

## Scope
- Page: `web/frontend/src/views/StockDetail.vue`
- Synthetic route key: `/secondary/legacy-stock-detail-static-shell`
- Family: `static-shell / no-one-to-one-canonical-owner`

## Problem
- The legacy stock-detail page still owned its own pseudo-live quote header, chart, technical analysis, trading summary, and trade-operation shell even though there is no one-to-one active canonical owner for direct delegation.
- The legacy shell exposed local stock-detail semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/StockDetail.vue` into an honest static shell.
- Remove the legacy page's forked pseudo-live stock-detail shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/StockDetail.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `web/frontend/src/views/StockDetail.vue` now renders only an honest static shell.
- The page no longer fabricates local quote, chart, technical, summary, or trading-operation truth and now drops out of the high-priority secondary shortlist.
