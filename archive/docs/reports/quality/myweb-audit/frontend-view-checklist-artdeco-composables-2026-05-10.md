# Frontend View Checklist: `views/artdeco-pages/composables/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/composables/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `useArtDecoDashboard.ts` | Vue composable / route-local dashboard state owner | `/dashboard` support | imported by `ArtDecoDashboard.vue`; imports dashboard/market services, header summary, mock websocket, market kline helper, chart options, and local types | `ArtDecoDashboardLogic.spec.ts`; dashboard audit batches; guard-map | `canonical-support-asset/dashboard-route-local-state` | `not-archive-scope` |
| `useArtDecoDashboard.chart-options.ts` | chart option helper | `/dashboard` support | imported by `useArtDecoDashboard.ts` | dashboard audit docs list it as dashboard support file | `canonical-support-asset/dashboard-chart-options` | `not-archive-scope` |
| `useArtDecoDashboard.types.ts` | TypeScript type definitions | `/dashboard` support | imported by `useArtDecoDashboard.ts` and `useArtDecoDashboard.chart-options.ts` | dashboard audit docs list it as dashboard support file | `canonical-support-asset/dashboard-types` | `not-archive-scope` |
| `useArtDecoTradingManagement.ts` | Vue composable / compatibility shell state | trade-management shell support | imported by `ArtDecoTradingManagement.vue` | `ArtDecoTradingManagement.spec.ts`; root ArtDeco checklist; secondary trade-management governance docs | `compat-support-asset/trade-management-shell-state` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts` routes `/dashboard` to `ArtDecoDashboard.vue`; that view directly consumes `useArtDecoDashboard.ts`.
- `docs/guides/frontend-structure.md` records `/dashboard` as the current ArtDeco exception, so its co-located composable is route-local canonical support rather than orphaned ArtDeco residue.
- `useArtDecoDashboard.chart-options.ts` and `useArtDecoDashboard.types.ts` are not route pages, but they are directly required by the `/dashboard` composable and should stay governed as a dashboard-family support slice.
- `ArtDecoTradingManagement.vue` consumes `useArtDecoTradingManagement.ts` while embedding canonical `/trade/*` pages. The composable therefore follows the compatibility shell lifecycle, not independent archive review.

## Hidden Reference And Guard Evidence

- `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts` imports `useArtDecoDashboard.ts` directly, so dashboard composable changes are guarded outside the Vue route file itself.
- Dashboard audit batches under `docs/reports/quality/myweb-audit/audit-20260426-02/` repeatedly identify `useArtDecoDashboard.ts` as the primary route-local owner for aggregate provenance, refresh binding, fund-flow retention, industry retention, capital-flow tab state, and auxiliary live slices.
- `docs/reports/quality/myweb-audit/dashboard-myweb-audit-2026-05-10.md` lists the dashboard composable, chart-options helper, and types file as the dashboard audit scope.
- `web/frontend/src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts` mocks `useArtDecoTradingManagement.ts`, preserving an explicit test boundary for the compatibility trade shell.
- `frontend-view-guard-map-2026-05-10.json` records many references to `artdeco-pages/composables/useArtDecoDashboard`, confirming this directory cannot be handled by route-only orphan scanning.

## Functional Asset Assessment

- The dashboard composable group is active canonical support for `/dashboard`. It owns route-local data status, freshness/provenance semantics, selector state, chart option projection, header summary synchronization, and verified snapshot retention.
- Keeping dashboard state co-located under `artdeco-pages/composables/` is consistent with the current standard for single-consumer view-local composables. It should not be prematurely moved to global `src/composables/` unless a second active consumer appears.
- `useArtDecoDashboard.chart-options.ts` is a helper rather than a composable, but it is intentionally co-located with the dashboard route state because it only serves that route family.
- `useArtDecoDashboard.types.ts` is a local type support file. It has no independent business lifecycle and should move only if the dashboard route family itself is relocated.
- `useArtDecoTradingManagement.ts` still contains legacy static values and hardcoded options. That is cleanup debt for the compatibility shell, but it is not archive evidence while `ArtDecoTradingManagement.vue` remains retained.

## Redundant Page Decision

No file in this batch is archive-approved.

- Dashboard files are active route-local support for `/dashboard` and are excluded from redundant-page archive flow.
- The trade-management composable is tied to a retained compatibility shell. It can be simplified in a later mutation batch, but should not be archived independently.
- Static or pseudo-live values inside `useArtDecoTradingManagement.ts` should be tracked as shell cleanup debt and removed only with the parent shell lifecycle decision.

## Follow-Up Notes

- If `/dashboard` is later migrated out of `artdeco-pages`, move the composable, chart helper, and local types together as one dashboard-family batch.
- If retiring `ArtDecoTradingManagement.vue`, first map legacy tabs to canonical `/trade/*` routes and decide whether `attribution` remains a static shell or receives a formal successor.
- Do not bulk move this directory into global composables; current evidence supports view-local ownership, not shared global extraction.
