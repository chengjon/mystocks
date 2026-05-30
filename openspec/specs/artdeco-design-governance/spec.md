# artdeco-design-governance Specification

## Purpose
Define ArtDeco frontend design-governance requirements for shared primitive ownership, tokenized visual states, routed-page status/overlay/tooltip cleanup, and the boundary between canonical routed pages, workbench pages, compatibility layers, and shared design primitives.
## Requirements
### Requirement: Routed Pages Consume Canonical Status Surfaces

The system SHALL require active business-route pages to consume canonical ArtDeco status-chip semantics instead of keeping repeated page-local `status-badge` truth where shared badge ownership is sufficient.

#### Scenario: A routed page renders status labels
- **WHEN** a canonical routed page under `views/<domain>/` needs a capsule-style status label
- **THEN** it SHALL use the approved shared badge ownership surface for the semantics where practical
- **AND** page-local status badge styling SHALL NOT remain the primary truth for those meanings

#### Scenario: A routed page already uses a local status-badge class
- **WHEN** that routed page is touched for status-surface cleanup
- **THEN** the local badge contract SHALL be mapped to the shared ArtDeco status semantics
- **AND** the redundant route-local style truth SHALL be removed or reduced so it no longer acts as a competing semantic source

### Requirement: Routed Overlay Surfaces Follow Active Overlay Tokens

The system SHALL require route-owned overlays, drawers, and modal backdrops to follow the active overlay token contract where those pages already own floating-surface rendering.

#### Scenario: A routed page owns a modal or drawer backdrop
- **WHEN** a canonical routed page defines its own overlay, backdrop, drawer shell, or modal shell
- **THEN** the backdrop styling SHALL bind to the active `--ad-overlay-*` token contract
- **AND** the change SHALL preserve the page's existing behavior contract rather than rewriting the UI flow

### Requirement: Routed Tooltip Debt Must Be Explicitly Proven

The system SHALL treat tooltip cleanup in active business routes as opt-in by evidence, not by broad text search alone.

#### Scenario: A route contains `title` attributes or tooltip-like markup
- **WHEN** a routed-page cleanup batch audits tooltip debt
- **THEN** it SHALL distinguish true user-facing tooltip implementations from component titles, dialog titles, and chart-local tooltip systems
- **AND** only confirmed tooltip debt SHALL be normalized within the routed-page batch

### Requirement: Routed-Page Cleanup Must Stay Distinct From Workbench Cleanup

The system SHALL keep canonical routed-page surface governance separate from completed ArtDeco workbench-page cleanup.

#### Scenario: A routed-page cleanup proposal is implemented
- **WHEN** the batch targets `views/<domain>/` pages
- **THEN** it SHALL NOT reopen `views/artdeco-pages/**` cleanup inside the same change
- **AND** it SHALL preserve the approved ownership split between routed pages, workbench pages, and shared primitives

### Requirement: ArtDeco Design Contract Precedence

The system SHALL treat `DESIGN.md` as the experience-strategy truth for active ArtDeco frontend work, with runtime and placement governance documents refining implementation boundaries rather than replacing the design contract.

#### Scenario: A new ArtDeco frontend batch is prepared
- **WHEN** a new ArtDeco implementation batch is defined
- **THEN** the batch SHALL derive its experience direction from `DESIGN.md`
- **AND** SHALL use active `web/` governance documents to determine runtime and placement boundaries
- **AND** SHALL NOT use historical V3 summaries or compatibility redirect files as co-equal truth sources

### Requirement: Shared Primitive State-Machine Adoption

The system SHALL adopt the `--ad-*` state-machine token model on canonical shared ArtDeco primitives before attempting broad page-level rollout.

#### Scenario: Shared primitive state behavior is modernized
- **WHEN** a shared ArtDeco primitive such as button, input, or card is updated for state behavior
- **THEN** its visual state expression SHALL bind to the `--ad-*` token system where the current design contract defines those states
- **AND** the change SHALL remain limited to visual-state expression rather than replacing the underlying behavior contract

#### Scenario: Page-level cleanup is proposed in the same batch
- **WHEN** a batch begins to expand from shared primitives into broad page-by-page token adoption
- **THEN** that expansion SHALL be treated as out of scope for the primitive-adoption batch
- **AND** it SHALL require a separate reviewed change

### Requirement: Canonical Shared Semantic Surfaces

The system SHALL assign filter-chip and status-chip semantics to canonical shared surfaces instead of leaving them as repeated page-local styling patterns.

#### Scenario: Filter-chip semantics are implemented
- **WHEN** a reusable filter-chip-like surface is introduced or updated
- **THEN** the implementation SHALL use one canonical shared ownership surface
- **AND** page-local inline styling SHALL NOT become the primary truth for filter-chip semantics

#### Scenario: Status semantics are implemented
- **WHEN** reusable status-chip or badge semantics are updated
- **THEN** the implementation SHALL align with the approved `DESIGN.md` semantic set for values such as warning, holding, pending, profit, and loss where supported
- **AND** the batch SHALL avoid creating competing semantic implementations across multiple shared surfaces without ownership clarity

