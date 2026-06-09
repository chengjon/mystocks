# Batch Audit Report: risk-batch-12

## Scope
- Module: risk
- Pages:
  - /risk/management
- Batch rationale: close the canonical `/risk/management` initial freshness placeholder truth gap so loading and first-load failure shells no longer seed footer `最后一次更新` from the local current clock before any verified positions snapshot exists

## Agent Summary

### route-inventory
- `/risk/management` remains the canonical routed risk-management workspace at `web/frontend/src/views/risk/Center.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`, so the current repair stays page-local and consumer-compatible.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond honest initial freshness presentation on the footer surface.

### data-state-audit
- One high-severity routed freshness defect remained: the page treated the local current clock as if it were already verified route metadata, even while the route was still in loading or first-load failure state.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed pages can correctly delay their request-id or content-shell data and still leak false freshness truth if a footer or sibling meta surface is initialized from the local current clock before the first verified snapshot exists.
- Occurrence basis:
  - `/risk/management` initialized `lastUpdateTime` from `new Date().toLocaleString()`
  - `ArtDecoPageTemplate` keeps the footer visible during loading and first-load failure shells, so the false freshness value remained user-visible before any verified positions snapshot existed
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.47 + v1.46 + v1.43` checks to routed pages that expose footer or hero freshness metadata before first verified snapshot truth exists.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed initial freshness placeholder-truth issue
- priority order applied: visible freshness truth > page-local containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/views/risk/Center.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-management-issue-12`
- deferred items: none

## Fix Summary
- Changed the canonical risk-management owner to initialize footer freshness as `--` instead of local current time.
- Preserved the existing success path so footer freshness still advances after a verified positions snapshot arrives.
- Added an owner-level regression that pins both the loading shell and the first-load failure shell against local-current-time freshness leakage.
- Added a Phase 4 routed assertion that guards the same footer truth on `/risk/management`.
- Reused existing `myweb-audit v1.47` without a new skill-version bump because the defect exactly matched the current initial-freshness placeholder rule.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-12-repair-approval.yaml`
- Approved issue ids:
  - `risk-management-issue-12`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-12`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts` -> passed `2/2`
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts tests/unit/views/risk-center-template-retention.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `25/25`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `27` structurally valid tests including the new `/risk/management` footer-freshness assertion
  - targeted system-Chrome browser verification confirmed:
    - controlled first-load failure now renders footer `最后一次更新：--`
    - the same controlled failure remains on `/risk/management` and keeps the footer visible under the error shell
    - natural PM2 `/risk/management` still reaches the route, issues `200` requests to `/api/health/ready`, `/api/health`, and `/api/v1/trade/positions`, renders a real request id, and advances footer freshness to a real time after success
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-12-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-12-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-12-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-12-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-12-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/risk/Center.vue web/frontend/src/views/risk/__tests__/Center.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-12-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-12-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-12-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-12-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-management-initial-freshness-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-12-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 126`, `changed_count: 317`, and `affected_count: 0`

## Next Batch Plan
- Continue applying `v1.47 + v1.46 + v1.43` to routed pages that still expose freshness metadata before the first verified snapshot exists.
