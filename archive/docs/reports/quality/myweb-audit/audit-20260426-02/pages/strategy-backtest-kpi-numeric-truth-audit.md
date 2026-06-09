# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-16`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-005`
- Consolidated issue: `strategy-backtest-issue-05`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- Its top KPI strip is rendered through the page-local `BacktestKpiGrid.vue` wrapper around shared `ArtDecoStatCard` primitives.
- Before repair, that wrapper let shared delta chrome and exact-decimal formatting leak onto absolute KPI cards, so the route surfaced faux `+0%` movement semantics and `0.00` pseudo precision even though the strip only proved plain absolute values.

## Trigger
1. Open `/strategy/backtest?strategyId=101`.
2. Inspect the visible stats strip before or without any backtest-result mutation.
3. Check for shared `.artdeco-stat-change`, `+0%`, or exact-decimal count formatting such as `总回测次数 0.00`.

## Expected
- Absolute KPI cards should render plain values only.
- Count-only cards should remain on whole-count semantics.
- The route must not leak shared delta chrome such as flat dots or `+0%` unless the current card has a verified comparison baseline.

## Actual Before Repair
- `BacktestKpiGrid.vue` passed raw `items` into shared `ArtDecoStatCard` defaults.
- The visible strip rendered inherited `.artdeco-stat-change` chrome.
- Count-only values could render with exact-decimal pseudo precision such as `12.00`.

## Repair
- Forced `show-change=false` inside the page-local `BacktestKpiGrid.vue` wrapper.
- Normalized finite numeric KPI values to strings before passing them into shared stat-card rendering.
- Added owner regression coverage in `BacktestKpiGrid.spec.ts`.
- Strengthened routed Phase 3 matrix coverage in `phase3-mainline-matrix.spec.ts`.
- Promoted `myweb-audit` to `v1.58` for routed KPI-wrapper numeric-cluster truth.

## Verification
- Owner regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts`
- Strategy family regression:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts`
- Type-check:
  - `timeout 180s npm run type-check`
- Routed E2E structure:
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list`
- Targeted live verification:
  - controlled authenticated system-`google-chrome` verification confirmed `/strategy/backtest?strategyId=101` now reports `changeCount: 0`, `hasPlusZero: false`, `hasZeroPointZeroZero: false`, and card values `总回测次数=0 / 策略胜率=0% / 年化收益=0% / 最大回撤=0%`
  - the canonical routed strip no longer shows `.artdeco-stat-change`, `+0%`, or `0.00`

## Skill Feedback
- `v1.58` adds a reusable distinction between honest absolute KPI strips and shared stat-card defaults that imply unsupported movement or fractional semantics.
- Future audits should treat same-strip `+0%` and `0.00` leaks as one routed numeric cluster instead of fixing them piecemeal.
