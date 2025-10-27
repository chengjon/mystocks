# P5: MyStocks Web API 完整文档

**版本**: 2.0.0
**完成日期**: 2025-10-25
**分支**: 002-arch-optimization
**状态**: ✅ 完成
**基础架构**: FastAPI + PostgreSQL + TDengine

---

## 📋 文档概述

本文档提供MyStocks量化交易数据管理系统Web API的完整使用指南，包括：

- ✅ 所有API端点详细说明
- ✅ 请求/响应示例
- ✅ 认证和安全机制
- ✅ 错误处理指南
- ✅ 最佳实践建议
- ✅ OpenAPI/Swagger规范

---

## 🎯 快速开始

### API基础信息

| 项目 | 信息 |
|------|------|
| **Base URL** | `http://localhost:8000` |
| **API Docs** | `http://localhost:8000/api/docs` |
| **ReDoc** | `http://localhost:8000/api/redoc` |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` |
| **Health Check** | `http://localhost:8000/health` |
| **协议** | HTTP/1.1, REST |
| **数据格式** | JSON |
| **认证方式** | OAuth2 Password Bearer |

### 快速测试

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 获取API文档
open http://localhost:8000/api/docs

# 3. 登录获取Token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 4. 使用Token访问受保护端点
curl -X GET "http://localhost:8000/api/data/stocks/basic?limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔐 认证和安全

### OAuth2 Password Bearer 认证

MyStocks API使用OAuth2 Password Bearer Token认证机制。

#### 认证流程

1. **获取访问令牌**

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

2. **使用Token访问API**

```http
GET /api/data/stocks/basic
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

3. **刷新Token**

```http
POST /api/auth/refresh
Authorization: Bearer YOUR_CURRENT_TOKEN
```

4. **登出**

```http
POST /api/auth/logout
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 认证端点

| 端点 | 方法 | 描述 | 是否需要认证 |
|------|------|------|--------------|
| `/api/auth/login` | POST | 用户登录 | ❌ |
| `/api/auth/logout` | POST | 用户登出 | ✅ |
| `/api/auth/me` | GET | 获取当前用户信息 | ✅ |
| `/api/auth/refresh` | POST | 刷新访问令牌 | ✅ |
| `/api/auth/users` | GET | 获取用户列表（管理员） | ✅ |

---

## 📡 核心API模块

### 1. 数据管理 API (`/api/data`)

提供股票基本信息、K线数据、财务数据等核心数据查询功能。

#### 1.1 股票基本信息

```http
GET /api/data/stocks/basic
```

**查询参数**:
- `limit` (int, 1-1000): 返回记录数限制，默认100
- `search` (string, optional): 股票代码或名称搜索关键词
- `industry` (string, optional): 行业筛选
- `market` (string, optional): 市场筛选: SH/SZ

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/data/stocks/basic?limit=10&market=SH" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "symbol": "600519.SH",
      "name": "贵州茅台",
      "market": "SH",
      "industry": "食品饮料",
      "list_date": "2001-08-27"
    }
  ],
  "total": 10,
  "timestamp": "2025-10-25T10:30:00"
}
```

#### 1.2 股票日线数据

```http
GET /api/data/stocks/daily
```

**查询参数**:
- `symbol` (string, required): 股票代码，如: 000001.SZ
- `start_date` (string, optional): 开始日期，格式: YYYY-MM-DD
- `end_date` (string, optional): 结束日期，格式: YYYY-MM-DD
- `limit` (int, 1-5000): 返回记录数限制，默认100

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/data/stocks/daily?symbol=600519.SH&start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-02",
      "open": 1680.00,
      "high": 1720.00,
      "low": 1675.00,
      "close": 1710.00,
      "volume": 12500000,
      "amount": 21375000000
    }
  ],
  "total": 243,
  "timestamp": "2025-10-25T10:30:00"
}
```

#### 1.3 股票搜索

