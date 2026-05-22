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

### Requirement: Runtime Unblock Must Precede Broad Architecture Evidence
The backend SHALL restore a successful `app.main` import and the associated targeted collection smoke before route/OpenAPI closure evidence, health/status closure claims, or broad architecture batch scheduling are treated as current truth.

#### Scenario: Runtime unblock is still failing
- **WHEN** `app.main` import fails because a response-helper module in the route import chain has a missing transitive import
- **THEN** the failure SHALL be recorded as the active blocker
- **AND** route/OpenAPI closure claims SHALL remain deferred
- **AND** no broad architecture batch SHALL be treated as open for execution based on stale runtime evidence

#### Scenario: Runtime unblock is restored
- **WHEN** `app.main` import succeeds after low-risk import-time route/helper repairs
- **THEN** the evidence SHALL record the route count and targeted health route collection or test result
- **AND** route/OpenAPI evidence refresh MAY proceed from the verified checkout
- **AND** remaining non-import-chain static debt SHALL remain separate from the runtime unblock claim

### Requirement: Schema Compatibility Must Be Proved Before Directory Retirement
The backend SHALL preserve schema compatibility until canonical exports, consumer migration, and targeted validation prove that the legacy `app/schema/` path can be retired without breaking current consumers.

#### Scenario: Legacy schema consumers still exist
- **WHEN** `from app.schema` consumers remain in the codebase
- **THEN** the change SHALL preserve a compatibility path
- **AND** the retirement decision SHALL remain deferred until the consumer migration evidence is recorded

### Requirement: Singleton Lifecycle Work Must Start From Classification
The backend SHALL classify service and singleton candidates by interface depth, statefulness, and test-double suitability before selecting a lifecycle implementation pilot.

#### Scenario: No low-risk pilot exists
- **WHEN** the inventory does not contain a clean low-risk singleton pilot
- **THEN** the plan SHALL switch to interface extraction and test-double strategy instead of forcing a misleading pilot selection

### Requirement: Codebase Map Evidence Shall Distinguish Historical And Current-Head Truth
The codebase map SHALL mark each recorded artifact as historical, commit-scoped, current-head, or stale-aware so that older counts cannot be mistaken for current truth.

#### Scenario: A count changes at a later HEAD
- **WHEN** a newer HEAD contradicts an older live-count snapshot
- **THEN** the newer HEAD SHALL be recorded explicitly
- **AND** the older snapshot SHALL remain labeled as historical evidence only

### Requirement: Backend Core Import Compatibility Governance

The project SHALL preserve import compatibility when splitting backend Core modules.

#### Scenario: Core module is moved

- **GIVEN** a Core module path is imported by backend code, tests, or scripts
- **WHEN** the module implementation is moved to a new package or file
- **THEN** the old import path SHALL remain available through an approved re-export or thin wrapper
- **AND** the wrapper SHALL have a documented retirement condition
- **AND** lifecycle-owned Core modules SHALL identify their coordination point with dependency lifecycle governance before movement

#### Scenario: Logger internals are reorganized

- **GIVEN** logging internals are moved under `app.core.logging`
- **WHEN** caller imports are reviewed
- **THEN** `app.core.logger` SHALL remain the canonical caller entrypoint
- **AND** callers SHALL NOT be required to import internal logging implementation modules
- **AND** import smoke SHALL cover `from app.core.logger import logger`

### Requirement: Backend Core Split Batch Governance

The project SHALL split Core modules in small independently verifiable batches.

#### Scenario: Core split batch is prepared

- **GIVEN** a batch moves Core files or changes Core imports
- **WHEN** the batch is prepared for implementation
- **THEN** it SHALL include import inventory, compatibility strategy, import smoke, runtime smoke, and rollback notes
- **AND** broad database, cache, security, socketio, or logger moves SHALL be blocked until lifecycle ownership and monkeypatch paths are classified

### Requirement: Backend Service DI Pilot Governance

The backend SHALL introduce service-tier dependency injection pilots only through
a named OpenSpec change or explicitly approved child implementation issue that
defines scope, test override strategy, rollback, and verification gates before
source edits begin.

#### Scenario: Pilot scope is approved before implementation

- **WHEN** a service singleton or direct-construction pilot is selected for
  implementation
- **THEN** the pilot SHALL identify the exact route, service, and test files
  allowed to change
- **AND** the parent decision issue SHALL NOT be treated as implementation
  authorization

#### Scenario: Route service dependency is overrideable in tests

- **WHEN** a route depends on a selected service DI pilot
- **THEN** the route SHALL obtain that service through a FastAPI dependency
  provider or an equivalent injectable seam
