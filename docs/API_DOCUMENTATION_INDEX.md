# MyStocks API Documentation Index

**Generated**: 2025-10-30
**Total Endpoints**: 121

---

## Table of Contents

- [API](#api): 121 endpoints


---

## Critical Lessons from BUG-NEW-002

### Multiple Fund-Flow Endpoint Versions

During BUG-NEW-002 investigation, we discovered **3 different fund-flow endpoints** across different API versions. This caused confusion and delays in finding the correct endpoint.

#### ✅ CURRENT (Recommended)
- **Endpoint**: `GET /api/market/v3/fund-flow`
- **Module**: `market_v3.py`
- **Status**: ✅ Active, PostgreSQL-backed, Week 3 architecture
- **Parameters**: 
  - `industry_type`: csrc | sw_l1 | sw_l2
  - `trade_date`: Optional (defaults to latest)
  - `limit`: 1-100 (default: 20)
- **Use Case**: Dashboard fund flow panel, production use

#### ⚠️ LEGACY (Avoid)
- **Endpoint**: `GET /api/market/fund-flow` (market.py)
  - Status: Legacy, may use different database
  - Recommendation: Migrate to v3

- **Endpoint**: `GET /api/market-v2/fund-flow` (market_v2.py)
  - Status: V2 version, East Money Finance direct API
  - Recommendation: Use v3 for consistency

### Quick Search Guide

**If you need fund flow data**:
1. Use `/api/market/v3/fund-flow` (PostgreSQL, current architecture)
2. Avoid legacy `/api/market/fund-flow` endpoints

**If you need dragon-tiger (龙虎榜) data**:
1. Use `/api/market/v3/dragon-tiger`

**If you need ETF data**:
1. Use `/api/market/v3/etf-data`

**If you need chip race (竞价抢筹) data**:
1. Use `/api/market/v3/chip-race`

---

---

## Quick Reference

| Method | Endpoint | Description | Module |
|--------|----------|-------------|--------|
| POST   | `/api/announcement/fetch` | 从数据源获取并保存公告 | `announcement` |
| GET    | `/api/announcement/important` | 获取重要公告 | `announcement` |
| GET    | `/api/announcement/list` | 查询公告列表 | `announcement` |
| POST   | `/api/announcement/monitor/evaluate` | 评估所有监控规则 | `announcement` |
| GET    | `/api/announcement/stats` | 获取公告统计信息 | `announcement` |
| GET    | `/api/announcement/stock/{stock_code}` | 获取指定股票的公告 | `announcement` |
| GET    | `/api/announcement/today` | 获取今日公告 | `announcement` |
| GET    | `/api/announcement/types` | 获取支持的公告类型 | `announcement` |
| POST   | `/api/auth/logout` | 用户登出 | `auth` |
| POST   | `/api/auth/mfa/backup-codes/regenerate` | Regenerate backup codes for TOTP | `mfa` |
| GET    | `/api/auth/mfa/methods` | Get available MFA methods | `mfa` |
| POST   | `/api/auth/mfa/setup/{method}` | Setup MFA method for current user | `mfa` |
| GET    | `/api/auth/mfa/status` | Get MFA status for current user | `mfa` |
| POST   | `/api/auth/mfa/verify` | Verify MFA code during login | `mfa` |
| POST   | `/api/auth/mfa/verify-setup/{method}` | Verify and confirm MFA setup | `mfa` |
| DELETE | `/api/auth/mfa/{method}` | Disable MFA method for current user | `mfa` |
| GET    | `/api/auth/oauth2/available-providers` | 获取可用的 OAuth2 提供商列表 | `oauth2` |
| POST   | `/api/auth/oauth2/link/{provider}` | 关联 OAuth2 账户到现有用户 | `oauth2` |
| GET    | `/api/auth/oauth2/{provider}` | OAuth2 登录重定向端点 | `oauth2` |
| GET    | `/api/auth/oauth2/{provider}/callback` | OAuth2 回调端点 | `oauth2` |
| POST   | `/api/auth/refresh` | 刷新访问令牌 | `auth` |
| GET    | `/api/auth/users` | 获取用户列表（仅管理员） | `auth` |
| GET    | `/api/data/dashboard/favorites` | 获取自选股列表 | `dashboard` |
| GET    | `/api/data/dashboard/fund-flow` | 获取资金流向数据 | `dashboard` |
| GET    | `/api/data/dashboard/industry-stocks` | 获取行业股票列表 | `dashboard` |
| GET    | `/api/data/dashboard/strategy-matches` | 获取策略匹配股票 | `dashboard` |
| GET    | `/api/data/dashboard/summary` | 获取仪表板汇总数据 (Graceful degradation: returns partial data on err... | `dashboard` |
| GET    | `/api/data/financial` | 获取股票财务数据 | `data` |
| GET    | `/api/data/kline` | 获取股票K线数据（stocks/daily的别名） | `data` |
| GET    | `/api/data/markets/overview` | 获取市场概览数据 | `data` |

*Showing 30 of 121 endpoints. See detailed sections below for complete list.*

---

## API

**Endpoints**: 121

### POST `/api/announcement/fetch`

**Description**: 从数据源获取并保存公告

- **Module**: `announcement.py`
- **Function**: `fetch_announcements()`

### GET `/api/announcement/important`

**Description**: 获取重要公告

- **Module**: `announcement.py`
- **Function**: `get_important_announcements()`

### GET `/api/announcement/list`

**Description**: 查询公告列表

- **Module**: `announcement.py`
- **Function**: `get_announcements()`

### POST `/api/announcement/monitor/evaluate`

**Description**: 评估所有监控规则

- **Module**: `announcement.py`
- **Function**: `evaluate_monitor_rules()`

### GET `/api/announcement/stats`

**Description**: 获取公告统计信息

- **Module**: `announcement.py`
- **Function**: `get_announcement_stats()`

### GET `/api/announcement/stock/{stock_code}`

**Description**: 获取指定股票的公告

- **Module**: `announcement.py`
- **Function**: `get_stock_announcements()`

### GET `/api/announcement/today`

**Description**: 获取今日公告

- **Module**: `announcement.py`
- **Function**: `get_today_announcements()`

### GET `/api/announcement/types`

**Description**: 获取支持的公告类型

- **Module**: `announcement.py`
- **Function**: `get_announcement_types()`

### POST `/api/auth/logout`

**Description**: 用户登出

- **Module**: `auth.py`
- **Function**: `logout()`

### POST `/api/auth/mfa/backup-codes/regenerate`

**Description**: Regenerate backup codes for TOTP

- **Module**: `mfa.py`
- **Function**: `regenerate_backup_codes()`

### GET `/api/auth/mfa/methods`

**Description**: Get available MFA methods

- **Module**: `mfa.py`
- **Function**: `get_mfa_methods()`

### POST `/api/auth/mfa/setup/{method}`

**Description**: Setup MFA method for current user

- **Module**: `mfa.py`
- **Function**: `setup_mfa()`

### GET `/api/auth/mfa/status`

**Description**: Get MFA status for current user

- **Module**: `mfa.py`
- **Function**: `get_mfa_status()`

### POST `/api/auth/mfa/verify`

**Description**: Verify MFA code during login

- **Module**: `mfa.py`
- **Function**: `verify_mfa_code()`

### POST `/api/auth/mfa/verify-setup/{method}`

**Description**: Verify and confirm MFA setup

- **Module**: `mfa.py`
- **Function**: `verify_mfa_setup()`

### DELETE `/api/auth/mfa/{method}`

**Description**: Disable MFA method for current user

- **Module**: `mfa.py`
- **Function**: `disable_mfa()`

### GET `/api/auth/oauth2/available-providers`

**Description**: 获取可用的 OAuth2 提供商列表

- **Module**: `oauth2.py`
- **Function**: `get_available_providers()`

### POST `/api/auth/oauth2/link/{provider}`

**Description**: 关联 OAuth2 账户到现有用户

- **Module**: `oauth2.py`
- **Function**: `link_oauth2_account()`

### GET `/api/auth/oauth2/{provider}`

**Description**: OAuth2 登录重定向端点

- **Module**: `oauth2.py`
- **Function**: `oauth2_login()`

### GET `/api/auth/oauth2/{provider}/callback`

**Description**: OAuth2 回调端点

- **Module**: `oauth2.py`
- **Function**: `oauth2_callback()`

### POST `/api/auth/refresh`

**Description**: 刷新访问令牌

- **Module**: `auth.py`
- **Function**: `refresh_token()`

### GET `/api/auth/users`

**Description**: 获取用户列表（仅管理员）

- **Module**: `auth.py`
- **Function**: `get_users()`

### GET `/api/data/dashboard/favorites`

**Description**: 获取自选股列表

- **Module**: `dashboard.py`
- **Function**: `get_dashboard_favorites()`

### GET `/api/data/dashboard/fund-flow`

**Description**: 获取资金流向数据

- **Module**: `dashboard.py`
- **Function**: `get_dashboard_fund_flow()`

### GET `/api/data/dashboard/industry-stocks`

**Description**: 获取行业股票列表

- **Module**: `dashboard.py`
- **Function**: `get_dashboard_industry_stocks()`

### GET `/api/data/dashboard/strategy-matches`

**Description**: 获取策略匹配股票

- **Module**: `dashboard.py`
- **Function**: `get_dashboard_strategy_matches()`

### GET `/api/data/dashboard/summary`

**Description**: 获取仪表板汇总数据 (Graceful degradation: returns partial data on errors)

- **Module**: `dashboard.py`
- **Function**: `get_dashboard_summary()`

### GET `/api/data/financial`

**Description**: 获取股票财务数据

- **Module**: `data.py`
- **Function**: `get_financial_data()`

### GET `/api/data/kline`

**Description**: 获取股票K线数据（stocks/daily的别名）

- **Module**: `data.py`
- **Function**: `get_kline()`

### GET `/api/data/markets/overview`

**Description**: 获取市场概览数据

- **Module**: `data.py`
- **Function**: `get_market_overview()`

### GET `/api/data/stocks/basic`

**Description**: 获取股票基本信息列表

- **Module**: `data.py`
- **Function**: `get_stocks_basic()`

### GET `/api/data/stocks/daily`

**Description**: 获取股票日线数据

- **Module**: `data.py`
- **Function**: `get_daily_kline()`

### GET `/api/data/stocks/search`

**Description**: 股票搜索接口

- **Module**: `data.py`
- **Function**: `search_stocks()`

### GET `/api/market/v3/chip-race`

**Description**: 获取竞价抢筹数据

- **Module**: `market_v3.py`
- **Function**: `get_chip_race_data()`

### GET `/api/market/v3/dragon-tiger`

**Description**: 获取龙虎榜数据

- **Module**: `market_v3.py`
- **Function**: `get_dragon_tiger_data()`

### GET `/api/market/v3/etf-data`

**Description**: 获取ETF实时数据

- **Module**: `market_v3.py`
- **Function**: `get_etf_data()`

### GET `/api/market/v3/fund-flow`

**Description**: 获取行业资金流向数据（PostgreSQL版本）

- **Module**: `market_v3.py`
- **Function**: `get_fund_flow_data()`

### GET `/api/metrics`

**Description**: Prometheus metrics端点

- **Module**: `metrics.py`
- **Function**: `metrics()`

### DELETE `/api/monitoring/alert-rules/{rule_id}`

**Description**: 删除告警规则

- **Module**: `monitoring.py`
- **Function**: `delete_alert_rule()`

### POST `/api/monitoring/alerts/mark-all-read`

**Description**: 批量标记所有未读告警为已读

- **Module**: `monitoring.py`
- **Function**: `mark_all_alerts_read()`

### POST `/api/monitoring/alerts/{alert_id}/mark-read`

**Description**: 标记告警为已读

- **Module**: `monitoring.py`
- **Function**: `mark_alert_read()`

### POST `/api/monitoring/control/start`

**Description**: 启动监控

- **Module**: `monitoring.py`
- **Function**: `start_monitoring()`

### GET `/api/monitoring/control/status`

**Description**: 获取监控状态

- **Module**: `monitoring.py`
- **Function**: `get_monitoring_status()`

### POST `/api/monitoring/control/stop`

**Description**: 停止监控

- **Module**: `monitoring.py`
- **Function**: `stop_monitoring()`

### POST `/api/monitoring/dragon-tiger/fetch`

**Description**: 手动触发获取龙虎榜数据

- **Module**: `monitoring.py`
- **Function**: `fetch_dragon_tiger_data()`

### POST `/api/monitoring/realtime/fetch`

**Description**: 手动触发获取实时数据

- **Module**: `monitoring.py`
- **Function**: `fetch_realtime_data()`

### GET `/api/monitoring/stats/today`

**Description**: 获取今日统计数据

- **Module**: `monitoring.py`
- **Function**: `get_today_statistics()`

### POST `/api/multi-source/clear-cache`

**Description**: 清空数据缓存

- **Module**: `multi_source.py`
- **Function**: `clear_cache()`

### GET `/api/multi-source/dragon-tiger`

**Description**: 获取龙虎榜（支持多数据源）

- **Module**: `multi_source.py`
- **Function**: `fetch_dragon_tiger()`

### GET `/api/multi-source/fund-flow`

**Description**: 获取资金流向（支持多数据源）

- **Module**: `multi_source.py`
- **Function**: `fetch_fund_flow()`

### GET `/api/multi-source/health/{source_type}`

**Description**: 获取指定数据源的健康状态

- **Module**: `multi_source.py`
- **Function**: `get_data_source_health()`

### GET `/api/multi-source/realtime-quote`

**Description**: 获取实时行情（支持多数据源）

- **Module**: `multi_source.py`
- **Function**: `fetch_realtime_quote()`

### POST `/api/multi-source/refresh-health`

**Description**: 刷新所有数据源的健康状态

- **Module**: `multi_source.py`
- **Function**: `refresh_data_source_health()`

### GET `/api/multi-source/supported-categories`

**Description**: 获取所有支持的数据类别及其对应的数据源

- **Module**: `multi_source.py`
- **Function**: `get_supported_categories()`

### POST `/api/notification/email/newsletter`

**Description**: 发送每日新闻简报

- **Module**: `notification.py`
- **Function**: `send_daily_newsletter()`

### POST `/api/notification/email/price-alert`

**Description**: 发送价格提醒邮件

- **Module**: `notification.py`
- **Function**: `send_price_alert()`

### POST `/api/notification/email/send`

**Description**: 发送邮件（需要管理员权限）

- **Module**: `notification.py`
- **Function**: `send_email()`

### POST `/api/notification/email/welcome`

**Description**: 发送欢迎邮件

- **Module**: `notification.py`
- **Function**: `send_welcome_email()`

### GET `/api/notification/status`

**Description**: 获取邮件服务状态

- **Module**: `notification.py`
- **Function**: `get_email_service_status()`

### POST `/api/notification/test-email`

**Description**: 发送测试邮件到当前用户邮箱

- **Module**: `notification.py`
- **Function**: `send_test_email()`

### POST `/api/stock-search/cache/clear`

**Description**: 清除搜索缓存

- **Module**: `stock_search.py`
- **Function**: `clear_search_cache()`

### GET `/api/stock-search/profile/{symbol}`

**Description**: 获取公司基本信息（暂不支持）

- **Module**: `stock_search.py`
- **Function**: `get_company_profile()`

### GET `/api/stock-search/recommendation/{symbol}`

**Description**: 获取分析师推荐趋势（暂不支持）

- **Module**: `stock_search.py`
- **Function**: `get_recommendation_trends()`

### GET `/api/system/adapters/health`

**Description**: 🚀 适配器健康检查端点（新增）

- **Module**: `system.py`
- **Function**: `get_adapters_health()`

### GET `/api/system/architecture`

**Description**: 获取系统架构信息 (Week 3简化后 - 双数据库架构)

- **Module**: `system.py`
- **Function**: `get_system_architecture()`

### GET `/api/system/database/health`

**Description**: 数据库健康检查 (US2 - 双数据库架构)

- **Module**: `system.py`
- **Function**: `database_health()`

### GET `/api/system/database/stats`

**Description**: 数据库统计信息 (US2 - 双数据库架构)

- **Module**: `system.py`
- **Function**: `database_stats()`

### GET `/api/system/datasources`

**Description**: 获取已配置的数据源列表

- **Module**: `system.py`
- **Function**: `get_datasources()`

### GET `/api/system/health`

**Description**: 系统健康检查端点

- **Module**: `system.py`
- **Function**: `system_health()`

### GET `/api/system/logs/summary`

**Description**: 获取日志统计摘要

- **Module**: `system.py`
- **Function**: `get_logs_summary()`

### DELETE `/api/tasks/executions/cleanup`

**Description**: 清理旧的执行记录

- **Module**: `tasks.py`
- **Function**: `cleanup_executions()`

### POST `/api/tasks/export`

**Description**: 导出任务配置

- **Module**: `tasks.py`
- **Function**: `export_config()`

### GET `/api/tasks/health`

**Description**: 任务管理器健康检查

- **Module**: `tasks.py`
- **Function**: `health_check()`

### POST `/api/technical/batch/indicators`

**Description**: 批量获取多只股票的技术指标

- **Module**: `technical_analysis.py`
- **Function**: `get_batch_indicators()`

### GET `/api/technical/patterns/{symbol}`

**Description**: 检测技术形态 (预留功能)

- **Module**: `technical_analysis.py`
- **Function**: `detect_patterns()`

### GET `/api/technical/{symbol}/history`

**Description**: 获取股票历史行情数据

- **Module**: `technical_analysis.py`
- **Function**: `get_stock_history()`

### POST `/api/tradingview/chart/config`

**Description**: 获取 TradingView 图表配置

- **Module**: `tradingview.py`
- **Function**: `get_chart_config()`

### GET `/api/tradingview/market-overview/config`

**Description**: 获取 TradingView 市场概览配置

- **Module**: `tradingview.py`
- **Function**: `get_market_overview_config()`

### POST `/api/tradingview/mini-chart/config`

**Description**: 获取 TradingView 迷你图表配置

- **Module**: `tradingview.py`
- **Function**: `get_mini_chart_config()`

### GET `/api/tradingview/screener/config`

**Description**: 获取 TradingView 股票筛选器配置

- **Module**: `tradingview.py`
- **Function**: `get_screener_config()`

### GET `/api/tradingview/symbol/convert`

**Description**: 将股票代码转换为 TradingView 格式

- **Module**: `tradingview.py`
- **Function**: `convert_symbol()`

### POST `/api/tradingview/ticker-tape/config`

**Description**: 获取 TradingView Ticker Tape 配置

- **Module**: `tradingview.py`
- **Function**: `get_ticker_tape_config()`

### GET `/api/v1/risk/alerts`

**Description**: 获取风险预警规则列表

- **Module**: `risk_management.py`
- **Function**: `list_risk_alerts()`

### POST `/api/v1/risk/alerts`

**Description**: 创建风险预警规则

- **Module**: `risk_management.py`
- **Function**: `create_risk_alert()`

### PUT `/api/v1/risk/alerts/{alert_id}`

**Description**: 更新风险预警规则

- **Module**: `risk_management.py`
- **Function**: `update_risk_alert()`

### DELETE `/api/v1/risk/alerts/{alert_id}`

**Description**: 删除风险预警规则（软删除：设置为非活跃）

- **Module**: `risk_management.py`
- **Function**: `delete_risk_alert()`

### GET `/api/v1/risk/beta`

**Description**: 计算Beta系数

- **Module**: `risk_management.py`
- **Function**: `calculate_beta()`

### GET `/api/v1/risk/dashboard`

**Description**: 获取风险仪表盘数据

- **Module**: `risk_management.py`
- **Function**: `get_risk_dashboard()`

### GET `/api/v1/risk/metrics/history`

**Description**: 获取风险指标历史数据

- **Module**: `risk_management.py`
- **Function**: `get_risk_metrics_history()`

### POST `/api/v1/risk/notifications/test`

**Description**: 发送测试通知

- **Module**: `risk_management.py`
- **Function**: `test_notification()`

### GET `/api/v1/risk/var-cvar`

**Description**: 计算VaR和CVaR

- **Module**: `risk_management.py`
- **Function**: `calculate_var_cvar()`

### GET `/api/v1/sse/alerts`

**Description**: SSE endpoint for risk alert notifications

- **Module**: `sse_endpoints.py`
- **Function**: `sse_alerts_stream()`

### GET `/api/v1/sse/backtest`

**Description**: SSE endpoint for backtest execution progress updates

- **Module**: `sse_endpoints.py`
- **Function**: `sse_backtest_stream()`

### GET `/api/v1/sse/dashboard`

**Description**: SSE endpoint for real-time dashboard updates

- **Module**: `sse_endpoints.py`
- **Function**: `sse_dashboard_stream()`

### GET `/api/v1/sse/status`

**Description**: Get SSE server status

- **Module**: `sse_endpoints.py`
- **Function**: `sse_status()`

### GET `/api/v1/sse/training`

**Description**: SSE endpoint for model training progress updates

- **Module**: `sse_endpoints.py`
- **Function**: `sse_training_stream()`

### GET `/api/v1/strategy/backtest/results`

**Description**: 获取回测结果列表

- **Module**: `strategy_management.py`
- **Function**: `list_backtest_results()`

### GET `/api/v1/strategy/backtest/results/{backtest_id}`

**Description**: 获取回测详细结果

- **Module**: `strategy_management.py`
- **Function**: `get_backtest_result()`

### GET `/api/v1/strategy/backtest/results/{backtest_id}/chart-data`

**Description**: 获取回测图表数据

- **Module**: `strategy_management.py`
- **Function**: `get_backtest_chart_data()`

### POST `/api/v1/strategy/backtest/run`

**Description**: 执行回测

- **Module**: `strategy_management.py`
- **Function**: `run_backtest()`

### GET `/api/v1/strategy/models`

**Description**: 获取模型列表

- **Module**: `strategy_management.py`
- **Function**: `list_models()`

### POST `/api/v1/strategy/models/train`

**Description**: 启动模型训练任务

- **Module**: `strategy_management.py`
- **Function**: `train_model()`

### GET `/api/v1/strategy/models/training/{task_id}/status`

**Description**: 查询训练状态

- **Module**: `strategy_management.py`
- **Function**: `get_training_status()`

### GET `/api/v1/strategy/strategies`

**Description**: 获取策略列表

- **Module**: `strategy_management.py`
- **Function**: `list_strategies()`

### POST `/api/v1/strategy/strategies`

**Description**: 创建新策略

- **Module**: `strategy_management.py`
- **Function**: `create_strategy()`

### GET `/api/v1/strategy/strategies/{strategy_id}`

**Description**: 获取策略详情

- **Module**: `strategy_management.py`
- **Function**: `get_strategy()`

### PUT `/api/v1/strategy/strategies/{strategy_id}`

**Description**: 更新策略

- **Module**: `strategy_management.py`
- **Function**: `update_strategy()`

### DELETE `/api/v1/strategy/strategies/{strategy_id}`

**Description**: 删除策略

- **Module**: `strategy_management.py`
- **Function**: `delete_strategy()`

### POST `/api/watchlist/add`

**Description**: 添加股票到自选股列表

- **Module**: `watchlist.py`
- **Function**: `add_to_watchlist()`

### GET `/api/watchlist/check/{symbol}`

**Description**: 检查股票是否在自选股列表中

- **Module**: `watchlist.py`
- **Function**: `check_in_watchlist()`

### DELETE `/api/watchlist/clear`

**Description**: 清空当前用户的自选股列表

- **Module**: `watchlist.py`
- **Function**: `clear_watchlist()`

### GET `/api/watchlist/count`

**Description**: 获取自选股数量

- **Module**: `watchlist.py`
- **Function**: `get_watchlist_count()`

### GET `/api/watchlist/group/{group_id}`

**Description**: 获取指定分组的自选股列表

- **Module**: `watchlist.py`
- **Function**: `get_watchlist_by_group()`

### GET `/api/watchlist/groups`

**Description**: 获取当前用户的所有自选股分组

- **Module**: `watchlist.py`
- **Function**: `get_user_groups()`

### POST `/api/watchlist/groups`

**Description**: 创建新的自选股分组

- **Module**: `watchlist.py`
- **Function**: `create_group()`

### PUT `/api/watchlist/groups/{group_id}`

**Description**: 修改分组名称

- **Module**: `watchlist.py`
- **Function**: `update_group()`

### DELETE `/api/watchlist/groups/{group_id}`

**Description**: 删除分组（会同时删除该分组下的所有自选股）

- **Module**: `watchlist.py`
- **Function**: `delete_group()`

### PUT `/api/watchlist/move`

**Description**: 将股票从一个分组移动到另一个分组

- **Module**: `watchlist.py`
- **Function**: `move_stock_to_group()`

### PUT `/api/watchlist/notes/{symbol}`

**Description**: 更新自选股备注

- **Module**: `watchlist.py`
- **Function**: `update_watchlist_notes()`

### DELETE `/api/watchlist/remove/{symbol}`

**Description**: 从自选股列表中删除股票

- **Module**: `watchlist.py`
- **Function**: `remove_from_watchlist()`

### GET `/api/watchlist/with-groups`

**Description**: 获取所有分组及其包含的自选股（分组视图）

- **Module**: `watchlist.py`
- **Function**: `get_watchlist_with_groups()`
