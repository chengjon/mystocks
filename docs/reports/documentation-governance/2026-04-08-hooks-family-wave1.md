# Hooks Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/hooks/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/hooks/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/hooks/` 当前角色是 `supporting`，不是仓库级治理或文档系统 trunk
- `docs/INDEX.md` 仍把整个 hooks family 的 leaf docs 平铺到根导航
- 同时根索引残留了已删除 `docs/web-dev/` 的旧入口语义，容易把 hooks family 误读成独立 trunk

## Changes

- 将 `docs/guides/hooks/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Hooks family 的根导航
- 根导航现在优先保留：
  - `guides/hooks/INDEX.md`
  - `guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
  - `guides/hooks/web-dev-hooks-guide.md`
  - `guides/hooks/pre_commit_hook_setup_guide.md`
  - `Supporting Guides` -> `guides/hooks/INDEX.md`
- 将根索引中的残留 `Web Dev` 入口改为 `Web Dev Hooks`，并显式路由到 `guides/hooks/`

## Gate Check

- canonical replacement:
  - `docs/overview/documentation-system.md`
- family transition index:
  - `docs/guides/hooks/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 hooks leaf docs 的直接暴露
  - 残留 `web-dev` 根入口已改为 hooks family 别名入口
- retention duty:
  - 诊断、分析、入门与历史说明文档继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把 hooks family 的诊断/历史叶子文档误读为主入口
- 已删除 `docs/web-dev/` 后的读者入口被稳定收束到 `docs/guides/hooks/`
- 后续若某些诊断或历史文件的 inbound links 继续下降，可再逐份评估 archive/delete
