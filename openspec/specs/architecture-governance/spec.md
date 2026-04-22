# architecture-governance Specification

## Purpose
Define the governance contract for architecture and technical-debt execution artifacts, including authoritative reference routing, conflict tracking, debt registration, execution boards, and weekly governance cadence.
## Requirements
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

### Requirement: Runtime Audit Governance
The system SHALL record data-source, database, cache, and runtime-dependency audits as governance artifacts that classify each audited item by runtime status, compatibility duty, and required verification evidence.

#### Scenario: Runtime audit is published
- **WHEN** a data or database runtime audit is completed
- **THEN** the audit output SHALL identify each reviewed item as active, compatibility-retained, redundant, or pending classification
- **AND** it SHALL record the canonical evidence source and the minimum verification used for the judgment

### Requirement: Frontend Data Capability Registry
The system SHALL maintain a frontend data capability registry that records the owner, source-of-truth, refresh behavior, and consumer scope for active frontend data chains.

#### Scenario: Capability registry entry is added
- **WHEN** a frontend data flow is introduced or materially changed
- **THEN** the registry SHALL record the capability name, owner, source-of-truth, and backing endpoint or channel
- **AND** it SHALL record cache/realtime behavior and known consumer scope

#### Scenario: Pilot migration is classified
- **WHEN** a frontend data capability is selected for staged migration
- **THEN** the registry SHALL identify it as pilot, active, compatibility-retained, or cleanup-ready
- **AND** it SHALL record the expected verification evidence for closure

### Requirement: Frontend Realtime Channel Registry
The system SHALL maintain a realtime channel registry for frontend push-driven channels and their policy metadata.

#### Scenario: Realtime channel is registered
- **WHEN** a WebSocket or SSE channel is adopted or modified
- **THEN** the registry SHALL record the owner, push-only status, coalescing behavior, and refresh semantics
- **AND** it SHALL identify whether force refresh or fallback polling is allowed

### Requirement: Phased Frontend Data Migration Governance
The system SHALL execute frontend data architecture migrations through independently shippable phases with coexistence, rollback, and cleanup criteria.

#### Scenario: Migration phase is planned
- **WHEN** a frontend data architecture change is proposed
- **THEN** the phase plan SHALL identify what coexists, what remains canonical, and what evidence closes the phase
- **AND** it SHALL NOT require immediate full-repo conversion as a prerequisite for starting

#### Scenario: Cleanup stage is entered
- **WHEN** migration moves to cleanup-stage enforcement
- **THEN** closure evidence SHALL show that replacement paths are active and verified
- **AND** any new hard discipline gate SHALL be introduced only after coexistence exit criteria are met

