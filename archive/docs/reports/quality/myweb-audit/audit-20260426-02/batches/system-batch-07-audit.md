# Batch Audit Report: system-batch-07

## Scope
- Module: system
- Pages:
  - `/system/health`
- Batch rationale: close the remaining routed system-health request-provenance truth gap so hero `REQ_ID` follows the currently visible verified health snapshot instead of the last failed retry

## Agent Summary

### route-inventory
- `/system/health` continues to resolve directly to the canonical `web/frontend/src/views/system/Health.vue` entry.

### functional-audit
- No new routed interaction-path defect required a separate repair wave in this batch; the dominant routed issue was hero request provenance on `/system/health`.

### data-state-audit
- One high-severity issue cluster remained:
  - the routed page still treated `useArtDecoApi.lastRequestId` as if it always represented the visible health snapshot, so first-load failure and stale-refresh failure both produced misleading hero provenance

### visual-artdeco-audit
- No separate ArtDeco-only repair wave was required after the page-local request-provenance fix landed.

### responsive-a11y-audit
- No new desktop-breakpoint or a11y defect required a repair wave in this batch.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - routed hero request metadata can drift when a canonical page binds directly to `lastRequestId` instead of a verified-snapshot source
  - first-load failure and stale-refresh failure are two states of the same request-provenance cluster and should be audited together
- Occurrence basis:
  - `/system/health` showed `REQ_ID: req-health-first-fail` before any verified snapshot existed
  - the same route could swap hero request provenance to a failed retry even while the previous verified health snapshot remained visible
- Shared component or token involved:
  - reviewed but not changed: `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
- Suggested follow-up scope:
  - continue checking canonical routes that still bind `REQ`, `REQ_ID`, or `TRACE_ID` directly to "last request" instead of "currently visible verified snapshot"

## Main Skill Decisions
- duplicates merged:
  - first-load request-id leak and stale-refresh request-id overwrite were consolidated into one request-provenance issue because they both came from the same canonical page owner
- priority order applied:
  - verified-snapshot request provenance > generic refresh messaging
- primary owners selected:
  - `web/frontend/src/views/system/Health.vue`
- shared-impact review items:
  - `web/frontend/src/composables/artdeco/useArtDecoApi.ts` reviewed but not changed because the defect was page-local and did not require shared-wrapper semantics changes
- fixes applied:
  - `system-health-issue-02`
- deferred items: none

## Fix Summary
- Updated `/system/health` so hero `REQ_ID` is now derived from page-local verified snapshot truth instead of directly from `useArtDecoApi.lastRequestId`.
- Added component regression coverage for both first-load failure and refresh-after-success failure.
- Added routed Phase 4 coverage for the same request-provenance states.
- Reused existing `myweb-audit v1.41` request-provenance truth and `v1.39` browser-context interception guidance without introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `system-health-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - any future shared-wrapper cleanup if more canonical request-provenance leaks accumulate beyond page-local owners

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-07`.

## Reasons Not Fixed
- `useArtDecoApi.ts` remains unchanged because the routed defect was fully fixable in the canonical page owner without altering shared wrapper semantics.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/Health.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/API.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `17/17`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `14` tests
  - `git diff --check -- web/frontend/src/views/system/Health.vue web/frontend/src/views/system/__tests__/Health.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-07-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-07-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-07-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-07-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/system-health-request-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/system-batch-07-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Targeted routed-page verification confirmed:
  - controlled first-load failure now shows `REQ_ID: N/A` and `STATUS: UNKNOWN`
  - the same first-load failure no longer leaks `req-system-b07-first-fail` into the visible shell
  - controlled refresh-after-success failure now keeps `REQ_ID: req-system-b07-success` while the previous `mystocks-backend / 2.0.0` snapshot remains visible
  - natural PM2 verification still shows a live request id and `STATUS: HEALTHY`
  - actual PM2 requests reached `http://localhost:3020/api/health`, `http://localhost:3020/api/health/ready`, and `http://localhost:3020/api/health` with `200` on the natural path
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-07-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-07-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-07-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-07-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-07-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 77`, `changed_count: 260`, `affected_count: 0`)

## Next Batch Plan
- Continue system and adjacent canonical-route audits with the strengthened request-provenance rule, especially where hero metadata still binds directly to the last request instead of the currently visible verified snapshot.
