# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-18`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-006`
- Consolidated issue: `strategy-backtest-issue-06`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The visible hero shell exposes a top-level freshness surface through `最后更新 / UPDATED`.
- Before repair, the route-local task snapshot helper rewrote `lastUpdated` with `new Date().toLocaleString()` as soon as queued or running task-state updates arrived, even though no verified backtest result or report snapshot had synchronized yet.

## Trigger
1. Open `/strategy/backtest?strategyId=101` with a controlled successful strategy-list load so the route has one verified freshness value.
2. Wait long enough for the local current clock to diverge.
3. Click `启动回测` while the request only reaches queued state and no verified result or report snapshot exists yet.
4. Inspect the visible hero freshness surface `最后更新 / UPDATED`.

## Expected
- Queued or running task-state updates may change progress, task rows, logs, and banners immediately.
- Hero freshness must stay pinned to the last verified snapshot or explicit placeholder truth until a new verified result or report snapshot actually exists.

## Actual Before Repair
- The route replaced the previously verified `UPDATED` value with a newer local current timestamp as soon as the queued task snapshot landed, even though the visible page still had no new verified backtest result or report snapshot.

## Repair
- Removed the local-current-clock write from `applyBacktestTaskSnapshot()`.
- Added owner regression coverage in `ArtDecoBacktestAnalysis.spec.ts` with fake-time control so the verified strategy-context freshness and queued-task timestamp cannot collapse to the same second.
- Strengthened routed Phase 3 matrix coverage in `phase3-mainline-matrix.spec.ts` so the queued-only browser path must preserve the same `最后更新` text before and after `启动回测`.
- Promoted `myweb-audit` to `v1.61` for queued-task freshness truth on routed task and workbench pages.

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
  - controlled authenticated system-`google-chrome` verification confirmed the queued-only path keeps identical `最后更新` text before and after `启动回测` while the banner still says `回测任务已创建，进入排队`
  - natural PM2 `/strategy/backtest?strategyId=101` still reaches the route and keeps its current honest shell with route-level freshness coming from the verified strategy-list sync path

## Skill Feedback
- `v1.61` adds a reusable distinction between task-state progress truth and verified result freshness truth.
- Future audits should verify that queued or running background task updates cannot mutate `UPDATED`-style hero metadata before a new verified result, report, or primary snapshot actually exists.
