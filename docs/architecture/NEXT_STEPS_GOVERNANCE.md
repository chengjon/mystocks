# 下一步工作指引：架构治理与数据流标准化 (2026Q1)

> **历史计划说明**:
> 本文件是架构相关的阶段性计划、路线图或实施方案，不是当前架构基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内优先级、时间线、实施状态和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 1. 当前背景
我们已经完成了 2026-02-08 的架构大重构，确立了 **5 大核心域边界** 并实现了 **API 路由动态标准化**。所有后续开发必须基于此架构基座。

## 2. 核心域开发指引

### 2.1 核心域 (Core) - 基础设施
- **任务目标**: 保持 `src/core/` 的纯净。
- **规范**: 任何新的全局配置或跨域协调逻辑必须实现为 `src/core/` 中的独立模块，并通过根目录的 `unified_manager.py` 暴露。

### 2.2 数据访问域 (Data Access) - 存储路由
- **任务目标**: 实现 TDengine 与 PostgreSQL 的透明读写。
- **规范**: 严禁在业务 Service 中直接调用数据库驱动。必须通过 `src/data_access/factory.py` 获取 DataAccess 实例。

### 2.3 业务服务域 (Services) - API 标准化
- **任务目标**: 彻底消除 API 硬编码。
- **规范**: 
  - 新增 API 路由必须先在 `web/backend/app/api/VERSION_MAPPING.py` 中注册。
  - 在 `main.py` 中，路由会自动根据映射注册，无需手动添加 `prefix`。

### 2.4 监控域 (Monitoring) - 异步非阻塞
- **任务目标**: 确保监控不拖慢业务。
- **规范**: 所有监控日志和指标记录必须使用 `src/monitoring/infrastructure/postgresql_async_v3` 提供的异步接口。

## 3. 协作检查清单 (Pre-push Checklist)
在提交 PR 之前，请自查以下三项：
1. **物理路径**: 是否有新增的 `.ts/js/yaml` 文件遗留在根目录？（必须移入 `config/`）
2. **路由注册**: 你的 API 路由是否使用了 `VERSION_MAPPING`？（禁止在 `app.include_router` 中手写 prefix）
3. **入口透明**: 如果你修改了根目录的 `.py` 文件，它是否保持了纯粹的 Re-export 结构？

## 4. 重点突破方向 (Next Milestones)
- **T02**: 完善 `SPEC_CONFLICT_MATRIX.md`，解决 API 契约与前端类型的冲突。
- **T05**: 实施 API 契约漂移检查，集成到 Pre-commit 钩子中。
