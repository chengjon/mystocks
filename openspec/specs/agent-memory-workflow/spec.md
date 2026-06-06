# agent-memory-workflow Specification

## Purpose
Define the project-level memory workflow contract so Graphiti MCP serves as the canonical agent memory layer while Mongo remains the sole coordination source of truth for task lifecycle and execution control.
## Requirements
### Requirement: Graphiti MCP Must Be the Project Memory MCP

The project SHALL expose Graphiti MCP as the active project-level memory MCP entry in its maintained MCP configuration files.

#### Scenario: Active MCP config uses Graphiti memory

- **WHEN** an agent reads the repository MCP configuration
- **THEN** it finds a Graphiti MCP server entry
- **AND** that entry points to the project-approved Graphiti MCP endpoint
- **AND** the project-level Apifox MCP entry is no longer advertised as an active memory tool

### Requirement: Mongo Must Remain the Coordination Source of Truth

The project SHALL preserve MongoDB control-plane state as the only authoritative coordination source for main/worker task lifecycle.

#### Scenario: Agent chooses between Mongo and Graphiti

- **WHEN** an agent needs task status, assignment state, approval state, or work item lifecycle
- **THEN** it uses Mongo-backed coordination tools
- **AND** it does not treat Graphiti memory as authoritative workflow state

### Requirement: Graphiti Usage Boundaries Must Be Documented

The project SHALL document when Graphiti MCP is used, when Mongo is used, how `group_id` values are partitioned for agent workflows, and which Graphiti operations require Mongo-backed work-item context versus direct Graphiti inputs.

#### Scenario: Operator chooses between scoped preflight and generic memory

- **WHEN** an operator or assistant needs Graphiti functionality
- **THEN** the documentation distinguishes Mongo-backed scoped preflight from generic Graphiti memory operations
- **AND** the documentation states which inputs are required for each mode
- **AND** the documentation preserves Mongo as the control-plane truth source

### Requirement: Graphiti Must Expose a Shared Cross-Assistant CLI Contract

The project SHALL expose Graphiti operations through a shared repo-local CLI contract that can be invoked by assistants and operators without depending on assistant-specific MCP tool namespaces.

#### Scenario: Assistant invokes shared Graphiti CLI

- **WHEN** Claude, Codex, OpenCode, or a human operator needs Graphiti functionality
- **THEN** they can invoke the same repo-local Graphiti CLI contract
- **AND** assistant-specific hooks or wrappers only translate local events into that shared CLI
- **AND** the shared CLI remains usable even when no assistant hook is present

### Requirement: Graphiti Must Support Scoped And Generic Modes

The project SHALL support both Mongo-backed scoped Graphiti preflight and direct generic Graphiti memory operations.

#### Scenario: Scoped preflight uses Mongo work-item context

- **WHEN** the caller runs Graphiti preflight for a work item
- **THEN** the system reads work-item context from Mongo-backed collaboration records
- **AND** it derives Graphiti queries from task/work metadata
- **AND** it does not treat Graphiti as workflow truth

#### Scenario: Generic memory bypasses Mongo work-item lookup

- **WHEN** the caller runs a direct Graphiti remember or search operation without a work item
- **THEN** the system accepts explicit Graphiti inputs such as `group_id`, title, body, or query
- **AND** it does not require `TASK.md`, `Issue Identifier`, or a Mongo work item
- **AND** the operation is treated as memory retrieval or recording rather than workflow-state mutation

### Requirement: Explicit Graphiti Writes Must Be Auditable

The project SHALL return and persist auditable metadata for explicit Graphiti write operations.

#### Scenario: Explicit memory recording returns durable metadata

- **WHEN** the caller records an explicit Graphiti memory entry
- **THEN** the result contains `episode_uuid`
- **AND** the result contains `group_id`
- **AND** the result contains ingest status
- **AND** the result contains available queue or processing timing metadata
- **AND** any persisted audit projection includes enough metadata to verify that the write occurred

### Requirement: Stop Hook Task Closeout Reporting
The project SHALL support a Stop-hook-driven Graphiti closeout report for clearly completed tasks.

#### Scenario: Final assistant message indicates completion
- **WHEN** the Stop hook inspects the final assistant message for a session
- **AND** that message matches an approved completion phrase such as `收尾已完成`, `任务完成`, `已完成`, `done`, or `finished`
- **AND** the message does not match a configured negative phrase such as `未完成`, `尚未完成`, or `not completed`
- **THEN** the hook SHALL build a standardized closeout summary
- **AND** it SHALL submit the closeout through the shared Graphiti CLI contract

#### Scenario: Final assistant message does not indicate completion
- **WHEN** the Stop hook inspects the final assistant message for a session
- **AND** the message does not match an approved completion phrase
- **THEN** the hook SHALL NOT submit a Graphiti closeout report

### Requirement: Stop Hook Graphiti Closeout Payload Must Be Auditable
The project SHALL record auditable metadata for Stop-hook-driven Graphiti closeout writes.

#### Scenario: Closeout report is written
- **WHEN** the Stop hook writes a Graphiti closeout report
- **THEN** the payload SHALL include a bounded summary of the completed work
- **AND** it SHALL include changed file evidence or an explicit empty marker
- **AND** it SHALL include available verification evidence
- **AND** the result SHALL retain durable metadata including `episode_uuid` and `group_id`

#### Scenario: Duplicate Stop events occur for same final assistant message
- **WHEN** the Stop hook is invoked more than once for the same `session_id` and final assistant message identifier
- **THEN** the project SHALL deduplicate the Graphiti closeout write
- **AND** it SHALL ensure at most one closeout episode is recorded for that final message

### Requirement: Stop Hook Graphiti Reporting Must Remain Non-Blocking
The project SHALL keep completion-triggered Graphiti reporting non-blocking with respect to Stop completion.

#### Scenario: Graphiti write fails during closeout reporting
- **WHEN** the Stop hook detects completion but the Graphiti write cannot be completed
- **THEN** the hook SHALL emit warning or audit context
- **AND** it SHALL NOT block Stop solely because the Graphiti write failed
- **AND** it SHALL preserve enough local evidence to troubleshoot the failed write later

