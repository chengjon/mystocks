# Batch Audit Report: system-batch-10

## Scope
- Module: system
- Pages:
  - `/system/data`
- Batch rationale: close the remaining routed system-data request-provenance truth gap so visible `REQ_ID` follows the currently visible verified config snapshot instead of a fabricated `cfg-*` fallback or failed refresh request id

## Agent Summary

### route-inventory
- `/system/data` continues to resolve directly to the canonical `web/frontend/src/views/system/DataSource.vue` entry.

### functional-audit
- No new routed interaction-path defect required a separate repair wave in this batch; the dominant routed issue was visible request provenance on `/system/data`.

### data-state-audit
- One high-severity issue cluster remained:
  - the routed page still treated missing or failed transport metadata as if it could synthesize or replace visible config-snapshot provenance

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
  - routed hero and stats-strip request metadata can drift when a canonical page binds directly to transport request freshness instead of a verified-snapshot source
  - missing-request-id success and stale-refresh failure are two states of the same request-provenance cluster and should be audited together
- Occurrence basis:
  - `/system/data` could fabricate `cfg-*` when a verified config snapshot had no request metadata
  - the same route could swap visible request provenance to a failed refresh id even while the previous verified config rows remained visible
- Shared component or token involved:
  - reviewed but not changed: `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
  - reviewed but not changed: `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts`
- Suggested follow-up scope:
  - continue checking canonical routes that still bind `REQ`, `REQ_ID`, or `TRACE_ID` directly to transport freshness instead of the currently visible verified snapshot

## Main Skill Decisions
- duplicates merged:
  - fabricated `cfg-*` fallback and stale-refresh request-id overwrite were consolidated into one request-provenance issue because they both came from the same canonical page owner
- priority order applied:
  - verified-snapshot request provenance > generic refresh messaging
- primary owners selected:
  - `web/frontend/src/views/system/DataSource.vue`
- shared-impact review items:
  - `web/frontend/src/composables/artdeco/useArtDecoApi.ts` reviewed but not changed because the defect was page-local and did not require shared-wrapper semantics changes
  - `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts` reviewed but not changed because the defect was visible request provenance, not endpoint row normalization
- fixes applied:
  - `system-data-issue-02`
- deferred items: none

## Fix Summary
- Updated `/system/data` so visible `REQ_ID` is now derived from page-local verified config-snapshot truth instead of synthesizing `cfg-*` when request metadata is absent.
- Added component regression coverage for both missing-request-id success and refresh-after-success failure.
- Added routed Phase 4 coverage for the same request-provenance states.
- Reused existing `myweb-audit v1.45` route-provenance guidance without introducing a new skill version; project latest remains `v1.45`.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-10-repair-approval.yaml`
- Approved issue ids:
  - `system-data-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - any future shared-wrapper cleanup if more canonical request-provenance leaks accumulate beyond page-local owners

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-10`.

## Reasons Not Fixed
- `useArtDecoApi.ts` and `dataManagementData.ts` remain unchanged because the routed defect was fully fixable in the canonical page owner without altering shared wrapper or row-normalization semantics.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts` -> passed `4/4`
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/API.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `23/23`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `26` tests
  - targeted system-Chrome browser verification confirmed:
    - a verified config snapshot without request metadata now renders `REQ_ID: N/A` and `当前请求 N/A` instead of fabricating `cfg-*`
    - a controlled refresh-after-success failure now keeps `REQ_ID: req-live-system-data-success`, preserves visible `AKShare 行情 / TDX 实时深度` rows, and shows `获取数据源配置失败，当前仍显示上次成功同步的数据源配置快照。`
    - natural PM2 `/system/data` currently renders a real request id and `19` live config rows
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-10-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-10-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-10-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-10-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-10-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/system/DataSource.vue web/frontend/src/views/system/__tests__/DataSource.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-10-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-10-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-10-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-10-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/system-data-refresh-request-provenance-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/system-batch-10-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 126`, `changed_count: 317`, `affected_count: 0`)

## Next Batch Plan
- Continue system and adjacent canonical-route audits with the strengthened request-provenance rule, especially where visible metadata still binds directly to transport freshness instead of the currently visible verified snapshot.
