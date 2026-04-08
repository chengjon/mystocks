# Historical Evidence Trunk

> **历史索引说明**:
> 本文件是 `docs/reports/` 的 canonical historical-evidence entrypoint，用于把读者导向报告、复盘、审计材料和历史计划快照。
> 它不是当前实施状态、当前能力真相或仓库共享规则的唯一事实来源；当前规则与主线仍分别以 `architecture/STANDARDS.md`、`openspec/specs/` 和已批准变更为准。

## How To Use Reports

进入 `docs/reports/` 时，先判断你的目标：

- 要看治理执行证据：
  [`documentation-governance/`](/opt/claude/mystocks_spec/docs/reports/documentation-governance/)
- 要看技术债、质量或代码审查材料：
  [`technical_debt/`](/opt/claude/mystocks_spec/docs/reports/technical_debt/),
  [`quality/`](/opt/claude/mystocks_spec/docs/reports/quality/),
  [`reviews/`](/opt/claude/mystocks_spec/docs/reports/reviews/)
- 要看测试与验证产物：
  [`test-reports/`](/opt/claude/mystocks_spec/docs/reports/test-reports/),
  [`test-reports-e2e/`](/opt/claude/mystocks_spec/docs/reports/test-reports-e2e/),
  [`api_verification/`](/opt/claude/mystocks_spec/docs/reports/api_verification/)
- 要看清理、迁移或阶段性交付材料：
  [`cleanup/`](/opt/claude/mystocks_spec/docs/reports/cleanup/),
  [`phase_reports/`](/opt/claude/mystocks_spec/docs/reports/phase_reports/),
  [`completion_reports/`](/opt/claude/mystocks_spec/docs/reports/completion_reports/)
- 要看历史工作日志或任务包：
  [`worklogs/`](/opt/claude/mystocks_spec/docs/reports/worklogs/),
  [`tasks/`](/opt/claude/mystocks_spec/docs/reports/tasks/)

## Root-Level Files

`docs/reports/` 根目录下仍存在大量历史快照、报告、计划摘要和专题材料。

这些 root-level markdown 默认应按 historical evidence 使用：

- 可以阅读、检索、回溯
- 不应被当作当前 canonical trunk
- 若与当前代码、OpenSpec 或仓库级规则冲突，以主线 truth 为准

## Legacy And Archive

- 历史中文 legacy cluster 已迁出 active tree：
  [`archive/docs/reports/legacy-cn-2026-04-08/`](/opt/claude/mystocks_spec/archive/docs/reports/legacy-cn-2026-04-08/)
- [`INDEX.md`](/opt/claude/mystocks_spec/docs/reports/INDEX.md) 仅作为旧链接兼容索引保留，不再维护为权威总览

## Reader Routing

- 当前规则、审批门禁、删除标准：
  [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)
- 当前 capability truth：
  [`openspec/specs/`](/opt/claude/mystocks_spec/openspec/specs/)
- 当前批准中的变更：
  [`openspec/changes/`](/opt/claude/mystocks_spec/openspec/changes/)
- 文档系统 trunk map：
  [`docs/overview/documentation-system.md`](/opt/claude/mystocks_spec/docs/overview/documentation-system.md)

## Governance Status

- `docs/reports/README.md` 保留为唯一 reports historical-evidence trunk
- `docs/reports/` 主要用于 retention, audit, verification, retrospective
- 后续治理应继续做 bounded archive/classification，而不是把 reports 根入口扩写成新的 current-truth 总览
