# Batch Audit Report: dashboard-batch-03

## Scope
- Module: dashboard
- Pages:
  - /dashboard
- Batch rationale: close the shared-header refresh binding gap on the canonical dashboard route so bootstrap summary resets can no longer leave the visible `刷新数据` control as a no-op, and fold that pattern back into myweb-audit as `v1.56`

## Agent Summary

### route-inventory
- `/dashboard` remains the canonical dashboard route at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- The route-local slice state owner remains `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### functional-audit
- One high-severity route-interaction defect remained: the visible shared-header refresh control became a no-op after dashboard bootstrap summary reset.

### data-state-audit
- Because the visible refresh control could not issue a second request cycle, later route-level stale-refresh truth such as fund-flow degradation could not be reproduced through the visible dashboard action path.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can correctly own a refresh callback, but a shared header or summary reset path can silently clear that callback and leave a visible manual refresh control rendered with no live request behind it.
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - shared helper usage via `web/frontend/src/composables/useHeaderSummary.ts`
- Suggested follow-up scope: continue applying `v1.56` to routed pages that render shared-header or layout-level refresh controls backed by per-route callbacks.

## Main Skill Decisions
- duplicates merged: yes; the no-op refresh button, missing second fund-flow request, and blocked stale-refresh proof were merged into one dashboard refresh-binding issue because they all came from the same bootstrap reset clearing the shared callback
- priority order applied: visible route-owned action truth > stale-refresh reproducibility > shared-helper containment
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- shared-impact review items: none
- fixes applied:
  - `dashboard-home-issue-03`
- deferred items:
  - a separate numeric-surface issue remains on retained fund-flow stat-card chrome such as `+0%`

## Fix Summary
- Rebound the dashboard page-owned refresh callback immediately after bootstrap summary reset.
- Added a targeted regression that proves `headerSummary.refresh()` now issues a second request cycle after mount.
- Reused the existing routed stale-refresh test surface and confirmed through controlled browser verification that the visible shared-header button now drives the second fund-flow request.
- Upgraded `myweb-audit` to `v1.56` with shared-refresh binding checks.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `dashboard-home-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - numeric-surface follow-up on retained fund-flow stat-card chrome remains separate from the refresh-binding repair

## Unresolved Items
- No approved repair remains unimplemented in `dashboard-batch-03`.

## Reasons Not Fixed
- Shared stat-card chrome on retained dashboard fund-flow cards was not changed in this batch because it is a distinct numeric-surface issue from the refresh-binding defect repaired here.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "keeps the shared header refresh action bound after the dashboard bootstrap reset path runs"` -> reproduced the expected red failure and then passed `1/1`
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` -> passed `13/13`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `28` structurally valid tests
  - controlled browser verification confirmed `/dashboard` now issues a second `/api/akshare/market/fund-flow/hsgt-summary` request after clicking the visible shared-header `刷新数据` control
  - the same controlled browser verification confirmed request count `2`, route-level degraded alert `资金流向数据暂不可用`, retained verified fund-flow slice text `沪股通净流入 / 18.5亿`, and `0` blocking `.error-message` nodes
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch continued to use system-`google-chrome` Playwright-library verification

## Next Batch Plan
- Continue scanning routed pages that expose shared-header or layout-level refresh controls backed by route-local callbacks.
- Revisit `/dashboard` for the remaining retained fund-flow stat-card chrome issue (`+0%`) as a separate numeric-surface batch if it is still visible on the canonical route.
