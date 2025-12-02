# MyStocks API端点文档

## 概览

本文档包含了MyStocks量化交易数据管理系统的所有API端点定义，提供完整的RESTful API接口信息。

### 总端点统计
- **总端点数量**: 280+ 个
- **HTTP方法分布**:
  - GET: 180+ 个端点
  - POST: 80+ 个端点
  - PUT: 15+ 个端点
  - DELETE: 15+ 个端点
  - PATCH: 2+ 个端点

### 功能模块分类
- **认证与用户管理**: 5 个端点
- **数据查询与股票信息**: 25+ 个端点
- **市场数据与行情**: 30+ 个端点
- **技术分析与指标**: 20+ 个端点
- **仪表盘与监控**: 15+ 个端点
- **策略管理与回测**: 20+ 个端点
- **自选股管理**: 15+ 个端点
- **通知与消息**: 8+ 个端点
- **系统管理**: 15+ 个端点
- **缓存管理**: 12+ 个端点
- **备份与恢复**: 15+ 个端点
- **数据质量监控**: 10+ 个端点
- **公告与资讯**: 15+ 个端点
- **WebSocket与SSE**: 5+ 个端点
- **风险管理**: 10+ 个端点

## 端点详情

### 主应用端点 (main.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/health` | GET | health_check | main.py | 系统健康检查 |
| `/api/socketio-status` | GET | socketio_status | main.py | Socket.IO连接状态 |
| `/api/csrf-token` | GET | get_csrf_token | main.py | 获取CSRF防护令牌 |
| `/` | GET | root | main.py | 根路径欢迎信息 |
| `/api/docs` | GET | custom_swagger_ui_html | main.py | 自定义Swagger文档页面 |

### 认证与用户管理 (auth.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/login` | POST | login_for_access_token | auth.py | 用户登录获取访问令牌 |
| `/logout` | POST | logout | auth.py | 用户登出 |
| `/me` | GET | read_users_me | auth.py | 获取当前用户信息 |
| `/refresh` | POST | refresh_token | auth.py | 刷新访问令牌 |
| `/users` | GET | get_users | auth.py | 获取用户列表（仅管理员） |

### 数据查询与股票信息 (data.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/stocks/basic` | GET | get_stocks_basic | data.py | 获取股票基本信息列表（支持筛选和分页） |
| `/stocks/industries` | GET | get_stocks_industries | data.py | 获取所有行业分类列表 |
| `/stocks/concepts` | GET | get_stocks_concepts | data.py | 获取所有概念分类列表 |
| `/stocks/daily` | GET | get_daily_kline | data.py | 获取股票日线数据 |
| `/markets/overview` | GET | get_market_overview | data.py | 获取市场概览数据 |
| `/stocks/search` | GET | search_stocks | data.py | 股票搜索接口 |
| `/kline` | GET | get_kline | data.py | 获取股票K线数据（别名） |
| `/stocks/kline` | GET | get_kline_data | data.py | 获取股票K线数据（标准化） |
| `/financial` | GET | get_financial_data | data.py | 获取股票财务数据 |
| `/markets/price-distribution` | GET | get_price_distribution | data.py | 获取全市场涨跌分布统计 |
| `/markets/hot-industries` | GET | get_hot_industries | data.py | 获取热门行业TOP5表现数据 |
| `/markets/hot-concepts` | GET | get_hot_concepts | data.py | 获取热门概念TOP5表现数据 |
| `/stocks/intraday` | GET | get_intraday_data | data.py | 获取股票分时数据 |
| `/stocks/{symbol}/detail` | GET | get_stock_detail | data.py | 获取股票详细信息 |
| `/stocks/{symbol}/trading-summary` | GET | get_trading_summary | data.py | 获取股票历史交易摘要统计 |
| `/test/factory` | GET | test_data_source_factory | data.py | 测试数据源工厂集成（无需认证） |

