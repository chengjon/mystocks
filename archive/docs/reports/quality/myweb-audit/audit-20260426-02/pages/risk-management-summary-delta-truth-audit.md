# Page Audit: /risk/management

## Scope
- Route: `/risk/management`
- Canonical entry: `web/frontend/src/views/risk/Center.vue`
- Batch: `risk-batch-13`

## Defect Summary
- The canonical risk-management route rendered secondary `%` rows under `总资产` and `今日收益` even though the live positions contract only proved `total_market_value`, `total_profit_loss`, and `total_profit_loss_percent`.
- Before repair, `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts` reused `total_profit_loss_percent` for both `totalAssetsChange` and `todayProfitChange`, and `ArtDecoRiskStatsGrid.vue` presented those values as if they were verified per-card change baselines.
- The same surface leaked `+0%` on natural empty-success payloads, which falsely implied a supported comparison baseline even when the route only proved absolute totals.

## Repair
- Changed `RiskMetrics.totalAssetsChange` and `RiskMetrics.todayProfitChange` to nullable summary-delta fields.
- Changed `toRiskManagementMetrics()` to keep those fields unresolved when the current positions contract only proves holdings totals plus aggregate PnL ratio.
- Changed `ArtDecoRiskStatsGrid.vue` to degrade unsupported secondary delta rows to explicit `待接入` copy instead of rendering `%` values.
- Added node-level, owner-component, and routed-matrix regressions so the same holdings-derived summary-delta leak cannot return.
- Promoted `myweb-audit v1.49` summary-delta truth guidance for future holdings/exposure routes.

## Verification
- Node regression:
  - `node --test web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementData.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementHelpers.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementModulePresence.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/stopLossMonitorData.test.ts` passed `17/17`
- Component regression:
  - `npx vitest run src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts` passed `2/2`
- Risk family regression:
  - `npx vitest run src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStockPanel.spec.ts` passed `35/35`
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` listed `27` tests including the strengthened `/risk/management` stats-grid assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - natural PM2 `/risk/management` now renders `总资产 / ¥0 / 待接入` and `今日收益 / +¥0 / 待接入`, and no longer shows `+0%`
  - controlled browser-context fulfillment with `total_profit_loss_percent: 1.84` now renders `总资产 / ¥372,664 / 待接入` and `今日收益 / +¥6,844 / 待接入`, and no longer leaks `+1.84%`

## Skill Feedback
- This page required a new skill-version bump. `myweb-audit v1.49` now explicitly blocks holdings or exposure pages from reusing aggregate PnL ratios or zero placeholders as faux summary-delta truth for unrelated cards.
