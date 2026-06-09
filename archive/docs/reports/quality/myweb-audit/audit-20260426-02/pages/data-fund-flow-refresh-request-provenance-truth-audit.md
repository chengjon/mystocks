# Page Audit Report: /data/fund-flow

## Purpose
Canonical fund-flow workbench for northbound summary review, trend observation, ranking reordering, and top-level request provenance on a routed data page.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/data/FundFlow.vue`.
- The same owner is also imported by `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`, so the repair stays page-local and wrapper-compatible.

### functional-audit
- No new routed interaction defect required a separate repair wave beyond restoring honest stale-refresh request provenance.

### data-state-audit
- One high-severity route-truth defect remained before repair:
  - a failed ranking refresh could overwrite hero `REQ` even while the previous verified ranking snapshot and its `2` visible rows were still on screen

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `data-fund-flow-issue-03`
  - Repair target: `web/frontend/src/views/data/FundFlow.vue`
  - Outcome: fixed in `data-batch-15`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused where possible
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - authenticated browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate first-load failure and stale-refresh failure states
- Verified at: 2026-05-03
- Checked routes:
  - `/data/fund-flow`
- Checked states:
  - first-load failure
  - stale-refresh failure
  - natural PM2 observation
- Checked breakpoints:
  - 1440
- Validation notes:
  - browser-context first-load failure verification confirmed the route continues to render `ROWS: --` and `REQ: N/A` without leaking failed summary or ranking request ids
  - browser-context success-then-refresh-fail verification confirmed the route now keeps `REQ: req-data-b15-ranking-success`, preserves the `2`-row ranking summary, and still shows `贵州茅台`
  - natural PM2 observation currently bounces through `/dashboard -> /login` after the route first mounts in this environment, so it is recorded as environment observation only rather than success proof for this batch

## Residual Risks
- [Low] Natural PM2 `/data/fund-flow` success proof is not claimed in this batch because the environment currently re-enters `/dashboard -> /login` after initial route mount.
- [Low] The default `npx playwright test` Chromium runner remains unavailable on this machine, so browser proof continues to rely on system `google-chrome` rather than the repo-bundled Playwright executable.
