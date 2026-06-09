# Page Audit Report: /watchlist/manage

## Purpose
Canonical watchlist management route for reviewing watchlist groups, the currently selected stock list, and top-level self-selection summary counts, routed through `web/frontend/src/views/watchlist/Manage.vue` and owned by `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

## Agent Findings

### route-inventory
- Canonical route entry remains `web/frontend/src/views/watchlist/Manage.vue`.
- Routed surface owner remains `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

### functional-audit
- One high-severity routed selector-provenance defect remained before repair:
  - a later stock-slice refresh failure during watchlist switching left the previously verified stock rows visible while the active tab had already switched to the newly requested watchlist
  - the route also surfaced only a generic load-failure shell instead of explicit stale-refresh truth for the retained selector snapshot

### data-state-audit
- The defect was selector-scoped row provenance rather than first-load envelope truth:
  - the old verified `核心组合` rows were still valid as retained snapshot data
  - what broke was the selector binding, because the route presented those retained rows under the newly selected `成长跟踪` tab

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
- `watchlist-manage-issue-06`
  - Repair target: `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
  - Outcome: fixed in `watchlist-batch-06`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Verified at: 2026-05-05
- Checked routes:
  - `/watchlist/manage`
- Checked states:
  - default
  - watchlist-stock-refresh-failure
- Checked breakpoints:
  - 1440
- Validation notes:
  - component regression now proves that clicking `成长跟踪` after a verified `核心组合` load no longer leaves `.watchlist-tab.active` bound to the failed selector while the old `贵州茅台 / 宁德时代` rows remain visible
  - the same regression now proves the route surfaces `自选列表刷新异常` together with `当前仍显示上次成功同步的自选组合快照。`
  - targeted browser-context verification with system `google-chrome` confirmed the later stock refresh failure keeps `核心组合` active, preserves the verified `贵州茅台 / 宁德时代` rows, and does not leak `比亚迪`
  - the same targeted browser-context proof starts from a successful default `核心组合` snapshot before triggering the later selector-refresh failure

## Residual Risks
- [Low] The selector-refresh failure proof still relies on controlled browser-context fulfillment because the natural PM2 route is healthy and does not reproduce the second-request failure shape on demand.
- [Low] The natural PM2 default success path was not re-run in this micro-batch; the unchanged happy-path shell remains covered by the component regression's initial verified-state assertions plus the controlled success-then-failure browser proof.
- [Low] The repo's default Playwright Chromium runner is still unavailable on this machine, so browser-path verification continues to rely on Playwright-library control of system `google-chrome`.
