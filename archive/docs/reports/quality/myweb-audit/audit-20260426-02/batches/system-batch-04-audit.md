# Batch Audit Report: system-batch-04

## Scope
- Module: system
- Pages:
  - /system/data
- Batch rationale: close the routed system-data payload-normalization truth gap and fold the endpoint-level fallback rule back into the audit skill

## Agent Summary

### route-inventory
- `/system/data` continues to resolve directly to canonical `web/frontend/src/views/system/DataSource.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity payload-normalization truth defect remained: live endpoint rows could collapse into repeated source-level placeholders when the routed page ignored `description` and `endpoint_name` fields from the live contract.

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
- Repeated issue pattern: endpoint-oriented config or registry pages must preserve endpoint-level identity even when the live contract omits friendly `name`, `endpoint`, or `url` fields.
- Occurrence basis:
  - `/system/data` previously rendered repeated rows like `akshare / N/A` even though the live payload exposed endpoint-level `description` and `endpoint_name`
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts`
- Suggested follow-up scope: extend future config, catalog, and registry audits to inspect whether endpoint-level identity is preserved on the primary live data surface when only description or identifier fields are present.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: payload-normalization truth > generic source placeholder rendering
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts`
- shared-impact review items: none
- fixes applied:
  - `system-data-issue-01`
- deferred items: none

## Fix Summary
- Updated the shared system-data mapper so live `description` is used as the row name before falling back to `source_name`.
- Updated the endpoint column fallback to use `endpoint_name` when the live contract omits `endpoint` and `url`.
- Added canonical routed-page and mapper regression coverage for the live payload shape that previously collapsed into repeated `akshare / N/A` rows.
- Extended `myweb-audit` with a `v1.20` payload-normalization truth rule so future audits catch this pattern earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `system-data-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoDataManagement.spec.ts src/api/__tests__/monitoringApi.spec.ts tests/unit/views/system-wrapper-retention.spec.ts` -> passed `8/8`
  - `node --test src/views/artdeco-pages/system-tabs/__node_tests__/dataManagementData.test.ts src/views/artdeco-pages/system-tabs/__node_tests__/dataManagementCapabilities.test.ts` -> passed `5/5`
  - `timeout 180s npm run type-check` -> passed
  - targeted routed-page verification confirmed:
    - a fresh authenticated page deep-link to `/system/data` now shows a real request id in the hero meta and 19 live rows
    - `/system/data` now renders endpoint-level descriptions and `endpoint_name` values in the visible configuration rows instead of collapsing them into repeated `source_name / N/A` rows
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
  - same-tab automation navigation could show the global readiness fallback banner with `signal is aborted without reason`, but a fresh authenticated page deep-link to `/system/data` completed with healthy readiness and live endpoint rows, so the banner was treated as automation-environment evidence rather than a route defect
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-04-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-04-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-04-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-04-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the system-domain audit, apply the strengthened payload-normalization truth, trace-truth, example-telemetry truth, and runtime-status truth rules to the remaining routed system pages and any related registry or catalog surfaces.
