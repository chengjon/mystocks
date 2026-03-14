# Symphony 本地 SQLite + 多 CLI 协作工作流

## 一句话原则

`TASK.md` / `TASK-REPORT.md` 是人工协作契约，`Maestro/Symphony` 是契约形成后的自动化执行层，而 MongoDB Multi-CLI Coordination 是 `maestro.collab` 的下一代协作控制面。

为匹配本项目的本地优先 + 多 CLI 工作流，仓库根目录的 `TASK.md` / `TASK-REPORT.md` 被目录治理策略定义为 **workflow-approved exceptions**：它们是当前协作机制的正式入口与回报面，不再视为“待迁移债务”。

## 当前阶段边界（2026-03-13）

- 当前已落地基线仍是 `SQLite tracker + SQLite collaboration registry`
- `MongoDB Multi-CLI Coordination` 当前归属 `maestro.collab` 演进线，不作为平行新系统存在
- 本期目标是在 MyStocks 内验证 Mongo 协作主事实源，而不是立即独立拆仓
- 在切换期内，`TASK.md` 继续承担任务契约职责
- 在切换期内，`TASK-REPORT.md` 允许从 Mongo 协作状态导出摘要，并保留人工异常补充

## 权威责任模型

- **人**：定义目标、方向、总任务和高层约束
- **`main CLI`**：拆解总任务，结合约束/依赖/`.FILE_OWNERSHIP` 决定 owner 与 worker CLI，定义验收标准，维护 `TASK.md`，审阅 `TASK-REPORT.md`
- **`worker CLI`**：按 `TASK.md` 执行，在 owner 边界内修改，更新协作状态，并在需要时补充 `TASK-REPORT.md` 证据
- **Symphony / `Maestro Runtime`**：在任务进入活跃状态后负责自动化分发、执行、监控、心跳、stale 检测、重试与状态汇总
- **Mongo Coordination Control Plane**：负责主 CLI 分发、worker 更新、request 审批和跨 worker 汇总

这几类角色中，只有人和 `main CLI` 可以定义任务契约；运行时系统和协作控制面只负责契约之后的自动化流程。  
其中 `main CLI` 可以使用 `maestro.collab` 的建议能力辅助判断 owner，但最终分配动作仍是显式人工决定。

## 角色分工

### 开发者 / 主 CLI

- 拆任务、定 owner、定边界、定验收
- 维护 `TASK.md`
- 审阅 `TASK-REPORT.md`
- 做重派、合并、回滚决策

### Worker CLI

- 读取 `TASK.md`
- 在 owner 边界内执行
- 更新协作状态
- 在需要时补充 `TASK-REPORT.md`
- 提供验证证据

### Symphony / Maestro Runtime

- 读取 SQLite tracker 中已进入活跃状态的任务
- 拉起对应 worker 执行会话
- 暴露运行态、最近事件、heartbeat / stale 视图
- 负责自动化分发、监控、重试，不负责任务定义

### MongoDB Coordination Control Plane

- 归属 `maestro.collab` 的下一代协作控制面
- 管理主 CLI 分发、worker 更新、request 审批和跨 worker 汇总
- 在当前阶段与现有 runtime 并存，并通过兼容入口逐步接线
- 稳定前不替代 `TASK.md` 的人工契约作用

## 推荐流程

1. 开发者 / 主 CLI 完成任务拆分
2. 更新 `TASK.md`，必要时初始化 `TASK-REPORT.md`
3. 运行 `maestro_collab suggest` 获取 owner 建议
4. 主 CLI 决定当前任务走哪条协作路径：
   - SQLite 基线路径
   - Mongo 协作控制面路径
5. 若走 SQLite 基线路径：
   - 将 issue 放入本地 tracker 活跃状态
   - 启动 Symphony
6. 若走 Mongo 协作控制面路径：
   - 由主 CLI 创建/分发 Mongo `work_item`
   - worker 通过 `coordctl` / 兼容入口读取任务并上报更新
   - 必要时导出 `TASK-REPORT.md` 摘要
7. Runtime / Control Plane 自动执行后续流程：
   - 创建 / 复用 workspace
   - 启动 worker session
   - 持续监控 session 状态
8. Worker 在执行中更新协作状态；若当前任务仍依赖 Markdown，则同步更新 `TASK-REPORT.md`
9. 主 CLI 查看：
   - `TASK-REPORT.md`
   - Symphony / collab 状态 API
   - Git / PR / 提交证据
10. 主 CLI 决定是否收尾、重派、回滚，或推进到 `verified / merged`

## 为什么不让 Symphony 直接写 TASK.md

- `TASK.md` 是任务契约，不只是运行指令
- 它包含边界、owner、验收标准、协作语义
- 这些内容更适合由开发者与主 CLI 共同确定
- Symphony 更适合做契约之后的“自动化流水线”

## 当前最小落地能力

当前建议至少做到：

- 默认使用 SQLite tracker
- `WORKFLOW.md` 明确 worker 必须读取 `TASK.md` / `TASK-REPORT.md`
- 状态 API 能看见运行态与 heartbeat/stale 信息
- workspace hooks 能拿到 repo/workspace/issue 上下文

补充：

- Mongo 协作控制面当前属于增强能力，不改变上述本地优先基线
- 新任务可逐步切到 Mongo 主事实源，但在途任务允许按兼容策略收尾

