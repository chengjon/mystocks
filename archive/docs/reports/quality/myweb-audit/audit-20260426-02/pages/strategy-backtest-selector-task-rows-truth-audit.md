# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-25`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-010`
- Consolidated issue: `strategy-backtest-issue-10`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The route already exposes selector-owned context through `selectedStrategyId`, the context strip, and route-local execution surfaces such as the `回测任务` tab.
- Before repair, task rows were stored in one route-local list instead of being keyed to the current `strategyId` query, so a same-instance selector switch could keep showing the previous strategy's verified task row.

## Trigger
1. Open `/strategy/backtest?strategyId=101` with a controlled successful strategies payload for strategy `101`.
2. Start a controlled completed run so the `回测任务` tab shows a verified `TASK ... / 回测任务已完成` row.
3. Switch the same mounted route instance to `/strategy/backtest?strategyId=202` before strategy `202` has any verified task context.
4. Reopen the `回测任务` tab without remounting the owner route.

## Expected
- Selector-owned task rows must belong only to the current `strategyId` query.
- If the new selector has no verified task context, the same mounted route should keep `ID 202` in the context strip while the `回测任务` tab falls back to `0 rows` and no stale `TASK ... / 回测任务已完成` row remains visible.

## Actual Before Repair
- The backtest owner kept one route-local `backtestTasks` list and reused it across selector switches.
- After switching to `strategyId=202`, `/strategy/backtest` could still show the earlier verified task row from `101`, including the stale `TASK ... / 回测任务已完成` surface, even though the new selector had never verified its own task context.

## Repair
- Added selector-keyed task-row retention inside the backtest owner view-model.
- Rebased visible `backtestTasks` on the current `strategyId` selector instead of one route-global task list.
- Preserved same-selector verified task-row retention so switching away and back can restore the correct selector-owned task rows from the page-local cache.
- Added owner regression coverage for the same-instance `strategyId=101 -> 202` task-tab switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/backtest` must clear old verified task rows after a selector switch into a strategy without its own verified task context.
- Reused existing `myweb-audit v1.70 + v1.66` because the defect fits existing selector-owned execution and selector-owned row truth guidance.

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
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/backtest` route first shows a verified `101` task row in the `回测任务` tab
  - the same verification then switched to `strategyId=202`, reopened `回测任务`, and confirmed `0` visible `.task-item` rows
  - the stale prior `TASK ... / 回测任务已完成` row no longer remained visible under the new selector shell

## Skill Feedback
- Existing `v1.70` already covered selector-owned execution-state truth, and `v1.66` already covered selector-owned rows. This batch did not need a new skill version because the failure mode is the intersection of those two existing rules.
- Future audits should treat task tabs the same way as selector-owned report rows whenever a mounted workbench route can switch entities without remounting.
