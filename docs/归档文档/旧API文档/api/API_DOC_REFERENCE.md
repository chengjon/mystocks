# MyStocks API 文档参考样式

## 文档结构示例

### 📋 目录导航
- [监控系统](#1-监控系统)
- [技术分析](#2-技术分析)
- [多数据源](#3-多数据源)
- [市场数据](#4-市场数据)
- [策略管理](#5-策略管理)
- [系统管理](#6-系统管理)

---

## 1. 监控系统

### 🔔 告警规则管理

#### GET /api/monitoring/alert-rules
获取告警规则列表

**查询参数：**
- `rule_type` (string, 可选): 规则类型
- `is_active` (boolean, 可选): 是否启用

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "rule_name": "茅台涨停监控",
      "rule_type": "limit_up",
      "symbol": "600519",
      "is_active": true,
      "priority": 5
    }
  ]
}
```

#### POST /api/monitoring/alert-rules
创建告警规则

**请求体：**
```json
{
  "rule_name": "茅台涨停监控",
  "rule_type": "limit_up",
  "symbol": "600519",
  "stock_name": "贵州茅台",
  "parameters": {"include_st": false},
  "notification_config": {"channels": ["ui", "sound"]},
  "priority": 5,
  "is_active": true
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "告警规则创建成功",
  "data": {
    "id": 1,
    "rule_name": "茅台涨停监控"
  }
}
```

#### PUT /api/monitoring/alert-rules/{rule_id}
更新告警规则

**路径参数：**
- `rule_id` (integer): 规则ID

**请求体：**
```json
{
  "is_active": false,
  "priority": 3
}
```

#### DELETE /api/monitoring/alert-rules/{rule_id}
删除告警规则

---

### 📊 实时监控数据

#### GET /api/monitoring/realtime/{symbol}
获取单只股票实时监控数据

**路径参数：**
- `symbol` (string): 股票代码

**响应示例：**
```json
{
  "symbol": "600519",
  "price": 1680.50,
  "change_percent": 2.34,
  "volume": 1234567,
  "timestamp": "2025-11-11T14:30:00"
}
```

#### GET /api/monitoring/realtime
获取实时监控数据列表

**查询参数：**
- `symbols` (string, 可选): 股票代码列表，逗号分隔
- `limit` (integer, 可选): 返回数量限制，默认100
- `is_limit_up` (boolean, 可选): 仅返回涨停股票
- `is_limit_down` (boolean, 可选): 仅返回跌停股票

#### POST /api/monitoring/realtime/fetch
手动触发获取实时数据

**请求体：**
```json
{
  "symbols": ["600519", "000001", "600000"]
}
```

---

### 🐅 龙虎榜数据

#### GET /api/monitoring/dragon-tiger
获取龙虎榜数据

**查询参数：**
- `trade_date` (date, 可选): 交易日期，默认今天
- `symbol` (string, 可选): 股票代码
- `min_net_amount` (float, 可选): 最小净买入额
- `limit` (integer, 可选): 返回数量限制

#### POST /api/monitoring/dragon-tiger/fetch
手动获取龙虎榜数据

---

## 2. 技术分析

### 📈 指标查询

#### GET /api/technical/{symbol}/indicators
获取股票所有技术指标

**路径参数：**
- `symbol` (string): 股票代码

**查询参数：**
- `period` (string, 可选): 数据周期 (daily/weekly/monthly)，默认daily
- `start_date` (string, 可选): 开始日期 YYYY-MM-DD
- `end_date` (string, 可选): 结束日期 YYYY-MM-DD

**响应示例：**
```json
{
  "symbol": "600519",
  "latest_price": 1680.50,
  "latest_date": "2025-11-11",
  "trend": {
    "ma5": 1675.20,
    "ma10": 1668.80,
    "macd": 15.60,
    "macd_signal": 12.30
  },
  "momentum": {
    "rsi6": 65.4,
    "kdj_k": 72.1,
    "kdj_d": 68.5
  },
  "volatility": {
    "bb_upper": 1720.50,
    "bb_middle": 1680.50,
    "bb_lower": 1640.50
  }
}
```

#### GET /api/technical/{symbol}/trend
获取趋势指标

#### GET /api/technical/{symbol}/momentum
获取动量指标

#### GET /api/technical/{symbol}/volatility
获取波动性指标

#### GET /api/technical/{symbol}/volume
获取成交量指标

### 🔔 交易信号

#### GET /api/technical/{symbol}/signals
获取交易信号

**响应示例：**
```json
{
  "overall_signal": "buy",
  "signal_strength": 0.75,
  "signals": [
    {
      "type": "macd_golden_cross",
      "signal": "buy",
      "strength": 0.8
    },
    {
      "type": "rsi_oversold",
      "signal": "buy",
      "strength": 0.7
    }
  ]
}
```

### 📊 历史数据

#### GET /api/technical/{symbol}/history
获取股票历史行情数据

**查询参数：**
- `period` (string, 可选): 周期 (daily/weekly/monthly)
- `start_date` (string, 可选): 开始日期
- `end_date` (string, 可选): 结束日期
- `limit` (integer, 可选): 返回数据点数量，默认100

**响应示例：**
```json
{
  "symbol": "600519",
  "period": "daily",
  "count": 100,
  "dates": ["2025-10-01", "2025-10-02", ...],
  "data": [
    {
      "open": 1670.0,
      "close": 1680.5,
      "high": 1690.0,
      "low": 1665.0,
      "volume": 1234567
    }
  ]
}
```

### 🏭 批量处理

#### POST /api/technical/batch/indicators
批量获取多只股票技术指标

**查询参数：**
- `symbols` (array): 股票代码列表，最多20只

---

## 3. 多数据源

### 💊 数据源健康监控

#### GET /api/multi-source/health
获取所有数据源健康状态

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "source_type": "akshare",
      "status": "healthy",
      "enabled": true,
      "priority": 1,
      "success_rate": 98.5,
      "avg_response_time": 0.45,
      "last_check": "2025-11-11T14:30:00"
    }
  ]
}
```

#### GET /api/multi-source/realtime-quote
获取实时行情（多数据源）

#### GET /api/multi-source/fund-flow
获取资金流向（多数据源）

---

## 4. 市场数据

### 📋 股票搜索

#### GET /api/stock-search
搜索股票

**查询参数：**
- `q` (string): 搜索关键词
- `limit` (integer, 可选): 返回数量限制

### 📊 基础数据

#### GET /api/data/stock-info
获取股票基本信息

#### GET /api/data/daily-kline
获取日线数据

---

## 5. 策略管理

### 🎯 策略定义

#### GET /api/strategy
获取策略列表

#### POST /api/strategy
创建策略

#### PUT /api/strategy/{strategy_id}
更新策略

#### DELETE /api/strategy/{strategy_id}
删除策略

### 🧪 回测

#### POST /api/strategy/{strategy_id}/backtest
执行策略回测

---

## 6. 系统管理

### ⚙️ 系统状态

#### GET /api/system/status
获取系统状态

**响应示例：**
```json
{
  "success": true,
  "data": {
    "database_status": "healthy",
    "monitoring_active": true,
    "api_version": "3.0.0",
    "uptime": "7d 12h 34m"
  }
}
```

#### GET /api/system/metrics
获取系统指标

### 📧 通知管理

#### GET /api/notification/channels
获取通知渠道

#### POST /api/notification/send
发送通知

---

## 错误响应格式

所有API错误响应统一格式：

```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "股票代码格式错误",
    "details": "股票代码必须是6位数字"
  },
  "timestamp": "2025-11-11T14:30:00Z"
}
```

## 通用查询参数

- `limit` (integer): 返回数量限制，默认100，最大1000
- `offset` (integer): 偏移量，用于分页
- `sort` (string): 排序字段
- `order` (string): 排序方向 (asc/desc)

## 状态码说明

- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 资源不存在
- `500`: 服务器内部错误

---

*这是API文档的参考样式，请确认是否符合您的要求。确认后我将基于项目实际API创建完整的文档。*
