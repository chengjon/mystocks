# Frontend View Checklist: `useArtDecoDashboard.fetchers.ts`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `composables/useArtDecoDashboard.fetchers.ts` | dashboard fetcher helper | `/dashboard` support | imported by `useArtDecoDashboard.ts` | dashboard route/composable tests and audit docs indirectly cover it through `useArtDecoDashboard.ts` | `canonical-support-asset/dashboard-fetchers` | `not-archive-scope` |

## Evidence

- `useArtDecoDashboard.ts` imports `useDashboardFetchers` from `./useArtDecoDashboard.fetchers.ts`.
- The helper imports `dashboardService`, `marketService`, `extractKlineRows`, and local dashboard types, then centralizes dashboard fetch/update flows.
- `useArtDecoDashboard.ts` contains an explicit comment noting fetch functions were extracted to `useArtDecoDashboard.fetchers.ts`.
- Dashboard tests and audit batches currently exercise this file through the public `useArtDecoDashboard()` boundary rather than by importing the fetcher helper directly.

## Functional Asset Assessment

- This is not a page, but it is an active dashboard route-family support module.
- It owns fetch-side slice synchronization for market overview, fund flow, industry flow, capital-flow ranking, technical indicators, monitoring, strategy, PnL, and stress-test related dashboard state.
- Keeping it co-located with `useArtDecoDashboard.ts` is consistent with view-local dashboard ownership.
- It should not be moved to global composables or API layers unless the dashboard route family is deliberately refactored with a new owner boundary.

## Redundant Page Decision

This file is not archive-approved.

- It is actively imported by the canonical dashboard composable.
- It should move or split only with the `/dashboard` route-family lifecycle.
- If dashboard fetch semantics are refactored later, update the dashboard composable tests and dashboard audit evidence in the same mutation batch.

## Follow-Up Notes

- Merge this row into the primary `artdeco-pages/composables/*` checklist if a generated consolidated inventory is produced later.
- Treat dashboard fetcher changes as dashboard-route changes, not as generic shared transport cleanup.
