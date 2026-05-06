# Governance Guide Family

> **导航说明**:
> 本文件是 `docs/guides/governance/` 的 transition index，不是仓库共享规则、审批门禁或当前治理口径的唯一事实来源。
> 若需确认当前仓库级治理规则，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若需确认文档系统 trunk 与 lifecycle，请优先阅读 [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)。

## Current Trunk First

这一 family 只保留 focused workflow helpers，不再承担并行 governance trunk 的角色。当前阅读顺序是：

1. [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)
2. [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)
3. 再按需进入本 family 的专题执行指南

## Active Supporting Guides

- [`FEATURE_MANAGEMENT_WORKFLOW.md`](./FEATURE_MANAGEMENT_WORKFLOW.md)
  - 功能状态、功能树、task card / PR 镜像与变更同步流程
- [`TECHNICAL_DEBT_MANAGEMENT.md`](./TECHNICAL_DEBT_MANAGEMENT.md)
  - 技术债识别、分级、偿还与预防的专题执行细则
- [`API_CONTRACT_RUNTIME_VALIDATION_DEVELOPER_GUIDE.md`](./API_CONTRACT_RUNTIME_VALIDATION_DEVELOPER_GUIDE.md)
  - API 契约 runtime validation 的 current-state developer guide
- [`API_CONTRACT_TESTING_BEST_PRACTICES.md`](./API_CONTRACT_TESTING_BEST_PRACTICES.md)
  - API 契约测试目录、fixtures、推荐命令与反模式说明
- [`API_CONTRACT_IMPACT_ANALYSIS_USAGE_GUIDE.md`](./API_CONTRACT_IMPACT_ANALYSIS_USAGE_GUIDE.md)
  - 当前 diff-based contract impact analysis 工作流使用说明

## Retention Rule

- 该 family 当前角色是 `supporting`
- 专题治理流程允许保留，但不得覆盖 `architecture/STANDARDS.md` 的共享规则地位
- 历史索引或局部导航可以继续引用本 family 内文档，但不应把它们当成仓库级治理真相源
