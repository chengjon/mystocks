# Page Audit Report: /watchlist/screener

## Purpose
Canonical watchlist-domain screening route for loading the stock universe, applying local draft filters, and reviewing candidate rows, routed through `web/frontend/src/views/watchlist/Screener.vue` and owned by `web/frontend/src/views/stocks/Screener.vue`.

## Agent Findings

### route-inventory
- Canonical route entry: `web/frontend/src/views/watchlist/Screener.vue`
- Routed surface owner: `web/frontend/src/views/stocks/Screener.vue`

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring honest summary-state presentation on the primary screener route.

### data-state-audit
- One high-severity summary-truth defect remained: the route mixed unresolved first-load, backend failure, and verified count-only stock-universe tallies under the same shared stat-card behavior, so the page could not distinguish verified screener summary from unverified universe state.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `watchlist-screener-issue-01`
  - Repair target: `web/frontend/src/views/stocks/Screener.vue`
  - Shared impact: `ArtDecoStatCard.vue` remains observation-only
  - Outcome: fixed in `watchlist-batch-03`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/stocks/Screener.vue`
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Impact basis: the routed defect lived on a thin wrapper route over a shared stock screener surface, but the approved repair stayed local to the page owner and did not widen into a shared default-behavior change.
- Potentially affected related pages:
  - `/watchlist/screener`

## Repair Plan
- Fix now:
  - convert hero universe count and top count-only cards to route-local placeholders until verified universe evidence exists
  - convert verified count-only summary cards to explicit string values
  - preserve `show-change=false` on the entire top summary strip
- Deferred:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a future shared-component batch
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-03-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/stocks/Screener.vue`
  - now derives `showSummaryPlaceholders` from unresolved first-load and no-evidence error state
  - now renders hero `UNIVERSE` and all four top summary cards through route-local display values
  - now keeps verified count-only summary cards as plain strings without shared faux precision
- Regression coverage:
  - `web/frontend/src/views/watchlist/__tests__/Screener.spec.ts`
  - `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - browser-context fulfillment was used for the verified non-empty universe path, while the natural PM2 error path and the hanging first-load path were also verified directly
- Verified at: 2026-04-30
- Checked routes:
  - `/watchlist/screener`
- Checked states:
  - default
  - loading
  - error
- Checked breakpoints:
  - 1440
- Validation notes:
  - `npx vitest run src/views/watchlist/__tests__/Screener.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/watchlist/__tests__/Manage.spec.ts` passed `5/5`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` listed `15` structurally valid phase-2 routed tests, including the strengthened `/watchlist/screener` success and unresolved-first-load assertions
  - natural PM2 verification confirmed the backend error path now shows `UNIVERSE: --`, summary-strip `-- / -- / -- / --`, and zero `.artdeco-stat-change` nodes while `/api/v1/data/stocks/basic` returns `401`
  - browser-context success verification confirmed the same route now renders `3 / 3 / 2 / 1.61亿` with zero `.artdeco-stat-change` nodes and the expected screener body
  - browser-context hanging-first-load verification confirmed the route now renders `UNIVERSE: --`, summary-strip `-- / -- / -- / --`, zero `.artdeco-stat-change` nodes, and the visible `股票池同步中` state while the first stock-universe request remains unresolved

## Residual Risks
- [Low] The natural PM2 environment currently returns `401` for `/api/v1/data/stocks/basic`, so the verified non-empty stock-universe summary path still relies on controlled browser-context fulfillment rather than a natural backend dataset.
- [Low] Shared `ArtDecoStatCard.vue` defaults still carry the same faux precision behavior for pages that have not yet adopted page-local truthful rendering.
