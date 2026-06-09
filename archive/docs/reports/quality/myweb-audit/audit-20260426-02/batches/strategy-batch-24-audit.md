# Batch Audit Report: strategy-batch-24

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend selector-owned route truth to the canonical strategy-backtest execution panel so same-instance `strategyId` query switches no longer leak the earlier strategy's completed progress and run logs into a new selector without its own verified task context.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`, with `web/frontend/src/views/strategy/Backtest.vue` acting as the wrapper shell.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible execution progress and run-log panel were stored in one route-local state block, so the same mounted page instance could switch from `strategyId=101` to `strategyId=202` and still present the earlier strategy's completed execution state even though the new selector had never verified its own task context.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-owned execution-state truth is still vulnerable if a mounted workbench stores verified progress or logs route-locally instead of by current selector.
- Occurrence basis:
  - `/strategy/backtest` already exposed a query-owned strategy context through the route `strategyId`
  - the route allowed a same-instance query switch without clearing or restoring selector-owned execution progress and run logs
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- Suggested follow-up scope: continue applying `v1.70` to query-scoped routed workbenches whose visible execution panels derive task-stage summaries, progress, or logs from selector-owned verified snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-owned execution-state truth > route-local execution retention > same-instance query-switch proof
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` and `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` were reviewed as wrapper consumers and inherit the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-backtest-issue-09`
- deferred items:
  - no shared progress, logging, or task-store redesign was approved for this batch

## Fix Summary
- Added selector-keyed execution-state retention inside the canonical backtest owner view-model.
- Rebased visible `progress` and `runLogs` on the current selector's verified execution context instead of one route-local execution panel state.
- Preserved same-selector verified execution retention so switching away and back can restore the correct selector-owned progress and logs from the page-local cache.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch execution path.
- Promoted `myweb-audit` to `v1.70` for selector-owned execution-state truth on query-owned routed workbenches.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-24-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-09`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-24`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` execution-panel path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `27/27`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `49` structurally valid tests including the strengthened `/strategy/backtest` selector-switch execution assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first reaches a completed `101` execution state with `回测完成 / 100%`
    - the same mounted route instance then reaches `ID 202` with `等待任务 / 0%`
    - the stale `回测结果已同步到报告中心。` log line no longer remains visible after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-24-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-24-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-24-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-24-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-selector-execution-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
