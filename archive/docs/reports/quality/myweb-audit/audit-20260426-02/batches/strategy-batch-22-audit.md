# Batch Audit Report: strategy-batch-22

## Scope
- Module: strategy
- Pages:
  - /strategy/opt
- Batch rationale: extend the existing selector-scoped verified-snapshot rule to the canonical strategy-optimization route so same-instance `strategyId` query switches no longer leak the earlier optimization request provenance, summary tallies, or visible rows into a new selector without its own verified snapshot.

## Agent Summary

### route-inventory
- `/strategy/opt` remains the canonical routed optimization workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`, with `web/frontend/src/views/strategy/Optimization.vue` acting as the wrapper shell.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible `REQ_ID / PROCESS`, `VISIBLE / TOTAL`, top-strip tallies, and optimization rows were guarded by one global verified-snapshot flag, so the same routed page instance could switch from `strategyId=101` to `strategyId=202` and still present the earlier strategy's verified snapshot even though the new selector had never verified.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped request provenance and row truth are still vulnerable if summary tallies are guarded by one route-local verified flag instead of the current selector's verified snapshot.
- Occurrence basis:
  - `/strategy/opt` already exposed selector-scoped hero and summary truth through `FOCUS`, `REQ_ID / PROCESS`, `VISIBLE / TOTAL`, the top-strip candidate tallies, and the visible optimization rows
  - the route allowed a same-instance query switch without resetting those surfaces to current-selector placeholder truth
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- Suggested follow-up scope: continue applying `v1.68` to query-scoped routed workbenches and detail pages whose hero meta, summary tallies, or visible rows are derived from selector-owned snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-scoped verified-snapshot truth > request-provenance retention > stale-refresh retention
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Optimization.vue` and `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` were reviewed as wrapper consumers and inherit the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-opt-issue-03`
- deferred items:
  - no shared API, stat-card, or cross-tab selector redesign was approved for this batch

## Fix Summary
- Added selector-keyed verified-strategy tracking inside the canonical strategy-optimization owner route.
- Rebased hero `REQ_ID / PROCESS`, `VISIBLE / TOTAL`, top-strip tallies, and visible optimization rows on the current selector's verified snapshot.
- Preserved same-selector stale-refresh retention while clearing old snapshot truth after a same-instance selector switch without a new verified optimization snapshot.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch path.
- Reused existing `myweb-audit v1.68` for selector-scoped verified-snapshot truth on query-owned routed workbenches.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-22-repair-approval.yaml`
- Approved issue ids:
  - `strategy-opt-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-22`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` selector-switch path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` -> passed `27/27`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `47` structurally valid tests including the strengthened `/strategy/opt` selector-switch assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first renders `FOCUS: ID 101 / REQ_ID: req-live-strategy-opt-success / PROCESS: 42.00`
    - the same routed page instance then reaches `FOCUS: ID 202 / REQ_ID: N/A / PROCESS: N/A`
    - the visible route shows `VISIBLE: -- / TOTAL: --`, `-- / -- / -- / ID 202`, zero optimization rows, and `未找到策略 202 的优化候选，请返回策略管理页重试。`
    - old `Momentum Alpha` content no longer leaks after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-22-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-22-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-22-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-22-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-optimization-selector-snapshot-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
