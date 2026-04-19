## Context

The completed change `align-artdeco-stateful-primitives-with-design` established two important truths:

- `ArtDecoBadge.vue` is the canonical shared owner for filter-chip and status-chip semantics
- shared overlay token adoption already exists on shared surfaces such as `ArtDecoLoadingOverlay.vue` and `ArtDecoTradeForm.vue`

The remaining drift now sits on the active business-route mainline. Most route hosts remain canonical pages under `views/<domain>/`, but current `main` also routes `/system/data` through `views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`. That means this batch must align active routed surfaces based on router truth, not on directory naming alone, without pretending they are new shared primitives.

## Goals

- remove repeated route-local `status-badge` truth from active business-route pages
- route badge semantics through the approved shared ArtDeco badge contract
- align route-local overlay / drawer / modal backdrop styling with `--ad-overlay-*`
- keep tooltip normalization narrowly scoped to real user-facing tooltip debt rather than broad chart-local restyling

## Non-Goals

- converting all business routes to full ArtDeco workbench structure
- broad cleanup of `views/artdeco-pages/**` beyond canonical router-owned surfaces
- chart tooltip redesign
- layout or router rewrites
- rewriting dialog/drawer behavior logic

## Design Decisions

### Decision 1: Routed pages consume the shared badge owner

Active business routes will not define their own long-lived `status-badge` contract where `ArtDecoBadge.vue` can express the same meaning.

Reason:

- the shared owner is already approved
- route pages should consume shared UI truth, not recreate it
- this reduces semantic drift between workbench pages and canonical routes

### Decision 2: Overlay token adoption applies only where the route already owns the floating UI

Pages such as `WatchlistManagement` and `StatsAnalysis` already own route-local modal/drawer overlays. This batch may align those overlays to `--ad-overlay-*` without extracting new primitives.

Reason:

- these are active routed pages, not shared overlay components
- token alignment is low risk when the structure already exists
- it avoids premature primitive extraction

### Decision 3: Tooltip scope must be proven, not assumed

Native `title` props and component `title` APIs are not automatically tooltip debt. Only confirmed user-facing tooltip-like local implementations should be normalized in this batch.

Reason:

- the audit shows more overlay debt than true tooltip debt
- many `title=` matches are card/dialog titles rather than tooltip surfaces
- this prevents the change from becoming vague or over-scoped

### Decision 4: Business-route work stays distinct from ArtDeco workbench governance

This batch targets canonical routed business surfaces on the current router mainline. It must not reopen broader `views/artdeco-pages/**` cleanup that is already complete, but it may touch a router-owned exception such as `/system/data` when `main` already uses that file as the active route host.

Reason:

- routed pages and workbench pages have different ownership and lifecycle
- scope discipline keeps reviewable risk bounded

## Verification Strategy

Minimum verification:

- `npx vue-tsc --noEmit`
- `npm run build:no-types`
- consumer inspection on each touched route family

Escalation rule:

- if any change touches router wiring, shared layout shell, or global route wrappers, verification must escalate to PM2 + Playwright
