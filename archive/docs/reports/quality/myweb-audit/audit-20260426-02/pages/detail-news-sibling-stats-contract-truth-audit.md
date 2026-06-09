# Page Audit: /detail/news/:symbol

## Scope
- Route: `/detail/news/:symbol`
- Canonical entry: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- Batch: `detail-batch-02`

## Defect Summary
- The routed detail news page already requested a dedicated live announcement stats contract, but only surfaced `total_count` in the visible stat strip.
- As a result, the top surface looked partially live but semantically broken:
  - `公告总数` fell back to `0` before any verified stats snapshot existed
  - `TODAY`, `IMPORTANT`, and `TRIGGERED` stayed as label-only cards with no verified count surface
- The page therefore misrepresented the route as if one stat had verified while the adjacent sibling cards remained unresolved or unimplemented.

## Repair
- Added page-local `displayStats` derivation so the visible four-card strip reads all sibling fields from the dedicated announcement stats contract.
- Added placeholder gating so every stat card degrades to `--` until that specific stats slice has verified.
- Kept the repair page-local in `AnnouncementMonitor.vue` plus routed regressions rather than widening into shared announcement composables.

## Verification
- Component regression:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts` passed `2/2`
- Narrow routed regression:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` passed `5/5`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `28` tests including the new detail-news sibling-stats assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled success now renders `2 / 2 / 1 / 0` across the four stat cards and keeps the route banner plus announcement row visible
  - controlled stats-slice failure now renders `-- / -- / -- / --` while the announcements list still shows `2026 年第一季度经营数据公告`
  - the stats-failure path no longer falls through to `公告总数 0` or a single-count-plus-label-only shell
  - natural PM2 `/detail/news/600519` still reaches the route and currently renders four live count cards `0 / 0 / 0 / 0`

## Skill Feedback
- This batch introduced `myweb-audit v1.50`.
- New rule: when a routed page requests a dedicated live stats or summary contract with multiple sibling count fields, the visible sibling stat cards must either render those verified counts or explicitly degrade each unsupported card to placeholder truth such as `--`.
