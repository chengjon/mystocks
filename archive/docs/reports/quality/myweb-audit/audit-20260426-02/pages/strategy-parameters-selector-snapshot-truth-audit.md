# Page Audit Report: /strategy/parameters

## Batch
- Batch ID: `strategy-batch-21`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-parameters-data-state-003`
- Consolidated issue: `strategy-parameters-issue-03`

## Route Truth
- The page is a canonical routed workbench at `/strategy/parameters`.
- The route exposes selector-scoped hero and summary truth through `FOCUS`, `REQ_ID`, `PROCESS`, the top-strip parameter tallies, and the visible parameter cards.
- Before repair, those surfaces were guarded by one global verified-snapshot flag instead of the current `strategyId` query, so the same mounted page instance could switch to a new strategy and still present the earlier strategy's verified provenance.

## Trigger
1. Open `/strategy/parameters?strategyId=101` with a controlled successful strategies payload for strategy `101`.
2. Confirm the route shows `FOCUS: 101`, `REQ_ID: req-live-strategy-parameters-success`, `PROCESS: 36.00 ms`, and one visible `Momentum Alpha` card.
3. Switch the same routed page instance to `/strategy/parameters?strategyId=202` before strategy `202` has any verified parameter snapshot.
4. Inspect the hero meta, top-strip counts, and visible parameter cards.

## Expected
- Selector-scoped parameter rows, summary tallies, and request provenance must belong only to the current `strategyId`.
- If the new selector has no verified parameter snapshot, the route should degrade to `REQ_ID: N/A`, `PROCESS: N/A ms`, `-- / -- / -- / 202`, and zero visible cards until the new selector verifies.

## Actual Before Repair
- The route treated one route-local verified-snapshot flag as proof for every strategy query.
- After switching to `strategyId=202`, `/strategy/parameters` could still show the old `REQ_ID / PROCESS` and verified summary truth even though strategy `202` had no verified parameter snapshot of its own.

## Repair
- Added selector-keyed verified strategy tracking so hero `REQ_ID / PROCESS`, top-strip tallies, and visible cards now derive from the current `strategyId` query rather than from one global verified route snapshot.
- Hid prior verified provenance whenever the route switches to a selector without its own verified parameter snapshot.
- Preserved existing same-selector stale-refresh retention behavior for selectors that already verified in the current payload.
- Added owner regression coverage in `StrategyParametersTab.spec.ts` for the same-instance `strategyId=101 -> 202` query-switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/parameters` must clear old provenance and visible cards after the selector switch.
- Reused existing `myweb-audit v1.68` selector-scoped verified-snapshot truth instead of promoting a new rule version.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts`
- Strategy family regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
- Type-check:
  - `timeout 180s npm run type-check`
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list`
- Targeted live verification:
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/parameters` route first renders `FOCUS: 101 / REQ_ID: req-live-strategy-parameters-success / PROCESS: 36.00 ms`
  - the same verification then switched to `strategyId=202` and confirmed `FOCUS: 202 / REQ_ID: N/A / PROCESS: N/A ms / -- / -- / -- / 202`
  - the browser proof also confirmed zero visible parameter cards and no leaked `Momentum Alpha` text after the selector switch

## Skill Feedback
- Existing `v1.68` already covered this failure mode: query-owned workbenches cannot rely on one route-local verified flag when hero meta and visible surfaces are selector-scoped.
- Future audits should treat same-instance query switches as required proof paths whenever parameter, signal, or detail workbenches derive hero provenance and summary truth from selector-owned snapshots.
