## ADDED Requirements

### Requirement: OpenStock Data Source Runtime Container

The containerized runtime deployment capability SHALL support an optional `openstock` runtime service without forcing an immediate all-project Docker migration.

#### Scenario: Compose topology includes optional data-source runtime

- **WHEN** the data-source runtime extraction reaches remote mode
- **THEN** the approved deployment topology SHALL include an `openstock` service definition or equivalent runtime entrypoint
- **AND** that service SHALL expose readiness and liveness checks
- **AND** the main backend SHALL be able to select local or remote data-source client mode through configuration

#### Scenario: Data-source runtime smoke verifies readiness

- **WHEN** `scripts/run_data_source_runtime_smoke.sh` executes successfully
- **THEN** it SHALL verify data-source runtime readiness, main-backend facade compatibility, and local/remote rollback behavior
- **AND** it SHALL avoid creating a parallel deployment truth source outside the approved runtime delivery artifacts

#### Scenario: Data-source runtime failure does not take down main backend

- **WHEN** the remote `openstock` service is unavailable or unhealthy
- **THEN** the main backend SHALL remain available for non-data-source product APIs
- **AND** operators SHALL be able to switch back to local data-source client mode if the local runtime prerequisites remain available
