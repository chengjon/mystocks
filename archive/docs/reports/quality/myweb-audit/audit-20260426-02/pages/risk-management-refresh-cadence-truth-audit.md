# Page Audit: /risk/management

## Scope
- Route: `/risk/management`
- Canonical entry: `web/frontend/src/views/risk/Center.vue`
- Batch: `risk-batch-14`

## Defect Summary
- The canonical risk-management route hardcoded footer copy `风险数据每5分钟自动更新 · 最后一次更新：...`.
- Static review over `web/frontend/src/views/risk/Center.vue` and the active page-template path found no route-owned polling scheduler, push subscription, or equivalent cadence mechanism backing that five-minute claim.
- The footer therefore overstated route truth even on healthy natural loads: the page refreshed on route-sync completion, not on a verified five-minute timer.

## Repair
- Changed the footer copy in `web/frontend/src/views/risk/Center.vue` to `风险数据按当前页同步结果更新 · 最后一次更新：...`.
- Added an owner-level regression that explicitly fails if the canonical route reintroduces `每5分钟自动更新` without a real scheduler.
- Added a Phase 4 routed assertion so `/risk/management` now guards the same honest-cadence wording in live browser verification.

## Verification
- Component regression:
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts` passed `3/3`
- Risk family regression:
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStockPanel.spec.ts` passed `39/39`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `28` tests including the new `/risk/management` footer-cadence assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - a natural authenticated PM2 `/risk/management` load now renders footer `风险数据按当前页同步结果更新 · 最后一次更新：...`
  - the same verification confirms the footer no longer contains `每5分钟自动更新`
  - the route still advances `最后一次更新` to a real time after a verified live positions snapshot succeeds

## Skill Feedback
- This page promoted `myweb-audit` to `v1.52`.
- New reusable rule: routed pages must not promise a fixed polling or auto-refresh cadence in visible copy unless the route actually owns the corresponding scheduler, push subscription, or equivalent refresh mechanism.
