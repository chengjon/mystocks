# MongoDB Multi-CLI Coordination Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在本项目内部落地 `Maestro` 下一代 MongoDB 协作控制面，先补齐“主 CLI 分发 -> worker 上报 -> request 审批 -> 状态汇总”链路，并与现有 `Maestro` 结构对齐。  
**Phase Scope:** 本期不独立拆仓；先服务 `mystocks_spec`，为后续独立化沉淀可迁移经验。  
**Architecture:** 本方案被定义为 `maestro.collab` 的下一代协作控制面演进，而不是平行新系统。在 `maestro.collab` 内增加 Mongo backend 与作用域服务层，保持现有 runtime 连续运行，通过 `coordctl`/`maestro_collab` 提供统一操作面。  
**Tech Stack:** Python, MongoDB, Pydantic, CLI tooling, unit/integration tests

---

## Implementation Status

- `Task 0`: 已完成
- `Task 1`: 已完成
- `Task 2`: 已完成
- `Task 3`: 已完成
- `Task 4`: 已完成
- `Task 5`: 基本完成
  - backend 选择、Mongo tracker、runtime -> control-plane 同步已完成
  - 更深的在途任务自动收口仍可后续补强
- `Task 6`: 已完成（最小迁移/导出版本）
- `Task 7`: 部分完成
  - unit / smoke / wiring 回归已完成
  - 更高层 integration / PM2 / Docker 级验证未完成
- `Task 8`: 已完成

### Task 0: 定义切换窗口与兼容策略（先做）

**Status:** `Completed`

**Files:**
- Modify: `docs/plans/2026-03-13-mongodb-multicli-coordination-design.md`
- Modify: `docs/guides/multi-cli-tasks/MAESTRO_SUMMARY.md`
- Modify: `docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`（补充过渡说明）
- Modify: `TASK.md`（记录 cutover 决策）

**Step 1: 固化架构原则**

- 明确 Mongo 协作线归属 `maestro.collab`
- 明确当前阶段仍由 `maestro.profiles.mystocks` 约束
- 明确“先项目内验证，后独立化评估”

**Step 2: 明确 cutover 时间点与在途任务名单**

- 新建任务默认走 Mongo 协作流
- 在途任务（至少 `dev-api-availability-gemini`）允许按兼容策略收尾

**Step 3: 明确导出与回滚规则**

- Mongo 主写、Markdown 快照导出
- 出现阻塞时可回切手工流程，必须留痕

### Task 1: 在 `maestro.collab` 中建立存储抽象与 Mongo backend

**Status:** `Completed`

**Files:**
- Create/Modify: `src/services/maestro/collab/store/*.py`
- Create/Modify: `src/services/maestro/collab/backends/mongo/*.py`
- Modify: `src/services/maestro/collab/registry.py`（保留 SQLite backend）

**Step 1: 定义协作存储抽象接口**

覆盖：
- `work_items`
- `work_updates`
- `work_requests`
- `work_events`
- `worker_status_views`

**Step 2: 实现 Mongo backend**

字段最小集：
- `work_item_id`
- `title`
- `objective`
- `branch`
- `owner_cli`
- `status`
- `allowed_paths`
- `forbidden_paths`
- `acceptance_checks`
- `openspec`

**Step 3: 索引与幂等策略**

- `work_items.work_item_id` 唯一索引
- `work_items` 对 `(branch, task_key)` 建立复合唯一，避免单 `branch` 唯一导致复用受限
- `work_updates` 使用幂等键（如 `update_id`）避免重试重复写入
- `work_requests` 对 `(work_item_id, request_id)` 建立唯一

### Task 2: 实现作用域校验与审计服务层

**Status:** `Completed`

**Files:**
- Create: `src/services/maestro/collab/authz/*.py`
- Create: `src/services/maestro/collab/services/*.py`

**Step 1: 定义主 CLI / worker CLI 权限矩阵**

**Step 2: 服务层强制作用域校验**

- worker 只能读取自己的 `work_item`
- worker 只能追加自己的 `work_updates`
- worker 只能创建自己的 `work_requests`
- worker 不能直接修改任务定义

**Step 3: 全量审计**

