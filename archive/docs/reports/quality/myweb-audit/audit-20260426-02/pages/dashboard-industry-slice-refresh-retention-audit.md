# Dashboard Industry Slice Refresh Retention Audit

## Route
- `/dashboard`
- canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- primary state owner: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`

## Defect Summary
Before repair, the dashboard could successfully render a verified industry slice and then lose that same visible truth on a later refresh failure. The route-level industry catch path cleared market breadth and sector surfaces back to fallback truth even though the current dashboard shell should have stayed on the last verified industry snapshot.

This produced one route-level truth defect:
- the later industry refresh failure cleared verified `涨跌家数`, heat-map, and sector-radar surfaces
- the aggregate shell needed to degrade to explicit `MIXED / DEGRADED` truth while preserving the verified slice, not collapse the slice or leave optimistic route meta behind

## Root Cause
The route-local industry branch inside `useArtDecoDashboard.ts` treated every failure the same way:

1. it reset `marketHeat` to `[]`
2. it reset `marketData.stocks` to `0↑/0↓`
3. it only surfaced a generic route-level error without distinguishing first-load failure from later retained-slice failure

Because the composable did not track a verified industry snapshot boundary, later refresh failures used the same fallback path as unresolved first-load failures.

## Repair
- `useArtDecoDashboard.ts` now tracks whether the dashboard has already synchronized a verified industry slice.
- A later industry refresh failure now preserves the last verified market breadth, heat-map, and sector-radar surfaces.
- The same later failure now degrades the aggregate shell to `DATA: MIXED`, `SYNC: DEGRADED`, and `行业热度数据暂不可用` instead of leaving the route all-green.
- Dashboard owner and routed phase-matrix regressions now lock the `success -> later industry refresh fail` path.

## Verification
- unit regression:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "keeps the last verified industry slice visible when a later industry refresh fails"` -> first reproduced the red `0↑/0↓` failure, then passed `1/1`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `15/15`
- structural routed E2E parse:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `32` tests including the retained-industry-slice route assertion
- type-check:
  - `timeout 180s npm run type-check` -> passed
- targeted live verification via Playwright-library + system `google-chrome` with browser-context interception and `serviceWorkers: block`:
  - later industry refresh failure settled to `DATA: MIXED`, `REQ: live-dashboard-fund-flow`, `TIME: 22ms`, `SYNC: DEGRADED`
  - route-level alerts rendered `行业热度数据暂不可用`
  - the visible market-status card still rendered `涨跌家数 2↑/0↓`
  - `.heat-map-card .chart-state-note` stayed absent
  - `.sector-radar-card .chart-state-note` stayed absent
