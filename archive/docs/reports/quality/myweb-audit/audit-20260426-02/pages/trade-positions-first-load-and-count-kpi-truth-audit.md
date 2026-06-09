# Page Audit Report: /trade/positions

## Purpose
Canonical trade-domain positions workbench for reviewing request metadata, current positions, market value, pnl, and allocation surfaces backed by `src/views/trade/Center.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/trade/Center.vue`
- Shared routed wrappers:
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring truthful first-load and empty-state numeric presentation.

### data-state-audit
- One high-severity numeric-truth cluster existed before repair:
  - the hero meta, top KPI strip, and content summary rendered unresolved first-load positions state through `N/A`, `0`, `0.00`, and `¥0` values
  - the same route rendered resolved empty count-only KPI cards with shared `+0%` chrome and exact-decimal formatting

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-positions-issue-01`
  - Repair target: `web/frontend/src/views/trade/Center.vue`
  - Shared impact: `/strategy/pos`
  - Outcome: fixed in `trade-batch-06`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/trade/Center.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- Impact basis: `/strategy/pos` is a routed wrapper over the same canonical positions page, so misleading first-load or empty-state tallies on the canonical trade page would also leak into the strategy route family.

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - verification blocked service workers and fulfilled the positions request through browser-context interception when testing unresolved first-load state
- Verified at: 2026-04-30
- Checked routes:
  - `/trade/positions`
- Checked states:
  - loading
  - empty
- Checked breakpoints:
  - 1440
- Validation notes:
  - with the first `/api/v1/trade/positions` request intentionally hung, live verification now showed `REQ_ID: --`, `TIME: --`, `ROWS: --`, KPI values `-- / -- / -- / --`, zero `.artdeco-stat-change` nodes, and content meta `MARKET_VALUE: -- / TOTAL_PNL: --`
  - normal PM2 verification still resolved the route to honest empty-state data with `ROWS: 0`, top KPI values `0 / 0 / ¥0 / --`, content meta `MARKET_VALUE: ¥0 / TOTAL_PNL: ¥0`, zero `.artdeco-stat-change` nodes, and no `+0%` or `0.00`
  - live PM2 requests observed `200` responses for `/api/health/ready`, `/api/health`, and `/api/v1/trade/positions`

## Residual Risks
- [Low] This batch intentionally scoped to first-load and empty-state numeric truth, so stale-refresh retention for positions remains a separate behavior question if a future routed audit reproduces a refresh failure with previously loaded rows.
- [Low] The route still uses `N/A` as the non-pending fallback for request metadata after a completed load when the backend omits those fields entirely; the current PM2 path does return live request metadata.