### 市场数据与行情 (market.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/fund-flow` | GET | get_fund_flow | market.py | 查询资金流向 |
| `/fund-flow/refresh` | POST | refresh_fund_flow | market.py | 刷新资金流向 |
| `/etf/list` | GET | get_etf_list | market.py | 查询ETF列表 |
| `/etf/refresh` | POST | refresh_etf | market.py | 刷新ETF数据 |
| `/chip-race` | GET | get_chip_race | market.py | 查询竞价抢筹 |
| `/chip-race/refresh` | POST | refresh_chip_race | market.py | 刷新抢筹数据 |
| `/lhb` | GET | get_lhb | market.py | 查询龙虎榜 |
| `/lhb/refresh` | POST | refresh_lhb | market.py | 刷新龙虎榜 |
| `/quotes` | GET | get_quotes | market.py | 查询实时行情 |
| `/stocks` | GET | get_stocks | market.py | 查询股票列表 |
| `/kline` | GET | get_kline | market.py | 查询K线数据 |
| `/heatmap` | GET | get_heatmap | market.py | 获取市场热力图数据 |
| `/health` | GET | health_check | market.py | 市场数据API健康检查 |

### 市场数据V2 (market_v2.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/fund-flow` | GET | get_fund_flow_v2 | market_v2.py | 查询个股资金流向 |
| `/fund-flow/refresh` | POST | refresh_fund_flow_v2 | market_v2.py | 刷新资金流向数据 |
| `/etf/list` | GET | get_etf_list_v2 | market_v2.py | 查询ETF列表 |
| `/etf/refresh` | POST | refresh_etf_v2 | market_v2.py | 刷新ETF数据 |
| `/lhb` | GET | get_lhb_v2 | market_v2.py | 查询龙虎榜 |
| `/lhb/refresh` | POST | refresh_lhb_v2 | market_v2.py | 刷新龙虎榜数据 |
| `/sector/fund-flow` | GET | get_sector_fund_flow | market_v2.py | 查询行业/概念资金流向 |
| `/sector/fund-flow/refresh` | POST | refresh_sector_fund_flow | market_v2.py | 刷新行业/概念资金流向 |
| `/dividend` | GET | get_dividend | market_v2.py | 查询股票分红配送 |
| `/dividend/refresh` | POST | refresh_dividend | market_v2.py | 刷新股票分红配送数据 |
| `/blocktrade` | GET | get_blocktrade | market_v2.py | 查询股票大宗交易 |
| `/blocktrade/refresh` | POST | refresh_blocktrade | market_v2.py | 刷新股票大宗交易数据 |
| `/refresh-all` | POST | refresh_all | market_v2.py | 批量刷新所有市场数据 |

### 技术分析与指标 (technical_analysis.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/{symbol}/indicators` | GET | get_all_indicators | technical_analysis.py | 获取股票的所有技术指标 |
| `/{symbol}/trend` | GET | get_trend_indicators | technical_analysis.py | 获取趋势类技术指标 |
| `/{symbol}/momentum` | GET | get_momentum_indicators | technical_analysis.py | 获取动量类技术指标 |
| `/{symbol}/volatility` | GET | get_volatility_indicators | technical_analysis.py | 获取波动率类技术指标 |
| `/{symbol}/volume` | GET | get_volume_indicators | technical_analysis.py | 获取成交量类技术指标 |
| `/{symbol}/signals` | GET | get_trading_signals | technical_analysis.py | 获取交易信号 |
| `/{symbol}/history` | GET | get_indicator_history | technical_analysis.py | 获取技术指标历史数据 |
| `/batch/indicators` | POST | batch_calculate_indicators | technical_analysis.py | 批量计算技术指标 |
| `/patterns/{symbol}` | GET | get_chart_patterns | technical_analysis.py | 获取图表形态分析 |

### 指标计算器 (indicators.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/registry` | GET | get_indicator_registry | indicators.py | 获取技术指标注册表 |
| `/registry/{category}` | GET | get_indicators_by_category | indicators.py | 按分类获取技术指标 |
| `/calculate` | POST | calculate_indicator | indicators.py | 计算技术指标 |
| `/configs` | POST | create_indicator_config | indicators.py | 创建指标配置 |
| `/configs` | GET | list_indicator_configs | indicators.py | 获取指标配置列表 |
| `/configs/{config_id}` | GET | get_indicator_config | indicators.py | 获取特定指标配置 |
| `/configs/{config_id}` | PUT | update_indicator_config | indicators.py | 更新指标配置 |
| `/configs/{config_id}` | DELETE | delete_indicator_config | indicators.py | 删除指标配置 |

### 仪表盘服务 (dashboard.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/api/dashboard/summary` | GET | get_dashboard_summary | dashboard.py | 获取仪表盘汇总数据 |
| `/api/dashboard/market-overview` | GET | get_market_overview | dashboard.py | 获取市场概览 |
| `/api/dashboard/health` | GET | health_check | dashboard.py | 仪表盘健康检查 |