每次写操作记录：
- `actor_cli`
- `branch`
- `work_item_id`
- `action`
- `timestamp`

### Task 3: 实现统一命令面（`coordctl` + `maestro_collab` 对齐）

**Status:** `Completed`

**Files:**
- Modify: `scripts/runtime/maestro_collab.py`
- Create: `scripts/runtime/coordctl.py`（可选包装入口）

**Step 1: 主 CLI 命令**

- `work create`
- `work dispatch`
- `work list`
- `work show`
- `request review`
- `work transition --to verified|merged`

**Step 2: worker CLI 命令**

- `work show`
- `work mark`
- `update add`
- `request create`

**Step 3: 输出规范**

- 支持 `text`
- 支持 `json`
- 错误码与审计 ID 可追踪

### Task 4: 汇总读模型与状态面

**Status:** `Completed`

**Files:**
- Modify: `src/services/maestro/collab/services/*.py`
- Modify: `src/services/symphony/status_api.py`（如需接入摘要）

**Step 1: 设计 `worker_status_views` 刷新逻辑**

**Step 2: 在 update/request/status 变化时增量刷新摘要**

主 CLI 需快速看到：
- 当前状态
- 最近一次更新
- 当前 blocker
- 是否有待审批 request

### Task 5: Runtime 接线（不中断现有主线）

**Status:** `Mostly Completed`

**Files:**
- Modify: `src/services/symphony/orchestrator.py`
- Modify: `src/services/symphony/workspace_manager.py`
- Modify: `src/services/maestro/profiles/mystocks.py`

**Step 1: 让 runtime 可感知 Mongo 协作状态**

**Step 2: 保留兼容开关**

- 可配置 SQLite-only / Mongo-only / Dual-write（过渡期）

**Step 3: 在途任务收口保障**

- 不打断 `dev-api-availability-gemini` 现有开发
- 完成后补齐迁移导入与状态闭环

### Task 6: 迁移脚本与一次性导入

**Status:** `Completed (Minimal Version)`

**Files:**
- Create: `scripts/runtime/migrate_collab_to_mongo.py`
- Create: `scripts/runtime/export_collab_snapshots.py`

**Step 1: 导入历史协作状态**

- 从现有 SQLite 协作表导入 assignment/workspace/heartbeat

**Step 2: 导入 Markdown 关键信息（仅必要字段）**

- 从 `TASK.md` / `TASK-REPORT.md` 提取 task id、owner、验收摘要、最后进展

**Step 3: 迁移校验**

- 校验总数、状态分布、最近更新时间一致性

### Task 7: 测试与验收

**Status:** `Partially Completed`

**Files:**
- Create/Modify: `tests/unit/services/maestro/collab/**`
- Create/Modify: `tests/integration/services/maestro/collab/**`

**Step 1: 单测**

- 任务创建与分发
- 状态流转（含 `merged`）
- worker 作用域隔离
- request 创建与审批
- 审计日志完整性
- 幂等写入与并发冲突处理

**Step 2: 集成测试**

- 主 CLI 创建任务
- worker 拉取任务
- worker 更新进展
- worker 发起 request
- 主 CLI 审批 request 并推进到 `verified/merged`
- 汇总视图更新
- 在途任务迁移后可查询

### Task 8: 文档与运行手册

**Status:** `Completed`

**Files:**
- Create: `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
- Modify: `docs/guides/multi-cli-tasks/MAESTRO_SUMMARY.md`（补 Mongo 期边界）
- Modify: `docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`（补 cutover）

**Step 1: 编写操作手册**

- Mongo 初始化
- `coordctl` 使用方式
- 主 CLI 与 worker CLI 的职责边界

**Step 2: 编写迁移与回滚手册**

- 在途任务如何处理
- 出现故障如何回切
- 如何从 Mongo 导出 Markdown 快照供审阅

---

## Exit Criteria（本期完成标准）

- 新建任务可稳定走 Mongo 协作闭环
- 在途任务可不中断收口并导入 Mongo
- 主 CLI 可按 `verified -> merged` 完成任务生命周期管理
- worker 串台写入被服务层拒绝并可审计
- 仍可在必要时回切到 Markdown 手工流程
