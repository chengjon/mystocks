# Symphony Service Design

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


## Context

The upstream Symphony specification describes a language-agnostic orchestrator that continuously
polls an issue tracker, maps each issue to a stable workspace, and runs a coding-agent session in
that workspace according to a repo-owned `WORKFLOW.md` contract.

MyStocks already has:

- Python runtime dependencies needed for the core implementation (`pyyaml`, `httpx`, `jinja2`,
  `fastapi`)
- existing structured logging helpers in `src/core/logging/structured.py`
- a scripts-based runtime entrypoint pattern under `scripts/runtime/`

MyStocks does not yet have a dedicated automation service that owns dispatch state, retries,
workspace safety, and Codex app-server integration.

## Goals

- Implement the core Symphony conformance profile in Python
- Keep the implementation isolated from the main FastAPI product backend
- Preserve repo-owned workflow policy in root `WORKFLOW.md`
- Reuse existing Python dependencies where practical
- Support safe restart recovery without a database
- Expose operator-readable logs and an optional HTTP status surface

## Non-Goals

- Building a multi-tenant orchestration platform
- Persisting retry queues across process restarts
- Implementing business-specific tracker mutations in the orchestrator
- Building a rich production dashboard before core orchestration behavior is stable

## Architecture

The implementation is split into the same abstraction layers used by the upstream specification:

1. **Workflow + Config Layer**
   - `workflow_loader.py` parses `WORKFLOW.md` front matter and prompt body
   - `config.py` resolves defaults, `$VAR` indirection, normalized states, path expansion, and
     dynamic reload state

2. **Integration Layer**
   - `linear_client.py` fetches candidate issues, terminal-state issues, and issue-state refreshes
   - normalization produces a stable `Issue` model used by all higher layers

3. **Execution Layer**
   - `workspace_manager.py` creates/reuses sanitized per-issue workspaces and runs hooks
   - `codex_app_server.py` owns the JSON-line protocol over stdio
   - `dynamic_tools.py` defines optional client-side tool specs/handlers exposed at thread start
   - `agent_runner.py` coordinates workspace prep, prompt rendering, multiple turns, and cleanup

4. **Coordination Layer**
   - `orchestrator.py` owns the authoritative in-memory runtime state, polling, reconciliation,
     retries, and slot-based dispatch

5. **Observability Layer**
   - `status_api.py` exposes optional dashboard and JSON endpoints
   - structured logs capture issue/session context and operator-visible failures

## Module Layout

New package:

- `src/services/symphony/__init__.py`
- `src/services/symphony/errors.py`
- `src/services/symphony/models.py`
- `src/services/symphony/workflow_loader.py`
- `src/services/symphony/config.py`
- `src/services/symphony/linear_client.py`
- `src/services/symphony/workspace_manager.py`
- `src/services/symphony/template_renderer.py`
- `src/services/symphony/codex_app_server.py`
- `src/services/symphony/agent_runner.py`
- `src/services/symphony/orchestrator.py`
- `src/services/symphony/status_api.py`
- `src/services/symphony/service.py`

Runtime entrypoint:

- `scripts/runtime/run_symphony.py`

Repo workflow contract:

- `WORKFLOW.md`

Tests:

- `tests/unit/services/symphony/`

## Key Decisions

### 1. Use Jinja2 strict rendering

The spec requires strict template rendering with unknown variables and filters treated as errors.
Jinja2 with `StrictUndefined` already exists in repo dependencies and supports the required
`{{ issue.identifier }}` syntax used by upstream examples.

### 2. Use polling-based workflow reload instead of filesystem watchers

The spec requires `WORKFLOW.md` changes to be detected and re-applied without restart. The repo
does not currently declare `watchdog`, so the service will poll the workflow file mtime on a short
interval and also revalidate defensively before dispatch. This satisfies the hot-reload
requirement without introducing a new watcher dependency.

### 3. Keep Symphony outside `web/backend`

The upstream spec defines a dedicated scheduler/runner lifecycle, not a product API feature.
Placing the code under `src/services/symphony/` and launching it via `scripts/runtime/` avoids
coupling retry state and Codex subprocess management to the customer-facing backend.

### 4. Implement the optional HTTP status surface

FastAPI and Uvicorn already exist in the repository. A minimal optional status API improves
operator visibility and makes the implementation closer to the upstream reference without adding a
second web framework.

### 5. Auto-approve approvals, fail on user input requests

The implementation targets trusted environments by default:

- command/file approvals are auto-approved for the session
- unsupported dynamic tool calls return structured failure responses
- user-input requests immediately fail the run attempt

This posture is documented in `WORKFLOW.md` and service docs, while still keeping approval and
sandbox settings configurable through workflow front matter.

### 6. Gate `linear_graphql` behind workflow config and advertise via `config.dynamic_tools`

The upstream Symphony spec treats `linear_graphql` as an optional client-side tool. MyStocks should
only expose it when the repo workflow explicitly enables it, so trusted repos can opt in without
silently expanding the agent's tracker access surface.

When enabled:

- Symphony advertises a `linear_graphql` `DynamicToolSpec` in the `thread/start` request under
  `config.dynamic_tools`
- incoming dynamic tool requests for `linear_graphql` are executed against the existing
  `LinearIssueTrackerClient`
- results are returned as text content items containing JSON payloads so the coding agent can parse
  them without adding a second transport format

When disabled or unknown, Symphony returns a structured tool failure response instead of silently
dropping the request.

## Safety Model

- Sanitize workspace keys to `[A-Za-z0-9._-]`
- Enforce workspace-root containment before any hook or Codex launch
- Launch Codex only with `cwd == workspace_path`
- Avoid logging tokens or expanded secret values
- Truncate hook output in logs
- Preserve last known good configuration on invalid workflow reloads

## Testing Strategy

Follow TDD in vertical slices:

1. workflow parsing and config resolution
2. workspace creation, hooks, and path safety
3. Linear normalization and pagination behavior
4. Codex app-server protocol handling using a fake stdio server fixture
5. orchestrator dispatch/retry/reconciliation logic
6. optional FastAPI status endpoints

Focused unit tests will live under `tests/unit/services/symphony/` and avoid real Linear/Codex
network dependencies unless explicitly enabled later.
