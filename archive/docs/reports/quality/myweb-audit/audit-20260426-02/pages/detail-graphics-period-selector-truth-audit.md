# Page Audit: /detail/graphics/:symbol

## Scope
- Route: `/detail/graphics/:symbol`
- Canonical entry: `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- Batch: `detail-batch-08`

## Defect Summary
- The canonical detail graphics route already treated the current route symbol as selector truth after `detail-batch-07`.
- But its primary K-line snapshot and the attached indicator workspace were still keyed only to `symbol`, while the page shell exposed a second selector dimension: `period`.
- That meant a same-instance selector change could drift the visible snapshot away from the current period:
  - `/detail/graphics/600519` verified successfully under `PERIOD: 1d`
  - switching the same page instance to `PERIOD: 1w`
  - then failing the first `1w` K-line request
  - could still leave the previous verified `1d` trend points, request provenance, and indicators visible under the new `1w` shell

## Repair
- Updated `marketKlineData.ts` so `buildMarketKlineParams()` now accepts explicit selector periods instead of hard-coding `daily`.
- Updated `KLineAnalysis.vue` so the route-owned page now tracks verified state per `symbol + period` scope key instead of symbol-only state.
- A same-instance `1d -> 1w` switch with no verified `1w` snapshot now:
  - clears the old trend snapshot
  - clears the old request provenance
  - clears the old indicator workspace
- Added owner regressions and a Phase 1 routed assertion for the period-switch first-load failure path.

## Verification
- Owner regressions:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` passed `8/8`
- Helper node test:
  - `node --test web/frontend/src/views/market/__node_tests__/marketKlineData.test.ts` passed `4/4`
- Type check:
  - `timeout 180s npm run type-check` passed
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed `42` tests including the new period-switch assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - natural PM2 reachability confirmed the same page instance remained on `/detail/graphics/600519`
  - after switching the selector from `PERIOD: 1d` to `PERIOD: 1w`, `.module-meta` updated to `PERIOD: 1w` without crashing the page
- Environment note:
  - on this machine the `/detail/graphics` request path again remained outside browser-network interception during PM2 live verification, so the controlled `1d -> 1w` failure proof was closed by owner regressions plus the new Phase 1 routed assertion rather than a browser-fulfilled failure harness

## Skill Feedback
- This batch reused existing `myweb-audit v1.71`.
- No new version was required because selector-scoped local snapshot truth was already codified by the existing selector-context guidance.
