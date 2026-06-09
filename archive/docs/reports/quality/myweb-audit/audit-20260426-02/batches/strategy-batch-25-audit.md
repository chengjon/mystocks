# Batch Audit Report: strategy-batch-25

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend selector-owned route truth to the canonical strategy-backtest task tab so same-instance `strategyId` query switches no longer leak the earlier strategy's completed task rows into a new selector without its own verified task context.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`, with `web/frontend/src/views/strategy/Backtest.vue` acting as the wrapper shell.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible `回测任务` rows were stored in one route-local list, so the same mounted page instance could switch from `strategyId=101` to `strategyId=202` and still present the earlier strategy's verified task row even though the new selector had never verified its own task context.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-owned task rows are still vulnerable if a mounted workbench stores verified task surfaces route-locally instead of by current selector.
- Occurrence basis:
  - `/strategy/backtest` already exposed a query-owned strategy context through the route `strategyId`
  - the route allowed a same-instance query switch without clearing or restoring selector-owned task rows
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- Suggested follow-up scope: continue applying `v1.70 + v1.66` to query-scoped routed workbenches whose visible task tabs or execution ledgers derive row sets from selector-owned verified snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-owned task-row truth > selector-owned execution retention > same-instance query-switch proof
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` and `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` were reviewed as wrapper consumers and inherit the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-backtest-issue-10`
- deferred items:
  - no shared task-store or shared execution-ledger redesign was approved for this batch

## Fix Summary
- Added selector-keyed task-row retention inside the canonical backtest owner view-model.
- Rebased visible `backtestTasks` on the current selector's verified task context instead of one route-local task list.
- Preserved same-selector verified task-row retention so switching away and back can restore the correct selector-owned rows from the page-local cache.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch task-tab path.
- Reused existing `myweb-audit v1.70 + v1.66`; no new skill version was needed.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-25-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-10`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-25`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` task-tab path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `28/28`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `50` structurally valid tests including the strengthened `/strategy/backtest` selector-switch task-tab assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first reaches a completed `101` task row in the `回测任务` tab
    - the same mounted route then reaches `ID 202`
    - reopening `回测任务` under `202` produces `0` visible `.task-item` rows
    - the stale prior `TASK ... / 回测任务已完成` row no longer remains visible after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-25-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-25-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-25-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-25-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-selector-task-rows-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
