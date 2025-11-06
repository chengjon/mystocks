# MyStocks API 数据格式约定
# Data Format Conventions for MyStocks API

**Version**: 2.0.0
**Last Updated**: 2025-11-06
**Author**: MyStocks Development Team

---

## 目录 (Table of Contents)

1. [时间戳格式 (Timestamp Formats)](#1-时间戳格式)
2. [数值格式 (Numeric Formats)](#2-数值格式)
3. [货币和金额 (Currency and Money)](#3-货币和金额)
4. [分页约定 (Pagination Conventions)](#4-分页约定)
5. [排序约定 (Sorting Conventions)](#5-排序约定)
6. [错误码标准 (Error Code Standards)](#6-错误码标准)
7. [字段命名规范 (Field Naming Conventions)](#7-字段命名规范)
8. [日期范围查询 (Date Range Queries)](#8-日期范围查询)
9. [空值处理 (Null/Empty Value Handling)](#9-空值处理)
10. [特殊字符和编码 (Special Characters & Encoding)](#10-特殊字符和编码)
11. [股票代码格式 (Stock Symbol Formats)](#11-股票代码格式)
12. [百分比格式 (Percentage Formats)](#12-百分比格式)
13. [布尔值约定 (Boolean Conventions)](#13-布尔值约定)
14. [数组和列表 (Arrays and Lists)](#14-数组和列表)

---

## 1. 时间戳格式

### 1.1 标准时间格式

**所有API响应中的时间戳必须使用 UTC 时间，格式为 ISO 8601**

#### 响应格式 (Response Format)

```json
{
  "timestamp": "2025-11-06T12:34:56.789Z",
  "created_at": "2025-11-06T12:34:56.789000",
  "updated_at": "2025-11-06T12:34:56Z"
}
```

**规范**:
- ✅ **推荐**: ISO 8601 格式 `YYYY-MM-DDTHH:MM:SS.fffZ`
- ✅ UTC时区标识 `Z` 或 `+00:00`
- ✅ 毫秒精度 (`.fff`) 用于高精度场景
- ❌ **禁止**: 本地时区时间戳（除非明确标注时区）
- ❌ **禁止**: Unix时间戳数字（除非字段明确命名为 `*_unix`）

#### Unix时间戳 (Unix Timestamp)

仅在特定场景使用，字段必须以 `_unix` 或 `_ms` 结尾：

```json
{
  "timestamp_unix": 1699267200,       // 秒级时间戳
  "timestamp_ms": 1699267200000,      // 毫秒级时间戳
  "created_at_unix": 1699267200
}
```

### 1.2 WebSocket消息时间戳

WebSocket消息统一使用 **UTC毫秒级时间戳**:

```json
{
  "type": "notification",
  "timestamp": 1699267200000,         // UTC毫秒
  "server_time": 1699267200000,       // 服务器时间 UTC毫秒
  "data": {...}
}
```

**规范**:
- ✅ 所有WebSocket消息的 `timestamp` 字段使用毫秒级时间戳
- ✅ 服务器时间字段: `server_time`
- ✅ 客户端请求时间: `timestamp`

### 1.3 日期格式 (Date Only)

仅日期（无时间）使用 `YYYY-MM-DD` 格式:

```json
{
  "trade_date": "2025-11-06",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

---

## 2. 数值格式

### 2.1 浮点数精度

**默认精度规则**:

| 数据类型 | 小数位数 | 示例 | 说明 |
|---------|---------|------|------|
| 股票价格 | 2位小数 | `1850.50` | 人民币价格 |
| 涨跌幅 | 2位小数 | `2.35` | 百分比数值 |
| 成交量 | 整数 | `1000000` | 股数 |
| 成交额 | 2位小数 | `1850000000.50` | 人民币金额 |
| 市盈率 PE | 2位小数 | `25.50` | 倍数 |
| 换手率 | 2位小数 | `3.50` | 百分比 |
| 资金流向 | 2位小数 | `123456789.50` | 人民币金额 |

#### JSON示例

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "price": 1850.50,
  "change": 2.35,
  "change_percent": 1.28,
  "volume": 1000000,
  "turnover": 1850000000.50,
  "pe_ratio": 25.50,
  "turnover_rate": 3.50
}
```

### 2.2 超大数值

对于超大数值（如总市值、成交额），使用字符串防止精度丢失:

```json
{
  "market_cap": "2500000000000.00",     // 2.5万亿，使用字符串
  "market_cap_num": 2500000000000.00,   // 数值形式（可能丢失精度）
  "turnover_amount": "18500000000.50"   // 185亿
}
```

**规范**:
- ✅ 超过JavaScript Number安全范围 (`2^53 - 1`) 的数值使用字符串
- ✅ 提供 `_num` 后缀的数值版本（供快速计算）
- ✅ 保留2位小数

---

## 3. 货币和金额

### 3.1 货币格式

所有金额字段使用 **人民币（CNY）** 为默认货币单位，单位为 **元（Yuan）**

```json
{
  "price": 1850.50,              // 单位: 元
  "amount": 18500000.00,         // 单位: 元
  "currency": "CNY",             // 货币代码
  "amount_display": "¥1,850.50" // 显示格式（可选）
}
```

**规范**:
- ✅ 默认货币: CNY（人民币）
- ✅ 金额单位: 元（Yuan）
- ✅ 精度: 2位小数
- ✅ 可选: 提供 `*_display` 字段（格式化显示）

### 3.2 大额金额单位转换

```json
{
  "amount": 1850000000.00,          // 原始金额（元）
  "amount_wan": 185000.00,          // 万元
  "amount_yi": 18.50,               // 亿元
  "amount_display": "18.50亿元"     // 显示格式
}
```

---

## 4. 分页约定

### 4.1 分页请求参数

**统一分页参数**:

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `page` | integer | 1 | 当前页码（从1开始） |
| `page_size` | integer | 20 | 每页记录数 |
| `offset` | integer | 0 | 偏移量（可选，与page互斥） |
| `limit` | integer | 20 | 限制数量（可选，与page_size互斥） |

#### 请求示例

```http
GET /api/stocks?page=1&page_size=20
GET /api/stocks?offset=0&limit=20
```

### 4.2 分页响应格式

使用 `PagedResponse[T]` 模型:

```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {"symbol": "600000", "name": "浦发银行"},
    {"symbol": "600519", "name": "贵州茅台"}
  ],
  "total": 4800,
  "page": 1,
  "page_size": 20,
  "total_pages": 240,
  "has_next": true,
  "has_prev": false,
  "timestamp": "2025-11-06T12:34:56.789Z"
}
```

**规范**:
- ✅ `page`: 当前页码（从1开始）
- ✅ `total`: 总记录数
- ✅ `total_pages`: 总页数（自动计算）
- ✅ `has_next`: 是否有下一页
- ✅ `has_prev`: 是否有上一页

---

## 5. 排序约定

### 5.1 排序参数

**统一排序参数**:

| 参数名 | 类型 | 说明 | 示例 |
|-------|------|------|------|
| `order_by` | string | 排序字段 | `price` |
| `order` | string | 排序方向 | `asc`, `desc` |
| `sort` | string | 组合排序 | `price:desc,volume:asc` |

#### 请求示例

```http
GET /api/stocks?order_by=price&order=desc
GET /api/stocks?sort=price:desc,volume:asc
```

### 5.2 排序方向

**标准排序方向**:
- `asc` - 升序（Ascending）
- `desc` - 降序（Descending）

❌ **禁止**: 使用 `ASC`, `DESC`, `ascending`, `descending` 等变体

---

## 6. 错误码标准

### 6.1 HTTP状态码

| 状态码 | 说明 | 使用场景 |
|-------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权（需要登录） |
| 403 | Forbidden | 禁止访问（权限不足或CSRF验证失败） |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

### 6.2 业务错误码

使用 `error_code` 字段标识具体错误类型:

```json
{
  "success": false,
  "message": "股票代码格式不正确",
  "error_code": "INVALID_PARAMETER",
  "details": {
    "field": "symbol",
    "value": "abc",
    "expected": "6位数字"
  },
  "timestamp": "2025-11-06T12:34:56.789Z"
}
```

**标准错误码** (参见 `app/models/base.py` 中的 `ErrorCode` 类):

| 错误码 | 说明 |
|-------|------|
| `INVALID_PARAMETER` | 无效参数 |
| `VALIDATION_ERROR` | 数据验证失败 |
| `RESOURCE_NOT_FOUND` | 资源不存在 |
| `UNAUTHORIZED` | 未授权 |
| `FORBIDDEN` | 禁止访问 |
| `DATABASE_ERROR` | 数据库错误 |
| `EXTERNAL_API_ERROR` | 外部API错误 |
| `INTERNAL_ERROR` | 内部错误 |

---

## 7. 字段命名规范

### 7.1 命名风格

**统一使用 snake_case（下划线分隔）命名风格**

✅ **正确**:
```json
{
  "stock_symbol": "600519",
  "company_name": "贵州茅台",
  "market_cap": 2500000000000.00,
  "pe_ratio": 25.50,
  "created_at": "2025-11-06T12:34:56.789Z"
}
```

❌ **错误**:
```json
{
  "StockSymbol": "600519",      // PascalCase
  "companyName": "贵州茅台",    // camelCase
  "MarketCap": 2500000000000.00,
  "PE_Ratio": 25.50,
  "CreatedAt": "2025-11-06T12:34:56.789Z"
}
```

### 7.2 布尔字段命名

布尔字段使用 `is_*`, `has_*`, `can_*`, `should_*` 前缀:

```json
{
  "is_active": true,
  "has_permission": false,
  "can_trade": true,
  "should_alert": false
}
```

### 7.3 时间字段命名

时间字段使用 `*_at`, `*_time`, `*_date` 后缀:

```json
{
  "created_at": "2025-11-06T12:34:56.789Z",
  "updated_at": "2025-11-06T12:34:56.789Z",
  "deleted_at": null,
  "trade_time": "09:30:00",
  "trade_date": "2025-11-06"
}
```

---

## 8. 日期范围查询

### 8.1 范围查询参数

**统一范围查询参数**:

| 参数名 | 类型 | 说明 | 示例 |
|-------|------|------|------|
| `start_date` | string | 开始日期（包含） | `2025-01-01` |
| `end_date` | string | 结束日期（包含） | `2025-12-31` |
| `from` | string | 开始时间戳 | `2025-01-01T00:00:00Z` |
| `to` | string | 结束时间戳 | `2025-12-31T23:59:59Z` |

#### 请求示例

```http
GET /api/stocks/history?symbol=600519&start_date=2025-01-01&end_date=2025-12-31
GET /api/stocks/history?symbol=600519&from=2025-01-01T00:00:00Z&to=2025-12-31T23:59:59Z
```

**规范**:
- ✅ 日期范围: `start_date` / `end_date` (仅日期)
- ✅ 时间范围: `from` / `to` (完整时间戳)
- ✅ 范围包含边界（闭区间 `[start, end]`）
- ❌ **禁止**: 使用 `begin`, `finish`, `since`, `until` 等变体

---

## 9. 空值处理

### 9.1 Null vs Empty String

**明确区分 `null` 和空字符串 `""`**:

```json
{
  "name": "",            // 空字符串：值存在但为空
  "description": null,   // null：值不存在或未设置
  "optional_field": null // 可选字段未提供
}
```

**规范**:
- ✅ `null`: 值不存在、未设置、未知
- ✅ `""`: 空字符串，值存在但为空
- ✅ `[]`: 空数组
- ✅ `{}`: 空对象
- ❌ **禁止**: 使用 `undefined` (JSON不支持)

### 9.2 可选字段

可选字段可以省略或设为 `null`:

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "description": null,        // 可选字段，未设置
  "optional_metadata": null   // 可选字段
}
```

---

## 10. 特殊字符和编码

### 10.1 字符编码

**所有API统一使用 UTF-8 编码**

```http
Content-Type: application/json; charset=utf-8
```

### 10.2 特殊字符转义

JSON字符串中的特殊字符必须转义:

```json
{
  "company_name": "贵州茅台",
  "description": "高端白酒\n市值超过2万亿",
  "path": "C:\\data\\stocks\\600519.csv",
  "quote": "He said \"Hello\""
}
```

**转义规则**:
- `\"` - 双引号
- `\\` - 反斜杠
- `\n` - 换行
- `\t` - 制表符
- `\r` - 回车

---

## 11. 股票代码格式

### 11.1 A股股票代码

**标准格式**: 6位数字

```json
{
  "symbol": "600519",        // 上交所
  "symbol_full": "600519.SH" // 带交易所后缀
}
```

**交易所后缀**:
- `.SH` - 上海证券交易所
- `.SZ` - 深圳证券交易所
- `.BJ` - 北京证券交易所

#### 完整示例

```json
{
  "symbol": "600519",
  "symbol_full": "600519.SH",
  "exchange": "SH",
  "name": "贵州茅台"
}
```

### 11.2 指数代码

```json
{
  "index_code": "000001",      // 上证指数
  "index_code_full": "000001.SH",
  "index_name": "上证指数"
}
```

---

## 12. 百分比格式

### 12.1 数值表示

百分比使用 **小数形式**，不带百分号:

```json
{
  "change_percent": 2.35,      // 表示 2.35%
  "turnover_rate": 3.50,       // 表示 3.50%
  "profit_margin": 0.25,       // 表示 0.25% 或 25bp
  "change_percent_display": "2.35%"  // 显示格式（可选）
}
```

**规范**:
- ✅ 数值: `2.35` 表示 2.35%
- ✅ 精度: 2位小数
- ❌ **禁止**: 使用 `0.0235` 表示 2.35%（会导致混淆）

---

## 13. 布尔值约定

### 13.1 布尔值表示

**严格使用 JSON 布尔值 `true` / `false`**

✅ **正确**:
```json
{
  "is_active": true,
  "has_permission": false
}
```

❌ **错误**:
```json
{
  "is_active": 1,              // 数字
  "has_permission": "false",   // 字符串
  "is_enabled": "yes"          // yes/no
}
```

### 13.2 三态值

需要表示"未知"状态时，使用 `null`:

```json
{
  "is_profitable": true,       // 盈利
  "is_growing": false,         // 不增长
  "is_verified": null          // 未验证/未知
}
```

---

## 14. 数组和列表

### 14.1 空数组

空列表使用 `[]`，不使用 `null`:

✅ **正确**:
```json
{
  "items": [],
  "tags": []
}
```

❌ **错误**:
```json
{
  "items": null,
  "tags": null
}
```

### 14.2 数组元素一致性

数组中所有元素必须具有相同的结构:

✅ **正确**:
```json
{
  "stocks": [
    {"symbol": "600000", "name": "浦发银行", "price": 10.50},
    {"symbol": "600519", "name": "贵州茅台", "price": 1850.50}
  ]
}
```

❌ **错误**:
```json
{
  "stocks": [
    {"symbol": "600000", "name": "浦发银行"},
    {"symbol": "600519", "price": 1850.50}  // 缺少name字段
  ]
}
```

---

## 附录 A: 完整响应示例

### A.1 成功响应 (Stock Quote)

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "symbol": "600519",
    "symbol_full": "600519.SH",
    "name": "贵州茅台",
    "exchange": "SH",
    "price": 1850.50,
    "change": 42.50,
    "change_percent": 2.35,
    "open": 1810.00,
    "high": 1855.00,
    "low": 1808.00,
    "close": 1850.50,
    "volume": 1000000,
    "turnover": 1850000000.50,
    "turnover_rate": 3.50,
    "pe_ratio": 25.50,
    "pb_ratio": 5.20,
    "market_cap": "2500000000000.00",
    "market_cap_wan": 250000000.00,
    "market_cap_yi": 25000.00,
    "trade_date": "2025-11-06",
    "trade_time": "15:00:00",
    "is_trading": true,
    "is_st": false
  },
  "timestamp": "2025-11-06T15:00:05.123Z",
  "request_id": "req_abc123"
}
```

### A.2 分页响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": [
    {"symbol": "600000", "name": "浦发银行", "price": 10.50},
    {"symbol": "600519", "name": "贵州茅台", "price": 1850.50}
  ],
  "total": 4800,
  "page": 1,
  "page_size": 20,
  "total_pages": 240,
  "has_next": true,
  "has_prev": false,
  "timestamp": "2025-11-06T12:34:56.789Z"
}
```

### A.3 错误响应

```json
{
  "success": false,
  "message": "股票代码格式不正确",
  "error_code": "INVALID_PARAMETER",
  "details": {
    "field": "symbol",
    "value": "abc",
    "expected": "6位数字股票代码",
    "example": "600519"
  },
  "timestamp": "2025-11-06T12:34:56.789Z",
  "path": "/api/stocks/quote",
  "request_id": "req_xyz789"
}
```

---

## 附录 B: 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 2.0.0 | 2025-11-06 | 初始版本，定义完整的数据格式约定 |

---

## 附录 C: 参考资料

- [ISO 8601 - Date and time format](https://en.wikipedia.org/wiki/ISO_8601)
- [RFC 7159 - JSON Data Interchange Format](https://tools.ietf.org/html/rfc7159)
- [REST API Design Guidelines](https://restfulapi.net/)
- [MyStocks API Models](./app/models/base.py)
- [MyStocks WebSocket Message Formats](./app/models/websocket_message.py)
- [MyStocks OpenAPI Configuration](./app/openapi_config.py)
