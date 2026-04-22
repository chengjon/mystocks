## Context

The repository already has:

- repo-local Claude hook registration in `.claude/settings.json`,
- Stop hooks that receive `transcript_path`, `session_id`, and `cwd`,
- a working completion detector in `.claude/hooks/record_three_layers.py`,
- a shared Graphiti CLI contract under `scripts/runtime/coordctl.py` / `scripts/runtime/start_work_with_graphiti.sh`,
- an `agent-memory-workflow` spec that explicitly prefers shared CLI contracts and auditable Graphiti writes.

The missing piece is not Graphiti access. The missing piece is a standardized completion-triggered closeout projection into Graphiti.

## Goals / Non-Goals

### Goals

- Detect task-closeout intent from the final assistant response at Stop time.
- Emit a normalized Graphiti memory entry only for clear completion-style endings.
- Include durable metadata so later audits can verify the write.
- Reuse the existing shared Graphiti CLI contract.
- Keep the hook non-blocking by default.

### Non-Goals

- Do not treat Graphiti as workflow state truth.
- Do not block Stop when Graphiti is unavailable.
- Do not write a Graphiti episode for every response.
- Do not add direct MCP-specific logic to the hook when shared CLI already exists.

## Decisions

### 1. Attach to Existing Stop Hook Chain

**Decision**: add a dedicated Stop hook command after quality gates, rather than modifying UserPromptSubmit or PostToolUse events.

**Rationale**:

- completion is best inferred from the final assistant message, which Stop already sees;
- the hook should run once per response rather than once per file edit;
- this aligns with the existing `record_three_layers.py` pattern.

### 2. Completion Trigger Must Be Phrase-Based But Guarded

**Decision**: the hook will only trigger when the last assistant message matches approved completion phrases and does not match negative phrases.

Trigger examples:

- `收尾已完成`
- `任务完成`
- `已完成`
- `完成了`
- `已修复`
- `task completed`
- `done`
- `finished`

Negative examples:

- `未完成`
- `尚未完成`
- `not completed`
- `待继续`

**Rationale**:

- the user explicitly wants phrase-based completion listening;
- guardrails are required to avoid writing false closeout episodes.

### 3. Use Standardized Closeout Payload

**Decision**: define a closeout payload with stable fields:

- `event_type`
- `session_id`
- `actor_cli`
- `project_root`
- `summary`
- `completion_phrase`
- `changed_files`
- `verification`
- `request_context`
- `audit`

**Rationale**:

- later review needs consistent records;
- freeform summaries alone are weak for search and audit.

### 4. Use Shared Graphiti CLI Contract

**Decision**: the hook will call the repo-local Graphiti CLI contract instead of calling Graphiti MCP directly.

**Rationale**:

- this is already required by `agent-memory-workflow`;
- it keeps the hook transport-neutral and reusable.

### 5. Non-Blocking Failure Semantics

**Decision**: Graphiti write failure only produces hook context / stderr warning and local audit evidence; it does not block Stop.

**Rationale**:

- task completion should not be blocked by memory infrastructure;
- Graphiti is memory, not control-plane truth.

## Risks / Trade-offs

### False Positives

- **Risk**: a generic completion sentence could write an unwanted closeout episode.
- **Mitigation**: phrase allowlist + negative-pattern check + dedupe on `session_id:last_message_id`.

### False Negatives

- **Risk**: a finished task without a completion keyword will not be reported.
- **Mitigation**: keep trigger phrases configurable and document preferred closing language.

### Repeated Writes

- **Risk**: Stop hook may run repeatedly for the same final assistant message.
- **Mitigation**: persist dedupe state keyed by session/message id.

### Noisy Payloads

- **Risk**: sending raw long responses to Graphiti reduces search quality.
- **Mitigation**: derive a bounded summary and structured verification fields instead of shipping entire transcripts.

## Migration Plan

### Phase 1: Hook Contract

- define trigger phrases, payload schema, and config location;
- document operator behavior and failure semantics.

### Phase 2: Implementation

- add a new Stop hook script and register it in `.claude/settings.json`;
- reuse transcript parsing and shared Graphiti CLI;
- store local dedupe/audit state.

### Phase 3: Verification

- add unit tests for trigger detection, no-trigger cases, dedupe, and Graphiti payload structure;
- document example output and operator usage.

## Open Questions

- should the trigger phrase list be repo-global config or embedded in the hook first?
- should the Graphiti `group_id` be the project root group only, or support task/worktree-specific groups when task metadata exists?
