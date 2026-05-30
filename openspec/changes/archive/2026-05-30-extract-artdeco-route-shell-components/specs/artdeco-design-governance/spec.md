## ADDED Requirements

### Requirement: ArtDeco Route Shell Component Extraction

The system SHALL extract shared ArtDeco route shell components only after route grammar evidence proves repeated structure and an approved proposal defines the component contracts, ownership boundaries, migration order, and rollback plan.

#### Scenario: A shared route shell component is approved for implementation
- **WHEN** a shared component such as a route header, runtime strip, control lens, data surface shell, or evidence panel is selected for implementation
- **THEN** the approved contract SHALL define props, slots, events, route hook passthrough, supported runtime vocabulary, token rules, candidate consumers, migration order, and rollback behavior
- **AND** the implementation SHALL preserve route-level `data-testid` hooks or provide an explicitly mapped replacement with equivalent E2E coverage
- **AND** the implementation SHALL use existing ArtDeco tokens rather than creating new raw visual values

#### Scenario: A route is migrated to a shared route shell component
- **WHEN** a canonical routed page adopts a shared ArtDeco route shell component
- **THEN** route-specific API orchestration, data normalization, stale snapshot logic, fallback copy, financial row semantics, filtering behavior, and route metadata SHALL remain route-local
- **AND** the migration SHALL NOT modify router definitions, backend API handlers, OpenAPI contracts, or frontend API clients in the same batch
- **AND** focused E2E coverage SHALL verify the migrated route surface before and after the migration

#### Scenario: Extraction scope grows during implementation
- **WHEN** a route shell extraction batch discovers behavior that requires shared ownership of domain-specific data, copy, API calls, or row semantics
- **THEN** that behavior SHALL remain route-local or the extraction SHALL stop for a narrower proposal
- **AND** the batch SHALL NOT broaden the shared component contract without a separate reviewed proposal
