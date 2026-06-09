# Classification Refinement Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 在主干收口完成后的第一轮 taxonomy refinement。
> 目标不是继续大规模 rewrite，而是把 `overview/operations/testing` 的根级文档补齐 machine-readable lifecycle classification，减少治理审计中的无效 `unclassified` 噪音。

## Scope

- `docs/overview/`
- `docs/operations/`
- `docs/testing/`

## Changes

### Overview

- taxonomy 现在覆盖 `docs/overview/*.md`
- 除 canonical trunk 和 transition indexes 外，其余 overview 根级文档归入 `supporting`

### Operations

- taxonomy 现在覆盖 `docs/operations/*.md`
- `docs/operations/运维效果分析报告.md` 单独归类为 `report`
- 其余 root runbooks 归入 `supporting`

### Testing

- taxonomy 现在覆盖 `docs/testing/*.md`
- 历史计划类文档归入 `plan`
- retrospective / analysis / debt / value docs 归入 `report`
- 其余 active guides、compatibility guides、quick references 归入 `supporting`

## Intent

- 不新增 parallel truth
- 不对现有正文做额外扩写
- 先把 lifecycle 语义表达清楚，再决定后续是否需要 bounded cleanup

## Expected Outcome

这一轮之后，`docs/overview/`、`docs/operations/`、`docs/testing/` 的根级文档应不再大面积出现在 `unclassified` findings 中。
