# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-15`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-004`
- Consolidated issue: `strategy-backtest-issue-04`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The visible hero shell exposes a top-level freshness surface through `最后更新 / UPDATED`.
- Before repair, the rejected-run guard inside `runBacktest()` wrote `new Date().toLocaleString()` when no verified strategy context existed, so a local warning-only interaction could still present a fabricated fresh-sync timestamp.

## Trigger
1. Open `/strategy/backtest` with a controlled first-load strategy-list failure or other unresolved strategy-context shell.
2. Click `启动回测`.
3. Inspect the visible hero freshness surface `最后更新 / UPDATED`.

## Expected
- Rejected or no-op manual actions should keep hero freshness pinned to the last verified snapshot or explicit placeholder truth such as `--`.
- Warning banners and local logs may update, but the page must not claim a fresh routed sync without a new verified snapshot.

## Actual Before Repair
- The route replaced `UPDATED: --` with a local current timestamp even though no strategy context was verified and no real backtest task had started.

## Repair
- Removed the local-current-clock write from the `!strategyId` branch in `runBacktest()`.
- Added owner regression coverage in `ArtDecoBacktestAnalysis.spec.ts`.
- Strengthened routed Phase 3 matrix coverage in `phase3-mainline-matrix.spec.ts`.
- Promoted `myweb-audit` to `v1.54` for action-triggered freshness truth on unresolved-context manual actions.

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
  - controlled authenticated system-`google-chrome` verification confirmed `first-load fail -> click run` keeps `最后更新` at `--` while showing `未绑定有效策略ID，无法启动真实回测。`
  - natural PM2 `/strategy/backtest` still reaches the route and currently renders an honest live shell with route-level freshness coming from the verified strategy-list sync path

## Skill Feedback
- `v1.54` adds a reusable distinction between first-load shell truth and action-triggered freshness truth.
- Future audits should explicitly verify that rejected or no-op manual actions cannot mutate `UPDATED`-style hero metadata before a new verified snapshot exists.
