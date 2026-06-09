# Frontend View Checklist: `views/artdeco-pages/market-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/market-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` | Vue compatibility wrapper | no direct route/menu owner | wraps `views/market/Realtime.vue` | `domain-body-migration-ownership.spec.ts`; guard-map | `compat-retained/market-realtime-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` | Vue compatibility wrapper | no direct route/menu owner | wraps `views/market/Technical.vue` | `MarketKLineTab.spec.ts`; `domain-body-migration-ownership.spec.ts`; guard-map | `compat-retained/market-technical-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue` | Vue compatibility wrapper | no direct route/menu owner | wraps `views/data/Concepts.vue` | `MarketConceptTab.spec.ts`; `domain-body-migration-ownership.spec.ts`; guard-map | `compat-retained/data-concepts-wrapper` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketETFTab.vue` | Vue embedded ETF panel | no direct route/menu owner found | no current source importer found in focused scan | inventory + guard-map references | `candidate-review/etf-embedded-panel` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/market-tabs/marketRealtimeData.ts` | helper re-export | canonical market support | re-exports `views/market/marketRealtimeData` | node test; guard-map | `compat-support-reexport/market-realtime-data` | `not-archive-scope` |
| `web/frontend/src/views/artdeco-pages/market-tabs/marketKlineData.ts` | helper re-export | canonical market support | re-exports `views/market/marketKlineData`; imported by dashboard composable through legacy path | node test; guard-map; detail audit manifests | `compat-support-reexport/market-kline-data` | `not-archive-scope` |
| `web/frontend/src/views/artdeco-pages/market-tabs/marketConceptData.ts` | helper re-export | canonical data support | re-exports `views/data/marketConceptData` | node test; guard-map | `compat-support-reexport/data-concept-data` | `not-archive-scope` |

## Route And Menu Truth

- `router/index.ts`: current market/data route owners remain under `views/market/*` and `views/data/*`, not under `artdeco-pages/market-tabs/*`.
- `MenuConfig.ts`: market and data are current formal domains, but no direct menu item points to the ArtDeco market tab files.
- `MarketRealtimeTab.vue`, `MarketKLineTab.vue`, and `MarketConceptTab.vue` now delegate to canonical route bodies.
- `MarketETFTab.vue` does not appear to be imported by current source code in the focused scan and is not current `/market/etf` truth.

## Hidden Reference And Guard Evidence

- `web/frontend/tests/unit/config/domain-body-migration-ownership.spec.ts` explicitly asserts canonical ownership moved to `views/market/Realtime.vue`, `views/market/Technical.vue`, and `views/data/Concepts.vue`, while the ArtDeco tab paths remain as legacy wrappers.
- `MarketKLineTab.spec.ts` and `MarketConceptTab.spec.ts` still mount the compatibility wrappers and verify the canonical data request behavior through the wrapped pages.
- `marketKlineData.ts`, `marketRealtimeData.ts`, and `marketConceptData.ts` are compatibility re-exports, not independent helper implementations.
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts` imports `extractKlineRows` through the legacy `market-tabs/marketKlineData.ts` path, so the re-export has active compatibility value.
- `frontend-view-guard-map-2026-05-10.json` contains references for all four tab Vue files and the three helper re-export files.

## Functional Asset Assessment

- The realtime, K-line, and concept tab Vue files are thin compatibility wrappers. They should stay until wrapper-retention and legacy import decisions are handled in an approved mutation batch.
- The three `market*Data.ts` files are compatibility re-exports over canonical data modules; they should not be archived as unused duplicates while tests or legacy consumers still import them.
- `MarketETFTab.vue` contains a standalone ETF workbench with stats strip, selector-like refresh behavior, `/v1/market/etf` call, and a hardcoded fallback dataset. This creates a pseudo-live/fallback-literal risk and overlaps with `views/market/Etf.vue`, which was previously classified as a non-routed honest static shell.
- Because `MarketETFTab.vue` has UI and data-contract ideas that might be absorbed into a future canonical ETF route, it is not archive-approved in this documentation batch.

## Redundant Page Decision

No file in this batch is archive-approved.

- `MarketRealtimeTab.vue`, `MarketKLineTab.vue`, and `MarketConceptTab.vue` remain `compat-retained/*` wrappers.
- `marketRealtimeData.ts`, `marketKlineData.ts`, and `marketConceptData.ts` remain `compat-support-reexport/*` assets.
- `MarketETFTab.vue` remains `candidate-review/etf-embedded-panel` because it is not current route truth but still needs an absorption/retirement decision against the market ETF shell and any future ETF canonical owner.

## Follow-Up Notes

- If retiring market wrapper paths, update `domain-body-migration-ownership.spec.ts`, wrapper-specific specs, and any legacy imports in the same approved mutation batch.
- If relocating or removing `marketKlineData.ts` re-export, first update `useArtDecoDashboard.ts` and related guard-map expectations.
- For `MarketETFTab.vue`, decide whether ETF should be a canonical market route, a static non-production shell, or an archived demo asset; do not preserve its hardcoded fallback as production truth.
