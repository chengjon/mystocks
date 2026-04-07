> **历史分析说明**:
> 本文件是阶段性分析材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。

====================================================================================================
MyStocks API 架构设计深度分析报告
====================================================================================================

**Historical Report Snapshot Time**: 2025-11-30T20:49:56.712832

## 📊 整体统计

- **总API模块数**: 35
- **总端点数**: 261
- **API版本**: v1, v2
- **标签类别**: 24 个

### HTTP方法分布

- **DELETE**: 12 个端点 (4%)
- **GET**: 164 个端点 (62%)
- **POST**: 76 个端点 (29%)
- **PUT**: 9 个端点 (3%)

## 🏗️ API 模块组织结构


### announcement
- **文件**: `announcement.py`
- **路由前缀**: `/api/announcement`
- **端点数**: 13
- **端点清单**:

  - `POST /fetch` -
  - `GET /list` -
  - `GET /today` -
  - `GET /important` -
  - `GET /stock/{stock_code}` -
  - `POST /monitor/evaluate` - 评估所有监控规则
  - `GET /stats` - 获取公告统计信息
  - `GET /types` - 获取支持的公告类型
  - `GET /monitor-rules` - 获取监控规则列表
  - `POST /monitor-rules` -
  - `PUT /monitor-rules/{rule_id}` -
  - `DELETE /monitor-rules/{rule_id}` -
  - `GET /triggered-records` -

### announcement.routes
- **文件**: `announcement/routes.py`
- **路由前缀**: `/announcement`
- **端点数**: 14
- **端点清单**:

  - `GET /health` - 健康检查
  - `GET /status` - 获取服务状态
  - `POST /analyze` -
  - `POST /fetch` -
  - `GET /list` -
  - `GET /today` -
  - `GET /important` -
  - `GET /stats` - 获取公告统计信息
  - `GET /monitor-rules` - 获取监控规则列表
  - `POST /monitor-rules` -
  - `PUT /monitor-rules/{rule_id}` -
  - `DELETE /monitor-rules/{rule_id}` -
  - `GET /triggered-records` -
  - `POST /monitor/evaluate` - 评估所有监控规则

### auth
- **文件**: `auth.py`
- **路由前缀**: `(根路由)`
- **端点数**: 5
- **端点清单**:

  - `POST /login` -
  - `POST /logout` -
  - `GET /me` -
  - `POST /refresh` -
  - `GET /users` -

### backtest_ws
- **文件**: `backtest_ws.py`
- **路由前缀**: `/ws`
- **端点数**: 1
- **端点清单**:

  - `GET /status` - 获取 WebSocket 连接状态

### backup_recovery
- **文件**: `backup_recovery.py`
- **路由前缀**: `/api/backup-recovery`
- **端点数**: 13
- **端点清单**:

  - `POST /backup/tdengine/full` - 执行 TDengine 全量备份
  - `POST /backup/tdengine/incremental` -
  - `POST /backup/postgresql/full` - 执行 PostgreSQL 全量备份
  - `GET /backups` -
  - `POST /recovery/tdengine/full` -
  - `POST /recovery/tdengine/pitr` -
  - `POST /recovery/postgresql/full` -
  - `GET /recovery/objectives` - 获取恢复目标 (RTO/RPO)
  - `POST /scheduler/start` - 启动备份调度器
  - `POST /scheduler/stop` - 停止备份调度器
  - `GET /scheduler/jobs` - 获取所有计划的备份任务
  - `GET /integrity/verify/{backup_id}` -
  - `POST /cleanup/old-backups` -

### cache
- **文件**: `cache.py`
- **路由前缀**: `/cache`
- **端点数**: 11
- **端点清单**:

  - `GET /status` -
  - `GET /{symbol}/{data_type}` -
  - `POST /{symbol}/{data_type}` -
  - `DELETE /{symbol}` -
  - `GET /{symbol}/{data_type}/fresh` -
  - `POST /evict/manual` -
  - `GET /eviction/stats` -
  - `POST /prewarming/trigger` -
  - `GET /prewarming/status` -
  - `GET /monitoring/metrics` -
  - `GET /monitoring/health` -

### dashboard
- **文件**: `dashboard.py`
- **路由前缀**: `/api/dashboard`
- **端点数**: 1
- **端点清单**:

  - `GET /health` - 健康检查端点

