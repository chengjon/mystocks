# Page Audit: /risk/management

## Scope
- Route: `/risk/management`
- Canonical entry: `web/frontend/src/views/risk/Center.vue`
- Batch: `risk-batch-12`

## Defect Summary
- The canonical risk-management route seeded footer freshness from `new Date().toLocaleString()` before any verified positions snapshot existed.
- Because `ArtDecoPageTemplate` keeps the footer slot mounted during both the loading shell and the first-load error shell, the visible copy `风险数据每5分钟自动更新 · 最后一次更新：...` leaked local current-time truth even though the route had not yet verified any live risk snapshot.

## Repair
- Changed `lastUpdateTime` to initialize as `--` in `web/frontend/src/views/risk/Center.vue`.
- Kept the existing `handleDataLoaded` success path so the same footer still advances to a real time once a verified positions snapshot arrives.
- Added owner-level and routed regressions to pin both the loading shell and the first-load failure shell against local-current-time freshness leakage.

## Verification
- Component regression:
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts` passed `2/2`
- Risk family regression:
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts tests/unit/views/risk-center-template-retention.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` passed `25/25`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `27` tests including the new `/risk/management` footer-freshness assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - controlled first-load failure now renders footer `最后一次更新：--` while the page remains on `/risk/management`
  - the same controlled proof keeps the footer visible under the error shell instead of leaking a local current-time stamp
  - natural PM2 `/risk/management` still reaches the route, shows a real request id, and advances footer freshness to a real time after the live positions request succeeds

## Skill Feedback
- This page did not require a new skill-version bump. It reused existing `myweb-audit v1.47` initial freshness placeholder truth guidance on a canonical routed page.
