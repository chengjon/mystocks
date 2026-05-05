# Data Source Guide Family

> **导航说明**:
> 本文件是 `docs/guides/data-source/` 的 transition index，不是仓库共享规则、当前数据源实现边界或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体实现状态，再结合根目录 `AGENTS.md`、当前代码与相关脚本核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留数据源接入、管理、速查、监控与优化说明，不承担仓库级 trunk。推荐阅读顺序：

1. [`NEW_API_SOURCE_INTEGRATION_GUIDE.md`](./NEW_API_SOURCE_INTEGRATION_GUIDE.md)
2. [`DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`](./DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md)
3. [`DATA_SOURCE_TOOLS_QUICK_REFERENCE.md`](./DATA_SOURCE_TOOLS_QUICK_REFERENCE.md)
4. 再按需进入数据清洗、监控、端点注册、扩展策略和优化专题

## Active Supporting Guides

- [`NEW_API_SOURCE_INTEGRATION_GUIDE.md`](./NEW_API_SOURCE_INTEGRATION_GUIDE.md)
  - 新增数据源/API 接口开发与验证入口
- [`DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`](./DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md)
  - 数据源管理工具完整使用说明
- [`DATA_SOURCE_TOOLS_QUICK_REFERENCE.md`](./DATA_SOURCE_TOOLS_QUICK_REFERENCE.md)
  - 数据源管理与调用速查卡片
- [`DATA_SOURCE_OPERATIONS_MANUAL.md`](./DATA_SOURCE_OPERATIONS_MANUAL.md)
  - `optimize-data-source-v2` 当前已落地能力的运维入口
- [`DATA_SOURCE_DEVELOPER_GUIDE.md`](./DATA_SOURCE_DEVELOPER_GUIDE.md)
  - `DataSourceManagerV2` 主链路、扩展点与验证矩阵
- [`../akshare/INDEX.md`](../akshare/INDEX.md)
  - `expand-akshare-data-sources` 当前 AkShare 专题 guide family 入口

## Retained Specialized References

- [`ADAPTIVE_RATE_LIMITER_GUIDE.md`](./ADAPTIVE_RATE_LIMITER_GUIDE.md)
  - 独立 `AdaptiveRateLimiter` 组件与当前接入边界说明
- [`DATA_LINEAGE_TRACKER_GUIDE.md`](./DATA_LINEAGE_TRACKER_GUIDE.md)
  - governance-side `DataLineageTracker` 与可选 Neo4j 存储说明
- [`DATA_CLEANING_QUICK_START.md`](./DATA_CLEANING_QUICK_START.md)
  - 数据清洗与验证快速开始
- [`DATA_SOURCE_ENDPOINT_REGISTRATION_GUIDE.md`](./DATA_SOURCE_ENDPOINT_REGISTRATION_GUIDE.md)
  - 数据源端点注册方案
- [`DATA_SOURCE_EXPANSION_STRATEGY.md`](./DATA_SOURCE_EXPANSION_STRATEGY.md)
  - 数据源扩展与规划说明
- [`DATA_SOURCE_MONITORING_GUIDE.md`](./DATA_SOURCE_MONITORING_GUIDE.md)
  - 数据源监控系统集成指南
- [`DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md`](./DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md)
  - 与当前运维手册/开发者文档对齐后的部署前检查入口
- [`DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md`](./DATA_SOURCE_OPTIMIZATION_QUICK_REFERENCE.md)
  - 优化方案快速参考
- [`../../reports/tasks/optimize-data-source-v2-external-acceptance-handoff-2026-05-05.md`](../../reports/tasks/optimize-data-source-v2-external-acceptance-handoff-2026-05-05.md)
  - `optimize-data-source-v2` 当前 repo-local 收口后的外部验收交接入口

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只保留当前仍有较强直接使用价值的接入、管理与速查入口，其余清洗、监控、优化与扩展材料统一通过本 index 进入
- 若后续 specialized references 的实际入链继续下降，可继续按 bounded batch 单独评估 archive/delete
