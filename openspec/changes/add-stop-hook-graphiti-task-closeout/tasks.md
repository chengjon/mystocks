## 1. Hook Contract

- [x] 1.1 Define the completion trigger phrases, negative phrases, and dedupe rule for Stop-hook closeout reporting
- [x] 1.2 Define the standardized Graphiti closeout payload shape and required audit metadata
- [x] 1.3 Document non-blocking failure behavior and operator expectations

## 2. Hook Implementation

- [x] 2.1 Add a dedicated Stop hook script for completion-triggered Graphiti closeout writes
- [x] 2.2 Register the hook in `.claude/settings.json` without replacing existing Stop quality gates
- [x] 2.3 Reuse the shared Graphiti CLI contract instead of direct MCP-only calls
- [x] 2.4 Persist local dedupe / audit state so one final assistant message writes at most one closeout episode

## 3. Verification

- [x] 3.1 Add tests for trigger match, negative match, and no-trigger cases
- [x] 3.2 Add tests for Graphiti payload formatting and durable metadata expectations
- [x] 3.3 Add tests for duplicate Stop events not producing duplicate Graphiti writes
- [x] 3.4 Document the closeout-reporting hook in the hooks guide

## 4. Rollout

- [x] 4.1 Validate `add-stop-hook-graphiti-task-closeout` with OpenSpec strict validation
- [x] 4.2 Record approval before implementation begins
