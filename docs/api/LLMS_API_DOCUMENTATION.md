# MyStocks 帮助文档

## 文档概览
- [项目首页](#): https://github.com/mystocks/project
- [Apifox项目](https://app.apifox.com/project/7376246): 218个API端点，96个数据模型
- [快速开始](#快速开始): 5分钟上手指南
- [API文档](./API_DOCUMENTATION.md): 完整的API参考文档
- [架构指南](./docs/architecture/README.md): 系统架构设计

---

## 快速开始

### 开始使用 > [快速上手](#快速上手)
- [环境配置](#环境配置)
- [第一个API调用](#第一个api调用)
- [认证流程](#认证流程)
- [常用操作](#常用操作)

### 开始使用 > [API设计规范](./docs/standards/API_DESIGN.md)
- [接口命名规范](./docs/standards/NAMING_CONVENTIONS.md)
- [参数设计原则](./docs/standards/PARAMETER_DESIGN.md)
- [响应格式标准](./docs/standards/RESPONSE_FORMAT.md)
- [错误处理规范](./docs/standards/ERROR_HANDLING.md)

### 开始使用 > [数据模型](./docs/api/data-models.md)
- [基础数据模型](./docs/api/base-models.md)
- [市场数据模型](./docs/api/market-models.md)
- [技术指标模型](./docs/api/indicator-models.md)
- [监控数据模型](./docs/api/monitoring-models.md)

### 开始使用 > [认证与授权](#认证与授权)
- [JWT Token认证](./docs/auth/jwt-auth.md)
- [CSRF Token保护](./docs/auth/csrf-protection.md)
- [角色权限管理](./docs/auth/rbac.md)
- [API访问控制](./docs/auth/access-control.md)

---

## 🚀 快速开始

### 环境配置

**Apifox 环境变量配置**：
```json
{
  "base_url": "http://localhost:8020",
  "auth_token": "{{auto_generated}}",
  "csrf_token": "{{auto_generated}}"
}
```

### 第一次使用

**步骤1：健康检查**
```http
GET {{base_url}}/health
```

**步骤2：配置自动认证**
在环境设置 → 前置脚本中添加自动登录逻辑

**步骤3：测试核心API**
```http
GET {{base_url}}/api/market/realtime/000001
Authorization: Bearer {{auth_token}}
```

---

## 🔐 认证授权

### 认证流程

**步骤1：获取CSRF Token**
```http
GET {{base_url}}/api/auth/csrf-token
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "token": "abc123xyz789..."
  }
}
```

**步骤2：用户登录**
```http
POST {{base_url}}/api/auth/login
Content-Type: application/json
X-CSRF-Token: {{csrf_token}}

{
  "username": "admin",
  "password": "your_password"
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

**步骤3：使用Token调用API**
```http
GET {{base_url}}/api/market/realtime/000001
Authorization: Bearer {{auth_token}}
X-CSRF-Token: {{csrf_token}}
```

### 端点列表

#### GET /api/auth/csrf-token
获取CSRF Token

**响应示例**：
```json
{
  "success": true,
  "data": {
    "token": "csrf_token_string"
  }
}
```

#### POST /api/auth/login
用户登录

**请求参数**：
- `username` (string, 必需): 用户名
- `password` (string, 必需): 密码

**响应示例**：
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

#### POST /api/auth/logout
用户登出

#### POST /api/auth/refresh
刷新Token

---

## 🏥 系统管理

### 核心端点

#### GET /health
健康检查

**响应示例**：
```json
{
  "status": "healthy",
  "timestamp": "2025-11-11T14:30:00Z",
  "version": "3.0.0"
}
```

#### GET /api/system/info
获取系统信息

**响应示例**：
```json
{
  "success": true,
  "data": {
    "version": "3.0.0",
    "database_status": "connected",
    "uptime": "7d 12h 34m",
    "api_endpoints": 218,
    "data_models": 96
  }
}
```

#### GET /api/system/status
获取系统状态

**响应示例**：
```json
{
  "success": true,
  "data": {
    "database_status": "healthy",
    "monitoring_active": true,
    "redis_status": "connected",
    "tdengine_status": "connected",
    "postgresql_status": "connected"
  }
}
```

#### GET /api/socketio-status
Socket.IO状态检查

---

## 📊 市场数据

### 实时行情

#### GET /api/market/realtime/{symbol}
获取单只股票实时行情

**路径参数**：
- `symbol` (string): 股票代码

**响应示例**：
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "price": 12.34,
    "change": 0.12,
    "change_pct": 0.98,
    "volume": 1234567,
    "amount": 15234567.89,
    "open": 12.20,
    "high": 12.45,
    "low": 12.10,
    "prev_close": 12.22,
    "timestamp": "2025-11-11T14:30:00"
  }
}
```

#### GET /api/market/v2/realtime-batch
批量获取实时行情

**查询参数**：
- `symbols` (string): 股票代码列表，逗号分隔
- `limit` (integer): 返回数量限制

**示例**：
```http
GET {{base_url}}/api/market/v2/realtime-batch?symbols=000001,000002,600000&limit=100
Authorization: Bearer {{auth_token}}
```

**响应示例**：
```json
{
  "success": true,
  "data": [
    {
      "symbol": "000001",
      "price": 12.34,
      "change_pct": 0.98
    },
    {
      "symbol": "000002",
      "price": 8.76,
      "change_pct": -1.23
    }
  ],
  "count": 2,
  "timestamp": "2025-11-11T14:30:00"
}
```

### K线数据

#### GET /api/market/kline
获取K线数据

**查询参数**：
- `symbol` (string, 必需): 股票代码
- `period` (string): 周期 (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
- `start_date` (string): 开始日期 YYYY-MM-DD
- `end_date` (string): 结束日期 YYYY-MM-DD
- `limit` (integer): 返回数据点数量

**示例**：
```http
GET {{base_url}}/api/market/kline?symbol=000001&period=daily&limit=100
Authorization: Bearer {{auth_token}}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "period": "daily",
    "count": 100,
    "kline_data": [
      {
        "date": "2025-11-11",
        "open": 12.20,
        "high": 12.45,
        "low": 12.10,
        "close": 12.34,
        "volume": 1234567,
        "amount": 15234567.89
      }
    ]
  }
}
```

### 资金流向

#### GET /api/market/fund-flow
获取资金流向数据

**查询参数**：
- `symbol` (string): 股票代码
- `period` (string): 时间周期
- `limit` (integer): 返回数量

**响应示例**：
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "main_inflow": 1234567.89,
    "main_outflow": -876543.21,
    "net_inflow": 358024.68,
    "main_net_ratio": 0.23,
    "timestamp": "2025-11-11T14:30:00"
  }
}
```

#### GET /api/market/v2/sector-flow
获取板块资金流向

#### GET /api/market/v3/fund-flow
获取行业资金流向（申万、证监会分类）

**查询参数**：
- `industry_type` (string): 行业分类类型 (sw_l1, sw_l2, csrc_l1, csrc_l2)
- `limit` (integer): 返回数量限制

### 市场概览

#### GET /api/market/v2/market-overview
获取市场概览

**响应示例**：
```json
{
  "success": true,
  "data": {
    "trade_date": "2025-11-11",
    "market_status": "trading",
    "sh_index": {
      "value": 3245.67,
      "change": 12.34,
      "change_pct": 0.38
    },
    "sz_index": {
      "value": 9876.54,
      "change": -23.45,
      "change_pct": -0.24
    },
    "total_volume": 123456789012,
    "total_amount": 987654321098.76,
    "limit_up_count": 45,
    "limit_down_count": 23,
    "rising_count": 1876,
    "falling_count": 2134
  }
}
```

---

## 📈 技术分析

### 指标查询

#### GET /api/technical/{symbol}/indicators
获取股票所有技术指标

**路径参数**：
- `symbol` (string): 股票代码

**查询参数**：
- `period` (string): 数据周期 (daily, weekly, monthly)
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期

**响应示例**：
```json
{
  "success": true,
  "data": {
    "symbol": "600519",
    "latest_price": 1680.50,
    "latest_date": "2025-11-11",
    "trend": {
      "ma5": 1675.20,
      "ma10": 1668.80,
      "ma20": 1650.30,
      "macd": 15.60,
      "macd_signal": 12.30,
      "macd_hist": 3.30
    },
    "momentum": {
      "rsi6": 65.4,
      "rsi12": 58.2,
      "kdj_k": 72.1,
      "kdj_d": 68.5,
      "kdj_j": 79.2
    },
    "volatility": {
      "bb_upper": 1720.50,
      "bb_middle": 1680.50,
      "bb_lower": 1640.50,
      "atr": 25.80
    },
    "volume": {
      "obv": 123456789,
      "vwap": 1675.80,
      "volume_ratio": 1.23
    }
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

### 交易信号

#### GET /api/technical/{symbol}/signals
获取交易信号

**响应示例**：
```json
{
  "success": true,
  "data": {
    "symbol": "600519",
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
}
```

### 历史数据

#### GET /api/technical/{symbol}/history
获取股票历史行情数据

**查询参数**：
- `period` (string): 周期 (daily, weekly, monthly)
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期
- `limit` (integer): 返回数据点数量

### 批量处理

#### POST /api/technical/batch/indicators
批量获取多只股票技术指标

---

## 🔄 多数据源

### 数据源管理

#### GET /api/multi-source/health
获取所有数据源健康状态

**响应示例**：
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
      "error_count": 12,
      "last_check": "2025-11-11T14:30:00"
    },
    {
      "source_type": "tushare",
      "status": "healthy",
      "enabled": true,
      "priority": 2,
      "success_rate": 95.2,
      "avg_response_time": 0.78,
      "error_count": 28,
      "last_check": "2025-11-11T14:29:45"
    }
  ]
}
```

#### GET /api/multi-source/realtime-quote
获取实时行情（多数据源）

#### GET /api/multi-source/fund-flow
获取资金流向（多数据源）

### 公告监控

#### GET /api/announcement/today
获取今日公告

#### GET /api/announcement/important
获取重要公告

#### POST /api/announcement/monitor/evaluate
评估监控规则

---

## 🔔 监控系统

### 告警规则

#### GET /api/monitoring/alert-rules
获取告警规则列表

**查询参数**：
- `rule_type` (string): 规则类型
- `is_active` (boolean): 是否启用

**响应示例**：
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "rule_name": "茅台涨停监控",
      "rule_type": "limit_up",
      "symbol": "600519",
      "stock_name": "贵州茅台",
      "is_active": true,
      "priority": 5,
      "created_at": "2025-11-10T10:00:00"
    }
  ]
}
```

#### POST /api/monitoring/alert-rules
创建告警规则

**请求体**：
```json
{
  "rule_name": "茅台涨停监控",
  "rule_type": "limit_up",
  "symbol": "600519",
  "stock_name": "贵州茅台",
  "parameters": {
    "include_st": false
  },
  "notification_config": {
    "channels": ["ui", "sound"],
    "level": "warning"
  },
  "priority": 5,
  "is_active": true
}
```

#### PUT /api/monitoring/alert-rules/{rule_id}
更新告警规则

#### DELETE /api/monitoring/alert-rules/{rule_id}
删除告警规则

### 实时监控

#### GET /api/monitoring/realtime
获取实时监控数据列表

**查询参数**：
- `symbols` (string): 股票代码列表，逗号分隔
- `limit` (integer): 返回数量限制
- `is_limit_up` (boolean): 仅返回涨停股票
- `is_limit_down` (boolean): 仅返回跌停股票

#### POST /api/monitoring/realtime/fetch
手动触发获取实时数据

**请求体**：
```json
{
  "symbols": ["600519", "000001", "600000"]
}
```

### 龙虎榜

#### GET /api/monitoring/dragon-tiger
获取龙虎榜数据

**查询参数**：
- `trade_date` (date): 交易日期
- `symbol` (string): 股票代码
- `min_net_amount` (float): 最小净买入额
- `limit` (integer): 返回数量限制

#### POST /api/monitoring/dragon-tiger/fetch
手动获取龙虎榜数据

### 监控摘要

#### GET /api/monitoring/summary
获取监控系统摘要

**响应示例**：
```json
{
  "success": true,
  "data": {
    "total_monitored": 2500,
    "limit_up_count": 45,
    "limit_down_count": 23,
    "big_rise_count": 187,
    "big_fall_count": 134,
    "avg_change": 0.23,
    "total_amount": 987654321098.76,
    "active_alerts": 12,
    "unread_alerts": 5
  }
}
```

---

## 📋 股票搜索

### 搜索功能

#### GET /api/stock-search
搜索股票

**查询参数**：
- `q` (string): 搜索关键词
- `limit` (integer): 返回数量限制

**示例**：
```http
GET {{base_url}}/api/stock-search?q=平安&limit=10
```

**响应示例**：
```json
{
  "success": true,
  "data": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "pinyin": "PAYH",
      "market": "SZ",
      "industry": "银行"
    }
  ],
  "count": 1
}
```

#### GET /api/stocks/info/{symbol}
获取股票详情

**响应示例**：
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "market": "SZ",
    "industry": "银行",
    "listing_date": "1991-04-03",
    "total_shares": 19405918000,
    "circulating_shares": 17687458000,
    "market_cap": 239789123456.78
  }
}
```

---

## 📋 自选股管理

### 基本操作

#### GET /api/watchlist
获取自选股列表

#### POST /api/watchlist/add
添加自选股

**请求体**：
```json
{
  "symbol": "000001",
  "note": "关注的银行股"
}
```

#### DELETE /api/watchlist/remove/{symbol}
删除自选股

#### PUT /api/watchlist/update/{symbol}
更新自选股备注

---

## 🧠 问财接口

### 自然语言查询

#### POST /api/wencai/query
问财自然语言查询

**请求体**：
```json
{
  "query": "今日涨停的银行股",
  "context": {}
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "query": "今日涨停的银行股",
    "sql": "SELECT * FROM stock_daily WHERE change_pct >= 9.5 AND industry = '银行'",
    "results": [
      {
        "symbol": "000001",
        "name": "平安银行",
        "price": 12.34,
        "change_pct": 9.89
      }
    ],
    "count": 1,
    "execution_time": 0.023
  }
}
```

#### GET /api/wencai/templates
获取问财模板

#### POST /api/wencai/execute
执行自定义查询

---

## 📡 通达信接口

### TDX数据

#### GET /api/tdx/kline
获取通达信K线数据

**查询参数**：
- `symbol` (string): 股票代码
- `period` (string): 周期
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期

#### GET /api/tdx/realtime
获取通达信实时数据

#### GET /api/tdx/finance
获取财务数据

#### GET /api/tdx/industry
获取行业数据

---

## 💾 数据管理

### 基础数据

#### GET /api/data/stock-info
获取股票基本信息

**查询参数**：
- `symbol` (string): 股票代码
- `market` (string): 市场代码

#### GET /api/data/daily-kline
获取日线数据

**查询参数**：
- `symbol` (string): 股票代码
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期
- `adjust` (string): 复权类型 (qfq, hfq, none)

#### GET /api/data/industry
获取行业分类

### 批量数据

#### POST /api/data/batch-import
批量导入数据

#### GET /api/data/export
导出数据

**查询参数**：
- `table` (string): 表名
- `format` (string): 导出格式 (csv, xlsx, json)
- `filters` (object): 过滤条件

---

## ⚡ 缓存管理

### 缓存状态

#### GET /api/cache/stats
获取缓存统计

**响应示例**：
```json
{
  "success": true,
  "data": {
    "redis_stats": {
      "hits": 1256789,
      "misses": 34567,
      "hit_rate": 0.973,
      "memory_used": "256MB",
      "memory_total": "512MB"
    },
    "app_cache": {
      "hits": 98765,
      "misses": 1234,
      "hit_rate": 0.988,
      "size": 156
    }
  }
}
```

#### POST /api/cache/clear
清理缓存

**请求体**：
```json
{
  "cache_type": "redis",  // redis, app, all
  "pattern": "stock:*"    // 可选，清理特定模式
}
```

#### POST /api/cache/prewarm
预热缓存

**请求体**：
```json
{
  "symbols": ["000001", "000002", "600000"],
  "data_types": ["realtime", "kline"]
}
```

---

## ⚙️ 任务管理

### 异步任务

#### GET /api/tasks
获取任务列表

**响应示例**：
```json
{
  "success": true,
  "data": [
    {
      "task_id": "task_001",
      "type": "data_sync",
      "status": "running",
      "progress": 65,
      "created_at": "2025-11-11T14:00:00",
      "updated_at": "2025-11-11T14:30:00"
    }
  ]
}
```

#### POST /api/tasks/create
创建新任务

**请求体**：
```json
{
  "type": "data_sync",
  "params": {
    "symbols": ["000001", "000002"],
    "data_type": "realtime"
  },
  "priority": "normal"
}
```

#### GET /api/tasks/{task_id}
获取任务详情

#### DELETE /api/tasks/{task_id}
取消任务

---

## 📧 通知管理

### 通知渠道

#### GET /api/notification/channels
获取通知渠道

**响应示例**：
```json
{
  "success": true,
  "data": [
    {
      "channel": "email",
      "enabled": true,
      "config": {
        "smtp_server": "smtp.gmail.com",
        "port": 587
      }
    },
    {
      "channel": "webhook",
      "enabled": true,
      "config": {
        "url": "https://hooks.slack.com/services/..."
      }
    }
  ]
}
```

#### POST /api/notification/send
发送通知

**请求体**：
```json
{
  "channel": "email",
  "to": ["admin@example.com"],
  "subject": "系统告警",
  "content": "股票600519触发涨停监控",
  "priority": "high"
}
```

#### GET /api/notification/history
获取通知历史

#### POST /api/notification/test
测试通知

---

## 🛡️ 错误处理

### 错误响应格式

所有API错误响应统一格式：

```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "股票代码格式错误",
    "details": "股票代码必须是6位数字",
    "timestamp": "2025-11-11T14:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| INVALID_SYMBOL | 400 | 股票代码格式错误 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| RATE_LIMITED | 429 | 请求频率限制 |
| SERVER_ERROR | 500 | 服务器内部错误 |

### 错误处理示例

```javascript
// JavaScript错误处理
try {
  const response = await fetch('/api/market/realtime/000001', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-CSRF-Token': csrfToken
    }
  });

  const data = await response.json();

  if (!data.success) {
    console.error('API Error:', data.error);
    // 处理业务逻辑错误
    return;
  }

  // 处理成功响应
  console.log('Market data:', data.data);

} catch (error) {
  console.error('Network Error:', error);
  // 处理网络错误
}
```

---

## 🔧 环境配置

### 开发环境

```bash
# 启动后端服务
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload

# 启动前端服务
cd web/frontend
npm run dev
```

### 环境变量

```bash
# 数据库配置
TDENGINE_HOST=192.168.1.100
TDENGINE_PORT=6030
POSTGRESQL_HOST=192.168.1.100
POSTGRESQL_PORT=5432

# Redis配置
REDIS_HOST=192.168.1.100
REDIS_PORT=6379

# API配置
SECRET_KEY=your_secret_key
JWT_EXPIRE_HOURS=24
```

### Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

---

## 📖 使用示例

### JavaScript/TypeScript

```typescript
// API客户端封装
class MyStocksAPI {
  private baseURL: string;
  private token: string;
  private csrfToken: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async login(username: string, password: string) {
    // 获取CSRF Token
    const csrfResponse = await fetch(`${this.baseURL}/api/auth/csrf-token`);
    const csrfData = await csrfResponse.json();
    this.csrfToken = csrfData.data.token;

    // 登录
    const loginResponse = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': this.csrfToken
      },
      body: JSON.stringify({ username, password })
    });

    const loginData = await loginResponse.json();
    this.token = loginData.data.access_token;

    return loginData;
  }

  async getRealtimeData(symbol: string) {
    const response = await fetch(`${this.baseURL}/api/market/realtime/${symbol}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'X-CSRF-Token': this.csrfToken
      }
    });

    return await response.json();
  }
}