### 自选股管理 (watchlist.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/` | GET | get_watchlist | watchlist.py | 获取自选股列表 |
| `/symbols` | GET | get_watchlist_symbols | watchlist.py | 获取自选股代码列表 |
| `/add` | POST | add_to_watchlist | watchlist.py | 添加股票到自选股 |
| `/remove/{symbol}` | DELETE | remove_from_watchlist | watchlist.py | 从自选股移除股票 |
| `/check/{symbol}` | GET | check_in_watchlist | watchlist.py | 检查股票是否在自选股中 |
| `/notes/{symbol}` | PUT | update_watchlist_notes | watchlist.py | 更新自选股备注 |
| `/count` | GET | get_watchlist_count | watchlist.py | 获取自选股数量 |
| `/clear` | DELETE | clear_watchlist | watchlist.py | 清空自选股 |
| `/groups` | GET | get_watchlist_groups | watchlist.py | 获取自选股分组 |
| `/groups` | POST | create_watchlist_group | watchlist.py | 创建自选股分组 |
| `/groups/{group_id}` | PUT | update_watchlist_group | watchlist.py | 更新自选股分组 |
| `/groups/{group_id}` | DELETE | delete_watchlist_group | watchlist.py | 删除自选股分组 |
| `/group/{group_id}` | GET | get_watchlist_by_group | watchlist.py | 按分组获取自选股 |
| `/move` | PUT | move_to_group | watchlist.py | 移动股票到分组 |
| `/with-groups` | GET | get_watchlist_with_groups | watchlist.py | 获取带分组信息的自选股 |

### 策略管理 (strategy_management.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/strategies` | GET | list_strategies | strategy_management.py | 获取策略列表 |
| `/strategies` | POST | create_strategy | strategy_management.py | 创建新策略 |
| `/strategies/{strategy_id}` | GET | get_strategy | strategy_management.py | 获取特定策略详情 |
| `/strategies/{strategy_id}` | PUT | update_strategy | strategy_management.py | 更新策略 |
| `/strategies/{strategy_id}` | DELETE | delete_strategy | strategy_management.py | 删除策略 |
| `/models/train` | POST | train_model | strategy_management.py | 训练模型 |
| `/models/training/{task_id}/status` | GET | get_training_status | strategy_management.py | 获取模型训练状态 |
| `/models` | GET | list_models | strategy_management.py | 获取模型列表 |
| `/backtest/run` | POST | run_backtest | strategy_management.py | 运行回测 |
| `/backtest/results` | GET | list_backtest_results | strategy_management.py | 获取回测结果列表 |
| `/backtest/results/{backtest_id}` | GET | get_backtest_result | strategy_management.py | 获取特定回测结果 |
| `/backtest/results/{backtest_id}/chart-data` | GET | get_backtest_chart_data | strategy_management.py | 获取回测图表数据 |

### 策略执行 (strategy.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/definitions` | GET | get_strategy_definitions | strategy.py | 获取策略定义列表 |
| `/run/single` | POST | run_single_strategy | strategy.py | 运行单个策略 |
| `/run/batch` | POST | run_batch_strategies | strategy.py | 批量运行策略 |
| `/results` | GET | get_strategy_results | strategy.py | 获取策略执行结果 |
| `/matched-stocks` | GET | get_matched_stocks | strategy.py | 获取匹配的股票 |
| `/stats/summary` | GET | get_strategy_stats_summary | strategy.py | 获取策略统计汇总 |

### 系统管理 (system.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/health` | GET | health_check | system.py | 系统健康检查 |
| `/adapters/health` | GET | get_adapters_health | system.py | 获取适配器健康状态 |
| `/datasources` | GET | get_datasources | system.py | 获取数据源列表 |
| `/test-connection` | POST | test_connection | system.py | 测试连接 |
| `/logs` | GET | get_logs | system.py | 获取系统日志 |
| `/logs/summary` | GET | get_logs_summary | system.py | 获取日志摘要 |
| `/architecture` | GET | get_architecture | system.py | 获取系统架构信息 |
| `/database/health` | GET | get_database_health | system.py | 数据库健康检查 |
| `/database/stats` | GET | get_database_stats | system.py | 数据库统计信息 |

