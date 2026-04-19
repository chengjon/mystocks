# Change: Align Business-Route Status And Tooltip Surfaces

## Why

The completed ArtDeco shared-primitive batch closed chip/status ownership and shared overlay token adoption inside `components/artdeco/**` and `views/artdeco-pages/**`, but the active business-route mainline still carries local UI truth in several routed pages:

- repeated page-level `status-badge` implementations in `system`, `strategy`, `market`, and `monitoring`
- route-local overlay / modal / drawer backdrop styling that still hardcodes background, blur, and z-index instead of using the active token contract
- sparse but still possible tooltip-like local implementations that should not become a third visual truth alongside shared primitives and ArtDeco workbench pages

Without a separate reviewed change, the project will keep two frontend governance tracks:

- shared ArtDeco surfaces aligned with `DESIGN.md`
- active routed pages continuing to drift via local badge and floating-surface styling

## What Changes

- align active business-route `status-badge` surfaces to the canonical ArtDeco badge semantics instead of repeated local styling
- align route-local overlay / drawer / modal backdrops with the active `--ad-overlay-*` token contract where those pages already own floating UI
- audit business-route tooltip-like local implementations and only normalize the ones that are true user-facing tooltip debt
- keep the change scoped to active routed pages and shared route-level surfaces, not ArtDeco workbench blocks that were already handled

## Implementation Boundary

Primary route targets identified by the current audit:

- `web/frontend/src/views/system/DataSource.vue`
- `web/frontend/src/views/system/DatabaseMonitor.vue`
- `web/frontend/src/views/strategy/ResultsQuery.vue`
- `web/frontend/src/views/strategy/StrategyList.vue`
- `web/frontend/src/views/market/MarketDataView.vue`
- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/strategy/styles/StatsAnalysis.scss`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`

Supporting truth sources:

- `DESIGN.md`
- `web/frontend/src/styles/artdeco-tokens.scss`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `openspec/changes/align-artdeco-stateful-primitives-with-design/`

## Non-Goals

- responsive cleanup
- chart-local tooltip styling normalization
- workbench-page cleanup under `views/artdeco-pages/**`
- route/layout shell rewrites
- replacing Element Plus behavior contracts
- broad visual redesign of business routes

## Impact

- Affected specs: `artdeco-design-governance`
- Affected code: active business-route pages and their local styles in `views/system`, `views/strategy`, `views/market`, and `views/monitoring`
- Risk: medium, because the change touches active routed pages, but bounded by keeping ownership and token decisions anchored to the already approved ArtDeco primitive contract

## Success Criteria

- active routed pages no longer define repeated local `status-badge` truth where `ArtDecoBadge.vue` can own the semantics
- route-local overlay/backdrop surfaces bind to `--ad-overlay-*` tokens where the route already owns the floating UI
- any true route-level tooltip debt is normalized without expanding into chart-local tooltip restyling
- the change stays within active business-route scope and does not reopen the completed ArtDeco workbench batch
