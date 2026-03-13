# MongoDB Multi-CLI Coordination Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在本项目内部实现 MongoDB 主事实源的多 CLI 协作 MVP，用于替代当前以 `TASK.md / TASK-REPORT.md` 为主的长期协作真相源。

**Architecture:** 使用 `mystocks_coord` 作为项目级协作数据库，落地 `work_items`、`work_updates`、`work_requests`、`work_events` 和 `worker_status_views` 五个集合，通过 `coordctl` CLI 提供主 CLI 与 worker CLI 的统一访问入口，并在服务层实现严格作用域控制。

**Tech Stack:** Python, MongoDB, Pydantic, CLI tooling, unit/integration tests

---

### Task 1: 定义 Mongo 数据模型与集合索引

**Files:**
- Create: `src/services/multicli_coord/models/*.py`
- Create: `src/services/multicli_coord/mongo/indexes.py`

**Step 1: 定义 `work_items` 模型**

字段包含：
- `work_item_id`
- `title`
- `objective`
- `branch`
- `worktree_path`
- `owner_cli`
- `status`
- `allowed_paths`
- `forbidden_paths`
- `acceptance_checks`
- `openspec`

**Step 2: 定义 `work_updates` / `work_requests` / `work_events` / `worker_status_views` 模型**

**Step 3: 定义索引**

- `work_items.work_item_id` 唯一索引
- `work_items.branch` 唯一索引
- `work_updates.work_item_id + update_seq`
- `work_requests.work_item_id + status`
- `worker_status_views.branch`

### Task 2: 实现 repository 层

**Files:**
- Create: `src/services/multicli_coord/repositories/*.py`

**Step 1: 编写 `work_items_repo.py`**

支持：
- create
- get_by_work_item_id
- get_by_branch
- update_status
- update_definition

**Step 2: 编写 `work_updates_repo.py`**

支持：
- append_update
- list_updates
- get_latest_update

**Step 3: 编写 `work_requests_repo.py`、`work_events_repo.py`、`worker_status_views_repo.py`**

### Task 3: 实现权限与作用域控制

**Files:**
- Create: `src/services/multicli_coord/authz/*.py`
- Create: `src/services/multicli_coord/services/*.py`

**Step 1: 定义主 CLI / worker CLI 权限矩阵**

**Step 2: 实现 worker 作用域校验**

- worker 只能读取自己的 `work_item`
- worker 只能追加自己的 `work_updates`
- worker 只能创建自己的 `work_requests`

**Step 3: 实现状态流转规则**

允许：
- `created -> dispatched`
- `dispatched -> in_progress`
- `in_progress -> blocked`
- `in_progress -> ready_for_review`
- `ready_for_review -> verified`

### Task 4: 实现 `coordctl` 最小命令集

**Files:**
- Create: `scripts/coord/coordctl.py`

**Step 1: 主 CLI 命令**

- `work create`
- `work dispatch`
- `work list`
- `work show`
- `request review`

**Step 2: worker CLI 命令**

- `work show`
- `work mark`
- `update add`
- `request create`

**Step 3: CLI 输出统一**

- 支持 `text`
- 支持 `json`

### Task 5: 实现汇总视图

**Files:**
- Modify: `src/services/multicli_coord/services/*.py`

**Step 1: 设计 `worker_status_views` 更新逻辑**

**Step 2: 当 update/request/status 变化时刷新摘要**

主 CLI 需要能快速看到：
- 当前状态
- 最近一次更新
- 当前 blocker
- 是否有待审批 request

### Task 6: 测试 MVP

**Files:**
- Create: `tests/unit/services/multicli_coord/**`
- Create: `tests/integration/services/multicli_coord/**`

**Step 1: 单测**

- 任务创建
- 状态流转
- worker 作用域隔离
- request 创建与审批

**Step 2: 集成测试**

- 主 CLI 创建任务
- worker 拉取任务
- worker 更新进展
- worker 发起 request
- 主 CLI 审批 request
- 汇总视图更新

### Task 7: 文档与迁移说明

**Files:**
- Create: `docs/guides/MONGO_MULTICLI_COORDINATION_GUIDE.md`
- Modify: `.multi-cli-tasks/guides/*.md`（如需引用）

**Step 1: 编写使用说明**

- 如何初始化 MongoDB
- 如何使用 `coordctl`
- 主 CLI 与 worker CLI 的职责

**Step 2: 编写迁移说明**

- 当前 `TASK.md / TASK-REPORT.md` 如何过渡到 MongoDB 主事实源
- `.multi-cli-tasks/` 如何从真相源降级为模板与导出区