### Requirement: Compatibility Layers Stay Non-Canonical

The system SHALL keep ArtDeco compatibility style files as bridges only during shared primitive modernization.

#### Scenario: Primitive work encounters compatibility-era variables
- **WHEN** shared primitive adoption touches paths that still depend on compatibility-era variables
- **THEN** the batch SHALL resolve the primitive against canonical token truth where practical
- **AND** SHALL NOT create new runtime truth in `artdeco-main.css`, `artdeco-variables.css`, or `artdeco-colors.css`

### Requirement: Decorative Corner Marker Exception Preservation

The system SHALL preserve the approved runtime exception that decorative corner markers remain globally disabled unless overlap and collision issues are explicitly resolved in a later reviewed change.

#### Scenario: A design enhancement proposal touches decorative chrome
- **WHEN** an ArtDeco frontend batch proposes stronger decorative framing
- **THEN** it MAY reuse geometric language conceptually
- **BUT** it SHALL NOT re-enable global decorative corner marker elements in runtime without a separately reviewed change that proves non-overlapping behavior

### Requirement: ArtDeco Routed Page Grammar

The system SHALL govern data-heavy ArtDeco business routes with a documented route grammar before extracting shared page-structure components.

#### Scenario: A data-heavy ArtDeco route is shaped or crafted
- **WHEN** a canonical route under `web/frontend/src/views/<domain>/` is selected for ArtDeco page work
- **THEN** the route brief SHALL evaluate the sequence `compact operational header -> first-level review/control lens -> runtime trust/status strip -> primary data surface -> secondary evidence panels`
- **AND** deviations from that sequence SHALL be recorded in the critique, shape brief, implementation report, or route-specific design document
- **AND** the route grammar SHALL NOT by itself require router, API contract, frontend API client, or shared component changes

#### Scenario: A route grammar pattern repeats across pages
- **WHEN** multiple page pilots prove the same route grammar
- **THEN** the repeated structure SHALL be documented as design governance before a shared Vue component is created
- **AND** the documentation SHALL distinguish reusable layout grammar from route-local data semantics and orchestration

### Requirement: Runtime Trust Strip Vocabulary

The system SHALL require route-level runtime trust or status strips to expose honest data-state vocabulary instead of hiding loading, stale, degraded, empty, unavailable, or refresh-failure conditions behind generic decoration.

#### Scenario: A route renders live or derived data
- **WHEN** a route displays market, risk, position, signal, or other operational data
- **THEN** its runtime trust/status surface SHALL expose whether the route is loading, verified, refreshing, stale, degraded, empty, unavailable, or failed during refresh when those states apply
- **AND** the state copy SHALL be route-specific enough for the user to understand whether the primary data surface is actionable

#### Scenario: A refresh fails after verified data exists
- **WHEN** a refresh request fails but the route still has a previously verified snapshot
- **THEN** the route SHALL keep the verified snapshot visible when that is the existing route behavior
- **AND** the trust/status surface SHALL identify the displayed data as stale or degraded rather than replacing it with an unrelated empty state

### Requirement: Route-Level Verification Hooks

The system SHALL define stable route-level verification hooks for ArtDeco page craft work so E2E tests verify user-visible route surfaces rather than brittle nested implementation details.

#### Scenario: A page craft slice adds or updates route-level surfaces
- **WHEN** a page craft slice adds or changes a header, control lens, trust/status strip, primary data surface, runtime message, empty state, unavailable state, refresh action, or retry action
- **THEN** the route SHALL expose stable route-level test hooks for those user-visible surfaces where practical
- **AND** the E2E tests SHALL prefer those route-level hooks over selectors that depend on shared component internals

#### Scenario: A prior pilot lacks route-level hooks
- **WHEN** a future approved batch touches an earlier pilot that lacks route-level verification hooks
- **THEN** the batch SHALL either add hooks inside the approved route-local scope or record why hook alignment is deferred
- **AND** hook alignment SHALL NOT be used as a reason to modify API contracts, router definitions, or shared components in the same batch

### Requirement: Shared Component Extraction Approval Gate

The system SHALL require a separate reviewed proposal before turning repeated ArtDeco route grammar into shared Vue components.

#### Scenario: A shared ArtDeco route component is proposed
- **WHEN** a shared component such as a route header band, review lens, runtime trust strip, primary data surface shell, or route verification hook helper is proposed
- **THEN** the proposal SHALL define props, slots, events, supported runtime state vocabulary, route-local ownership boundaries, token requirements, E2E hook naming, migration order, and rollback behavior
- **AND** it SHALL prove that the component has enough routed consumers to justify extraction
- **AND** it SHALL NOT own API orchestration, route metadata, router configuration, backend contracts, frontend API clients, or financial row semantics

#### Scenario: Page-specific semantics are found during extraction
- **WHEN** a candidate shared component would need route-specific labels, API normalization, stale snapshot logic, fallback copy, or table/list row semantics
- **THEN** those concerns SHALL remain route-local unless a later approved proposal defines a narrower shared contract
- **AND** the extraction SHALL be reduced, deferred, or rejected rather than creating a broad component that hides route behavior