### 通知服务 (notification.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/status` | GET | get_notification_status | notification.py | 获取通知服务状态 |
| `/email/send` | POST | send_email | notification.py | 发送邮件 |
| `/email/welcome` | POST | send_welcome_email | notification.py | 发送欢迎邮件 |
| `/email/newsletter` | POST | send_newsletter | notification.py | 发送订阅邮件 |
| `/email/price-alert` | POST | send_price_alert | notification.py | 发送价格预警邮件 |
| `/test-email` | POST | test_email_service | notification.py | 测试邮件服务 |

### 缓存管理 (cache.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/status` | GET | get_cache_status | cache.py | 获取缓存状态 |
| `/{symbol}/{data_type}` | GET | get_cached_data | cache.py | 获取缓存数据 |
| `/{symbol}/{data_type}` | POST | cache_data | cache.py | 缓存数据 |
| `/{symbol}` | DELETE | delete_cached_symbol | cache.py | 删除特定股票缓存 |
| `/` | DELETE | clear_all_cache | cache.py | 清空所有缓存 |
| `/{symbol}/{data_type}/fresh` | GET | get_fresh_data | cache.py | 获取新数据（绕过缓存） |
| `/evict/manual` | POST | manual_eviction | cache.py | 手动缓存淘汰 |
| `/eviction/stats` | GET | get_eviction_stats | cache.py | 获取缓存淘汰统计 |
| `/prewarming/trigger` | POST | trigger_prewarming | cache.py | 触发缓存预热 |
| `/prewarming/status` | GET | get_prewarming_status | cache.py | 获取缓存预热状态 |
| `/monitoring/metrics` | GET | get_cache_metrics | cache.py | 获取缓存监控指标 |
| `/monitoring/health` | GET | get_cache_health | cache.py | 缓存健康检查 |

### 备份与恢复 (backup_recovery.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/backup/tdengine/full` | POST | backup_tdengine_full | backup_recovery.py | TDengine完整备份 |
| `/backup/tdengine/incremental` | POST | backup_tdengine_incremental | backup_recovery.py | TDengine增量备份 |
| `/backup/postgresql/full` | POST | backup_postgresql_full | backup_recovery.py | PostgreSQL完整备份 |
| `/backups` | GET | list_backups | backup_recovery.py | 获取备份列表 |
| `/recovery/tdengine/full` | POST | recovery_tdengine_full | backup_recovery.py | TDengine完整恢复 |
| `/recovery/tdengine/pitr` | POST | recovery_tdengine_pitr | backup_recovery.py | TDengine时间点恢复 |
| `/recovery/postgresql/full` | POST | recovery_postgresql_full | backup_recovery.py | PostgreSQL完整恢复 |
| `/recovery/objectives` | GET | get_recovery_objectives | backup_recovery.py | 获取恢复目标 |
| `/scheduler/start` | POST | start_backup_scheduler | backup_recovery.py | 启动备份调度器 |
| `/scheduler/stop` | POST | stop_backup_scheduler | backup_recovery.py | 停止备份调度器 |
| `/scheduler/jobs` | GET | list_backup_jobs | backup_recovery.py | 获取备份任务列表 |
| `/integrity/verify/{backup_id}` | GET | verify_backup_integrity | backup_recovery.py | 验证备份完整性 |
| `/cleanup/old-backups` | POST | cleanup_old_backups | backup_recovery.py | 清理旧备份 |

### 数据质量监控 (data_quality.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/health` | GET | health_check | data_quality.py | 数据质量服务健康检查 |
| `/metrics` | GET | get_quality_metrics | data_quality.py | 获取数据质量指标 |
| `/alerts` | GET | get_quality_alerts | data_quality.py | 获取数据质量告警 |
| `/alerts/{alert_id}/acknowledge` | POST | acknowledge_alert | data_quality.py | 确认数据质量告警 |
| `/alerts/{alert_id}/resolve` | POST | resolve_alert | data_quality.py | 解决数据质量告警 |
| `/config/mode` | GET | get_quality_mode | data_quality.py | 获取数据质量模式 |
| `/status/overview` | GET | get_quality_overview | data_quality.py | 获取数据质量概览 |
| `/test/quality` | POST | test_data_quality | data_quality.py | 测试数据质量 |
| `/metrics/trends` | GET | get_quality_trends | data_quality.py | 获取数据质量趋势 |

### 健康检查服务 (health.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/health` | GET | health_check | health.py | 基础健康检查 |
| `/health/detailed` | GET | detailed_health_check | health.py | 详细健康检查 |
| `/reports/health/{timestamp}` | GET | get_health_report | health.py | 获取特定时间的健康报告 |

