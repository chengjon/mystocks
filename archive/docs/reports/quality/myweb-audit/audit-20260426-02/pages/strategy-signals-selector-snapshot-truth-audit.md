# Page Audit Report: /strategy/signals

## Batch
- Batch ID: `strategy-batch-20`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-signals-data-state-003`
- Consolidated issue: `strategy-signals-issue-03`

## Route Truth
- The page is a canonical routed workbench at `/strategy/signals`.
- The route exposes selector-scoped hero and summary truth through `FOCUS`, `REQ_ID`, `COUNT`, top-strip signal tallies, and the visible signal timeline rows.
- Before repair, those surfaces were guarded by one global verified-snapshot flag instead of the current `strategyId` query, so the same mounted page instance could switch to a new strategy and still display the earlier strategy's verified rows and request provenance.

## Trigger
1. Open `/strategy/signals?strategyId=101` with a controlled successful signal response for strategy `101`.
2. Confirm the route shows `FOCUS: 101`, `REQ_ID: req-live-strategy-signals-101`, `COUNT: 2`, and visible rows such as `贵州茅台` and `比亚迪`.
3. Switch the same routed page instance to `/strategy/signals?strategyId=202` before strategy `202` has any verified signal snapshot.
4. Resolve the new selector request as `success: false`.
5. Inspect the hero meta, content-shell `COUNT`, state panel, and visible signal rows.

## Expected
- Selector-scoped rows, counts, and request provenance must belong only to the current `strategyId`.
- If the new selector has no verified signal snapshot, the route should degrade to selector-local placeholder or unavailable truth such as `REQ_ID: N/A`, `COUNT: --`, and zero visible rows until the new selector verifies.

## Actual Before Repair
- The route treated one route-local verified-snapshot flag as proof for every strategy query.
- After switching to `strategyId=202`, `/strategy/signals` could still show the old `REQ_ID`, `COUNT`, and `101` signal rows even though strategy `202` had no verified signal snapshot of its own.

## Repair
- Added selector-keyed verified-snapshot tracking so visible rows, counts, and `REQ_ID` now derive from the current strategy query rather than from one global verified route snapshot.
- Hid prior verified rows and request provenance whenever the route switches to a selector without its own verified signal snapshot.
- Preserved existing same-selector stale-refresh retention behavior for routes that already verified the current selector.
- Added owner regression coverage in `StrategySignalsTab.spec.ts` for the same-instance `strategyId=101 -> 202` query-switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/signals` must clear old rows and request provenance after the selector switch.
- Promoted `myweb-audit` to `v1.68` for selector-scoped verified-snapshot truth on query-owned routed workbenches and details.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts`
- Strategy family regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
- Type-check:
  - `timeout 180s npm run type-check`
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list`
- Targeted live verification:
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/signals` route first renders `FOCUS: 101 / REQ_ID: req-live-strategy-signals-101 / COUNT: 2`
  - the same verification then switched to `strategyId=202` and confirmed `FOCUS: 202 / REQ_ID: N/A / COUNT: --`, zero visible rows, and `strategy 202 signals unavailable`
  - the browser proof also confirmed old `贵州茅台` and `比亚迪` rows no longer leak into the new selector shell

## Skill Feedback
- `v1.68` adds a reusable distinction between a route-local verified flag and the current selector's own verified snapshot.
- Future audits should treat same-instance query switches as a required proof path whenever a routed workbench derives hero meta, counts, or rows from selector-scoped snapshots.
