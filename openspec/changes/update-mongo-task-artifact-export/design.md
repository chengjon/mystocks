## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


The repository already has:

- Mongo-backed work items, updates, requests, events, and status views
- `coordctl` / `maestro_collab` command surfaces for create, claim, plan, update, request, submit-like flows
- migration and snapshot utilities

But active worker instructions still rely on manually maintained `TASK.md` content. That creates a split between:

- Mongo as machine-state truth
- markdown as human-managed task truth

The next step is to collapse active task definition into Mongo and keep markdown only as an export layer.

## Goals

- Make Mongo the only active task-definition source for current multi-CLI work.
- Preserve `TASK.md` / `TASK-REPORT.md` as readable artifacts by generating them from Mongo.
- Keep the first implementation small and CLI-first.

## Non-Goals

- Do not remove markdown artifacts entirely.
- Do not redesign the full Maestro runtime.
- Do not add a web UI.
- Do not migrate all historical legacy CLI docs in this change.

## Decisions

### 1. Export, do not hand-maintain

For Mongo-backed active tasks:

- `TASK.md` becomes an exported snapshot of work-item definition
- `TASK-REPORT.md` becomes an exported snapshot of updates / requests / current status

### 2. Start with explicit export commands

The first implementation adds explicit export commands instead of introducing automatic background generation. This keeps behavior inspectable and testable.

### 3. Preserve compatibility with current worktree expectations

Workers may still be told to read `TASK.md`, but that file should be generated from Mongo rather than hand-authored for active Mongo-backed tasks.

### 4. Limit initial rendering scope

The exported task contract only needs the fields already present in Mongo records:

- work item identity
- title / objective
- branch / owner
- path boundaries
- acceptance checks
- latest status
- updates / requests summary

No new large schema should be introduced in this first pass.
