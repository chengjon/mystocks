# Docs Index

**最后更新**: 2026-03-12

---

## 推荐先读

- [架构红线与审批门禁](../architecture/STANDARDS.md) - 所有写操作前必须先对齐的治理基线
- [AI Quick Start](./guides/AI_QUICK_START.md) - 按任务类型选择正确入口，再回到功能域
- [功能树 (FUNCTION_TREE.md)](./FUNCTION_TREE.md) - 业务能力总线，按功能域定位规范、代码、测试和运行入口
- [功能管理工作流](./guides/FEATURE_MANAGEMENT_WORKFLOW.md) - 功能状态、入口同步和 PR 填写要求

---

## AI 快速开始

- [AI Quick Start](./guides/AI_QUICK_START.md) - 完整任务路由、最小读取路径和文档优先级
- 最短原则：先判断任务类型，再读治理入口，再回到 [功能树](./FUNCTION_TREE.md) 的目标功能域
- 不要先做目录式全仓搜索；优先使用功能树里的“领域入口”表定位规范、代码、测试和运行入口

---

## 功能管理入口

- [功能树 (FUNCTION_TREE.md)](./FUNCTION_TREE.md) - 所有功能的完整清单、状态和领域入口
- [更新日志 (CHANGELOG.md)](../CHANGELOG.md) - 版本变更记录
- [功能管理工作流](./guides/FEATURE_MANAGEMENT_WORKFLOW.md) - 功能开发、维护、废弃流程与 PR 对齐要求
- [测试文档总览](./testing/README.md) - 测试策略与验证入口
- [运维文档总览](./operations/README.md) - 运行、发布、排障入口

---

## 治理入口

- [主线治理专用目录 README](../governance/mainline/README.md)
- [主线治理执行规范 v0.2](../governance/mainline/spec/ai-development-mainline-governance-spec.md)
- [主线治理任务总结与使用手册](../governance/mainline/reports/mainline-governance-v0.2-task-summary.md)
- [OpenSpec 工作流](../openspec/AGENTS.md)

## 主线治理链路（从输入到合并）

1. 任务卡模板：`governance/mainline/templates/ai-task-card.yaml`
2. 任务卡 Schema：`governance/mainline/schemas/ai-task-card.schema.json`
3. 本地门禁脚本：`governance/mainline/scripts/mainline_scope_gate.py`
4. CI 门禁工作流：`.github/workflows/mainline-governance.yml`
5. PR 模板入口：`.github/pull_request_template.md`
6. 功能域字段补充：`docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md`
7. 报告产物：`governance/mainline/reports/mainline-governance-report.json`

## 说明

- 每个 PR 必须提供 `governance/mainline/task-cards/pr-<PR号>.yaml`。
- `feature` 类型必须满足：
  - `openspec.change_id` 非空
  - `openspec.approval_status = approved`
- 若 PR 涉及功能变化、入口变化或跨域改动，必须同时对齐 `FUNCTION_TREE` 节点和功能管理工作流中的字段要求。
- 门禁失败后禁止绕过，必须修复根因。