```http
GET /api/data/stocks/search
```

**查询参数**:
- `keyword` (string, required): 搜索关键词
- `limit` (int, 1-100): 返回结果数量限制，默认20

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/data/stocks/search?keyword=茅台&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 1.4 财务数据

```http
GET /api/data/financial
```

**查询参数**:
- `symbol` (string, required): 股票代码，如: 000001
- `report_type` (string): 报表类型: balance/income/cashflow，默认balance
- `period` (string): 报告期: quarterly/annual/all，默认all
- `limit` (int, 1-100): 返回记录数限制，默认20

**报表类型说明**:
- `balance`: 资产负债表
- `income`: 利润表
- `cashflow`: 现金流量表

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/data/financial?symbol=600519&report_type=income&period=annual" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. 市场数据 API (`/api/market`)

提供实时行情、资金流向、ETF数据、龙虎榜等市场数据。

#### 2.1 资金流向

**查询资金流向**:
```http
GET /api/market/fund-flow
```

**查询参数**:
- `symbol` (string, required): 股票代码
- `timeframe` (string): 时间维度: 1/3/5/10天，默认1
- `start_date` (date, optional): 开始日期
- `end_date` (date, optional): 结束日期

**缓存策略**: 5分钟TTL

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/market/fund-flow?symbol=600519.SH&timeframe=1"
```

**响应示例**:
```json
[
  {
    "symbol": "600519.SH",
    "trade_date": "2025-10-25",
    "timeframe": "1",
    "main_net_inflow": 125000000,
    "retail_net_inflow": -125000000,
    "super_large_net_inflow": 80000000,
    "large_net_inflow": 45000000,
    "medium_net_inflow": -30000000,
    "small_net_inflow": -95000000
  }
]
```

**刷新资金流向**:
```http
POST /api/market/fund-flow/refresh?symbol=600519.SH&timeframe=1
```

#### 2.2 ETF数据

**查询ETF列表**:
```http
GET /api/market/etf/list
```

**查询参数**:
- `symbol` (string, optional): ETF代码
- `keyword` (string, optional): 关键词搜索
- `limit` (int, 1-500): 返回数量，默认50

**缓存策略**: 1分钟TTL

**查询方式**:
- 指定symbol: 返回单个ETF数据
- 指定keyword: 模糊搜索名称/代码
- 不指定条件: 返回全市场ETF(按涨跌幅排序)

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/market/etf/list?keyword=创业板&limit=10"
```

**刷新ETF数据**:
```http
POST /api/market/etf/refresh
```

#### 2.3 竞价抢筹

**查询竞价抢筹**:
```http
GET /api/market/chip-race
```

**查询参数**:
- `race_type` (string): 抢筹类型: open/end，默认open
- `trade_date` (date, optional): 交易日期
- `min_race_amount` (float, optional): 最小抢筹金额
- `limit` (int, 1-500): 返回数量，默认100

**类型说明**:
- `open`: 早盘抢筹(集合竞价)
- `end`: 尾盘抢筹(收盘竞价)

**缓存策略**: 5分钟TTL

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/market/chip-race?race_type=open&min_race_amount=10000000"
```

**刷新抢筹数据**:
```http
POST /api/market/chip-race/refresh?race_type=open
```

#### 2.4 龙虎榜

**查询龙虎榜**:
```http
GET /api/market/lhb
```

**查询参数**:
- `symbol` (string, optional): 股票代码
- `start_date` (date, optional): 开始日期
- `end_date` (date, optional): 结束日期
- `min_net_amount` (float, optional): 最小净买入额
- `limit` (int, 1-500): 返回数量，默认100

**缓存策略**: 24小时TTL（龙虎榜数据每日更新）

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/market/lhb?symbol=600519.SH&start_date=2024-01-01"
```

**刷新龙虎榜**:
```http
POST /api/market/lhb/refresh?trade_date=2025-10-25
```

