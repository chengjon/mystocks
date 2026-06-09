# Batch Audit Report: system-batch-02

## Scope
- Module: system
- Pages:
  - /system/api
- Batch rationale: close the routed system-api trace-truth gap and fold the request-trace truth rule back into the audit skill

## Agent Summary

### route-inventory
- `/system/api` continues to resolve directly to canonical `web/frontend/src/views/system/API.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity trace-truth defect remained: the telemetry page showed a fabricated local request ID instead of the real traced wrapper ID.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed observability pages that surface `REQ_ID` or trace metadata must treat the API wrapper as the source of truth instead of inventing page-local correlation placeholders.
- Occurrence basis:
  - `/system/api` previously rendered `REQ_ID: sys-*` even though `/api/health` returned a real wrapper `request_id`
- Shared component or token involved:
  - none; the repair stayed inside `API.vue` plus its canonical routed-page regression test
- Suggested follow-up scope: extend future routed telemetry audits to verify trace surfaces after both initial loads and secondary actions such as exports or manual refresh.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: trace truth > decorative request-id presence
- primary owners selected:
  - `web/frontend/src/views/system/API.vue`
- shared-impact review items: none
- fixes applied:
  - `system-api-issue-01`
- deferred items: none

## Fix Summary
- Removed the local synthetic `sys-*` fallback from the visible `REQ_ID` surface.
- Re-aligned the routed telemetry page to the existing `useArtDecoApi.lastRequestId` trace source of truth.
- Added canonical unit coverage for request-trace truth.
- Extended `myweb-audit` with a request-trace truth rule for future routed observability pages.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `system-api-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-02`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/API.spec.ts` -> passed `1/1`
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `5/5`
  - `timeout 180s npm run type-check` -> passed
  - targeted system-Chrome browser verification confirmed:
    - the initial telemetry header shows `REQ_ID: req-health-top`
    - clicking `导出报告` advances the header trace to `REQ_ID: req-health-detailed-top`
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-02-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-02-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-02-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-02-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus evidence for this batch remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the system-domain audit, apply the strengthened trace-truth and example-telemetry truth rules to any remaining routed observability pages that surface runtime metadata.
