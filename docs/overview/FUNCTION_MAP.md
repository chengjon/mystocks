# FUNCTION_MAP

> **使用说明**:
> 本文件用于快速定位特定专题工作流中的能力入口，不是当前仓库共享规则、全局架构地图或长期维护承诺的唯一事实来源。
> 如与 `architecture/STANDARDS.md` 冲突，应始终以 `architecture/STANDARDS.md` 作为仓库级共享规则与审批门禁来源；若涉及具体执行入口，再按职责分别核对根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

## Purpose

本文件用于快速定位当前专题工作流中的主要能力入口。

## 0. Data Source Optimization V2 Closeout

- `openspec/changes/optimize-data-source-v2/proposal.md`
  - `optimize-data-source-v2` 的专题目标、范围与阶段划分
- `openspec/changes/optimize-data-source-v2/design.md`
  - SmartCache、CircuitBreaker、SmartRouter、BatchProcessor、监控与可选 Phase 3 能力的设计约束
- `openspec/changes/optimize-data-source-v2/tasks.md`
  - 当前最完整的执行清单；已明确区分 repo-local 已闭合项与外部部署 / 观测 / 验收项
- `openspec/changes/optimize-data-source-v2/REPO_LOCAL_STATUS.md`
  - 单页结论：仓库内实现、测试、文档与治理已正式闭环；剩余未勾选项全部属于外部动作
- `docs/guides/data-source/INDEX.md`
  - 数据源专题文档导航入口
- `docs/guides/data-source/DATA_SOURCE_OPTIMIZATION_DEPLOYMENT_CHECKLIST.md`
  - 后续外部部署 / 灰度 / 观测执行入口
- `docs/reports/DATA_SOURCE_OPTIMIZATION_V2_LOCAL_PERFORMANCE_REPORT_2026-05-02.md`
  - 本地性能与吞吐 benchmark 收口报告
- `docs/reports/DATA_SOURCE_OPTIMIZATION_V2_LOCAL_COST_ANALYSIS_2026-05-02.md`
  - 本地成本代理指标与 ROI 边界说明
- `docs/guides/data-source/DATA_SOURCE_OPERATIONS_MANUAL.md`
  - 运维、告警、监控与排障操作手册
- `docs/guides/data-source/DATA_SOURCE_DEVELOPER_GUIDE.md`
  - 开发者视角的调用链、扩展点与验证矩阵

> 当前结论：
> `optimize-data-source-v2` 已无合法可继续推进的仓库内新增改动；
> 后续只剩外部部署、live 观测、SLA 验收、会议与归档动作。

## 1. Control Plane

- `src/services/maestro/collab/store/models.py`
  - 控制面核心记录模型：`WorkItemRecord`、`WorkUpdateRecord`、`WorkRequestRecord`、`WorkEventRecord`、`WorkerStatusViewRecord`
- `src/services/maestro/collab/store/base.py`
  - `CollaborationStore` 协议接口
- `src/services/maestro/collab/backends/mongo/indexes.py`
  - Mongo 索引定义
- `src/services/maestro/collab/backends/mongo/store.py`
  - Mongo control-plane 读写实现

## 2. Authorization And Service Layer

- `src/services/maestro/collab/authz/policy.py`
  - `ActorIdentity`
  - `CoordinationAuthorizer`
  - `AuthorizationError`
- `src/services/maestro/collab/services/coordination.py`
  - `CoordinationService`
  - 作用域校验
  - 审计事件
  - `worker_status_views` 自动刷新

## 3. Runtime Registry

- `src/services/maestro/collab/registry.py`
  - 现有 SQLite runtime registry
- `src/services/maestro/collab/runtime_registry.py`
  - `MongoCollaborationRegistry`
  - `DualWriteCollaborationRegistry`
  - runtime -> control-plane 状态同步
  - control-plane 摘要读取

## 4. Runtime Dispatch Source

- `src/services/symphony/mongo_tracker.py`
  - `MongoWorkItemTrackerClient`
  - 从 Mongo `work_items` 获取 candidate issues
- `src/services/symphony/tracker_factory.py`
  - `create_tracker_client()`
  - 支持 `tracker.kind == mongo`
- `src/services/symphony/config.py`
  - `TrackerConfig` / `RuntimeConfig`
  - Mongo tracker 与 collab backend 配置解析

## 5. Runtime Wiring

- `src/services/symphony/service.py`
  - `_create_collab_registry()`
  - 支持 `sqlite / mongo / dual-write`
- `src/services/symphony/orchestrator.py`
  - dispatch / event / exit 时同步 control-plane

## 6. Status API

- `src/services/symphony/status_api.py`
  - `/api/v1/collab/control-plane`
  - `/api/v1/state` 中的 `control_plane` 摘要

## 7. CLI Surface

- `scripts/runtime/maestro_collab.py`
  - 兼容旧入口
  - 新增 `work / update / request` 命令组
- `scripts/runtime/coordctl.py`
  - 面向 control-plane 的兼容包装入口

## 8. Migration And Export

- `scripts/runtime/migrate_collab_to_mongo.py`
  - SQLite runtime facts -> Mongo runtime registry
  - `TASK.md / TASK-REPORT.md` 最小字段 -> Mongo control-plane
- `scripts/runtime/export_collab_snapshots.py`
  - Mongo control-plane -> Markdown 快照

## 9. Smoke And Validation

- `scripts/runtime/smoke_mongo_multicli.py`
  - 真实 Mongo smoke
  - 支持显式 `--mongo-uri`
  - 缺省时自动加载项目根目录 `.env`

## 10. Docs

- `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
  - 操作手册
- `docs/plans/2026-03-13-mongodb-multicli-coordination-design.md`
  - 设计文档
- `docs/plans/2026-03-13-mongodb-multicli-coordination-implementation-plan.md`
  - 实施计划
- `docs/reports/MONGODB_MULTICLI_COORDINATION_PROGRESS_2026-03-14.md`
  - 当前进展报告
