# MyStocks API 映射与依赖关系文档

> **版本**: v2.0 | **更新日期**: 2026-02-16 | **API版本管理**: `web/backend/app/api/VERSION_MAPPING.py`

---

## 📋 概述

本文档映射前端组件到后端 API 端点的完整对应关系。所有 API 路径以 `VERSION_MAPPING.py` 为权威来源。

### 认证机制

| 机制 | 说明 | 实现 |
|------|------|------|
| JWT Bearer Token | 登录后获取，存储于 `localStorage.auth_token`，通过 `Authorization: Bearer {token}` 发送 | `apiClient.ts` 请求拦截器 |
| CSRF Token | GET `/api/csrf-token` 获取，通过 `X-CSRF-Token` 头发送（仅 POST/PUT/PATCH/DELETE） | `apiClient.ts` 请求拦截器 |

### 统一响应格式 (UnifiedResponse)

```typescript
interface UnifiedResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T | null;
  timestamp: string;
  request_id: string;
  errors: any | null;
}
```

### 代理配置

前端 Vite 代理: `/api` → `http://localhost:8000`（端口范围: 前端 3000-3009, 后端 8000-8009）

---

## 1. 认证 (Authentication)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 登录页 | `/src/views/Login.vue` | 登录按钮 | `/api/v1/auth/login` | POST | `username`, `password` | `auth.py` |
| 登录页 (兼容) | `/src/views/Login.vue` | 表单登录 | `/api/auth/login` | POST | URLSearchParams | `auth.py` (compat_router) |
| 全局 | `/src/stores/auth.ts` | 登出操作 | `/api/v1/auth/logout` | POST | JWT Header | `auth.py` |
| 全局 | `/src/stores/auth.ts` | 获取当前用户 | `/api/v1/auth/me` | GET | JWT Header | `auth.py` |
| 全局 | `/src/stores/auth.ts` | 刷新令牌 | `/api/v1/auth/refresh` | POST | refresh_token | `auth.py` |
| 全局 | `/src/api/apiClient.ts` | CSRF令牌 | `/api/csrf-token` | GET | 无 | `main.py` |
| 用户管理 | - | 用户注册 | `/api/v1/auth/register` | POST | Body | `auth.py` |
| 用户管理 | - | 密码重置请求 | `/api/v1/auth/reset-password/request` | POST | email | `auth.py` |
| 用户管理 | - | 密码重置确认 | `/api/v1/auth/reset-password/confirm` | POST | token, new_password | `auth.py` |
| 管理员 | - | 用户列表 | `/api/v1/auth/users` | GET | JWT Header (admin) | `auth.py` |

## 2. 股票列表与筛选 (Stock List & Filtering)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 股票列表页 | `/src/views/Stocks.vue` | 表格主体 | `/api/v1/data/stocks/basic` | GET | `limit`, `offset`, `search`, `industry`, `concept`, `market`, `sort_field`, `sort_order` | `data.py` |
| 股票列表页 | `/src/views/Stocks.vue` | 行业筛选 | `/api/v1/data/stocks/industries` | GET | 无 | `data.py` |
| 股票列表页 | `/src/views/Stocks.vue` | 概念筛选 | `/api/v1/data/stocks/concepts` | GET | 无 | `data.py` |
| 全局搜索 | `/src/api/astockApi.ts` | 模糊搜索 | `/api/v1/data/stocks/search` | GET | `keyword`, `limit` | `data.py` |
| 股票搜索 | - | 独立搜索 | `/api/stock-search` | GET | `keyword` | `stock_search.py` |

