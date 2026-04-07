# Symphony Service Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**Date:** 2026-03-08
**Scope:** Python implementation of the upstream Symphony service specification

## Context

The upstream Symphony spec defines a long-running orchestrator that polls Linear, creates isolated
workspaces, and runs Codex app-server sessions from a repo-owned `WORKFLOW.md`. MyStocks already
has the needed Python runtime libraries, but it does not have a single automation service that owns
dispatch state, retries, reconciliation, and session observability.

## Decision

Implement Symphony as a dedicated Python service under `src/services/symphony/`, launched from
`scripts/runtime/run_symphony.py`, with root `WORKFLOW.md` as the repo-owned workflow contract.

Key design choices:

1. Use strict Jinja2 rendering for workflow prompts because the upstream examples already use
   `{{ issue.identifier }}` syntax and Jinja2 is already available in the repo.
2. Use mtime polling for workflow reloads instead of `watchdog`, because the repo does not declare
   a file-watch dependency and the spec allows defensive revalidation during runtime operations.
3. Keep the service separate from `web/backend` because Symphony is a scheduler/runner lifecycle,
   not an end-user product API.
4. Implement the optional HTTP status surface with FastAPI because the dependencies are already
   present and the feature materially improves operator visibility.
5. Default to trusted-environment behavior: auto-approve approvals, fail on user-input-required
   turns, and keep sandbox/approval knobs configurable in `WORKFLOW.md`.

## Module Map

- `src/services/symphony/models.py`: typed runtime entities
- `src/services/symphony/workflow_loader.py`: `WORKFLOW.md` parsing
- `src/services/symphony/config.py`: defaults, env resolution, normalization, reload state
- `src/services/symphony/linear_client.py`: Linear GraphQL reads and issue normalization
- `src/services/symphony/workspace_manager.py`: path safety, hooks, cleanup
- `src/services/symphony/template_renderer.py`: strict prompt rendering and continuation prompts
- `src/services/symphony/codex_app_server.py`: stdio JSON-line protocol client
- `src/services/symphony/agent_runner.py`: workspace + Codex turn loop
- `src/services/symphony/orchestrator.py`: poll loop, claims, retries, reconciliation, metrics
- `src/services/symphony/status_api.py`: optional dashboard + JSON API
- `src/services/symphony/service.py`: top-level lifecycle wiring
- `scripts/runtime/run_symphony.py`: CLI entrypoint
- `WORKFLOW.md`: repo-owned workflow policy

## Non-Goals

- Persisting retry queues across restarts
- Implementing tracker business mutations in orchestrator code
- Building a rich UI beyond the minimum dashboard/status API
- Adding nonessential dependencies before the core conformance path is stable

## Safety Strategy

- Sanitize workspace names to the spec character set
- Enforce workspace root containment before any hook or agent launch
- Never execute Codex outside the per-issue workspace
- Keep invalid workflow reloads non-fatal by retaining the last known good config
- Avoid logging secret values or raw tokens

## Validation

- Unit tests for workflow parsing, config resolution, workspace safety, Linear normalization,
  Codex protocol handling, orchestrator retry logic, and status API snapshots
- `openspec validate add-symphony-service --strict`
- Targeted `pytest` runs for each Symphony slice before broader verification
