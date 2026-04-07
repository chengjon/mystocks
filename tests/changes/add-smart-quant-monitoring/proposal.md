# Change: Smart Quantitative Monitoring and Portfolio Management System

> **专题方案说明**:
> 本文件用于描述某项测试能力、测试契约、测试规格或变更提案的边界与要求，服务于测试方案管理和差异追踪。
> 它不自动等同于当前已落地测试实现或当前运行结果；执行时需同时核对 `architecture/STANDARDS.md`、当前代码实现、测试脚本与最新验证结果。


## Why

当前系统缺乏智能股票监控和投资组合管理能力，无法满足量化投资需求，而v3.0实施计划通过充分复用现有架构（MonitoringEventPublisher、src/gpu模块）可实现高性价比的快速落地，开发周期9-10周。

## What Changes

### Watchlist Management (监控清单管理)
- 新增 `monitoring_watchlists` 和 `monitoring_watchlist_stocks` PostgreSQL 表，支持入库上下文记录（entry_price, entry_reason, stop_loss_price, target_price）
- 新增 8 个 RESTful API 端点（CRUD 清单、批量添加股票、风控配置管理）
- 数据迁移：现有 watchlist.py 数据 → 新系统（保留历史数据用于回测）

### Dynamic Health Scoring (动态健康度评分)
- 新增 `MarketRegimeIdentifier` 市场体制识别器（牛/熊/震荡三态）
- 新增五维雷达图评分（趋势、技术、动量、波动、风险），根据市场体制动态调整权重
- 新增高级风险指标计算器：Sortino 比率、Calmar 比率、最大回撤持续期、下行标准差
- 异步批量保存：复用 `MonitoringEventPublisher` + Worker，批量写入 `monitoring_health_scores` 表

### Dual-Mode Calculation Engine (双模计算引擎)
- 新增 `VectorizedHealthCalculator` (CPU模式，Pandas向量化，100只股票 <5秒)
- 新增 `GPUHealthCalculator` (GPU模式，CuPy/RAPIDS，1000只股票 <2秒，50-100x加速)
- 新增 `HealthCalculatorFactory` 智能工厂，根据数据规模和GPU健康状态自动切换
- 复用 `src/monitoring/gpu_performance_optimizer.py` 和 `src/gpu` 模块

### Portfolio Optimization (投资组合优化)
- 新增组合整体健康度分析（加权平均评分、风险分布、行业集中度）
- 新增再平衡建议算法（考虑交易成本、再平衡阈值5%）
- 新增风险预警系统（止损/止盈触发，三级预警：🔴紧急、🟡提醒、🟢提示）

### Frontend Visualization (前端可视化)
- 新增清单管理页面（支持入库上下文表单）
- 新增健康度雷达图组件（ECharts 五维雷达图）
- 新增风控看板页面（止损/止盈预警列表）

## Impact

### Affected specs
- 新增 `watchlist-management` 规范
- 新增 `health-scoring` 规范
- 新增 `calculation-engine` 规范
- 新增 `portfolio-optimization` 规范
- 新增 `data-migration` 规范

### Affected code
- `src/monitoring/infrastructure/postgresql_async.py` - 新增异步访问层
- `src/monitoring/domain/market_regime.py` - 新增市场体制识别器
- `src/monitoring/domain/calculator_cpu.py` - 新增CPU计算引擎
- `src/monitoring/domain/calculator_gpu.py` - 新增GPU计算引擎
- `src/monitoring/domain/calculator_factory.py` - 新增计算引擎工厂
- `src/monitoring/async_monitoring.py` - 扩展支持 `metric_update` 事件
- `web/backend/app/api/monitoring_watchlists.py` - 新增清单管理API
- `web/backend/app/api/monitoring_analysis.py` - 新增智能分析API
- `web/frontend/src/views/monitoring/` - 新增监控相关页面

### Dependencies
- PostgreSQL (已有) - 存储 watchlist 和 health_scores 表
- Redis (已有) - 事件总线队列
- TDengine (已有) - K线数据查询
- `src/monitoring/gpu_performance_optimizer.py` (已有) - GPU健康检查
- `src/gpu/` (已有) - GPU加速模块

### Breaking changes
- None (新增功能，不影响现有系统)

### Performance Impact
- API响应时间：P95 <500ms (CQRS架构，读写分离)
- CPU计算：100只股票 <5秒
- GPU计算：1000只股票 <2秒 (50-100x加速比)
- Worker批量写入：50条/批次，成功率 >99%

### Data Migration
- 现有 watchlist.py 数据 → monitoring_watchlists + monitoring_watchlist_stocks 表
- 保留所有历史入库记录（用于回测验证）
- 迁移脚本：`scripts/migrations/migrate_watchlist_to_monitoring.py`
- 预计数据量：~100只股票，5个清单

---

**变更ID**: `add-smart-quant-monitoring`
**状态**: 待审核
**创建日期**: 2026-01-07
**作者**: Claude Code (Main CLI)
**预计周期**: 9-10周
