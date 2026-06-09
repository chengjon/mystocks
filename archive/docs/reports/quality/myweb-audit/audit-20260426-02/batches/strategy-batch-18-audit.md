# Batch Audit Report: strategy-batch-18

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend freshness-provenance auditing so the canonical strategy-backtest route no longer lets queued or running task-state updates stamp hero freshness metadata with the local current clock before any new verified result or report snapshot exists.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/strategy/Backtest.vue` and its downstream owner `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route-local `applyBacktestTaskSnapshot()` helper advanced the hero freshness surface with `new Date().toLocaleString()` whenever queued or running task-state updates arrived, so progress-only task movement could masquerade as fresh routed result truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: freshness-provenance audits must inspect queued or running task-state updates separately from verified result synchronization, because local task-progress flows can still mutate hero freshness metadata without producing any new verified routed snapshot.
- Occurrence basis:
  - `/strategy/backtest` already had a visible hero freshness surface through `最后更新 / UPDATED`
  - queued task-state updates used the same route-local helper as later terminal updates and stamped local current time before any new result existed
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Suggested follow-up scope: continue applying `v1.61` to routed task, execution, and workbench pages whose visible hero freshness can be touched by queued or running background task-state updates before any result or report snapshot exists.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: queued-task freshness truth > route-local hero provenance
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` was reviewed as the routed wrapper and did not require a separate repair
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` inherits the safer freshness truth without a template rewrite
- fixes applied:
  - `strategy-backtest-issue-06`
- deferred items:
  - no strategy-service or backend backtest-schema redesign was approved for this batch

## Fix Summary
- Removed the local-current-clock write from the route-local task snapshot helper during queued and running progress updates.
- Added owner-level regression coverage with controlled time drift so queued-only task progress must preserve the previously verified freshness text.
- Added routed Phase 3 matrix coverage so `/strategy/backtest` keeps hero freshness metadata stable through the queued-only browser path.
- Promoted `myweb-audit` to `v1.61` for queued-task freshness truth on routed task and workbench pages.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-18-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-06`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-18`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the queued-only freshness path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `21/21`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `43` structurally valid tests including the strengthened `/strategy/backtest` queued-only freshness assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated `verified strategy load -> wait -> click run -> queued-only` route kept identical `最后更新 / UPDATED` text before and after the click
    - the same controlled verification confirmed the route-level banner `回测任务已创建，进入排队` appears without mutating hero freshness
    - natural PM2 verification confirmed `/strategy/backtest?strategyId=101` still reaches the route and keeps the surrounding shell stable while this freshness boundary remains route-local

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-18-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-18-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-18-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-18-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-queued-task-freshness-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
