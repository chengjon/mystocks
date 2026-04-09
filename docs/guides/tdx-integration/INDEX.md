# TDX Integration Guide Family

> **导航说明**:
> 本文件是 `docs/guides/tdx-integration/` 的 transition index，不是当前仓库共享规则、当前 TDX 接入基线或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及当前接入实现边界，再结合根目录 `AGENTS.md` 与实际代码核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于 TDX 集成专题说明与历史接入材料，不承担仓库级 trunk。推荐阅读顺序：

1. [`README.md`](./README.md)
2. [`WINDOWS_TDX_BRIDGE_SETUP.md`](./WINDOWS_TDX_BRIDGE_SETUP.md)
3. 再按需进入整合分析、数据抓取、数据分析和完整示例

## Active Supporting Guides

- [`README.md`](./README.md)
  - TDX 集成主题总览与历史兼容入口
- [`WINDOWS_TDX_BRIDGE_SETUP.md`](./WINDOWS_TDX_BRIDGE_SETUP.md)
  - Windows TDX HTTP 桥接代理配置指南

## Retained Specialized References

- [`INTEGRATION_ANALYSIS.md`](./INTEGRATION_ANALYSIS.md)
  - 历史整合分析
- [`data_capture.md`](./data_capture.md)
  - 数据抓取功能说明
- [`data_analysis.md`](./data_analysis.md)
  - 数据分析功能说明
- [`data_visualization.md`](./data_visualization.md)
  - 数据呈现功能说明
- [`complete_example.md`](./complete_example.md)
  - 完整项目使用示例

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露总览和桥接接入入口，其余采集/分析/示例材料统一通过本 index 进入
- 若后续历史分析和示例材料入链继续下降，再按 bounded batch 单独评估 archive/delete
