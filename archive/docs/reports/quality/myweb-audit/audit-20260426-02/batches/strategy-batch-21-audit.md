# Batch Audit Report: strategy-batch-21

## Scope
- Module: strategy
- Pages:
  - /strategy/parameters
- Batch rationale: extend the existing selector-scoped verified-snapshot rule to the canonical strategy-parameters route so same-instance `strategyId` query switches no longer leak the earlier parameter request provenance, top-strip tallies, or visible cards into a new selector without its own verified snapshot.

## Agent Summary

### route-inventory
- `/strategy/parameters` remains the canonical routed parameter workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`, with `web/frontend/src/views/strategy/Parameters.vue` acting as the wrapper shell.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible `REQ_ID / PROCESS`, top-strip tallies, and parameter cards were guarded by one global verified-snapshot flag, so the same routed page instance could switch from `strategyId=101` to `strategyId=202` and still present the earlier strategy's verified snapshot even though the new selector had never verified.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped request provenance and row truth are still vulnerable if summary tallies and visible cards are guarded by one route-local verified flag instead of the current selector's verified snapshot.
- Occurrence basis:
  - `/strategy/parameters` already exposed selector-scoped hero and summary truth through `FOCUS`, `REQ_ID`, `PROCESS`, the top-strip parameter tallies, and the visible parameter cards
  - the route allowed a same-instance query switch without resetting those surfaces to current-selector placeholder truth
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- Suggested follow-up scope: continue applying `v1.68` to query-scoped routed workbenches and detail pages whose hero meta, summary tallies, or visible rows are derived from selector-owned snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-scoped verified-snapshot truth > request-provenance retention > stale-refresh retention
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Parameters.vue` was reviewed as the wrapper consumer and inherits the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-parameters-issue-03`
- deferred items:
  - no shared `useArtDecoApi` or cross-tab selector redesign was approved for this batch

## Fix Summary
- Added selector-keyed verified-strategy tracking inside the canonical strategy-parameters owner route.
- Rebased hero `REQ_ID / PROCESS`, top-strip tallies, and visible parameter cards on the current selector's verified snapshot.
- Preserved same-selector stale-refresh retention while clearing old snapshot truth after a same-instance selector switch without a new verified parameter snapshot.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch path.
- Reused existing `myweb-audit v1.68` for selector-scoped verified-snapshot truth on query-owned routed workbenches.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-21-repair-approval.yaml`
- Approved issue ids:
  - `strategy-parameters-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-21`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` selector-switch path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts` -> passed `26/26`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `46` structurally valid tests including the strengthened `/strategy/parameters` selector-switch assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first renders `FOCUS: 101 / REQ_ID: req-live-strategy-parameters-success / PROCESS: 36.00 ms`
    - the same routed page instance then reaches `FOCUS: 202 / REQ_ID: N/A / PROCESS: N/A ms`
    - the visible route shows `-- / -- / -- / 202`, zero parameter cards, and `未找到策略 202 的参数配置，请返回策略管理页重试。`
    - old `Momentum Alpha` content no longer leaks after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-21-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-21-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-21-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-21-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-parameters-selector-snapshot-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
