# MyStocks API 完整列表文档

## 概述

本文档包含 MyStocks 量化交易数据管理系统中所有的 RESTful API 端点详细说明。API 基于 FastAPI 框架构建，采用 JWT 认证（除公开端点外）。

**API 基础信息**：
- 基础URL: `http://localhost:8000`
- API文档: `http://localhost:8000/api/docs`
- 认证方式: Bearer Token
- 数据格式: JSON
- 响应格式: JSON

## 目录

1. [认证API (auth.py)](#认证api)
2. [市场数据API (market.py)](#市场数据api)
3. [TDX行情API (tdx.py)](#tdx行情api)
4. [系统管理API (system.py)](#系统管理api)
5. [监控API (monitoring.py)](#监控api)
6. [问财API (wencai.py)](#问财api)
7. [策略管理API (strategy.py & strategy_management.py)](#策略管理api)
8. [技术分析API (technical_analysis.py)](#技术分析api)
9. [任务管理API (tasks.py)](#任务管理api)
10. [监控指标API (metrics.py)](#监控指标api)
11. [SSE实时推送API (sse_endpoints.py)](#sse实时推送api)
12. [公告API (announcement.py)](#公告api)
13. [自选股管理API (watchlist.py)](#自选股管理api)
14. [机器学习API (ml.py)](#机器学习api)
15. [风险管理API (risk_management.py)](#风险管理api)
16. [通知API (notification.py)](#通知api)
17. [股票搜索API (stock_search.py)](#股票搜索api)
18. [缓存API (cache.py)](#缓存api)
19. [多数据源API (multi_source.py)](#多数据源api)

---

## 认证API

**基础路径**: `/api/auth`

### 1. 用户登录
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**响应**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "username": "admin",
    "email": "admin@mystocks.com",
    "role": "admin"
  }
}
```

### 2. 用户登出
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

### 3. 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### 4. 刷新令牌
```http
POST /api/auth/refresh
Authorization: Bearer <token>
```

### 5. 获取用户列表（仅管理员）
```http
GET /api/auth/users
Authorization: Bearer <token>
```

---

## 市场数据API

**基础路径**: `/api/market`

### 1. 获取资金流向
```http
GET /api/market/fund-flow?symbol=600519&timeframe=1
Authorization: Bearer <token>
```

**参数**:
- `symbol`: 股票代码 (如: 600519.SH)
- `timeframe`: 1=今日, 3=3日, 5=5日, 10=10日
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)

### 2. 刷新资金流向数据
```http
POST /api/market/fund-flow/refresh?symbol=600519&timeframe=1
Authorization: Bearer <token>
```

### 3. 获取ETF列表
```http
GET /api/market/etf/list?keyword=沪深300
Authorization: Bearer <token>
```

**参数**:
- `symbol`: ETF代码 (可选)
- `keyword`: 关键词搜索 (可选)
- `limit`: 返回数量 (默认50, 最大500)

### 4. 刷新ETF数据
```http
POST /api/market/etf/refresh
Authorization: Bearer <token>
```

### 5. 获取竞价抢筹数据
```http
GET /api/market/chip-race?race_type=open
Authorization: Bearer <token>
```

**参数**:
- `race_type`: 抢筹类型 (open=早盘, end=尾盘)
- `trade_date`: 交易日期 (可选)
- `min_race_amount`: 最小抢筹金额 (可选)
- `limit`: 返回数量 (默认100)

### 6. 获取龙虎榜
```http
GET /api/market/lhb?start_date=2025-10-01&end_date=2025-10-31
Authorization: Bearer <token>
```

**参数**:
- `symbol`: 股票代码 (可选)
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)
- `min_net_amount`: 最小净买入额 (可选)
- `limit`: 返回数量 (默认100)

### 7. 获取实时行情
```http
GET /api/market/quotes?symbols=000001,600519
Authorization: Bearer <token>
```

**参数**:
- `symbols`: 股票代码列表，逗号分隔 (可选)

### 8. 获取股票列表
```http
GET /api/market/stocks?limit=100&search=平安
Authorization: Bearer <token>
```

**参数**:
- `limit`: 返回记录数限制 (1-1000)
- `search`: 股票代码或名称搜索关键词 (可选)
- `exchange`: 交易所筛选 (SSE/SZSE) (可选)
- `security_type`: 证券类型筛选 (可选)

### 9. 获取K线数据
```http
GET /api/market/kline?stock_code=600519&period=daily&adjust=qfq&start_date=2025-10-01&end_date=2025-10-31
Authorization: Bearer <token>
```

**参数**:
- `stock_code`: 股票代码（6位数字或带交易所后缀）
- `period`: 时间周期 (daily/weekly/monthly)
- `adjust`: 复权类型 (qfq/hfq/空字符串)
- `start_date`: 开始日期 YYYY-MM-DD (可选)
- `end_date`: 结束日期 YYYY-MM-DD (可选)

### 10. 获取市场热力图
```http
GET /api/market/heatmap?market=cn&limit=50
Authorization: Bearer <token>
```

**参数**:
- `market`: 市场类型 (cn=A股/hk=港股)
- `limit`: 返回股票数量 (10-200)

### 11. 健康检查
```http
GET /api/market/health
```

---

## TDX行情API

**基础路径**: `/api/tdx`

### 1. 获取股票实时行情
```http
GET /api/tdx/quote/600519
Authorization: Bearer <token>
```

**返回**:
- 实时行情数据，包含最新价、涨跌幅、五档行情等

### 2. 获取股票K线数据
```http
GET /api/tdx/kline?symbol=600519&period=1d&start_date=2025-10-01&end_date=2025-10-31
Authorization: Bearer <token>
```

**参数**:
- `symbol`: 股票代码(6位数字)
- `start_date`: 开始日期 YYYY-MM-DD (可选)
- `end_date`: 结束日期 YYYY-MM-DD (可选)
- `period`: K线周期 (1m/5m/15m/30m/1h/1d)

### 3. 获取指数实时行情
```http
GET /api/tdx/index/quote/000001
Authorization: Bearer <token>
```

**参数**:
- `symbol`: 6位数字指数代码
  - 000001: 上证指数
  - 399001: 深证成指
  - 399006: 创业板指

### 4. 获取指数K线数据
```http
GET /api/tdx/index/kline?symbol=000001&period=1d&start_date=2025-10-01
Authorization: Bearer <token>
```

### 5. 健康检查
```http
GET /api/tdx/health
```

---

## 系统管理API

**基础路径**: `/api/system`

### 1. 系统健康检查
```http
GET /api/system/health
```

**返回**:
- 数据库连接状态
- 系统运行时间
- 服务状态

### 2. 适配器健康检查
```http
GET /api/system/adapters/health
```

**返回**:
- 所有数据适配器的健康状态
- 最后检查时间
- 错误信息

### 3. 获取数据源列表
```http
GET /api/system/datasources
```

**返回**:
- 所有可用的数据源配置信息

### 4. 测试数据库连接
```http
POST /api/system/test-connection
Content-Type: application/json

{
  "db_type": "mysql",
  "host": "localhost",
  "port": 3306
}
```

**支持的数据库类型**:
- `mysql`: MySQL/MariaDB
- `postgresql`: PostgreSQL
- `tdengine`: TDengine
- `redis`: Redis

### 5. 获取系统日志
```http
GET /api/system/logs?filter_errors=true&limit=100&level=ERROR
```

**参数**:
- `filter_errors`: 是否只显示有问题的日志 (默认false)
- `limit`: 返回条数限制 (1-1000, 默认100)
- `offset`: 偏移量，用于分页 (默认0)
- `level`: 日志级别筛选 (INFO/WARNING/ERROR/CRITICAL) (可选)
- `category`: 日志分类筛选 (database/api/adapter/system) (可选)

### 6. 获取日志统计摘要
```http
GET /api/system/logs/summary
```

**返回**:
- 总日志数
- 各级别日志数量
- 各分类日志数量
- 最近错误数

### 7. 获取系统架构信息
```http
GET /api/system/architecture
```

**返回**:
- 数据库架构 (TDengine + PostgreSQL)
- 数据分类路由策略
- 架构简化指标
- 技术栈信息

---

## 监控API

**基础路径**: `/api/monitoring`

### 1. 系统性能指标
```http
GET /api/monitoring/performance
```

### 2. 数据库性能监控
```http
GET /api/monitoring/database
```

### 3. API调用统计
```http
GET /api/monitoring/api-stats
```

### 4. 数据质量监控
```http
GET /api/monitoring/data-quality
```

### 5. 缓存命中率
```http
GET /api/monitoring/cache-hit-ratio
```

---

## 问财API

**基础路径**: `/api/wencai`

### 1. 执行问财查询
```http
POST /api/wencai/query
Content-Type: application/json

{
  "question": "股价大于10元且涨幅大于3%的股票",
  "date": "2025-10-15"
}
```

### 2. 获取查询结果
```http
GET /api/wencai/result/{query_id}
Authorization: Bearer <token>
```

### 3. 获取历史查询
```http
GET /api/wencai/history?limit=20
Authorization: Bearer <token>
```

### 4. 获取支持的问财语法
```http
GET /api/wencai/syntax
```

---

## 策略管理API

**基础路径**: `/api/strategy` & `/api/v1/strategy`

### 1. 获取策略列表
```http
GET /api/strategy/strategies?status=active&page=1&page_size=20
Authorization: Bearer <token>
```

**参数**:
- `status`: 过滤状态 ('draft', 'active', 'archived') (可选)
- `page`: 页码 (默认1)
- `page_size`: 每页数量 (默认20)

### 2. 创建新策略
```http
POST /api/strategy/strategies
Content-Type: application/json

{
  "name": "均线策略",
  "strategy_type": "technical",
  "description": "基于移动平均线的交易策略",
  "config": {
    "ma_short": 5,
    "ma_long": 20
  }
}
Authorization: Bearer <token>
```

### 3. 获取策略详情
```http
GET /api/strategy/strategies/1
Authorization: Bearer <token>
```

### 4. 更新策略
```http
PUT /api/strategy/strategies/1
Content-Type: application/json

{
  "name": "均线策略-更新版",
  "config": {
    "ma_short": 10,
    "ma_long": 30
  }
}
Authorization: Bearer <token>
```

### 5. 删除策略
```http
DELETE /api/strategy/strategies/1
Authorization: Bearer <token>
```

### 6. 启动模型训练
```http
POST /api/strategy/models/train
Content-Type: application/json

{
  "name": "股价预测模型",
  "model_type": "random_forest",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10
  },
  "training_config": {
    "test_size": 0.2,
    "random_state": 42
  }
}
Authorization: Bearer <token>
```

### 7. 查询训练状态
```http
GET /api/strategy/models/training/task_123/status
Authorization: Bearer <token>
```

### 8. 获取模型列表
```http
GET /api/strategy/models?model_type=random_forest&status=completed
Authorization: Bearer <token>
```

### 9. 执行回测
```http
POST /api/strategy/backtest/run
Content-Type: application/json

{
  "name": "策略回测1",
  "strategy_id": 1,
  "start_date": "2025-01-01",
  "end_date": "2025-10-31",
  "initial_cash": 1000000,
  "commission_rate": 0.0003
}
Authorization: Bearer <token>
```

### 10. 获取回测结果列表
```http
GET /api/strategy/backtest/results?strategy_id=1&page=1&page_size=20
Authorization: Bearer <token>
```

### 11. 获取回测详细结果
```http
GET /api/strategy/backtest/results/1
Authorization: Bearer <token>
```

### 12. 获取回测图表数据
```http
GET /api/strategy/backtest/results/1/chart-data
Authorization: Bearer <token>
```

---

## 技术分析API

**基础路径**: `/api/technical-analysis`

### 1. 计算技术指标
```http
POST /api/technical-analysis/indicators
Content-Type: application/json

{
  "symbol": "600519",
  "indicators": ["MA", "MACD", "RSI"],
  "period": "daily",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31"
}
Authorization: Bearer <token>
```

### 2. 获取预设指标配置
```http
GET /api/technical-analysis/indicators/config
Authorization: Bearer <token>
```

### 3. 批量计算指标
```http
POST /api/technical-analysis/indicators/batch
Content-Type: application/json

{
  "symbols": ["600519", "000001", "600036"],
  "indicators": ["MA", "MACD"],
  "period": "daily"
}
Authorization: Bearer <token>
```

### 4. 获取K线形态识别
```http
POST /api/technical-analysis/patterns
Content-Type: application/json

{
  "symbol": "600519",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "pattern_types": ["DOJI", "HAMMER", "ENGULFING"]
}
Authorization: Bearer <token>
```

### 5. 获取支撑阻力位
```http
GET /api/technical-analysis/support-resistance?symbol=600519&period=daily
Authorization: Bearer <token>
```

---

## 任务管理API

**基础路径**: `/api/tasks`

### 1. 注册新任务
```http
POST /api/tasks/register
Content-Type: application/json

{
  "task_id": "daily_data_update",
  "task_type": "data_update",
  "schedule": "0 20 * * *",
  "handler": "data_update_handler",
  "params": {
    "data_source": "akshare"
  }
}
Authorization: Bearer <token>
```

### 2. 注销任务
```http
DELETE /api/tasks/daily_data_update
Authorization: Bearer <token>
```

### 3. 列出所有任务
```http
GET /api/tasks?task_type=data_update&tags=daily,important
Authorization: Bearer <token>
```

### 4. 获取任务详情
```http
GET /api/tasks/daily_data_update
Authorization: Bearer <token>
```

### 5. 启动任务
```http
POST /api/tasks/daily_data_update/start
Content-Type: application/json

{
  "force": true,
  "params": {
    "override_date": "2025-10-15"
  }
}
Authorization: Bearer <token>
```

### 6. 停止任务
```http
POST /api/tasks/daily_data_update/stop
Authorization: Bearer <token>
```

### 7. 列出执行记录
```http
GET /api/tasks/executions?task_id=daily_data_update&limit=100
Authorization: Bearer <token>
```

### 8. 获取执行记录详情
```http
GET /api/tasks/executions/execution_123
Authorization: Bearer <token>
```

### 9. 获取任务统计信息
```http
GET /api/tasks/statistics?task_id=daily_data_update
Authorization: Bearer <token>
```

### 10. 导入任务配置
```http
POST /api/tasks/import
Content-Type: application/json

{
  "config_path": "/path/to/task_config.yaml"
}
Authorization: Bearer <token>
```

### 11. 导出任务配置
```http
POST /api/tasks/export
Content-Type: application/json

{
  "output_path": "/path/to/exported_config.yaml"
}
Authorization: Bearer <token>
```

### 12. 清理旧的执行记录
```http
DELETE /api/tasks/executions/cleanup?days=30
Authorization: Bearer <token>
```

### 13. 任务管理器健康检查
```http
GET /api/tasks/health
```

---

## 监控指标API

**基础路径**: `/metrics`

### 1. 获取Prometheus指标
```http
GET /metrics
```

**返回**:
- Prometheus格式的监控指标
- HTTP请求计数器
- 数据库连接状态
- 缓存命中率
- API健康状态

---

## SSE实时推送API

**基础路径**: `/api/v1/sse`

### 1. 模型训练进度推送
```http
GET /api/v1/sse/training?client_id=client_123
```

**事件类型**:
- `connected`: 连接确认
- `training_progress`: 训练进度更新
- `ping`: 心跳保活 (每30秒)

### 2. 回测执行进度推送
```http
GET /api/v1/sse/backtest?client_id=client_123
```

**事件类型**:
- `connected`: 连接确认
- `backtest_progress`: 回测进度更新
- `ping`: 心跳保活

### 3. 风险告警通知
```http
GET /api/v1/sse/alerts?client_id=client_123
```

**事件类型**:
- `connected`: 连接确认
- `risk_alert`: 风险告警通知
- `ping`: 心跳保活

**告警严重级别**:
- `low`: 信息性告警
- `medium`: 警告性告警
- `high`: 重要告警
- `critical`: 关键告警

### 4. 仪表盘数据更新
```http
GET /api/v1/sse/dashboard?client_id=client_123
```

**事件类型**:
- `connected`: 连接确认
- `dashboard_update`: 仪表盘数据更新
- `ping`: 心跳保活

**更新类型**:
- `metrics`: 投资组合指标更新
- `positions`: 持仓更新
- `orders`: 订单更新
- `market`: 市场数据更新

### 5. SSE服务器状态
```http
GET /api/v1/sse/status
```

**返回**:
- 所有频道的连接统计信息

---

## 公告API

**基础路径**: `/api/announcement`

### 1. 获取并保存公告
```http
POST /api/announcement/fetch?symbol=600519&start_date=2025-10-01&end_date=2025-10-31&category=all
Authorization: Bearer <token>
```

**参数**:
- `symbol`: 股票代码 (可选)
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)
- `category`: 公告类别 (默认all)

### 2. 查询公告列表
```http
GET /api/announcement/list?stock_code=600519&start_date=2025-10-01&end_date=2025-10-31&announcement_type=分红&min_importance=3&page=1&page_size=20
Authorization: Bearer <token>
```

**参数**:
- `stock_code`: 股票代码 (可选)
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)
- `announcement_type`: 公告类型 (可选)
- `min_importance`: 最小重要性级别 (0-5) (可选)
- `page`: 页码 (默认1)
- `page_size`: 每页数量 (默认20)

### 3. 获取今日公告
```http
GET /api/announcement/today?min_importance=3
Authorization: Bearer <token>
```

### 4. 获取重要公告
```http
GET /api/announcement/important?days=7&min_importance=3
Authorization: Bearer <token>
```

**参数**:
- `days`: 查询天数 (1-30, 默认7)
- `min_importance`: 最小重要性级别 (0-5, 默认3)

### 5. 获取指定股票的公告
```http
GET /api/announcement/stock/600519?days=30
Authorization: Bearer <token>
```

**参数**:
- `days`: 查询天数 (1-365, 默认30)

### 6. 评估监控规则
```http
POST /api/announcement/monitor/evaluate
Authorization: Bearer <token>
```

### 7. 获取公告统计信息
```http
GET /api/announcement/stats
Authorization: Bearer <token>
```

### 8. 获取支持的公告类型
```http
GET /api/announcement/types
Authorization: Bearer <token>
```

---

## 自选股管理API

**基础路径**: `/api/watchlist`

### 1. 获取自选股列表
```http
GET /api/watchlist
Authorization: Bearer <token>
```

### 2. 添加自选股
```http
POST /api/watchlist
Content-Type: application/json

{
  "symbol": "600519",
  "display_name": "贵州茅台",
  "exchange": "SH",
  "market": "CN",
  "notes": "重点关注",
  "group_id": 1,
  "group_name": "白酒板块"
}
Authorization: Bearer <token>
```

### 3. 删除自选股
```http
DELETE /api/watchlist/1
Authorization: Bearer <token>
```

### 4. 更新自选股备注
```http
PUT /api/watchlist/1/notes
Content-Type: application/json

{
  "notes": "已买入，持有中"
}
Authorization: Bearer <token>
```

### 5. 创建分组
```http
POST /api/watchlist/groups
Content-Type: application/json

{
  "name": "科技股",
  "description": "科技创新相关股票"
}
Authorization: Bearer <token>
```

### 6. 获取分组列表
```http
GET /api/watchlist/groups
Authorization: Bearer <token>
```

### 7. 更新分组
```http
PUT /api/watchlist/groups/1
Content-Type: application/json

{
  "name": "科技股-更新",
  "description": "科技创新相关股票（含AI概念）"
}
Authorization: Bearer <token>
```

### 8. 删除分组
```http
DELETE /api/watchlist/groups/1
Authorization: Bearer <token>
```

### 9. 移动股票到分组
```http
PUT /api/watchlist/1/group
Content-Type: application/json

{
  "group_id": 2
}
Authorization: Bearer <token>
```

### 10. 获取股票详情
```http
GET /api/watchlist/1
Authorization: Bearer <token>
```

---

## 机器学习API

**基础路径**: `/ml`

### 1. 获取通达信股票数据
```http
POST /ml/tdx/data
Content-Type: application/json

{
  "stock_code": "000001",
  "market": "sh"
}
Authorization: Bearer <token>
```

### 2. 列出可用的股票代码
```http
GET /ml/tdx/stocks/sh
Authorization: Bearer <token>
```

### 3. 生成特征数据
```http
POST /ml/features/generate
Content-Type: application/json

{
  "stock_code": "000001",
  "market": "sh",
  "step": 10,
  "include_indicators": true
}
Authorization: Bearer <token>
```

### 4. 训练预测模型
```http
POST /ml/models/train
Content-Type: application/json

{
  "stock_code": "000001",
  "market": "sh",
  "step": 10,
  "test_size": 0.2,
  "model_name": "price_prediction_model",
  "model_params": {
    "n_estimators": 100,
    "max_depth": 10
  }
}
Authorization: Bearer <token>
```

### 5. 使用模型进行预测
```http
POST /ml/models/predict
Content-Type: application/json

{
  "model_name": "price_prediction_model",
  "stock_code": "000001",
  "market": "sh",
  "days": 5
}
Authorization: Bearer <token>
```

### 6. 列出所有模型
```http
GET /ml/models
Authorization: Bearer <token>
```

### 7. 获取模型详情
```http
GET /ml/models/price_prediction_model
Authorization: Bearer <token>
```

### 8. 超参数搜索
```http
POST /ml/models/hyperparameter-search
Content-Type: application/json

{
  "stock_code": "000001",
  "market": "sh",
  "step": 10,
  "cv": 5,
  "param_grid": {
    "n_estimators": [50, 100, 200],
    "max_depth": [5, 10, 15]
  }
}
Authorization: Bearer <token>
```

### 9. 评估模型性能
```http
POST /ml/models/evaluate
Content-Type: application/json

{
  "model_name": "price_prediction_model",
  "stock_code": "000001",
  "market": "sh"
}
Authorization: Bearer <token>
```

---

## 风险管理API

**基础路径**: `/api/v1/risk`

### 1. 计算VaR和CVaR
```http
GET /api/v1/risk/var-cvar?entity_type=portfolio&entity_id=1&confidence_level=0.95
Authorization: Bearer <token>
```

**参数**:
- `entity_type`: 实体类型 ('backtest', 'portfolio', 'strategy')
- `entity_id`: 实体ID
- `confidence_level`: 置信水平 (0.90, 0.95, 0.99)

**返回**:
```json
{
  "var_95_hist": -0.0289,
  "var_95_param": -0.0309,
  "var_99_hist": -0.0385,
  "cvar_95": -0.0360,
  "cvar_99": -0.0432
}
```

### 2. 计算Beta系数
```http
GET /api/v1/risk/beta?entity_type=portfolio&entity_id=1&market_index=000001
Authorization: Bearer <token>
```

**返回**:
```json
{
  "beta": 1.23,
  "correlation": 0.85
}
```

### 3. 获取风险仪表盘数据
```http
GET /api/v1/risk/dashboard
Authorization: Bearer <token>
```

**返回**:
- 最新风险指标
- 活跃预警规则
- 风险历史数据（最近30天）

### 4. 获取风险指标历史数据
```http
GET /api/v1/risk/metrics/history?entity_type=portfolio&entity_id=1&start_date=2025-09-01&end_date=2025-10-31
Authorization: Bearer <token>
```

### 5. 获取风险预警规则列表
```http
GET /api/v1/risk/alerts?is_active=true
Authorization: Bearer <token>
```

**参数**:
- `is_active`: 是否只显示活跃规则 (可选)

### 6. 创建风险预警规则
```http
POST /api/v1/risk/alerts
Content-Type: application/json

{
  "name": "VaR告警",
  "metric_type": "var_95",
  "threshold_value": 0.05,
  "comparison_operator": "greater_than",
  "entity_type": "portfolio",
  "entity_id": 1,
  "notification_config": {
    "email": true,
    "webhook": false
  }
}
Authorization: Bearer <token>
```

### 7. 更新风险预警规则
```http
PUT /api/v1/risk/alerts/1
Content-Type: application/json

{
  "name": "VaR告警-更新",
  "threshold_value": 0.03
}
Authorization: Bearer <token>
```

### 8. 删除风险预警规则
```http
DELETE /api/v1/risk/alerts/1
Authorization: Bearer <token>
```

### 9. 发送测试通知
```http
POST /api/v1/risk/notifications/test
Content-Type: application/json

{
  "notification_type": "email",
  "config_data": {
    "email": "test@example.com"
  }
}
Authorization: Bearer <token>
```

**通知类型**:
- `email`: 邮件通知
- `webhook`: Webhook通知

---

## 通知API

**基础路径**: `/api/notification`

### 1. 发送通知
```http
POST /api/notification/send
Content-Type: application/json

{
  "type": "email",
  "recipient": "user@example.com",
  "title": "告警通知",
  "content": "您的投资组合VaR超过阈值",
  "priority": "high"
}
Authorization: Bearer <token>
```

### 2. 获取通知历史
```http
GET /api/notification/history?type=email&status=sent&limit=50
Authorization: Bearer <token>
```

**参数**:
- `type`: 通知类型 (email/webhook/sms) (可选)
- `status`: 状态 (sent/failed/pending) (可选)
- `limit`: 返回数量 (默认50)

### 3. 获取通知模板
```http
GET /api/notification/templates
Authorization: Bearer <token>
```

### 4. 创建通知模板
```http
POST /api/notification/templates
Content-Type: application/json

{
  "name": "风险告警模板",
  "type": "email",
  "subject": "风险告警：{title}",
  "content": "您的{entity_type} {entity_id} {message}",
  "variables": ["title", "entity_type", "entity_id", "message"]
}
Authorization: Bearer <token>
```

---

## 股票搜索API

**基础路径**: `/api/stock-search`

### 1. 搜索股票
```http
GET /api/stock-search?query=平安&exchange=SZSE&limit=20
Authorization: Bearer <token>
```

**参数**:
- `query`: 搜索关键词（股票代码或名称）
- `exchange`: 交易所筛选 (SSE/SZSE) (可选)
- `security_type`: 证券类型筛选 (可选)
- `limit`: 返回数量限制 (默认20)

### 2. 获取股票详细信息
```http
GET /api/stock-search/info/600519
Authorization: Bearer <token>
```

### 3. 获取股票财务数据
```http
GET /api/stock-search/financial/600519?year=2024&quarter=3
Authorization: Bearer <token>
```

**参数**:
- `year`: 年份 (4位数字)
- `quarter`: 季度 (1-4)

### 4. 获取股票实时行情
```http
GET /api/stock-search/realtime/600519
Authorization: Bearer <token>
```

### 5. 获取股票历史行情
```http
GET /api/stock-search/historical/600519?start_date=2025-10-01&end_date=2025-10-31&adjust=qfq
Authorization: Bearer <token>
```

**参数**:
- `start_date`: 开始日期 YYYY-MM-DD
- `end_date`: 结束日期 YYYY-MM-DD
- `adjust`: 复权类型 (qfq/hfq/空字符串)

### 6. 批量获取股票数据
```http
POST /api/stock-search/batch
Content-Type: application/json

{
  "symbols": ["600519", "000001", "600036"],
  "data_types": ["realtime", "basic_info"],
  "filters": {
    "market_cap_min": 100000000000
  }
}
Authorization: Bearer <token>
```

### 7. 获取股票概念板块
```http
GET /api/stock-search/concepts/600519
Authorization: Bearer <token>
```

### 8. 获取行业分类
```http
GET /api/stock-search/industries
Authorization: Bearer <token>
```

---

## 缓存API

**基础路径**: `/api/cache`

### 1. 获取缓存统计
```http
GET /api/cache/stats
Authorization: Bearer <token>
```

**返回**:
- 缓存命中率
- 缓存大小
- 缓存项数量
- 内存使用情况

### 2. 清理缓存
```http
DELETE /api/cache/clear?pattern=market_data&confirm=true
Authorization: Bearer <token>
```

**参数**:
- `pattern`: 缓存键匹配模式 (可选)
- `confirm`: 确认清理 (必须为true)

### 3. 获取缓存项详情
```http
GET /api/cache/key/market_quotes_600519
Authorization: Bearer <token>
```

### 4. 预热缓存
```http
POST /api/cache/warmup
Content-Type: application/json

{
  "keys": [
    "market_quotes_000001",
    "market_quotes_600519"
  ]
}
Authorization: Bearer <token>
```

### 5. 更新缓存配置
```http
PUT /api/cache/config
Content-Type: application/json

{
  "default_ttl": 300,
  "max_size": 10000,
  "eviction_policy": "LRU"
}
Authorization: Bearer <token>
```

### 6. 获取缓存性能指标
```http
GET /api/cache/performance
Authorization: Bearer <token>
```

**返回**:
- 平均响应时间
- QPS (每秒查询数)
- 缓存穿透率
- 缓存击穿率

---

## 多数据源API

**基础路径**: `/api/multi-source`

### 1. 获取所有数据源健康状态
```http
GET /api/multi-source/health
Authorization: Bearer <token>
```

**返回**:
```json
[
  {
    "source_type": "eastmoney",
    "status": "healthy",
    "enabled": true,
    "priority": 1,
    "success_rate": 0.95,
    "avg_response_time": 120.5,
    "error_count": 5,
    "last_check": "2025-10-15T10:30:00Z",
    "supported_categories": ["realtime_quote", "fund_flow"]
  }
]
```

### 2. 获取指定数据源健康状态
```http
GET /api/multi-source/health/eastmoney
Authorization: Bearer <token>
```

### 3. 获取实时行情（多数据源）
```http
GET /api/multi-source/realtime-quote?symbols=600519,000001&source=eastmoney
Authorization: Bearer <token>
```

**参数**:
- `symbols`: 股票代码，逗号分隔 (可选)
- `source`: 指定数据源 (eastmoney/cninfo/akshare/wencai) (可选)

### 4. 获取资金流向（多数据源）
```http
GET /api/multi-source/fund-flow?symbol=600519&timeframe=今日&source=eastmoney
Authorization: Bearer <token>
```

### 5. 获取龙虎榜（多数据源）
```http
GET /api/multi-source/dragon-tiger?date=2025-10-15&source=eastmoney
Authorization: Bearer <token>
```

### 6. 获取涨停股票池
```http
GET /api/multi-source/limit-up?date=2025-10-15&source=eastmoney
Authorization: Bearer <token>
```

### 7. 获取跌停股票池
```http
GET /api/multi-source/limit-down?date=2025-10-15&source=eastmoney
Authorization: Bearer <token>
```

### 8. 获取新股申购日历
```http
GET /api/multi-source/ipo-calendar?year=2025&month=10&source=eastmoney
Authorization: Bearer <token>
```

### 9. 获取财报预约披露
```http
GET /api/multi-source/earnings-schedule?year=2025&quarter=3&source=eastmoney
Authorization: Bearer <token>
```

### 10. 获取业绩快报
```http
GET /api/multi-source/performance-express?symbol=600519&year=2025&source=eastmoney
Authorization: Bearer <token>
```

### 11. 获取业绩预告
```http
GET /api/multi-source/performance-forecast?symbol=600519&year=2025&source=eastmoney
Authorization: Bearer <token>
```

### 12. 获取分红配送
```http
GET /api/multi-source/dividend?symbol=600519&year=2024&source=eastmoney
Authorization: Bearer <token>
```

### 13. 获取解禁股日历
```http
GET /api/multi-source/unlock-calendar?year=2025&month=10&source=eastmoney
Authorization: Bearer <token>
```

### 14. 获取机构调研
```http
GET /api/multi-source/institution-research?symbol=600519&limit=20&source=eastmoney
Authorization: Bearer <token>
```

### 15. 获取股东人数变化
```http
GET /api/multi-source/shareholder-change?symbol=600519&limit=10&source=eastmoney
Authorization: Bearer <token>
```

---

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

### 分页响应
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

## 认证说明

### 登录获取Token
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 使用Token访问API
```bash
curl -X GET "http://localhost:8000/api/market/quotes" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 预置用户
- **管理员**: username=admin, password=admin123
- **普通用户**: username=user, password=user123

---

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| UNAUTHORIZED | 401 | 未认证或Token无效 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 422 | 请求参数验证失败 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超过限制 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务暂时不可用 |

---

## 速率限制

- **认证API**: 每分钟10次
- **市场数据API**: 每分钟60次
- **查询密集型API**: 每分钟30次
- **数据修改API**: 每分钟20次

---

## 备注

1. 所有时间格式均为ISO 8601格式 (`YYYY-MM-DDTHH:mm:ssZ`)
2. 所有日期格式为`YYYY-MM-DD`
3. 股票代码支持6位数字或带交易所后缀格式
4. 缓存端点使用适当的TTL以平衡实时性和性能
5. SSE端点支持客户端自动重连
6. 监控端点提供Prometheus兼容的指标格式

**最后更新**: 2025-11-08
**API版本**: v2.1.0
**文档版本**: 1.0.0
