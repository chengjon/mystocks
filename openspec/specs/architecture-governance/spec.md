# architecture-governance Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define the governance contract for architecture and technical-debt execution artifacts, including authoritative reference routing, conflict tracking, debt registration, execution boards, and weekly governance cadence.
## Requirements
### Requirement: Q2 Architecture Closure Program
The project SHALL treat the 2026 Q2 phase evaluation as a cross-cutting closure program rather than as an unstructured collection of optimization suggestions.

#### Scenario: Q2 closure scope is defined
- **WHEN** a Q2 architecture or quality closure wave is proposed
- **THEN** the scope SHALL identify the canonical truths it intends to settle
- **AND** it SHALL identify the closure evidence required before the wave is marked complete

### Requirement: Sequential Closure Gate For Cross-Cutting Waves
The project SHALL execute cross-cutting architecture closure waves through a sequential gate unless the canonical truths and write scopes are already stabilized.

#### Scenario: Cross-cutting wave is planned
- **WHEN** a change affects overlapping architecture truth sources, governance rules, or shared composition entrypoints
- **THEN** the default execution model SHALL be single-CLI sequential delivery
- **AND** parallel multi-CLI execution SHALL require an explicit low-coupling justification

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

### Requirement: Backend Composition Source Of Truth
The backend SHALL define one canonical source-of-truth for application composition and startup assembly.

#### Scenario: Composition path is canonicalized
- **WHEN** multiple backend assembly entrypoints exist or appear to overlap
- **THEN** one path SHALL be declared canonical for application composition
- **AND** non-canonical paths SHALL be classified as compatibility-retained, delegated, or retirement-targeted

### Requirement: Realtime Delivery Truth Registry
The system SHALL maintain a realtime delivery truth registry for active push-driven backend paths.

#### Scenario: Realtime path is added or changed
- **WHEN** a websocket, socket manager, streaming service, or equivalent realtime delivery path is introduced or materially changed
- **THEN** the registry SHALL record its owner, canonical transport role, fallback policy, and consumer scope
- **AND** it SHALL identify whether the path is canonical, compatibility-retained, or cleanup-ready
- **AND** the registry SHALL be consistent with the canonical realtime transport selection policy defined for API integration

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

### Requirement: Broker Execution Truth Registry
The system SHALL maintain a broker execution truth registry for broker-facing execution and
lifecycle-ingestion paths.

#### Scenario: Broker-facing execution path is introduced or changed
- **WHEN** a broker-facing adapter, submission bridge, acknowledgement ingestion path, or execution-report ingestion path is introduced or materially changed
- **THEN** the registry SHALL record the canonical path owner, adapter or bridge identity, and current classification state
- **AND** it SHALL record the local-to-external order identity binding surface, lifecycle source scope, and reconciliation owner
- **AND** it SHALL identify whether the path is canonical, compatibility-retained, or still experimental

#### Scenario: Broker truth registry is reviewed during trading safety closure
- **WHEN** a trading path is reviewed for stronger lifecycle claims or production-eligible promotion
- **THEN** the broker execution truth registry SHALL be reviewed alongside the trading execution safety contract
- **AND** the recorded path SHALL be consistent with the broker acknowledgement and reconciliation contract defined for trading safety

### Requirement: Data Source Runtime Extraction Governance

The architecture-governance capability SHALL treat data-source runtime extraction as a proposal-first, phased migration with explicit ownership, rollback, and closure gates.

#### Scenario: Extraction proposal is approved before implementation

- **WHEN** implementation work begins for data-source runtime extraction
- **THEN** the `extract-data-source-runtime-service` proposal SHALL have passed strict OpenSpec validation
- **AND** the user SHALL have approved implementation after reviewing affected specs, phase scope, first pilot, and rollback path

#### Scenario: Phase 2 has an explicit approval gate

- **WHEN** the team is ready to move from completed Phase 0/1 work into Phase 2
- **THEN** Phase 2 SHALL require explicit approval of the REST/WebSocket runtime scope, `RemoteDataSourceClient`, Docker readiness work, and rollback path
- **AND** Phase 2 approval SHALL explicitly exclude MCP tools, MCP transports, mounted MCP diagnostics, and MCP-over-SSE compatibility

#### Scenario: Extraction depends on optimize-data-source-v2 evidence

- **WHEN** the extraction proposal maps local runtime capabilities into the new `DataSourceClient` or `DataSourceRuntime`
- **THEN** it SHALL reference `optimize-data-source-v2` as dependency evidence rather than re-implementing SmartRouter, CircuitBreaker, cache, metrics, BatchProcessor, or runtime config semantics
- **AND** remaining grey/production validation items from `optimize-data-source-v2` SHALL be classified as blockers or parallel follow-up before remote extraction is treated as deliverable

#### Scenario: Compatibility layers have closure criteria

- **WHEN** local/remote clients, main-backend facades, old registry paths, old priority config, or old manager wrappers coexist during migration
- **THEN** each compatibility layer SHALL be documented as thin forwarding or transition code
- **AND** each compatibility layer SHALL have explicit exit criteria before old paths are retired
- **AND** deletion or retirement SHALL follow `architecture/STANDARDS.md` approval and evidence requirements

#### Scenario: Verification matrix is executable

- **WHEN** a migration phase is marked complete
- **THEN** its task entry SHALL include executable validation commands or named evidence artifacts
- **AND** conceptual review alone SHALL NOT be sufficient to close implementation tasks
