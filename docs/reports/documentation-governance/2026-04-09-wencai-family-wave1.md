# Wencai Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/wencai/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/wencai/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/wencai/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把集成索引、历史规划和 quick reference 全部平铺暴露
- 这会让历史 `PLAN` 看起来与当前读者更可能需要的主题索引和快速参考处于同一优先级

## Changes

- 将 `docs/guides/wencai/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Wencai family 的根导航
- 根导航现在优先保留：
  - `guides/wencai/INDEX.md`
  - `guides/wencai/WENCAI_INTEGRATION_INDEX.md`
  - `guides/wencai/WENCAI_INTEGRATION_QUICKREF.md`
  - `Supporting Guides` -> `guides/wencai/INDEX.md`
- 将 `WENCAI_INTEGRATION_PLAN.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/wencai/WENCAI_INTEGRATION_INDEX.md`
  - `docs/guides/wencai/WENCAI_INTEGRATION_QUICKREF.md`
- family transition index:
  - `docs/guides/wencai/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 Wencai family 历史规划 leaf doc 的直接暴露
- retention duty:
  - `WENCAI_INTEGRATION_PLAN.md` 继续保留为 supporting/historical reference

## Expected Effect

- 根导航不再把 Wencai family 的历史规划误读为主入口
- 读者先进入主题索引和 quick reference，再按需查看完整规划
- 后续若历史规划入链继续下降，可继续单独评估 archive/delete
