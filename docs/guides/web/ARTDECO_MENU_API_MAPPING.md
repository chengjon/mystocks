# ArtDeco菜单系统 - API映射表

## 目标

本文档旨在提供 ArtDeco 菜单项与其后端 API 端点之间的明确映射关系。这将确保前端菜单功能与后端数据服务的紧密集成，并支持实时数据更新机制。

## 映射规则

每个菜单项的映射应包含以下信息：

-   **菜单项名称**: 对应的菜单项的名称。
-   **菜单项路径**: 对应的菜单项的路由路径。
-   **功能描述**: 该菜单项提供的核心功能。
-   **API 端点 (apiEndpoint)**: 调用的主要后端 API 端点 URL。
-   **HTTP 方法 (apiMethod)**: GET, POST, PUT, DELETE 等。
-   **所需参数 (queryParams/body)**: 调用 API 可能需要的关键查询参数或请求体示例。
-   **响应数据示例**: API 成功响应的关键数据结构示例。
-   **是否需要实时更新 (liveUpdate)**: 布尔值，指示该菜单项的数据是否需要通过 WebSocket 实时更新。
-   **WebSocket 频道 (wsChannel)**: 如果 `liveUpdate` 为 true，则指定用于实时更新的 WebSocket 频道名称。
-   **后端文件**: 对应的后端路由定义文件路径。

## 菜单-API 映射详情

### 1. 仪表盘 (/dashboard)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 仪表盘 | `/dashboard` | 汇总信息、市场热度、资金流向、股票池表现 | `/api/dashboard/overview` | GET | (无) | `{ "market_sentiment": " bullish", ... }` | 否 | (无) | `dashboard.py` |

### 2. 市场行情 (/market/*)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 市场行情 | `/market/data` | 实时行情、TDX接口、资金流向、ETF、概念、龙虎榜 | `/api/market/realtime-summary` | GET | (无) | `{ "latest_quotes": [...], "fund_flows": [...] }` | 是 | `market:summary` | `market.py` |
| 实时行情 | `/market/realtime` | 获取个股或市场实时行情数据 | `/api/market/stock/realtime` | GET | `symbol=SH600000` | `{ "symbol": "SH600000", "price": 10.25, ... }` | 是 | `market:realtime` | `market.py` |
| 技术指标 | `/market/indicators` | 计算和获取股票技术指标 | `/api/indicators/technical` | GET | `symbol=SH600000, type=SMA, period=30` | `{ "SMA": [...], "RSI": [...] }` | 否 | (无) | `technical_analysis.py` |
| 资金流向 | `/market/fund-flow` | 查看市场或个股资金流向 | `/api/market/fund-flow` | GET | `type=stock, symbol=SH600000` | `{ "main_inflow": ..., "retail_outflow": ... }` | 是 | `market:fund_flow` | `market.py` |
| ETF行情 | `/market/etf` | ETF 实时行情和历史数据 | `/api/market/etf` | GET | `symbol=510300` | `{ "etf_name": "沪深300ETF", ... }` | 是 | `market:etf` | `market_v2.py` |
| 概念行情 | `/market/concept` | 概念板块行情和相关股票 | `/api/market/concept` | GET | `name=人工智能` | `{ "concept_name": "人工智能", "stocks": [...] }` | 是 | `market:concept` | `market.py` |
| 龙虎榜 | `/market/longhubang` | 每日龙虎榜数据 | `/api/market/longhubang` | GET | `date=2026-01-19` | `{ "date": "2026-01-19", "top_stocks": [...] }` | 否 | (无) | `market.py` |
| 机构荐股 | `/market/institution` | 机构推荐股票列表 | `/api/market/institution` | GET | (无) | `{ "recommendations": [...] }` | 否 | (无) | `market.py` |
| 问财选股 | `/market/wencai` | 基于自然语言问句的选股 | `/api/market/wencai` | POST | `query=涨停` | `{ "matching_stocks": [...] }` | 否 | (无) | `market.py` |
| 股票筛选 | `/market/screener` | 基于多维度条件的股票筛选 | `/api/data/screener` | GET | `industry=科技, pe_ratio=10-20` | `{ "filtered_stocks": [...] }` | 否 | (无) | `data.py` |

