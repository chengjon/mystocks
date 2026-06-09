# Batch Audit Report: watchlist-batch-04

## Scope
- Module: watchlist
- Pages:
  - /watchlist/screener
- Batch rationale: close the canonical `/watchlist/screener` stock-universe request-provenance and resolved-failure-envelope truth defect so `success:false` payloads cannot be swallowed as empty-universe success and failed request ids cannot leak into visible hero metadata before or after a verified stock-universe snapshot exists, while reusing existing `myweb-audit v1.40`, `v1.41`, and `v1.39` rules.

## Agent Summary

### route-inventory
- `/watchlist/screener` remains the canonical routed screener entry at `web/frontend/src/views/watchlist/Screener.vue`, with the routed surface owner in `web/frontend/src/views/stocks/Screener.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed truth cluster remained: the route conflated resolved failure envelopes, latest request metadata, and visible verified stock-universe truth, so first-load failure and stale-refresh failure could both misrepresent what the page had actually verified.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed pages backed by direct transports or stores can treat resolved `success:false` envelopes and latest request ids as if they were verified visible-snapshot truth unless the page explicitly gates both failure classification and request provenance locally.
- Occurrence basis:
  - `/watchlist/screener` previously treated a resolved `success:false` first-load payload as empty-universe success
  - the same route previously leaked failed first-load or refresh `request_id` values into hero metadata even when no verified stock-universe snapshot existed or when the visible rows still belonged to an earlier success
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.40 + v1.41 + v1.39` to remaining routes that expose top-level `REQ`, `REQ_ID`, or similar shell meta while also consuming transports that may resolve failures into ordinary payload envelopes.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed request-and-envelope truth issue
- priority order applied: visible-snapshot truth > explicit failure-envelope classification > page-local containment
- primary owners selected:
  - `web/frontend/src/views/stocks/Screener.vue`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `watchlist-screener-issue-02`
- deferred items: none

## Fix Summary
- Added page-local resolved-envelope failure classification so `success:false` stock-universe payloads are handled as unavailable truth instead of empty-universe success.
- Added page-local verified-request provenance so hero `REQ` now tracks the request that produced the currently visible verified stock-universe snapshot.
- Preserved verified rows during stale-refresh failure and surfaced a warning banner rather than dropping the visible universe.
- Strengthened the routed component regression and the Phase 2 matrix with explicit first-load failure and refresh-after-success failure paths.
- Reused `myweb-audit v1.40` envelope-truth, `v1.41` request-provenance truth, and `v1.39` browser-context interception guidance without a new skill-version bump.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `watchlist-screener-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `watchlist-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/watchlist/__tests__/Screener.spec.ts` -> passed `4/4`
  - `npx vitest run src/views/watchlist/__tests__/Screener.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/watchlist/__tests__/Manage.spec.ts` -> passed `7/7`
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `21` structurally valid tests including the new `/watchlist/screener` request-and-envelope truth assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/stocks/Screener.vue web/frontend/src/views/watchlist/__tests__/Screener.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-04-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-04-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-04-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-04-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-screener-request-and-envelope-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-04-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception on `**/v1/data/stocks/basic**`, resolved first-load failure now renders `REQ: N/A`, `UNIVERSE: --`, top-strip `-- / -- / -- / --`, and the visible `股票池加载失败` state
    - the same first-load failure route no longer leaks the failed request id anywhere in the visible page shell and no longer falls through to the fake empty-universe copy
    - a controlled success-then-fail refresh path now keeps `REQ: req-watchlist-b04-success`, preserves visible rows such as `贵州茅台`, and shows the stale-refresh warning banner without leaking the failed retry id
    - the natural PM2 success path now renders a real request id, `UNIVERSE: 200`, and live summary values `200 / 200 / 95 / 0` while `/api/v1/data/stocks/basic?limit=200` returns `200`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-04-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-04-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-04-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-04-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-04-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue the watchlist and adjacent route families on any remaining shells that still bind top-level `REQ`, `REQ_ID`, or failure-state copy directly to the latest transport attempt instead of the currently visible verified snapshot truth.
