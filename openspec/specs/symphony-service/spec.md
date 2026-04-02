# symphony-service Specification

## Purpose
Define the local-first Symphony/Maestro orchestration runtime contract for repository-owned workflows,
tracker-backed issue dispatch, multi-CLI collaboration, and MyStocks-specific operating conventions.
## Requirements
### Requirement: Advisory Owner Suggestion

The system SHALL provide an advisory owner suggestion capability for the main CLI, using repository
ownership rules and task path hints to recommend likely owners without automatically assigning them.

#### Scenario: Suggest owner from file ownership matches
- **WHEN** an operator requests an owner suggestion for a task
- **THEN** the system evaluates `.FILE_OWNERSHIP` matches against the provided or derived task paths
- **AND** returns a ranked owner suggestion with reasons

#### Scenario: Keep assignment explicit
- **WHEN** the system produces an owner suggestion
- **THEN** the suggestion does not automatically modify assignment state
- **AND** the operator still decides whether to apply the recommendation

### Requirement: Repo-Owned Workflow Contract

The system SHALL load a repository-owned `WORKFLOW.md` file, parse YAML front matter and Markdown
prompt content, and re-apply valid workflow changes without restarting the service.

#### Scenario: Parse workflow with front matter
- **WHEN** `WORKFLOW.md` starts with YAML front matter delimited by `---`
- **THEN** the system parses the front matter into a config object
- **AND** trims the remaining Markdown body into the prompt template

#### Scenario: Preserve last known good workflow after invalid reload
- **WHEN** `WORKFLOW.md` changes to an invalid configuration at runtime
- **THEN** the system logs an operator-visible reload error
- **AND** continues operating with the last known good effective configuration
- **AND** does not crash active orchestration

### Requirement: Linear-Based Candidate Orchestration

The system SHALL support configurable tracker backends for candidate orchestration and MUST provide
both a Linear-backed tracker and a local SQLite-backed tracker.

#### Scenario: Dispatch from local SQLite tracker
- **WHEN** the workflow config sets `tracker.kind` to `local`
- **THEN** Symphony reads candidate issues from the configured SQLite tracker database
- **AND** it dispatches only issues whose states are active and non-terminal

#### Scenario: Preserve Linear compatibility
- **WHEN** the workflow config sets `tracker.kind` to `linear`
- **THEN** Symphony continues using the Linear-backed tracker client
- **AND** existing Linear orchestration behavior remains available

### Requirement: Isolated Workspace Lifecycle

The system SHALL map each issue identifier to a deterministic sanitized workspace path and enforce
workspace-root containment for all hook and agent execution.

#### Scenario: Reuse a deterministic per-issue workspace
- **WHEN** the service receives repeated runs for the same issue identifier
- **THEN** it resolves the same sanitized workspace path
- **AND** it reuses the existing directory when present
- **AND** runs `after_create` only when the directory is newly created

#### Scenario: Reject out-of-root workspace execution
- **WHEN** a resolved workspace path escapes the configured workspace root
- **THEN** the system rejects the run attempt
- **AND** does not execute hooks or launch the coding agent

### Requirement: Codex App-Server Session Execution

The system SHALL launch Codex app-server sessions in the issue workspace, render strict prompts,
process JSON-line protocol messages, and continue turns on the same thread until the run stops.

#### Scenario: Run a successful turn and emit session metadata
- **WHEN** a turn completes successfully
- **THEN** the system records the `thread_id`, `turn_id`, and combined `session_id`
- **AND** updates token and rate-limit telemetry from supported payloads
- **AND** keeps the thread alive for continuation turns within the same worker run

#### Scenario: Fail immediately on user input requirement
- **WHEN** the coding agent requests user input during a run
- **THEN** the run attempt fails immediately
- **AND** the orchestrator treats it as a retryable worker failure

### Requirement: Optional Linear GraphQL Client-Side Tool

