# Maestro Three-Layer Architecture Design

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


## Context

`Symphony` already acts as more than a tracker poller. In MyStocks it now represents:

- local-first orchestration
- multi-CLI automation after task activation
- workspace and runtime visibility

To extract this capability cleanly, the repo needs a stable family name and a layered boundary.

## Goals / Non-Goals

- Goals:
  - establish `Maestro` as the long-term runtime family name
  - create a three-layer extraction boundary
  - preserve current `symphony` imports during transition
- Non-Goals:
  - fully move implementation files out of `symphony` in this change
  - implement all future collaboration-core features now

## Decisions

1. Keep `symphony` as the current implementation package
2. Add `maestro` as a compatibility namespace immediately
3. Define the long-term layers as:
   - `maestro.kernel`
   - `maestro.collab`
   - `maestro.profiles`

## Risks / Trade-offs

- The first step is mostly namespace and architecture work, not a full refactor
- Some functionality still physically lives under `symphony`
- But this keeps churn low while making future extraction explicit

## Migration Plan

1. seed `maestro` namespace now
2. preserve old imports
3. migrate implementation files by layer in later changes
