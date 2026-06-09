# Batch Audit Report: trade-batch-09

## Scope
- Module: trade
- Pages:
  - /trade/signals
- Batch rationale: apply the new `v1.43` store-refresh snapshot-provenance rule so the canonical trade-signals route no longer lets shared realtime-store refresh failures overwrite the current verified signal snapshot or visible `REQ_ID / TIME` truth.

## Agent Summary

### route-inventory
- `/trade/signals` remains the canonical routed signal-execution workbench at `web/frontend/src/views/trade/Signals.vue`.
- The owner route is still reused by the trade-facing ArtDeco signal wrapper family, so the current repair keeps embedded consumers aligned without widening into shared store or shared wrapper redesign.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest stale-refresh provenance on manual refresh.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the trade-signals route treated a later resolved `success: false` refresh as if it had replaced the current verified signal snapshot, clearing rows and wiping request provenance instead of preserving last-known-good truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: store-backed routed pages can correctly classify first-load unavailable truth and still mis-handle later refresh failures if hero request meta and visible rows are bound directly to shared-store `lastRequestId`, `lastProcessTime`, or latest refresh payload instead of a page-local verified snapshot boundary.
- Occurrence basis:
  - `/trade/signals` previously rendered first-load unavailable truth honestly
  - the same route still cleared rows and lost its verified `REQ_ID / TIME` when a later manual refresh resolved as `success: false`
- Shared component or token involved:
  - `web/frontend/src/views/trade/Signals.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`
- Suggested follow-up scope: continue applying `v1.43` to store-backed canonical routes that expose manual refresh plus visible request meta, especially where shared realtime stores own both last-request metadata and current row arrays.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: stale-refresh request provenance > verified-row retention > first-load unavailable parity
- primary owners selected:
  - `web/frontend/src/views/trade/Signals.vue`
- shared-impact review items:
  - `ArtDecoSignalsView.vue` was reviewed as a route-family consumer but did not require a separate fix
- fixes applied:
  - `trade-signals-issue-03`
- deferred items:
  - no new shared-store redesign was approved for this batch

## Fix Summary
- Added page-local verified request and process metadata retention for the canonical trade-signals route.
- Added stale-refresh handling so a resolved `success: false` manual refresh now preserves verified signal rows and surfaces stale-state copy instead of clearing the routed shell.
- Strengthened routed component regression to cover `success -> refresh fail` request-provenance retention.
- Strengthened the Phase 3 matrix with a routed stale-refresh signal assertion.
- Added `myweb-audit v1.43` so future store-backed page audits must explicitly verify refresh-failure snapshot retention after prior success.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `trade-signals-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-09`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate first-load failure and `success -> refresh fail` signal states
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/History.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `19/19`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `31` structurally valid tests including the strengthened `/trade/signals` stale-refresh provenance assertion
  - targeted routed-page verification confirmed:
    - the browser-context first-load failure route rendered `COUNT: --`, `DATA: UNAVAILABLE`, `REQ_ID: N/A`, `TIME: N/A`, top-strip `-- / -- / -- / --`, and `trade signals unavailable，当前显示空状态。`
    - the same controlled verification confirmed the failed request id no longer appears anywhere in the visible route shell
    - the browser-context success-then-refresh-fail route rendered `COUNT: 3`, `DATA: REAL`, `REQ_ID: REQ-LIVE-TRADE-SIGNALS-SUCCESS`, `TIME: 42.00MS`, preserved `3` signal rows, and displayed `trade signals refresh unavailable，当前仍显示上次成功同步的交易信号快照。`
    - natural PM2 `/trade/signals` rendered an honest live empty-state shell with a real request id plus `0 / 0 / 0 / 未校验`
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Apply `v1.43` to the next store-backed canonical route that still exposes manual refresh plus visible request meta and row surfaces from shared request wrappers.
