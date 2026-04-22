## ADDED Requirements

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
