# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-23`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-008`
- Consolidated issue: `strategy-backtest-issue-08`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The route already exposes selector-owned context through `selectedStrategyId`, the context strip, and route-local result surfaces such as synced backtest report rows.
- Before repair, synced report rows were stored in one route-local array instead of being keyed to the current `strategyId` query, so a same-instance selector switch could keep showing the previous strategy's verified report row.

## Trigger
1. Open `/strategy/backtest?strategyId=101` with a controlled successful strategies payload for strategy `101`.
2. Start a controlled completed run so `报告中心` syncs one verified report row for `101`.
3. Switch the same mounted route instance to `/strategy/backtest?strategyId=202` before strategy `202` has any verified report context.
4. Inspect the report table without remounting the owner route.

## Expected
- Selector-owned report rows must belong only to the current `strategyId` query.
- If the new selector has no verified report context, the same mounted route should keep `ID 202` in the context strip while the visible report table drops back to zero rows.

## Actual Before Repair
- `syncBacktestResultReport()` wrote verified report rows into one route-local array and left them there across selector switches.
- After switching to `strategyId=202`, `/strategy/backtest` could still show the earlier `Momentum Alpha` report row even though the new selector had no verified report context of its own.

## Repair
- Added selector-keyed verified report-row retention inside the backtest owner view-model.
- Rebased visible `reportRows` on the current `strategyId` selector instead of one route-local array.
- Preserved same-selector verified report retention so switching away and back can restore the correct selector-owned report row from the page-local cache.
- Added owner regression coverage for the same-instance `strategyId=101 -> 202` report-row switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/backtest` must clear old verified report rows after a selector switch into a strategy without its own verified report context.
- Reused existing `myweb-audit v1.68` selector-scoped snapshot truth instead of promoting a new rule version.

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
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/backtest` route first syncs one verified report row for `strategyId=101`
  - the same verification then switched to `strategyId=202` and confirmed the report table drops from `1` visible row to `0` visible rows while the context strip updates to `ID 202`

## Skill Feedback
- Existing `v1.68` already covered this failure mode: query-owned routed workbenches cannot let one route-local verified result array stand in for every selector once visible rows belong to a concrete entity query.
- Future audits should treat synced result rows the same way as selector-owned request provenance and selector-owned detail rows whenever the mounted route can switch entities without remounting.