The system SHALL support an optional `linear_graphql` client-side tool for trusted Linear-backed
workflows when the repo workflow explicitly enables it.

#### Scenario: Advertise enabled client-side tool at thread start
- **WHEN** the workflow enables the `linear_graphql` client-side tool
- **THEN** Symphony includes a `linear_graphql` dynamic tool spec in the Codex `thread/start`
  request
- **AND** the tool input schema accepts a GraphQL `query` and optional `variables`

#### Scenario: Execute enabled `linear_graphql` dynamic tool calls
- **WHEN** Codex issues a dynamic tool request for `linear_graphql`
- **THEN** Symphony executes the request against Linear using the configured tracker credentials
- **AND** returns JSON text content items describing the GraphQL result

#### Scenario: Reject unsupported dynamic tool calls with structured failure
- **WHEN** Codex issues a dynamic tool request for an unknown or disabled tool
- **THEN** Symphony returns a structured dynamic tool failure response
- **AND** emits an operator-visible runtime event for the rejected tool name

### Requirement: Retry, Reconciliation, and Restart Recovery

The system SHALL keep a single authoritative in-memory orchestration state for retries,
reconciliation, and recovery after process restarts.

#### Scenario: Queue continuation retry after clean worker exit
- **WHEN** a worker exits normally
- **THEN** the orchestrator removes the running entry
- **AND** schedules a short continuation retry for the same issue

#### Scenario: Stop ineligible active runs during reconciliation
- **WHEN** the tracker refresh shows a running issue moved to a terminal or non-active state
- **THEN** the orchestrator stops the active worker
- **AND** cleans the workspace only for terminal-state transitions

### Requirement: Optional Operator Status Surface

The system SHALL expose an optional operator-facing dashboard and JSON state API when a status port
is configured.

#### Scenario: Serve runtime state snapshot
- **WHEN** the HTTP status surface is enabled
- **THEN** `GET /api/v1/state` returns running sessions, retry queue entries, token totals, and
  rate-limit snapshot
- **AND** `POST /api/v1/refresh` queues an immediate reconciliation and poll cycle

#### Scenario: Return issue-specific runtime details
- **WHEN** an operator requests `GET /api/v1/<issue_identifier>`
- **THEN** the system returns issue-specific runtime details if the issue is tracked
- **AND** returns a JSON `404` error when the issue is unknown

### Requirement: Local SQLite Tracker Storage

The system SHALL support a local SQLite-backed issue tracker for personal and local-first Symphony
usage.

#### Scenario: Bootstrap local tracker database
- **WHEN** Symphony starts with `tracker.kind` set to `local`
- **THEN** it creates the SQLite database and required tables if they do not exist
- **AND** it can immediately query candidate issues from the local store

#### Scenario: Record issue state changes in event history
- **WHEN** an issue is created or its state is updated through the local tracker interface
- **THEN** the current issue state is persisted in the `issues` table
- **AND** an audit entry is appended to `issue_events`

### Requirement: Local Tracker Command-Line Management

The system SHALL provide a small local tracker CLI for managing issues without Linear.

#### Scenario: Create and update issues locally
- **WHEN** an operator uses the local tracker CLI
- **THEN** they can create issues, list issues, and update issue state
- **AND** those changes become visible to Symphony on the next poll cycle

### Requirement: Human-Authored Task Contract Boundary

The system SHALL treat file ownership rules as human-authored coordination artifacts, and for
Mongo-backed active work it SHALL treat `TASK.md` and `TASK-REPORT.md` as exported task snapshots
derived from the control plane rather than authoritative hand-authored task records.

#### Scenario: Execute after Mongo-backed task exists

- **WHEN** a MyStocks issue is activated for Mongo-backed multi-CLI execution
- **THEN** the active task definition is sourced from the Mongo control plane
- **AND** any `TASK.md` / `TASK-REPORT.md` artifact used in the worktree is an exported snapshot of that state
- **AND** the system does not require operators to hand-maintain markdown as the primary active task source