- **AND** focused route tests SHALL use dependency overrides or a documented
  service test-double mechanism instead of relying on module-level service
  construction as the only test seam

#### Scenario: Stateless pilot does not expand lifecycle ownership

- **WHEN** a selected pilot has no approved stateful initialization or teardown
  scope
- **THEN** the implementation SHALL NOT introduce `app.state`, lifespan
  ownership, singleton registries, or service-internal refactors
- **AND** closeout evidence SHALL record that route behavior, response contract,
  and rollback scope remained bounded to the approved pilot

### Requirement: Route OpenAPI Governance Must Precede Route Mutation

Backend route, OpenAPI, and probe-facing endpoint changes SHALL pass through a
current-head governance and ownership classification gate before any runtime
route mutation, schema exposure change, probe rewrite, or route-contract
implementation is authorized.

#### Scenario: Governance proposal is prepared from current evidence

- **WHEN** a route/OpenAPI governance lane is proposed after route table,
  OpenAPI, and probe consumer evidence has been collected
- **THEN** the proposal SHALL record the route table head, runtime route count,
  OpenAPI path count, operation count, duplicate operationId count, warning
  count, probe matrix scope, generated artifact paths, captured git head, and
  stale-if-head-mismatch policy.

#### Scenario: Trading route ownership is classified

- **WHEN** trading, TradingView, v1 trading, runtime trading, or
  trading-adjacent route candidates are included in route/OpenAPI governance
- **THEN** each route group SHALL be classified as trading-owned,
  trading-adjacent, non-trading, or unknown before any trading route
  implementation lane is opened.

#### Scenario: Runtime compatibility is separated from schema exposure

- **WHEN** a compatibility route, wildcard shim, legacy path, hidden runtime
  route, or duplicate runtime path/method is reviewed
- **THEN** the governance packet SHALL distinguish runtime route existence from
  OpenAPI schema exposure and SHALL classify the route as active documented,
  runtime-only hidden from schema, intentionally absent, or retired by a later
  approved change.

#### Scenario: Control-plane and backup lanes stay explicit

- **WHEN** route/OpenAPI governance identifies health, readiness, status,
  metrics, OpenAPI docs, probe-facing, backup, or recovery endpoints
- **THEN** the governance packet SHALL route those findings to D2.5
  control-plane docs/probe stabilization, D2.4 backup ownership, or an
  explicitly approved narrow inclusion before implementation work begins.

#### Scenario: Proposal-only route governance remains locked

- **WHEN** a route/OpenAPI governance change is in proposal or evidence-only
  state
- **THEN** it SHALL NOT authorize backend source edits, frontend source edits,
  tests, generated client changes, route path changes, router registration
  changes, operationId changes, response contract changes, probe URL changes, or
  `include_in_schema` changes.

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

### Requirement: Stateful PM2 Workflow Execution Requires Explicit Approval

Stateful PM2 validation SHALL require an explicit approval record before any
workflow can stop, delete, recreate, or restart services.

#### Scenario: PM2 workflow mode is classified

- **WHEN** `scripts/run_pm2_integration_workflow.sh` is referenced by a task
  list, proposal, runbook, or issue
- **THEN** the work item SHALL classify the intended mode as no execution,
  read-only sampling, named equivalent, full `gate`, full `regression`, or full
  `all` before any PM2 command is run.

#### Scenario: Stateful PM2 gate requires an approval record

- **WHEN** a future work item requests full `gate`, `regression`, or `all`
  execution
- **THEN** the approval record SHALL name the approving source, approval
  timestamp, approving human or owner, target branch, target commit, exact
  command mode, expected state mutation, service impact, rollback and restore
  commands, evidence destination, timeout, stop rule, and acceptance owner.

#### Scenario: Named equivalent is not full PM2 evidence

- **WHEN** a named equivalent is approved instead of a full PM2 workflow
- **THEN** the approval record SHALL name the exact command set, explain why it
  substitutes for the stateful workflow, and state which full PM2 workflow
  evidence remains unproven.

#### Scenario: Existing PM2 evidence is cited without rerun

- **WHEN** existing PM2 gate evidence is used for a later governance or archive
  decision
- **THEN** the decision packet SHALL record the evidence path, captured branch or
  commit if known, freshness limits, and why no new PM2 execution is required.

#### Scenario: Proposal-only PM2 approval work remains locked

- **WHEN** a PM2 approval-policy change is in proposal or evidence-only state
- **THEN** it SHALL NOT authorize PM2 command execution, `pm2 stop all`,
  `pm2 delete all`, service restart, process recreation, backend source edits,
  frontend source edits, tests, generated client changes, docs/API edits, route
  changes, OpenAPI schema changes, probe URL changes, or movement of a decision
  issue to implementation-ready state.
