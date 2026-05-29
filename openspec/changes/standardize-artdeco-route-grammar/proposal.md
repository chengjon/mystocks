# Change: Standardize ArtDeco Route Grammar

## Why

Four routed Web ArtDeco pilots now prove the same operational page grammar:

- `web/frontend/src/views/market/Realtime.vue`
- `web/frontend/src/views/risk/Alerts.vue`
- `web/frontend/src/views/trade/Center.vue`
- `web/frontend/src/views/trade/Signals.vue`

The repeated structure is useful, but extracting shared Vue components immediately would be premature. Each route still owns its own data semantics, loading and stale-snapshot orchestration, table or list behavior, fallback copy, and API boundaries.

This change proposes a design-governance standard before component extraction. It defines the ArtDeco route grammar, runtime trust/status vocabulary, route-level E2E hook expectations, and the approval gate for any future shared component work.

## What Changes

- Add an ArtDeco route grammar requirement for data-heavy business routes.
- Standardize the sequence: compact operational header -> first-level review/control lens -> runtime trust/status strip -> primary data surface -> secondary evidence panels.
- Define route-local E2E hook expectations for page craft slices.
- Require runtime trust/status surfaces to expose honest states such as loading, verified, stale, degraded, empty, unavailable, and refresh failure.
- Require shared component extraction to go through a separate approval and contract definition.
- Keep page craft slices explicitly bounded: no router changes, no API contract changes, and no shared component extraction unless separately approved.

## Impact

- Affected spec: `artdeco-design-governance`
- Primary evidence document: `docs/reports/tasks/2026-05-29-artdeco-page-pilot-extraction-analysis.md`
- Primary task plan: `docs/reports/tasks/2026-05-29-artdeco-impeccable-line-summary-and-next-plan.md`
- No frontend runtime code is changed by this proposal itself.
- No route definitions, backend API handlers, OpenAPI contracts, frontend API clients, or shared ArtDeco components are changed by this proposal itself.

## Non-Goals

- Do not create shared Vue components in this change.
- Do not migrate the four pilot pages in this change.
- Do not modify `web/frontend/src/router/index.ts`.
- Do not modify backend API routes or API contract files.
- Do not alter compatibility-era `web/frontend/src/views/artdeco-pages/**` imports.
- Do not archive `add-artdeco-impeccable-design-gate` from the root worktree in this change.