### data
- **文件**: `data.py`
- **路由前缀**: `(根路由)`
- **端点数**: 15
- **端点清单**:

  - `GET /stocks/basic` -
  - `GET /stocks/industries` -
  - `GET /stocks/concepts` -
  - `GET /stocks/daily` -
  - `GET /markets/overview` -
  - `GET /stocks/search` -
  - `GET /kline` -
  - `GET /stocks/kline` -
  - `GET /financial` -
  - `GET /markets/price-distribution` -
  - `GET /markets/hot-industries` -
  - `GET /markets/hot-concepts` -
  - `GET /stocks/intraday` -
  - `GET /stocks/{symbol}/detail` -
  - `GET /stocks/{symbol}/trading-summary` -

### health
- **文件**: `health.py`
- **路由前缀**: `(根路由)`
- **端点数**: 3
- **端点清单**:

  - `GET /health` - 系统健康检查API端点
  - `GET /health/detailed` - 详细健康检查
  - `GET /reports/health/{timestamp}` -

### indicators
- **文件**: `indicators.py`
- **路由前缀**: `(根路由)`
- **端点数**: 8
- **端点清单**:

  - `GET /registry` - 获取指标注册表
  - `GET /registry/{category}` -
  - `POST /calculate` -
  - `POST /configs` -
  - `GET /configs` -
  - `GET /configs/{config_id}` -
  - `PUT /configs/{config_id}` -
  - `DELETE /configs/{config_id}` -

### industry_concept_analysis
- **文件**: `industry_concept_analysis.py`
- **路由前缀**: `/api/analysis`
- **端点数**: 5
- **端点清单**:

  - `GET /industry/list` - 获取所有行业分类列表
  - `GET /concept/list` - 获取所有概念分类列表
  - `GET /industry/stocks` -
  - `GET /concept/stocks` -
  - `GET /industry/performance` -

### market
- **文件**: `market.py`
- **路由前缀**: `/api/market`
- **端点数**: 5
- **端点清单**:

  - `POST /etf/refresh` -
  - `POST /lhb/refresh` -
  - `GET /stocks` -
  - `GET /kline` -
  - `GET /health` - API健康检查

### market_v2
- **文件**: `market_v2.py`
- **路由前缀**: `/api/market/v2`
- **端点数**: 13
- **端点清单**:

  - `GET /fund-flow` -
  - `POST /fund-flow/refresh` -
  - `GET /etf/list` -
  - `POST /etf/refresh` - 从东方财富刷新全市场ETF数据
  - `GET /lhb` -
  - `POST /lhb/refresh` -
  - `GET /sector/fund-flow` -
  - `POST /sector/fund-flow/refresh` -
  - `GET /dividend` -
  - `POST /dividend/refresh` -
  - `GET /blocktrade` -
  - `POST /blocktrade/refresh` -
  - `POST /refresh-all` - 一键刷新所有市场数据（用于定时任务）

### metrics
- **文件**: `metrics.py`
- **路由前缀**: `(根路由)`
- **端点数**: 1
- **端点清单**:

  - `GET /metrics` - Prometheus metrics端点

### ml
- **文件**: `ml.py`
- **路由前缀**: `/ml`
- **端点数**: 8
- **端点清单**:

  - `POST /tdx/data` -
  - `GET /tdx/stocks/{market}` -
  - `POST /features/generate` -
  - `POST /models/train` -
  - `POST /models/predict` -
  - `GET /models` -
  - `GET /models/{model_name}` -
  - `POST /models/evaluate` -

### monitoring
- **文件**: `monitoring.py`
- **路由前缀**: `/api/monitoring`
- **端点数**: 17
- **端点清单**:

  - `GET /alert-rules` -
  - `POST /alert-rules` -
  - `PUT /alert-rules/{rule_id}` -
  - `DELETE /alert-rules/{rule_id}` -
  - `GET /alerts` -
  - `POST /alerts/{alert_id}/mark-read` -
  - `POST /alerts/mark-all-read` - 批量标记所有未读告警为已读
  - `GET /realtime/{symbol}` -
  - `GET /realtime` -
  - `POST /realtime/fetch` -
  - `GET /dragon-tiger` -
  - `POST /dragon-tiger/fetch` -
  - `GET /summary` - 获取监控系统摘要
  - `GET /stats/today` - 获取今日统计数据
  - `POST /control/start` -
  - `POST /control/stop` - 停止监控
  - `GET /control/status` - 获取监控状态

### monitoring.routes
- **文件**: `monitoring/routes.py`
- **路由前缀**: `/monitoring`
- **端点数**: 3
- **端点清单**:

  - `GET /health` - 健康检查
  - `GET /status` - 获取服务状态
  - `POST /analyze` -

