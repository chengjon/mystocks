# Page Audit: /market/lhb

## Scope
- Route: `/market/lhb`
- Canonical entry: `web/frontend/src/views/market/LHB.vue`
- Batch: `market-batch-10`

## Defect Summary
- The canonical LHB route already exposed a local trade-date selector:
  - `今日`
  - `昨日`
  - `前日`
- But the page still kept one route-global verified leaderboard payload and one route-global verified request id.
- That meant a same-instance selector change could drift visible rows away from the active trade-date shell:
  - `/market/lhb` first verified successfully under `今日`
  - the same mounted route switched to `前日`
  - the first `前日` leaderboard request failed before any verified `前日` snapshot existed
  - the page could still inherit the old verified `今日` rows or hero request provenance under the new trade-date shell

## Repair
- Updated `LHB.vue` so verified leaderboard snapshots are stored by `currentDate` selector key instead of one route-global payload.
- Scoped hero `REQ` to the active trade-date selector's own verified request provenance.
- A same-instance `今日 -> 前日` switch with no verified `前日` snapshot now:
  - clears the old rows
  - clears the old request provenance
  - shows selector-local placeholders instead of stale leaderboard rows
- Added owner regressions and a Phase 1 routed assertion for the trade-date-switch failure path.

## Verification
- Owner regressions:
  - `npx vitest run src/views/market/__tests__/LHB.spec.ts src/views/market/__tests__/Realtime.spec.ts src/views/market/__tests__/Technical.spec.ts` passed `13/13`
  - the new owner red test first failed because `DATE: 前日` still inherited the earlier verified request provenance, then passed `1/1` after the repair
- Helper regression:
  - `node --test src/views/market/__node_tests__/dragonTigerData.test.ts` passed `4/4`
- Type check:
  - `timeout 180s npm run type-check` failed only on pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`; no new type errors were introduced by this batch
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed `45` tests including the new trade-date-switch assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - the initial controlled route rendered a verified `今日` snapshot with `贵州茅台 (600519)` visible
  - after switching the same mounted route to `前日` while the first `前日` request failed, the page reached `REQ: N/A / DATE: 前日 / ROWS: --`
  - the leaderboard then showed `0` visible `贵州茅台` rows and the route stayed in the selector-local error shell

## Skill Feedback
- This batch reused existing `myweb-audit v1.71`.
- No new version was required because selector-scoped verified-snapshot truth was already codified by the existing guidance.