### 任务管理 (tasks.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/register` | POST | register_task | tasks.py | 注册新任务 |
| `/{task_id}` | DELETE | delete_task | tasks.py | 删除任务 |
| `/` | GET | list_tasks | tasks.py | 获取任务列表 |
| `/{task_id}` | GET | get_task | tasks.py | 获取特定任务 |
| `/{task_id}/start` | POST | start_task | tasks.py | 启动任务 |
| `/{task_id}/stop` | POST | stop_task | tasks.py | 停止任务 |
| `/executions/` | GET | list_executions | tasks.py | 获取任务执行列表 |
| `/executions/{execution_id}` | GET | get_execution | tasks.py | 获取特定任务执行 |
| `/statistics/` | GET | get_task_statistics | tasks.py | 获取任务统计 |
| `/import` | POST | import_tasks | tasks.py | 导入任务 |
| `/export` | POST | export_tasks | tasks.py | 导出任务 |
| `/executions/cleanup` | DELETE | cleanup_executions | tasks.py | 清理任务执行记录 |
| `/health` | GET | health_check | tasks.py | 任务管理健康检查 |

### 股票搜索 (stock_search.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/search` | GET | search_stocks | stock_search.py | 股票搜索 |
| `/quote/{symbol}` | GET | get_stock_quote | stock_search.py | 获取股票行情 |
| `/profile/{symbol}` | GET | get_stock_profile | stock_search.py | 获取股票档案 |
| `/news/{symbol}` | GET | get_stock_news | stock_search.py | 获取股票新闻 |
| `/news/market/{category}` | GET | get_market_news | stock_search.py | 获取市场新闻 |
| `/recommendation/{symbol}` | GET | get_stock_recommendation | stock_search.py | 获取股票推荐 |
| `/cache/clear` | POST | clear_search_cache | stock_search.py | 清理搜索缓存 |

### 机器学习服务 (ml.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/tdx/data` | POST | get_tdx_data | ml.py | 获取通达信数据 |
| `/tdx/stocks/{market}` | GET | get_tdx_stocks | ml.py | 获取通达信股票列表 |
| `/features/generate` | POST | generate_features | ml.py | 生成特征数据 |
| `/models/train` | POST | train_model | ml.py | 训练机器学习模型 |
| `/models/predict` | POST | predict | ml.py | 模型预测 |
| `/models` | GET | list_models | ml.py | 获取模型列表 |
| `/models/{model_name}` | GET | get_model_detail | ml.py | 获取模型详情 |
| `/models/evaluate` | POST | evaluate_model | ml.py | 评估模型 |

### 问财自然语言查询 (wencai.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/queries` | GET | get_wencai_queries | wencai.py | 获取问财查询历史 |
| `/query` | POST | execute_wencai_query | wencai.py | 执行问财查询 |
| `/templates` | GET | get_query_templates | wencai.py | 获取查询模板 |
| `/templates` | POST | create_query_template | wencai.py | 创建查询模板 |
| `/templates/{template_id}` | PUT | update_query_template | wencai.py | 更新查询模板 |
| `/templates/{template_id}` | DELETE | delete_query_template | wencai.py | 删除查询模板 |
| `/history` | GET | get_query_history | wencai.py | 获取查询历史 |
| `/analyze` | POST | analyze_query_intent | wencai.py | 分析查询意图 |
| `/health` | GET | health_check | wencai.py | 问财服务健康检查 |

### 监控服务 (monitoring.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/alert-rules` | GET | list_alert_rules | monitoring.py | 获取告警规则列表 |
| `/alert-rules` | POST | create_alert_rule | monitoring.py | 创建告警规则 |
| `/alert-rules/{rule_id}` | PUT | update_alert_rule | monitoring.py | 更新告警规则 |
| `/alert-rules/{rule_id}` | DELETE | delete_alert_rule | monitoring.py | 删除告警规则 |
| `/alerts` | GET | list_alerts | monitoring.py | 获取告警记录 |
| `/alerts/{alert_id}/mark-read` | POST | mark_alert_read | monitoring.py | 标记告警为已读 |
| `/alerts/mark-all-read` | POST | mark_all_alerts_read | monitoring.py | 标记所有告警为已读 |
| `/realtime/{symbol}` | GET | get_realtime_monitoring | monitoring.py | 获取实时监控数据 |
| `/realtime` | GET | list_realtime_monitoring | monitoring.py | 获取实时监控列表 |
| `/realtime/fetch` | POST | fetch_realtime_data | monitoring.py | 获取实时数据 |
| `/dragon-tiger` | GET | get_dragon_tiger_list | monitoring.py | 获取龙虎榜数据 |
| `/dragon-tiger/fetch` | POST | fetch_dragon_tiger_data | monitoring.py | 获取龙虎榜数据 |
| `/summary` | GET | get_monitoring_summary | monitoring.py | 获取监控汇总 |
| `/stats/today` | GET | get_today_stats | monitoring.py | 获取今日统计 |
| `/control/start` | POST | start_monitoring | monitoring.py | 启动监控 |
| `/control/stop` | POST | stop_monitoring | monitoring.py | 停止监控 |
| `/control/status` | GET | get_monitoring_status | monitoring.py | 获取监控状态 |

