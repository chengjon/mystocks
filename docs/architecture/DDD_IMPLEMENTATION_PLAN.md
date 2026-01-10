# Task Plan: DDD架构应用实施

## 当前进度: 100% (Phases 1-11B) -> 准备进入 Phase 12 生产级增强

## 实施阶段

### Phase 1-10: 核心架构与垂直切片 ✅
*已完成策略、交易、行情、基础架构的全面 DDD 落地与验证。*

### Phase 11A: 系统集成与运行态引导 ✅
- [x] 配置依赖注入容器 (`bootstrap.py`)
- [x] 实现事件处理器并完成订阅 (Trading -> Portfolio)
- [x] 编写全链路集成演示脚本

### Phase 11B: 自选股与智能组合管理 [COMPLETED] ✅
- [x] **Watchlist 领域层**: 聚合根、快照服务、预警值对象
- [x] **Portfolio 增强**: 绩效分析、配置归因、交易流水记录
- [x] **预测服务**: 集成 `PredictionService` 实现价格与波动率预测
- [x] **持久化实现**: Watchlist 与 Portfolio 的 PostgreSQL 实现
- [x] **演示脚本**: `scripts/watchlist_portfolio_demo.py`

### Phase 12: 生产级增强 (Production Readiness) [NEXT] ⏳
- [ ] 12.1 **分布式事件总线**: 将 `LocalEventBus` 升级为基于 Redis 的异步总线，支持长耗时任务（如大规模回测）。
- [ ] 12.2 **分布式锁与并发控制**: 在 Repository 层引入乐观锁，防止多策略并发修改同一组合持仓。
- [ ] 12.3 **实时数据流集成**: 对接 WebSocket 行情流，驱动领域模型的实时状态更新（Real-time Mark-to-Market）。
- [ ] 12.4 **API 安全与多租户**: 引入用户上下文，支持多用户独立的自选股与组合。

### Phase 13: 自动化运维与监控可视化 [PLANNED]
- [ ] 13.1 **Grafana 业务仪表盘**: 基于 DDD 导出的指标（如胜率、回撤）创建可视化看板。
- [ ] 13.2 **自动恢复机制**: 实现 Saga 事务补偿逻辑，处理订单执行失败时的持仓回滚。
