# Page Audit Report: /market/lhb

## Purpose
Dragon-tiger leaderboard workbench for reviewing abnormal turnover, net buy/sell flow, and institution-seat participation by trade date.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/market/LHB.vue`

### functional-audit
- The date selector originally changed local state only and did not refetch a date-consistent leaderboard payload.

### data-state-audit
- No separate primary data-state issue was selected for this page in the current batch.

### visual-artdeco-audit
- No primary visual defect was selected for this page in the current batch.

### responsive-a11y-audit
- The original audit snapshot still contained an unsupported `48rem` branch, which was removed in the market shared cleanup wave.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 2
- Low: 0

## Consolidated Issues
- [Medium] The trade-date selector only sliced the currently loaded payload instead of driving a route-consistent query.
- Source roles: functional-audit
- Why consolidated: one page-local interaction defect in the LHB fetch contract
- Primary owner: `web/frontend/src/views/market/LHB.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger: change `今日/昨日/前日` and inspect the request path
- Expected: date selection should drive a date-scoped leaderboard query or be explicitly constrained to loaded dates
- Actual: the original code changed local state only while fetches always used `limit=100`

- [Medium] Unsupported mobile-width responsive branch existed under a desktop-first policy.
- Source roles: responsive-a11y-audit
- Why consolidated: part of the repeated market-domain desktop-policy cleanup
- Primary owner: `web/frontend/src/views/market/LHB.vue`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: inspect the scoped style block and locate `@media (width <= 48rem)`
- Expected: routed market pages should not carry unsupported mobile-width overrides
- Actual: the original audit snapshot still contained the `48rem` branch

## Shared Impact
- Shared component or layout involved: none selected as a cross-page repair owner for the functional fix
- Impact basis: page-local request-parameter truth
- Potentially affected related pages: none selected in this batch
- Follow-up check needed: no

## Repair Plan
- Fix now:
  - convert date selection into a real trade-date-scoped `/v2/market/lhb` request
  - keep selected-date availability truth separate from the currently displayed single-date payload
- Fix with shared-impact review:
  - market-domain desktop-policy cleanup
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-01-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/market/LHB.vue` now tracks a trade-date catalog and maps `今日/昨日/前日` to real `start_date/end_date` query parameters.
- `web/frontend/src/views/market/dragonTigerData.ts` now exports trade-date extraction and query-param helpers.
- `web/frontend/src/views/market/LHB.vue` now refreshes the currently selected date instead of always reloading the unscoped latest payload.
- `web/frontend/src/views/market/LHB.vue` removed the unsupported `@media (width <= 48rem)` branch.

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: Chromium reused the existing PM2 frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: 2026-04-26
- Checked routes:
  - `/market/lhb`
- Checked states:
  - default
  - empty
  - error
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes: targeted Chromium regression confirmed the selector now emits `start_date/end_date` for the chosen trade date, and node coverage confirms the helper-level trade-date catalog/query-param logic.

## Residual Risks
- [Low] Date lookup still depends on the page-local trade-date catalog rather than a full exchange calendar service.
- Reason: the approved batch scope was a frontend-only repair without backend calendar expansion
- Next action: only add a dedicated trading-calendar truth source if a later batch requires dates beyond the currently discoverable leaderboard window
