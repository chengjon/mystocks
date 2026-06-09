# Frontend View Checklist: ArtDeco Coverage Delta

> Date: 2026-05-10
> Scope: coverage reconciliation for ArtDeco files found after the main per-directory batches
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Delta Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `components/DashboardMarketPanorama.vue` | Vue dashboard support component | `/dashboard` support | imported by `ArtDecoDashboard.vue` | dashboard route/composable audits; guard-map source references | `canonical-support-asset/dashboard-market-panorama` | `not-archive-scope` |
| `strategy-tabs/components/styles/BacktestHeader.scss` | SCSS support style | `/strategy/backtest` support | imported by `BacktestHeader.vue` | strategy-tabs checklist covers component style group | `canonical-support-asset/backtest-header-style` | `not-archive-scope` |
| `strategy-tabs/components/styles/BacktestKpiGrid.scss` | SCSS support style | `/strategy/backtest` support | imported by `BacktestKpiGrid.vue` | `BacktestKpiGrid.spec.ts`; strategy audit docs and guard-map | `canonical-support-asset/backtest-kpi-style` | `not-archive-scope` |
| `strategy-tabs/components/styles/BacktestWorkbenchTabs.scss` | SCSS support style | `/strategy/backtest` support | imported by `BacktestWorkbenchTabs.vue` | strategy backtest audit docs and guard-map | `canonical-support-asset/backtest-tabs-style` | `not-archive-scope` |

## Why This Delta Exists

- The main `components/*` checklist covered the directory but omitted the existing `DashboardMarketPanorama.vue` row.
- The main `strategy-tabs/*` checklist classified `styles/*.scss and components/styles/*.scss` as a group; this delta records the nested component style files explicitly so the coverage inventory is auditable at file level.
- No runtime code changed in this batch.

## Evidence

- `ArtDecoDashboard.vue` imports `DashboardMarketPanorama` from `./components/DashboardMarketPanorama.vue`.
- `DashboardMarketPanorama.vue` renders dashboard market/fund-flow/sentiment slices from props passed by the dashboard route and should follow the `/dashboard` route-family lifecycle.
- `BacktestHeader.vue` imports `@use './styles/BacktestHeader'`.
- `BacktestKpiGrid.vue` imports `@use './styles/BacktestKpiGrid'`.
- `BacktestWorkbenchTabs.vue` imports `@use './styles/BacktestWorkbenchTabs'`.
- `frontend-view-guard-map-2026-05-10.json` records `BacktestWorkbenchTabs.scss` and `BacktestKpiGrid.scss`; strategy audit docs also cite those files as repair/verification assets.

## Redundant Page Decision

No file in this delta is archive-approved.

- `DashboardMarketPanorama.vue` is active dashboard route support and should move only with the `/dashboard` route family.
- Nested backtest styles are active support assets for canonical `/strategy/backtest` components.
- This delta does not change prior conclusions for inactive candidate components; it only closes explicit file-level coverage gaps.

## Follow-Up Notes

- If the components checklist is later consolidated into a single generated inventory, merge this delta row back into the primary `components/*` table.
- If `/strategy/backtest` component styles are relocated, move the three nested style files together with their owning Vue components and tests.
