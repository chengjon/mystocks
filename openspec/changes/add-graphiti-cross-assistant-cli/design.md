## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


The current repository already has the ingredients for Graphiti-backed memory workflows:

- Graphiti MCP is configured at the project level.
- Repo-local code can call Graphiti through a shared adapter/service layer.
- Mongo remains the only control-plane truth source for work-item lifecycle.

What is missing is a stable cross-assistant contract. Today the effective entry path is shaped by assistant-specific hook behavior, fixed prompt phrases, and Mongo-backed task artifacts. That works for one harness, but it does not scale to Codex, OpenCode, or direct operator shell usage.

## Goals

- Define one canonical Graphiti CLI surface that every assistant can invoke.
- Preserve Mongo-backed scope enforcement for task-bound preflight.
- Add a direct Graphiti memory mode that does not require `TASK.md`, `Issue Identifier`, or Mongo work items.
- Make Graphiti writes auditable and machine-verifiable.
- Keep assistant-specific hooks thin and disposable.

## Non-Goals

- Do not replace Mongo with Graphiti for workflow truth.
- Do not require `@graphiti` or any other prompt token as the primary interface.
- Do not complete the wider `maestroctl.py` naming/cutover effort in this change.
- Do not redesign Graphiti storage topology or MCP deployment.

## Decisions

### 1. Canonical interface is a shared CLI, not a hook

The canonical Graphiti interface will be a repo-local CLI contract exposed from the current transitional control surface and later carried forward into the single `maestroctl.py` surface.

Assistant hooks may still exist, but their only job is to translate assistant-specific events into the shared CLI invocation.

Why:

- shell commands are assistant-agnostic
- CLI output is easier to audit and test than hook-only side effects
- this avoids depending on whether a given harness directly exposes Graphiti MCP tools

### 2. Graphiti must support two explicit modes

#### Scoped preflight

Used when the caller has a Mongo-backed work item and wants task-aware historical context.

Required inputs:

- `work_item_id`
- actor identity
- optional `task_path`

Behavior:

- reads work-item context from Mongo
- derives Graphiti queries from task metadata
- optionally records preflight memory
- returns Graphiti state without mutating workflow truth

#### Generic memory

Used when the caller wants Graphiti retrieval or recording without requiring Mongo work items.

Required inputs depend on operation:

- search mode: explicit `group_id`/`group_ids` + query
- remember mode: explicit `group_id`, title/name, and body/body-file

Behavior:

- bypasses Mongo work-item lookup
- does not promise workflow scope enforcement
- returns auditable Graphiti write/read results directly

Why:

These are two different use cases and should not be collapsed. Removing all Mongo/TASK requirements only makes sense for generic memory operations, not for scoped task preflight.

### 3. Prompt tokens are convenience sugar only

Prompt markers such as `@graphiti` may be supported by wrappers, but they are not the contract.

Why:

- prompt parsing varies across assistants
- prompt markers are brittle and hard to validate
- operators need a direct command path even when hooks are absent

### 4. Graphiti write operations must return durable audit metadata

Any explicit memory record flow must return and persist:

- `episode_uuid`
- `group_id`
- ingest status
- processed/queued timing details where available
- actor identity / invocation context

Why:

Without these fields, “memory was recorded” is not operationally verifiable.

## Architecture

### Shared layers

- transport: Graphiti MCP adapter
- orchestration: Graphiti service methods for scoped preflight and generic memory operations
- CLI: canonical operator/assistant command surface
- wrappers: Claude/Codex/OpenCode-specific hooks or helpers that call the CLI

### Invocation model

1. assistant or operator chooses `preflight` or `remember/search`
2. wrapper, if present, invokes the shared CLI
3. CLI calls the shared Graphiti service layer
4. service either:
   - uses Mongo work-item context for scoped preflight, or
   - uses direct Graphiti inputs for generic memory mode
5. service returns structured results and writes auditable events where applicable

## Risks / Trade-offs

- Supporting two modes adds command-surface complexity.
  - Mitigation: keep the mode split explicit and minimal.
- Keeping current transitional CLI names may feel inconsistent with the MaeStro target.
  - Mitigation: document this as an intentionally compatible interim surface.
- Generic memory mode can be misused as pseudo-workflow state.
  - Mitigation: spec language must explicitly forbid treating generic Graphiti records as workflow truth.

## Migration Plan

1. Add spec requirements for canonical CLI, dual modes, and auditable writes.
2. Expose Graphiti subcommands from the current transitional runtime CLI surface.
3. Update assistant wrappers to call the shared CLI rather than embedding command logic.
4. Add tests for:
   - scoped preflight
   - generic remember/search flows
   - wrapper-to-CLI delegation
   - audit metadata persistence
5. Fold the same command contract into `maestroctl.py` during the broader cutover change.

## Open Questions

- Should generic memory search and generic remember share one `graphiti` verb tree, or separate top-level subcommands?
- Should explicit Graphiti remember operations always emit Mongo audit events when Mongo is available, or only when called from scoped mode?
