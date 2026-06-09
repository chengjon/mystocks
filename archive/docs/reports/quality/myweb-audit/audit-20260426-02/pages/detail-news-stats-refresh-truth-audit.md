# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-03`

## Defect Summary
- The routed detail news page already rendered all four sibling announcement stats from `/api/announcement/stats`.
- But once that stats slice had verified once, a later stats refresh failure silently preserved the old `stats` object inside the view-local composable.
- The visible top strip therefore kept stale counts on screen with no slice-local stale-summary cue, even though only the announcement row slice still had verified truth.

## Repair
- Updated `useAnnouncementMonitor.ts` so `fetchStats()` clears `stats.value` back to `{}` when `/api/announcement/stats` resolves `success: false` or throws.
- Kept the repair inside the view-local single-consumer composable instead of widening into shared announcement infrastructure.
- Added a composable red/green regression for the exact `success -> stats-refresh-fail` path.
- Added a routed Phase 4 assertion proving the four stat cards degrade to `--` while the verified announcement row remains visible.

## Verification
- Composable regression:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts` passed `3/3`
- Narrow routed regression:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `6/6`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `29` tests including the new detail-news stale-stats refresh assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled success now renders `2 / 2 / 1 / 0` across the four stat cards
  - after a later failing stats refresh, the same route renders `-- / -- / -- / --`
  - the verified announcement row `2026 年第一季度经营数据公告` remains visible after that stats failure
  - no unhandled routed mock requests remained
  - natural PM2 `/detail/news/600519` still reaches the route and currently renders four live count cards `0 / 0 / 0 / 0`

## Skill Feedback
- This batch introduced `myweb-audit v1.53`.
- New rule: when a routed page keeps an independent list or table visible after a dedicated sibling stats slice fails on refresh, the failed stat cluster must either show explicit slice-local stale-summary UX or degrade back to placeholder truth such as `--`; previously verified counts must not silently remain on screen as current truth.
