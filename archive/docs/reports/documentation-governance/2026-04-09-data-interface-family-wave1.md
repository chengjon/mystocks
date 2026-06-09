# Data Interface Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/data-interface/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/data-interface/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/data-interface/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把统一接口指南、扫描工具指南和 API 使用分析说明全部平铺暴露
- 这会让专门的分析脚本说明看起来与当前更常用的统一接口和扫描工具入口处于同一优先级

## Changes

- 将 `docs/guides/data-interface/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Data Interface family 的根导航
- 根导航现在优先保留：
  - `guides/data-interface/INDEX.md`
  - `guides/data-interface/UNIFIED_INTERFACE_GUIDE.md`
  - `guides/data-interface/DATA_INTERFACE_SCANNER_GUIDE.md`
  - `Supporting Guides` -> `guides/data-interface/INDEX.md`
- 将 `analyze_api_data_usage_README.md` 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/data-interface/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 `analyze_api_data_usage_README.md` 的直接暴露
- retention duty:
  - `analyze_api_data_usage_README.md`
  - 该文档继续保留为 specialized tool reference，并被脚本提示直接引用

## Expected Effect

- 根导航不再把 API 使用分析说明误读为 Data Interface family 的主入口
- 读者先进入统一接口与扫描工具指南，再按需查看 API/Web 使用分析工具说明
- 后续若该分析说明的实际入链继续下降，可继续单独评估 archive/delete
