# Governance Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/governance/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/governance/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/governance/` 当前角色是 `supporting`，不是仓库治理真相源
- family index 已经完成 transition 化，但 `docs/INDEX.md` 仍把全部 leaf docs 平铺暴露
- 这会弱化 `architecture/STANDARDS.md` 与 `docs/overview/documentation-system.md` 的 trunk-first 路由

## Changes

- 保留 `docs/guides/governance/INDEX.md` 作为 family transition index
- 收薄 `docs/INDEX.md` 中 Governance family 的根导航
- 根导航现在保留：
  - `guides/governance/INDEX.md`
  - `guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md`
  - `Supporting Guides` -> `guides/governance/INDEX.md`

## Gate Check

- canonical replacement:
  - `architecture/STANDARDS.md`
  - `docs/overview/documentation-system.md`
- family transition index:
  - `docs/guides/governance/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 leaf docs 的直接暴露
- retention duty:
  - `FEATURE_MANAGEMENT_WORKFLOW.md` 与 `TECHNICAL_DEBT_MANAGEMENT.md` 仍保留为 supporting guides

## Expected Effect

- 根导航不再把 governance family 误读成仓库级真相层
- 读者先回 trunk，再进入专题执行指南
- 后续如 `TECHNICAL_DEBT_MANAGEMENT.md` 的直接入链继续下降，可再单独评估是否进一步收口