## 命名与三层架构

为了后续把这套系统和多 CLI 协作管理核心一起迁移出去，推荐采用以下命名策略：

- **长期家族名**：`Maestro`
- **当前仓库兼容名**：`Symphony`
- **策略**：保留 `symphony` 现有实现路径，同时引入 `maestro` 作为未来独立 namespace

推荐的三层拆分如下：

1. **`maestro.kernel`**
   - 通用 orchestration runtime
   - tracker 装配与 agent 执行
   - 状态 API 与运行时装配
2. **`maestro.collab`**
   - 多 CLI 协作管理核心
   - assignment / workspace(worktree) registry / heartbeat(stale) 持久化
   - workspace / worktree / owner / task contract 自动化
   - MongoDB 协作控制面扩展
3. **`maestro.profiles.mystocks`**
   - MyStocks 专属协作规则、prompt、默认工作流和绑定策略

这意味着未来真正独立出去时：

- `kernel` + `collab` 可以抽到独立工具仓库
- `profiles.mystocks` 可以保留在 MyStocks，或作为单独 profile 包存在

## 当前第二层已落地内容

目前 `maestro.collab` 已经具备第一版机器态协作核心：

- issue assignment 持久化
- workspace / worktree registry 持久化
- worker heartbeat / stale 视图持久化

这些状态与 `TASK.md` / `TASK-REPORT.md` 分离，专门服务自动化执行层与后续独立迁移。  
下一阶段，`maestro.collab` 将继续向 Mongo 协作控制面演进，但该演进仍以当前项目为第一落点。

## Owner-Aware Dispatch

第二层继续向前后，现在运行时已经支持 owner-aware dispatch：

- 若 runtime 配置了 `cli_name`，则只会处理分配给自己的 issue
- 若 issue assignment 处于 `stale` 且启用了 `reclaim_stale_assignments`，则当前 runtime 可以回收执行
- 若没有 assignment，则仍保持本地默认的可调度行为

这样一来，`main CLI` 的 owner 决策不再只是记录在文档里，而会真正进入自动化运行时约束。

## Main CLI Operator Surfaces

为配合 `main CLI` 的分配职责，新增以下本地操作入口：

- CLI：`scripts/runtime/maestro_collab.py`
  - `suggest`
  - `assign`
  - `state`
  - `list-workspaces`
  - `list-stale`
- Status API：
  - `GET /api/v1/collab/issues/{issue_identifier}`
  - `GET /api/v1/collab/workspaces`
  - `GET /api/v1/collab/stale`

这组入口用于维护和观察机器态协作事实，而不是替代 `TASK.md` / `TASK-REPORT.md`。  
其中 `suggest` 只根据 `.FILE_OWNERSHIP`、显式路径和 `TASK.md` 路径线索给出建议 owner，不会自动写入 assignment。  
未来 Mongo 协作控制面稳定后，`coordctl` 可作为这组 operator surface 的兼容扩展入口。

## Main CLI 分发前检查命令

建议主 CLI 在“写好 `TASK.md` 初稿，但尚未正式 assign”时，固定执行一次：

```bash
python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md
```

如果 `TASK.md` 里的路径线索还不够，可以临时补充显式路径：

```bash
python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md \
  --path web/frontend/src/components/Charts/KLine.vue \
  --path tests/unit/services/symphony/test_status_api.py
```

主 CLI 推荐按下面顺序操作：

1. 起草/更新 `TASK.md`
2. 运行 `suggest` 查看建议 owner 与原因
3. 人工决定最终 owner / worker CLI
4. 在 `TASK.md` 中写清 owner、边界、验收
5. 使用 `assign` 把机器态 assignment 持久化

对应命令：

```bash
python scripts/runtime/maestro_collab.py assign MT-1 \
  --worker-cli cli-6 \
  --assigned-by main \
  --acceptance-summary "补充 owner suggestion 接入主CLI手册与模板"
```

这样形成的链路是：

- `suggest`：辅助判断
- `TASK.md`：人工契约
- `assign`：机器态事实

## `TASK.md` 推荐最小模板

主 CLI 在完成 owner 判断后，建议把下面这段直接写进 `TASK.md`：

```markdown
## Owner 建议检查
- Suggested Owner: `<cli-x / main>`
- Suggest Reasons: `<命中规则 / 路径线索 / fallback原因>`

## 最终 Owner 决策
- Final Owner: `<cli-x / main>`
- Worker CLI: `<cli-x / main>`
- Decision Basis: `<路径命中 / 模块边界 / 依赖判断>`

## Assign 记录
- Issue Identifier: `<MT-1 / LOCAL-1 / ...>`
- Assigned By: `main`
- Acceptance Summary: `<一句话验收口径>`
- Assigned At: `<YYYY-MM-DD HH:MM TZ>`
```

如果任务很小，也可以压缩成：

```markdown
- Suggested Owner: `<cli-x / main>`
- Final Owner / Worker: `<cli-x>`
- Assign Record: `<ISSUE-ID> | main | <验收摘要>`
```

## 后续可增强方向

- owner CLI 定向分发
- worktree 注册与自动回收
- stale worker 自动提醒
- assignment / heartbeat 持久化
- 主 CLI 一键重派
- Mongo 协作控制面接管主分发 / 审批 / 汇总
