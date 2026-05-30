## ADDED Requirements

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
