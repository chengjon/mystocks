## MODIFIED Requirements

### Requirement: Human-Authored Task Contract Boundary

The system SHALL treat `TASK.md`, `TASK-REPORT.md`, and file ownership rules as human-authored
coordination artifacts, while Mongo-backed collaboration state remains the runtime source of truth
for worker lifecycle, progress, and review handoff.

#### Scenario: Execute after task contract exists
- **WHEN** a MyStocks issue is activated for Symphony execution
- **THEN** Symphony treats the existing `TASK.md` and `TASK-REPORT.md` as authoritative human-readable collaboration context
- **AND** it does not redefine the task contract on behalf of the human operator
- **AND** the runtime lifecycle state continues to be read from the collaboration control plane

#### Scenario: Respect repository ownership boundaries
- **WHEN** a worker session is launched for a MyStocks issue
- **THEN** the session prompt instructs the worker to respect `.FILE_OWNERSHIP`
- **AND** the worker stays within the assigned task boundary unless the main CLI explicitly coordinates otherwise

### Requirement: Collaboration Operator Surfaces

The system SHALL provide local operator surfaces for managing and inspecting collaboration state,
including an active-work board suitable for main CLI review.

#### Scenario: Manage assignment from CLI
- **WHEN** an operator uses the collaboration management CLI
- **THEN** the operator can create or update issue assignment state in the local collaboration registry

#### Scenario: Inspect collaboration runtime state from API
- **WHEN** an operator calls the collaboration status API
- **THEN** the API exposes per-issue collaboration state, workspace mappings, and stale worker visibility

#### Scenario: Inspect active work board from CLI
- **WHEN** the main CLI requests the collaboration board view
- **THEN** the system returns active work rows with lifecycle status, latest update, plan progress, pending request state, and delivery summary

## ADDED Requirements

### Requirement: Worker Claim Acknowledgement

The system SHALL let an assigned worker explicitly acknowledge receipt of a dispatched work item and
record the start of execution in the collaboration control plane.

#### Scenario: Claim dispatched work
- **WHEN** the assigned worker claims a dispatched work item
- **THEN** the system records the claiming worker identity and claim timestamp
- **AND** the active work status becomes `in_progress`
- **AND** the summary view exposes the claim metadata to the main CLI

#### Scenario: Reject claim from non-owner worker
- **WHEN** a different worker attempts to claim a work item it does not own
- **THEN** the system rejects the claim request
- **AND** the work item state remains unchanged

### Requirement: Structured Worker Plan Progress

The system SHALL let workers publish structured plan items under a work item and SHALL aggregate
their completion progress for the main CLI.

#### Scenario: Publish initial plan items
- **WHEN** the assigned worker decomposes a claimed work item into plan items
- **THEN** the system persists those plan items with stable ordering and per-item status
- **AND** the summary view reflects the total planned work count

#### Scenario: Advance plan progress
- **WHEN** the worker marks a plan item as `done`
- **THEN** the system updates the plan item evidence metadata
- **AND** the summary view updates `plan_done`, `progress_percent`, and current focus

#### Scenario: Surface missing decomposition
- **WHEN** a work item is `in_progress` and no plan items have been published
- **THEN** the summary view reports `plan_total = 0`
- **AND** the main CLI can identify that the worker has not yet decomposed the task

### Requirement: Worker Delivery Submission

The system SHALL provide an explicit worker delivery submission flow before review handoff.

#### Scenario: Submit completed work for review
- **WHEN** the assigned worker submits a completed work item with delivery metadata
- **THEN** the system records the submitted commit SHA, branch, and verification summary
- **AND** the active work status becomes `ready_for_review`
- **AND** the summary view exposes the delivery metadata to the main CLI

#### Scenario: Keep handoff explicit
- **WHEN** a worker has finished local edits but has not submitted the work item
- **THEN** the control plane does not treat the work as `ready_for_review`
- **AND** the main CLI can still see that the item remains in active execution
