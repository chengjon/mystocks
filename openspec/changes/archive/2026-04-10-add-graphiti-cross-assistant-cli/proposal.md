# Change: Add Cross-Assistant Graphiti CLI Modes

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why

MyStocks already treats Graphiti as the long-term memory layer and Mongo as the collaboration truth source, but actual Graphiti usage is still too assistant-specific and too brittle. Today the usable path is effectively tied to Claude-only hooks, a fixed start-work prompt, and Mongo-backed work items, which means other assistants or non-hooked workflows cannot reliably consume the same memory workflow.

The repository needs one shared, explicit Graphiti operator surface that every assistant can call in the same way, while still preserving the distinction between Mongo-backed task coordination and Graphiti-backed memory retrieval or recording.

## What Changes

- Add a shared repo-local Graphiti CLI contract that is assistant-agnostic and shell-invocable.
- Define two supported Graphiti operation modes:
  - `scoped preflight` for Mongo-backed work items with task-bound context.
  - `generic memory` for direct Graphiti read/write flows that do not require Mongo work-item state.
- Make shared CLI commands the canonical Graphiti interface; assistant-specific hooks and prompt conventions become optional wrappers.
- Require auditable Graphiti write results to include stable metadata such as `episode_uuid`, `group_id`, ingest status, and timing details.
- Keep Mongo as the only authoritative workflow-truth source for task lifecycle, ownership, approval, and scope enforcement.

## Impact

- Affected specs:
  - `agent-memory-workflow`
- Affected code:
  - `scripts/runtime/coordctl.py`
  - `scripts/runtime/maestro_collab.py`
  - future `scripts/runtime/maestroctl.py` adoption path
  - `src/services/maestro/collab/**`
  - assistant wrapper hooks/scripts under `.claude/` and equivalent future harness integrations

## Alignment Constraints

- This change does not move workflow truth into Graphiti.
- This change does not require prompt markers such as `@graphiti` to be the primary activation mechanism.
- This change does not force all Graphiti usage through Mongo-backed work items.
- This change does not complete the broader `maestroctl.py` cutover; the shared Graphiti contract must remain compatible with the current transitional CLI surface.
