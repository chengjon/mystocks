# Batch Audit Report: strategy-batch-26

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend selector-owned route truth to the canonical strategy-backtest KPI strip so same-instance `strategyId` query switches no longer leak the earlier strategy's incremented summary into a new selector without its own verified KPI context.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`, with `web/frontend/src/views/strategy/Backtest.vue` acting as the wrapper shell.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible KPI strip reused one route-global summary surface, so the same mounted page instance could switch from `strategyId=101` to `strategyId=202` and still present the earlier strategy's incremented `总回测次数:3` even though the new selector had never verified its own KPI context.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-owned KPI strips are still vulnerable if a mounted workbench stores verified summary surfaces route-globally instead of by current selector.
- Occurrence basis:
  - `/strategy/backtest` already exposed a query-owned strategy context through the route `strategyId`
  - the route allowed a same-instance query switch without clearing or restoring selector-owned KPI values
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- Suggested follow-up scope: continue applying `v1.71 + v1.68` to query-scoped routed workbenches whose visible KPI strips or summary badges derive values from selector-owned verified snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-owned KPI-summary truth > selector-owned execution/task/report truth > same-instance query-switch proof
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` and `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` were reviewed as wrapper consumers and inherit the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-backtest-issue-11`
- deferred items:
  - no shared KPI-store or shared selector-state redesign was approved for this batch

## Fix Summary
- Added selector-keyed KPI summary retention inside the canonical backtest owner view-model.
- Rebased visible summary values on the current selector's verified task context instead of one route-global summary surface.
- Preserved same-selector verified KPI retention so switching away and back can restore the correct selector-owned totals from the page-local cache.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch KPI path.
- Reused existing `myweb-audit v1.71 + v1.68`; no new skill version was needed.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-26-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-11`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-26`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` KPI-summary path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `29/29`
  - `timeout 180s npm run type-check` -> failed only on pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`; no new type errors were introduced by this batch
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `51` structurally valid tests including the strengthened `/strategy/backtest` selector-switch KPI assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first shows a verified `101` KPI strip with `2 / 50% / 3.2% / -2%`
    - running a controlled backtest advances the same selector to `3 / 50% / 3.2% / -2%`
    - the same mounted route then reaches `当前策略上下文ID 202`
    - the KPI strip under `202` returns to the neutral baseline `2 / 50% / 3.2% / -2%`
    - the stale prior `总回测次数:3` increment no longer remains visible after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-26-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-26-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-26-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-26-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-selector-kpi-summary-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
