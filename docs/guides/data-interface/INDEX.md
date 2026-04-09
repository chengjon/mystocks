# Data Interface Guide Family

> **导航说明**:
> 本文件是 `docs/guides/data-interface/` 的 transition index，不是仓库共享规则、当前数据接口实现边界或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体实现状态，再结合根目录 `AGENTS.md`、当前代码与相关脚本输出核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留数据接口抽象、扫描工具和 API 使用分析说明，不承担仓库级 trunk。推荐阅读顺序：

1. [`UNIFIED_INTERFACE_GUIDE.md`](./UNIFIED_INTERFACE_GUIDE.md)
2. [`DATA_INTERFACE_SCANNER_GUIDE.md`](./DATA_INTERFACE_SCANNER_GUIDE.md)
3. 再按需进入 API 与 Web 前端数据使用分析工具说明

## Active Supporting Guides

- [`UNIFIED_INTERFACE_GUIDE.md`](./UNIFIED_INTERFACE_GUIDE.md)
  - 统一数据访问抽象层与智能路由使用说明
- [`DATA_INTERFACE_SCANNER_GUIDE.md`](./DATA_INTERFACE_SCANNER_GUIDE.md)
  - 数据接口扫描脚本与注册表盘点入口

## Retained Specialized References

- [`analyze_api_data_usage_README.md`](./analyze_api_data_usage_README.md)
  - API 与 Web 前端数据使用分析工具说明

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露统一接口与扫描工具两个仍具直接使用价值的入口，API 使用分析说明统一通过本 index 进入
- 若后续 `analyze_api_data_usage_README.md` 的实际入链继续下降，可再按 bounded batch 单独评估 archive/delete
