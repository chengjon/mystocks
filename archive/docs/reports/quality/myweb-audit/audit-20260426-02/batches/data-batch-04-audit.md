# Batch Audit Report: data-batch-04

## Scope
- Module: data
- Pages:
  - /data/concept
- Batch rationale: close the routed concept refresh-truth gap and fold the stale-refresh pattern back into the audit skill

## Agent Summary

### route-inventory
- `/data/concept` continues to resolve directly to canonical `web/frontend/src/views/data/Concepts.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity refresh-truth defect remained: after a successful first load, the page lacked an explicit stale-data warning contract for manual refresh failure.

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
- Repeated issue pattern: single-request routed pages also need explicit stale-refresh handling; otherwise a failed manual refresh leaves users unsure whether visible data is current.
- Occurrence basis:
  - `/data/concept` previously had no `last-known-good data is still visible` contract after refresh failure
- Shared component or token involved:
  - none; the defect and repair were page-local to `web/frontend/src/views/data/Concepts.vue`
- Suggested follow-up scope: continue auditing routed workbenches for both partial-success and stale-refresh truth gaps rather than treating those as isolated page quirks.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: explicit stale-refresh truth > generic refresh failure ambiguity
- primary owners selected:
  - `web/frontend/src/views/data/Concepts.vue`
- shared-impact review items: none
- fixes applied:
  - `data-concept-issue-01`
- deferred items: none

## Fix Summary
- Added a page-local stale-refresh warning state for `/data/concept`.
- Preserved the last successful concept rows when a manual refresh fails.
- Added both unit-level and browser-matrix regression coverage for the success-then-refresh-fail path.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `data-concept-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/views/data-concept-refresh-fallback.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/config/data-route-canonical-paths.spec.ts tests/unit/config/domain-body-migration-ownership.spec.ts` -> passed `15/15`
  - `timeout 180s npm run type-check` -> passed
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
  - targeted system-Chrome browser verification confirmed `/data/concept` shows `部分刷新失败`, keeps the `机器人` row visible, and labels the page `刷新异常` after a forced refresh failure
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-04-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-04-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-04-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-04-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus evidence for this batch remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the data-domain audit, use the strengthened stale-refresh rule to probe the next routed page where successful first loads and failed manual refreshes may still be conflated.
