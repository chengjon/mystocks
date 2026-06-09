# Page Audit Report: /strategy/opt

## Purpose
Strategy optimization workbench for reviewing candidate strategies, carrying optimization score context, and writing approved optimization context back into repository, parameter, and backtest routes.

## Agent Findings

### route-inventory
- Routed wrapper: `web/frontend/src/views/strategy/Optimization.vue`
- Canonical downstream owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`

### functional-audit
- No separate batch-dominant click-flow defect was selected beyond the writeback truth boundary.

### data-state-audit
- The page silently fell back to mock candidates on real fetch failure while keeping real writeback affordances enabled before repair.

### visual-artdeco-audit
- No primary visual ArtDeco defect was selected for this page in the current batch.

### responsive-a11y-audit
- The page stylesheet still carried an unsupported `48rem` branch before the shared secondary-strategy cleanup wave.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 2
- Low: 0

## Consolidated Issues
- [Medium] The optimization workbench silently switched to mock candidates while preserving writeback actions as if the real optimization chain were healthy.
- Source roles: data-state-audit
- Why consolidated: one owner controlled both the false fallback state and the unsafe continuation of cross-tab writeback
- Primary owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger:
  - open `/strategy/opt?strategyId=101`
  - force `strategyApi.getStrategies({})` failure or invalid payload
  - inspect source badge, empty state, and writeback actions
- Expected: route-level real fetch failure should show an explicit degraded state and keep mock candidates from being written into strategy context
- Actual: the page dropped to mock rows and preserved writeback affordances

- [Medium] Secondary strategy routed pages should remove unsupported `48rem` responsive branches under the desktop-first baseline.
- Source roles: responsive-a11y-audit
- Why consolidated: same repeated breakpoint policy defect also existed on `/strategy/signals` and `/strategy/gpu`
- Primary owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: inspect `ArtDecoStrategyOptimization.scss` for `@media (width <= 48rem)`
- Expected: current supported strategy routes keep only desktop-relevant breakpoints
- Actual: `/strategy/opt` still carried a `48rem` branch

## Shared Impact
- Shared component or layout involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationSourcePolicy.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss`
- Impact basis: optimization writeback fans out to repository, parameters, and backtest context, so false fallback rows create cross-tab contamination risk
- Potentially affected related pages:
  - `/strategy/repo`
  - `/strategy/parameters`
  - `/strategy/backtest`
- Follow-up check needed: yes

## Repair Plan
- Fix now:
  - keep routed `/strategy/opt` in an explicit unavailable state on real fetch failure or invalid payload
  - allow mock fallback only for embedded/demo surfaces
  - disable writeback whenever row source is not real
- Fix with shared-impact review:
  - remove the unsupported `48rem` branch from the optimization stylesheet
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-02-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationSourcePolicy.ts`
  - extracted explicit source policy helpers for route-level fallback and writeback gating
- `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyOptimizationViewModel.ts`
  - aligned exported source type with the new route/source policy
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
  - introduced explicit `unavailable` source state for routed real-page failures
  - limited mock fallback to embedded contexts only
  - disabled and guarded writeback whenever source is not real
  - added explicit degraded-state and mock-state notices
- `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss`
  - removed the unsupported `@media (width <= 48rem)` branch
- Verification support:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyOptimizationSourcePolicy.test.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - live verification used a Playwright-library Chromium-compatible script against system `google-chrome` with `serviceWorkers: 'block'`
- Verified at: 2026-04-26
- Checked routes:
  - `/strategy/opt`
- Checked states:
  - default
  - empty
  - error
  - disabled
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `node --test web/frontend/src/views/artdeco-pages/strategy-tabs/__node_tests__/strategyOptimizationSourcePolicy.test.ts` passed `3/3`
  - `timeout 180s npm run type-check` passed
  - custom Chromium-compatible browser verification against `http://127.0.0.1:3020/strategy/opt?strategyId=101` with forced strategy-list failure passed `1/1`
  - `rg -n "@media \\(width <= 48rem\\)" web/frontend/src/views/artdeco-pages/strategy-tabs/styles/StrategySignalsTab.scss web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss web/frontend/src/views/strategy/styles/BacktestGPU.scss` returned no matches

## Residual Risks
- [Low] The routed optimization page now blocks false fallback writeback, but embedded consumers still need deliberate review before they rely on mock fallback semantics.
- Reason: this batch preserved embedded/demo flexibility while explicitly tightening the canonical routed page.
- Next action: if a later strategy-center batch audits embedded consumers such as `ArtDecoTradingCenter`, confirm whether those surfaces should keep mock fallback or move to the same explicit unavailable-state contract.
