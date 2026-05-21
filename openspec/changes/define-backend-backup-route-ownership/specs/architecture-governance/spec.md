## ADDED Requirements

### Requirement: Backup Route Ownership Must Be Explicit Before Mutation

Backup and recovery route changes SHALL pass through a dedicated ownership,
safety, and evidence gate before any route module move, route path change,
schema exposure change, docs/API edit, consumer rewrite, or implementation issue
is authorized.

#### Scenario: Backup ownership proposal records current evidence

- **WHEN** a backup route ownership lane is proposed
- **THEN** the proposal SHALL record runtime route count, OpenAPI path count,
  backup candidate route count, backup schema-exposed route count, backup
  OpenAPI path and operation counts, duplicate operationId count, generated
  artifact paths, captured git head, and stale-if-head-mismatch policy.

#### Scenario: Backup route classes are classified

- **WHEN** backup route ownership is evaluated
- **THEN** the ownership packet SHALL classify backup execution, backup listing,
  recovery execution, scheduler control, integrity verification, cleanup, and
  health routes before implementation work begins.

#### Scenario: Cleanup and backup health ownership is explicit

- **WHEN** `cleanup_old_backups.py`, `cleanup_old_backups`, or
  `backup_service_health` is included in backup route ownership
- **THEN** the ownership packet SHALL record whether each item belongs to backup
  ownership, service-health/control-plane documentation, or another approved
  lane before any route movement or deletion is proposed.

#### Scenario: Backup safety matrix is required

- **WHEN** a backup or recovery route mutation is considered
- **THEN** the decision packet SHALL record auth dependency, admin permission,
  audit/logging behavior, destructive/stateful risk, consumer contracts,
  OpenAPI examples, minimum regression checks, and rollback or restore-safety
  expectations.

#### Scenario: Proposal-only backup ownership remains locked

- **WHEN** a backup route ownership change is in proposal or evidence-only state
- **THEN** it SHALL NOT authorize backend source edits, frontend source edits,
  tests, generated client changes, docs/API edits, route path changes, module
  moves, operationId changes, response contract changes, probe URL changes, PM2
  workflow execution, `include_in_schema` changes, or infrastructure backup
  implementation changes.