### multi_source
- **文件**: `multi_source.py`
- **路由前缀**: `/api/multi-source`
- **端点数**: 8
- **端点清单**:

  - `GET /health` - 获取所有数据源的健康状态
  - `GET /health/{source_type}` -
  - `GET /realtime-quote` -
  - `GET /fund-flow` -
  - `GET /dragon-tiger` -
  - `POST /refresh-health` - 刷新所有数据源的健康状态
  - `POST /clear-cache` - 清空数据缓存
  - `GET /supported-categories` - 获取所有支持的数据类别及其对应的数据源

### multi_source.routes
- **文件**: `multi_source/routes.py`
- **路由前缀**: `/multi_source`
- **端点数**: 3
- **端点清单**:

  - `GET /health` - 健康检查
  - `GET /status` - 获取服务状态
  - `POST /analyze` -

### notification
- **文件**: `notification.py`
- **路由前缀**: `(根路由)`
- **端点数**: 6
- **端点清单**:

  - `GET /status` - 获取邮件服务状态
  - `POST /email/send` -
  - `POST /email/welcome` -
  - `POST /email/newsletter` -
  - `POST /email/price-alert` -
  - `POST /test-email` -

### prometheus_exporter
- **文件**: `prometheus_exporter.py`
- **路由前缀**: `(根路由)`
- **端点数**: 3
- **端点清单**:

  - `GET /metrics` - Prometheus 指标端点
  - `GET /metrics/health` -
  - `GET /metrics/list` -

### risk_management
- **文件**: `risk_management.py`
- **路由前缀**: `/api/v1/risk`
- **端点数**: 9
- **端点清单**:

  - `GET /var-cvar` -
  - `GET /beta` -
  - `GET /dashboard` -
  - `GET /metrics/history` -
  - `GET /alerts` -
  - `POST /alerts` -
  - `PUT /alerts/{alert_id}` -
  - `DELETE /alerts/{alert_id}` -
  - `POST /notifications/test` -

### sse_endpoints
- **文件**: `sse_endpoints.py`
- **路由前缀**: `/api/v1/sse`
- **端点数**: 5
- **端点清单**:

  - `GET /training` -
  - `GET /backtest` -
  - `GET /alerts` -
  - `GET /dashboard` -
  - `GET /status` - Get SSE server status

### stock_search
- **文件**: `stock_search.py`
- **路由前缀**: `(根路由)`
- **端点数**: 7
- **端点清单**:

  - `GET /search` -
  - `GET /quote/{symbol}` -
  - `GET /profile/{symbol}` -
  - `GET /news/{symbol}` -
  - `GET /news/market/{category}` -
  - `GET /recommendation/{symbol}` -
  - `POST /cache/clear` -

### strategy
- **文件**: `strategy.py`
- **路由前缀**: `/api/strategy`
- **端点数**: 6
- **端点清单**:

  - `GET /definitions` - 获取所有策略定义
  - `POST /run/single` -
  - `POST /run/batch` -
  - `GET /results` -
  - `GET /matched-stocks` -
  - `GET /stats/summary` -

### strategy_management
- **文件**: `strategy_management.py`
- **路由前缀**: `/api/v1/strategy`
- **端点数**: 12
- **端点清单**:

  - `GET /strategies` -
  - `POST /strategies` -
  - `GET /strategies/{strategy_id}` -
  - `PUT /strategies/{strategy_id}` -
  - `DELETE /strategies/{strategy_id}` -
  - `POST /models/train` -
  - `GET /models/training/{task_id}/status` -
  - `GET /models` -
  - `POST /backtest/run` -
  - `GET /backtest/results` -
  - `GET /backtest/results/{backtest_id}` -
  - `GET /backtest/results/{backtest_id}/chart-data` -

### system
- **文件**: `system.py`
- **路由前缀**: `(根路由)`
- **端点数**: 9
- **端点清单**:

  - `GET /health` - 系统健康检查端点 (双数据库架构: TDengine + PostgreSQL)
  - `GET /adapters/health` - 🚀 适配器健康检查端点（新增）
  - `GET /datasources` - 获取已配置的数据源列表
  - `POST /test-connection` -
  - `GET /logs` -
  - `GET /logs/summary` - 获取日志统计摘要
  - `GET /architecture` - 获取系统架构信息 (Week 3简化后 - 双数据库架构)
  - `GET /database/health` -
  - `GET /database/stats` -

