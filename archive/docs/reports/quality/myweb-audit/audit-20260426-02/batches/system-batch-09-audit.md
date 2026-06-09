# Batch Audit Report: system-batch-09

## Scope
- Module: system
- Pages:
  - `/system/config`
- Batch rationale: close the remaining routed system-config active-tab request-provenance gap so visible header `REQ_ID / TIME` follows the currently displayed tab snapshot instead of the last sibling loader that finished

## Agent Summary

### route-inventory
- `/system/config` continues to resolve directly to the canonical `web/frontend/src/views/system/Settings.vue` entry.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond the tab-local header provenance issue.

### data-state-audit
- One high-severity issue cluster remained:
  - the routed page still treated shared `useArtDecoApi.lastRequestId/lastProcessTime` as if they always identified the visible tab snapshot, so concurrent sibling loads could overwrite the default-tab header and tab switches could surface the wrong request provenance

### visual-artdeco-audit
- No separate ArtDeco-only repair wave was required after the page-local provenance fix landed.

### responsive-a11y-audit
- No new desktop-breakpoint or a11y defect required a repair wave in this batch.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - multi-tab canonical pages can leak sibling loader provenance into a shared hero or header when the page binds directly to last-request metadata instead of tab-local verified snapshot metadata
  - default-tab drift and active-tab switching drift are two states of the same tab-local provenance cluster and should be audited together
- Occurrence basis:
  - `/system/config` could show general-settings or monitor request metadata while still displaying the source-config table on the default tab
  - the same route could fail to swap visible header provenance when the user switched between tab-local surfaces
- Shared component or token involved:
  - reviewed but not changed: `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
- Suggested follow-up scope:
  - continue checking canonical multi-tab routes where header `REQ`, `REQ_ID`, or `TIME` may still be bound to shared loader metadata instead of the visible tab slice

## Main Skill Decisions
- duplicates merged:
  - the default-tab overwrite and active-tab switching drift were consolidated into one request-provenance issue because both came from the same canonical page owner
- priority order applied:
  - visible active-tab provenance > generic shared loader metadata
- primary owners selected:
  - `web/frontend/src/views/system/Settings.vue`
- shared-impact review items:
  - `web/frontend/src/composables/artdeco/useArtDecoApi.ts` reviewed but not changed because the defect was fully page-local
- fixes applied:
  - `system-config-issue-03`
- deferred items: none

## Fix Summary
- Updated `/system/config` so the routed header now derives visible `REQ_ID / TIME` from tab-local verified metadata captured inside each loader closure.
- Added routed component regression coverage for both late-sibling overwrite and active-tab switching provenance.
- Added Phase 4 routed coverage to lock the same request-provenance rule on the canonical page.
- Reused existing `myweb-audit v1.43` request-provenance truth and `v1.34` multi-tab tab-slice truth without introducing a new skill version; project latest remains `v1.43`.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `system-config-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - any future shared-wrapper cleanup if more multi-tab request-provenance leaks accumulate beyond page-local owners

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-09`.

## Reasons Not Fixed
- `useArtDecoApi.ts` remains unchanged because the routed defect was fully fixable in the canonical page owner without altering shared wrapper semantics.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts` -> passed `6/6`
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `21/21`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `24` tests
  - `git diff --check -- web/frontend/src/views/system/Settings.vue web/frontend/src/views/system/__tests__/Settings.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-09-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-09-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-09-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-09-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/system-config-active-tab-request-provenance-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/system-batch-09-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Targeted routed-page verification confirmed:
  - the default live sources tab now keeps its own header provenance instead of drifting to sibling monitor or settings loaders
  - the same live route switches header provenance with the visible active tab:
    - sources -> `REQ_ID: 1fbe6533-391c-4a38-873b-02cd99737cdc`
    - monitor -> `REQ_ID: 0733171d-c701-4c61-bf28-4edcd3eb7c3a`
    - settings -> `REQ_ID: a9a9c44c-bfa8-4f81-8498-990eddd29626`
  - the default source tab still shows live table rows including `AKShare龙虎榜详情数据` and `akshare.stock_lhb_detail_em`
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-09-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-09-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-09-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-09-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-09-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict in the current dirty worktree (`risk_level: low`, `changed_files: 126`, `changed_count: 317`, `affected_count: 0`)

## Next Batch Plan
- Continue system and adjacent canonical multi-tab audits, especially where routed headers still bind to shared loader metadata instead of the currently visible tab-local snapshot.