// 使用示例
const api = new MyStocksAPI('http://localhost:8020');
await api.login('admin', 'password');
const data = await api.getRealtimeData('000001');
console.log(data);
```

### Python

```python
import requests
import json

class MyStocksAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.csrf_token = None

    def login(self, username, password):
        # 获取CSRF Token
        csrf_response = requests.get(f"{self.base_url}/api/auth/csrf-token")
        csrf_data = csrf_response.json()
        self.csrf_token = csrf_data['data']['token']

        # 登录
        login_response = requests.post(
            f"{self.base_url}/api/auth/login",
            headers={
                'Content-Type': 'application/json',
                'X-CSRF-Token': self.csrf_token
            },
            json={'username': username, 'password': password}
        )

        login_data = login_response.json()
        self.token = login_data['data']['access_token']

        return login_data

    def get_realtime_data(self, symbol):
        response = requests.get(
            f"{self.base_url}/api/market/realtime/{symbol}",
            headers={
                'Authorization': f'Bearer {self.token}',
                'X-CSRF-Token': self.csrf_token
            }
        )
        return response.json()

# 使用示例
api = MyStocksAPI('http://localhost:8020')
api.login('admin', 'password')
data = api.get_realtime_data('000001')
print(data)
```

---

## 📞 支持与帮助

### 文档资源
- **Apifox项目**: https://app.apifox.com/project/7376246
- **Swagger UI**: http://localhost:8020/api/docs
- **OpenAPI文档**: http://localhost:8020/openapi.json

### 技术支持
- **项目GitHub**: [项目仓库地址]
- **技术栈**: FastAPI + TDengine + PostgreSQL + Vue 3
- **文档更新**: 2025-11-11
- **API版本**: 3.0.0

### 社区资源
- **Apifox帮助**: https://apifox.com/help/
- **FastAPI文档**: https://fastapi.tiangolo.com/
- **Vue 3文档**: https://vuejs.org/

---

**© 2025 MyStocks 量化交易数据管理系统 - 基于 Apifox 标准格式的完整API文档**
