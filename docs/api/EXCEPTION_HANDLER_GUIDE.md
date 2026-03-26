# 全局异常处理器使用指南

本文档说明如何使用MyStocks API的全局异常处理器系统。

## 📦 模块概览

### `exception_handler.py` - 全局异常处理器

统一的异常处理系统,自动捕获所有异常并转换为标准APIResponse格式。

```python
from app.core.exception_handler import (
    register_exception_handlers,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    ExceptionHandlerConfig,
)
```

---

## 🚀 快速开始

### 自动注册 (推荐)

异常处理器已在`main.py`中自动注册:

```python
# main.py
from app.core.exception_handler import register_exception_handlers

app = FastAPI(...)

# 自动注册所有异常处理器
register_exception_handlers(app)
```

**无需手动处理异常**,系统会自动捕获并转换。

---

## 📋 异常处理器覆盖范围

### 1. 全局异常处理器

**捕获**: 所有未捕获的异常

**处理逻辑**:
1. 根据异常类型确定错误码
2. 映射到正确的HTTP状态码
3. 构建统一响应格式
4. 记录详细日志

**支持的异常类型**:
- `HTTPException` - HTTP异常
- `RequestValidationError` - FastAPI请求验证错误
- `ValidationError` - Pydantic验证错误
- `SQLAlchemyError` - 数据库错误
- `PermissionError` - 权限错误
- `ValueError` - 值错误 (业务逻辑验证)
- 所有其他异常 → 服务器内部错误

### 2. HTTP异常处理器

**捕获**: `HTTPException`

**示例**:
```python
from fastapi import HTTPException

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    if not order_exists(order_id):
        raise HTTPException(
            status_code=404,
            detail={
                "code": "ORDER_NOT_FOUND",
                "message": "委托不存在"
            }
        )
```

**自动转换为**:
```json
{
  "success": false,
  "code": 4000,
  "message": "委托不存在",
  "data": null,
  "request_id": "uuid...",
  "timestamp": "2025-12-29T..."
}
```

### 3. 验证异常处理器

**捕获**: `RequestValidationError`, `ValidationError`

**示例**:
```python
from pydantic import BaseModel, Field

class OrderRequest(BaseModel):
    symbol: str = Field(..., pattern="^[0-9]{6}\\.[A-Z]{2}$")
    quantity: int = Field(..., gt=0)

@router.post("/orders")
async def create_order(order: OrderRequest):
    pass
```

**无效请求**:
```json
{
  "symbol": "ABCDE",  // 无效格式
  "quantity": -100    // 负数
}
```

**自动转换为**:
```json
{
  "success": false,
  "code": 1001,
  "message": "输入参数验证失败",
  "data": null,
  "request_id": "uuid...",
  "timestamp": "2025-12-29T...",
  "detail": {
    "validation_errors": [
      {
        "field": "symbol",
        "message": "String should match pattern '^[0-9]{6}\\.[A-Z]{2}$'",
        "type": "string_pattern_mismatch"
      },
      {
        "field": "quantity",
        "message": "Input should be greater than 0",
        "type": "greater_than"
      }
    ],
    "error_count": 2
  }
}
```

### 4. 数据库异常处理器

**捕获**: `SQLAlchemyError`

**自动转换为**:
```json
{
  "success": false,
  "code": 9003,
  "message": "数据库操作失败",
  "data": null,
  "request_id": "uuid...",
  "timestamp": "2025-12-29T...",
  "detail": {
    "type": "DatabaseError"
  }
}
```

**开发环境额外信息**:
```json
"detail": {
  "type": "IntegrityError",
  "message": "duplicate key value violates unique constraint",
  "original_error": "psycopg2.errors.UniqueViolation: ..."
}
```

---

## 🎯 异常类型到错误码映射

### ValueError → 业务错误码

系统会根据`ValueError`的消息自动推断错误码:

```python
# 股票代码错误
raise ValueError("股票代码格式不正确")
# → ErrorCode.SYMBOL_INVALID (1100)

# 日期错误
raise ValueError("日期格式不正确")
# → ErrorCode.DATE_INVALID (1200)

# 数量错误
raise ValueError("委托数量必须是100的整数倍")
# → ErrorCode.QUANTITY_INVALID (1400)

# 资金不足
raise ValueError("可用资金不足")
# → ErrorCode.INSUFFICIENT_CASH (4200)
```

### HTTPException → 错误码映射

| HTTP状态码 | 错误码 | 场景 |
|-----------|--------|------|
| 400 | 1000 (BAD_REQUEST) | 请求参数错误 |
| 401 | 6000 (AUTHENTICATION_FAILED) | 身份验证失败 |
| 403 | 6001 (AUTHORIZATION_FAILED) | 权限不足 |
| 404 | 4000 (ORDER_NOT_FOUND) | 资源不存在 |
| 409 | 4300 (MARKET_CLOSED) | 业务冲突 |
| 422 | 1001 (VALIDATION_ERROR) | 参数验证失败 |
| 429 | 6005 (RATE_LIMIT_EXCEEDED) | 请求过于频繁 |
| 500 | 9000 (INTERNAL_SERVER_ERROR) | 服务器内部错误 |

---

## 🔧 自定义业务异常

### 使用HTTPException

```python
from fastapi import HTTPException
from app.core.error_codes import ErrorCode, get_http_status, get_error_message

@router.post("/trade/orders")
async def create_order(order: OrderRequest):
    # 验证资金充足
    if order.quantity * order.price > account.cash:
        error_code = ErrorCode.INSUFFICIENT_CASH
        raise HTTPException(
            status_code=get_http_status(error_code),
            detail={
                "code": error_code.value,
                "message": get_error_message(error_code)
            }
        )
```