## 3. 股票详情与技术分析 (Stock Detail & Technical Analysis)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 股票详情页 | `/src/views/StockDetail.vue` | 信息头部 | `/api/v1/data/stocks/{symbol}/detail` | GET | Path: `symbol` | `data.py` |
| 股票详情页 | `/src/views/StockDetail.vue` | K线图 | `/api/v1/market/kline` | GET | `symbol`, `period`, `start_date`, `end_date` | `market.py` |
| K线API | `/src/api/klineApi.ts` | K线数据 | `/api/v1/market/kline` | GET | `symbol`, `period`, `start_date`, `end_date` | `market.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 全部指标 | `/api/v1/technical/{symbol}/indicators` | GET | Path: `symbol`, Query: `period`, `start_date`, `end_date` | `technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 趋势指标 | `/api/v1/technical/{symbol}/trend` | GET | Path: `symbol` | `technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 动量指标 | `/api/v1/technical/{symbol}/momentum` | GET | Path: `symbol` | `technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 波动指标 | `/api/v1/technical/{symbol}/volatility` | GET | Path: `symbol` | `technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 成交量指标 | `/api/v1/technical/{symbol}/volume` | GET | Path: `symbol` | `technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 交易信号 | `/api/v1/technical/{symbol}/signals` | GET | Path: `symbol`, Query: `period` | `technical_analysis.py` |
| 技术分析页 | `/src/views/TechnicalAnalysis.vue` | 历史数据 | `/api/v1/technical/{symbol}/history` | GET | Path: `symbol` | `technical_analysis.py` |
| 指标API | `/src/api/indicatorApi.ts` | 批量指标 | `/api/v1/technical/batch/indicators` | POST | Body: symbols[], params | `technical_analysis.py` |

## 4. 市场数据 (Market Data)

### 4.1 市场数据 V1 (`/api/v1/market`)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 仪表盘 | `/src/views/Dashboard.vue` | 市场概览 | `/api/v1/data/markets/overview` | GET | 无 | `data.py` |
| 仪表盘 | `/src/views/Dashboard.vue` | 热门行业 | `/api/v1/data/markets/hot-industries` | GET | `limit` | `data.py` |
| 资金流向 | ArtDeco FundFlow 组件 | 数据表 | `/api/v1/market/fund-flow` | GET | `symbol`, `timeframe`, `start_date`, `end_date` | `market.py` |
| ETF行情 | ArtDeco ETFAnalysis 组件 | 数据表 | `/api/v1/market/etf` | GET | `symbol`, `keyword`, `market`, `category`, `limit`, `offset` | `market.py` |
| 龙虎榜 | ArtDeco DragonTiger 组件 | 数据表 | `/api/v1/market/lhb` | GET | `trade_date`, `symbol` | `market.py` |
| 行情报价 | `/src/api/market.ts` | 实时报价 | `/api/v1/market/quotes` | GET | `symbols` | `market.py` |
| 筹码分析 | - | 筹码竞赛 | `/api/v1/market/chip-race` | GET | `symbol` | `market.py` |

### 4.2 市场数据 V2 (`/api/v2/market`)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 资金流向 | ArtDeco 组件 | 增强资金流 | `/api/v2/market/fund-flow` | GET | `symbol`, `timeframe` | `market_v2.py` |
| 资金流向 | - | 刷新数据 | `/api/v2/market/fund-flow/refresh` | POST | - | `market_v2.py` |
| ETF列表 | ArtDeco 组件 | ETF列表 | `/api/v2/market/etf/list` | GET | `keyword`, `market` | `market_v2.py` |
| ETF | - | 刷新ETF | `/api/v2/market/etf/refresh` | POST | - | `market_v2.py` |
| 龙虎榜 | ArtDeco 组件 | 龙虎榜详情 | `/api/v2/market/lhb` | GET | `trade_date` | `market_v2.py` |
| 板块资金 | ArtDeco 组件 | 板块资金流 | `/api/v2/market/sector/fund-flow` | GET | `sector` | `market_v2.py` |
| 分红配送 | - | 股票分红 | `/api/v2/market/dividend` | GET | `symbol` | `market_v2.py` |
| 大宗交易 | - | 大宗交易 | `/api/v2/market/blocktrade` | GET | `symbol` | `market_v2.py` |
| 批量刷新 | - | 全量刷新 | `/api/v2/market/refresh-all` | POST | - | `market_v2.py` |

