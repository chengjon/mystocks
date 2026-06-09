# Batch Audit Report: detail-batch-06

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` selector-scoped primary-row truth gap so a new failing symbol cannot inherit the previously verified announcement rows, reusing existing `myweb-audit v1.66`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail page at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the primary announcement list was not selector-scoped, so a new failing route symbol could still show the previous verified symbol rows.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped canonical detail routes must treat the current route selector as part of primary-row provenance, not just banner copy.
- Occurrence basis:
  - `/detail/news/:symbol` let `/detail/news/000001` inherit the verified `600519` announcement rows when the first `000001` list request failed
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.66` to other selector-driven detail pages where the route selector and the visible primary rows can drift apart.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-row issue
- priority order applied: current route selector truth > primary list row provenance > stale retention only for the same verified selector
- primary owners selected:
  - `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-06`
- deferred items: none

## Fix Summary
- Updated the route-owned announcement monitor composable so the primary announcement list now tracks selector-scoped verified snapshots.
- Added route-local unavailable and stale note copy to the primary `公告列表` card.
- Ensured a new failing symbol clears the previous verified rows instead of leaking them into the current detail route.
- Added owner regressions plus a Phase 4 routed browser assertion for selector-switch failure.
- Reused existing `myweb-audit v1.66` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-06`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `13/13`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `31` tests including the new detail/news selector-switch assertion
  - targeted system-Chrome browser verification confirmed:
    - `/detail/news/600519` first shows `2026 年第一季度经营数据公告`
    - `/detail/news/000001` after a controlled first-load failure now shows `当前标的公告暂不可用，请稍后重试。`
    - the same controlled route-switch path no longer leaks `2026 年第一季度经营数据公告` into `.announcements-card`
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