### 使用ValueError + 自定义消息

```python
from app.core.validators import TradingValidator
from app.core.validation_messages import CommonMessages

@router.post("/trade/orders")
async def create_order(order: OrderRequest):
    # 验证委托数量
    try:
        TradingValidator.validate_quantity(order.quantity)
    except ValueError as e:
        # ValueError会被全局异常处理器捕获
        # 并自动映射到ErrorCode.QUANTITY_INVALID
        raise
```

---

## 📝 环境配置

### 开发环境 vs 生产环境

```python
# 开发环境
ENVIRONMENT=development

# 生产环境
ENVIRONMENT=production
```

**差异**:

| 特性 | 开发环境 | 生产环境 |
|------|---------|---------|
| **堆栈跟踪** | ✅ 包含在响应中 | ❌ 不包含 |
| **请求信息** | ✅ 包含在响应中 | ❌ 不包含 |
| **详细错误消息** | ✅ 暴露原始错误 | ❌ 仅通用消息 |
| **数据库错误详情** | ✅ 包含完整错误 | ❌ 仅错误类型 |

**生产环境示例**:
```json
{
  "success": false,
  "code": 9003,
  "message": "数据库操作失败",
  "data": null,
  "request_id": "uuid...",
  "timestamp": "2025-12-29T...",
  "detail": {
    "type": "DatabaseError"
  }
}
```

**开发环境示例**:
```json
{
  "success": false,
  "code": 9003,
  "message": "数据库操作失败",
  "data": null,
  "request_id": "uuid...",
  "timestamp": "2025-12-29T...",
  "detail": {
    "type": "IntegrityError",
    "message": "duplicate key value violates unique constraint",
    "original_error": "psycopg2.errors.UniqueViolation: ...",
    "stack_trace": "Traceback (most recent call last):\n  ...",
    "request": {
      "method": "POST",
      "url": "http://...",
      "path": "/api/trade/orders",
      "client": "127.0.0.1:50000"
    }
  }
}
```

---

## 📊 日志记录

### 客户端错误 (4xx)

**日志级别**: `warning`

```log
2025-12-29 10:30:45 [WARNING] Client error occurred
  error_code=1400
  error_name=QUANTITY_INVALID
  error_category=client
  exception_type=ValueError
  request_method=POST
  request_path=/api/trade/orders
  request_id=abc-123
  error_message=委托数量必须是100的整数倍(A股交易规则)
```

### 服务器错误 (5xx)

**日志级别**: `error`

```log
2025-12-29 10:31:15 [ERROR] Server error occurred
  error_code=9003
  error_name=DATABASE_ERROR
  error_category=server
  exception_type=SQLAlchemyError
  request_method=GET
  request_path=/api/market/kline
  request_id=def-456
  error_message=relation "market_data" does not exist
  stack_trace=Traceback (most recent call last):
    File "/app/api/market/routes.py", line 45, in get_kline
      result = db.execute(query)
  ...
```

---

## ✅ 最佳实践

### 1. 使用验证器而非手动验证

**❌ 不推荐**:
```python
@router.post("/orders")
async def create_order(order: OrderRequest):
    if order.quantity <= 0:
        raise ValueError("数量必须大于0")
    if order.quantity % 100 != 0:
        raise ValueError("数量必须是100的整数倍")
```

**✅ 推荐**:
```python
from app.core.validators import TradingValidator
from pydantic import BaseModel, field_validator

class OrderRequest(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        return TradingValidator.validate_quantity(v)
```

### 2. 使用统一的错误抛出方式

**❌ 不推荐**:
```python
# 混合使用不同的错误处理方式
return {"error": "insufficient funds"}
raise HTTPException(status_code=400, detail="insufficient")
raise ValueError("资金不足")
```

**✅ 推荐**:
```python
# 统一使用HTTPException或ValueError
from app.core.error_codes import ErrorCode, get_http_status, get_error_message

error_code = ErrorCode.INSUFFICIENT_CASH
raise HTTPException(
    status_code=get_http_status(error_code),
    detail={
        "code": error_code.value,
        "message": get_error_message(error_code)
    }
)
```

### 3. 前端统一错误处理

```typescript
async function handleAPICall<T>(apiCall: () => Promise<Response>): Promise<T> {
  const response = await apiCall();

  if (!response.ok) {
    const error: APIError = await response.json();

    // 根据错误码处理
    switch (error.code) {
      case 1400: // QUANTITY_INVALID
        showFieldError("quantity", error.message);
        break;
      case 4200: // INSUFFICIENT_CASH
        showErrorToast(error.message);
        break;
      case 6000: // AUTHENTICATION_FAILED
        redirectToLogin();
        break;
      default:
        showErrorToast(error.message);
    }

    throw new Error(error.message);
  }

  const data: APIResponse<T> = await response.json();
  return data.data as T;
}
```

---

## ✅ 验收标准

使用全局异常处理器后，所有API端点应满足:

- ✅ 所有异常都转换为统一响应格式
- ✅ 错误码正确映射到HTTP状态码
- ✅ 客户端错误(4xx)和服务器错误(5xx)明确区分
- ✅ 生产环境不暴露敏感信息
- ✅ 开发环境包含详细调试信息
- ✅ 所有错误都有详细的日志记录
- ✅ 支持监控和告警集成

---

## 📚 相关文档

- **错误码体系**: `docs/api/ERROR_CODE_GUIDE.md`
- **验证器使用**: `docs/api/VALIDATION_GUIDE.md`
- **统一响应格式**: `web/backend/app/schemas/common_schemas.py`
- **错误码定义**: `web/backend/app/core/error_codes.py`

---

**文档版本**: 1.0
**更新时间**: 2025-12-29
**维护者**: CLI-2 Backend API Architect
