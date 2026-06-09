# Page Audit Report: /dashboard

## Purpose
Canonical dashboard route for aggregate market, fund-flow, industry, strategy, and system surfaces backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Route-local slice state is owned by `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`.

### functional-audit
- No independent new interaction repair was implemented in this batch.
- One out-of-scope observation was recorded during natural PM2 browser verification: the visible dashboard `刷新数据` control did not trigger a second fund-flow request on this machine, so the stale-refresh route proof for this batch relies on the strengthened dashboard logic harness and routed phase1 coverage instead of that natural control path.

### data-state-audit
- One high-severity route-truth defect existed before repair: once `/dashboard` had already shown a verified fund-flow slice, a later failing `/api/akshare/market/fund-flow/hsgt-summary` refresh still replaced the visible fund-flow cards with blocking inline error truth.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `dashboard-home-issue-02`
  - Repair target: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - Shared impact: none
  - Outcome: fixed in `dashboard-batch-02`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Impact basis: the repair stays local to the dashboard composable and dashboard owner template.
- Potentially affected related pages:
  - `/dashboard`

## Repair Plan
- Fix now:
  - split fund-flow failure semantics into blocking first-load error truth vs later degraded warning truth
  - preserve the verified fund-flow cards and chart after later refresh failures
  - strengthen dashboard logic and routed phase1 coverage for `success -> fund-flow refresh fail`
- Deferred:
  - a separate control-path observation remains: the natural PM2 dashboard `刷新数据` button did not trigger a second fund-flow request on this machine
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/dashboard-batch-02-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - now records whether the route has ever verified a fund-flow slice
  - now routes later fund-flow refresh failures into a degraded warning channel instead of blocking `error.fundFlow`
- `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
  - now only shows fund-flow skeletons before the first verified fund-flow snapshot
  - now keeps the verified fund-flow cards and chart visible after later failures
- Regression coverage:
  - `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`
  - `web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts`

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
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts -t "keeps the last verified fund-flow slice visible when a later fund-flow refresh fails"` reproduced the expected red failure and then passed `1/1` after repair
  - `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` passed `12/12`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed `28` structurally valid phase1 routed tests including the strengthened dashboard stale-refresh case
  - controlled browser verification confirmed the natural PM2 `/dashboard` route still renders the verified `沪股通净流入 / 18.5亿` fund-flow slice on initial load
  - the same controlled browser verification recorded an out-of-scope observation that the visible `刷新数据` control did not trigger a second fund-flow request in the current PM2 path on this machine, so the stale-refresh proof for this batch is carried by the strengthened dashboard logic harness and routed phase1 coverage rather than that control path

## Residual Risks
- [Low] The natural PM2 dashboard `刷新数据` control still needs a follow-up batch because it did not trigger a second fund-flow request during controlled browser observation on this machine.
- [Low] Other core dashboard slices such as market and industry still use their own existing later-failure behavior; `dashboard-batch-02` only closes the reproduced fund-flow stale-refresh defect.
