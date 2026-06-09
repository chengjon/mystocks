# Page Audit Report: /risk/management

## Purpose
Primary routed risk-management workbench for reviewing portfolio-level exposure while exposing a secondary stock-analysis tab for future single-name risk workflows.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/risk/Center.vue`.

### functional-audit
- One high-severity routed defect existed before repair: the `个股分析` tab could not switch in a live browser session and still promised executable single-name risk analysis even though the current routed slice was only an unsupported entry surface.

### data-state-audit
- No separate live single-name contract was found for the stock tab; the approved repair therefore kept the slice honest and page-local instead of fabricating tab-local analysis truth.

### visual-artdeco-audit
- No visual-dominant defect required a separate repair wave in this batch.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a separate repair wave in this batch.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `risk-management-issue-03`
  - Repair target: `web/frontend/src/views/risk/Center.vue`
  - Outcome: fixed in `risk-batch-06`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Verified at: 2026-04-29
- Checked routes:
  - `/risk/management`
- Checked states:
  - default
  - stock-tab
- Checked breakpoints:
  - 1440
- Validation notes:
  - source-level regression now locks the stock-tab metadata to `当前仅保留个股风险分析入口，个股级仓位、止损与波动联动待接入。`
  - component regression now confirms the stock panel renders `个股风险分析入口`, `查看接入说明`, the pending-integration copy, and the non-actionable single-name warning
  - route-family regression now confirms the canonical risk center retains a custom tab button with explicit `type="button"` so the tab switch remains live-browser operable
  - `phase4-mainline-matrix` now includes a dedicated `Risk-Management stock tab degrades unsupported single-name analysis into pending integration copy` route assertion
  - targeted browser verification confirmed the real PM2 `/risk/management` route now selects the stock tab, renders the pending-integration subtitle and panel copy, shows the CTA toast `个股风险分析入口待接入，当前仅保留接入说明与反馈。`, and removes both the old action promise and the old selector-hint copy

## Residual Risks
- [Low] The stock tab is now honest and interactive, but it still has no separate live single-name API contract; a future batch will be needed if the product wants true symbol-level risk analysis.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this path on this machine because the local Playwright chromium bundle is missing.
