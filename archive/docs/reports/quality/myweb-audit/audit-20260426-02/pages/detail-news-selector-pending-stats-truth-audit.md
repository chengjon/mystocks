# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-11`

## Defect Summary
- The routed detail news page already cleared stale primary rows for explicit selector failure paths and for unresolved primary-list selector switches.
- But it still left one selector-pending summary truth gap:
  - `/detail/news/600519` verified the four top stats cards as `2 / 2 / 1 / 0`
  - the same page instance switched to `/detail/news/000001`
  - the first `000001` stats request remained unresolved
  - the route banner had already switched to `000001`, but the old `600519` stats cluster still stayed visible until the new stats request resolved

## Repair
- Updated `useAnnouncementMonitor.ts` so the stats slice now synchronizes selector-scoped snapshots at fetch start.
- Updated `AnnouncementMonitor.vue` so same-instance symbol switches explicitly refresh the stats slice as well as the primary announcement list.
- The new selector behavior is now:
  - same selector with a verified stats snapshot: keep that selector's cards during stale refreshes
  - different selector without a verified stats snapshot yet: clear the previous cards immediately and enter the new selector shell honestly
- Added a RED owner regression plus a Phase 4 same-instance selector-switch browser assertion for the unresolved first-load stats path.

## Verification
- Owner regressions:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `16/16`
- Type check:
  - `timeout 180s npm run type-check` failed because of pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - no new type errors were introduced by this batch's touched files
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `35` tests including the new selector-pending stats assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - authenticated `/detail/news/600519` first shows `2 / 2 / 1 / 0`
  - same-instance follow-up route `/detail/news/000001` now shows `当前详情标的: 000001`
  - the same controlled follow-up route no longer leaks the previous `2 / 2 / 1 / 0` stats cluster
  - the unresolved `000001` shell shows `-- / -- / -- / --` instead

## Skill Feedback
- This batch reused existing `myweb-audit v1.71` and `v1.68`.
- No new version was required because selector-owned summary-card provenance for same-instance detail-route switches was already codified by the existing selector-truth rules.
