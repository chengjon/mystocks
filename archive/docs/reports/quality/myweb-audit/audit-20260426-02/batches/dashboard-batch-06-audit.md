# Batch Audit Report: dashboard-batch-06

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply the new `v1.63` service-normalizer envelope-truth rule so the canonical dashboard route keeps the verified capital-flow ranking slice visible on later `big-deal` refresh failure instead of swallowing the failure into fake empty-success rendering

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The visible capital-flow ranking and heatmap slice are owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`, but the failed later-refresh path also depends on `web/frontend/src/api/services/dashboardService.ts`.

### data-state-audit
- One high-severity route-truth defect remained: a later `big-deal` refresh failure reached the dashboard as a success-looking empty array, so the visible capital-flow ranking slice collapsed even though the route already had stale-slice retention logic.
- The defect crossed the service-to-route boundary: fixing only the page-level stale-state branch was insufficient until the service stopped erasing the resolved `success:false` envelope.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: route-local stale-slice retention can still fail on the real page when an upstream service normalizer maps a resolved failure envelope into empty-success payloads before the page owner sees it.
- Occurrence basis:
  - `/dashboard` uses a route-local service to fetch the capital-flow ranking slice
  - `apiClient` resolves non-2xx responses into ordinary `success:false` envelopes
  - the service omitted its envelope gate and normalized the failed response into `data: []`
- Shared component or helper involved:
  - `web/frontend/src/api/services/dashboardService.ts`
- Suggested follow-up scope: continue applying `v1.63` to any routed detail, dashboard, or workbench page where page-local stale-state logic exists but the real route still degrades to empty-success because a service/helper swallowed the failure envelope first.

## Main Skill Decisions
- duplicates merged: yes; disappearing capital-flow rows, missing heatmap stale note, and service-level empty-success normalization were merged into one dashboard service-envelope issue because they all came from the same `getStockFlowRanking()` failure path
- priority order applied: service-envelope truth > route-local stale-slice retention > aggregate-shell consistency
- primary owners selected:
  - `web/frontend/src/api/services/dashboardService.ts`
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- shared-impact review items:
  - `web/frontend/src/api/services/dashboardService.ts`
- fixes applied:
  - `dashboard-home-issue-06`
- deferred items: none

## Fix Summary
- Added a resolved-envelope gate to `dashboardService.getStockFlowRanking()` so `success:false` refresh responses now throw before ranking normalization.
- Preserved the dashboard's last verified capital-flow ranking slice on same-tab later refresh failure and surfaced explicit stale ranking copy in both the ranking card and heatmap card.
- Added service, owner, and routed phase-matrix regressions that lock the `success -> later big-deal refresh fail` truth path.
- Upgraded `myweb-audit` to `v1.63` with service-normalizer envelope-truth guidance.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-06`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `web/frontend/src/api/services/dashboardService.ts`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-06`.

## Reasons Not Fixed
- The repair intentionally stayed inside the dashboard route family plus its route-local service boundary; no broader shared market-data helper or shared chart primitive change was necessary.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate the later `big-deal` refresh failure while leaving the rest of the route functional
- Regression checks completed:
  - `npx vitest run src/api/services/__tests__/dashboardService.spec.ts -t "throws when the API client resolves a unified error envelope"` -> reproduced the expected red empty-success failure and then passed `1/1`
  - `npx vitest run src/api/services/__tests__/dashboardService.spec.ts` -> passed `5/5`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `17/17`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `33` structurally valid tests including the new dashboard retained-capital-flow-slice assertion
  - targeted routed-page verification confirmed the settled later-`big-deal`-failure path now renders:
    - ranking stale note `资金流向持续排名暂不可用，当前仍显示上次成功同步的排名快照。`
    - retained ranking rows `贵州茅台 / 宁德时代`
    - one `.capital-heatmap-card .chart-state-note`
    - aggregate `DATA: MIXED`
    - aggregate `SYNC: DEGRADED`
    - route alert `资金流向数据暂不可用`
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path

## Next Batch Plan
- Continue applying `v1.63` anywhere a routed page appears to have correct page-local stale-state handling in unit tests but the real browser still collapses a failed slice into empty-success because a route-local service or helper erased the failure envelope first.