### 风险管理 (risk_management.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/var-cvar` | GET | get_var_cvar | risk_management.py | 获取VaR和CVaR风险指标 |
| `/beta` | GET | get_beta | risk_management.py | 获取贝塔系数 |
| `/dashboard` | GET | get_risk_dashboard | risk_management.py | 获取风险管理仪表盘 |
| `/metrics/history` | GET | get_risk_metrics_history | risk_management.py | 获取风险指标历史 |
| `/alerts` | GET | get_risk_alerts | risk_management.py | 获取风险告警 |
| `/alerts` | POST | create_risk_alert | risk_management.py | 创建风险告警 |
| `/alerts/{alert_id}` | PUT | update_risk_alert | risk_management.py | 更新风险告警 |
| `/alerts/{alert_id}` | DELETE | delete_risk_alert | risk_management.py | 删除风险告警 |
| `/notifications/test` | POST | test_risk_notification | risk_management.py | 测试风险通知 |

### 多数据源管理 (multi_source.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/health` | GET | get_multi_source_health | multi_source.py | 获取多数据源健康状态 |
| `/health/{source_type}` | GET | get_source_health | multi_source.py | 获取特定数据源健康状态 |
| `/realtime-quote` | GET | get_realtime_quote | multi_source.py | 获取实时行情 |
| `/fund-flow` | GET | get_fund_flow_multi | multi_source.py | 获取多源资金流向 |
| `/dragon-tiger` | GET | get_dragon_tiger_multi | multi_source.py | 获取多源龙虎榜 |
| `/refresh-health` | POST | refresh_health_status | multi_source.py | 刷新健康状态 |
| `/clear-cache` | POST | clear_source_cache | multi_source.py | 清理数据源缓存 |
| `/supported-categories` | GET | get_supported_categories | multi_source.py | 获取支持的分类 |

### 指标服务 (metrics.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/metrics` | GET | get_metrics | metrics.py | 获取系统指标 |

### 公告管理 (announcement.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/fetch` | POST | fetch_announcements | announcement.py | 获取公告数据 |
| `/list` | GET | list_announcements | announcement.py | 获取公告列表 |
| `/today` | GET | get_today_announcements | announcement.py | 获取今日公告 |
| `/important` | GET | get_important_announcements | announcement.py | 获取重要公告 |
| `/stock/{stock_code}` | GET | get_stock_announcements | announcement.py | 获取股票公告 |
| `/monitor/evaluate` | POST | evaluate_monitor_rules | announcement.py | 评估监控规则 |
| `/stats` | GET | get_announcement_stats | announcement.py | 获取公告统计 |
| `/types` | GET | get_announcement_types | announcement.py | 获取公告类型 |
| `/monitor-rules` | GET | get_monitor_rules | announcement.py | 获取监控规则 |
| `/monitor-rules` | POST | create_monitor_rule | announcement.py | 创建监控规则 |
| `/monitor-rules/{rule_id}` | PUT | update_monitor_rule | announcement.py | 更新监控规则 |
| `/monitor-rules/{rule_id}` | DELETE | delete_monitor_rule | announcement.py | 删除监控规则 |
| `/triggered-records` | GET | get_triggered_records | announcement.py | 获取触发记录 |

### SSE端点 (sse_endpoints.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/sse/status` | GET | sse_status | sse_endpoints.py | SSE连接状态 |