### 3. 股票管理 (/stocks/*)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 股票管理 | `/stocks/management` | 自选股、关注列表、策略选股、行业选股 | `/api/user/stock-management-summary` | GET | (无) | `{ "watchlist_count": 5, "strategy_selections": [...] }` | 否 | (无) | `watchlist.py` |
| 自选股列表 | `/stocks/watchlist` | 管理用户的自选股票列表 | `/api/watchlist` | GET/POST/DELETE | `user_id=1, symbol=SH600000` | `{ "watchlist": [...] }` | 是 | `user:watchlist` | `watchlist.py` |
| 投资组合 | `/stocks/portfolio` | 管理和查看投资组合 | `/api/trading/portfolio` | GET/POST | `user_id=1` | `{ "portfolio": { "total_value": ..., "holdings": [...] } }` | 是 | `user:portfolio` | `trading_router.py` |
| 策略选股结果 | `/stocks/strategy-selection` | 查看策略选股结果 | `/api/strategy/selection-results` | GET | `strategy_id=1` | `{ "strategy_name": "趋势跟踪", "stocks": [...] }` | 是 | `strategy:selection` | `strategy_management.py` |
| 行业选股结果 | `/stocks/industry-selection` | 查看行业选股结果 | `/api/data/industry-selection` | GET | `industry=科技` | `{ "industry_name": "科技", "stocks": [...] }` | 否 | (无) | `data.py` |
| 概念选股结果 | `/stocks/concept-selection` | 查看概念选股结果 | `/api/data/concept-selection` | GET | `concept=人工智能` | `{ "concept_name": "人工智能", "stocks": [...] }` | 否 | (无) | `data.py` |

### 4. 投资分析 (/analysis/*)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 投资分析 | `/analysis/data` | 技术分析、基本面分析、指标分析、筛选 | `/api/analysis/summary` | GET | (无) | `{ "technical_reports_count": ..., "fundamental_analysis": [...] }` | 否 | (无) | `advanced_analysis.py` |
| 技术分析报告 | `/analysis/technical` | 生成和查看个股技术分析报告 | `/api/analysis/technical` | GET | `symbol=SH600000` | `{ "report": { "MACD": "金叉", ... } }` | 否 | (无) | `technical_analysis.py` |
| 基本面分析 | `/analysis/fundamental` | 获取个股基本面数据和分析 | `/api/analysis/fundamental` | GET | `symbol=SH600000` | `{ "financials": [...], "valuation": {...} }` | 否 | (无) | `data.py` |
| 指标分析 | `/analysis/indicators` | 对自定义或预设指标进行分析 | `/api/indicators/analyze` | POST | `indicators=[SMA, RSI], data=[...]` | `{ "analysis_results": [...] }` | 否 | (无) | `indicators.py` |
| 筛选器 | `/analysis/screener` | 基于多个条件进行股票筛选 | `/api/data/screener` | POST | `conditions=[{"field": "PE", "op": ">", "value": 20}]` | `{ "matching_stocks": [...] }` | 否 | (无) | `data.py` |
| 股票对比 | `/analysis/comparison` | 对多只股票进行关键指标对比 | `/api/analysis/compare-stocks` | GET | `symbols=[SH600000, SZ000001]` | `{ "comparison_data": [...] }` | 否 | (无) | `advanced_analysis.py` |

### 5. 风险管理 (/risk/*)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 风险管理 | `/risk/management` | 风险监控、预警设置、舆情管理、因子分析 | `/api/risk/overview` | GET | (无) | `{ "portfolio_risk_score": 75, "alerts": [...] }` | 是 | `risk:overview` | `risk_management.py` |
| 个股预警设置 | `/risk/alerts` | 设置和管理个股价格、指标预警 | `/api/v1/risk/alerts` | GET/POST | `user_id=1, type=price, threshold=10` | `{ "active_alerts": [...] }` | 是 | `risk:alerts` | `risk_management.py` |
| 风险指标监控 | `/risk/metrics` | 实时监控投资组合和个股风险指标 | `/api/v1/risk/metrics` | GET | `portfolio_id=1` | `{ "VaR": 0.05, "Beta": 1.2 }` | 是 | `risk:metrics` | `risk_management.py` |
| 舆情管理 | `/risk/sentiment` | 监控市场和个股相关舆情 | `/api/monitoring/sentiment` | GET | `symbol=SH600000` | `{ "sentiment_score": 0.6, "news_headlines": [...] }` | 是 | `monitoring:sentiment` | `monitoring.py` |
| 因子分析 | `/risk/factors` | 进行风险因子分析和归因 | `/api/v1/risk/factors` | POST | `portfolio_id=1, factors=[size, value]` | `{ "factor_exposures": [...] }` | 否 | (无) | `risk_management.py` |
| 持仓风险分析 | `/risk/position-risk` | 对当前持仓进行风险评估 | `/api/v1/risk/position` | GET | `user_id=1` | `{ "position_VaR": ..., "concentration_risk": ... }` | 是 | `risk:position` | `risk_management.py` |

