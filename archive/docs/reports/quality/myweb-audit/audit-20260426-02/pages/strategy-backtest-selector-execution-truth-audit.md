# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-24`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-009`
- Consolidated issue: `strategy-backtest-issue-09`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The route already exposes selector-owned context through `selectedStrategyId`, the context strip, and route-local execution surfaces such as the progress panel and run-log panel.
- Before repair, execution progress and run logs were stored in one route-local state block instead of being keyed to the current `strategyId` query, so a same-instance selector switch could keep showing the previous strategy's completed execution state.

## Trigger
1. Open `/strategy/backtest?strategyId=101` with a controlled successful strategies payload for strategy `101`.
2. Start a controlled completed run so the execution panel reaches `回测完成 / 100%` and the log panel records `回测结果已同步到报告中心。`.
3. Switch the same mounted route instance to `/strategy/backtest?strategyId=202` before strategy `202` has any verified task context.
4. Inspect the execution panel without remounting the owner route.

## Expected
- Selector-owned execution surfaces must belong only to the current `strategyId` query.
- If the new selector has no verified task context, the same mounted route should keep `ID 202` in the context strip while the visible execution panel falls back to neutral baseline truth such as `等待任务 / 0%` and no stale success log.

## Actual Before Repair
- The backtest owner kept one route-local `progress` plus `runLogs` surface and reused it across selector switches.
- After switching to `strategyId=202`, `/strategy/backtest` could still show the earlier completed execution state from `101`, including `100%` progress and the stale `回测结果已同步到报告中心。` log line, even though the new selector had no verified task context of its own.

## Repair
- Added selector-keyed execution-state retention inside the backtest owner view-model.
- Rebased visible `progress` and `runLogs` on the current `strategyId` selector instead of one route-global execution panel state.
- Preserved same-selector verified execution-state retention so switching away and back can restore the correct selector-owned progress and logs from the page-local cache.
- Added owner regression coverage for the same-instance `strategyId=101 -> 202` execution-panel switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/backtest` must clear old completed execution truth after a selector switch into a strategy without its own verified task context.
- Promoted the rule to `myweb-audit v1.70` because selector-scoped row and local-action truth now extends into selector-owned execution-state surfaces such as progress panels and run logs.

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
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/backtest` route first reaches a completed `101` execution state with `回测完成 / 100%`
  - the same verification then switched to `strategyId=202` and confirmed the execution panel falls back to `等待任务 / 0%`
  - the stale `回测结果已同步到报告中心。` log line no longer remains visible after the selector switch

## Skill Feedback
- Existing selector-scoped snapshot rules covered rows, counts, request provenance, and local hints, but not execution-panel state. This batch promoted `v1.70` so same-instance selector switches on routed workbenches must also govern progress panels, task-stage summaries, and run logs.
- Future audits should treat selector-owned execution-state surfaces the same way as selector-owned rows whenever a mounted route can switch entities without remounting.
