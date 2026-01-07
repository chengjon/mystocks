# MyStocks API 映射与依赖关系文档

#### 1. 认证 (Authentication)

| 页面 | 组件 | 控件/操作 | 对应 API | 请求方式 | 依赖参数 | 源文件 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 登录页 | `/src/views/Login.vue` | 登录按钮 | `/api/v1/auth/login` | `POST` | `username`, `password` | `web/backend/app/api/auth.py` |
| (全局) | `/src/stores/auth.js` | 登出操作 | `/api/v1/auth/logout` | `POST` | 登录令牌 (Header) | `web/backend/app/api/auth.py` |
| (全局) | `/src/stores/auth.js` | 获取当前用户信息 | `/api/v1/auth/me` | `GET` | 登录令牌 (Header) | `web/backend/app/api/auth.py` |

#### 2. 股票列表与筛选 (Stock List & Filtering)

| 页面 | 组件 | 控件/操作 | 对应 API | 请求方式 | 依赖参数 | 源文件 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 股票列表页 | `/src/views/Stocks.vue` | 表格主体 | `/api/data/stocks/basic` | `GET` | (Query) `limit`, `offset`, `search`, `industry`, `concept`, `market`, `sort_field`, `sort_order` | `web/backend/app/api/data.py` |
| 股票列表页 | `/src/views/Stocks.vue` | 行业筛选下拉 | `/api/data/stocks/industries` | `GET` | 无 | `web/backend/app/api/data.py` |
| 股票列表页 | `/src/views/Stocks.vue` | 概念筛选下拉 | `/api/data/stocks/concepts` | `GET` | 无 | `web/backend/app/api/data.py` |
| (全局) | - | 股票模糊搜索 | `/api/data/stocks/search` | `GET` | (Query) `keyword`, `limit` | `web/backend/app/api/data.py` |

#### 3. 股票详情与技术分析 (Stock Detail & Technical Analysis)

| 页面 | 组件 | 控件/操作 | 对应 API | 请求方式 | 依赖参数 | 源文件 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 股票详情页 | `/src/views/StockDetail.vue` | 股票信息头部 | `/api/data/stocks/{symbol}/detail` | `GET` | (Path) `symbol` | `web/backend/app/api/data.py` |
| 股票详情页 | `/src/views/StockDetail.vue` | K线图容器 | `/api/data/stocks/kline` | `GET` | (Query) `symbol`, `period`, `start_date`, `end_date` | `web/backend/app/api/data.py` |
| 股票详情页 | `/src/views/StockDetail.vue` | 分时图 | `/api/data/stocks/intraday` | `GET` | (Query) `symbol`, `date` | `web/backend/app/api/data.py` |
| 股票详情页 | `/src/views/StockDetail.vue` | 交易摘要 | `/api/data/stocks/{symbol}/trading-summary` | `GET` | (Path) `symbol`, (Query) `period` | `web/backend/app/api/data.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 指标面板 | `/api/technical/{symbol}/indicators` | `GET` | (Path) `symbol`, (Query) `period`, `start_date`, `end_date`, `limit` | `web/backend/app/api/technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 交易信号 | `/api/technical/{symbol}/signals` | `GET` | (Path) `symbol`, (Query) `period` | `web/backend/app/api/technical_analysis.py` |

#### 4. 市场数据 (Market Data)

| 页面 | 组件 | 控件/操作 | 对应 API | 请求方式 | 依赖参数 | 源文件 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 仪表盘 | `/src/views/Dashboard.vue` | 市场概览 | `/api/data/markets/overview` | `GET` | 无 | `web/backend/app/api/data.py` |
| 仪表盘 | `/src/views/Dashboard.vue` | 热门行业 | `/api/data/markets/hot-industries` | `GET` | (Query) `limit` | `web/backend/app/api/data.py` |
| 资金流向 | `/src/components/market/FundFlowPanel.vue` | 数据表 | `/api/market/fund-flow` | `GET` | (Query) `symbol`, `timeframe`, `start_date`, `end_date` | `web/backend/app/api/market.py` |
| ETF行情 | `/src/components/market/ETFDataTable.vue` | 数据表 | `/api/market/etf/list` | `GET` | (Query) `symbol`, `keyword`, `market`, `category`, `limit`, `offset` | `web/backend/app/api/market.py` |
| 龙虎榜 | `/src/components/market/LongHuBangTable.vue`| 数据表 | `/api/monitoring/dragon-tiger` | `GET` | (Query) `trade_date`, `symbol`, `min_net_amount`, `limit` | `web/backend/app/api/monitoring.py` |

#### 5. 监控与告警 (Monitoring & Alerts)

| 页面 | 组件 | 控件/操作 | 对应 API | 请求方式 | 依赖参数 | 源文件 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 风险监控 | `/src/views/RiskMonitor.vue` | 告警规则列表 | `/api/monitoring/alert-rules` | `GET` | (Query) `rule_type`, `is_active` | `web/backend/app/api/monitoring.py` |
| 风险监控 | `/src/views/RiskMonitor.vue` | 创建告警规则 | `/api/monitoring/alert-rules` | `POST` | (Body) `AlertRuleCreate` | `web/backend/app/api/monitoring.py` |
| 风险监控 | `/src/views/RiskMonitor.vue` | 告警记录 | `/api/monitoring/alerts` | `GET` | (Query) `symbol`, `alert_type`, `alert_level`, `is_read`, `start_date`, `end_date`, `limit`, `offset` | `web/backend/app/api/monitoring.py` |
| 实时监控 | `/src/views/RealTimeMonitor.vue` | SSE状态监控 | - (WebSocket) | - | - | `web/backend/app/core/socketio_manager.py` |
