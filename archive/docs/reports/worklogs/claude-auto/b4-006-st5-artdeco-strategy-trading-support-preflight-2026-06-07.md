# B4.006 ST-5 ArtDeco Strategy/Trading Support Preflight

Date: 2026-06-07
Branch: `wip/root-dirty-20260403`
HEAD: `8d27cb7738cd` (`B4.006 ST-4: stabilize trade route support`)

## Scope Status

This is a no-source boundary preflight. It records evidence and package boundaries only.

- Staged files before ST-5: `0`.
- Full dirty worktree remains broad and unrelated. ST-5 must stage only exact package files.
- ST-5 scoped dirty files: `26`.
- ST-5 status split: `17` modified, `9` untracked.
- Extension split: `9` `.vue`, `12` `.ts`, `5` `.scss`.
- Extra dirty files inside `web/frontend/src/views/artdeco-pages/{strategy-tabs,trading-tabs}/`: `0`.
- Closed ST-1 to ST-4 residue in scoped check: `0`.
- ST-HOLD dirty files remain out of scope:
  - `web/frontend/src/views/strategy/BatchScan.vue`
  - `web/frontend/src/views/strategy/ResultsQuery.vue`
  - `web/frontend/src/views/strategy/SingleRun.vue`
  - `web/frontend/src/views/strategy/StatsAnalysis.vue`

## Exact ST-5 File List

Strategy tabs and support:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/backtestModulePresence.test.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestHeader.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestKpiGrid.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestWorkbenchTabs.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationViewModel.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyManagement.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/StrategyParametersTab.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyOptimizationSourcePolicy.test.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategySignalsData.test.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationSourcePolicy.ts`

Trading tabs:

- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts`
- `web/frontend/src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts`

## Exclusions

Do not stage or edit these during ST-5:

- ST-HOLD files under `web/frontend/src/views/strategy/{BatchScan,ResultsQuery,SingleRun,StatsAnalysis}.vue`.
- Closed ST-1 to ST-4 files, including route wrappers under `web/frontend/src/views/strategy/Signals.vue`, `web/frontend/src/views/strategy/Gpu.vue`, `web/frontend/src/views/trade/Terminal.vue`, `web/frontend/src/views/trade/Signals.vue`, and `web/frontend/src/views/trade/History.vue`.
- ST-6 sidecar/noncanonical route-truth candidates under `web/frontend/src/views/trading-decision/`, `web/frontend/src/views/trading/`, and their tests.
- ST-7 shared/static governance files such as `web/frontend/src/utils/atrading.ts`, `web/frontend/src/utils/strategy-adapters.ts`, `web/frontend/src/utils/trade-adapters.ts`, and route/static config tests.
- Root package metadata and unrelated dirty files.

## Consumer Boundary

Detected consumers:

- `StrategyParametersTab`: `web/frontend/src/views/strategy/Parameters.vue`
- `ArtDecoStrategyOptimization`: `web/frontend/src/views/strategy/Optimization.vue`, `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- `ArtDecoStrategyManagement`: `web/frontend/src/views/strategy/List.vue`, `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- Backtest support components: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`, `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue`, and existing backtest component specs
- `strategySignalsData`: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`, `web/frontend/src/views/trade/Signals.vue`
- Trading tabs: `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`, `web/frontend/src/views/trade/Signals.vue`, and advanced ArtDeco trading signal component references

The new `strategyOptimizationSourcePolicy.ts` is not in the current GitNexus index. Local reference scan found only:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationViewModel.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyOptimizationSourcePolicy.test.ts`

## GitNexus Impact

All indexed ST-5 impact checks are LOW risk with `processes_affected = 0`.

Already available from prior handoff:

- `ArtDecoStrategyManagement.vue`: LOW, impacted 4, direct 2.
- `ArtDecoStrategyOptimization.vue`: LOW, impacted 2, direct 2.
- `StrategyParametersTab.vue`: LOW, impacted 1, direct 1.
- `BacktestKpiGrid.vue`: LOW, impacted 4, direct 1.
- `strategySignalsData.ts`: LOW, impacted 13, direct 3.
- `strategyOptimizationViewModel.ts`: LOW, impacted 4, direct 2.
- `ArtDecoHistoryView.vue`: LOW, impacted 1, direct 1.

Fresh checks in this preflight:

- `ArtDecoTradingSignals.vue` under `trading-tabs`: LOW, impacted 3, direct 1.
- `ArtDecoPerformanceAnalysis.vue`: LOW, impacted 1, direct 1.
- `ArtDecoPositionMonitor.vue`: LOW, impacted 1, direct 1.
- `BacktestHeader.vue`: LOW, impacted 3, direct 1.
- `strategyOptimizationSourcePolicy.ts`: not found in index because it is new/untracked; local reference boundary listed above.

GitNexus reported `fresh_for_staged_diff = true`; it also reported `current_commit_differs_from_indexed_commit` while unstaged ST-5 work exists. Run the GitNexus analyzer and `gitnexus.detect_changes(scope: "staged")` at each commit gate.

## OPENDOG Preflight

OPENDOG verification is fresh and has no failing runs at preflight time.

- Latest verification has `all_expected_kinds_recorded = true`.
- Latest verification reports `failing_runs = 0`.
- Recent recorded build/test runs passed but have `exit_code_masked_possible = true`, so each ST-5 package must record fresh native verification with OPENDOG after running local commands.

## Proposed Minimal Commit Packages

### ST-5A Parameters Tab Support

Files:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/StrategyParametersTab.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts`

