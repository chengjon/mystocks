## ADDED Requirements

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
