## ADDED Requirements

### Requirement: Architecture Source of Truth
The system SHALL define and maintain an architecture source-of-truth document that enumerates authoritative references per domain.

#### Scenario: SoT is published
- **WHEN** a governance review completes
- **THEN** the SoT document is updated with current authoritative references

### Requirement: Spec Conflict Matrix
The system SHALL maintain a conflict matrix that tracks conflicting or overlapping specifications with status and owner fields.

#### Scenario: Conflict recorded
- **WHEN** a conflicting requirement is identified
- **THEN** a conflict entry is created with an owner and resolution status

### Requirement: Debt Register
The system SHALL maintain a debt register that records owner, due date, and next action for each debt item.

#### Scenario: Debt item added
- **WHEN** a new debt item is discovered
- **THEN** it is recorded in the register with owner and DDL

### Requirement: Execution Board
The system SHALL provide an execution board that tracks governance tasks with status and acceptance criteria.

#### Scenario: Task tracked
- **WHEN** governance work begins
- **THEN** the task appears on the execution board with status and acceptance criteria

### Requirement: Governance Cadence
The system SHALL run a weekly governance cadence with a rollup report summarizing progress and blockers.

#### Scenario: Weekly rollup published
- **WHEN** the governance week ends
- **THEN** a rollup report is produced with progress metrics and blockers
