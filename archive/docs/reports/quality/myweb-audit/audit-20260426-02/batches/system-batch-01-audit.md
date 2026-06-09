# Batch Audit Report: system-batch-01

## Scope
- Module: system
- Pages:
  - /system/config
- Batch rationale: close the routed system-config telemetry-truth gap and fold the example-telemetry rule back into the audit skill

## Agent Summary

### route-inventory
- `/system/config` continues to resolve directly to canonical `web/frontend/src/views/system/Settings.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity telemetry-truth defect remained: the monitor tab kept embedded example API metrics on the primary runtime surface after real monitor requests failed.

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
- Repeated issue pattern: routed monitor workbenches need explicit separation between live metrics, health-summary fallback, and fully unavailable monitor states.
- Occurrence basis:
  - `/system/config` previously kept embedded example API metric rows visible after both real monitor endpoints failed
- Shared component or token involved:
  - none; the repair stayed inside `Settings.vue` plus its routed-page regression tests
- Suggested follow-up scope: extend future routed system-page audits to verify that example runtime rows are never left on the main telemetry surface after request failure.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: telemetry truth > preserving monitor-table shape with fake metrics
- primary owners selected:
  - `web/frontend/src/views/system/Settings.vue`
- shared-impact review items: none
- fixes applied:
  - `system-config-issue-01`
- deferred items: none

## Fix Summary
- Removed the fallback path that left embedded example metric rows on the main monitor table after real monitor failures.
- Split the monitor state into `PENDING`, `REAL`, `SUMMARY`, and `UNAVAILABLE`.
- Added explicit summary-state and unavailable-state copy so health-summary fallback no longer impersonates API performance telemetry.
- Strengthened the canonical page test and kept the compatibility wrapper test aligned with the canonical routed behavior.
- Extended `myweb-audit` with an example-telemetry truth rule for future routed monitor pages.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-01-repair-approval.yaml`
- Approved issue ids:
  - `system-config-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-01`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `4/4`
  - `timeout 180s npm run type-check` -> passed
  - targeted system-Chrome browser verification confirmed:
    - summary fallback path shows `DATA: SUMMARY`, renders the `mystocks-backend` summary row, and no longer renders embedded example API metric rows
    - unavailable path shows `DATA: UNAVAILABLE`, renders `暂无系统监控接口数据。`, and no longer renders embedded example API metric rows
  - `pm2 list` had already confirmed `mystocks-backend` and `mystocks-frontend` online earlier in this audit run
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-01-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-01-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-01-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-01-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus evidence for this batch remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the system-domain audit, apply the strengthened example-telemetry truth rule to `/system/api` and other routed runtime-observability pages.