## 5. 监控与告警 (Monitoring & Alerts)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 风险监控 | `/src/views/RiskMonitor.vue` | 告警规则列表 | `/api/v1/monitoring/alert-rules` | GET | `rule_type`, `is_active` | `monitoring.py` |
| 风险监控 | `/src/views/RiskMonitor.vue` | 创建告警规则 | `/api/v1/monitoring/alert-rules` | POST | Body: AlertRuleCreate | `monitoring.py` |
| 风险监控 | `/src/views/RiskMonitor.vue` | 更新告警规则 | `/api/v1/monitoring/alert-rules/{rule_id}` | PUT | Path: rule_id, Body | `monitoring.py` |
| 风险监控 | `/src/views/RiskMonitor.vue` | 删除告警规则 | `/api/v1/monitoring/alert-rules/{rule_id}` | DELETE | Path: rule_id | `monitoring.py` |
| 风险监控 | `/src/views/RiskMonitor.vue` | 告警记录 | `/api/v1/monitoring/alerts` | GET | `symbol`, `alert_type`, `is_read`, `limit`, `offset` | `monitoring.py` |
| 告警管理 | `/src/api/monitoring.ts` | 标记已读 | `/api/v1/monitoring/alerts/{alert_id}/mark-read` | POST | Path: alert_id | `monitoring.py` |
| 告警管理 | `/src/api/monitoring.ts` | 全部已读 | `/api/v1/monitoring/alerts/mark-all-read` | POST | 无 | `monitoring.py` |
| 实时监控 | `/src/views/RealTimeMonitor.vue` | 实时数据 | `/api/v1/monitoring/realtime/{symbol}` | GET | Path: symbol | `monitoring.py` |
| 实时监控 | `/src/views/RealTimeMonitor.vue` | 监控列表 | `/api/v1/monitoring/realtime` | GET | 无 | `monitoring.py` |
| 龙虎榜 | ArtDeco DragonTiger 组件 | 龙虎榜数据 | `/api/v1/monitoring/dragon-tiger` | GET | `trade_date`, `symbol`, `min_net_amount`, `limit` | `monitoring.py` |
| 监控概览 | - | 监控摘要 | `/api/v1/monitoring/summary` | GET | 无 | `monitoring.py` |
| 监控控制 | - | 启动监控 | `/api/v1/monitoring/control/start` | POST | 无 | `monitoring.py` |
| 监控控制 | - | 停止监控 | `/api/v1/monitoring/control/stop` | POST | 无 | `monitoring.py` |
| 监控控制 | - | 监控状态 | `/api/v1/monitoring/control/status` | GET | 无 | `monitoring.py` |

## 6. 策略管理 (Strategy Management)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 策略管理 | `/src/views/StrategyManagement.vue` | 策略定义列表 | `/api/v1/strategy/definitions` | GET | 无 | `strategy.py` |
| 策略管理 | `/src/views/StrategyManagement.vue` | 单股运行 | `/api/v1/strategy/run/single` | POST | Body: symbol, strategy_id | `strategy.py` |
| 策略管理 | `/src/views/StrategyManagement.vue` | 批量运行 | `/api/v1/strategy/run/batch` | POST | Body: symbols[], strategy_id | `strategy.py` |
| 策略管理 | `/src/api/strategy.ts` | 结果查询 | `/api/v1/strategy/results` | GET | `strategy_id`, `symbol` | `strategy.py` |
| 策略管理 | `/src/api/strategy.ts` | 匹配股票 | `/api/v1/strategy/matched-stocks` | GET | `strategy_id` | `strategy.py` |
| 策略管理 | `/src/api/strategy.ts` | 统计摘要 | `/api/v1/strategy/stats/summary` | GET | 无 | `strategy.py` |

## 7. 系统管理 (System)

