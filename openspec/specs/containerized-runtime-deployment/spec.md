# containerized-runtime-deployment Specification

## Purpose
Define the repository contract for containerized runtime deployment, including Docker compose topology, canonical versus backup smoke port roles, deployment environment coverage, runtime smoke evidence, and integration with runtime delivery governance outputs.
## Requirements
### Requirement: Containerized Deployment Contract
The system SHALL provide a containerized runtime deployment contract based on the repository Docker compose topology.

#### Scenario: Compose topology defines required runtime services
- **WHEN** the repository validates the containerized deployment capability
- **THEN** the compose contract SHALL define backend, frontend, postgresql, and redis services
- **AND** backend SHALL depend on postgresql and redis
- **AND** frontend SHALL depend on backend

#### Scenario: Canonical and backup smoke ports stay separated
- **WHEN** containerized deployment capability is validated
- **THEN** canonical PM2 runtime ports SHALL remain `8020` for backend and `3020` for frontend
- **AND** backup container smoke ports SHALL remain `8021` for backend and `3021` for frontend
- **AND** the capability SHALL reject configurations that collapse canonical and backup smoke port roles

### Requirement: Containerized Runtime Smoke Evidence
The system SHALL produce reproducible containerized runtime smoke evidence for deployment verification.

#### Scenario: Smoke run captures runtime readiness and observability
- **WHEN** `scripts/run_containerized_runtime_smoke.sh` executes successfully
- **THEN** it SHALL capture backend health, backend readiness, frontend index, metrics health, and Prometheus delta artifacts
- **AND** it SHALL write a machine-readable `docker-runtime-smoke.json`
- **AND** it SHALL write a human-readable `SUMMARY.md`

#### Scenario: Smoke run preserves backup-smoke role metadata
- **WHEN** the smoke report is generated
- **THEN** the machine-readable report SHALL tag service URLs with the `backup_smoke` role
- **AND** downstream delivery gates SHALL be able to distinguish backup smoke URLs from canonical PM2 runtime URLs

### Requirement: Deployment Environment Contract
The system SHALL validate deployment environment coverage before treating containerized deployment as deliverable.

#### Scenario: Required env keys are documented
- **WHEN** deployment env contract validation runs
- **THEN** `.env.example` SHALL document backend, frontend, database, auth, and port-role keys required by deployment
- **AND** backend and frontend PM2 ecosystem `requireEnv(...)` keys SHALL be covered by `.env.example`

#### Scenario: Frontend deployment origin contract is explicit
- **WHEN** deployment env contract validation runs
- **THEN** `CORS_ORIGINS` documentation SHALL include canonical frontend `3020` and backup smoke frontend `3021`
- **AND** contract validation SHALL fail if either origin is missing from the documented deployment baseline

### Requirement: Runtime Delivery Gate Includes Containerized Deployment Capability
The system SHALL integrate the containerized deployment capability into the runtime delivery gate and governance outputs.

#### Scenario: Full runtime delivery gate consumes deployment contract artifacts
- **WHEN** `scripts/run_full_runtime_delivery_gate.sh` executes
- **THEN** it SHALL include container deployment contract, deployment env contract, and docker runtime smoke artifacts in its summary and manifest outputs
- **AND** it SHALL surface containerized deployment evidence without creating a parallel deployment truth source

#### Scenario: Governance reporting references the approved deployment entrypoints
- **WHEN** governance docs or weekly report templates describe containerized deployment verification
- **THEN** they SHALL reference the approved runtime delivery and container smoke entrypoints
- **AND** they SHALL not require users to infer deployment capability from unrelated low-level scripts alone
