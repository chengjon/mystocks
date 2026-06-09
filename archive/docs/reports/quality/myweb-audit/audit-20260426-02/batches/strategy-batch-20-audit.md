# Batch Audit Report: strategy-batch-20

## Scope
- Module: strategy
- Pages:
  - /strategy/signals
- Batch rationale: extend selector-scoped verified-snapshot truth so the canonical strategy-signals route no longer leaks one strategy query's rows, counts, or `REQ_ID` provenance after the same routed page instance switches to a different `strategyId` without its own verified signal snapshot.

## Agent Summary

### route-inventory
- `/strategy/signals` remains the canonical routed signal workbench through `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`, with `/watchlist/signals` reusing the same owner surface.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route's visible rows, top-strip counts, `COUNT`, and hero `REQ_ID` were guarded by one global verified-snapshot flag, so the same routed page instance could switch from `strategyId=101` to `strategyId=202` and still present the previous strategy's verified snapshot even though the new selector had never verified.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped row provenance alone is not enough on query-owned workbenches if the route still uses one global verified flag for every selector. Counts, request provenance, and visible rows must all stay keyed to the current selector's verified snapshot.
- Occurrence basis:
  - `/strategy/signals` already exposed selector-scoped hero and summary truth through `FOCUS`, `REQ_ID`, `COUNT`, top-strip totals, and the visible signal timeline
  - the route allowed a same-instance query switch without resetting those surfaces to current-selector placeholder truth
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Suggested follow-up scope: continue applying `v1.68` to query-scoped routed workbenches and detail pages whose visible rows, counts, or request meta are derived from selector-owned snapshots.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: selector-scoped verified-snapshot truth > selector-scoped row provenance > stale-refresh retention
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- shared-impact review items:
  - `web/frontend/src/views/watchlist/Signals.vue` was reviewed as the shared consumer and inherits the safer owner behavior without a separate repair
- fixes applied:
  - `strategy-signals-issue-03`
- deferred items:
  - no shared realtime-store redesign or query-parser abstraction change was approved for this batch

## Fix Summary
- Added selector-keyed verified-snapshot tracking inside the canonical strategy-signals owner route.
- Rebased hero `REQ_ID`, `COUNT`, top-strip tallies, visible rows, and error-shell decisions on the current selector's verified snapshot.
- Preserved same-selector stale-refresh retention while clearing old snapshot truth after a same-instance selector switch without a new verified snapshot.
- Added owner regression coverage and strengthened routed Phase 3 matrix coverage for the `strategyId=101 -> 202` query-switch path.
- Promoted `myweb-audit` to `v1.68` for selector-scoped verified-snapshot truth on query-owned workbenches and details.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-20-repair-approval.yaml`
- Approved issue ids:
  - `strategy-signals-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-20`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the same-instance `strategyId=101 -> 202` selector-switch path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts` -> passed `25/25`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `45` structurally valid tests including the strengthened `/strategy/signals` selector-switch assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated route first renders `FOCUS: 101 / REQ_ID: req-live-strategy-signals-101 / COUNT: 2`
    - the same routed page instance then reaches `FOCUS: 202 / REQ_ID: N/A / COUNT: --`
    - the visible route shows zero signal rows and `strategy 202 signals unavailable`
    - old `贵州茅台` and `比亚迪` rows no longer leak after the selector switch

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-20-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-20-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-20-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-20-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-signals-selector-snapshot-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