| 页面/组件 | 前端路径 | 控件/操作 | API 端点 | 方法 | 参数 | 后端源文件 |
|-----------|----------|-----------|----------|------|------|------------|
| 根路径 | - | API欢迎 | `/` | GET | 无 | `main.py` |
| 健康检查 | - | 系统健康 | `/health` | GET | 无 | `main.py` |
| 监控 | - | Prometheus指标 | `/metrics` | GET | 无 | `main.py` |
| API文档 | - | Swagger UI | `/api/docs` | GET | 无 | `main.py` |
| API文档 | - | ReDoc | `/api/redoc` | GET | 无 | `main.py` |
| Socket状态 | - | SocketIO状态 | `/api/socketio-status` | GET | 无 | `main.py` |

## 8. 其他功能模块

### 自选股管理 (`/api/watchlist`)

| 操作 | API 端点 | 方法 | 后端源文件 |
|------|----------|------|------------|
| 自选股CRUD | `/api/watchlist/*` | GET/POST/PUT/DELETE | `watchlist.py` |

### 通知服务 (`/api/notification`)

| 操作 | API 端点 | 方法 | 后端源文件 |
|------|----------|------|------------|
| 通知管理 | `/api/notification/*` | GET/POST | `notification.py` |

### TradingView (`/api/tradingview`)

| 操作 | API 端点 | 方法 | 后端源文件 |
|------|----------|------|------------|
| 图表配置 | `/api/tradingview/*` | GET/POST | `tradingview.py` |

### 数据源管理

| 操作 | API 端点 | 方法 | 后端源文件 |
|------|----------|------|------------|
| 数据源注册表 | `/api/v1/data-sources/*` | GET/POST | `data_source_registry.py` |
| 数据源配置 | `/api/v1/data-source-config/*` | GET/POST/PUT/DELETE | `data_source_config.py` |

### 指标管理 (`/api/v1/indicators`)

| 操作 | API 端点 | 方法 | 后端源文件 |
|------|----------|------|------------|
| 指标注册表 | `/api/v1/indicators/*` | GET/POST/PUT/DELETE | `indicators.py` |

---

## 📊 API 前缀汇总

| 前缀 | 版本 | 功能模块 | 路由来源 |
|------|------|----------|----------|
| `/api/v1/auth` | v1 | 认证授权 | VERSION_MAPPING |
| `/api/v1/data` | v1 | 数据管理（股票、市场） | VERSION_MAPPING |
| `/api/v1/market` | v1 | 市场数据（K线、行情、资金流） | VERSION_MAPPING |
| `/api/v2/market` | v2 | 增强市场数据（ETF、大宗、分红） | VERSION_MAPPING |
| `/api/v1/strategy` | v1 | 策略管理 | VERSION_MAPPING |
| `/api/v1/monitoring` | v1 | 监控告警 | VERSION_MAPPING |
| `/api/v1/technical` | v1 | 技术分析 | VERSION_MAPPING |
| `/api/v1/system` | v1 | 系统管理 | VERSION_MAPPING |
| `/api/v1/indicators` | v1 | 指标管理 | VERSION_MAPPING |
| `/api/v1/trade` | v1 | 交易管理 | VERSION_MAPPING |
| `/api/v1/tdx` | v1 | 通达信数据 | VERSION_MAPPING |
| `/api/v1/announcement` | v1 | 公告监控 | VERSION_MAPPING |
| `/api/auth` | compat | 兼容登录 | main.py 直接注册 |
| `/api/stock-search` | - | 股票搜索 | main.py 直接注册 |
| `/api/watchlist` | - | 自选股 | main.py 直接注册 |
| `/api/tradingview` | - | TradingView | main.py 直接注册 |
| `/api/notification` | - | 通知服务 | main.py 直接注册 |
| `/api` | - | 缓存/数据质量/ML/健康等 | main.py 直接注册 |

---

**Last Updated**: 2026-02-16
**维护者**: MyStocks Team
**权威来源**: `web/backend/app/api/VERSION_MAPPING.py`