Diff size: 3 files, 2 modified, 1 untracked, about 511 additions and 87 deletions.

Focused tests:

- `cd web/frontend && npm run test:unit -- src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts`
- `cd web/frontend && npm run type-check`
- Focused E2E route smoke for `/strategy/parameters` if the Playwright suite exposes it; otherwise PM2 route smoke plus affected unit coverage.

### ST-5B Optimization Tab Support

Files:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationViewModel.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationSourcePolicy.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyOptimizationSourcePolicy.test.ts`

Diff size: 6 files, 3 modified, 3 untracked, about 562 additions and 49 deletions.

Focused tests:

- `cd web/frontend && npm run test:unit -- src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts`
- `cd web/frontend && npm run test:node -- src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyOptimizationSourcePolicy.test.ts` if the script exists; otherwise run the repo's node-test command or direct Vitest equivalent discovered in `package.json`.
- `cd web/frontend && npm run type-check`
- Focused E2E route smoke for `/strategy/optimization` if available.

### ST-5C Strategy Management Support

Files:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyManagement.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts`

Diff size: 3 files, 2 modified, 1 untracked, about 416 additions and 20 deletions.

Focused tests:

- `cd web/frontend && npm run test:unit -- src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts`
- `cd web/frontend && npm run type-check`
- Focused strategy management E2E if available, otherwise route smoke through canonical strategy list route.

### ST-5D Backtest Component Support

Files:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestHeader.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestKpiGrid.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestWorkbenchTabs.scss`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/backtestModulePresence.test.ts`

Diff size: 6 files, 5 modified, 1 untracked, about 49 additions and 13 deletions.

Focused tests:

- `cd web/frontend && npm run test:unit -- src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts`
- Run the package's node/module-presence test command after discovering the script.
- `cd web/frontend && npm run type-check`
- Existing backtest E2E candidates include Python Playwright tests for `/strategy/backtest`; choose the smallest stable PM2-compatible route smoke.

### ST-5E Strategy Signals Data Support

Files:

- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategySignalsData.test.ts`

Diff size: 2 files, 1 modified, 1 untracked, about 168 additions and 2 deletions.

Focused tests:

- Run the node-data test for `strategySignalsData.test.ts` after discovering the script.
- `cd web/frontend && npm run type-check`
- Route smoke for affected strategy/trade signals pages if available, without editing closed ST-1 wrapper files.

### ST-5F Trading Tabs Support

Files:

- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts`
- `web/frontend/src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts`

Diff size: 6 files, 4 modified, 2 untracked, about 151 additions and 397 deletions.

Focused tests:

- `cd web/frontend && npm run test:unit -- src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts`
- `cd web/frontend && npm run type-check`
- PM2 route smoke for `/trade/history` and `/trade/signals` if stable; otherwise component-level coverage plus trading center smoke.

## Commit Gates Per Package

For every ST-5 package:

1. Confirm staged set is empty before selecting package files.
2. Stage only exact files in that package.
3. Confirm staged names are exactly the package file list.
4. Run focused unit/node tests.
5. Run `cd web/frontend && npm run type-check`.
6. Run focused E2E or PM2 route smoke with actual command, browser/project, total count, pass/fail/skip counts.
7. Confirm PM2 services:
   - `mystocks-backend`: `http://localhost:8020`
   - `mystocks-frontend`: `http://localhost:3020`
8. Record OPENDOG verification for native checks.
9. Run GitNexus analyzer if needed, then `gitnexus.detect_changes(scope: "staged")`.
10. Commit one package only.

## Decision

Proceed with ST-5A first after this no-source preflight, unless a later gate reveals cross-package coupling that requires splitting further. Do not edit ST-HOLD, ST-1 to ST-4, ST-6, ST-7, or unrelated dirty files.