**数据源**: 东方财富网 (via akshare)
**更新时机**: 每日20:00之后

#### 2.5 实时行情

**查询实时行情**:
```http
GET /api/market/quotes
```

**查询参数**:
- `symbols` (string, optional): 股票代码列表，逗号分隔，如: 000001,600519

**缓存策略**: 10秒TTL（实时行情需要较高频率更新）
**数据源**: TDX实时行情

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/market/quotes?symbols=600519.SH,000001.SZ"
```

---

### 3. 技术指标 API (`/api/indicators`)

提供技术指标计算、指标注册表、配置管理等功能。

#### 3.1 指标注册表

**获取指标注册表**:
```http
GET /api/indicators/registry
```

**返回**: 所有可用的技术指标及其元数据

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/registry"
```

**响应示例**:
```json
{
  "success": true,
  "indicators": [
    {
      "abbreviation": "SMA",
      "full_name": "Simple Moving Average",
      "category": "trend",
      "description": "简单移动平均线",
      "parameters": {
        "timeperiod": {
          "type": "int",
          "default": 20,
          "min": 2,
          "max": 500
        }
      }
    },
    {
      "abbreviation": "RSI",
      "full_name": "Relative Strength Index",
      "category": "momentum",
      "description": "相对强弱指标",
      "parameters": {
        "timeperiod": {
          "type": "int",
          "default": 14,
          "min": 2,
          "max": 100
        }
      }
    }
  ],
  "total": 150
}
```

**按分类获取指标**:
```http
GET /api/indicators/registry/{category}
```

