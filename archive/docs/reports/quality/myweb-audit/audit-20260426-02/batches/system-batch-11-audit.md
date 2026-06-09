# Batch Audit Report: system-batch-11

## Scope
- Module: system
- Pages:
  - `/system/config`
- Batch rationale: close the default source-tab unresolved-count truth gap so the routed system-config shell no longer presents `0 / 0` before any verified source-config snapshot exists

## Agent Summary

### route-inventory
- `/system/config` continues to resolve directly to the canonical `web/frontend/src/views/system/Settings.vue` owner.

### functional-audit
- No new cross-route behavior change was required; the routed defect was isolated to the default `sources` shell on `/system/config`.

### data-state-audit
- One high-severity issue remained:
  - source-dependent count cards on the default active tab rendered as if the page had already verified an empty source inventory

### visual-artdeco-audit
- No separate ArtDeco-only repair wave was needed after count-card gating landed.

### responsive-a11y-audit
- No new responsive or a11y defect required a repair wave in this batch.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - a default active tab can still leak unresolved first-load zero metrics even when header provenance and runtime copy are already honest
- Occurrence basis:
  - `/system/config` defaulted to `sources`
  - source request remained unresolved
  - source-tab stat cards still displayed `0 / 0` as if the routed tab had a verified empty payload
- Shared component or token involved:
  - reviewed but not changed: `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
  - reviewed but not changed: `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts`
- Suggested follow-up scope:
  - continue checking default-active tab shells where one slice is still loading but count cards are computed directly from empty arrays

## Main Skill Decisions
- duplicates merged:
  - unresolved-first-load zero counts on the default source tab were kept as one page-local numeric-truth issue
- priority order applied:
  - verified source-snapshot truth > empty-array count convenience
- primary owners selected:
  - `web/frontend/src/views/system/Settings.vue`
- shared-impact review items:
  - `useArtDecoApi.ts` reviewed but not changed because the defect was page-local stat gating, not shared request-wrapper provenance
  - `dataManagementData.ts` reviewed but not changed because endpoint extraction was already correct once the route waited for a verified snapshot
- fixes applied:
  - `system-config-issue-03`
- deferred items: none

## Fix Summary
- Updated `/system/config` so source-dependent stat-card counts now stay at `-- / --` until the active source tab has a verified source-config snapshot.
- Preserved static write-capability truth, so the pending shell is now `-- / -- / ON / N/A` instead of a fake empty inventory.
- Added owner regression coverage for delayed first-load source truth.
- Added routed Phase 4 coverage for the same pending-first-load shell.
- Reused the stable `myweb-audit v2.0` route-truth families and updated the casebook plus coverage matrix instead of creating another micro-version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-11-repair-approval.yaml`
- Approved issue ids:
  - `system-config-issue-03`
- Deferred issue ids: none

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - repo default Playwright `chromium` runner succeeded for this proof
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts` -> passed `7/7`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Config keeps sources-tab counts unresolved while the first source-config snapshot is still pending"` -> passed `1/1`
  - controlled browser proof confirmed:
    - pending source-tab shell: `DATA: PENDING / REQ_ID: N/A / TIME: N/A`
    - pending stat strip: `-- / -- / ON / N/A`
    - delayed success transition: `3 / 2 / ON / req-phase4-config-late`
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue system and adjacent canonical-route audits, especially default-active tab shells where counts derive directly from empty arrays before the visible slice has any verified snapshot.
