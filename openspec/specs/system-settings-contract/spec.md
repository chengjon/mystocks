# system-settings-contract Specification

## Purpose
Define the sectioned System-Config contract so each settings section has a single canonical owner, explicit evidence semantics, and section-level migration exit criteria instead of page-level mixed-truth behavior.
## Requirements
### Requirement: Sectioned System-Config Ownership

The system SHALL define `System-Config` as a sectioned contract in which each section has exactly one canonical owner, scope, and write path.

#### Scenario: Mixed-scope ownership is explicit
- **WHEN** an operator or developer inspects the `System-Config` contract
- **THEN** `general`, `datasource`, and `security` SHALL be marked as system-scoped sections
- **AND** `notification` SHALL be marked as a user-scoped section
- **AND** each section SHALL declare its canonical owner rather than relying on page-level convention

#### Scenario: Duplicate storage layers are rejected
- **WHEN** a rollout proposes a second persistence path, compatibility store, or long-lived shim for an existing section
- **THEN** the change SHALL be treated as non-compliant
- **AND** the section SHALL continue using its current canonical owner until a governed migration is approved

### Requirement: Unified Page Contract Without Monolithic Truth

The system SHALL support a unified `System-Config` page contract without redefining every section as a single monolithic backend truth.

#### Scenario: Page contract composes section owners
- **WHEN** the page loads or saves settings
- **THEN** the contract SHALL compose section data through section owners or an explicitly governed composition layer
- **AND** the composition layer SHALL NOT become a persistence truth for sections it does not own

#### Scenario: Notification remains user-scoped
- **WHEN** the page includes notification preferences
- **THEN** those preferences SHALL continue to use the user-scoped canonical contract
- **AND** the system SHALL NOT mirror them into a fake system-global settings store

### Requirement: Section Metadata Must Distinguish Evidence Types

The system SHALL expose metadata that separates measured values, inferred values, and historical baselines for each section.

#### Scenario: Runtime truth and baselines are not conflated
- **WHEN** the contract returns section data or status metadata
- **THEN** it SHALL identify whether the displayed state is `measured`, `inferred`, or `historical-baseline`
- **AND** the UI and reports SHALL NOT present those evidence types as interchangeable current truth

#### Scenario: Section availability is explicit
- **WHEN** a section is unavailable, degraded, or temporarily local-only during migration
- **THEN** the contract SHALL report that status at the section level
- **AND** it SHALL NOT hide the condition behind a page-wide unlabeled fallback

### Requirement: Migration Closeout Requires Section Exit Criteria

The system SHALL retire degraded `System-Config` behavior only after section-specific exit criteria are satisfied.

#### Scenario: Local-storage fallback is retired safely
- **WHEN** the team proposes removing local-storage fallback from `System-Config`
- **THEN** each section SHALL have a verified canonical backend read/write path or an explicitly approved non-writeable status
- **AND** compatibility paths SHALL have named retirement tasks and owners
- **AND** no section may be declared complete based only on page-level smoke behavior

#### Scenario: Deletion requires code-path and function-tree judgment
- **WHEN** a rollout removes fallback code, compatibility files, or temporary entrypoints
- **THEN** the change SHALL document both code-path judgment and function-tree judgment
- **AND** deletion SHALL be blocked if the section remains active, compatible, experimental, or otherwise not formally retired

