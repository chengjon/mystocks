# Batch Audit Report: system-batch-12

## Scope
- Module: system
- Pages:
  - `/system/data`
- Batch rationale: close the remaining routed `/system/data` unresolved-count truth gap so the visible config shell no longer presents `0 / 0` before any verified config snapshot exists

## Agent Summary

### route-inventory
- `/system/data` continues to resolve directly to the canonical `web/frontend/src/views/system/DataSource.vue` owner.

### functional-audit
- No new cross-route behavior change was required; the routed defect was isolated to the first-load count surfaces on `/system/data`.

### data-state-audit
- One high-severity issue remained:
  - config-dependent count cards and visible count meta rendered as if the page had already verified an empty config inventory

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
  - a canonical governance route can still leak unresolved first-load zero metrics even when provenance and runtime copy are already honest
- Occurrence basis:
  - `/system/data` source-config request remained unresolved
  - the stats strip and content meta still displayed `0 / 0` as if the route had a verified empty payload
- Shared component or token involved:
  - reviewed but not changed: `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
  - reviewed but not changed: `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts`
- Suggested follow-up scope:
  - continue checking top-level governance routes where count cards derive directly from empty arrays before the visible slice has any verified snapshot

## Main Skill Decisions
- duplicates merged:
  - unresolved-first-load zero counts on `/system/data` were kept as one page-local numeric-truth issue
- priority order applied:
  - verified config-snapshot truth > empty-array count convenience
- primary owners selected:
  - `web/frontend/src/views/system/DataSource.vue`
- shared-impact review items:
  - `useArtDecoApi.ts` reviewed but not changed because the defect was page-local stat gating, not shared request-wrapper provenance
  - `dataManagementData.ts` reviewed but not changed because config extraction was already correct once the route waited for a verified snapshot
- fixes applied:
  - `system-data-issue-03`
- deferred items: none

## Fix Summary
- Updated `/system/data` so config-dependent count cards and visible count meta now stay at `-- / --` until the route has a verified config snapshot.
- Preserved static write-capability truth, so the pending shell is now `-- / -- / ON / N/A` instead of a fake empty inventory.
- Added owner regression coverage for delayed first-load config truth.
- Added routed Phase 4 coverage for the same pending-first-load shell.
- Reused the stable `myweb-audit v2.0` route-truth families and updated the casebook plus coverage matrix instead of creating another micro-version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-12-repair-approval.yaml`
- Approved issue ids:
  - `system-data-issue-03`
- Deferred issue ids: none

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - repo default Playwright `chromium` runner succeeded for this proof
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `25/25`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Data keeps stats-strip counts unresolved while the first config snapshot is still pending"` -> passed `1/1`
  - controlled browser proof confirmed:
    - pending shell: `REQ_ID: N/A`
    - pending stat strip: `-- / -- / ON / N/A`
    - delayed success transition: `3 / 2 / ON / req-phase4-system-data-pending-late`
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue system and adjacent canonical-route audits, especially top-level routes where count cards or summary meta derive directly from empty arrays before the visible slice has any verified snapshot.
