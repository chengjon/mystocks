# Batch Audit Report: strategy-batch-19

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend selector-local action truth so the canonical strategy-backtest route no longer leaks one strategy's generated snapshot hint after the same routed page instance switches to a different `strategyId` without its own verified local context.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/strategy/Backtest.vue` and its downstream owner `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route-local generated snapshot surface was selector-blind, so the same routed page instance could switch from `strategyId=101` to `strategyId=202` and still show `最近快照：Momentum Alpha` even though strategy `202` had no verified generated snapshot of its own.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector- or query-scoped local action artifacts must be audited separately from transport refresh truth because locally generated hints, banners, and lightweight artifacts can leak across route switches even when request provenance and stale-refresh semantics are already correct.
- Occurrence basis:
  - `/strategy/backtest` already exposed selector-local generated snapshot feedback through the execution-action hint
  - the route reused a shared route-local generated snapshot surface after a same-instance query switch
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Suggested follow-up scope: continue applying `v1.67` to routed workbenches and detail pages that generate local snapshots, hint chips, or context banners tied to query-scoped selectors.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-local action truth > route-local generated-snapshot provenance
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` was reviewed as the routed wrapper and did not require a separate repair
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` inherits the safer selector-local action truth without a template rewrite
- fixes applied:
  - `strategy-backtest-issue-07`
- deferred items:
  - no strategy transport, global selector store, or backend backtest-schema redesign was approved for this batch

## Fix Summary
- Gated generated snapshot copy behind the current `selectedStrategyId` so only strategy-owned local artifacts remain visible after query changes.
- Restored neutral selector-local baseline copy when the new strategy query has no verified generated snapshot.
- Added owner regression coverage for the same-instance `101 -> 202` route-query switch.
- Added routed Phase 3 matrix coverage so `/strategy/backtest` clears the old generated snapshot hint in the browser path.
- Promoted `myweb-audit` to `v1.67` for selector-local action truth on query-scoped routed workbenches and details.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-19-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-07`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-19`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts and same-instance router-driven route switching were used to isolate the `generate snapshot -> switch strategyId` path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `22/22`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `44` structurally valid tests including the strengthened `/strategy/backtest` selector-local action assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route can generate a local snapshot for `strategyId=101`
    - the same routed page instance then reaches `当前策略上下文ID 202` with no leaked `最近快照：Momentum Alpha`
    - the visible execution-action hint returns to neutral selector-local baseline copy when the new strategy has no verified generated snapshot

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-19-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-19-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-19-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-19-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-selector-local-action-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
