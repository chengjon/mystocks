# Batch Audit Report: trade-batch-10

## Scope
- Module: trade
- Pages:
  - /trade/positions
- Batch rationale: reuse existing `v1.43` store-refresh snapshot-provenance rules so the canonical trade-positions route no longer lets transport refresh failures overwrite the current verified holdings snapshot or visible `REQ_ID / TIME` truth.

## Agent Summary

### route-inventory
- `/trade/positions` remains the canonical routed holdings workbench at `web/frontend/src/views/trade/Center.vue`.
- The same owner continues to feed the `/strategy/pos` consumer, so the current repair stays page-local and consumer-compatible.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest stale-refresh provenance on manual refresh.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the trade-positions route treated a later resolved `success: false` refresh as if it had replaced the current verified holdings snapshot, letting transport request provenance leak into the visible shell and clearing rows instead of preserving last-known-good truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: transport-backed routed pages can correctly classify first-load unavailable truth and still mis-handle later refresh failures if hero request meta and visible rows are bound directly to `useArtDecoApi`'s latest request metadata instead of a page-local verified snapshot boundary.
- Occurrence basis:
  - `/trade/positions` already had honest first-load placeholder handling from earlier numeric-truth work
  - the same route still reused latest transport provenance and stale-state truth after later resolved `success: false` refreshes
- Shared component or token involved:
  - `web/frontend/src/views/trade/Center.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- Suggested follow-up scope: continue applying `v1.43` to transport-backed canonical routes that expose manual refresh plus visible request meta, especially where one routed owner also feeds sibling wrapper routes.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: stale-refresh request provenance > verified-row retention > first-load unavailable parity
- primary owners selected:
  - `web/frontend/src/views/trade/Center.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `trade-positions-issue-02`
- deferred items:
  - no new shared `useArtDecoApi` redesign was approved for this batch

## Fix Summary
- Added page-local verified request and process metadata retention to the canonical trade-positions route.
- Added stale-refresh handling so a resolved `success: false` manual refresh now preserves verified holdings rows and surfaces stale-state copy instead of clearing the routed shell.
- Strengthened routed component regression to cover failed first-load request-id suppression and `success -> refresh fail` request-provenance retention.
- Strengthened the Phase 3 matrix with routed failure and stale-refresh holdings assertions.
- Spot-checked the shared `/strategy/pos` consumer to confirm the same owner repair preserved route-family behavior.
- Reused existing `myweb-audit v1.43` without a new skill-version bump because the defect exactly matched the current store-refresh snapshot-provenance rule.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-10-repair-approval.yaml`
- Approved issue ids:
  - `trade-positions-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-10`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate first-load failure and `success -> refresh fail` positions states
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `23/23`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `35` structurally valid tests including the strengthened `/trade/positions` failure and stale-refresh assertions
  - targeted routed-page verification confirmed:
    - the browser-context first-load failure route rendered `REQ_ID: N/A`, `TIME: N/A`, `ROWS: --`, top-strip `-- / -- / -- / --`, and `MARKET_VALUE: -- / TOTAL_PNL: --`
    - the same controlled verification confirmed the failed request id no longer appears anywhere in the visible route shell
    - browser-context `success -> refresh fail` verification confirmed the same route now keeps `REQ_ID: req-live-trade-positions-success`, `TIME: 31.00ms`, `ROWS: 2`, preserves `2` visible holdings rows, and shows `positions refresh unavailable，当前仍显示上次成功同步的持仓快照。`
    - natural PM2 verification confirmed `/trade/positions` still loads and currently renders the honest live empty-state shell with a real request id plus `0 / 0 / ¥0 / --`
    - natural PM2 verification confirmed the shared `/strategy/pos` consumer still loads with the same honest zero-row empty state

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-10-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-10-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-10-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-10-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trade-positions-store-refresh-provenance-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
