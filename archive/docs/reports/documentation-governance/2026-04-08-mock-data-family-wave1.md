# Mock Data Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/mock-data/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/mock-data/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/mock-data/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把当前指南、历史路线图、历史计划和旧快照全部平铺到根导航
- 这会让历史参考材料看起来和当前切换指南处于同一优先级

## Changes

- 将 `docs/guides/mock-data/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Mock Data family 的根导航
- 根导航现在优先保留：
  - `guides/mock-data/INDEX.md`
  - `guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md`
  - `guides/mock-data/MOCK_DATA_USAGE_RULES.md`
  - `guides/mock-data/MOCK_REAL_DATA_INDEX.md`
  - `Supporting Guides` -> `guides/mock-data/INDEX.md`
- 将历史路线图、历史计划与旧版 `README_MOCK_DATA.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md`
  - `docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md`
- family transition index:
  - `docs/guides/mock-data/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对历史 mock-data leaf docs 的直接暴露
- retention duty:
  - 历史路线图、历史计划和旧快照说明继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把历史 mock-data 文档误读为当前主入口
- 读者会先进入切换指南、使用规则和专题导航，再决定是否查看历史参考
- 后续若历史文档入链进一步下降，可继续逐份评估 archive/delete
