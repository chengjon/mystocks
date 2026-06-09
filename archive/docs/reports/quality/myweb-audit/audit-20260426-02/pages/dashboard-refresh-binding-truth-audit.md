# Page Audit Report: /dashboard

## Purpose
Canonical dashboard route for aggregate market, fund-flow, industry, strategy, and system surfaces backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Route-local slice state is owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### functional-audit
- One high-severity interaction defect existed before repair: the visible shared-header `刷新数据` control became a no-op after the dashboard bootstrap summary reset cleared the shared refresh callback.

### data-state-audit
- The no-op shared refresh control blocked later stale-refresh truth on `/dashboard` because the page could no longer issue a second fund-flow request through the visible header action.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `dashboard-home-issue-03`
  - Repair target: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - Shared impact: none
  - Outcome: fixed in `dashboard-batch-03`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - shared layout refresh helper usage via `web/frontend/src/composables/useHeaderSummary.ts`
- Impact basis: the repair stays dashboard-local by rebinding the page-owned callback after bootstrap reset instead of changing the shared header summary store semantics.
- Potentially affected related pages:
  - `/dashboard`

## Repair Plan
- Fix now:
  - preserve the shared header reset behavior for placeholder summary text
  - immediately rebind the dashboard page-owned refresh callback after bootstrap reset
  - add a targeted regression that proves `headerSummary.refresh()` issues a second request cycle after mount
- Deferred:
  - none in this batch
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-03-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - now rebinds `headerSummary.setRefreshFn(refreshData)` immediately after bootstrap summary reset
- Regression coverage:
  - `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Verified at: 2026-05-04
- Checked routes:
  - `/dashboard`
- Checked states:
  - default
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "keeps the shared header refresh action bound after the dashboard bootstrap reset path runs"` reproduced the expected red failure and then passed `1/1` after repair
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` passed `13/13`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed `28` structurally valid phase1 routed tests including the existing dashboard stale-refresh route case
  - controlled browser verification confirmed the visible shared-header `刷新数据` control now triggers a second `/api/akshare/market/fund-flow/hsgt-summary` request on `/dashboard`
  - the same controlled browser verification confirmed request count `2`, route-level degraded alert `资金流向数据暂不可用`, and retained verified fund-flow slice text `沪股通净流入 / 18.5亿`, with `0` blocking `.error-message` nodes

## Residual Risks
- [Low] The retained verified fund-flow slice still shows shared stat-card chrome such as `+0%` on secondary cards like `北向资金总额` and `主力净流入`; that is a separate numeric-surface issue from the refresh-binding defect fixed in `dashboard-batch-03`.
- [Low] Other dashboard slices still rely on their own independent later-refresh behavior; `dashboard-batch-03` only closes the reproduced shared-header refresh binding defect.
