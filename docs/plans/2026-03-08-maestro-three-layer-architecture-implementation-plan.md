# Maestro Three-Layer Architecture Implementation Plan

## Goal

为当前基于 Symphony 的本地多 CLI 运行时建立一个未来可独立的命名与分层骨架，使后续可把通用
runtime 与多 CLI 协作核心迁移出去，同时保留 MyStocks 自身 profile。

## Task 1: 固化命名与层次文档

**Files**

- Create: `docs/plans/2026-03-08-maestro-three-layer-architecture-design.md`
- Create: `docs/plans/2026-03-08-maestro-three-layer-architecture-implementation-plan.md`
- Modify: `docs/guides/multi-cli-tasks/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
- Modify: `WORKFLOW.md`

**Steps**

1. 写清楚 `Maestro` 与 `Symphony` 的关系
2. 写清楚三层边界
3. 把角色责任模型补进权威说明

## Task 2: 先写失败测试，锁定新 namespace

**Files**

- Create: `tests/unit/services/symphony/test_maestro_namespace.py`

**Steps**

1. 验证 `src.services.maestro` 可以导入
2. 验证 `kernel` / `collab` / `profiles.mystocks` 三层可见
3. 验证 profile 中有角色模型与层次元信息

## Task 3: 建立最小兼容 namespace

**Files**

- Create: `src/services/maestro/__init__.py`
- Create: `src/services/maestro/kernel/__init__.py`
- Create: `src/services/maestro/collab/__init__.py`
- Create: `src/services/maestro/profiles/__init__.py`
- Create: `src/services/maestro/profiles/mystocks.py`
- Create: `src/services/maestro/README.md`
- Modify: `src/services/symphony/__init__.py`

**Steps**

1. 建立 `maestro` 兼容 namespace
2. 将现有 `symphony` runtime 通过 alias 方式暴露到 `maestro.kernel`
3. 将协作相关能力暴露到 `maestro.collab`
4. 将 MyStocks 专属责任模型与三层元信息放入 `maestro.profiles.mystocks`

## Task 4: 验证

**Files**

- Create: `openspec/changes/define-maestro-three-layer-architecture/...`

**Steps**

1. 跑新测试与 Symphony 单测
2. 跑 `ruff` / `black --check`
3. 跑 `openspec validate define-maestro-three-layer-architecture --strict`
