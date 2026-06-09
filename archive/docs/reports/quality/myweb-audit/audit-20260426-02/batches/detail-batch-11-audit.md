# Batch Audit Report: detail-batch-11

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` selector-pending stats-card truth gap so a new unresolved symbol shell cannot keep the previous verified counts visible, reusing existing `myweb-audit v1.71` and `v1.68`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail page at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: the top stats cards were stale-refresh aware but not selector-scoped for unresolved same-instance detail-symbol switches.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped canonical detail routes must clear the previous selector summary cards as soon as the route/entity shell switches to a new selector that has not yet verified its own dedicated stats slice.
- Occurrence basis:
  - `/detail/news/:symbol` let `/detail/news/000001` inherit the verified `600519` stats-card cluster while the first `000001` stats request remained unresolved
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.71` and `v1.68` to other selector-driven detail pages where unresolved first loads can leave the previous entity summary cards visible.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-pending stats issue
- priority order applied: current route selector truth > dedicated stats-card provenance > stale retention only for the same verified selector
- primary owners selected:
  - `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-11`
- deferred items: none

## Fix Summary
- Updated the route-owned announcement monitor composable so the dedicated stats slice now synchronizes selector-scoped snapshots at fetch start.
- Ensured a new unresolved symbol clears the previous verified stat cards immediately instead of waiting for the new stats request to settle.
- Updated the route shell to refresh the stats slice on same-instance symbol switches in addition to the primary announcement list.
- Added owner regressions plus a Phase 4 routed browser assertion for selector-switch pending-state stats leakage.
- Reused existing `myweb-audit v1.71` and `v1.68` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-11-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-11`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-11`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome` after authenticating through the natural login gate
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `16/16`
  - `timeout 180s npm run type-check` -> failed due to pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `35` tests including the new detail/news selector-pending stats assertion
  - targeted system-Chrome browser verification confirmed:
    - authenticated `/detail/news/600519` first shows the verified stats cluster `2 / 2 / 1 / 0`
    - same-instance `/detail/news/000001` then reaches `当前详情标的: 000001`
    - the same controlled route-switch path no longer leaks the previous `2 / 2 / 1 / 0` counts
    - the unresolved new selector shell instead shows `-- / -- / -- / --`
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
