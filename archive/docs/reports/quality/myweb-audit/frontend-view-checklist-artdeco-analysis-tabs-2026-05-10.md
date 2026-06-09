# Frontend View Checklist: `views/artdeco-pages/analysis-tabs/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/analysis-tabs/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` | Vue page | `/detail/graphics/:symbol`, route name `stock-graphics` | dynamic import in `router/index.ts` | `KLineAnalysis.spec.ts`, `pageConfig.ts`, detail-audit reports | `canonical-active/detail-route-owner` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/analysis-tabs/BacktestAnalysis.vue` | Vue embedded/prototype page | no current route/menu owner found | no current source importer found in focused scan | inventory/docs references only | `candidate-review/legacy-embedded-backtest-prototype` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts` | owner regression test | n/a | tests `KLineAnalysis.vue` directly | request provenance, stale snapshot, indicator slice truth | `active-route-owner-test` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts` currently routes `detail/graphics/:symbol` to `@/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.
- `pageConfig.ts` registers route name `stock-graphics` with component `KLineAnalysis.vue`.
- No direct `MenuConfig.ts` owner is expected for `KLineAnalysis.vue` because it is a detail route, not a primary menu page.
- No current route/menu owner was found for `analysis-tabs/BacktestAnalysis.vue`.

## Hidden Reference And Guard Evidence

- `KLineAnalysis.vue` has direct owner tests in `web/frontend/src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts`.
- Existing myweb-audit reports identify `KLineAnalysis.vue` as the canonical detail graphics owner and track previous fixes around selector/request provenance and indicator-slice refresh truth.
- `BacktestAnalysis.vue` appears in historical docs and inventory as an embedded ArtDeco analysis asset, but focused current-source search did not find an active importer.
- The current canonical strategy backtest route resolves through `web/frontend/src/views/strategy/Backtest.vue`, which delegates to `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`.

## Functional Asset Assessment

### `KLineAnalysis.vue`

- Owns active detail route behavior for stock graphics.
- Maintains route-scoped symbol/period state.
- Fetches K-line data through `dataApi.getKline`.
- Fetches technical indicators through `dashboardService.getTechnicalIndicatorsSafe`.
- Preserves verified snapshot provenance, request id display, stale-refresh behavior, and independent indicator-slice error states.

### `BacktestAnalysis.vue`

- Implements a compact embedded backtest prototype with stats cards, run action, and equity curve chart.
- It does not appear to be the current canonical backtest route owner.
- It overlaps conceptually with canonical `strategy/Backtest.vue` and `ArtDecoBacktestAnalysis.vue`, but should not be archived by static non-import evidence alone.
- If retained value exists, it is likely limited to layout/visual ideas or simplified embedded backtest presentation, not route truth.

## Redundant Page Decision

No file in this batch is archive-approved.

- `KLineAnalysis.vue` is an active canonical detail-route owner and is excluded from redundant-page archive flow.
- `KLineAnalysis.spec.ts` is active owner coverage and must remain with the route owner.
- `BacktestAnalysis.vue` remains `candidate-review/legacy-embedded-backtest-prototype`; archive eligibility requires a separate approved mutation batch that records successor mapping to canonical strategy backtest, confirms no hidden dynamic import, and explicitly decides whether any stats/chart/run-action presentation should be absorbed first.

## Follow-Up Notes

- Do not group `analysis-tabs/*` as one lifecycle bucket. The directory contains both an active detail route owner and an unrouted legacy embedded prototype.
- If `BacktestAnalysis.vue` is later proposed for archive, compare it against `views/strategy/Backtest.vue` and `views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` first.
- Any future change to `KLineAnalysis.vue` should run its owner regression spec because previous audits fixed request provenance, selector-owned snapshot state, and indicator-slice freshness behavior.