### tasks
- **文件**: `tasks.py`
- **路由前缀**: `/api/tasks`
- **端点数**: 13
- **端点清单**:

  - `POST /register` -
  - `DELETE /{task_id}` -
  - `GET /` -
  - `GET /{task_id}` - 获取任务统计信息
  - `POST /{task_id}/start` -
  - `POST /{task_id}/stop` -
  - `GET /executions/` -
  - `GET /executions/{execution_id}` -
  - `GET /statistics/` - 获取任务统计信息
  - `POST /import` -
  - `POST /export` -
  - `DELETE /executions/cleanup` -
  - `GET /health` - 任务管理健康检查

### technical.routes
- **文件**: `technical/routes.py`
- **路由前缀**: `/technical`
- **端点数**: 3
- **端点清单**:

  - `GET /health` - 健康检查
  - `GET /status` - 获取服务状态
  - `POST /analyze` -

### technical_analysis
- **文件**: `technical_analysis.py`
- **路由前缀**: `/api/technical`
- **端点数**: 9
- **端点清单**:

  - `GET /{symbol}/indicators` -
  - `GET /{symbol}/trend` -
  - `GET /{symbol}/momentum` -
  - `GET /{symbol}/volatility` -
  - `GET /{symbol}/volume` -
  - `GET /{symbol}/signals` -
  - `GET /{symbol}/history` -
  - `POST /batch/indicators` -
  - `GET /patterns/{symbol}` -

### trade.routes
- **文件**: `trade/routes.py`
- **路由前缀**: `/trade`
- **端点数**: 6
- **端点清单**:

  - `GET /health` - 健康检查
  - `GET /portfolio` - 获取投资组合概览
  - `GET /positions` - 获取持仓列表
  - `GET /trades` -
  - `GET /statistics` - 获取交易统计数据
  - `POST /execute` -

### tradingview
- **文件**: `tradingview.py`
- **路由前缀**: `(根路由)`
- **端点数**: 6
- **端点清单**:

  - `POST /chart/config` -
  - `POST /mini-chart/config` -
  - `POST /ticker-tape/config` -
  - `GET /market-overview/config` -
  - `GET /screener/config` -
  - `GET /symbol/convert` -

### v1.pool_monitoring
- **文件**: `v1/pool_monitoring.py`
- **路由前缀**: `/pool-monitoring`
- **端点数**: 4
- **端点清单**:

  - `GET /postgresql/stats` - 获取PostgreSQL连接池统计信息
  - `GET /tdengine/stats` - 获取TDengine连接池统计信息
  - `GET /health` - 检查所有连接池的健康状态
  - `GET /alerts` - 检测连接池是否存在需要告警的情况

### watchlist
- **文件**: `watchlist.py`
- **路由前缀**: `(根路由)`
- **端点数**: 15
- **端点清单**:

  - `GET /` -
  - `GET /symbols` -
  - `POST /add` -
  - `DELETE /remove/{symbol}` -
  - `GET /check/{symbol}` -
  - `PUT /notes/{symbol}` -
  - `GET /count` -
  - `DELETE /clear` -
  - `GET /groups` -
  - `POST /groups` -
  - `PUT /groups/{group_id}` -
  - `DELETE /groups/{group_id}` -
  - `GET /group/{group_id}` -
  - `PUT /move` -
  - `GET /with-groups` -

### wencai
- **文件**: `wencai.py`
- **路由前缀**: `/api/market/wencai`
- **端点数**: 1
- **端点清单**:

  - `GET /health` - 健康检查


## 📈 路由统计按前缀

- **announcement**: 13 个端点
- **announcement.routes**: 14 个端点
- **auth**: 5 个端点
- **backtest_ws**: 1 个端点
- **backup_recovery**: 13 个端点
- **cache**: 11 个端点
- **dashboard**: 1 个端点
- **data**: 15 个端点
- **health**: 3 个端点
- **indicators**: 8 个端点
- **industry_concept_analysis**: 5 个端点
- **market**: 5 个端点
- **market_v2**: 13 个端点
- **metrics**: 1 个端点
- **ml**: 8 个端点
- **monitoring**: 17 个端点
- **monitoring.routes**: 3 个端点
- **multi_source**: 8 个端点
- **multi_source.routes**: 3 个端点
- **notification**: 6 个端点
- **prometheus_exporter**: 3 个端点
- **risk_management**: 9 个端点
- **sse_endpoints**: 5 个端点
- **stock_search**: 7 个端点
- **strategy**: 6 个端点
- **strategy_management**: 12 个端点
- **system**: 9 个端点
- **tasks**: 13 个端点
- **technical.routes**: 3 个端点
- **technical_analysis**: 9 个端点
- **trade.routes**: 6 个端点
- **tradingview**: 6 个端点
- **v1.pool_monitoring**: 4 个端点
- **watchlist**: 15 个端点
- **wencai**: 1 个端点
