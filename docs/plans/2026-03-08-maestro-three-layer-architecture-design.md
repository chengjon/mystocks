# Maestro Three-Layer Architecture Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Context

`Symphony` 在 MyStocks 中已经从“偏 Linear 的通用 orchestrator”演进为：

- 本地 SQLite tracker 驱动
- 面向多 CLI 协作
- 以 `TASK.md` / `TASK-REPORT.md` 为人工契约
- 以自动分发、执行、监控为运行层

此时继续只使用 `Symphony` 这个仓库内实现名，会让未来的独立化路径不够清晰。因此需要一个
更适合作为外部工具家族名的命名方案，以及一套便于迁移的三层边界。

## Naming Recommendation

推荐长期家族名为 **`Maestro`**。

原因：

- 与“编排、指挥、协同执行”语义直接对应
- 比 `Symphony` 更强调“控制面 / 调度面”
- 更适合作为一个可抽离的工具名，而不是单仓库特性名

命名策略：

- **家族名**：`Maestro`
- **当前兼容实现名**：`Symphony`
- **迁移策略**：先在仓库内建立 `src/services/maestro` 兼容 namespace，随后逐步把通用能力迁移到该命名体系

## Three Layers

### 1. `maestro.kernel`

职责：

- 通用 orchestration runtime
- tracker 装配
- agent 执行
- 状态 API
- 工作流解析与运行时配置

这层未来应该能脱离 MyStocks 单独运行。

### 2. `maestro.collab`

职责：

- 多 CLI 协作管理核心
- workspace / worktree 生命周期
- owner / assignment / heartbeat / stale 管理
- 与 `TASK.md` / `TASK-REPORT.md` 对接的自动化流程

这层是未来与 `kernel` 一起迁移出去的重点。

### 3. `maestro.profiles`

职责：

- 仓库专属 profile
- prompt 模板
- 默认 tracker / workflow 绑定
- 本项目特有协作约束

当前对应的是 `maestro.profiles.mystocks`。

## Migration Shape

未来独立化时建议按以下方式拆分：

1. 外部工具仓库：
   - `maestro.kernel`
   - `maestro.collab`
2. MyStocks 仓库：
   - `maestro.profiles.mystocks`
   - 以及 repo-owned `WORKFLOW.md`

这样可以实现：

- 通用运行时复用
- 多 CLI 管理核心复用
- 各项目仅保留自己的 profile 和策略绑定

## Near-Term Implementation

本轮只做最小且可持续的动作：

- 建立 `src/services/maestro` 兼容 namespace
- 在文档中固化责任模型与三层边界
- 保留 `src/services/symphony` 作为现有兼容实现入口

## Deferred Work

- 真正把实现文件迁移到 `maestro/kernel`、`maestro/collab` 下
- 为 assignment / heartbeat / worktree registry 建立持久化模型
- 让 profile 以更明确的插件方式挂接 runtime
