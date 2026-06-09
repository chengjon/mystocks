# Page Audit Report: /data/fund-flow

## Purpose
数据域的资金流向总览页，展示北向资金概览、趋势图和个股排行。

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/data/FundFlow.vue`
- Routed from `/data/fund-flow`

### functional-audit
- Ranking controls and refresh actions are present, but not live-verified.

### data-state-audit
- Partial API failure currently clears unrelated successful data surfaces.

### visual-artdeco-audit
- Core hierarchy is clear, with hero -> stats -> chart/ranking structure.

### responsive-a11y-audit
- Shared responsive cleanup removed the unsupported `48rem` branch for this page.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 1
- Low: 0

## Consolidated Issues
- [High] One failed subrequest collapses the entire page into an empty/default data surface.
- Source roles: data-state-audit
- Why consolidated: The same fetch branch clears summary, trend, and ranking together.
- Primary owner: `web/frontend/src/views/data/fundFlowPageData.ts`
- Fix bucket: `fix-now`
- Reproduction or trigger: Inspect `fetchFundFlowData` and follow the `summary === null || bigDeal === null` branch.
- Expected: Successful subresponses should be preserved and only the missing subsection should degrade.
- Actual: All internal data stores are reset to defaults if either request fails.

- [Medium] Unsupported mobile-width responsive branch exists under a desktop-only page contract.
- Source roles: responsive-a11y-audit
- Why consolidated: Same issue pattern appears across the data domain.
- Primary owner: `web/frontend/src/views/data/FundFlow.vue`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: Inspect the scoped style block and locate `@media (width <= 48rem)`.
- Expected: Desktop-only pages should not carry unsupported mobile branch logic.
- Actual: The 48rem style branch existed in the original audit snapshot and was removed in the shared cleanup wave.

## Shared Impact
- Shared component or layout involved: none confirmed for the partial-success bug
- Impact basis: local fetch orchestration bug; repeated responsive pattern for style redline
- Potentially affected related pages: `/data/industry`, `/data/concept`, `/data/indicator` for the responsive branch pattern
- Follow-up check needed: yes

## Repair Plan
- Fix now: partial-success degradation
- Fix with shared-impact review: responsive redline cleanup
- Deferred: none
- Approval status: `approved`

## Fixes Applied
- `web/frontend/src/views/data/fundFlowPageData.ts`: added partial-merge helper to preserve successful overview surfaces.
- `web/frontend/src/views/data/FundFlow.vue`: replaced global reset branch with partial-success merge behavior.
- `web/frontend/src/views/data/FundFlow.vue`: removed the unsupported `@media (width <= 48rem)` branch and folded remaining layout protection into the desktop breakpoint.
- `web/frontend/src/views/artdeco-pages/market-data-tabs/fundFlowPageData.ts`: corrected re-export path for node test compatibility.
- `web/frontend/src/views/artdeco-pages/market-data-tabs/__node_tests__/fundFlowPageData.test.ts`: added partial-merge coverage.

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: Chromium reused the existing PM2 frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: code review plus targeted Playwright route verification
- Checked routes: `/data/fund-flow`
- Checked states: default, loading, error, empty
- Checked breakpoints: desktop policy reviewed from code only; no live viewport execution
- Validation notes: Node partial-merge test passes. Targeted Playwright Phase 2 matrix checks passed for success and empty-state flows on `/data/fund-flow`. The batch GitNexus staged verdict remained `passed-low-risk` from isolated batch-only scope.

## Residual Risks
- [Low] Live breakpoint-specific layout verification remains outstanding
- Reason: targeted live verification covered route success and empty-state behavior, but not explicit desktop breakpoint assertions for this page
- Next action: add a focused viewport-aware Playwright check if page-specific layout proof is required
