# Maestro Collab Core Implementation Plan

## Goal

实现 `maestro.collab` 的第一版可持久化协作核心，覆盖 assignment、workspace registry、
heartbeat/stale 三类机器态，并接入现有本地运行时。

## Task 1: 文档与规格

**Files**

- Create: `docs/plans/2026-03-08-maestro-collab-core-design.md`
- Create: `docs/plans/2026-03-08-maestro-collab-core-implementation-plan.md`
- Create: `openspec/changes/add-maestro-collab-core/proposal.md`
- Create: `openspec/changes/add-maestro-collab-core/design.md`
- Create: `openspec/changes/add-maestro-collab-core/tasks.md`
- Create: `openspec/changes/add-maestro-collab-core/specs/symphony-service/spec.md`

## Task 2: 先写失败测试

**Files**

- Create: `tests/unit/services/symphony/test_maestro_collab_registry.py`

**Steps**

1. 测试 schema bootstrap
2. 测试 assignment 持久化
3. 测试 workspace registry 持久化
4. 测试 heartbeat 与 stale 检测

## Task 3: 实现 `maestro.collab`

**Files**

- Create: `src/services/maestro/collab/models.py`
- Create: `src/services/maestro/collab/registry.py`
- Modify: `src/services/maestro/collab/__init__.py`

## Task 4: 轻量接入运行时

**Files**

- Modify: `src/services/symphony/workspace_manager.py`
- Modify: `src/services/symphony/orchestrator.py`
- Modify: `src/services/symphony/service.py`

**Steps**

1. 为本地 tracker 创建 collab registry
2. 在 workspace 创建时注册 workspace
3. 在 dispatch / event / exit 时刷新 assignment 与 heartbeat

## Task 5: 验证

**Steps**

1. 跑新增 collab 单测
2. 跑 Symphony 单测
3. 跑 `ruff` / `black --check`
4. 跑 `openspec validate add-maestro-collab-core --strict`
