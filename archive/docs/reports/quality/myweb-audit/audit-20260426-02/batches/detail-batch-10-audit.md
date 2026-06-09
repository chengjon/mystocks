# Batch Audit Report: detail-batch-10

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` selector-pending primary-row truth gap so a new unresolved symbol shell cannot keep the previous verified announcement rows visible, reusing existing `myweb-audit v1.71` and `v1.66`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail page at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the primary announcement list was selector-scoped for success and explicit failure, but not for unresolved first-load selector switches.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped canonical detail routes must clear the previous selector rows as soon as the route/entity shell switches to a new selector that has not yet verified its own primary snapshot.
- Occurrence basis:
  - `/detail/news/:symbol` let `/detail/news/000001` inherit the verified `600519` primary announcement row while the first `000001` list request remained unresolved
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.71` and `v1.66` to other selector-driven detail pages where unresolved first loads can leave the previous entity rows visible.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-pending row issue
- priority order applied: current route selector truth > primary list row provenance > stale retention only for the same verified selector
- primary owners selected:
  - `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-10`
- deferred items: none

## Fix Summary
- Updated the route-owned announcement monitor composable so the primary announcement list synchronizes selector-scoped snapshots at fetch start.
- Ensured a new unresolved symbol clears the previous verified rows immediately instead of waiting for the new request to settle.
- Added owner regressions plus a Phase 4 routed browser assertion for selector-switch pending-state leakage.
- Reused existing `myweb-audit v1.71` and `v1.66` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-10-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-10`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-10`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome` after authenticating through the natural login gate
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `15/15`
  - `timeout 180s npm run type-check` -> failed due to pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `34` tests including the new detail/news selector-pending assertion
  - targeted system-Chrome browser verification confirmed:
    - authenticated `/detail/news/600519` first shows `2026 年第一季度经营数据公告`
    - same-instance `/detail/news/000001` then reaches `当前详情标的: 000001`
    - the same controlled route-switch path no longer leaks `2026 年第一季度经营数据公告`
    - the unresolved new selector shell instead shows the list empty state
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
