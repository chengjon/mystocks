# TDX Integration Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/tdx-integration/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则、当前 TDX 接入基线或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/tdx-integration/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/tdx-integration/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把总览、桥接指南、历史整合分析、数据抓取、数据分析和完整示例全部平铺暴露
- 这会让历史整合分析和示例材料看起来与当前接入入口同优先级

## Changes

- 将 `docs/guides/tdx-integration/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 TDX Integration family 的根导航
- 根导航现在优先保留：
  - `guides/tdx-integration/README.md`
  - `guides/tdx-integration/WINDOWS_TDX_BRIDGE_SETUP.md`
  - `Supporting Guides` -> `guides/tdx-integration/INDEX.md`
- 将整合分析、数据抓取、数据分析、数据呈现和完整示例收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - `docs/guides/tdx-integration/README.md`
  - `docs/guides/tdx-integration/WINDOWS_TDX_BRIDGE_SETUP.md`
- family transition index:
  - `docs/guides/tdx-integration/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 TDX family 历史说明类 leaf docs 的直接暴露
- retention duty:
  - 历史整合分析和示例材料继续保留为 supporting/reference docs

## Expected Effect

- 根导航不再把 TDX family 的历史分析和示例材料误读为主入口
- 读者先进入总览和 Windows 桥接指南，再按需查看其余专题材料
- 后续若历史分析和示例材料入链继续下降，可继续逐份评估 archive/delete