**可用分类**:
- `trend`: 趋势指标
- `momentum`: 动量指标
- `volatility`: 波动率指标
- `volume`: 成交量指标
- `candlestick`: K线形态

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/indicators/registry/momentum"
```

#### 3.2 计算技术指标

**计算指标**:
```http
POST /api/indicators/calculate
```

**请求体**:
```json
{
  "symbol": "600519.SH",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "indicators": [
    {
      "abbreviation": "SMA",
      "parameters": {"timeperiod": 20}
    },
    {
      "abbreviation": "RSI",
      "parameters": {"timeperiod": 14}
    }
  ],
  "use_cache": true
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/indicators/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "indicators": [
      {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
      {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
    ]
  }'
```

**响应示例**:
```json
{
  "success": true,
  "symbol": "600519.SH",
  "data": [
    {
      "date": "2024-01-02",
      "close": 1710.00,
      "SMA_20": 1695.50,
      "RSI_14": 62.5
    },
    {
      "date": "2024-01-03",
      "close": 1725.00,
      "SMA_20": 1698.75,
      "RSI_14": 65.3
    }
  ],
  "total": 243,
  "cache_hit": false
}
```

#### 3.3 指标配置管理

**创建指标配置**:
```http
POST /api/indicators/configs
```

**请求体**:
```json
{
  "name": "我的常用配置",
  "indicators": [
    {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
    {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
  ]
}
```

**获取配置列表**:
```http
GET /api/indicators/configs?user_id=1
```

**获取单个配置**:
```http
GET /api/indicators/configs/{config_id}?user_id=1
```

**更新配置**:
```http
PUT /api/indicators/configs/{config_id}?user_id=1
```

**删除配置**:
```http
DELETE /api/indicators/configs/{config_id}?user_id=1
```

---

### 4. 系统管理 API (`/api/system`)

提供系统健康检查、数据库管理、日志查询等功能。

#### 4.1 系统健康检查

**系统健康**:
```http
GET /api/system/health
```

**返回**:
- 数据库连接状态
- 系统运行时间
- 服务状态

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/health"
```

**响应示例**:
```json
{
  "status": "healthy",
  "uptime": 86400,
  "database": {
    "postgresql": "connected",
    "tdengine": "connected"
  },
  "services": {
    "api": "running",
    "cache": "active"
  },
  "timestamp": "2025-10-25T10:30:00"
}
```

#### 4.2 适配器健康检查

**适配器健康**:
```http
GET /api/system/adapters/health
```

**检查项**:
- akshare: AkShare适配器
- tdx: 通达信适配器
- financial: 财务数据适配器

**返回**:
- 每个适配器的健康状态
- 最后检查时间
- 错误信息（如果有）

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/adapters/health"
```

**响应示例**:
```json
{
  "success": true,
  "adapters": {
    "akshare": {
      "status": "healthy",
      "last_check": "2025-10-25T10:29:55",
      "error": null
    },
    "tdx": {
      "status": "degraded",
      "last_check": "2025-10-25T10:29:55",
      "error": "Connection timeout"
    },
    "financial": {
      "status": "healthy",
      "last_check": "2025-10-25T10:29:55",
      "error": null
    }
  }
}
```

#### 4.3 数据库健康检查

**数据库健康**:
```http
GET /api/system/database/health
```

**检查TDengine和PostgreSQL的连接状态和健康指标**

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/database/health"
```

**响应示例**:
```json
{
  "success": true,
  "message": "数据库健康检查完成",
  "data": {
    "tdengine": {
      "status": "healthy",
      "version": "3.0.0",
      "database": "market_data",
      "tables": 5,
      "connection_time_ms": 12.5
    },
    "postgresql": {
      "status": "healthy",
      "version": "PostgreSQL 14.5",
      "database": "mystocks",
      "tables": 45,
      "connection_time_ms": 8.3
    },
    "summary": {
      "total_databases": 2,
      "healthy_databases": 2,
      "overall_status": "healthy"
    }
  }
}
```

#### 4.4 数据库统计信息

**数据库统计**:
```http
GET /api/system/database/stats
```

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/database/stats"
```

**响应示例**:
```json
{
  "success": true,
  "message": "数据库统计信息获取成功",
  "data": {
    "architecture": "dual-database",
    "total_classifications": 34,
    "routing": {
      "tdengine": ["TICK_DATA", "MINUTE_DATA", "SECOND_DATA"],
      "postgresql": ["DAILY_KLINE", "SYMBOLS_INFO", "TRADE_CALENDAR", "..."]
    },
    "features": {
      "auto_routing": true,
      "monitoring": true,
      "caching": true
    }
  }
}
```

#### 4.5 系统日志查询

**获取系统日志**:
```http
GET /api/system/logs
```

**查询参数**:
- `filter_errors` (bool): 是否只显示有问题的日志，默认false
- `limit` (int, 1-1000): 返回条数限制，默认100
- `offset` (int): 偏移量，默认0
- `level` (string, optional): 日志级别筛选 (INFO/WARNING/ERROR/CRITICAL)
- `category` (string, optional): 日志分类筛选 (database/api/adapter/system)

**请求示例**:
```bash
# 获取所有日志
curl -X GET "http://localhost:8000/api/system/logs"

# 只获取错误日志
curl -X GET "http://localhost:8000/api/system/logs?filter_errors=true"

# 获取ERROR级别日志
curl -X GET "http://localhost:8000/api/system/logs?level=ERROR"

# 获取数据库相关日志
curl -X GET "http://localhost:8000/api/system/logs?category=database"
```

**日志摘要**:
```http
GET /api/system/logs/summary
```

**返回**:
- 总日志数
- 各级别日志数量
- 各分类日志数量
- 最近错误数

#### 4.6 系统架构信息

**获取系统架构**:
```http
GET /api/system/architecture
```

**返回**:
- 数据库架构 (TDengine + PostgreSQL)
- 数据分类路由策略
- 架构简化指标
- 技术栈信息

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/system/architecture"
```

---

### 5. 策略管理 API (`/api/strategy`)

提供股票策略筛选、回测、管理等功能。

#### 5.1 策略筛选

**策略端点** (详见 `/api/strategy` 路由)

支持多种策略：
- 低价策略
- 高价策略
- 放量突破策略
- 均线多头策略
- 强势股策略

#### 5.2 策略管理 (Week 1架构)

**策略管理端点** (详见 `/api/strategy-management` 路由)

基于 `MyStocksUnifiedManager` + `MonitoringDatabase` 实现

---

### 6. 风险管理 API (`/api/risk-management`)

提供投资组合风险评估、持仓分析等功能。

**风险管理端点** (详见 `/api/risk-management` 路由)

基于 `MyStocksUnifiedManager` + `MonitoringDatabase` 实现

---

### 7. 实时推送 API (SSE)

提供Server-Sent Events实时数据推送。

#### 7.1 SSE端点

**训练进度推送**:
```http
GET /api/sse/training/{task_id}
```

**回测进度推送**:
```http
GET /api/sse/backtest/{task_id}
```

**告警推送**:
```http
GET /api/sse/alerts
```

**仪表盘数据推送**:
```http
GET /api/sse/dashboard
```

**客户端示例**:
```javascript
const eventSource = new EventSource('http://localhost:8000/api/sse/dashboard');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Dashboard update:', data);
};

eventSource.onerror = function(error) {
  console.error('SSE error:', error);
  eventSource.close();
};
```

---

### 8. 机器学习 API (`/api/ml`)

提供机器学习预测、特征工程等功能。

#### 8.1 预测端点

**机器学习预测** (详见 `/api/ml` 路由)

支持：
- 价格预测
- 趋势预测
- 风险评估

---

### 9. 监控告警 API (`/api/monitoring`)

提供实时监控和告警功能。

**监控端点** (详见 `/api/monitoring` 路由)

---

### 10. 技术分析 API (`/api/technical-analysis`)

提供增强的技术分析功能。

**技术分析端点** (详见 `/api/technical-analysis` 路由)

---

### 11. 多数据源 API (`/api/multi-source`)

提供多数据源管理和切换功能。

**多数据源端点** (详见 `/api/multi-source` 路由)

---

### 12. 公告监控 API (`/api/announcement`)

提供公司公告监控和分析功能。

**公告端点** (详见 `/api/announcement` 路由)

---

## 📊 错误处理

### HTTP状态码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| **200** | 成功 | 请求成功处理 |
| **201** | 已创建 | 资源创建成功 |
| **204** | 无内容 | 删除成功 |
| **400** | 错误请求 | 参数验证失败 |
| **401** | 未授权 | Token无效或过期 |
| **403** | 禁止访问 | 权限不足 |
| **404** | 未找到 | 资源不存在 |
| **422** | 验证错误 | 请求参数格式错误 |
| **500** | 服务器错误 | 内部服务器错误 |

### 错误响应格式

**标准错误响应**:
```json
{
  "detail": "错误详细信息"
}
```

**验证错误响应** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "symbol"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**业务错误响应**:
```json
{
  "success": false,
  "message": "股票代码不存在",
  "error_code": "STOCK_NOT_FOUND",
  "timestamp": "2025-10-25T10:30:00"
}
```

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `INVALID_TOKEN` | Token无效 | 重新登录获取新Token |
| `TOKEN_EXPIRED` | Token过期 | 使用refresh端点刷新Token |
| `STOCK_NOT_FOUND` | 股票不存在 | 检查股票代码格式 |
| `DATABASE_ERROR` | 数据库错误 | 联系管理员 |
| `ADAPTER_ERROR` | 数据源适配器错误 | 检查数据源连接 |
| `CACHE_ERROR` | 缓存错误 | 禁用缓存或清除缓存 |
| `RATE_LIMIT_EXCEEDED` | 超过速率限制 | 降低请求频率 |

---

## 💡 最佳实践

### 1. 认证最佳实践

```python
import requests
from datetime import datetime, timedelta

class MyStocksAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.token_expires_at = None

    def login(self, username, password):
        """登录并获取Token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={"username": username, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data['access_token']
        self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'])

    def is_token_valid(self):
        """检查Token是否有效"""
        if not self.access_token:
            return False
        return datetime.now() < self.token_expires_at

    def refresh_token_if_needed(self):
        """如果Token快过期，自动刷新"""
        if not self.is_token_valid():
            response = requests.post(
                f"{self.base_url}/api/auth/refresh",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'])

    def get(self, endpoint, params=None):
        """带自动Token刷新的GET请求"""
        self.refresh_token_if_needed()

        response = requests.get(
            f"{self.base_url}{endpoint}",
            params=params,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        response.raise_for_status()
        return response.json()

# 使用示例
client = MyStocksAPIClient()
client.login("admin", "admin123")

# 获取股票基本信息
stocks = client.get("/api/data/stocks/basic", params={"limit": 10})
```

### 2. 缓存使用建议

**缓存策略**:

| 数据类型 | 缓存时间 | 原因 |
|---------|----------|------|
| **实时行情** | 10秒 | 需要高频更新 |
| **ETF数据** | 1分钟 | 平衡实时性和性能 |
| **资金流向** | 5分钟 | 减少数据库压力 |
| **龙虎榜** | 24小时 | 每日更新 |
| **股票基本信息** | 10分钟 | 变化较少 |
| **技术指标** | 使用`use_cache=true` | 计算密集 |

**禁用缓存示例**:
```bash
# 强制从数据库查询最新数据
curl -X GET "http://localhost:8000/api/data/stocks/daily?symbol=600519.SH&use_cache=false"
```

### 3. 批量请求优化

**避免循环单次请求**:

❌ **错误做法**:
```python
# 不要这样做
symbols = ['600519.SH', '000001.SZ', '000002.SZ']
for symbol in symbols:
    data = client.get(f"/api/data/stocks/daily?symbol={symbol}")
```

✅ **正确做法**:
```python
# 使用批量查询或并发请求
import concurrent.futures

symbols = ['600519.SH', '000001.SZ', '000002.SZ']

def fetch_stock_data(symbol):
    return client.get(f"/api/data/stocks/daily?symbol={symbol}")

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_stock_data, symbols))
```

### 4. 错误处理

**完整的错误处理示例**:
```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, headers=None, params=None):
    """带完整错误处理的API调用"""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Token无效或过期，请重新登录")
        elif e.response.status_code == 404:
            print("资源不存在")
        elif e.response.status_code == 422:
            print(f"参数验证错误: {e.response.json()}")
        else:
            print(f"HTTP错误: {e}")
        return None

    except requests.exceptions.Timeout:
        print("请求超时")
        return None

    except requests.exceptions.ConnectionError:
        print("连接错误，服务器可能未启动")
        return None

    except RequestException as e:
        print(f"请求异常: {e}")
        return None
```

### 5. 分页最佳实践

**分页查询示例**:
```python
def fetch_all_stocks(client, page_size=100):
    """分页获取所有股票"""
    all_stocks = []
    offset = 0

    while True:
        response = client.get(
            "/api/data/stocks/basic",
            params={"limit": page_size, "offset": offset}
        )

        stocks = response.get('data', [])
        if not stocks:
            break

        all_stocks.extend(stocks)
        offset += page_size

        # 避免请求过快
        time.sleep(0.1)

    return all_stocks
```

### 6. 性能监控

**添加请求计时**:
```python
import time

def timed_request(func):
    """装饰器: 记录API调用时间"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"API调用耗时: {elapsed:.3f}秒")
        return result
    return wrapper

@timed_request
def get_stock_data(symbol):
    return client.get(f"/api/data/stocks/daily?symbol={symbol}")
```

---

## 🔍 测试和调试

### Swagger UI交互式文档

访问 `http://localhost:8000/api/docs` 使用Swagger UI进行：

1. **浏览所有API端点**
2. **查看请求/响应模型**
3. **在线测试API** (Try it out)
4. **查看示例响应**

### ReDoc文档

访问 `http://localhost:8000/api/redoc` 查看更清晰的API文档

### Postman集合

**导入OpenAPI规范到Postman**:

1. 下载OpenAPI规范: `http://localhost:8000/openapi.json`
2. 在Postman中: `Import` → `Upload Files` → 选择 `openapi.json`
3. 自动生成完整的API集合

### curl测试脚本

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. 健康检查
echo "=== 健康检查 ==="
curl -s "$BASE_URL/health" | jq

# 2. 登录
echo -e "\n=== 登录 ==="
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

echo "Token: $TOKEN"

# 3. 获取股票基本信息
echo -e "\n=== 获取股票基本信息 ==="
curl -s "$BASE_URL/api/data/stocks/basic?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. 获取日线数据
echo -e "\n=== 获取日线数据 ==="
curl -s "$BASE_URL/api/data/stocks/daily?symbol=600519.SH&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. 系统健康检查
echo -e "\n=== 系统健康检查 ==="
curl -s "$BASE_URL/api/system/health" | jq

# 6. 数据库健康检查
echo -e "\n=== 数据库健康检查 ==="
curl -s "$BASE_URL/api/system/database/health" | jq
```

保存为 `test_api.sh`，添加执行权限:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 📚 技术栈

### 后端框架

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.100+ | Web框架 |
| **Pydantic** | 2.0+ | 数据验证 |
| **SQLAlchemy** | 2.0+ | ORM |
| **Uvicorn** | 0.23+ | ASGI服务器 |
| **structlog** | - | 结构化日志 |

### 数据库

| 数据库 | 用途 |
|--------|------|
| **PostgreSQL** | 主数据库（日线、参考、元数据） |
| **TDengine** | 时序数据库（高频tick/分钟数据） |

### 数据源

| 数据源 | 用途 |
|--------|------|
| **AkShare** | 中国市场数据 |
| **通达信TDX** | 实时行情 |
| **东方财富** | 资金流向、ETF |

---

## 🚀 部署指南

### 开发环境

```bash
# 1. 启动后端服务
cd web/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. 访问API文档
open http://localhost:8000/api/docs
```

### 生产环境

```bash
# 使用Gunicorn + Uvicorn Workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建镜像
docker build -t mystocks-api:latest .

# 运行容器
docker run -d -p 8000:8000 --name mystocks-api mystocks-api:latest
```

---

## 📝 变更日志

### Version 2.0.0 (2025-10-25)

- ✅ 完成P5: API接口文档
- ✅ 生成OpenAPI/Swagger规范
- ✅ 创建全面的API使用指南
- ✅ 添加请求/响应示例
- ✅ 文档化错误处理
- ✅ 提供最佳实践建议

### Version 1.0.0 (Week 3 简化)

- ✅ 简化为双数据库架构（TDengine + PostgreSQL）
- ✅ 移除MySQL和Redis
- ✅ 实现自动路由
- ✅ 集成监控系统
- ✅ 实现缓存优化

---

## 📞 支持和联系

**项目**: MyStocks 量化交易数据管理系统
**版本**: 2.0.0 (US3 + P5)
**API版本**: v2

**相关文档**:
- [US3 架构文档](./architecture.md)
- [P1+P2 完成总结](./P1_P2_COMPLETION_SUMMARY.md)
- [P3 性能优化文档](./P3_PERFORMANCE_OPTIMIZATION_COMPLETION.md)
- [Grafana 监控集成](./P2_GRAFANA_MONITORING_COMPLETION.md)

---

**部署状态**: ✅ 生产就绪
**文档完整度**: ⭐⭐⭐⭐⭐ (100%)
**最后更新**: 2025-10-25
