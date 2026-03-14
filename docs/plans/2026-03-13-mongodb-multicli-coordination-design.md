# MongoDB Multi-CLI Coordination Design

> **日期**: 2026-03-13
> **状态**: 已批准（范围修订版）
> **适用范围**: 本项目 `mystocks_spec` 及其 worktree
> **阶段定位**: 本项目内落地期（暂不独立成通用产品）

---

## Context

当前项目已经采用 Git worktree + 多 CLI 协作模式，并已有 `Maestro/Symphony` 本地协作内核。  
截至 `2026-03-13`，主线存在“部分分支已并入、部分分支仍在开发”的并行状态：

- `dev-data-db-audit-claude` 已并入 `main`
- `dev-artdeco-pages-codex` 已并入 `main`
- `dev-api-availability-gemini` 仍在开发

在这种状态下，单靠 `TASK.md`、`TASK-REPORT.md` 与 `.multi-cli-tasks/` 的目录同步，存在以下问题：

- 主 CLI 无法实时掌握全部 worker 状态
- worktree 删除后，任务过程态难以完整留存
- request/审批/回放链路分散在多个文件
- 难以积累“未来可独立化的协作控制面”经验

本方案目标不是这一期就独立项目，而是先在 MyStocks 内把 MongoDB 协作链路跑通、边界跑清楚。

## Architecture Principle

`MongoDB Multi-CLI Coordination` 应被视为 `Maestro` 体系下的下一代协作控制面：

- 当前阶段归属 `maestro.collab` 演进线
- 当前阶段继续受 `maestro.profiles.mystocks` 的项目边界约束
- 当前阶段不作为平行于 `Maestro` 的独立新系统存在
- 仅在本项目内验证稳定后，再评估是否迁出为独立运行/管理系统

## Goals

- 在本项目内落地 MongoDB 协作控制面，优先覆盖“任务分发 -> 进展上报 -> request 审批 -> 汇总回看”
- 让主 CLI 能统一查看 worker 状态和待审批请求
- 让 worker 只能在自身作用域提交更新，不可直接改主任务定义
- 为后续独立化预留边界，但本期不做独立仓库拆分
- 与 `MAESTRO_SUMMARY` 的三层结构对齐，避免平行新体系

## Non-Goals

- 本次不做 Web UI
- 本次不做多项目支持
- 本次不做多用户组织模型
- 本次不把系统独立成通用产品
- 本次不重写 `maestro.kernel` 主运行时

## Boundary Decision (与 MAESTRO 对齐)

遵循 `docs/guides/MAESTRO_SUMMARY.md` 的边界，本方案采用“本项目优先、层内扩展”：

1. `maestro.kernel`
- 保持现有 orchestration 主流程不变
- 继续承担 worker 运行、状态 API、workspace 生命周期

2. `maestro.collab`
- 在现有 collab 核心上新增 MongoDB 协作存储能力
- 不新起平行 runtime，不绕开现有 `maestro_collab` 操作面

3. `maestro.profiles.mystocks`
- 维护本项目的切换窗口、策略开关、默认后端和导出策略
- 本项目特有规则放在 profile，不固化到通用协作内核

## Recommended Approach

采用“**Maestro vNext 协作控制面 + MongoDB 主事实源 + 分阶段切换**”：

- MongoDB 保存任务主记录、进展更新、正式请求、事件日志和汇总读模型
- 主 CLI 与 worker CLI 通过 `coordctl`（可作为 `maestro_collab` 的兼容入口）统一操作
- worker 不直接自由查询 MongoDB 明细集合
- `TASK.md` / `TASK-REPORT.md` 在切换后转为“入口说明 + 导出快照 + 人工审阅载体”，不再承担过程态主写入

## Architecture

### 1. Data Model

第一阶段使用以下集合：

- `work_items`
- `work_updates`
- `work_requests`
- `work_events`
- `worker_status_views`

说明：

- `work_items`：主 CLI 定义的任务主记录
- `work_updates`：worker 追加式进展上报
- `work_requests`：worker 的正式变更请求，替代直接改主记录
- `work_events`：审计事件与时间线回放
- `worker_status_views`：主 CLI 快速摘要读模型

### 2. Access & Trust Model

#### Main CLI

- 可读全部集合
- 可写 `work_items`
- 可审批 `work_requests`
- 可维护 `worker_status_views`
- 可将任务推进到 `verified` / `merged`

#### Worker CLI

