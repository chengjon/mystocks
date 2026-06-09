# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-09`

## Defect Summary
- The canonical detail news route already kept the primary `公告列表` selector-scoped.
- But its sibling `监控规则管理` and `触发记录` tables still rendered raw auxiliary arrays without filtering them to the current detail symbol.
- That meant a same-instance route switch could leave previous-symbol auxiliary rows visible under the new route banner:
  - `/detail/news/600519` verified auxiliary rows successfully
  - navigating to `/detail/news/000001` changed the route banner and primary list shell
  - the page could still show the old `600519` rule row and triggered-record row inside the new `000001` detail shell

## Repair
- Updated `AnnouncementMonitor.vue` so the detail route now derives:
  - `visibleMonitorRules`
  - `visibleTriggeredRecords`
- Auxiliary selector truth now behaves as follows:
  - no `routeSymbol`: render the full auxiliary arrays
  - current `routeSymbol` present:
    - monitor rules keep only global rules (`stock_codes=[]`) or rows whose `stock_codes` include the active symbol
    - triggered records keep only rows whose `stock_code` matches the active symbol
- This keeps global rules available while preventing previous-symbol auxiliary rows from leaking into a new detail shell.
- Added a routed view regression plus a Phase 4 same-instance selector-switch browser assertion.

## Verification
- Owner regressions:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `14/14`
- Type check:
  - `timeout 180s npm run type-check` failed because of pre-existing unrelated errors in `src/components/technical/composables/useKLinePatternOverlays.ts`
  - no new type errors were introduced by this batch's touched files
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `33` tests including the new auxiliary selector-switch assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - authenticated `/detail/news/600519` first shows `高重要性公告` and `2026 年第一季度经营数据公告`
  - same-instance follow-up route `/detail/news/000001` now shows `当前详情标的: 000001`
  - the same controlled follow-up route keeps `全市场风险提示`
  - the same controlled follow-up route no longer leaks `高重要性公告` or `2026 年第一季度经营数据公告` into the new detail shell

## Skill Feedback
- This batch reused existing `myweb-audit v1.66` and `v1.60`.
- No new version was required because selector-scoped row provenance and auxiliary-slice truth were already codified by the existing detail/watchlist audit rules.
