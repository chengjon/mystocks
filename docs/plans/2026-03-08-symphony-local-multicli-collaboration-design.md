# Symphony Local-First Multi-CLI Collaboration Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Context

MyStocks 当前已经引入 Symphony，并已将默认 tracker 从 Linear 切换为本地 SQLite。与此同时，
仓库已有一套成熟的多 CLI 协作规范，核心包括：

- `main` 分支承担主 CLI 的协调职责
- 非 `main` worktree 承担 worker CLI 的执行职责
- `.FILE_OWNERSHIP` 约束模块边界
- `TASK.md` / `TASK-REPORT.md` 用于任务约定、执行汇报与阻塞留痕

现阶段的问题不是“再造一套协作体系”，而是让 Symphony 和现有体系自然衔接，减少开发者重复做
分发、监控、回收、催办等流程性工作。

## Goals

- 保持 **本地优先**：默认使用 SQLite tracker，不依赖 Linear
- 保持 **人工治理优先**：`TASK.md` / `TASK-REPORT.md` 继续由开发者与主 CLI 形成
- 让 Symphony 负责 **任务形成后的自动化流程**
- 让 Symphony 的行为契合多 CLI 文档中的主 CLI / worker CLI 分工
- 为未来的心跳监控、重派、stale 检测预留清晰扩展点

## Non-Goals

- 本次不让 Symphony 自动生成或重写 `TASK.md`
- 本次不让 Symphony 自动替 worker 编写完整 `TASK-REPORT.md`
- 本次不移除现有 Linear 兼容代码
- 本次不一次性实现完整的“多 worktree 调度平台”

## Core Decision

采用 **双层协作模型**：

1. **人工协作层**
   - `TASK.md`
   - `TASK-REPORT.md`
   - `.FILE_OWNERSHIP`
   - 主 CLI / 开发者的任务拆分与验收决策

2. **机器执行层**
   - SQLite tracker
   - Symphony orchestrator
   - workspace / worktree 生命周期
   - worker 会话分发、心跳监控、重试、stale 检测

这意味着：

- `TASK.md` 回答“做什么、谁做、标准是什么”
- `TASK-REPORT.md` 回答“人工完成了什么、卡在哪、证据是什么”
- Symphony 回答“谁正在跑、是否卡住、是否该重试、是否该提醒主 CLI”

## Responsibility Boundary

### 开发者 / 主 CLI

- 形成或确认 `TASK.md`
- 指定 owner、模块边界、依赖关系、验收标准
- 审阅 `TASK-REPORT.md`
- 做最终合并、回滚、重派决策

### Worker CLI

- 遵循 `TASK.md`
- 遵循 `.FILE_OWNERSHIP`
- 更新 `TASK-REPORT.md`
- 提供验证证据

### Symphony

- 从 SQLite tracker 读取“已准备执行”的 issue
- 创建或复用 issue workspace
- 作为自动化执行层拉起 worker session
- 暴露 session 运行态、最近事件、心跳/stale 信息
- 在异常退出时记录失败并支持后续重试 / 重派
- 不越权改写人工协作契约

## Target Operating Flow

1. 开发者 / 主 CLI 完成任务拆分并更新 `TASK.md`
2. 主 CLI 或开发者将 issue 标记为可执行（tracker 中进入活跃状态）
3. Symphony 读取本地 tracker，分发 issue 到对应 worker 运行上下文
4. Worker session 在其 workspace 中：
   - 读取 `TASK.md`
   - 读取 `TASK-REPORT.md`
   - 遵循 `.FILE_OWNERSHIP`
   - 执行任务并补充报告
5. Symphony 通过状态 API 提供运行态与心跳视图
6. 主 CLI 根据 `TASK-REPORT.md` + Symphony 状态完成协调与收尾

## Minimal First Implementation

第一阶段只做最有价值且低风险的改动：

1. **Prompt 对齐**
   - 在 `WORKFLOW.md` 中明确：
     - `TASK.md` / `TASK-REPORT.md` 为人工协作产物
     - worker 只在既定任务范围内执行
     - 严格遵守 `.FILE_OWNERSHIP`

2. **Hook 上下文增强**
   - 在 workspace hooks 中注入更多环境变量
   - 便于后续接 worktree、owner、issue 上下文

3. **状态 API 增强**
   - 为 running issue 增加 heartbeat / stale 视图
   - 让 Symphony 可以承担“自动化监工”角色

4. **操作指南**
   - 补一份专门的本地 SQLite + 多 CLI 协作说明

## Future Extensions

后续如继续推进，可按顺序增加：

- issue assignment / owner registry
- stale worker 自动提醒
- worktree 注册表
- blocked / awaiting-review / ready-to-merge 等更细状态
- 主 CLI 批量重派与回收

## Why This Is Better Than Linear-First

- 减少远程依赖与鉴权成本
- 保持现有多 CLI 流程不变，只把重复劳动自动化
- 人工决策与机器执行边界清晰，调试成本更低
- 数据模型本地可控，更适合个人项目与本地开发环境