### 6. 策略和交易管理 (/strategy/*)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 策略和交易管理 | `/strategy/trading` | 策略设计、GPU回测、交易信号、历史记录 | `/api/strategy/overview` | GET | (无) | `{ "active_strategies": [...], "pending_signals": [...] }` | 是 | `strategy:overview` | `strategy_management.py` |
| 策略设计 | `/strategy/design` | 创建和编辑量化交易策略 | `/api/strategy/design` | POST/PUT | `strategy_config={...}` | `{ "strategy_id": "uuid", "status": "draft" }` | 否 | (无) | `strategy_management.py` |
| 策略管理 | `/strategy/management` | 激活、停止、删除交易策略 | `/api/strategy/management` | GET/POST/PUT/DELETE | `strategy_id=uuid, action=activate` | `{ "status": "success" }` | 是 | `strategy:management` | `strategy_management.py` |
| 策略回测 | `/strategy/backtest` | 对策略进行历史数据回测 | `/api/strategy/backtest` | POST | `strategy_id=uuid, start_date=..., end_date=...` | `{ "backtest_report": {...} }` | 否 | (无) | `strategy_management.py` |
| GPU加速回测 | `/strategy/gpu-backtest` | 利用 GPU 进行高性能策略回测 | `/api/gpu/backtest` | POST | `strategy_id=uuid, config={...}` | `{ "backtest_id": "uuid", "status": "running" }` | 是 | `gpu:backtest_status` | `realtime_mtm_init.py` |
| 交易信号 | `/strategy/signals` | 查看实时交易信号和建议 | `/api/signals/latest` | GET | (无) | `{ "signals": [...] }` | 是 | `signals:latest` | `signal_monitoring.py` |
| 交易历史 | `/strategy/history` | 查询历史交易记录 | `/api/trading/history` | GET | `user_id=1, start_date=...` | `{ "trades": [...] }` | 否 | (无) | `trading_router.py` |
| 持仓分析 | `/strategy/positions` | 分析当前交易策略的持仓情况 | `/api/trading/positions` | GET | `strategy_id=uuid` | `{ "current_positions": [...] }` | 是 | `strategy:positions` | `trading_router.py` |
| 事后归因 | `/strategy/attribution` | 分析交易结果的驱动因素 | `/api/trading/attribution` | POST | `trade_id=uuid` | `{ "attribution_report": {...} }` | 否 | (无) | `trading_router.py` |

### 7. 系统监控 (/system/*)

| 菜单项名称 | 菜单项路径 | 功能描述 | API 端点 | HTTP 方法 | 所需参数 | 响应数据示例 | 是否需要实时更新 | WebSocket 频道 | 后端文件 |
|---|---|---|---|---|---|---|---|---|---|
| 系统监控 | `/system/monitoring` | 平台监控、系统设置、数据更新、数据质量 | `/api/monitoring/platform-status` | GET | (无) | `{ "cpu_usage": "20%", "memory_usage": "50%" }` | 是 | `system:status` | `monitoring.py` |
| 平台监控 | `/system/platform-monitor` | 实时监控系统资源和服务状态 | `/api/monitoring/dashboard` | GET | (无) | `{ "service_health": {...}, "resource_metrics": {...} }` | 是 | `monitoring:dashboard` | `monitoring.py` |
| 系统设置 | `/system/settings` | 管理和配置系统各项参数 | `/api/v1/system/settings` | GET/PUT | `key=value` | `{ "theme": "dark", "locale": "zh-CN" }` | 否 | (无) | `system.py` |
| 数据更新状态 | `/system/data-update` | 查看数据同步和更新任务状态 | `/api/tasks/status` | GET | `task_type=data_sync` | `{ "last_sync": "...", "status": "completed" }` | 是 | `tasks:status` | `tasks.py` |
| 数据质量报告 | `/system/data-quality` | 评估数据质量和完整性 | `/api/data-quality/metrics` | GET | `data_source=TDX` | `{ "completeness": 0.98, "accuracy": 0.99 }` | 否 | (无) | `data_quality.py` |
| API健康检查 | `/system/api-health` | 检查各 API 端点的健康状态 | `/api/health` | GET | (无) | `{ "status": "healthy", "services": {...} }` | 是 | `health:status` | `health.py` |