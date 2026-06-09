# Page Audit Report: /strategy/opt

## Batch
- Batch ID: `strategy-batch-22`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-opt-data-state-003`
- Consolidated issue: `strategy-opt-issue-03`

## Route Truth
- The page is a canonical routed optimization workbench at `/strategy/opt`.
- The route exposes selector-scoped truth through `FOCUS`, hero `REQ_ID / PROCESS`, `VISIBLE / TOTAL`, top-strip summary tallies, and the visible optimization candidate rows.
- Before repair, those surfaces were guarded by one global verified-snapshot flag instead of the current `strategyId` query, so the same mounted page instance could switch to a new strategy and still present the earlier strategy's verified optimization snapshot.

## Trigger
1. Open `/strategy/opt?strategyId=101` with a controlled successful strategies payload for strategy `101`.
2. Confirm the route shows `FOCUS: ID 101`, `REQ_ID: req-live-strategy-opt-success`, `PROCESS: 42.00`, and one visible `Momentum Alpha` optimization row.
3. Switch the same routed page instance to `/strategy/opt?strategyId=202` before strategy `202` has any verified optimization snapshot.
4. Inspect the hero meta, summary tallies, and visible optimization table.

## Expected
- Selector-scoped optimization rows, summary tallies, and request provenance must belong only to the current `strategyId`.
- If the new selector has no verified optimization snapshot, the route should degrade to `REQ_ID: N/A`, `PROCESS: N/A`, `VISIBLE: -- / TOTAL: --`, `-- / -- / -- / ID 202`, and zero visible rows until the new selector verifies.

## Actual Before Repair
- The route treated one route-local verified-snapshot flag as proof for every strategy query.
- After switching to `strategyId=202`, `/strategy/opt` could still show the old `REQ_ID / PROCESS`, `VISIBLE / TOTAL`, and verified optimization row even though strategy `202` had no verified optimization snapshot of its own.

## Repair
- Added selector-keyed verified strategy tracking so hero `REQ_ID / PROCESS`, `VISIBLE / TOTAL`, top-strip tallies, and visible rows now derive from the current `strategyId` query rather than from one global verified route snapshot.
- Hid prior verified provenance whenever the route switches to a selector without its own verified optimization snapshot.
- Preserved existing same-selector stale-refresh retention behavior for selectors that already verified in the current payload.
- Added owner regression coverage in `ArtDecoStrategyOptimization.spec.ts` for the same-instance `strategyId=101 -> 202` query-switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/opt` must clear old provenance and visible rows after the selector switch.
- Reused existing `myweb-audit v1.68` selector-scoped verified-snapshot truth instead of promoting a new rule version.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
- Strategy family regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/watchlist/__tests__/Signals.spec.ts`
- Type-check:
  - `timeout 180s npm run type-check`
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list`
- Targeted live verification:
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/opt` route first renders `FOCUS: ID 101 / REQ_ID: req-live-strategy-opt-success / PROCESS: 42.00`
  - the same verification then switched to `strategyId=202` and confirmed `FOCUS: ID 202 / REQ_ID: N/A / PROCESS: N/A / -- / -- / -- / ID 202`
  - the browser proof also confirmed zero visible optimization rows and no leaked `Momentum Alpha` text after the selector switch

## Skill Feedback
- Existing `v1.68` already covered this failure mode: query-owned workbenches cannot rely on one route-local verified flag when hero meta, summary tallies, and visible rows are selector-scoped.
- Future audits should treat same-instance query switches as required proof paths whenever optimization, parameter, or signal workbenches derive visible truth from selector-owned snapshots.
