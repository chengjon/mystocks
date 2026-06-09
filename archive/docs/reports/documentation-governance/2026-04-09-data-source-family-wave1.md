# Data Source Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/data-source/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/data-source/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/data-source/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把接入、管理、速查、清洗、监控、扩展和优化材料全部平铺暴露
- 这会让专题化 runbook 与高频入口看起来处于同一优先级，增加根导航噪音

## Changes

- 将 `docs/guides/data-source/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Data Source family 的根导航
- 根导航现在优先保留：
  - `guides/data-source/INDEX.md`
  - `guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md`
  - `guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`
  - `guides/data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md`
  - `Supporting Guides` -> `guides/data-source/INDEX.md`
- 将数据清洗、监控、端点注册、扩展与优化材料收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/data-source/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对清洗、监控、优化和扩展 leaf docs 的直接暴露
- retention duty:
  - `DATA_CLEANING_QUICK_START.md`
  - `DATA_SOURCE_ENDPOINT_REGISTRATION_GUIDE.md`
  - `DATA_SOURCE_EXPANSION_STRATEGY.md`
  - `DATA_SOURCE_MONITORING_GUIDE.md`
  - `DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md`
  - `DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`
  - 以上文档继续保留为 specialized/reference docs

## Expected Effect

- 根导航优先展示新增数据源接入、数据源管理和速查入口
- 清洗、监控、优化与扩展材料不再与高频入口平级暴露，但仍可通过 family index 进入
- 后续若这些专题材料的实际入链继续下降，可继续逐份评估 archive/delete
