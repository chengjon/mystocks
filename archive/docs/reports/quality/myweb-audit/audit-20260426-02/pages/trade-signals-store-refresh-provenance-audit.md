# Page Audit Report: /trade/signals

## Purpose
Canonical trade-signal workbench for reviewing live signal rows, request provenance, and manual refresh behavior on the shared realtime-store route.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/trade/Signals.vue`.
- The same owner continues to feed the trade-facing ArtDeco signal wrapper family, so the current repair stays page-local and wrapper-compatible.

### functional-audit
- No new routed interaction defect required a separate repair wave beyond preserving stale-refresh truth on the existing `刷新信号` workflow.

### data-state-audit
- One high-severity route-truth defect existed before repair:
  - after a verified first load, a resolved `success: false` manual refresh still let shared-store metadata overwrite the hero `REQ_ID / TIME`, cleared routed signal rows, and downgraded the visible shell to faux unavailable truth instead of retaining the current verified snapshot with a stale-data warning

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `trade-signals-issue-03`
  - Repair target: `web/frontend/src/views/trade/Signals.vue`
  - Outcome: fixed in `trade-batch-09`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused where possible
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` plus auth seeding was used to isolate first-load failure and `success -> refresh fail` store-backed signal states
- Verified at: 2026-05-02
- Checked routes:
  - `/trade/signals`
- Checked states:
  - loading
  - error
  - default
- Checked breakpoints:
  - 1440
- Validation notes:
  - browser-context first-load failure verification confirmed the route now renders `COUNT: --`, `DATA: UNAVAILABLE`, `REQ_ID: N/A`, `TIME: N/A`, top-strip `-- / -- / -- / --`, and `trade signals unavailable，当前显示空状态。`
  - the same controlled verification confirmed the failed request id no longer appears anywhere in the visible route shell
  - browser-context success-then-refresh-fail verification confirmed the same route now keeps `COUNT: 3`, `DATA: REAL`, `REQ_ID: REQ-LIVE-TRADE-SIGNALS-SUCCESS`, `TIME: 42.00MS`, preserves `3` visible signal rows, and shows `trade signals refresh unavailable，当前仍显示上次成功同步的交易信号快照。`
  - natural PM2 verification confirmed `/trade/signals` still renders an honest live shell with a real request id and current empty-state summary `0 / 0 / 0 / 未校验`

## Residual Risks
- [Low] Natural PM2 currently returns a valid empty signal set rather than non-empty live rows, so the routed live-success proof for row retention still depends on controlled browser-context verification.
- [Low] The default `npx playwright test` Chromium runner remains unavailable on this machine, so browser proof continues to rely on system-`google-chrome` rather than the repo-bundled Playwright executable.
