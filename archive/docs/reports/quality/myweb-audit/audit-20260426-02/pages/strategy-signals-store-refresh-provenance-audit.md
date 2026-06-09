# Page Audit Report: /strategy/signals

## Purpose
Canonical strategy-domain signal workbench for reviewing live strategy signal timelines, request provenance, and manual refresh behavior on the shared realtime-store route owner `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`.
- The same routed owner is imported by `web/frontend/src/views/watchlist/Signals.vue`, so consumer safety had to be spot-checked while keeping the repair page-local.

### functional-audit
- No new routed interaction defect required a separate repair wave beyond preserving honest stale-refresh truth on the existing `刷新信号` workflow.

### data-state-audit
- One high-severity route-truth defect existed before repair:
  - after a verified first load, a resolved `success: false` manual refresh still let shared-store metadata overwrite the visible `REQ_ID`, could clear routed signal rows, and could downgrade the route toward faux unavailable truth instead of retaining the current verified snapshot with a stale-data warning

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `strategy-signals-issue-02`
  - Repair target: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - Shared impact: `/watchlist/signals` consumer inherits the same owner fix
  - Outcome: fixed in `strategy-batch-09`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused where possible
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` plus auth seeding was used to isolate first-load failure and `success -> refresh fail` store-backed signal states
- Verified at: 2026-05-02
- Checked routes:
  - `/strategy/signals`
  - `/watchlist/signals` (consumer spot-check)
- Checked states:
  - error
  - default
  - empty
- Checked breakpoints:
  - 1440
- Validation notes:
  - browser-context first-load failure verification confirmed the route now renders `REQ_ID: N/A`, `COUNT: --`, top-strip `-- / -- / -- / --`, and `策略信号加载失败 / strategy signals unavailable`
  - the same controlled verification confirmed the failed request id no longer appears anywhere in the visible route shell
  - browser-context success-then-refresh-fail verification confirmed the same route now keeps `REQ_ID: req-live-strategy-signals-success`, preserves `COUNT: 2` plus the visible `贵州茅台` and `宁德时代` rows, and shows `strategy signals refresh unavailable，当前仍显示上次成功同步的策略信号快照。`
  - natural PM2 verification confirmed `/strategy/signals` still renders an honest live empty-state shell with a real request id plus `0 / 0 / 0 / 0`
  - natural PM2 verification confirmed `/watchlist/signals` still renders the watchlist-specific shell with `FOCUS: WATCHLIST`, a real request id, zero `.artdeco-stat-change` nodes, and honest `0 / 0 / 0 / 0` tally cards

## Residual Risks
- [Low] Natural PM2 currently returns an empty live signal set rather than non-empty rows, so the routed row-retention proof still depends on controlled browser-context verification.
- [Low] The default `npx playwright test` Chromium runner remains unavailable on this machine, so browser proof continues to rely on system `google-chrome` rather than the repo-bundled Playwright executable.
