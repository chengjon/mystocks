# Page Audit Report: /risk/stop-loss

## Purpose
Primary routed stop-loss workbench for reviewing the currently derived primary watchlist, quote-backed stop-loss cards, and top-level stop-loss summary counts, owned by `web/frontend/src/views/risk/StopLoss.vue`.

## Agent Findings

### route-inventory
- Canonical route entry remains `web/frontend/src/views/risk/StopLoss.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`, so the repair stays page-local and consumer-compatible.

### functional-audit
- One high-severity routed selector-truth defect remained before repair:
  - the route derived its active selector from the current primary watchlist and could switch that selector on a later refresh
  - if the newly derived selector's stock slice failed before verification, the route still showed the previous watchlist's stop-loss cards, counts, and request provenance

### data-state-audit
- The defect was implicit selector-discovery truth rather than generic stale-refresh retention:
  - the old verified `watchlist:101` cards remained valid only for that selector
  - what broke was the selector binding, because the route treated a route-global verified flag as proof for the newly derived `watchlist:202` selector

### visual-artdeco-audit
- No new visual-dominant defect required a separate repair wave in this batch.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `risk-stop-loss-issue-15`
  - Repair target: `web/frontend/src/views/risk/StopLoss.vue`
  - Outcome: fixed in `risk-batch-15`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Verified at: 2026-05-05
- Checked routes:
  - `/risk/stop-loss`
- Checked states:
  - default
  - selector-switch-refresh-failure
- Checked breakpoints:
  - 1440
- Validation notes:
  - the new owner-level regression now proves that after a verified `watchlist:101` load, switching the derived primary watchlist to `watchlist:202` and failing `watchlist:202/stocks` no longer leaves `REQ_ID: req-stoploss-101-success`, `贵州茅台`, or the old tally cards visible
  - the same regression now proves the route degrades to `REQ_ID: N/A`, `-- / -- / -- / --`, and `0` cards together with `watchlist 202 stocks unavailable，当前暂无已验证止损快照。`
  - targeted browser-context verification with system `google-chrome` confirmed the same success-then-derived-selector-failure path on the routed shell

## Residual Risks
- [Low] The selector-switch refresh-failure proof still relies on controlled browser-context fulfillment because the natural PM2 route is healthy and does not reproduce the second-request failure shape on demand.
- [Low] The natural PM2 default success path was not re-run in this micro-batch; the unchanged happy-path shell remains covered by the owner regression's initial verified-state assertions plus the controlled success-then-failure browser proof.
- [Low] The repo's default Playwright Chromium runner is still unavailable on this machine, so browser-path verification continues to rely on Playwright-library control of system `google-chrome`.
