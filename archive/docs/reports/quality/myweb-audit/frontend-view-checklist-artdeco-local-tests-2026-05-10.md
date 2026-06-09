# Frontend View Checklist: `views/artdeco-pages/**/__tests__` and `__node_tests__`

> Date: 2026-05-10
> Scope: local Vitest and Node test files under `web/frontend/src/views/artdeco-pages/`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

Current filesystem count: 48 local ArtDeco test files.

| Group | Count | Test Role | Lifecycle Result | Archive Status |
| --- | ---: | --- | --- | --- |
| Root shell tests | 1 | guards `ArtDecoTradingManagement.vue` shell behavior | `active-guard/trade-management-shell` | `not-archive-approved` |
| Template tests | 3 | guards reusable page template and template composable helpers | `active-guard/template-governance` | `not-archive-approved` |
| Analysis tests | 1 | guards `KLineAnalysis.vue` route/detail behavior | `active-guard/detail-kline` | `not-archive-approved` |
| Market-data tests | 8 | guards wrappers, static shells, and helper data re-exports | `active-guard/market-data-compat` | `not-archive-approved` |
| Market-tab tests | 5 | guards market wrappers and helper re-exports | `active-guard/market-tab-compat` | `not-archive-approved` |
| Portfolio tests | 1 | guards portfolio data helper used by canonical trade portfolio | `active-guard/trade-portfolio-support` | `not-archive-approved` |
| Risk tests | 8 | guards risk wrappers, canonical support panels, data helpers, and module presence | `active-guard/risk-support` | `not-archive-approved` |
| Stock-management tests | 2 | guards watchlist route data/action helpers | `active-guard/watchlist-support` | `not-archive-approved` |
| Strategy tests | 11 | guards strategy route bodies, helpers, styles/components, lifecycle/source policy, and signals data | `active-guard/strategy-support` | `not-archive-approved` |
| System tests | 5 | guards system wrapper/data/settings support assets | `active-guard/system-support` | `not-archive-approved` |
| Trading tests | 3 | guards legacy trading wrappers and transform helpers | `active-guard/trading-compat` | `not-archive-approved` |

## Representative Files

- `__tests__/ArtDecoTradingManagement.spec.ts`
- `_templates/__tests__/ArtDecoPageTemplate.spec.ts`
- `_templates/composables/__tests__/useArtDecoPageTemplate.spec.ts`
- `_templates/composables/__node_tests__/useArtDecoPageTemplateHelpers.test.ts`
- `analysis-tabs/__tests__/KLineAnalysis.spec.ts`
- `market-data-tabs/__tests__/ArtDecoMarketOverview.spec.ts`
- `market-data-tabs/__node_tests__/fundFlowPageData.test.ts`
- `market-tabs/__tests__/MarketKLineTab.spec.ts`
- `risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts`
- `risk-tabs/__node_tests__/riskManagementModulePresence.test.ts`
- `strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts`
- `strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts`
- `system-tabs/__tests__/ArtDecoSystemSettings.spec.ts`
- `trading-tabs/__tests__/tradingDataTransform.spec.ts`

## Evidence

- `find web/frontend/src/views/artdeco-pages -path '*/__tests__/*' -o -path '*/__node_tests__/*' | wc -l` returned `48`.
- The guard map records many of these tests as direct references, including high-reference strategy, system, and risk specs.
- Existing per-directory checklists already cite these tests as guard evidence for wrappers, static shells, helper re-exports, and canonical support assets.
- Historical audit closeouts repeatedly use these tests as verification commands for dashboard, detail, market, risk, strategy, system, trade, and secondary shell repairs.

## Functional Asset Assessment

- These files are test/guard assets, not pages. They must not be counted as redundant views.
- A test file may become removable only when its guarded production asset is formally retired, migrated, or replaced, and the successor guard is updated in the same approved mutation batch.
- Node tests under `__node_tests__` are especially important for non-Vue helper modules and re-export compatibility contracts that are not visible through router/menu scans.
- Local tests that guard honest static shells are still active governance assets until the static shell itself is retired with explicit approval.

## Redundant Page Decision

No test file in this batch is archive-approved.

- Do not bulk archive local ArtDeco tests as part of page cleanup.
- Do not delete a test because the guarded component is not a router entry; many reviewed ArtDeco assets are compatibility wrappers or canonical support assets.
- If a future mutation batch archives a page or helper, update or retire only the directly related tests in that same batch, with the successor or `no-successor-needed` rationale recorded.

## Follow-Up Notes

- Keep test lifecycle decisions coupled to the corresponding production checklist.
- Before any approved archive move, search for both `__tests__` and `__node_tests__` references, not just Vue route imports.
- Treat guard retirement as a first-class mutation task, not as incidental cleanup.
