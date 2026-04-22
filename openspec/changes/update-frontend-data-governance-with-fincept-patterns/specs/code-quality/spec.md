## ADDED Requirements

### Requirement: Frontend Data Access Discipline Gates
The project SHALL define phased discipline checks for frontend data-access regressions during and after migration.

#### Scenario: Coexistence period is active
- **WHEN** frontend data migration is still in coexistence phase
- **THEN** discipline checks MAY run in non-blocking or report-only mode
- **AND** they SHALL identify direct forbidden patterns without preventing approved coexistence work

#### Scenario: Cleanup-stage enforcement begins
- **WHEN** migration closure criteria are met for the targeted frontend data paths
- **THEN** discipline checks SHALL block newly introduced forbidden patterns
- **AND** the checks SHALL at minimum cover silent catch suppression, unregistered direct data-access regressions, or equivalent approved rules

### Requirement: Frontend Migration Closeout Evidence
The project SHALL require closeout evidence before removing legacy frontend data-access paths or promoting discipline checks to blocking status.

#### Scenario: Legacy path is retired
- **WHEN** a legacy frontend data-access path is proposed for retirement
- **THEN** closeout evidence SHALL identify the verified replacement path and its verification artifacts
- **AND** it SHALL distinguish active canonical paths from compatibility-retained or cleanup-ready paths
