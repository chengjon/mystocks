# Batch Audit Report: dashboard-batch-08

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: apply the new `v1.65` auxiliary-slice sync-state rule so the canonical dashboard route treats technical-indicator and monitoring panels with real live contracts as honest unavailable or stale slices instead of fake integration placeholders

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The affected auxiliary slices are route-owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### data-state-audit
- One high-severity route-truth defect remained: the dashboard still treated verified auxiliary live slices as if they were non-integrated or placeholder-only capabilities whenever the first load or a later refresh failed.
- The defect covered two route-owned slices on the same canonical page:
  - technical indicators
  - system monitoring

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed dashboard can already own real live auxiliary slices but still collapse those slices to fake capability copy or placeholder rows when the slice fails before first verification or on a later refresh.
- Occurrence basis:
  - `/dashboard` owns both auxiliary slices inside the dashboard composable
  - monitoring truth was additionally blurred by service-level health-envelope normalization
  - the route therefore lost both first-load unavailable truth and later stale-refresh retention truth on live auxiliary surfaces
- Shared component or helper involved:
  - `web/frontend/src/api/services/dashboardService.ts`
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- Suggested follow-up scope: continue applying `v1.65` to routed dashboards and workbenches that already own real auxiliary slices but still fall back to `真实接口待接入...`, placeholder rows, or generic empty copy.

## Main Skill Decisions
- duplicates merged: yes; technical-indicator and monitoring failures came from the same auxiliary-slice sync-state pattern on the same canonical route
- priority order applied: auxiliary live-slice truth > stale-refresh retention truth > service-envelope truth
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/src/api/services/dashboardService.ts`
- shared-impact review items:
  - none beyond the dashboard family
- fixes applied:
  - `dashboard-home-issue-08`
- deferred items: none

## Fix Summary
- Added explicit verification and stale-state tracking for dashboard indicators and monitoring slices.
- Replaced fake auxiliary capability copy with route-owned unavailable and stale-refresh messages.
- Preserved the last verified indicator and monitoring rows on later refresh failure.
- Tightened `dashboardService.getSystemHealth()` so resolved unified error envelopes stay visible as failure truth.
- Added owner, service, and routed regressions that lock first-load and later refresh-failure truth for both slices.
- Upgraded `myweb-audit` to `v1.65` with auxiliary-slice sync-state guidance.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-08`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-08`.

## Reasons Not Fixed
- The repair intentionally stayed inside the canonical dashboard route and its one dashboard service normalization path; no shared stat-card or global dashboard-shell rewrite was required for this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` was used to isolate both first-load auxiliary failures and later stale-refresh truth on `/dashboard`
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts src/api/services/__tests__/dashboardService.spec.ts` -> passed `28/28`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "technical-indicator|monitoring slice"` -> passed `4/4`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed the new dashboard auxiliary-slice assertions in a structurally valid matrix
  - targeted routed-page verification confirmed:
    - first-load indicator failure renders `技术指标暂不可用，当前暂无已验证指标快照。`
    - first-load monitoring failure renders `系统监控暂不可用，当前暂无已验证监控快照。`
    - later indicator refresh failure keeps `RSI 61.2 偏强` visible and renders explicit stale copy
    - later monitoring refresh failure keeps `HEALTHY / mystocks-backend / 2.0.0` visible and renders explicit stale copy
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path

## Next Batch Plan
- Continue applying `v1.65` anywhere a routed dashboard, detail page, or workbench already owns real auxiliary live slices but still degrades them to fake integration copy, placeholder rows, or generic empty-state truth on first-load or later refresh failure.
