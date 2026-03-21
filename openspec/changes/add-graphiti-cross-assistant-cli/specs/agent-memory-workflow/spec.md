## MODIFIED Requirements
### Requirement: Graphiti Usage Boundaries Must Be Documented

The project SHALL document when Graphiti MCP is used, when Mongo is used, how `group_id` values are partitioned for agent workflows, and which Graphiti operations require Mongo-backed work-item context versus direct Graphiti inputs.

#### Scenario: Operator chooses between scoped preflight and generic memory

- **WHEN** an operator or assistant needs Graphiti functionality
- **THEN** the documentation distinguishes Mongo-backed scoped preflight from generic Graphiti memory operations
- **AND** the documentation states which inputs are required for each mode
- **AND** the documentation preserves Mongo as the control-plane truth source

## ADDED Requirements
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
