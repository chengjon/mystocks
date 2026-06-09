# Page Audit Report: /watchlist/manage

## Purpose
Canonical watchlist management route for reviewing watchlist groups, the currently selected stock list, and top-level self-selection summary counts, routed through `web/frontend/src/views/watchlist/Manage.vue` and owned by `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

## Agent Findings

### route-inventory
- Canonical route entry remains `web/frontend/src/views/watchlist/Manage.vue`.
- Routed surface owner remains `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

### functional-audit
- One high-severity routed selector-pending defect remained before repair:
  - a same-instance click from `核心组合` to `成长跟踪` switched the active tab immediately
  - but the new watchlist's first stock request could remain unresolved while the old `贵州茅台 / 宁德时代` rows stayed visible under the new active tab

### data-state-audit
- The defect was selector-scoped pending primary-row provenance:
  - the old `核心组合` rows were still valid as the last verified stock snapshot
  - what broke was the selector truth, because the route presented those retained rows under the new unresolved `成长跟踪` shell

### visual-artdeco-audit
- No new visual-dominant defect required a repair wave in this batch.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `watchlist-manage-issue-07`
  - Repair target: `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
  - Outcome: fixed in `watchlist-batch-07`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Verified at: 2026-05-06
- Checked routes:
  - `/watchlist/manage`
- Checked states:
  - default
  - selector-switch-first-load-pending
- Checked breakpoints:
  - 1440
- Validation notes:
  - component regression now proves that clicking `成长跟踪` after a verified `核心组合` load no longer leaves stale `贵州茅台 / 宁德时代` rows under the new active tab while the new selector is unresolved
  - the same regression now proves the summary strip stays `2 / -- / -- / --`
  - targeted browser-context verification with system `google-chrome` confirmed the unresolved new selector shell reaches `成长跟踪`, shows `自选列表同步中`, keeps `rowCount: 0`, and does not leak `贵州茅台`

## Residual Risks
- [Low] The selector-pending proof still relies on controlled browser-context fulfillment because the natural PM2 route is healthy and does not reproduce the unresolved `watchlists/:watchlistId/stocks` shape on demand.
- [Low] The repo's default Playwright Chromium runner is still unavailable on this machine, so browser-path verification continues to rely on Playwright-library control of system `google-chrome`.
