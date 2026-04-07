# Multi-CLI Worktree Operations Center

> **使用说明**:
> 本文件用于说明多 CLI 协作流程中的当前入口、任务工件或执行方式，服务于协作推进过程中的上下文同步。
> 其中的步骤、状态和局部约束不能脱离 `architecture/STANDARDS.md`、当前协作口径与实际执行结果单独解读为最终事实。


欢迎来到多 CLI 协作运营中心（`.multi-cli-tasks/`）。这是本项目管理并行开发生命周期的指挥舱。采用点前缀命名，表明其为工具链工作目录，区别于常规项目目录。

**当前主手册版本**: v3.2（在 v3.1 基础上切换到 `main` 协调验收制 + `worktree/dev-*` 开发制）
**最后更新**: 2026-03-05

## 🏢 目录架构

- **[guides/](./guides/)**: 核心规范与手册
  - **[MULTI_CLI_WORKTREE_MANAGEMENT.md](./guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)**: 体系总纲 (核心, v3.2)
  - **[MAIN_CLI_WORKFLOW.md](./guides/MAIN_CLI_WORKFLOW.md)**: 主 CLI 规范 (v3.2)
  - **[WORKER_CLI_GUIDE.md](./guides/WORKER_CLI_GUIDE.md)**: Worker CLI 指南 (v3.2)
  - **[MONITORING_GUIDE.md](./guides/MONITORING_GUIDE.md)**: 监控指南 (v3.2)
  - **[GIT_WORKTREE_MAIN_CLI_MANUAL.md](./guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md)**: Git 命令参考 (v3.2)
  - **[CONFLICT_PREVENTION.md](./guides/CONFLICT_PREVENTION.md)**: 冲突预防 (v3.2)
  - **[GIT_REMOTE_NAME_STANDARD.md](./guides/GIT_REMOTE_NAME_STANDARD.md)**: 远程命名标准 (v3.2)
  - **[OPERATIONAL_RESILIENCE.md](./guides/OPERATIONAL_RESILIENCE.md)**: 运营韧性补充 (v3.2)
  - **[AI_PROMPT_AND_MANUAL_SOP.md](./guides/AI_PROMPT_AND_MANUAL_SOP.md)**: AI复用 Prompt 与人工SOP
- **[guides/templates/](./guides/templates/)**: 标准化任务书与报告模板 (v3.2)
  - **[TASK_TEMPLATE.md](./guides/templates/TASK_TEMPLATE.md)**: 任务与报告模板
  - **[FILE_OWNERSHIP.template](./guides/templates/FILE_OWNERSHIP.template)**: 文件所有权模板
- **mystocks_phaseX_.../**: 各个活跃或已结项的任务单元子目录。

## 🕹️ 快速操作

1.  **查阅标准**: 请进入 `guides/` 查阅对应的标准文档。
2.  **管理任务**: 请进入对应的worktree目录查看 `TASK.md` 和 `TASK-REPORT.md`。
3.  **阶段总结**: 查阅根目录下的 `PHASE_X_SUMMARY.md`, 由主CLI根据各个worktree目录下的 `TASK.md` 和 `TASK-REPORT.md`整合编辑。
4.  **历史路径迁移**（如仍存在仓库内 `.worktrees/`）:
    `bash scripts/worktree/migrate_worktrees_to_parallel.sh --target-root /opt/claude`

## ✅ v3.2 治理快照（执行优先级最高）

1. `main` 只做协调与验收，不直接做功能开发。
2. 新功能统一在 `worktree/dev-*` 分支开发。
3. 每个 worktree 分支通过 PR 合并到 `main`。
4. PR 必须包含：变更范围、验证命令与结果、风险/回滚说明。
5. 合并前必须通过三道门禁：质量门（TS/Python/tests）、安全门（secrets/audit/SAST）、审查门（code review）。
6. `main` 仅保留“干净、可复现、可回滚”版本。

---
*保持扁平，高效协作。*
