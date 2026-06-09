# Batch Audit Report: system-batch-03

## Scope
- Module: system
- Pages:
  - /system/api
  - /system/health
- Batch rationale: close the routed system runtime-status truth gap and fold the middleware degradation rule back into the audit skill

## Agent Summary

### route-inventory
- `/system/api` continues to resolve directly to canonical `web/frontend/src/views/system/API.vue`.
- `/system/health` continues to resolve directly to canonical `web/frontend/src/views/system/Health.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- Two medium-severity runtime-status truth defects remained: both routed observability pages kept middleware labels in verified-running states even when the health probe was unavailable.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 2
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed observability pages that expose middleware or runtime-status labels must degrade those labels to explicit unverified states when the backing health probe is unavailable or unhealthy.
- Occurrence basis:
  - `/system/api` previously rendered `性能追踪 启用`, `统一响应 启用`, and `Redis 缓存 活跃` alongside a runtime failure message
  - `/system/health` previously rendered `Performance Tracing ENABLED`, `Unified Response ENABLED`, and `Redis Caching ACTIVE` alongside a runtime failure message
- Shared component or token involved:
  - none; the repairs stayed inside the two canonical routed pages plus their routed-page regression tests
- Suggested follow-up scope: extend future routed telemetry and health audits to inspect status badges, middleware rows, and operational labels whenever the page shows unavailable or unhealthy runtime states.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: runtime-status truth > decorative active-status copy
- primary owners selected:
  - `web/frontend/src/views/system/API.vue`
  - `web/frontend/src/views/system/Health.vue`
- shared-impact review items: none
- fixes applied:
  - `system-api-issue-02`
  - `system-health-issue-01`
- deferred items: none

## Fix Summary
- Replaced hardcoded active middleware labels with runtime-derived rows on both routed system observability pages.
- Added explicit pending-state styling for unverified middleware rows on the system API page family.
- Added routed-page regression coverage for the failed health-probe branch on both pages.
- Extended `myweb-audit` with a `v1.19` runtime-status truth rule so future audits catch this pattern earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `system-api-issue-02`
  - `system-health-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-03`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `7/7`
  - `timeout 180s npm run type-check` -> passed
  - targeted routed-page verification confirmed:
    - `/system/api` now shows the runtime failure message together with `性能追踪 未校验`, `统一响应 未校验`, and `Redis 缓存 未校验`
    - `/system/health` now shows the runtime failure message together with `Performance Tracing UNVERIFIED`, `Unified Response UNVERIFIED`, and `Redis Caching UNVERIFIED`
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-03-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-03-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-03-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-03-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 83`, `changed_count: 300`, `affected_count: 0`)

## Next Batch Plan
- If the user continues the system-domain audit, apply the strengthened runtime-status truth, trace-truth, and example-telemetry truth rules to any remaining routed observability pages that surface runtime metadata.
