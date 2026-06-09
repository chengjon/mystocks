# OpenSpec Cmd Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/openspec-cmd/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前 OpenSpec 官方工作流、文档系统 trunk、治理口径或审批门禁，请优先以 `openspec/AGENTS.md`、`architecture/STANDARDS.md`、`docs/README.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/openspec-cmd/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/openspec-cmd/` 当前角色是 `supporting`，不是 OpenSpec 官方工作流或仓库级 trunk
- `docs/INDEX.md` 仍把命令模板和报告示例与主指南并列暴露
- 这会让模板/示例看起来与当前主指南同优先级

## Changes

- 将 `docs/guides/openspec-cmd/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Openspec Cmd family 的根导航
- 根导航现在优先保留：
  - `guides/openspec-cmd/README.md`
  - `guides/openspec-cmd/check.md`
  - `Supporting Guides` -> `guides/openspec-cmd/INDEX.md`
- 将 `check-report-example.md` 与 `command-template.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `openspec/AGENTS.md`
  - `docs/guides/openspec-cmd/README.md`
- family transition index:
  - `docs/guides/openspec-cmd/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对模板与示例文档的直接暴露
- retention duty:
  - 模板与示例仍保留为 supporting/reference docs

## Expected Effect

- 根导航不再把模板和示例误读为当前 OpenSpec 主入口
- 读者先进入 OpenSpec 主指南和 `check` 命令说明，再按需查看模板和示例
- 后续若模板或示例入链继续下降，可继续单独评估 archive/delete
