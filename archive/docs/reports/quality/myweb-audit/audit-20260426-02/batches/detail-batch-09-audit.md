# Batch Audit Report: detail-batch-09

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` auxiliary selector-truth gap so a same-instance symbol switch cannot leave previous-symbol rule or trigger rows visible under the new detail banner, reusing existing `myweb-audit v1.66` and `v1.60`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail page at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the detail route's sibling auxiliary tables were not selector-scoped, so a same-instance symbol switch could leave the previous symbol's rule and trigger rows visible under the new route shell.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped canonical detail routes must keep sibling auxiliary rows aligned with the current route entity instead of blindly rendering the last verified cross-entity auxiliary arrays.
- Occurrence basis:
  - `/detail/news/:symbol` let `/detail/news/000001` inherit the verified `600519` auxiliary rule and trigger rows during the same page instance
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.66` and `v1.60` to other selector-driven detail pages where auxiliary rows can drift away from the active entity banner.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed auxiliary selector-row issue
- priority order applied: current detail symbol truth > auxiliary row provenance > retention only for rows that still belong to the active symbol
- primary owners selected:
  - `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-09`
- deferred items: none

## Fix Summary
- Updated the route-owned announcement detail view so auxiliary rules and triggered records are filtered to the current detail symbol.
- Preserved global rules with empty `stock_codes` across symbol switches.
- Added owner regressions plus a Phase 4 routed browser assertion for same-instance selector-switch leakage.
- Reused existing `myweb-audit v1.66` and `v1.60` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-09`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-09`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome` after authenticating through the natural login gate
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `14/14`
  - `timeout 180s npm run type-check` -> failed due to pre-existing unrelated errors in `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `33` tests including the new detail/news auxiliary selector-switch assertion
  - targeted system-Chrome browser verification confirmed:
    - authenticated `/detail/news/600519` first shows `高重要性公告` and `2026 年第一季度经营数据公告`
    - same-instance `/detail/news/000001` then reaches `当前详情标的: 000001`
    - the same controlled route-switch path keeps `全市场风险提示`
    - the same controlled route-switch path no longer leaks `高重要性公告` or `2026 年第一季度经营数据公告`
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
