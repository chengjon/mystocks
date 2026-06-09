# Page Audit Report: /data/indicator

## Purpose
数据分析中心，承载指标库、指标编辑器、智能选股和筛选结果。

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/data/Advanced.vue`
- Routed from `/data/indicator`
- Truth mismatch noted between router meta and generated page config API endpoint

### functional-audit
- Indicator-condition controls do not affect screening results.
- Indicator-card select and result-row click affordances were inert in the original audit snapshot.

### data-state-audit
- Route meta and generated page config disagree on canonical API truth.

### visual-artdeco-audit
- Layout is coherent, but the editor area is a placeholder rather than a completed interaction surface.

### responsive-a11y-audit
- Shared responsive cleanup removed the unsupported `48rem` branches from the page and target analysis child components.

## Issue Summary
- Blocking: 0
- High: 2
- Medium: 2
- Low: 0

## Consolidated Issues
- [High] Smart-screener indicator conditions are exposed in the UI but never participate in the screening path.
- Source roles: functional-audit
- Why consolidated: The control path is visibly present but disconnected from the filtering logic.
- Primary owner: `web/frontend/src/composables/market/useDataAnalysis.ts`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: Inspect `AnalysisScreener.vue` controls and `useDataAnalysis.applyScreening`.
- Expected: Added indicator conditions should influence results.
- Actual: `screeningFilters.indicators` is ignored.

- [High] Indicator-card and results-row click affordances are dead-end interactions.
- Source roles: functional-audit
- Why consolidated: Child components emit events, but parent handlers are empty.
- Primary owner: `web/frontend/src/composables/market/useDataAnalysis.ts`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: Inspect `selectIndicator` and `handleRowClick` in Advanced.vue.
- Expected: Clicks should open a detail flow, update context, or be explicitly disabled.
- Actual: Both handlers are empty functions.

- [Medium] Router meta and generated page config disagree on the page's API truth.
- Source roles: route-inventory, data-state-audit
- Why consolidated: The same page is described with different canonical APIs.
- Primary owner: `scripts/dev/tools/generate-page-config.js`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: Compare router meta and generated `pageConfig`.
- Expected: One canonical API truth for the page.
- Actual: `/api/v1/indicators/registry` vs `/api/data/indicator`.

- [Medium] Unsupported mobile-width responsive branch exists under a desktop-only page contract.
- Source roles: responsive-a11y-audit
- Why consolidated: Same issue pattern appears across the data domain.
- Primary owner: `web/frontend/src/views/data/Advanced.vue`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: Inspect the scoped style block and locate `@media (width <= 48rem)`.
- Expected: Desktop-only pages should not carry unsupported mobile branch logic.
- Actual: The 48rem branches existed in the original audit snapshot and were removed in the shared cleanup wave.

## Shared Impact
- Shared component or layout involved: `useDataAnalysis`, `AnalysisIndicators`, `AnalysisScreener`, `AnalysisResults`
- Impact basis: shared composable change and generated config truth mismatch
- Potentially affected related pages: wrapper consumers of `Advanced.vue`, any automation consuming `pageConfig['data-indicator']`
- Follow-up check needed: yes

## Repair Plan
- Fix now:
  - replace misleading indicator-condition flow with explicit unsupported-state messaging
  - replace inert click paths with real indicator/stock context behavior
  - align generated page-config API truth with router meta
- Fix with shared-impact review:
  - `useDataAnalysis`
  - `AnalysisScreener`
  - generator input for `pageConfig.ts`
- `Advanced.vue`
- `AnalysisIndicators.vue`
- Deferred: none
- Approval status: `approved`

## Fixes Applied
- `web/frontend/src/composables/market/useDataAnalysis.ts`: added explicit unsupported-state handling for indicator conditions and real selected-indicator/selected-stock state transitions.
- `web/frontend/src/views/data/Advanced.vue`: replaced empty handlers with visible context behavior and passed support-state props into the screener.
- `web/frontend/src/views/artdeco-pages/components/AnalysisScreener.vue`: disabled unsupported indicator-condition controls and added visible support messaging.
- `web/frontend/src/views/data/Advanced.vue`: removed the unsupported `@media (width <= 48rem)` branch.
- `web/frontend/src/views/artdeco-pages/components/AnalysisIndicators.vue`: removed the unsupported `@media (width <= 48rem)` branch.
- `web/frontend/src/views/artdeco-pages/components/AnalysisScreener.vue`: removed the unsupported `@media (width <= 48rem)` branch.
- `scripts/dev/tools/generate-page-config.js`: aligned generator truth for `data-indicator`.
- `web/frontend/src/config/pageConfig.ts`: regenerated to emit `/api/v1/indicators/registry`.

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: Chromium reused the existing PM2 frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: code review plus targeted Playwright route verification
- Checked routes: `/data/indicator`
- Checked states: default, error
- Checked breakpoints: desktop policy reviewed from code only; no live viewport execution
- Validation notes: Page-config generator refresh completed successfully. Targeted Playwright Phase 2 matrix checks passed for success and error-state flows on `/data/indicator`, and focused interaction checks passed for selected-indicator and selected-stock context flows. The batch GitNexus staged verdict remained `passed-low-risk` from isolated batch-only scope.

## Residual Risks
- [Low] Desktop-only breakpoint compliance is still derived from code review rather than live multi-viewport execution
- Reason: the responsive cleanup was verified structurally and through existing desktop Chromium runs, but not through additional manual viewport sweeps
- Next action: if a later batch expands responsive verification, add explicit 1920/1440/1280 screenshot or assertion coverage for the shared analysis workbench
