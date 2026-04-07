# Maestro Owner-Aware Dispatch Design

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


## Context

The repository now has a local collaboration registry, but assignment is still informational rather
than operational. The next step is to feed assignment into dispatch and expose the resulting state
through CLI and API surfaces.

## Goals / Non-Goals

- Goals:
  - enforce assignment-aware dispatch
  - optionally reclaim stale assignments
  - provide small operator surfaces for assignment and status inspection
- Non-Goals:
  - parse owner from task files automatically
  - build a complete fleet scheduler

## Decisions

1. add `runtime.cli_name`
2. add `runtime.reclaim_stale_assignments`
3. let main CLI manage assignment through a dedicated CLI
4. expose collab issue/workspace/stale endpoints through the status API

## Risks / Trade-offs

- incorrect `cli_name` configuration can prevent dispatch
- stale reclaim is intentionally conservative and opt-in

## Migration Plan

1. land config and tests
2. wire dispatch gating
3. add CLI and API surfaces
