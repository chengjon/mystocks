# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-19`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-007`
- Consolidated issue: `strategy-backtest-issue-07`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The route exposes selector-local action feedback through state-banner copy and the execution-action hint, including generated snapshot text such as `最近快照：Momentum Alpha`.
- Before repair, that generated snapshot surface was stored as route-local memory rather than strategy-query-owned truth, so the same routed page instance could switch to a new `strategyId` and still display the previous strategy's local generated snapshot copy.

## Trigger
1. Open `/strategy/backtest?strategyId=101` with a controlled successful strategy-list load and a local snapshot available for strategy `101`.
2. Click `生成上下文快照` and confirm the page shows `最近快照：Momentum Alpha`.
3. Switch the same routed page instance to `/strategy/backtest?strategyId=202` before any verified generated snapshot exists for strategy `202`.
4. Inspect the visible state banner, context strip, and execution-action hint.

## Expected
- Selector- or query-scoped local action feedback must belong to the current strategy only.
- If the new `strategyId` has no verified local generated snapshot, the route should degrade to neutral selector-local baseline copy and may pair that baseline with explicit context-switched messaging.

## Actual Before Repair
- The route kept the previous `Momentum Alpha` generated snapshot hint visible after the same page instance switched to `strategyId=202`, even though strategy `202` had no verified local snapshot of its own.

## Repair
- Added a route-local `activeGeneratedSnapshot` guard so generated snapshot copy is only visible when `lastGeneratedSnapshot.strategyId === selectedStrategyId`.
- Restored neutral selector-local baseline copy when a new strategy query has no verified generated snapshot.
- Added owner regression coverage in `ArtDecoBacktestAnalysis.spec.ts` for the same-instance `101 -> 202` route-query switch path.
- Strengthened routed Phase 3 matrix coverage in `phase3-mainline-matrix.spec.ts` so `/strategy/backtest` must clear the old generated snapshot hint after the query switch.
- Promoted `myweb-audit` to `v1.67` for selector-local action truth on query-scoped routed workbenches and details.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts`
- Strategy family regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts`
- Type-check:
  - `timeout 180s npm run type-check`
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list`
- Targeted live verification:
  - controlled authenticated system-`google-chrome` verification confirmed the same routed page instance reaches `当前策略上下文ID 202` with neutral baseline copy and no leaked `最近快照：Momentum Alpha`
  - the owner red-green regression remains the primary proof for the more specific `策略上下文已切换` banner branch because the local PM2 browser path settled banner text to the neutral synced variant while still proving the selector-local hint leak was removed

## Skill Feedback
- `v1.67` adds a reusable distinction between selector-owned local action artifacts and global route-local memory.
- Future audits should verify that generated snapshots, hint chips, and context banners are rebound or cleared whenever a query-scoped routed workbench switches to a new selector without its own verified local artifact.
