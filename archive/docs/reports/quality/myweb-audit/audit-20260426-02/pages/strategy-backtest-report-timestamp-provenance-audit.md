# Page Audit Report: /strategy/backtest

## Batch
- Batch ID: `strategy-batch-14`
- Module: `strategy`
- Canonical entry: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Primary repair owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`

## Issue Summary
- Severity: High
- Category: data-state
- Finding ID: `strategy-backtest-data-state-003`
- Consolidated issue: `strategy-backtest-issue-03`

## Route Truth
- The page is a canonical routed workbench at `/strategy/backtest`.
- The visible `报告中心` table includes a row-level freshness surface through the `生成时间` column.
- Before repair, the route mapped missing result completion metadata through `formatUpdatedAtLabel()` and substituted `new Date().toLocaleString()`, so a valid synced report row could still present a fabricated local current-time freshness stamp.

## Trigger
1. Open `/strategy/backtest?strategyId=101`.
2. Let `/api/v1/strategy/backtest/run` and the visible result-sync path succeed.
3. Return a valid `/api/v1/strategy/backtest/results/*` payload without `completed_at`, `completedAt`, `updated_at`, or `updatedAt`.
4. Switch to `报告中心` and inspect the visible `生成时间` cell.

## Expected
- Missing row-level completion metadata should degrade to explicit placeholder truth such as `--`.
- The page must not substitute the local current clock for report freshness that the payload does not prove.

## Actual Before Repair
- The route showed a precise local current-time `生成时间` even though the synced result payload omitted completion metadata entirely.

## Repair
- Changed `formatUpdatedAtLabel()` in `backtestAnalysisViewModel.ts` so missing completion metadata now degrades to `--`.
- Added owner regression coverage in `ArtDecoBacktestAnalysis.spec.ts`.
- Added routed Phase 3 matrix coverage in `phase3-mainline-matrix.spec.ts`.
- Promoted `myweb-audit` to `v1.48` for row-level result freshness provenance.

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
  - controlled system-`google-chrome` route confirmed the first synced report row now renders `策略 101 ... --`
  - natural PM2 `/strategy/backtest` still reaches the route and keeps the surrounding shell stable while this repair remains route-local

## Skill Feedback
- `v1.48` adds a reusable distinction between hero freshness metadata and row-level result freshness surfaces.
- Future audits should explicitly inspect report-table cells such as `generatedAt`, `updatedAt`, `completed_at`, and `completedAt`, even when hero freshness already looks correct.
