# Superpowers Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/superpowers/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/superpowers/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/superpowers/` 当前角色是 `supporting`，不是仓库级 trunk
- 当前 family 仅保留 `INDEX.md` 与两份历史 implementation plan
- `docs/INDEX.md` 仍直接暴露 `plans/` 子目录和两份 plan 文件，容易让历史计划被误读为当前主入口

## Changes

- 将 `docs/guides/superpowers/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Superpowers family 的根导航
- 根导航现在只保留：
  - `guides/superpowers/INDEX.md`
  - `Supporting Guides` -> `guides/superpowers/INDEX.md`
- 将两份历史 plan 统一收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/superpowers/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已移除对 `plans/` 和具体 plan 文件的直接暴露
- retention duty:
  - `plans/2026-03-23-frontend-test-gates.md`
  - `plans/2026-03-25-guides-onboarding-migration.md`
  - 以上文档继续保留为 historical implementation plans

## Expected Effect

- 根导航不再把 superpowers 的历史计划误读为活跃 workflow 入口
- 读者统一先进入 family index，再按需查看两份历史 implementation plan
- 后续若这两份计划已无现实入链义务，可继续单独评估 archive/delete
