# Task Plan: Signal Monitoring System Phase 2 Extended Implementation

> **历史计划说明**:
> 本文件是 API 相关的阶段性计划、路线图或方案材料，不是当前 API 契约、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内优先级、时间线、实施状态和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Goal
完成信号监控系统 v2.1 的所有剩余功能，包括服务集成、统计聚合、额外API端点和告警通知配置。

## Phases

- [x] **Phase 2.1**: 核心基础功能（已完成）
  - [x] 数据库表结构
  - [x] 3个核心API端点
  - [x] Grafana仪表板
  - [x] Prometheus告警规则
  - [x] 集成测试

- [ ] **Phase 2.2**: 服务集成（P0 - 关键）
  - [ ] 查找并分析 SignalGenerationService
  - [ ] 集成 MonitoredStrategyExecutor
  - [ ] 集成 SignalPushService 监控
  - [ ] 实现 SignalResultTracker

- [ ] **Phase 2.3**: 统计聚合（P1 - 重要）
  - [ ] 创建 signal_statistics_hourly 表
  - [ ] 实现 SignalAggregationTask
  - [ ] 配置定时调度

- [ ] **Phase 2.4**: API补充（P1 - 重要）
  - [ ] GET /api/signals/statistics
  - [ ] GET /api/signals/active
  - [ ] GET /api/strategies/{strategy_id}/health (detailed)

- [ ] **Phase 2.5**: 告警通知（P2 - 增强）
  - [ ] 配置 Alertmanager
  - [ ] Email 通知配置
  - [ ] Webhook 通知配置

- [ ] **Phase 2.6**: 验证和测试
  - [ ] 端到端集成测试
  - [ ] 性能测试
  - [ ] 生成完成报告

## Key Questions

1. **SignalGenerationService 位置**: 在 src/ 的哪个位置？
2. **SignalPushService 是否存在**: 需要创建还是集成现有服务？
3. **定时任务调度**: 使用 Celery 还是 APScheduler？
4. **Alertmanager 配置**: 是否已有 Alertmanager 容器？

## Decisions Made

- **服务集成优先**: 先实现服务集成，让监控系统真正运转
- **使用现有装饰器**: 复用 src/monitoring/signal_decorator.py 中的装饰器
- **APScheduler 用于定时任务**: 轻量级，无需额外 Celery 依赖

## Errors Encountered

*(暂无)*

## Status

**Currently in Phase 2.2** - 查找并分析现有的 SignalGenerationService，准备进行服务集成
