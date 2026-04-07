# MongoDB Multi-CLI Coordination Progress Report

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


## Date

- 2026-03-14

## Scope Completed In This Iteration

### 1. Control Plane Foundation

- 新增 `maestro.collab` 的 Mongo control-plane 存储抽象
- 新增 `work_items / work_updates / work_requests / work_events / worker_status_views`
- 新增控制面服务层、作用域校验与审计事件

### 2. Runtime Registry Wiring

- 新增 `MongoCollaborationRegistry`
- 新增 `DualWriteCollaborationRegistry`
- `SymphonyService` 支持 `sqlite / mongo / dual-write` collab backend

### 3. Runtime Dispatch Source

- 新增 `MongoWorkItemTrackerClient`
- `tracker.kind == mongo` 时可直接从 Mongo `work_items` 调度

### 4. Runtime -> Control Plane Sync

- dispatch 时把任务推进到 `in_progress`
- runtime event 时同步 `latest_update`
- worker 正常退出时同步到 `ready_for_review`
- worker 异常退出时同步到 `blocked`

### 5. CLI Surface

- 扩展 `scripts/runtime/maestro_collab.py`
- 新增 `scripts/runtime/coordctl.py`
- 支持：
  - `work create/list/show/transition/mark`
  - `update add`
  - `request create/review`
- 保留旧命令：
  - `assign`
  - `state`
  - `suggest`

### 6. Migration / Export

- `scripts/runtime/migrate_collab_to_mongo.py`
  - SQLite runtime facts -> Mongo runtime registry
  - `TASK.md / TASK-REPORT.md` 最小字段 -> Mongo control plane
- `scripts/runtime/export_collab_snapshots.py`
  - Mongo control plane -> Markdown 快照

### 7. Status API Integration

- 新增 `/api/v1/collab/control-plane`
- `/api/v1/state` 新增 `control_plane` 摘要段

### 8. Smoke Verification

- 新增 `scripts/runtime/smoke_mongo_multicli.py`
- 支持：
  - 显式 `--mongo-uri`
  - 缺省时自动加载项目根目录 `.env`

## Key Files

- `src/services/maestro/collab/store/*`
- `src/services/maestro/collab/services/*`
- `src/services/maestro/collab/authz/*`
- `src/services/maestro/collab/backends/mongo/*`
- `src/services/maestro/collab/runtime_registry.py`
- `src/services/symphony/mongo_tracker.py`
- `src/services/symphony/config.py`
- `src/services/symphony/tracker_factory.py`
- `src/services/symphony/service.py`
- `src/services/symphony/orchestrator.py`
- `src/services/symphony/status_api.py`
- `scripts/runtime/maestro_collab.py`
- `scripts/runtime/coordctl.py`
- `scripts/runtime/migrate_collab_to_mongo.py`
- `scripts/runtime/export_collab_snapshots.py`
- `scripts/runtime/smoke_mongo_multicli.py`

## Verification Evidence

### Targeted Regression

```bash
pytest tests/unit/services/symphony/test_config.py \
  tests/unit/services/symphony/test_tracker_factory.py \
  tests/unit/services/symphony/test_mongo_tracker.py \
  tests/unit/services/symphony/test_mongo_runtime_flow.py \
  tests/unit/services/symphony/test_orchestrator.py \
  tests/unit/services/symphony/test_workspace_manager.py \
  tests/unit/services/symphony/test_status_api.py \
  tests/unit/services/symphony/test_maestro_collab_cli.py \
  tests/unit/services/symphony/test_maestro_namespace.py \
  tests/unit/services/symphony/test_collab_backend_selection.py \
  tests/unit/maestro_collab \
  tests/unit/runtime/test_maestro_coordination_cli.py \
  tests/unit/runtime/test_collab_migration_scripts.py \
  tests/unit/runtime/test_smoke_mongo_multicli.py \
  -q -o addopts=''
```

Result:

- `77 passed`

最新扩展后的定向回归：

```bash
pytest tests/unit/services/symphony/test_config.py \
  tests/unit/services/symphony/test_tracker_factory.py \
  tests/unit/services/symphony/test_mongo_tracker.py \
  tests/unit/services/symphony/test_mongo_runtime_flow.py \
  tests/unit/services/symphony/test_orchestrator.py \
  tests/unit/services/symphony/test_workspace_manager.py \
  tests/unit/services/symphony/test_status_api.py \
  tests/unit/services/symphony/test_maestro_collab_cli.py \
  tests/unit/services/symphony/test_maestro_namespace.py \
  tests/unit/services/symphony/test_collab_backend_selection.py \
  tests/unit/maestro_collab \
  tests/unit/runtime/test_maestro_coordination_cli.py \
  tests/unit/runtime/test_collab_migration_scripts.py \
  tests/unit/runtime/test_smoke_mongo_multicli.py \
  -q -o addopts=''
```

Result:

- `77 passed`

### Real Mongo Smoke

Executed:

```bash
python scripts/runtime/smoke_mongo_multicli.py
```

Observed output:

```json
{
  "assignment_status": "retrying",
  "control_plane_status": "ready_for_review",
  "db_name": "mystocks_coord_smoke_d9b2b916",
  "status_api_control_plane_count": 1,
  "work_item_id": "SMOKE-1"
}
```

## Important Findings

- 本机 `localhost:27017` 需要鉴权才能 `createIndexes / dropDatabase`
- 匿名连接可 `ping`，但不足以跑真实 smoke
- 项目根目录 `.env` 中的 Mongo 凭据可用于无参 smoke 脚本
- 真实 Mongo 文档包含 `_id`，已补清洗逻辑，避免 Pydantic `extra_forbidden` 报错
- status API 现已在 `/api/v1/state` 中直接包含 `control_plane` 摘要段

## Remaining Work

- 完整的 `TASK.md / TASK-REPORT.md` 结构化导入
- 更细的状态机推进规则
- 更完整的 request/blocker 聚合视图
- 更接近真实部署方式的 integration / PM2 / Docker 验证
