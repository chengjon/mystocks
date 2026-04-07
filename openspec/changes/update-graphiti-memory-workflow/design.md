## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


MyStocks currently uses:

- MongoDB via `maestro.collab` / `coordctl` as the task and status control plane
- GitNexus as code intelligence
- Exa as web/code/company search

Graphiti is already deployed outside this repository. The missing piece is a repository-local contract that defines Graphiti as the memory layer rather than another task database.

## Goals

- Make Graphiti MCP the active memory MCP entry for the project.
- Remove lingering Apifox MCP configuration from project-level MCP files.
- Define a stable boundary between Graphiti memory and Mongo coordination state.
- Keep the change small and configuration/documentation only.

## Non-Goals

- Do not add Graphiti API calls to application runtime code.
- Do not move task status, approval state, or work item lifecycle into Graphiti.
- Do not redesign the existing Mongo multi-CLI control plane.

## Decisions

### 1. Mongo remains the only coordination source of truth

Mongo continues to own:

- work creation
- assignment
- claim / plan / submit events
- state transitions
- review / merge lifecycle

Graphiti must not store or derive authoritative `work_item.status`.

### 2. Graphiti MCP becomes the memory layer for agents

Graphiti MCP is used for:

- handoff summaries
- recovered context for resumed work
- factual recall across main/worker sessions
- architecture and decision memory

This matches the deployed service model and avoids coupling project runtime to Graphiti API prematurely.

### 3. Graphiti API stays as a documented future extension

The project acknowledges the deployed `graphiti-api`, but this change intentionally does not integrate it into repository runtime code. That work would require a separate approved proposal because it changes automation and system behavior.

### 4. `group_id` is partitioned by workflow role

The guide will standardize initial names such as:

- `mystocks_spec_main`
- `mystocks_spec_workers`
- `mystocks_spec_docs`
- `mystocks_spec_review`

This keeps memory domains readable and avoids mixing orchestration, docs, and review artifacts into a single global memory bucket.
