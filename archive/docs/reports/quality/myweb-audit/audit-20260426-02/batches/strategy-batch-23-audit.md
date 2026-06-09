# Batch Audit Report: strategy-batch-23

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend the existing selector-scoped verified-snapshot rule to the canonical strategy-backtest route so same-instance `strategyId` query switches no longer leak the earlier strategy's synced report row into a new selector without its own verified report context.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`, with `web/frontend/src/views/strategy/Backtest.vue` acting as the wrapper shell.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible synced report row was stored in one route-local array, so the same mounted page instance could switch from `strategyId=101` to `strategyId=202` and still present the earlier strategy's verified report row even though the new selector had never verified its own report context.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped result-row truth is still vulnerable if a mounted workbench stores verified rows route-locally instead of by current selector.
- Occurrence basis:
  - `/strategy/backtest` already exposed a query-owned strategy context through the route `strategyId`
  - the route allowed a same-instance query switch without clearing or restoring selector-owned synced report rows
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- Suggested follow-up scope: continue applying `v1.68` to query-scoped routed workbenches and detail pages whose visible result rows are derived from selector-owned verified snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-scoped verified-snapshot truth > route-local result-row retention > same-instance query-switch proof
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` and `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` were reviewed as wrapper consumers and inherit the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-backtest-issue-08`
- deferred items:
  - no shared report-center redesign or summary reinterpretation was approved for this batch

## Fix Summary
- Added selector-keyed verified report-row retention inside the canonical backtest owner view-model.
- Rebased visible report rows on the current selector's verified report context instead of one route-local array.
- Preserved same-selector verified report retention while clearing old report rows after a same-instance selector switch into a strategy without its own verified report context.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch path.
- Reused existing `myweb-audit v1.68` for selector-scoped verified-snapshot truth on query-owned routed workbenches.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-23-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-08`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-23`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` report-row path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `26/26`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `48` structurally valid tests including the strengthened `/strategy/backtest` selector-switch report-row assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first syncs one verified report row for `strategyId=101`
    - the same mounted route instance then reaches `ID 202` with zero visible report rows when the new selector has no verified report context
    - old `Momentum Alpha` report-row truth no longer remains visible after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-23-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-23-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-23-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-23-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-selector-report-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
