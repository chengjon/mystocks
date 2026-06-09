# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-26`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-011`
- Consolidated issue: `strategy-backtest-issue-11`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The route already exposes selector-owned context through `selectedStrategyId`, the context strip, the KPI strip, and route-local execution surfaces such as the `回测任务` and `报告中心` tabs.
- Before repair, KPI summary values were stored in one route-global `summary` surface instead of being keyed to the current `strategyId` query, so a same-instance selector switch could keep showing the previous strategy's incremented totals.

## Trigger
1. Open `/strategy/backtest?strategyId=101` with a controlled successful strategies payload for strategy `101`.
2. Confirm the KPI strip starts at the baseline summary `总回测次数:2 / 策略胜率:50% / 年化收益:3.2% / 最大回撤:-2%`.
3. Start a controlled completed run so the KPI strip advances to `总回测次数:3` for strategy `101`.
4. Switch the same mounted route instance to `/strategy/backtest?strategyId=202` before strategy `202` has any verified KPI summary of its own.
5. Inspect the visible KPI strip without remounting the routed owner.

## Expected
- Selector-owned KPI summary values must belong only to the current `strategyId` query.
- If the new selector has no verified KPI context, the same mounted route should keep `当前策略上下文ID 202` while the KPI strip falls back to the neutral baseline summary `2 / 50% / 3.2% / -2%`.

## Actual Before Repair
- The backtest owner kept one route-global `summary` surface and mutated it in place after a completed run.
- After switching to `strategyId=202`, `/strategy/backtest` could still show `总回测次数:3`, so the new selector shell inherited the prior strategy's verified KPI summary even though `202` had never verified its own KPI context.

## Repair
- Added selector-keyed KPI summary retention inside the backtest owner view-model.
- Rebased visible summary values on the current `strategyId` selector instead of one route-global summary surface.
- Preserved same-selector verified KPI retention so switching away and back can restore the correct selector-owned totals from the page-local cache.
- Added owner regression coverage for the same-instance `strategyId=101 -> 202` KPI-strip switch path.
- Strengthened the routed Phase 3 matrix so `/strategy/backtest` must clear the stale incremented KPI summary after a selector switch into a strategy without its own verified KPI context.
- Reused existing `myweb-audit v1.71 + v1.68` because the defect fits the current selector-owned snapshot truth guidance.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts -t "does not leak the previous strategy KPI summary into a new route query without its own verified task context"`
- Strategy family regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts`
- Type-check:
  - `timeout 180s npm run type-check`
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list`
- Targeted live verification:
  - controlled authenticated system-`google-chrome` verification with `serviceWorkers: block` confirmed the same mounted `/strategy/backtest` route first shows a verified `101` KPI strip with `2 -> 3`
  - the same verification then switched to `strategyId=202` and confirmed the KPI strip returned to `2 / 50% / 3.2% / -2%`
  - the stale prior `总回测次数:3` increment no longer remained visible under the new selector shell

## Skill Feedback
- Existing `v1.68` already covered selector-owned snapshot truth, and `v1.71` already covered route-scoped selector ownership. This batch did not need a new skill version because the failure mode is the KPI-strip variant of those existing rules.
- Future audits should treat KPI strips the same way as selector-owned report rows, task rows, and execution panels whenever a mounted workbench route can switch entities without remounting.
