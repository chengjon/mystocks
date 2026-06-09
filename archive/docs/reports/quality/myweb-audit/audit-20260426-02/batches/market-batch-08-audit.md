# Batch Audit Report: market-batch-08

## Scope
- Module: market
- Pages:
  - /market/realtime
- Batch rationale: close the canonical `/market/realtime` quote request-provenance defect so first-load failures and stale-refresh failures cannot leak failed `TRACE_ID` values into visible hero metadata or falsely imply a verified quote snapshot exists before the route has actually completed one, while reusing existing `myweb-audit v1.41`, `v1.39`, and `v1.38` rules

## Agent Summary

### route-inventory
- `/market/realtime` continues to resolve directly to canonical `web/frontend/src/views/market/Realtime.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed request-provenance cluster remained: the page treated the latest request id as if it always represented the currently visible verified quote snapshot, even when the latest request had failed before any verified sample existed or after a successful sample was already on screen.

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
- Repeated issue pattern: routed request metadata can leak failure-attempt provenance when a page-level request wrapper exposes the most recent request id rather than the request id that produced the currently visible verified quote snapshot.
- Occurrence basis:
  - `/market/realtime` previously rendered a failed first-load quote `request_id` before any verified snapshot existed
  - the same route previously claimed it had retained a previous verified sample when the first load had actually failed
  - the same route previously replaced the hero trace id with a failed refresh request id even though the visible quote rows still came from the earlier successful sync
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.41` request/envelope truth checks to remaining routes that expose top-level `REQ`, `REQ_ID`, `TRACE_ID`, or similar meta directly from `lastRequestId`, especially where stale-refresh warnings claim the page is preserving a previous successful snapshot.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed request-provenance cluster issue
- priority order applied: routed visible-snapshot truth > page-local containment
- primary owners selected:
  - `web/frontend/src/views/market/Realtime.vue`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `market-realtime-issue-02`
- deferred items: none

## Fix Summary
- Added a page-local verified-request-id state so the routed hero `TRACE_ID` now tracks the request that actually produced the visible quote snapshot.
- Added a no-verified-snapshot placeholder gate so hero `TRACE_ID / SAMPLE` metadata and the top summary strip degrade to `N/A / --` style placeholders before any verified quote snapshot exists.
- Added honest first-load error copy so the route no longer claims it preserved a previous verified sample when the first quote load failed.
- Strengthened the routed component regression with first-load failure and stale-refresh failure cases.
- Strengthened the Phase 1 matrix with explicit `/market/realtime` failure-provenance assertions.
- Reused `myweb-audit v1.41`, `v1.39`, and `v1.38` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `market-realtime-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `market-batch-08`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/market/__tests__/Realtime.spec.ts src/views/market/__tests__/LHB.spec.ts src/views/market/__tests__/Technical.spec.ts` -> passed `11/11`
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `21` structurally valid tests including the new `/market/realtime` request-provenance assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/market/Realtime.vue web/frontend/src/views/market/__tests__/Realtime.spec.ts web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-08-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-08-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-08-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/market-batch-08-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/market-realtime-request-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/market-batch-08-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception and `serviceWorkers: block`, failed first-load `/market/realtime` now renders `TRACE_ID: N/A`, `SAMPLE: --`, top stats `-- / -- / 核心蓝筹样本 / --`, and the no-verified-snapshot error copy
    - the same first-load failure route no longer leaks the failed request id anywhere in the visible page shell
    - a controlled success-then-fail refresh path now keeps `TRACE_ID: req-market-b08-success`, preserves `2` visible quote rows, and shows the stale-refresh error banner without leaking the failed retry id
    - natural PM2 verification still renders a live success shell such as `TRACE_ID: 3788958d-9594-42d3-b33f-e6a839a56ec2`, `13.0亿`, `20%`, and `5只`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-08-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-08-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-08-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/market-batch-08-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/market-batch-08-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue the market and adjacent runtime family on any remaining top-level request-metadata surfaces that still derive `REQ`, `REQ_ID`, or `TRACE_ID` directly from the latest transport attempt instead of the currently visible verified snapshot.
