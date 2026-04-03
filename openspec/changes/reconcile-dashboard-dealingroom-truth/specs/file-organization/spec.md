## ADDED Requirements

### Requirement: Active Route Deprecation Safety
The system SHALL NOT move a frontend page into `deprecated/` while that page remains referenced by canonical router truth, generated page-config truth, or governed page inventory truth.

#### Scenario: Prevent deprecating a live route shell
- **WHEN** a page is still bound by router truth or generated page-config truth as a live route
- **THEN** deprecation work SHALL be blocked until a replacement or alias decision is approved
- **AND** the migration task SHALL record the blocker instead of moving the file

#### Scenario: Prevent deprecating a governed mainline page
- **GIVEN** a page is still tracked as a verified mainline page in governed inventory documentation
- **WHEN** a restructure task proposes moving that page to `deprecated/`
- **THEN** the task SHALL remain blocked until page-inventory truth is reconciled with router truth
