# Maestro Owner Suggestion Design

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


## Context

Owner-aware dispatch already exists, but ownership choice still begins as a human decision. The next
step is to help the main CLI with a rule-based suggestion layer that remains advisory.

## Goals / Non-Goals

- Goals:
  - reduce repetitive ownership lookup work
  - stay deterministic and explainable
  - keep main CLI in control
- Non-Goals:
  - fully understand arbitrary natural-language tasks
  - auto-assign based on suggestion alone

## Decisions

1. use `.FILE_OWNERSHIP` as the primary source of truth
2. derive path hints from `TASK.md` and explicit CLI paths
3. default unknown paths to `main`
4. expose reasons in the output

## Risks / Trade-offs

- suggestions are only as good as path hints
- sparse `TASK.md` files may produce conservative results

## Migration Plan

1. add parser + suggester
2. expose CLI
3. optionally feed suggestion into future UI/API surfaces
