## ADDED Requirements

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

The system SHALL poll Linear for active issues, normalize issue data into a stable model, and
dispatch only candidate-eligible work within configured concurrency limits.

#### Scenario: Dispatch only active and unclaimed issues
- **WHEN** the orchestrator polls Linear for candidate work
- **THEN** it only dispatches issues whose states are active and non-terminal
- **AND** it excludes issues that are already running or claimed
- **AND** it respects both global and per-state concurrency limits

#### Scenario: Block Todo issues with live blockers
- **WHEN** an issue is in `Todo`
- **AND** any blocker is still non-terminal
- **THEN** the orchestrator skips dispatch for that issue

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