#### Scenario: Preserve readable exported artifacts

- **WHEN** an operator needs a readable worktree-local task artifact for review or worker onboarding
- **THEN** the system can export `TASK.md` and `TASK-REPORT.md` from Mongo-backed collaboration records
- **AND** the exported artifact remains consistent with the current control-plane state

### Requirement: Local-First Multi-CLI Runtime Visibility

The system SHALL provide runtime visibility suitable for MyStocks local-first multi-CLI execution,
including hook context for workspace automation and heartbeat-derived stale detection for active
worker sessions.

#### Scenario: Provide hook context for local automation
- **WHEN** Symphony creates or reuses a workspace
- **THEN** workspace hooks receive repository, workspace, and issue context through environment variables
- **AND** operators can use those values to build local-first automation around the workspace lifecycle

#### Scenario: Surface stale worker telemetry
- **WHEN** Symphony reports running worker sessions through the status snapshot
- **THEN** each running session includes heartbeat metadata derived from the latest known activity
- **AND** the snapshot identifies whether the session is currently stale

### Requirement: Stable Layered Extraction Boundary

The system SHALL provide a stable compatibility namespace for future extraction and SHALL define a
three-layer architecture that separates generic orchestration runtime concerns from multi-CLI
collaboration concerns and repository-specific profile concerns.

#### Scenario: Expose long-term runtime namespace
- **WHEN** a caller imports the long-term orchestration namespace
- **THEN** the repository exposes a `maestro` compatibility namespace
- **AND** existing `symphony` imports remain valid during the migration period

#### Scenario: Expose three architectural layers
- **WHEN** a caller inspects the runtime architecture metadata
- **THEN** the system exposes `kernel`, `collab`, and `profiles` as the three long-term layers
- **AND** the MyStocks repository profile defines the formal responsibility model for human, main CLI, worker CLI, and runtime

### Requirement: Persistent Collaboration Registry

The system SHALL provide a persistent local collaboration registry suitable for MyStocks multi-CLI
automation, and the registry SHALL track machine-state collaboration facts separately from
human-authored task contract files.

#### Scenario: Persist issue assignment state
- **WHEN** a local-first runtime dispatches or finishes work for an issue
- **THEN** the collaboration registry records the issue assignment state for that issue
- **AND** the recorded state remains available across process restarts

#### Scenario: Persist workspace mapping
- **WHEN** the runtime creates or reuses a workspace for an issue
- **THEN** the collaboration registry records the issue-to-workspace mapping

#### Scenario: Persist worker heartbeat metadata
- **WHEN** the runtime receives worker session activity events
- **THEN** the collaboration registry records the latest heartbeat metadata for that issue
- **AND** operators can identify stale worker state from the persisted heartbeat view

### Requirement: Owner-Aware Dispatch

The system SHALL respect collaboration assignment ownership during local-first multi-CLI dispatch.

#### Scenario: Dispatch only to the assigned CLI
- **WHEN** an issue has a persisted `assigned_worker_cli`
- **THEN** only a runtime whose `cli_name` matches that assignment may dispatch the issue

#### Scenario: Reclaim stale assigned work when enabled
- **WHEN** an issue assignment is stale
- **AND** a runtime is configured to reclaim stale assignments
- **THEN** that runtime may dispatch the issue and update the assignment to itself

### Requirement: Collaboration Operator Surfaces

The system SHALL provide local operator surfaces for managing and inspecting collaboration state.

#### Scenario: Manage assignment from CLI
- **WHEN** an operator uses the collaboration management CLI
- **THEN** the operator can create or update issue assignment state in the local collaboration registry

#### Scenario: Inspect collaboration runtime state from API
- **WHEN** an operator calls the collaboration status API
- **THEN** the API exposes per-issue collaboration state, workspace mappings, and stale worker visibility
