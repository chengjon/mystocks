# Multi-CLI Tasks Family

> **导航说明**:
> 本文件是 `docs/guides/multi-cli-tasks/` 的 transition index，不是仓库共享规则、当前执行真相或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md)；若涉及具体执行入口，再结合根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前脚本实现、Mongo control plane 输出与最近一次实际验证结果核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留 multi-CLI 协作、注册、任务池、worktree、Mongo coordination 与 Maestro/Symphony 历史资料，不承担仓库级 trunk。推荐阅读顺序：

1. [`CLI_REGISTRATION_GUIDE.md`](./CLI_REGISTRATION_GUIDE.md)
2. [`TASK_POOL_USAGE_GUIDE.md`](./TASK_POOL_USAGE_GUIDE.md)
3. [`CLI_WORKFLOW_GUIDE.md`](./CLI_WORKFLOW_GUIDE.md)
4. [`MAIN_CLI_WORKFLOW_STANDARDS.md`](./MAIN_CLI_WORKFLOW_STANDARDS.md)
5. [`MONGO_MULTICLI_COORDINATION_GUIDE.md`](./MONGO_MULTICLI_COORDINATION_GUIDE.md)
6. [`MONGO_MULTICLI_OPERATION_CHECKLIST.md`](./MONGO_MULTICLI_OPERATION_CHECKLIST.md)
7. [`MULTI_CLI_WORKTREE_MANAGEMENT.md`](./MULTI_CLI_WORKTREE_MANAGEMENT.md)
8. [`BRANCH_STRATEGY.md`](./BRANCH_STRATEGY.md)
9. 再按需进入 Maestro/Symphony、prompt、config、roles 与其他历史方法/提案材料

## Active Supporting Guides

- [`CLI_REGISTRATION_GUIDE.md`](./CLI_REGISTRATION_GUIDE.md)
  - CLI 报到流程与执行入口
- [`TASK_POOL_USAGE_GUIDE.md`](./TASK_POOL_USAGE_GUIDE.md)
  - 任务池发布、认领与更新指南
- [`CLI_WORKFLOW_GUIDE.md`](./CLI_WORKFLOW_GUIDE.md)
  - Worker CLI 标准流程说明
- [`MAIN_CLI_WORKFLOW_STANDARDS.md`](./MAIN_CLI_WORKFLOW_STANDARDS.md)
  - Main CLI 工作规范与最佳实践
- [`MONGO_MULTICLI_COORDINATION_GUIDE.md`](./MONGO_MULTICLI_COORDINATION_GUIDE.md)
  - Mongo control plane 下的 multi-CLI 协作说明
- [`MONGO_MULTICLI_OPERATION_CHECKLIST.md`](./MONGO_MULTICLI_OPERATION_CHECKLIST.md)
  - Mongo coordination checklist
- [`MULTI_CLI_WORKTREE_MANAGEMENT.md`](./MULTI_CLI_WORKTREE_MANAGEMENT.md)
  - 多 CLI worktree 管理手册
- [`BRANCH_STRATEGY.md`](./BRANCH_STRATEGY.md)
  - 分支策略与开发流程

## Retained Specialized References

- [`CLI_ROLES_REFERENCE.md`](./CLI_ROLES_REFERENCE.md)
  - CLI 角色查看与辅助参考
- [`CONFIG_SYSTEM_GUIDE.md`](./CONFIG_SYSTEM_GUIDE.md)
  - Multi-CLI 配置系统使用指南
- [`GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md`](./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md)
  - Git worktree 协作冲突预防规范
- [`MAESTRO_QUICK_START.md`](./MAESTRO_QUICK_START.md)
  - Maestro quick start
- [`MAESTRO_SUMMARY.md`](./MAESTRO_SUMMARY.md)
  - Maestro 总结与边界说明
- [`MULTI_CLI_COLLABORATION_METHOD.md`](./MULTI_CLI_COLLABORATION_METHOD.md)
  - 多 CLI 协作方法历史方案
- [`MULTI_CLI_OPTIMIZATION_PROPOSAL.md`](./MULTI_CLI_OPTIMIZATION_PROPOSAL.md)
  - 多 CLI 协作优化提案
- [`MULTI_CLI_PROMPT_STRATEGIES.md`](./MULTI_CLI_PROMPT_STRATEGIES.md)
  - Prompt 策略与模板材料
- [`SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`](./SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md)
  - Symphony 本地 SQLite + 多 CLI 工作流
- [`worktree.md`](./worktree.md)
  - 历史 worktree 辅助说明

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只保留当前仍有较高直接使用价值的 registration、task pool、workflow、main-cli、Mongo coordination 与 worktree runbook
- Maestro/Symphony、prompt、config、roles、optimization proposal 与其他历史方法材料统一通过本 index 进入
- 后续若这些 retained references 的实际入链继续下降，可继续按 bounded batch 单独评估 archive/delete
