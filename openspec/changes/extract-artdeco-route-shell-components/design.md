# Design: ArtDeco Route Shell Component Extraction

## Scope

This proposal may introduce shared route shell components for repeated ArtDeco page structure. The target is structural consistency and verification stability, not business logic reuse.

Candidate components:

- `ArtDecoRouteHeader`
- `ArtDecoRuntimeStrip`
- `ArtDecoControlLens`
- `ArtDecoDataSurface`
- `ArtDecoRouteEvidencePanel`

These names are provisional. Implementation may choose narrower names if the approved contract is smaller.

## Ownership Boundaries

Shared components may own:

- Layout slots.
- Visual token binding.
- Standard status tone presentation.
- Stable hook passthrough.
- Basic responsive or desktop density behavior already approved by the current ArtDeco design system.

Shared components must not own:

- API orchestration.
- Route metadata.
- Router configuration.
- Backend contracts or OpenAPI schemas.
- Frontend API clients.
- Stale snapshot state machines.
- Domain row semantics.
- Page-specific fallback copy.
- Route-specific filtering or sorting logic.

## Contract Shape

Each component must define:

- Props: visual tone, title/subtitle/copy, status vocabulary, hook prefix, loading state where visual only.
- Slots: route-local controls, primary content, secondary evidence, actions, metadata.
- Events: only visual or user-action pass-through events; route-specific effects stay in the page.
- Hooks: stable `data-testid` passthrough using route prefix and approved suffixes.
- Tokens: use existing ArtDeco tokens; no new raw color or spacing truth.

## Migration Order

1. Choose one previously aligned low-risk route.
2. Add or update focused E2E coverage before migrating.
3. Replace only one shell surface at a time.
4. Preserve route-level hooks and existing user-visible copy.
5. Run focused E2E, token check, `impeccable --json`, eslint, type-check, PM2 status, OpenSpec validation, and GitNexus staged detect.
6. Record the route-specific migration report.
7. Continue to the next route only after the previous route is verified.

Suggested first migration candidates:

- `/trade/positions`
- `/trade/portfolio`
- `/risk/alerts`

Avoid starting with `/market/realtime` because it is the original high-value pilot and has denser market runtime behavior.

## Rollback Plan

Each migration must remain reversible by restoring the route-local shell markup for the touched surface. Do not combine route shell extraction with API, router, or behavior changes in the same commit.
