# Frontend View Checklist: `views/artdeco-pages/market-data-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/market-data-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ArtDecoIndustryAnalysis.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/data/Industry.vue` | `domain-body-migration-ownership.spec.ts`; data audit docs | `compat-retained/data-industry-wrapper` | `not-archive-approved` |
| `DragonTigerAnalysis.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoMarketData.vue`; wraps `views/market/LHB.vue` | `domain-body-migration-ownership.spec.ts`; market audit docs | `compat-retained/market-lhb-wrapper` | `not-archive-approved` |
| `FundFlowAnalysis.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoMarketData.vue`; wraps `views/data/FundFlow.vue` | `FundFlowAnalysis.spec.ts`; `domain-body-migration-ownership.spec.ts`; data audit docs | `compat-retained/data-fund-flow-wrapper` | `not-archive-approved` |
| `ArtDecoRealtimeMonitor.vue` | Vue compatibility wrapper | no direct route/menu owner | `ArtDecoTradingCenter.vue`; wraps `views/market/Realtime.vue` | `ArtDecoRealtimeMonitor.spec.ts`; secondary manifests | `compat-retained/market-realtime-wrapper` | `not-archive-approved` |
| `ArtDecoMarketOverview.vue` | Vue static shell | no direct route/menu owner | `ArtDecoTradingCenter.vue` function key `market-overview` | `ArtDecoMarketOverview.spec.ts`; secondary manifests | `candidate-review/static-market-overview-shell` | `not-archive-approved` |
| `ArtDecoMarketAnalysis.vue` | Vue static shell | no direct route/menu owner | `ArtDecoTradingCenter.vue` function key `market-analysis` | `ArtDecoMarketAnalysis.spec.ts`; secondary manifests | `candidate-review/static-market-analysis-shell` | `not-archive-approved` |
| `AuctionAnalysis.vue` | Vue embedded tab asset | no direct route/menu owner | `ArtDecoMarketData.vue` tab `auction` | inventory + guard-map references | `candidate-review/embedded-auction-panel` | `not-archive-approved` |
| `ConceptAnalysis.vue` | Vue embedded tab asset | no direct route/menu owner | `ArtDecoMarketData.vue` tab `concepts` | inventory + guard-map references | `candidate-review/embedded-concept-panel` | `not-archive-approved` |
| `DataQualityPanel.vue` | Vue embedded tab asset | no direct route/menu owner | `ArtDecoMarketData.vue` tab `data-quality` | inventory + guard-map references | `candidate-review/embedded-data-quality-panel` | `not-archive-approved` |
| `ETFAnalysis.vue` | Vue embedded tab asset | no direct route/menu owner | `ArtDecoMarketData.vue` tab `etf` | inventory + guard-map references | `candidate-review/embedded-etf-panel` | `not-archive-approved` |
| `FundFlow.vue` | Vue legacy fund-flow panel | no direct route/menu owner found | no current source importer found in focused scan | inventory + guard-map references | `candidate-review/legacy-fund-flow-panel` | `not-archive-approved` |
| `dragonTigerData.ts` | helper re-export | canonical market support | re-exports `views/market/dragonTigerData` | node tests + market audit manifests | `compat-support-reexport/dragon-tiger-data` | `not-archive-scope` |
| `industryAnalysisData.ts` | helper re-export | canonical data support | re-exports `views/data/industryAnalysisData` | node tests/specs + data audit manifests | `compat-support-reexport/industry-data` | `not-archive-scope` |
| `fundFlowPageData.ts` | helper re-export | canonical data support | re-exports `views/data/fundFlowPageData.ts` | node tests + data audit manifests | `compat-support-reexport/fund-flow-data` | `not-archive-scope` |

## Route And Menu Truth

- `router/index.ts`: current route truth for these capabilities is under `views/market/*` and `views/data/*`, not directly under `artdeco-pages/market-data-tabs/*`.
- `ArtDecoTradingCenter.vue`: still imports `ArtDecoMarketOverview.vue`, `ArtDecoRealtimeMonitor.vue`, `ArtDecoMarketAnalysis.vue`, and `ArtDecoIndustryAnalysis.vue` into its function-tree component map.
- `ArtDecoMarketData.vue`: still imports `DataQualityPanel.vue`, `FundFlowAnalysis.vue`, `ETFAnalysis.vue`, `ConceptAnalysis.vue`, `DragonTigerAnalysis.vue`, and `AuctionAnalysis.vue` as internal tabs.
- `FundFlow.vue` did not show a current source importer in the focused scan, but it is still present in inventory and guard-map outputs, so it is not archive-approved without a successor decision.

## Hidden Reference And Guard Evidence

- `domain-body-migration-ownership.spec.ts` confirms canonical ownership moved from ArtDeco wrappers into `views/market/LHB.vue`, `views/data/Industry.vue`, and `views/data/FundFlow.vue`.
- `ArtDecoRealtimeMonitor.spec.ts` verifies the wrapper delegates to canonical market realtime instead of a placeholder shell.
- `ArtDecoMarketOverview.spec.ts` and `ArtDecoMarketAnalysis.spec.ts` verify those two panels are honest static shells and must not show fake `REQ_ID` or placeholder live state.
- `FundFlowAnalysis.spec.ts` still mounts the wrapper path.
- `dragonTigerData.ts`, `industryAnalysisData.ts`, and `fundFlowPageData.ts` are compatibility re-exports, with node/spec tests and historical audit manifests tied to the canonical data helpers.

## Functional Asset Assessment

- Wrapper files are compatibility bridges and should stay until their legacy paths are intentionally retired with tests updated in the same approved mutation batch.
- `ArtDecoMarketOverview.vue` and `ArtDecoMarketAnalysis.vue` are already degraded static shells. They are not production truth, but they are guarded as honest non-live shells.
- `AuctionAnalysis.vue`, `ConceptAnalysis.vue`, `DataQualityPanel.vue`, and `ETFAnalysis.vue` are still used by `ArtDecoMarketData.vue`; they contain reusable tab UI but depend on parent-provided local datasets rather than current canonical route truth.
- `FundFlow.vue` and the older fund-flow tab implementation contain historical static/local data patterns and should be compared against canonical `views/data/FundFlow.vue` before any archive move.

## Redundant Page Decision

No file in this batch is archive-approved.

- Active compatibility wrappers and helper re-exports are excluded from archive flow.
- Static shells remain `candidate-review/*` because their tests currently define the expected non-live behavior.
- Embedded tab assets remain `candidate-review/*` until `ArtDecoMarketData.vue` itself is reviewed and either retired, absorbed, or mapped to canonical successors.

## Follow-Up Notes

- Review `ArtDecoMarketData.vue` in the later root ArtDeco batch; its lifecycle determines the child tabs.
- If retiring static shells, first update or remove `ArtDecoMarketOverview.spec.ts` and `ArtDecoMarketAnalysis.spec.ts` with explicit approval.
- If relocating helper re-exports, update node tests and all legacy imports in a single mutation batch.
