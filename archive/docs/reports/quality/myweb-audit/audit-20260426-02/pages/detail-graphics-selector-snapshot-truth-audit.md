# Page Audit: /detail/graphics/:symbol

## Scope
- Route: `/detail/graphics/:symbol`
- Canonical entry: `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- Batch: `detail-batch-07`

## Defect Summary
- The canonical detail graphics route already showed the current route symbol in the module header.
- But its primary K-line snapshot and indicator enrichment slices were not keyed to the current detail symbol.
- That meant a routed selector change could drift the visible snapshot away from the current symbol:
  - `/detail/graphics/600519` verified successfully
  - switching the same routed page instance to `/detail/graphics/000001`
  - then failing the new `000001` K-line or indicator slice could still leave the old `600519` snapshot visible under the new symbol header

## Repair
- Updated `KLineAnalysis.vue` so the route-owned page now tracks:
  - `lastRequestedStandaloneSymbol`
  - `lastVerifiedKlineSymbol`
  - `lastVerifiedIndicatorSymbol`
- The detail graphics route now applies selector-scoped truth:
  - new symbol with no verified K-line snapshot: clear the old trend snapshot and request provenance
  - new symbol with verified K-line but failed enrichment slice: keep only the new symbol trend snapshot and clear the previous symbol indicators
- Added owner regressions and Phase 1 routed assertions for:
  - selector-switch first-load K-line failure
  - selector-switch enrichment failure

## Verification
- Owner regressions:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` passed `7/7`
- Type check:
  - `timeout 180s npm run type-check` passed
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed `41` tests including the two new selector-switch assertions
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - natural PM2 route-switch verification confirmed the same page instance moved from `/detail/graphics/600519` to `/detail/graphics/000001`
  - after the route switch, `.module-meta` showed `SYMBOL: 000001` with a new request id instead of retaining the old `600519` header
  - the same route-switch proof confirmed `.indicators-card` stayed in current-symbol unavailable state and did not render the previous symbol indicators
- Environment note:
  - on this machine the `/detail/graphics` request path remained outside browser-network interception during PM2 live verification, so controlled failure proof was closed by owner regressions plus the new Phase 1 routed assertions rather than a browser-fulfilled failure harness

## Skill Feedback
- This batch reused existing `myweb-audit v1.66`.
- No new version was required because selector-scoped snapshot provenance was already codified by the existing watchlist/detail selector guidance.