### 连接池监控 (v1/pool_monitoring.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/postgresql/stats` | GET | get_postgresql_pool_stats | v1/pool_monitoring.py | PostgreSQL连接池统计 |
| `/tdengine/stats` | GET | get_tdengine_pool_stats | v1/pool_monitoring.py | TDengine连接池统计 |
| `/health` | GET | pool_health_check | v1/pool_monitoring.py | 连接池综合健康检查 |
| `/alerts` | GET | get_pool_alerts | v1/pool_monitoring.py | 连接池告警检测 |

### 行业概念分析 (industry_concept_analysis.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/industry/list` | GET | get_industry_list | industry_concept_analysis.py | 获取行业列表 |
| `/concept/list` | GET | get_concept_list | industry_concept_analysis.py | 获取概念列表 |
| `/industry/stocks` | GET | get_industry_stocks | industry_concept_analysis.py | 获取行业股票 |
| `/concept/stocks` | GET | get_concept_stocks | industry_concept_analysis.py | 获取概念股票 |
| `/industry/performance` | GET | get_industry_performance | industry_concept_analysis.py | 获取行业表现 |

### 通达信数据 (tdx.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/stock-list` | GET | get_tdx_stock_list | tdx.py | 获取通达信股票列表 |
| `/realtime-data` | GET | get_tdx_realtime_data | tdx.py | 获取通达信实时数据 |
| `/kline-data` | GET | get_tdx_kline_data | tdx.py | 获取通达信K线数据 |

### 交易接口 (trade/routes.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/health` | GET | health_check | trade/routes.py | 交易服务健康检查 |
| `/portfolio` | GET | get_portfolio | trade/routes.py | 获取投资组合 |
| `/positions` | GET | get_positions | trade/routes.py | 获取持仓信息 |
| `/trades` | GET | get_trades | trade/routes.py | 获取交易记录 |
| `/statistics` | GET | get_trade_statistics | trade/routes.py | 获取交易统计 |
| `/execute` | POST | execute_trade | trade/routes.py | 执行交易 |

### WebSocket回测 (backtest_ws.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/status` | GET | get_backtest_status | backtest_ws.py | 获取回测状态 |

### TradingView集成 (tradingview.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/chart/config` | POST | configure_chart | tradingview.py | 配置图表 |
| `/mini-chart/config` | POST | configure_mini_chart | tradingview.py | 配置迷你图表 |
| `/ticker-tape/config` | POST | configure_ticker_tape | tradingview.py | 配置跑马灯 |
| `/market-overview/config` | GET | get_market_overview_config | tradingview.py | 获取市场概览配置 |
| `/screener/config` | GET | get_screener_config | tradingview.py | 获取筛选器配置 |
| `/symbol/convert` | GET | convert_symbol | tradingview.py | 转换股票代码 |

### Prometheus导出器 (prometheus_exporter.py)

| 端点URL | HTTP方法 | 函数名 | 文件路径 | 功能描述 |
|---------|----------|--------|----------|----------|
| `/metrics` | GET | export_metrics | prometheus_exporter.py | 导出Prometheus指标 |

## 前缀说明

所有API端点都注册在FastAPI应用中，大部分使用`APIRouter`前缀：

- **主应用端点**: 无前缀（如 `/health`）
- **认证模块**: `/api/auth`
- **数据查询**: `/api/data`
- **市场数据**: `/api/market`
- **技术分析**: `/api/technical`
- **仪表盘**: `/api/dashboard`
- **策略管理**: `/api/strategy`
- **自选股**: `/api/watchlist`
- **系统管理**: `/api/system`
- **缓存管理**: `/api/cache`
- **备份恢复**: `/api/backup-recovery`
- **数据质量**: `/api/data-quality`
- **任务管理**: `/api/tasks`
- **监控服务**: `/api/monitoring`
- **风险管理**: `/api/risk-management`
- **多数据源**: `/api/multi-source`

## 认证说明

大部分API端点需要JWT认证，以下端点无需认证：

- `/health` - 系统健康检查
- `/login` - 用户登录
- `/test/factory` - 数据源工厂测试
- `/api/csrf-token` - CSRF令牌获取
- `/` - 根路径

## 响应格式

API响应采用统一格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2025-12-02T10:00:00Z",
  "request_id": "uuid"
}
```

错误响应格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  },
  "timestamp": "2025-12-02T10:00:00Z",
  "request_id": "uuid"
}
```

## API文档访问

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

**文档更新时间**: 2025-12-02
**版本**: 1.0
**项目**: MyStocks量化交易数据管理系统
