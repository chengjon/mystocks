# Buger Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/buger/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/buger/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/buger/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把服务接入、客户端连接和客户端集成细节全部平铺暴露
- 这会让客户端集成细节文档看起来与总览和连接排障入口处于同一优先级

## Changes

- 将 `docs/guides/buger/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Buger family 的根导航
- 根导航现在优先保留：
  - `guides/buger/INDEX.md`
  - `guides/buger/B项目接入指南.md`
  - `guides/buger/客户端连接指南.md`
  - `Supporting Guides` -> `guides/buger/INDEX.md`
- 将 `客户端集成指南.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/buger/B项目接入指南.md`
  - `docs/guides/buger/客户端连接指南.md`
- family transition index:
  - `docs/guides/buger/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 Buger family 集成细节 leaf doc 的直接暴露
- retention duty:
  - `客户端集成指南.md` 继续保留为 supporting/reference doc

## Expected Effect

- 根导航不再把 Buger family 的客户端集成细节误读为主入口
- 读者先进入接入总览与连接指南，再按需查看客户端集成实现细节
- 后续若客户端集成细节文档入链继续下降，可继续单独评估 archive/delete
