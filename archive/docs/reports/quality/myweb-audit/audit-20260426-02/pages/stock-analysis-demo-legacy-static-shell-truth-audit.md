# Page Audit: StockAnalysisDemo Legacy Static Shell Truth

## Scope
- Batch: `secondary-batch-44`
- Execution surface: `code-review-only`
- Owner: `web/frontend/src/views/StockAnalysisDemo.vue`

## Finding
`StockAnalysisDemo.vue` was an unrouted legacy demo shell that orchestrated six child tab pages:

- `StockOverviewTab.vue`
- `StockDataTab.vue`
- `StockStrategyTab.vue`
- `StockBacktestTab.vue`
- `StockRealtimeTab.vue`
- `StockStatusTab.vue`

Those tabs preserved selector-driven demo truth: local TDX parsing examples, screening strategy snippets, RQAlpha backtest metrics, simulated realtime ticker cards, monitoring logs, and integration-status claims. There is no verified one-to-one canonical owner for that aggregate stock-analysis demo workbench.

## Repair
- `StockAnalysisDemo.vue` now renders an honest static shell and points users to `/market/realtime`, `/market/technical`, and `/strategy/backtest`.
- The six child tab components were deleted after confirming `StockAnalysisDemo.vue` was their only consumer.
- `views/styles/StockAnalysisDemo.scss` was deleted after the parent stopped importing it.
- The old style-normalization test was converted into a decommission guard that asserts the retired files stay absent and the parent remains a static shell.

## Cleanup Decision
- Cleanup objects: `web/frontend/src/views/stock-analysis/*Tab.vue`, `web/frontend/src/views/styles/StockAnalysisDemo.scss`, and the now-empty `web/frontend/src/views/stock-analysis/` directory.
- Code-path status: no remaining source imports after `StockAnalysisDemo.vue` stopped importing the tab files and style.
- Functional-tree status: duplicate legacy demo implementation with no active routed owner.
- Deletion basis: preserving the files would keep an orphan selector-driven stock-analysis workbench with pseudo-live and demo-only truth semantics.

## Verification
- RED: `cd web/frontend && npx vitest run src/views/__tests__/StockAnalysisDemo.spec.ts` failed before repair because the page did not render `legacy-static-shell`.
- GREEN: `cd web/frontend && npx vitest run src/views/__tests__/StockAnalysisDemo.spec.ts tests/unit/config/stock-analysis-style-normalization.spec.ts tests/unit/config/root-demo-style-entrypoints.spec.ts` passed `5/5`.
- Secondary inventory: `npm run generate:myweb-audit:secondary-inventory` passed and reduced high-priority items from `11` to `5`.

## Residual Risk
No live browser proof was added because this is an unrouted secondary inventory page with no independent routed proof surface in the current router graph.
