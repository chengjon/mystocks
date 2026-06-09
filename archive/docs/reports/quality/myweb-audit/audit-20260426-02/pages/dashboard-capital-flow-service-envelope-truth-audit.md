# Dashboard Capital-Flow Service Envelope Truth Audit

## Route
- `/dashboard`
- canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- primary state owner: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- upstream service boundary: `web/frontend/src/api/services/dashboardService.ts`

## Defect Summary
Before repair, the dashboard already had a route-local later-failure retention branch for the capital-flow ranking slice, but the real route still collapsed that slice to empty-success truth on a later `big-deal` refresh failure. The visible ranking list disappeared, the heatmap stale note never rendered, and the route looked as if the slice had simply returned zero rows.

This produced one route-level truth defect:
- the later `big-deal` refresh failure reached `/dashboard` as `data: []` instead of failure truth
- the route therefore cleared the verified capital-flow ranking slice before route-local stale-state UX could run
- the operator could see aggregate `DATA: MIXED / SYNC: DEGRADED` from the fund-flow family, but the ranking slice itself still looked like a genuine empty success

## Root Cause
The root cause was one layer above the page owner:

1. `apiClient` resolves HTTP 500s into UnifiedResponse-style `success:false` envelopes instead of throwing
2. `dashboardService.getStockFlowRanking()` did not call `isErrorEnvelope()`
3. the service normalized the failed payload with `normalizeDashboardStockFlowRanking(response)` and returned `data: []`
4. `fetchStockFlowRanking()` therefore received a success-looking empty array instead of a thrown failure and could not enter the later-refresh stale-slice branch

The page-local retention logic was present but starved of failure truth because the service layer erased the envelope first.

## Repair
- `dashboardService.getStockFlowRanking()` now gates resolved `success:false` envelopes with `isErrorEnvelope()` and throws `stock flow ranking unavailable` before normalization.
- `useArtDecoDashboard.ts` now tracks a verified capital-flow snapshot boundary and same-tab stale-state semantics.
- `ArtDecoDashboard.vue` now surfaces explicit stale ranking copy in both the ranking card and capital-flow heatmap card.
- Service, owner, and routed regressions now lock the `success -> later big-deal refresh fail` path.

## Verification
- service regression:
  - `npx vitest run src/api/services/__tests__/dashboardService.spec.ts -t "throws when the API client resolves a unified error envelope"` -> first reproduced the red empty-success bug, then passed `1/1`
  - `npx vitest run src/api/services/__tests__/dashboardService.spec.ts` -> passed `5/5`
- owner and routed-owner regressions:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `17/17`
- structural routed E2E parse:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `33` tests including the new retained-capital-flow-slice assertion
- type-check:
  - `timeout 180s npm run type-check` -> passed
- targeted live verification via Playwright-library + system `google-chrome` with browser-context interception and `serviceWorkers: block`:
  - first verified state rendered `贵州茅台 / 宁德时代`
  - later `big-deal` refresh failure rendered `资金流向持续排名暂不可用，当前仍显示上次成功同步的排名快照。`
  - the ranking card still kept `贵州茅台 / 宁德时代`
  - `.capital-heatmap-card .chart-state-note` rendered the same stale ranking message
  - aggregate shell simultaneously rendered `DATA: MIXED`, `SYNC: DEGRADED`, and route alert `资金流向数据暂不可用`
