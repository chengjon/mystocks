# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-10`

## Defect Summary
- The canonical detail news route already cleared stale primary rows for explicit selector failure paths.
- But it still left one selector-pending truth gap:
  - `/detail/news/600519` verified the primary `公告列表`
  - the same page instance switched to `/detail/news/000001`
  - the first `000001` announcement request remained unresolved
  - the route banner had already switched to `000001`, but the old `600519` primary row still stayed visible until the new request resolved

## Repair
- Updated `useAnnouncementMonitor.ts` so the primary list now synchronizes selector-scoped snapshots at fetch start.
- The new selector behavior is now:
  - same selector with a verified snapshot: keep that selector's rows during stale refreshes
  - different selector without a verified snapshot yet: clear the previous rows immediately and enter the new selector shell honestly
- Added a RED owner regression plus a Phase 4 same-instance selector-switch browser assertion for the unresolved first-load path.

## Verification
- Owner regressions:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `15/15`
- Type check:
  - `timeout 180s npm run type-check` failed because of pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - no new type errors were introduced by this batch's touched files
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `34` tests including the new selector-pending assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - authenticated `/detail/news/600519` first shows `2026 年第一季度经营数据公告`
  - same-instance follow-up route `/detail/news/000001` now shows `当前详情标的: 000001`
  - the same controlled follow-up route no longer leaks `2026 年第一季度经营数据公告`
  - the unresolved `000001` shell shows the list empty state instead of stale `600519` rows

## Skill Feedback
- This batch reused existing `myweb-audit v1.71` and `v1.66`.
- No new version was required because selector-owned primary-row provenance for same-instance detail-route switches was already codified by the existing detail/watchlist audit rules.
