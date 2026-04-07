# Maestro Runtime Seed

> **参考指南说明**:
> 本文件用于说明 `src/` 目录下局部模块的使用方式、结构背景、调试方法、部署提示或技术参考，帮助理解具体实现。
> 其中的路径、步骤、指标和示例应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为共享规则或当前状态的唯一事实来源。


`Maestro` 是这套系统面向未来独立化的推荐家族名。

当前仓库内仍保留 `src/services/symphony` 作为兼容实现名，但对外的长期分层架构建议为：

1. `maestro.kernel`
   - 通用 orchestration runtime
   - tracker 装配
   - agent 执行
   - 状态 API
2. `maestro.collab`
   - 多 CLI 协作管理核心
   - assignment / workspace(worktree) registry / heartbeat(stale) 持久化
   - owner-aware dispatch gating / stale reclaim
   - `.FILE_OWNERSHIP` + `TASK.md` 驱动的 advisory owner suggestion
   - workspace / worktree / owner / task contract 自动化
3. `maestro.profiles`
   - 项目级 profile
   - 例如 `maestro.profiles.mystocks`

当前阶段 `maestro` 还是一个兼容 namespace，底层实现主要复用 `symphony` 模块；后续可以逐步把
`kernel` 与 `collab` 抽离成独立工具，再由各仓库保留自己的 `profiles`。

配套文档：

- `docs/guides/multi-cli-tasks/MAESTRO_SUMMARY.md`
- `docs/guides/multi-cli-tasks/MAESTRO_QUICK_START.md`
- `docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
