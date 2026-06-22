# Historical Evidence Trunk

> **历史索引说明**:
> 本文件是 `docs/reports/` 的 canonical historical-evidence entrypoint，用于把读者导向报告、复盘、审计材料和历史计划快照。
> 它不是当前实施状态、当前能力真相或仓库共享规则的唯一事实来源；当前规则与主线仍分别以 `architecture/STANDARDS.md`、`openspec/specs/` 和已批准变更为准。

## 2026-06-09 归档说明

以下 35 个子目录已整体归档至 [`archive/docs/reports/`](../../archive/docs/reports/)：

| 归档目录 | 说明 |
|----------|------|
| `analysis/` | 分析报告（TDX 可行性评估等） |
| `api_split/` | API 拆分报告 |
| `api_verification/` | API 验证产物 |
| `architecture-governance/` | 架构治理证据 |
| `artdeco-alignment/` | ArtDeco 对齐报告 |
| `batch-coverage-html/` | HTML 覆盖率报告 |
| `bugs/` | Bug 报告 |
| `cleanup/` | 清理操作记录 |
| `cli_reports/` | CLI 报告 |
| `code_quality/` | 代码质量报告 |
| `completion_reports/` | 完成报告 |
| `data-classification-coverage-html/` | 数据分类覆盖率 |
| `design/` | 设计报告 |
| `documentation-governance/` | 文档治理证据 |
| `evidence/` | 通用验证证据 |
| `hooks/` | Hooks 相关报告 |
| `load_test_reports/` | 负载测试报告 |
| `misc/` | 杂项 |
| `monitoring_reports/` | 监控报告 |
| `performance/` | 性能报告 |
| `phase4_6/` | Phase 4-6 报告 |
| `phase_reports/` | 阶段报告 |
| `plans/` | 历史计划 |
| `quality/` | 质量审计（含 HTML5 migration 证据） |
| `reviews/` | 代码审查记录 |
| `screenshots/` | 截图 |
| `security/` | 安全相关 |
| `smart_analysis_reports/` | 智能分析报告 |
| `tasks/` | 任务包 |
| `technical_debt/` | 技术债报告 |
| `test-reports/` | 测试报告 |
| `test-reports-e2e/` | E2E 测试报告 |
| `test_reports/` | 测试报告（旧） |
| `wencai/` | Wencai 报告 |
| `worklogs/` | 工作日志 |

如需查找归档内容，请在 `archive/docs/reports/<目录名>/` 中查找。

## Root-Level Files

`docs/reports/` 根目录下仍保留约 685 个历史报告文件。这些 root-level markdown 默认按 `report` 生命周期使用：

- 可以阅读、检索、回溯
- 不应被当作当前 canonical trunk
- 若与当前代码、OpenSpec 或仓库级规则冲突，以主线 truth 为准

文档治理证据目录仍可从 `/opt/claude/mystocks_spec/docs/reports/documentation-governance/` 回溯。
仓库共享规则主入口的物理路径是 `/opt/claude/mystocks_spec/architecture/STANDARDS.md`。

## Legacy And Archive

- 中文 legacy cluster 已迁出 active tree：`archive/docs/reports/legacy-cn-2026-04-08/`
- 2026-06-09 批量归档：35 个子目录已移至 `archive/docs/reports/`
- [`INDEX.md`](INDEX.md) 仅作为旧链接兼容索引保留，不再维护为权威总览

## Reader Routing

- 当前规则、审批门禁、删除标准：[`architecture/STANDARDS.md`](../../architecture/STANDARDS.md)
- 当前 capability truth：[`openspec/specs/`](../../openspec/specs/)
- 当前批准中的变更：[`openspec/changes/`](../../openspec/changes/)
- 文档系统 trunk map：[`docs/overview/documentation-system.md`](../overview/documentation-system.md)

## Governance Status

- `docs/reports/README.md` 保留为唯一 reports historical-evidence trunk
- `docs/reports/` 主要用于 retention, audit, verification, retrospective
- 后续治理应继续做 bounded archive/classification，而不是把 reports 根入口扩写成新的 current-truth 总览
