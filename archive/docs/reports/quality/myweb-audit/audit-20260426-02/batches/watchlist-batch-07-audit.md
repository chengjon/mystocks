# Batch Audit Report: watchlist-batch-07

## Scope
- Module: watchlist
- Pages:
  - /watchlist/manage
- Batch rationale: close the canonical `/watchlist/manage` selector-pending primary-row truth defect so a new unresolved watchlist cannot inherit the previous verified stock rows under its active tab, reusing existing `myweb-audit v1.71` and `v1.66`.

## Agent Summary

### route-inventory
- `/watchlist/manage` remains the canonical routed watchlist-management entry at `web/frontend/src/views/watchlist/Manage.vue`, with the routed surface owner in `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

### functional-audit
- One high-severity routed interaction-path defect remained: selector-scoped stock rows and active-tab chrome could drift out of sync during a same-instance switch into a new unresolved watchlist.

### data-state-audit
- The route already retained stale rows correctly for same-selector refresh failures.
- What remained was selector-pending provenance truth: the new watchlist tab could become active before that watchlist had any verified stock rows of its own.

### visual-artdeco-audit
- No new visual-dominant defect required a repair wave in this batch.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped routes that already fixed stale-refresh truth can still leak false route truth if a new selector shell stays unresolved while the previous verified rows remain visible.
- Occurrence basis:
  - `/watchlist/manage` previously switched `.watchlist-tab.active` to `成长跟踪`
  - the same route previously kept the verified `核心组合` rows visible while the first `成长跟踪` stock request was still unresolved
- Shared component or token involved:
  - none
- Shared mapper involved:
  - none in the approved repair
- Suggested follow-up scope: continue applying `v1.71 + v1.66` to remaining selector-scoped routed pages where unresolved selector switches can outlive the previous verified primary rows.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-pending provenance cluster
- priority order applied: preserve selector-to-row truth > preserve pending-state honesty > preserve stale retention only for selectors that already verified their own rows
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- shared-impact review items: none
- fixes applied:
  - `watchlist-manage-issue-07`
- deferred items: none

## Fix Summary
- Added selector-scoped verified stock snapshots so the route no longer reuses the last route-global stock rows during a same-instance switch into an unresolved watchlist.
- Kept the summary strip in pending state while the new selector has no verified stock snapshot.
- Strengthened both the component regression and the Phase 2 route matrix with an explicit `success -> selector-pending` proof.
- Reused existing `myweb-audit v1.71` and `v1.66` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `watchlist-manage-issue-07`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `watchlist-batch-07`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/watchlist/__tests__/Manage.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/watchlist/__tests__/Manage.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/watchlist/__tests__/Screener.spec.ts` -> passed `11/11`
  - `timeout 180s npm run type-check` -> failed only on pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `30` structurally valid tests including the new `/watchlist/manage` selector-pending assertion
  - `git diff --check -- web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue web/frontend/src/views/watchlist/__tests__/Manage.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-07-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-07-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-07-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-07-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-manage-selector-pending-row-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-07-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - the controlled proof starts from a successful default `核心组合` snapshot
    - a same-instance click into unresolved `成长跟踪` leaves `.watchlist-tab.active` on `成长跟踪`
    - the same route keeps `rowCount: 0`, `statValues: 2 / -- / -- / --`, and does not leak `贵州茅台`
    - the visible state panel now reads `自选列表同步中`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
