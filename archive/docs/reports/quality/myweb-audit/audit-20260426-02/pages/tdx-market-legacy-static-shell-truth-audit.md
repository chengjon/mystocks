# TDX Market Legacy Static Shell Truth Audit

## Scope
- Page:
  - `web/frontend/src/views/TdxMarket.vue`
- Synthetic route key:
  - `/secondary/legacy-tdx-market-static-shell`
- Family: `static-shell / no-verified-canonical-owner`

## Problem
- `TdxMarket.vue` still rendered a local pseudo-live TDX quote, index-monitoring, K-line, and refresh workbench.
- The nearest same-domain sibling, `web/frontend/src/views/market/Tdx.vue`, was not a safe canonical owner because it still depended on `useTdx()` simulated transport, mock quote data, and explicit TODO APIs.
- Preserving or delegating that shell would have kept duplicate non-canonical market truth alive in the secondary backlog.

## Repair
- Collapse `web/frontend/src/views/TdxMarket.vue` into an honest static shell.
- Hand users off to nearby verified canonical routes:
  - `/market/realtime`
  - `/market/technical`
  - `/system/data`

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/TdxMarket.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `web/frontend/src/views/TdxMarket.vue` now renders only an honest static shell.
- The page no longer implies local quote, index, K-line, request, sync, or refresh truth.
- `market/Tdx.vue` remains in the backlog as an unresolved pseudo-live sibling instead of being incorrectly promoted to canonical owner.
