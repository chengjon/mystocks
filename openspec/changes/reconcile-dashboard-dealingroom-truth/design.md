## Context

The current repository has three overlapping truths for the same home-shell area:

1. Router truth: `/dashboard` renders `ArtDecoDashboard.vue`.
2. Generated page-config truth: `dashboard` maps to `ArtDecoDashboard.vue`.
3. Governed page inventory truth: `DealingRoom` maps to `ArtDecoDashboard.vue` at `/dealing-room`.

At the same time, `TradingDashboard.vue` remains the active implementation for `/trade/terminal`. The approved `restructure-frontend-directory` change still assumes `ArtDecoDashboard.vue` can be moved to `deprecated/`, but that is unsafe while the component remains live under dashboard or DealingRoom semantics.

## Goals

- Pick one canonical route truth for the home shell.
- Preserve backward compatibility for any retained legacy DealingRoom entry point.
- Keep trade-terminal semantics separate from dashboard semantics.
- Remove the unsafe assumption that `ArtDecoDashboard.vue` is already replaceable.

## Decisions

### 1. Canonical route truth is `/dashboard`

`/dashboard` is already the live router target and generated page-config target. Making it canonical minimizes code churn and aligns with existing active specs that still describe a dashboard home shell.

### 2. `DealingRoom` becomes a compatibility alias, not a separate page file

The repo should not keep two competing active truths for the same page component. If `/dealing-room` compatibility is still required, it should redirect to or resolve the canonical dashboard shell.

### 3. `/trade/terminal` stays separate

`TradingDashboard.vue` is an active trade-terminal page with its own verified API family. It must not be renamed to `DealingRoom.vue` while the home-shell truth is being reconciled elsewhere.

### 4. `ArtDecoDashboard.vue` cannot be deprecated yet

Until router truth, generated config truth, and page inventory truth converge, `ArtDecoDashboard.vue` remains an active page and cannot safely move into `deprecated/`.

## Non-Goals

- Redesigning the dashboard UI.
- Refactoring dashboard internals into smaller components.
- Renaming trade-terminal behavior or changing its API contract.
