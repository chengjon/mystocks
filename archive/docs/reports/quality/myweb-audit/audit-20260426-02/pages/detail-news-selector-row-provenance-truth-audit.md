# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-06`

## Defect Summary
- The canonical detail news route already showed the current `routeSymbol` in the route banner.
- But its primary `公告列表` rows were still keyed only by the last successful fetch, not by the current selector.
- That meant a new failing detail selector could inherit the previous symbol snapshot:
  - `/detail/news/600519` verified successfully
  - navigating to `/detail/news/000001` then failing the first `000001` list request left the old `600519` rows visible under the new route banner

## Repair
- Updated `useAnnouncementMonitor.ts` so the primary announcement list now tracks:
  - `announcementSliceState`
  - `lastVerifiedAnnouncementSelectorKey`
- The primary list now applies selector-scoped truth:
  - same selector refresh failure: keep the last verified rows as stale truth
  - new selector first-load failure: clear the old rows and mark the current selector unavailable
- Added route-local copy in `AnnouncementMonitor.vue`:
  - `当前标的公告暂不可用，请稍后重试。`
  - `当前仍显示上次成功同步的公告快照。`
- Added owner regressions and a Phase 4 routed assertion for selector-switch failure.

## Verification
- Owner regressions:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `13/13`
- Type check:
  - `timeout 180s npm run type-check` passed
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `31` tests including the new selector-switch assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first route `/detail/news/600519` shows `2026 年第一季度经营数据公告`
  - controlled follow-up route `/detail/news/000001` now shows `当前标的公告暂不可用，请稍后重试。`
  - the same controlled follow-up route no longer leaks `2026 年第一季度经营数据公告` into `.announcements-card`

## Skill Feedback
- This batch reused existing `myweb-audit v1.66`.
- No new version was required because selector-scoped row provenance was already codified by the existing watchlist/manage audit rule.
