# Templates Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/templates/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则、当前模板口径或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/templates/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/templates/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把初始化模板、任务卡模板和技术债例外模板全部平铺暴露
- 这会让专项治理模板看起来与最常用初始化模板处于同一优先级

## Changes

- 将 `docs/guides/templates/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Templates family 的根导航
- 根导航现在优先保留：
  - `guides/templates/INDEX.md`
  - `guides/templates/INITIALIZATION_PROMPT.md`
  - `Supporting Guides` -> `guides/templates/INDEX.md`
- 将 `task-card-standard-template.md` 与 `tech-debt-exception-template.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/templates/INITIALIZATION_PROMPT.md`
- family transition index:
  - `docs/guides/templates/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 templates family 专项模板的直接暴露
- retention duty:
  - 任务卡模板和技术债例外模板继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把所有模板视为同级主入口
- 读者先进入初始化模板，再按需查看任务卡与技术债例外模板
- 后续若模板入链继续下降，可继续单独评估 archive/delete