- 只能读取自身作用域内 `work_items`
- 只能追加自己的 `work_updates`
- 只能创建自己的 `work_requests`
- 不能直接修改 `work_items`
- 默认不可读取其他 worker 的原始更新/请求

#### Trust Baseline (Phase 1 必做)

- worker CLI 不直连 MongoDB 明细集合
- 所有写入经统一服务层进行作用域校验与审计
- 每次写操作都记录 `actor_cli`、`branch`、`work_item_id`、`timestamp`

### 3. CLI-First Interaction

第一阶段读写统一通过 `coordctl`，并与现有 `scripts/runtime/maestro_collab.py` 保持兼容映射。

主 CLI 命令：

- `coordctl work create`
- `coordctl work dispatch`
- `coordctl work list`
- `coordctl work show`
- `coordctl request review`
- `coordctl work transition --to merged`

worker CLI 命令：

- `coordctl work show`
- `coordctl work mark`
- `coordctl update add`
- `coordctl request create`

### 4. State Flow

第一阶段状态流转：

- `created`
- `dispatched`
- `in_progress`
- `blocked`
- `ready_for_review`
- `verified`
- `merged`

第二阶段再扩展：

- `archived`

### 5. Storage Boundary

本期代码边界建议对齐 `maestro` 结构：

- `src/services/maestro/collab/**`（新增 Mongo backend 与服务层）
- `scripts/runtime/maestro_collab.py`（扩展命令面）
- `scripts/runtime/coordctl.py`（可选兼容包装）
- `config/maestro/collab/**`
- `tests/unit/services/maestro/collab/**`
- `tests/integration/services/maestro/collab/**`

MongoDB 数据库建议命名：

- `mystocks_coord`

## Cutover Strategy (本期重点补齐)

### Cutover Window

- `2026-03-13` 起，新建任务默认进入 MongoDB 协作流
- 已在途任务（如 `dev-api-availability-gemini`）允许按旧流程收尾，再做一次性归档导入

### Compatibility Rule

- 过渡期允许“Mongo 主写 + Markdown 导出快照”
- `TASK.md` 保留任务入口、owner 决策与验收口径
- `TASK-REPORT.md` 由自动导出摘要为主，人工补充异常说明

### Rollback Rule

- 若 Mongo 协作链路出现阻塞，主 CLI 可临时回切到 Markdown 手工流程
- 回切必须写入 `work_events` 和 `TASK.md` 变更记录，保证审计完整

## MVP

第一阶段最小可交付范围：

1. 主 CLI 创建任务并分发
2. worker 拉取自己的任务并上报进展
3. worker 发起正式变更 request
4. 主 CLI 审批 request 并推进状态到 `verified` / `merged`
5. 主 CLI 查看跨 worker 摘要视图
6. 对在途任务完成一次性迁移收口（至少覆盖 `dev-api-availability-gemini`）

第一阶段不做：

- Web UI
- `work_feedback`
- 多项目支持
- 独立仓库拆分

## Phase 2 Expansion

第二阶段按以下顺序扩展：

### Phase 2A

- 新增 `work_feedback`
- 增加 `archived`
- 完善最终验证记录与日报导出

### Phase 2B

- 增加 Git / worktree 弱联动（只读）
- 自动识别已合并分支并提示推进状态

### Phase 2C

- 完成 `.multi-cli-tasks/` 与 `reports/governance/` 导出策略收敛
- 评估是否进入“跨项目独立化立项”

## Risks / Trade-offs

### Risk 1: 双轨期复杂度上升

- 过渡期存在 Mongo 与 Markdown 并行
- 缓解：明确 cutover 时间点、在途任务名单、统一导出策略

### Risk 2: 权限边界不严导致串台

- 仅靠 CLI 自觉无法保证隔离
- 缓解：统一服务层校验 + 操作审计事件 + 作用域强校验

### Risk 3: 过早平台化拖慢主线交付

- 如果本期直接追求独立化，交付会失焦
- 缓解：明确“先服务本项目，后评估独立化”的阶段目标

## Acceptance Criteria

- 主 CLI 能创建并分发任务
- worker 只能读取/写入自身作用域数据
- worker 对任务定义异议只能走 `work_requests`
- 主 CLI 能审批 request，并推进到 `verified` / `merged`
- 主 CLI 能查看所有活跃 worker 摘要
- 在途分支可按兼容策略完成收口，不丢失过程数据
- 分支删除后状态可从 MongoDB 恢复并回放
