# Multi-CLI Worktree Operations Center

欢迎来到多 CLI 协作运营中心（`.multi-cli-tasks/`）。这是本项目管理并行开发生命周期的指挥舱。采用点前缀命名，表明其为工具链工作目录，区别于常规项目目录。

**当前主手册版本**: v3.1（在 v2.2 基础上吸收 v3.0 的 AI-CLI 协作治理条款）
**最后更新**: 2026-03-04

## 🏢 目录架构

- **[guides/](./guides/)**: 核心规范与手册
  - **[MULTI_CLI_WORKTREE_MANAGEMENT.md](./guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)**: 体系总纲 (核心, v3.1)
  - **[MAIN_CLI_WORKFLOW.md](./guides/MAIN_CLI_WORKFLOW.md)**: 主 CLI 规范 (v3.1)
  - **[WORKER_CLI_GUIDE.md](./guides/WORKER_CLI_GUIDE.md)**: Worker CLI 指南 (v3.1)
  - **[MONITORING_GUIDE.md](./guides/MONITORING_GUIDE.md)**: 监控指南 (v3.1)
  - **[GIT_WORKTREE_MAIN_CLI_MANUAL.md](./guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md)**: Git 命令参考 (v3.1)
  - **[CONFLICT_PREVENTION.md](./guides/CONFLICT_PREVENTION.md)**: 冲突预防 (v3.1)
  - **[GIT_REMOTE_NAME_STANDARD.md](./guides/GIT_REMOTE_NAME_STANDARD.md)**: 远程命名标准 (v3.1)
  - **[OPERATIONAL_RESILIENCE.md](./guides/OPERATIONAL_RESILIENCE.md)**: 运营韧性补充 (v3.1)
- **[guides/templates/](./guides/templates/)**: 标准化任务书与报告模板 (v3.1)
  - **[TASK_TEMPLATE.md](./guides/templates/TASK_TEMPLATE.md)**: 任务与报告模板
  - **[FILE_OWNERSHIP.template](./guides/templates/FILE_OWNERSHIP.template)**: 文件所有权模板
- **mystocks_phaseX_.../**: 各个活跃或已结项的任务单元子目录。

## 🕹️ 快速操作

1.  **查阅标准**: 请进入 `guides/` 查阅对应的标准文档。
2.  **管理任务**: 请进入对应的worktree目录查看 `TASK.md` 和 `TASK-REPORT.md`。
3.  **阶段总结**: 查阅根目录下的 `PHASE_X_SUMMARY.md`, 由主CLI根据各个worktree目录下的 `TASK.md` 和 `TASK-REPORT.md`整合编辑。

---
*保持扁平，高效协作。*
