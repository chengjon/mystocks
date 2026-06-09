# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-05`

## Defect Summary
- The canonical detail news route already kept its announcement list visible as the verified primary slice.
- But the sibling `monitor-rules` and `triggered-records` table slices still degraded silently:
  - first-load auxiliary failures fell through to empty tables with no route-local note
  - later auxiliary refresh failures kept old rows visible with no stale-slice note
- The result was a false empty-success or unlabeled stale-success surface even though the announcement list itself remained verified.

## Repair
- Updated `useAnnouncementMonitor.ts` so the route now tracks:
  - `monitorRulesSliceState`
  - `triggeredRecordsSliceState`
  - first verified snapshot boundaries for both auxiliary slices
- Added route-local note copy in `AnnouncementMonitor.vue`:
  - first-load unavailable:
    - `监控规则暂不可用，当前仅显示已验证的公告主列表。`
    - `触发记录暂不可用，当前仅显示已验证的公告主列表。`
  - later stale retention:
    - `当前仍显示上次成功同步的监控规则快照。`
    - `当前仍显示上次成功同步的触发记录快照。`
- Added owner regressions and a Phase 4 routed assertion for later auxiliary refresh failure.

## Verification
- Owner regressions:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `11/11`
- Type check:
  - `timeout 180s npm run type-check` passed
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `30` tests including the new detail/news auxiliary-slice assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first success shows:
    - rules row `高重要性公告`
    - trigger row `2026 年第一季度经营数据公告`
  - controlled later refresh failure now keeps both auxiliary tables visible and adds:
    - `当前仍显示上次成功同步的监控规则快照。`
    - `当前仍显示上次成功同步的触发记录快照。`
  - the verified announcement list remains visible throughout the same controlled refresh path

## Skill Feedback
- This batch reused existing `myweb-audit v1.65 + v1.60`.
- No new version was required because the repaired failure mode was already covered by the existing auxiliary live-slice and sibling enrichment-slice truth rules.
