# Frontend View Checklist: `views/artdeco-pages/stock-management-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/stock-management-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue` | Vue routed surface owner | `/watchlist/manage` via `views/watchlist/Manage.vue` | imported by `views/watchlist/Manage.vue` and `ArtDecoStockManagement.vue` | `views/watchlist/__tests__/Manage.spec.ts`; guard-map; watchlist audit manifests | `canonical-surface-owner/watchlist-manage` | `not-archive-scope` |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/PortfolioMonitor.vue` | Vue embedded portfolio panel | no direct route/menu owner | imported by `ArtDecoStockManagement.vue` | node tests cover shared portfolio extractors; guard-map | `candidate-review/embedded-portfolio-monitor` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts` | helper module | watchlist and stock-management support | imported by `stores/apiStores.ts`, `WatchlistManager.vue`, and `PortfolioMonitor.vue` | `stockManagementRouteData.test.ts`; watchlist audit manifests | `canonical-support-asset/watchlist-data-normalizer` | `not-archive-scope` |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteActions.ts` | helper module | watchlist import/export support | imported by `WatchlistManager.vue` | `stockManagementRouteActions.test.ts` | `canonical-support-asset/watchlist-import-export` | `not-archive-scope` |

## Route And Menu Truth

- `MenuConfig.ts`: current watchlist menu contains `/watchlist/manage`, `/watchlist/signals`, and `/watchlist/screener`; current trade menu contains `/trade/portfolio`.
- `router/index.ts`: `/watchlist/manage` imports `web/frontend/src/views/watchlist/Manage.vue`.
- `views/watchlist/Manage.vue`: thin wrapper that imports `WatchlistManager.vue` from this directory.
- `ArtDecoStockManagement.vue`: imports both `WatchlistManager.vue` and `PortfolioMonitor.vue` as embedded tab panels.
- Current `/trade/portfolio` route uses canonical trade portfolio surfaces, not `PortfolioMonitor.vue`.

## Hidden Reference And Guard Evidence

- `web/frontend/src/stores/apiStores.ts` imports `extractMonitoringWatchlists` and `extractMonitoringWatchlistStocks` from `stockManagementRouteData.ts`, so the helper is cross-cutting route support and not local dead code.
- `web/frontend/src/views/watchlist/__tests__/Manage.spec.ts` mounts the actual routed owner `WatchlistManager.vue` and verifies count-card, pending-state, selector, stale-snapshot, and row-provenance behavior.
- `stockManagementRouteData.test.ts` covers watchlist summary normalization, watchlist stock normalization, failure-envelope handling, portfolio position row mapping, and portfolio card stats.
- Historical myweb-audit watchlist batches repeatedly identify `WatchlistManager.vue` as the primary routed surface owner for `/watchlist/manage`.
- `frontend-view-guard-map-2026-05-10.json` contains repeated references to `WatchlistManager.vue`, `PortfolioMonitor.vue`, and route data helpers.

## Functional Asset Assessment

- `WatchlistManager.vue` is active production route surface through the canonical wrapper `views/watchlist/Manage.vue`; it must be excluded from redundant-page archive flow.
- `stockManagementRouteData.ts` is a shared normalization layer for monitoring watchlists and watchlist stocks, plus portfolio monitor mapping; its current location is legacy ArtDeco-local, but its usage is active.
- `stockManagementRouteActions.ts` is tied to `WatchlistManager.vue` import/export behavior and has direct node-test coverage.
- `PortfolioMonitor.vue` is not current `/trade/portfolio` truth, but it is still embedded in `ArtDecoStockManagement.vue` and reuses verified `/v1/trade/positions` extractors. It should be treated as an embedded asset or absorption candidate, not a direct archive candidate.
- `ArtDecoStockManagement.vue` itself still has a stats strip and tab shell around watchlist/portfolio flows; lifecycle decisions for `PortfolioMonitor.vue` should be made with that parent surface.

## Redundant Page Decision

No file in this batch is archive-approved.

- `WatchlistManager.vue`, `stockManagementRouteData.ts`, and `stockManagementRouteActions.ts` are active route/support assets and are outside archive scope.
- `PortfolioMonitor.vue` remains `candidate-review/embedded-portfolio-monitor` because it is not the `/trade/portfolio` route truth but is still imported by `ArtDecoStockManagement.vue` and contains reusable portfolio monitoring structure.
- Any future relocation should first choose the canonical owner for the watchlist normalization helpers. Moving them from `artdeco-pages/*` into `views/watchlist/*` or shared stores would be a mutation/refactor batch, not a documentation-only archive decision.

## Follow-Up Notes

- Review `ArtDecoStockManagement.vue` in the later root ArtDeco batch before deciding whether `PortfolioMonitor.vue` should be absorbed into canonical `/trade/portfolio`, retained as embedded stock-management context, or retired.
- If relocating `stockManagementRouteData.ts`, update `stores/apiStores.ts`, `WatchlistManager.vue`, `PortfolioMonitor.vue`, and node tests in one approved mutation batch.
- Do not classify `WatchlistManager.vue` as redundant because it sits under `artdeco-pages`; the active route wrapper currently delegates to it as the actual `/watchlist/manage` surface owner.
