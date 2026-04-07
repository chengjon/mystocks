## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。

The project has multiple technical debt reports but lacks a consistent governance loop. This design introduces a minimal, repeatable artifact set.

## Goals / Non-Goals
- Goals:
  - Single source of truth for architecture references.
  - Visible, owned backlog of debt items.
  - Weekly execution cadence with measurable evidence.
- Non-Goals:
  - Refactoring implementation code.
  - Changing runtime architecture in this change.

## Decisions
- Use OpenSpec deltas for governance requirements.
- Maintain debt artifacts under `technical_debt/governance/`.
- Track execution via root-level `TASK*.md` files.

## Risks / Trade-offs
- Risk: Governance artifacts become stale.
  - Mitigation: Weekly rollup and explicit owners/DDL fields.

## Migration Plan
1. Create baseline documents and indexes.
2. Assign owners and DDLs.
3. Start weekly reporting cadence.

## Open Questions
- Which team owns final approval of SoT updates?
