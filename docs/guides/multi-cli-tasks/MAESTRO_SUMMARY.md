# Maestro 总结文档

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录或工作日志，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论和处理结果如未重新复核，应视为历史快照，不得直接当作当前事实。


## 一句话定义

`Maestro` 是 MyStocks 当前这套“本地优先、多 CLI 协作、可演进协作控制面”的自动化运行时家族名。

在仓库内部，历史实现名仍然是 `Symphony`；但从长期演进、可迁移和可独立抽取的角度看，推荐把它理解为：

- `Symphony`：当前仓库中的兼容实现名
- `Maestro`：未来可独立出去的产品/运行时家族名

## 为什么要有 Maestro

这套系统解决的不是“如何再造一个 issue tracker”，而是：

1. 如何在**本地优先**前提下运行多 CLI / 多 worker 协作
2. 如何把**人工任务契约**与**机器执行状态**分开
3. 如何在不依赖 Linear 的情况下，保留 assignment、workspace、heartbeat、stale、owner-aware dispatch 这些自动化能力
4. 如何给未来的“独立工具化”保留一条清晰迁移路径

因此，Maestro 的目标不是替代人，而是把 active task truth 收敛到协作控制面，再把 `TASK.md` / `TASK-REPORT.md` 降级为导出快照与可读审阅面。

## 核心理念

### 1. 本地优先

- 默认 tracker 为 SQLite
- 默认 workspace 为本地目录
- 默认协作事实写入本地 `.symphony/tracker.db`
- 即使未来接 PostgreSQL、MongoDB 或远程服务，也不改变“本地先可跑”的基线

### 2. 人工契约优先

以下内容由人和 `main CLI` 决定：

- 目标与方向
- 总任务与边界
- owner / worker CLI
- 验收标准
- 任务契约内容本身
- 是否导出 `TASK.md` / `TASK-REPORT.md` 快照

Maestro 不直接替人写任务契约；它只消费这些契约并执行自动化流程。

### 3. 机器态与文档态分离

文档态（导出/审阅面）：

- `TASK.md`
- `TASK-REPORT.md`

机器态：

- issue assignment
- workspace / worktree registry
- worker heartbeat
- stale 视图
- owner suggestion 输出

这样做的好处是：人类可读的协作语义不被运行时污染，运行时也不需要去“猜”任务定义。

### 4. 渐进式协作控制面

- 当前已落地基线是 SQLite tracker + SQLite collaboration registry
- MongoDB Multi-CLI Coordination 应视为 `Maestro` 的下一代协作控制面
- 在 MyStocks 内先完成验证，再决定是否独立拆出
- 新控制面是 `maestro.collab` 的演进，不是当前阶段的平行新系统

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
- 面向未来的 MongoDB 协作控制面扩展

这是未来最值得独立抽出的“协作内核”。

当前阶段补充说明：

- SQLite 仍是当前已落地的本地基线
- MongoDB 协作控制面在本项目内归属 `maestro.collab` 演进线
- 若未来独立拆分，优先迁出的也是 `kernel + collab`

### `maestro.profiles`

职责：

- 项目级 profile
- repo-specific prompt / policy / workflow binding
- 默认配置与协作约束
- 控制当前项目对协作后端、切换窗口和导出策略的选择

当前仓库的落地点是 `maestro.profiles.mystocks`。

## 责任模型

### 人

- 定义目标、方向、总任务和高层约束

### `main CLI`

- 拆解任务
- 决定 owner / worker CLI
- 定义任务契约
- 导出 `TASK.md` / `TASK-REPORT.md`
- 审 `TASK-REPORT.md`
- 做分发、回收、重派、合并决策

### `worker CLI`

- 按导出的 `TASK.md` 快照执行
- 在 owner 边界内修改
- 更新 Mongo 协作状态，并在需要时补充 `TASK-REPORT.md`
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

## 正在演进的能力

### MongoDB Multi-CLI Coordination

定位：

- `Maestro` 体系下的下一代协作控制面
- 当前阶段先服务 MyStocks
- 目标是补齐“主 CLI 分发 -> worker 上报 -> request 审批 -> 跨 worker 汇总”链路

边界：

- 不重写 `maestro.kernel`
- 不立即独立成通用产品
- 不在当前阶段与 `maestro.collab` 平行建第二套长期体系

### Repo-Local Acceptance

当前推荐的本机收口命令：

```bash
bash scripts/runtime/run_local_maestro_acceptance.sh
```

该命令会串行执行：

- `coordctl work list`
- Mongo smoke
- Graphiti preflight smoke
- collab snapshot export

最新一次实跑收口记录见：

- `docs/reports/tasks/2026-04-03-maestro-local-acceptance-report.md`

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

未来扩展：

- `coordctl` 可作为面向 Mongo 控制面的兼容操作入口

## 推荐工作流

1. 人与 `main CLI` 确定目标与约束
2. `main CLI` 起草任务契约
3. 运行 `suggest` 获取 owner 建议
4. `main CLI` 决定最终 owner / worker
5. 在控制面中写入 owner、边界、验收，并按需导出 `TASK.md`
6. 创建本地 issue
7. 执行 `assign`
8. 把 issue 置为 `In Progress`
9. 启动 runtime
10. worker 执行并更新 Mongo 协作状态，必要时补充 `TASK-REPORT.md`
11. `main CLI` 根据状态 API、导出的 `TASK-REPORT.md` 和 Git 证据收尾

Mongo 协作控制面成熟后，步骤 6-11 将逐步迁移到新的协作主事实源，`TASK.md` 保留为导出快照而不是人工主契约。

## 为什么它现在适合 MyStocks

因为 MyStocks 当前更偏：

- 个人/本地开发
- 多 CLI 协作而非多人远程项目管理
- 需要低依赖、低耦合
- 希望未来能迁移、抽离，而不是被某个第三方平台卡住

Maestro 在这种场景下的价值是：

- 把本地多 CLI 协作的“自动化层”稳定下来
- 保留未来升级到 MongoDB / PostgreSQL / 远程服务的空间
- 先把最关键的协作事实跑通，而不是一开始就绑定外部 SaaS

## 当前边界

Maestro 现在还**不是**：

- 通用远程项目管理平台
- 自动拆任务系统
- 自动定义任务契约的系统
- 完整的可视化调度台

它当前更像一个：

- 本地优先协作运行时
- 多 CLI 协作状态内核
- 将来可独立抽离的 automation backbone

补充边界：

- MongoDB 协作线目前仍属于 `Maestro` 体系内部演进
- 本期目标是增强 MyStocks 的多 CLI 协作控制面，不是立即孵化平行产品
- 只有在 Mongo 协作链路在本项目内稳定后，才进入独立化评估

## 建议的长期演进方向

1. 抽离 `kernel` + `collab` 为独立工具仓库
2. 把 `profiles.mystocks` 继续留在业务仓库
3. 为 `assign/suggest/state` 增加更好的 operator UI
4. 在保留 SQLite 基线的同时，补 MongoDB 协作控制面
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
- `docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
- `docs/plans/2026-03-13-mongodb-multicli-coordination-design.md`
- `docs/plans/2026-03-13-mongodb-multicli-coordination-implementation-plan.md`
- `WORKFLOW.md`
