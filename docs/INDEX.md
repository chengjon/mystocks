# Docs Index

**最后更新**: 2026-03-01

---

## 治理入口（推荐先读）

- [主线治理专用目录 README](../governance/mainline/README.md)
- [主线治理执行规范 v0.2](../governance/mainline/spec/ai-development-mainline-governance-spec.md)
- [主线治理任务总结与使用手册](../governance/mainline/reports/mainline-governance-v0.2-task-summary.md)
- [架构红线与审批门禁](../architecture/STANDARDS.md)
- [OpenSpec 工作流](../openspec/AGENTS.md)

## 主线治理链路（从输入到合并）

1. 任务卡模板：`governance/mainline/templates/ai-task-card.yaml`
2. 任务卡 Schema：`governance/mainline/schemas/ai-task-card.schema.json`
3. 本地门禁脚本：`governance/mainline/scripts/mainline_scope_gate.py`
4. CI 门禁工作流：`.github/workflows/mainline-governance.yml`
5. PR 模板入口：`.github/pull_request_template.md`
6. 报告产物：`governance/mainline/reports/mainline-governance-report.json`

## 说明

- 每个 PR 必须提供 `governance/mainline/task-cards/pr-<PR号>.yaml`。
- `feature` 类型必须满足：
  - `openspec.change_id` 非空
  - `openspec.approval_status = approved`
- 门禁失败后禁止绕过，必须修复根因。
