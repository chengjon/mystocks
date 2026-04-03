## ADDED Requirements

### Requirement: Canonical Dashboard Route Truth
The system SHALL treat `/dashboard` as the canonical home / trading-room route backed by `ArtDecoDashboard.vue`.

#### Scenario: Canonical dashboard shell
- **WHEN** a user navigates to `/dashboard`
- **THEN** the router resolves the live home-shell page
- **AND** that page is `ArtDecoDashboard.vue`
- **AND** governed route truth and generated page-config truth both identify `/dashboard` as canonical

#### Scenario: Legacy DealingRoom compatibility
- **GIVEN** historical docs or bookmarks still reference `DealingRoom`
- **WHEN** compatibility support is enabled
- **THEN** `/dealing-room` SHALL redirect to or resolve the same canonical dashboard shell
- **AND** the system SHALL NOT treat `DealingRoom` as a separate active page file

### Requirement: Trade Terminal Separation
The system SHALL keep `/trade/terminal` semantics separate from dashboard / DealingRoom semantics.

#### Scenario: Trade terminal remains distinct
- **WHEN** a user navigates to `/trade/terminal`
- **THEN** the router resolves the trade-terminal implementation
- **AND** that implementation SHALL NOT be renamed to `DealingRoom.vue` as part of dashboard truth reconciliation
