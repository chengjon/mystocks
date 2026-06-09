# Page Audit Report: /risk/overview

## Purpose
Primary routed risk-governance overview workbench for reviewing risk rules, alert records, and overview-state messaging.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/risk/Overview.vue`.

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring truthful alert-tab and KPI behavior.

### data-state-audit
- One medium-severity hybrid live-surface truth defect existed before repair: the page loaded real rule data but kept embedded alert messages and fabricated KPI metrics on the same primary routed surface.

### visual-artdeco-audit
- No visual-dominant defect required a repair wave in this batch.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave in this batch.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- `risk-overview-issue-01`
  - Repair target: `web/frontend/src/views/risk/Overview.vue`
  - Outcome: fixed in `risk-batch-01`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Verified at: 2026-04-28
- Checked routes:
  - `/risk/overview`
- Checked states:
  - default
  - loading
  - empty
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - routed-page regression now confirms the canonical page requests live alert records and shows `暂无预警消息。` when the alerts payload is empty
  - wrapper-retention regression now confirms the canonical risk overview page keeps both `getAlertRules()` and `getAlerts({ page: 1, page_size: 50 })` wired into `src/views/risk/Overview.vue`
  - targeted logged-in browser verification confirmed the live routed page issues real `GET /api/v1/monitoring/alert-rules` and `GET /api/v1/monitoring/alerts?page=1&page_size=50` requests
  - the live KPI strip now shows `仓位集中度 未校验`, and the overview table shows `组合Beta`, `波动率(20日)`, `最大回撤(近3月)`, and `VaR(95%)` as `未校验 / 待接入`
  - the live alert tab now shows `暂无预警消息。` and no longer displays the embedded placeholder alert strings

## Residual Risks
- [Low] The routed `/risk/overview` page now labels KPI and overview slices honestly, but those metrics remain unconnected until a dedicated live risk-summary contract is introduced in a later batch.
- [Low] The strengthened routed-page E2E expectations were updated, but the repo's default `npx playwright test` Chromium runner still cannot execute this path on this machine because the local Playwright chromium bundle is missing.
