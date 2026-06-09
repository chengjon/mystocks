# Batch Audit Report: strategy-batch-09

## Scope
- Module: strategy
- Pages:
  - /strategy/signals
- Batch rationale: reuse existing `v1.43` store-refresh snapshot-provenance rules so the canonical strategy-signals route no longer lets shared realtime-store refresh failures overwrite the current verified signal snapshot or visible `REQ_ID` truth.

## Agent Summary

### route-inventory
- `/strategy/signals` remains the canonical routed signal workbench at `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`.
- The same owner continues to feed the `/watchlist/signals` consumer, so the current repair stays page-local and consumer-compatible.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest stale-refresh provenance on manual refresh.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the strategy-signals route treated a later resolved `success: false` refresh as if it had replaced the current verified signal snapshot, letting shared-store request provenance leak into the visible shell and risking row loss instead of preserving last-known-good truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: store-backed routed pages can correctly classify first-load unavailable truth and still mis-handle later refresh failures if hero request meta and visible rows are bound directly to shared-store `lastRequestId` or latest refresh payload instead of a page-local verified snapshot boundary.
- Occurrence basis:
  - `/strategy/signals` already had honest first-load placeholder handling from `strategy-batch-06`
  - the same route still reused shared-store refresh provenance and stale-state truth after later resolved `success: false` refreshes
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - `web/frontend/src/views/watchlist/Signals.vue`
- Suggested follow-up scope: continue applying `v1.43` to store-backed canonical routes that expose manual refresh plus visible request meta, especially where one routed owner also feeds sibling wrapper routes.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: stale-refresh request provenance > verified-row retention > first-load unavailable parity
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- shared-impact review items:
  - `web/frontend/src/views/watchlist/Signals.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `strategy-signals-issue-02`
- deferred items:
  - no new realtime-store redesign was approved for this batch

## Fix Summary
- Added page-local verified request-provenance retention to the canonical strategy-signals owner route.
- Added stale-refresh handling so a resolved `success: false` manual refresh now preserves verified signal rows and surfaces stale-state copy instead of clearing the routed shell.
- Strengthened routed component regression to cover resolved-envelope first-load failure and `success -> refresh fail` request-provenance retention.
- Strengthened the Phase 3 matrix with routed failure and stale-refresh signal assertions.
- Spot-checked the shared `/watchlist/signals` consumer to confirm the same owner repair preserved watchlist-specific route semantics.
- Reused existing `myweb-audit v1.43` without a new skill-version bump because the defect exactly matched the current store-refresh snapshot-provenance rule.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `strategy-signals-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-09`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate first-load failure and `success -> refresh fail` signal states
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts` -> passed `8/8`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `33` structurally valid tests including the strengthened `/strategy/signals` failure and stale-refresh assertions
  - targeted routed-page verification confirmed:
    - the browser-context first-load failure route rendered `REQ_ID: N/A`, `COUNT: --`, top-strip `-- / -- / -- / --`, and `策略信号加载失败 / strategy signals unavailable`
    - the same controlled verification confirmed the failed request id no longer appears anywhere in the visible route shell
    - browser-context `success -> refresh fail` verification confirmed the same route now keeps `REQ_ID: req-live-strategy-signals-success`, preserves `COUNT: 2` plus `2` visible signal rows, and shows `strategy signals refresh unavailable，当前仍显示上次成功同步的策略信号快照。`
    - natural PM2 verification confirmed `/strategy/signals` still loads and currently renders the honest live empty-state shell with a real request id plus `0 / 0 / 0 / 0`
    - natural PM2 verification confirmed the shared `/watchlist/signals` consumer still loads with `FOCUS: WATCHLIST`, a real request id, and zero `.artdeco-stat-change` nodes

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-09-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-09-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-09-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-09-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-signals-store-refresh-provenance-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
