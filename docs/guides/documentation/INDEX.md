# Documentation Guide Family

> **导航说明**:
> 本文件是 `docs/guides/documentation/` 的 transition index，不是仓库共享规则、当前 trunk map 或当前实现状态的唯一事实来源。
> 若涉及文档系统 canonical trunk、治理口径或 reader routing，请优先阅读 [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)；若涉及审批门禁与删除判定，再回到 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)。

## Current Trunk First

这一 family 不再单独承担 documentation governance trunk 的职责。当前阅读顺序是：

1. [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)
2. [`CANONICAL_TRUNK_ADMISSION_GUIDE.md`](/opt/claude/mystocks_spec/docs/guides/documentation/CANONICAL_TRUNK_ADMISSION_GUIDE.md)
3. 再按需进入本 family 内的 supporting workflow / methodology guides

## Active Supporting Guides

- [`CANONICAL_TRUNK_ADMISSION_GUIDE.md`](./CANONICAL_TRUNK_ADMISSION_GUIDE.md)
  - 文档准入、lifecycle 选择与最小治理检查
- [`DOCUMENTATION_WORKFLOW_GUIDE.md`](./DOCUMENTATION_WORKFLOW_GUIDE.md)
  - 文档整理、命名、索引更新与提交流程

## Retained Specialized References

以下文件继续保留在 `documentation/` family 中，但作为专题 supporting/reference guide 使用，不应被误读为并行 trunk：

- [`文件目录整理方法论指南.md`](./文件目录整理方法论指南.md)
  - 目录治理方法论、诊断模型与反模式
- [`文件目录管理方案.md`](./文件目录管理方案.md)
  - 通用目录治理最佳实践蓝图
- [`文档管理指南.md`](./文档管理指南.md)
  - 文档查找、边界说明写法与导航习惯
- [`文档结构说明.md`](./文档结构说明.md)
  - 历史结构说明与目录演化背景
- [`超长文档拆分办法.md`](./超长文档拆分办法.md)
  - 面向超长文档/文件拆分的专项方法

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 若后续某篇指南的 canonical replacement 已完全明确且 inbound links 清理完成，再按 bounded batch 单独归档或删除
- 在 delete gate 未满足前，默认保留这些专题指南作为 supporting/reference docs
