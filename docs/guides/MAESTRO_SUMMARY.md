# Maestro 总结文档

## 一句话定义

`Maestro` 是 MyStocks 当前这套“本地优先、多 CLI 协作、SQLite tracker 驱动”的自动化运行时家族名。

在仓库内部，历史实现名仍然是 `Symphony`；但从长期演进、可迁移和可独立抽取的角度看，推荐把它理解为：

- `Symphony`：当前仓库中的兼容实现名
- `Maestro`：未来可独立出去的产品/运行时家族名

## 为什么要有 Maestro

这套系统解决的不是“如何再造一个 issue tracker”，而是：

1. 如何在**本地优先**前提下运行多 CLI / 多 worker 协作
2. 如何把**人工任务契约**与**机器执行状态**分开
3. 如何在不依赖 Linear 的情况下，保留 assignment、workspace、heartbeat、stale、owner-aware dispatch 这些自动化能力
4. 如何给未来的“独立工具化”保留一条清晰迁移路径

因此，Maestro 的目标不是替代人，也不是替代 `TASK.md`，而是接管契约形成之后那些重复、机械、流程化的动作。

## 核心理念

### 1. 本地优先

- 默认 tracker 为 SQLite
- 默认 workspace 为本地目录
- 默认协作事实写入本地 `.symphony/tracker.db`
- 即使未来接 PostgreSQL 或远程系统，也不改变“本地先可跑”的基线

### 2. 人工契约优先

以下内容由人和 `main CLI` 决定：

- 目标与方向
- 总任务与边界
- owner / worker CLI
- 验收标准
- `TASK.md`
- `TASK-REPORT.md`

Maestro 不直接替人写任务契约；它只消费这些契约并执行自动化流程。

### 3. 机器态与文档态分离

文档态：

- `TASK.md`
- `TASK-REPORT.md`

机器态：

- issue assignment
- workspace / worktree registry
- worker heartbeat
- stale 视图
- owner suggestion 输出

这样做的好处是：人类可读的协作语义不被运行时污染，运行时也不需要去“猜”任务定义。

## 三层架构

### `maestro.kernel`

职责：

- orchestration runtime
- tracker 装配
- agent 执行
- 状态 API
- workflow 装载与运行时配置

当前主要复用 `src/services/symphony` 里的实现。

### `maestro.collab`

职责：

- 多 CLI 协作管理核心
- assignment 持久化
- workspace/worktree registry 持久化
- heartbeat / stale 持久化
- owner-aware dispatch gating
- stale reclaim
- `.FILE_OWNERSHIP` + `TASK.md` 驱动的 advisory owner suggestion

这是未来最值得独立抽出的“协作内核”。

### `maestro.profiles`

职责：

- 项目级 profile
- repo-specific prompt / policy / workflow binding
- 默认配置与协作约束

当前仓库的落地点是 `maestro.profiles.mystocks`。

## 责任模型

### 人

- 定义目标、方向、总任务和高层约束

### `main CLI`

- 拆解任务
- 决定 owner / worker CLI
- 写 `TASK.md`
- 审 `TASK-REPORT.md`
- 做分发、回收、重派、合并决策

### `worker CLI`

- 按 `TASK.md` 执行
- 在 owner 边界内修改
- 更新 `TASK-REPORT.md`
- 提供验证证据

### Maestro Runtime

- 轮询 tracker
- 拉起/复用 workspace
- 启动执行会话
- 记录 assignment / heartbeat / stale
- 暴露状态 API
- 在配置允许时执行 owner-aware dispatch / stale reclaim

## 当前已经落地的能力

### 1. 本地 SQLite tracker

支持：

- 创建本地 issue
- 列出 issue
- 更新 issue 状态

对应入口：

- `scripts/runtime/local_tracker.py`

### 2. 协作状态注册表

支持持久化：

- issue assignment
- workspace / worktree registry
- worker heartbeat
- stale 视图

对应入口：

- `src/services/maestro/collab/registry.py`
- `scripts/runtime/maestro_collab.py`

### 3. owner-aware dispatch

支持：

- runtime 仅消费分配给自己 `cli_name` 的 issue
- stale reclaim（配置开启时）
- assignment 约束真正进入自动化运行时

### 4. advisory owner suggestion

支持：

- 解析 `.FILE_OWNERSHIP`
- 从 `TASK.md` 中提取路径线索
- 基于路径命中给出建议 owner
- 对未知路径默认回退 `main`
- 多 owner 并列时保守回退 `main`

注意：

- `suggest` 是建议，不是自动分配
- 真正生效的分配，仍以 `TASK.md` + `assign` 为准

### 5. 状态 API

当前可观察：

- 运行态
- 单 issue 视图
- collab issue 视图
- workspace 列表
- stale heartbeat 列表

## 操作面

### 任务定义面

- `TASK.md`
- `TASK-REPORT.md`
- `.FILE_OWNERSHIP`
- `WORKFLOW.md`

### 运行时入口

- `scripts/runtime/run_symphony.py`

### tracker 入口

- `scripts/runtime/local_tracker.py`

### collab 入口

- `scripts/runtime/maestro_collab.py`

支持子命令：

- `suggest`
- `assign`
- `state`
- `list-workspaces`
- `list-stale`

## 推荐工作流

1. 人与 `main CLI` 确定目标与约束
2. `main CLI` 起草 `TASK.md`
3. 运行 `suggest` 获取 owner 建议
4. `main CLI` 决定最终 owner / worker
5. 在 `TASK.md` 中写入 owner、边界、验收
6. 创建本地 issue
7. 执行 `assign`
8. 把 issue 置为 `In Progress`
9. 启动 runtime
10. worker 执行并更新 `TASK-REPORT.md`
11. `main CLI` 根据状态 API、`TASK-REPORT.md` 和 Git 证据收尾

## 为什么它现在适合 MyStocks

因为 MyStocks 当前更偏：

- 个人/本地开发
- 多 CLI 协作而非多人远程项目管理
- 需要低依赖、低耦合
- 希望未来能迁移、抽离，而不是被某个第三方平台卡住

Maestro 在这种场景下的价值是：

- 把本地多 CLI 协作的“自动化层”稳定下来
- 保留未来升级到 PostgreSQL / 远程服务的空间
- 先把最关键的协作事实跑通，而不是一开始就绑定外部 SaaS

## 当前边界

Maestro 现在还**不是**：

- 通用远程项目管理平台
- 自动拆任务系统
- 自动写 `TASK.md` / `TASK-REPORT.md` 的系统
- 完整的可视化调度台

它当前更像一个：

- 本地优先协作运行时
- 多 CLI 协作状态内核
- 将来可独立抽离的 automation backbone

## 建议的长期演进方向

1. 抽离 `kernel` + `collab` 为独立工具仓库
2. 把 `profiles.mystocks` 继续留在业务仓库
3. 为 `assign/suggest/state` 增加更好的 operator UI
4. 在保留 SQLite 基线的同时，补 PostgreSQL 后端
5. 为多 CLI 心跳、阻塞、回收建立更完整的观测面

## 关键文件索引

- `src/services/maestro/README.md`
- `src/services/maestro/collab/__init__.py`
- `src/services/maestro/collab/registry.py`
- `src/services/maestro/collab/ownership.py`
- `src/services/maestro/collab/suggester.py`
- `src/services/maestro/profiles/mystocks.py`
- `src/services/symphony/service.py`
- `scripts/runtime/run_symphony.py`
- `scripts/runtime/local_tracker.py`
- `scripts/runtime/maestro_collab.py`
- `docs/guides/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
- `WORKFLOW.md`
