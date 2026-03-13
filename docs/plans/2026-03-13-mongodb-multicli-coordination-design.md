# MongoDB Multi-CLI Coordination Design

> **日期**: 2026-03-13
> **状态**: 已批准
> **适用范围**: 本项目 `mystocks_spec` 及其 worktree

---

## Context

当前项目已经采用 Git worktree + 多 CLI 协作模式，但任务分派和反馈主要依赖 `TASK.md`、`TASK-REPORT.md` 与 `.multi-cli-tasks/` 目录同步。随着分支数量增加，这种方式在删除 worktree、任务调整、主 CLI 汇总和跨 worker 协调时会引入额外同步成本。

用户希望将任务分派、进展反馈、正式变更请求和主 CLI 汇总统一到 MongoDB 中，以便实现：

- 单次写入，实时可见
- 分支删除后状态不丢失
- 主 CLI 可随时查看所有 worker 的进展
- worker 对任务定义有异议时走统一审批通道

本设计只服务当前项目及其 worktree，不在第一阶段抽象为跨项目通用系统。

## Goals

- 为本项目提供 MongoDB 主事实源的多 CLI 协作系统
- 主 CLI 统一查看所有 worker 的状态摘要和待审批请求
- worker 只能在自身作用域内读写
- worker 无法直接修改主 CLI 下发的任务定义
- worker 对任务定义的修改需求通过正式 request 通道提交
- 第一阶段通过 CLI 完成完整协作闭环

## Non-Goals

- 本次不做 Web UI
- 本次不做多项目支持
- 本次不做多用户账号体系
- 本次不做数据库原生细粒度 ACL
- 本次不把系统独立成通用产品

## Recommended Approach

采用“**MongoDB 主事实源 + CLI-first + 应用层权限控制**”方案：

- MongoDB 保存任务主记录、进展更新、正式请求、事件日志和汇总视图
- 主 CLI 和 worker CLI 统一通过本地 CLI 工具 `coordctl` 读写
- worker 不能直接自由查询或修改主记录
- `.multi-cli-tasks/` 从长期真相源降级为模板区、导出区和历史快照区

相比“继续以 Markdown 为主”的方式，这个方案更适合当前项目逐步扩大的 worktree 数量和多 CLI 协调需求。

## Architecture

### 1. Data Model

第一阶段使用以下集合：

- `work_items`
- `work_updates`
- `work_requests`
- `work_events`
- `worker_status_views`

说明：

- `work_items` 是任务主记录，对应当前 `TASK.md` 的核心字段
- `work_updates` 是 worker 的执行进展，对应当前 `TASK-REPORT.md`
- `work_requests` 是正式变更请求，不允许 worker 直接改任务主记录
- `work_events` 是轻量事件日志，用于审计和时间线回放
- `worker_status_views` 是主 CLI 的快速摘要读模型

### 2. Access Model

#### Main CLI

- 可读全部集合
- 可写 `work_items`
- 可审批 `work_requests`
- 可维护 `worker_status_views`
- 可将任务状态推进到 `verified`

#### Worker CLI

- 只能读取自己作用域内的 `work_items`
- 只能追加写入自己的 `work_updates`
- 只能创建自己的 `work_requests`
- 不能直接修改 `work_items`
- 不能访问其他 worker 的原始更新和请求

#### Cross-Worker Visibility

- worker 默认不读取其他 worker 的原始记录
- 如需跨 worker 可见性，只通过 `worker_status_views` 提供摘要信息

### 3. CLI-First Interaction

第一阶段所有读写都通过 `coordctl` 完成，避免让 worker 直接自由查询 MongoDB。

主 CLI 命令：

- `coordctl work create`
- `coordctl work dispatch`
- `coordctl work list`
- `coordctl work show`
- `coordctl request review`

worker CLI 命令：

- `coordctl work show`
- `coordctl work mark`
- `coordctl update add`
- `coordctl request create`

### 4. State Flow

第一阶段状态流转仅保留：

- `created`
- `dispatched`
- `in_progress`
- `blocked`
- `ready_for_review`
- `verified`

第二阶段再扩展：

- `merged`
- `archived`

### 5. Storage Boundary

代码建议放置在：

- `src/services/multicli_coord/**`
- `scripts/coord/coordctl.py`
- `config/multicli-coord/**`
- `tests/unit/services/multicli_coord/**`
- `tests/integration/services/multicli_coord/**`

MongoDB 数据库建议命名：

- `mystocks_coord`

## MVP

第一阶段最小可交付范围：

1. 主 CLI 创建任务
2. 主 CLI 下发任务
3. worker 拉取自己的任务
4. worker 上报进展
5. worker 发起正式变更请求
6. 主 CLI 查看全局汇总并审批请求

第一阶段不做：

- Web UI
- `work_feedback`
- 多项目支持
- Markdown 自动双写
- Git 自动联动

## Phase 2 Expansion

第二阶段按以下顺序扩展：

### Phase 2A

- 新增 `work_feedback`
- 增加 `merged` / `archived`
- 提供 Markdown 导出快照
- 完善最终验证记录

### Phase 2B

- 补充主 CLI 汇总、日报、阻塞聚合和风险排行

### Phase 2C

- 增加 Git / worktree 弱联动（只读型）

### Phase 2D

- 增加 `.multi-cli-tasks/` 和 `reports/governance/` 导出能力

### Phase 2E

- 仅在本项目内稳定后，再考虑独立为通用系统

## Risks / Trade-offs

### Risk 1: 协作复杂度上升

- 引入 MongoDB 和 CLI 子系统会增加新的维护对象
- 缓解方式：第一阶段严格控制范围，只做 5 个集合和最小命令集

### Risk 2: 权限边界不严导致串台

- 如果 worker 能直接改任务定义，系统会失去主 CLI 调度权
- 缓解方式：`work_items` 只允许主 CLI 修改，worker 只能通过 `work_requests`

### Risk 3: 过早平台化

- 过早抽象会导致当前项目迟迟得不到可用系统
- 缓解方式：只服务本项目，不先做多项目和 Web UI

## Acceptance Criteria

- 主 CLI 能创建并下发任务
- worker 只能读取自己的任务主记录
- worker 能追加写入自己的执行更新
- worker 对任务定义的异议只能通过 `work_requests`
- 主 CLI 能查看所有活跃 worker 的摘要视图
- 主 CLI 能审批 request 并更新任务主记录
- 分支删除后任务状态仍可从 MongoDB 恢复
