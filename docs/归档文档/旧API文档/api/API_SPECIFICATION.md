# MyStocks API 完整规范

**版本**: 2.0.0
**更新时间**: 2025-11-11
**规范状态**: 完整定义和验证 ✅

---

## 目录

1. [响应格式规范](#响应格式规范)
2. [WebSocket 消息格式规范](#websocket-消息格式规范)
3. [数据格式约定](#数据格式约定)
4. [HTTP 状态码](#http-状态码)
5. [认证和授权](#认证和授权)
6. [错误处理](#错误处理)
7. [API 版本控制](#api-版本控制)

---

## 响应格式规范

### 成功响应 (200)

所有成功的 HTTP 响应遵循统一格式：

```json
{
  "status": "success",
  "code": 200,
  "message": "Operation successful",
  "data": {
    "key": "value"
  },
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**字段说明**:
- `status` (string): 固定值 "success"
- `code` (integer): HTTP 状态码，通常为 200
- `message` (string): 操作成功的描述信息
- `data` (object|array|null): 响应数据，类型取决于业务逻辑
- `timestamp` (string): UTC 毫秒级时间戳，ISO 8601 格式

**实现位置**: `app/core/response_schemas.py::APIResponse.success()`

**使用示例**:

```python
@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse.not_found("User"), 404
    return APIResponse.success(data=user.to_dict())
```

---

### 分页响应

大量数据返回时使用分页格式：

```json
{
  "status": "success",
  "code": 200,
  "message": "Data retrieved successfully",
  "data": {
    "items": [
      { "id": 1, "name": "Item 1" },
      { "id": 2, "name": "Item 2" }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "pages": 5
    }
  },
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**分页参数**:
- `page` (integer): 当前页码，从 1 开始
- `page_size` (integer): 每页记录数，默认 20，最大 100
- `total` (integer): 总记录数
- `pages` (integer): 总页数，自动计算 = ceil(total / page_size)

**实现位置**: `app/core/response_schemas.py::APIResponse.paginated()`

**使用示例**:

```python
@router.get("/users")
def list_users(page: int = 1, page_size: int = 20):
    query = db.query(User)
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()
    return APIResponse.paginated(
        items=[u.to_dict() for u in items],
        total=total,
        page=page,
        page_size=page_size
    )
```

---

### 创建资源响应 (201)

创建新资源时返回 201 状态码：

```json
{
  "status": "success",
  "code": 201,
  "message": "Resource created successfully",
  "data": {
    "id": 123,
    "name": "New Item",
    "created_at": "2025-11-11T12:34:56.789Z"
  },
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**使用示例**:

```python
@router.post("/users")
def create_user(user_data: dict):
    user = db.create_user(user_data)
    return APIResponse.success(
        data=user.to_dict(),
        code=201
    ), 201
```

---

### 验证错误响应 (400)

请求数据验证失败时返回：

```json
{
  "status": "error",
  "code": 400,
  "error": "Validation Error",
  "message": "Validation failed",
  "details": {
    "email": ["Invalid email format"],
    "age": ["Must be between 18 and 120"]
  },
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**实现位置**: `app/core/response_schemas.py::APIResponse.validation_error()`

---

### 未授权响应 (401)

未提供认证凭据或凭据无效：

```json
{
  "status": "error",
  "code": 401,
  "error": "Unauthorized",
  "message": "Authentication required",
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**实现位置**: `app/core/response_schemas.py::APIResponse.unauthorized()`

---

### 禁止访问响应 (403)

用户已认证但无权限访问资源：

```json
{
  "status": "error",
  "code": 403,
  "error": "Forbidden",
  "message": "Insufficient permissions to access this resource",
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**实现位置**: `app/core/response_schemas.py::APIResponse.forbidden()`

---

### 资源未找到响应 (404)

请求的资源不存在：

```json
{
  "status": "error",
  "code": 404,
  "error": "Not Found",
  "message": "User not found",
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**实现位置**: `app/core/response_schemas.py::APIResponse.not_found()`

---

### 服务器错误响应 (500)

服务器内部错误：

```json
{
  "status": "error",
  "code": 500,
  "error": "Internal Server Error",
  "message": "An unexpected error occurred. Please try again later.",
  "details": {
    "error_id": "err_20251111_123456",
    "timestamp": "2025-11-11T12:34:56.789Z"
  },
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**实现位置**: `app/core/response_schemas.py::APIResponse.server_error()`

---

## WebSocket 消息格式规范

所有 WebSocket 通信使用 JSON 消息格式，定义见 `app/models/websocket_message.py`

### 消息类型枚举

```python
class WebSocketMessageType(str, Enum):
    # 客户端 -> 服务器
    REQUEST = "request"           # 数据请求
    SUBSCRIBE = "subscribe"       # 房间订阅
    UNSUBSCRIBE = "unsubscribe"   # 取消订阅
    PING = "ping"                 # 心跳请求

    # 服务器 -> 客户端
    RESPONSE = "response"         # 数据响应
    ERROR = "error"              # 错误响应
    NOTIFICATION = "notification" # 服务器推送通知
    PONG = "pong"                # 心跳响应
```

---

### 1. 请求消息 (REQUEST)

客户端发送给服务器的请求消息：

```json
{
  "type": "request",
  "request_id": "req_1699267200000",
  "action": "get_market_data",
  "payload": {
    "symbol": "600519",
    "data_type": "fund_flow",
    "timeframe": "1d"
  },
  "user_id": "user_001",
  "timestamp": 1699267200000,
  "trace_id": "trace_abc123"
}
```

**字段说明**:
- `type` (string): 固定值 "request"
- `request_id` (string): 请求唯一标识符，用于请求-响应匹配
- `action` (string): 操作类型，如 "get_market_data", "subscribe_room"
- `payload` (object): 请求数据负载，根据 action 类型确定
- `user_id` (string, optional): 已认证用户 ID
- `timestamp` (integer): UTC 毫秒级时间戳
- `trace_id` (string, optional): 分布式追踪 ID

---

### 2. 响应消息 (RESPONSE)

服务器返回给客户端的成功响应：

```json
{
  "type": "response",
  "request_id": "req_1699267200000",
  "success": true,
  "data": {
    "symbol": "600519",
    "fund_flow": {
      "main_inflow": 123456789.50,
      "retail_outflow": -67890123.25
    }
  },
  "timestamp": 1699267201500,
  "server_time": 1699267201500,
  "trace_id": "trace_abc123"
}
```

**字段说明**:
- `type` (string): 固定值 "response"
- `request_id` (string): 对应的请求 ID
- `success` (boolean): 请求是否成功，true 表示成功
- `data` (any): 响应数据负载
- `timestamp` (integer): 客户端时间戳
- `server_time` (integer): 服务器时间戳 (UTC 毫秒)
- `trace_id` (string, optional): 分布式追踪 ID

---

### 3. 错误消息 (ERROR)

服务器返回给客户端的错误响应：

```json
{
  "type": "error",
  "request_id": "req_1699267200000",
  "error_code": "INVALID_SYMBOL",
  "error_message": "股票代码不存在或格式不正确",
  "error_details": {
    "symbol": "INVALID",
    "hint": "请使用6位数字股票代码"
  },
  "timestamp": 1699267201500,
  "trace_id": "trace_abc123"
}
```

**错误代码列表**:

| 代码 | 说明 |
|------|------|
| AUTH_REQUIRED | 需要认证 |
| AUTH_FAILED | 认证失败 |
| AUTH_TOKEN_EXPIRED | Token 过期 |
| INVALID_MESSAGE_FORMAT | 消息格式无效 |
| INVALID_ACTION | 操作类型无效 |
| INVALID_SYMBOL | 股票代码无效 |
| INVALID_PARAMETERS | 参数无效 |
| PERMISSION_DENIED | 权限不足 |
| RATE_LIMIT_EXCEEDED | 超过速率限制 |
| ROOM_NOT_FOUND | 房间不存在 |
| SUBSCRIPTION_FAILED | 订阅失败 |
| ALREADY_SUBSCRIBED | 已订阅该房间 |
| INTERNAL_ERROR | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 服务不可用 |
| TIMEOUT | 请求超时 |

---

### 4. 心跳消息 (PING/PONG)

用于检测连接状态，防止超时断开

**客户端 PING**:
```json
{
  "type": "ping",
  "timestamp": 1699267200000
}
```

**服务器 PONG**:
```json
{
  "type": "pong",
  "timestamp": 1699267200500,
  "server_time": 1699267200500
}
```

---

### 5. 订阅消息 (SUBSCRIBE)

客户端订阅特定房间以接收实时数据：

```json
{
  "type": "subscribe",
  "request_id": "sub_1699267200000",
  "room": "market_600519",
  "user_id": "user_001",
  "timestamp": 1699267200000
}
```

**房间命名规范**:
- `market_{symbol}`: 股票行情房间，如 `market_600519`
- `portfolio_{user_id}`: 用户投资组合房间，如 `portfolio_user_001`
- `alert_{alert_id}`: 告警通知房间，如 `alert_alert_001`

---

### 6. 推送通知消息 (NOTIFICATION)

服务器主动推送给订阅房间的客户端：

```json
{
  "type": "notification",
  "room": "market_600519",
  "event": "price_update",
  "data": {
    "symbol": "600519",
    "price": 1850.50,
    "change": 2.5,
    "change_percent": 0.14
  },
  "timestamp": 1699267202000,
  "server_time": 1699267202000
}
```

**常见事件类型**:
- `price_update`: 价格更新
- `alert`: 告警通知
- `data_refresh`: 数据刷新
- `connection_status`: 连接状态变化

---

## 数据格式约定

### 时间戳格式

#### REST API 响应中的时间戳

使用 **ISO 8601 格式**的 UTC 时间戳，包含毫秒精度：

```
2025-11-11T12:34:56.789Z
```

**格式说明**:
- 时区: 统一使用 UTC (Z 后缀)
- 精度: 毫秒级 (3 位小数)
- 符号: T 分隔日期和时间，Z 表示 UTC

**Python 生成方式**:

```python
from datetime import datetime

# 推荐方式
timestamp = datetime.utcnow().isoformat()
# 结果: "2025-11-11T12:34:56.789123" (包含微秒)

# 标准方式 (带 Z 后缀)
timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
# 结果: "2025-11-11T12:34:56.789Z"
```

#### WebSocket 消息中的时间戳

使用 **UTC 毫秒级整数时间戳**：

```
1699267200000
```

**格式说明**:
- 类型: 整数 (long)
- 精度: 毫秒 (毫秒数)
- 时区: UTC

**Python 生成方式**:

```python
from datetime import datetime

# UTC 毫秒级时间戳
timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
# 结果: 1699267200000
```

#### 数据库存储格式

PostgreSQL 中使用 `TIMESTAMP WITH TIME ZONE` 类型：

```sql
CREATE TABLE market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(10, 2) NOT NULL,
    ...
);
```

---

### 数值精度

#### 价格数据 (Price)

使用 **Decimal 类型** with 2 位小数精度，表示人民币 (CNY)：

```json
{
  "price": 1850.50,
  "high": 1865.00,
  "low": 1840.25,
  "close": 1855.75
}
```

**Python 定义**:

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class MarketData(BaseModel):
    symbol: str
    price: Decimal = Field(..., decimal_places=2, max_digits=10)
    high: Decimal = Field(..., decimal_places=2, max_digits=10)
    low: Decimal = Field(..., decimal_places=2, max_digits=10)
```

**精度规范**:
- 小数位: 2 位
- 最大值: 99,999,999.99
- 示例: 1850.50, 1865.00, 1840.25

---

#### 交易量 (Volume)

使用 **整数** 表示股票数量，使用 **Decimal** 表示金额：

```json
{
  "volume": 1000000,
  "amount": 1850500000.00
}
```

**Python 定义**:

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class TradeData(BaseModel):
    symbol: str
    volume: int = Field(..., description="交易数量 (股数)")
    amount: Decimal = Field(..., decimal_places=2, description="交易金额 (元)")
```

---

#### 百分比数据 (Percentage)

使用 **Decimal** with 2-4 位小数精度：

```json
{
  "change_percent": 1.50,
  "profit_margin": 15.25,
  "win_rate": 65.12
}
```

**Python 定义**:

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class AnalysisData(BaseModel):
    change_percent: Decimal = Field(..., decimal_places=2, description="涨跌幅 (%)")
    profit_margin: Decimal = Field(..., decimal_places=2, description="利润率 (%)")
    win_rate: Decimal = Field(..., decimal_places=2, description="胜率 (%)")
```

**精度规范**:
- 普通百分比: 2 位小数 (如 1.50%, 15.25%)
- 高精度指标: 4 位小数 (如 0.1234%)

---

#### 资金流向数据 (Fund Flow)

使用 **Decimal with 2 位小数** 表示人民币金额：

```json
{
  "main_inflow": 123456789.50,
  "main_outflow": -67890123.25,
  "retail_inflow": 45678901.00,
  "retail_outflow": -23456789.75
}
```

**Python 定义**:

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class FundFlowData(BaseModel):
    main_inflow: Decimal = Field(..., decimal_places=2, description="主力净流入 (元)")
    main_outflow: Decimal = Field(..., decimal_places=2, description="主力净流出 (元)")
    retail_inflow: Decimal = Field(..., decimal_places=2, description="散户净流入 (元)")
    retail_outflow: Decimal = Field(..., decimal_places=2, description="散户净流出 (元)")
```

---

#### 指数和比率数据

使用 **Decimal** with 4 位小数精度：

```json
{
  "pe_ratio": 12.3456,
  "pb_ratio": 1.2345,
  "roc": 0.1234
}
```

---

### 特殊字段格式

#### 股票代码 (Symbol)

6 位数字代码，无前缀：

```json
{
  "symbol": "600519",
  "market": "A",
  "description": "贵州茅台"
}
```

**格式规范**:
- 长度: 6 位数字
- 市场: A (A股), HK (港股), US (美股)
- 示例: "600519" (贵州茅台), "000001" (平安银行)

---

#### 日期格式 (Date)

使用 **ISO 8601 日期格式**：

```json
{
  "trade_date": "2025-11-11",
  "report_date": "2025-09-30"
}
```

**格式**: `YYYY-MM-DD`

**Python 生成方式**:

```python
from datetime import datetime

date_str = datetime.utcnow().strftime('%Y-%m-%d')
# 结果: "2025-11-11"
```

---

#### 时间范围 (Duration)

使用 **ISO 8601 时间段格式**：

```json
{
  "duration": "PT5M",
  "period": "P1D"
}
```

**常见值**:
- `PT1M`: 1 分钟
- `PT5M`: 5 分钟
- `PT15M`: 15 分钟
- `PT1H`: 1 小时
- `P1D`: 1 天
- `P1W`: 1 周
- `P1M`: 1 个月
- `P1Y`: 1 年

---

#### 布尔值 (Boolean)

使用 `true` / `false` (小写)：

```json
{
  "is_suspended": false,
  "is_st": true,
  "is_new": false
}
```

---

#### 空值处理 (Null)

使用 `null` 表示空值：

```json
{
  "description": null,
  "comment": null
}
```

**Python 处理**:

```python
from pydantic import BaseModel, Field
from typing import Optional

class Data(BaseModel):
    description: Optional[str] = Field(None, description="可选描述")
    required_field: str  # 不能为 null
```

---

## HTTP 状态码

| 状态码 | 说明 | 用途 |
|--------|------|------|
| 200 | OK | 成功的 GET、PUT、DELETE 请求 |
| 201 | Created | 成功的 POST 请求 (资源已创建) |
| 204 | No Content | 成功的 DELETE 请求 (无返回体) |
| 400 | Bad Request | 请求参数无效、验证失败 |
| 401 | Unauthorized | 缺少认证凭据或凭据无效 |
| 403 | Forbidden | 用户已认证但无权限访问 |
| 404 | Not Found | 请求的资源不存在 |
| 409 | Conflict | 资源冲突 (如重复创建) |
| 429 | Too Many Requests | 超过速率限制 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

---

## 认证和授权

### JWT Token 认证

使用 **Bearer Token** 进行认证：

```http
GET /api/users/profile HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token 格式**:
- 方案: Bearer
- Token: JWT (JSON Web Token)
- 过期时间: 24 小时
- 刷新: 需要刷新 Token

### CSRF 保护

所有状态修改的请求 (POST, PUT, DELETE) 需要提供 CSRF Token：

```http
POST /api/users HTTP/1.1
X-CSRF-Token: abc123def456ghi789
Content-Type: application/json

{
  "name": "New User"
}
```

---

## 错误处理

### 标准错误响应格式

所有错误使用统一的响应格式：

```json
{
  "status": "error",
  "code": 400,
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": {
    "field_name": ["Error message 1", "Error message 2"]
  },
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

### 错误处理最佳实践

```python
from fastapi import HTTPException
from app.core.response_schemas import APIResponse

@router.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return APIResponse.not_found("User"), 404
        return APIResponse.success(data=user.to_dict())
    except ValueError as e:
        return APIResponse.validation_error(
            message=str(e),
            errors={"user_id": [str(e)]}
        ), 400
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        return APIResponse.server_error(), 500
```

---

## API 版本控制

### 版本策略

使用 **URL 路径版本控制**:

```
/api/v1/market/quotes
/api/v2/market/quotes
```

### 版本管理

- 当前版本: v1, v2
- 向后兼容: 仅新增字段，不删除现有字段
- 弃用计划: 通过 Deprecation 响应头通知客户端

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 01 Jan 2026 00:00:00 GMT
```

---

## 文件位置和相关代码

| 功能 | 文件位置 |
|------|--------|
| 响应格式规范 | `web/backend/app/core/response_schemas.py` |
| WebSocket 消息格式 | `web/backend/app/models/websocket_message.py` |
| OpenAPI 配置 | `web/backend/app/openapi_config.py` |
| 市场数据 Schema | `web/backend/app/schemas/market_schemas.py` |

---

## 更新历史

| 版本 | 日期 | 变更说明 |
|------|------|--------|
| 2.0.0 | 2025-11-11 | 完整的 API 规范定义，包含所有响应格式、WebSocket 消息格式和数据格式约定 |
| 1.0.0 | 2025-11-06 | 初始版本，基础 OpenAPI 配置 |

---

**规范制定者**: Claude Code
**最后审核**: 2025-11-11
**状态**: ✅ 完整且可用
