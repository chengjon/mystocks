# 统一错误码体系使用指南

本文档说明如何使用MyStocks API的统一错误码体系。

## 📦 模块概览

### `error_codes.py` - 统一错误码体系

提供完整的错误码定义、HTTP状态码映射和中文错误消息。

```python
from app.core.error_codes import (
    ErrorCode,
    HTTPStatus,
    ErrorCategory,
    get_http_status,
    get_error_message,
    get_error_category,
    is_success,
    is_client_error,
    is_server_error,
)
```

---

## 🚀 快速开始

### 示例1: 在API端点中使用错误码

```python
from fastapi import HTTPException
from app.core.error_codes import ErrorCode, get_http_status, get_error_message

@router.post("/trade/orders")
async def create_order(order: OrderRequest):
    # 业务逻辑验证
    if order.quantity % 100 != 0:
        error_code = ErrorCode.QUANTITY_INVALID

        raise HTTPException(
            status_code=get_http_status(error_code),
            detail={
                "code": error_code.value,
                "message": get_error_message(error_code)
            }
        )

    # ... 正常业务逻辑
```

**错误响应示例**:
```json
{
  "detail": {
    "code": 1400,
    "message": "委托数量必须是100的整数倍(A股交易规则)"
  }
}
```

### 示例2: 判断错误类型

```python
from app.core.error_codes import ErrorCode, is_client_error, is_server_error

def handle_error(error_code: ErrorCode):
    if is_success(error_code):
        print("操作成功")
    elif is_client_error(error_code):
        print(f"客户端错误: {error_code.value}")
        # 客户端错误 - 需要用户修正输入
    elif is_server_error(error_code):
        print(f"服务器错误: {error_code.value}")
        # 服务器错误 - 需要运维人员介入
```

---

## 📋 错误码分类

### 错误码结构

```
错误码设计规则:
- 0: 成功
- 1xxx: 通用错误 (参数验证、格式错误等)
- 2xxx: Market模块错误
- 3xxx: Technical模块错误
- 4xxx: Trade模块错误
- 5xxx: Strategy模块错误
- 6xxx: System模块错误
- 9xxx: 服务器内部错误
```

### 主要错误码列表

| 错误码 | 名称 | HTTP状态码 | 中文消息 |
|--------|------|-----------|---------|
| **0** | SUCCESS | 200 | 操作成功 |
| **1001** | VALIDATION_ERROR | 422 | 输入参数验证失败 |
| **1102** | SYMBOL_INVALID_FORMAT | 400 | 股票代码格式不正确... |
| **1201** | DATE_INVALID_FORMAT | 400 | 日期格式不正确... |
| **1400** | QUANTITY_INVALID | 400 | 委托数量必须是100的整数倍... |
| **2000** | KLINE_INTERVAL_INVALID | 400 | K线周期不正确... |
| **3001** | OVERLAY_INDICATOR_INVALID | 400 | 主图叠加指标不正确... |
| **4000** | ORDER_NOT_FOUND | 404 | 委托不存在 |
| **4100** | INSUFFICIENT_POSITION | 409 | 持仓数量不足 |
| **4200** | INSUFFICIENT_CASH | 409 | 可用资金不足 |
| **4300** | MARKET_CLOSED | 409 | 市场休市中，无法交易 |
| **6000** | AUTHENTICATION_FAILED | 401 | 身份验证失败 |
| **6005** | RATE_LIMIT_EXCEEDED | 429 | 请求过于频繁，请稍后再试 |
| **9000** | INTERNAL_SERVER_ERROR | 500 | 服务器内部错误 |

---

## 🔧 工具函数

### `get_http_status(error_code: ErrorCode) -> int`

获取错误码对应的HTTP状态码。

```python
from app.core.error_codes import ErrorCode, get_http_status

http_status = get_http_status(ErrorCode.QUANTITY_INVALID)
print(http_status)  # 400
```

### `get_error_message(error_code: ErrorCode) -> str`

获取错误码对应的中文消息。

```python
from app.core.error_codes import ErrorCode, get_error_message

message = get_error_message(ErrorCode.INSUFFICIENT_CASH)
print(message)  # "可用资金不足"
```

### `get_error_category(error_code: ErrorCode) -> ErrorCategory`

获取错误码的类别。

```python
from app.core.error_codes import ErrorCode, get_error_category, ErrorCategory

category = get_error_category(ErrorCode.VALIDATION_ERROR)
print(category)  # ErrorCategory.CLIENT_ERROR
```

### `is_success(error_code: ErrorCode) -> bool`

判断是否为成功错误码。

```python
from app.core.error_codes import ErrorCode, is_success

print(is_success(ErrorCode.SUCCESS))  # True
print(is_success(ErrorCode.BAD_REQUEST))  # False
```

### `is_client_error(error_code: ErrorCode) -> bool`

判断是否为客户端错误。

```python
from app.core.error_codes import ErrorCode, is_client_error

print(is_client_error(ErrorCode.QUANTITY_INVALID))  # True
print(is_client_error(ErrorCode.INTERNAL_SERVER_ERROR))  # False
```

### `is_server_error(error_code: ErrorCode) -> bool`

判断是否为服务器错误。

```python
from app.core.error_codes import ErrorCode, is_server_error

print(is_server_error(ErrorCode.DATABASE_ERROR))  # True
print(is_server_error(ErrorCode.BAD_REQUEST))  # False
```

---

## 📝 HTTP状态码映射规则

### 成功响应 (2xx)

| 错误码 | HTTP状态码 | 场景 |
|--------|-----------|------|
| 0 (SUCCESS) | 200 OK | 操作成功 |

### 客户端错误 (4xx)

| HTTP状态码 | 错误码示例 | 场景 |
|-----------|----------|------|
| 400 Bad Request | 1000 (BAD_REQUEST) | 请求参数错误 |
| 401 Unauthorized | 6000 (AUTHENTICATION_FAILED) | 身份验证失败 |
| 403 Forbidden | 4402 (RISK_LEVEL_HIGH) | 风险等级过高 |
| 404 Not Found | 4000 (ORDER_NOT_FOUND) | 资源不存在 |
| 409 Conflict | 4200 (INSUFFICIENT_CASH) | 业务冲突(资金不足) |
| 422 Unprocessable Entity | 1001 (VALIDATION_ERROR) | 参数验证失败 |
| 429 Too Many Requests | 6005 (RATE_LIMIT_EXCEEDED) | 请求过于频繁 |

### 服务器错误 (5xx)

| HTTP状态码 | 错误码示例 | 场景 |
|-----------|----------|------|
| 500 Internal Server Error | 9000 (INTERNAL_SERVER_ERROR) | 服务器内部错误 |
| 502 Bad Gateway | 9001 (EXTERNAL_SERVICE_ERROR) | 外部服务失败 |
| 503 Service Unavailable | 9002 (SERVICE_UNAVAILABLE) | 服务暂不可用 |

---

## 🎯 最佳实践

### 1. 在FastAPI端点中使用

```python
from fastapi import HTTPException, status
from app.core.error_codes import ErrorCode, get_http_status, get_error_message
from app.core.validators import TradingValidator
from app.core.validation_messages import CommonMessages

@router.post("/trade/orders")
async def create_order(order: OrderRequest):
    # 验证股票代码
    try:
        symbol = StockSymbolValidator.validate_format(order.symbol)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.SYMBOL_INVALID_FORMAT.value,
                "message": str(e)
            }
        )

    # 验证委托数量
    try:
        quantity = TradingValidator.validate_quantity(order.quantity)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.QUANTITY_INVALID.value,
                "message": str(e)
            }
        )

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

    # ... 执行下单逻辑
```

### 2. 在异常处理器中使用

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.error_codes import ErrorCode, get_error_message
from app.core.schemas.common_schemas import APIResponse

async def custom_exception_handler(request: Request, exc: Exception):
    """自定义异常处理器"""

    # 根据异常类型确定错误码
    if isinstance(exc, ValueError):
        error_code = ErrorCode.VALIDATION_ERROR
    elif isinstance(exc, PermissionError):
        error_code = ErrorCode.AUTHORIZATION_FAILED
    else:
        error_code = ErrorCode.INTERNAL_SERVER_ERROR

    # 构建统一响应格式
    response = APIResponse(
        success=False,
        code=error_code.value,
        message=get_error_message(error_code),
        data=None
    )

    return JSONResponse(
        status_code=get_http_status(error_code),
        content=response.model_dump()
    )
```

### 3. 前端错误处理

```typescript
// TypeScript类型定义
interface APIError {
  code: number;
  message: string;
}

interface APIResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T | null;
}

// 错误处理函数
async function handleAPICall<T>(apiCall: () => Promise<APIResponse<T>>): Promise<T> {
  const response = await apiCall();

  if (!response.success) {
    // 根据错误码处理不同错误
    switch (response.code) {
      case 1400: // QUANTITY_INVALID
        throw new Error("委托数量必须是100的整数倍");
      case 4200: // INSUFFICIENT_CASH
        throw new Error("可用资金不足");
      case 4300: // MARKET_CLOSED
        throw new Error("市场休市中，无法交易");
      case 6000: // AUTHENTICATION_FAILED
        // 跳转到登录页
        window.location.href = "/login";
        throw new Error("请先登录");
      default:
        throw new Error(response.message);
    }
  }

  return response.data as T;
}

// 使用示例
try {
  const result = await handleAPICall(() => api.createOrder(orderData));
  console.log("下单成功", result);
} catch (error) {
  console.error("下单失败", error.message);
  // 显示错误提示给用户
  showErrorToast(error.message);
}
```

---

## 🔄 与validation_messages.py集成

错误码体系与`validation_messages.py`完全集成:

```python
from app.core.error_codes import ErrorCode, get_error_message
from app.core.validation_messages import CommonMessages

# 错误消息优先从validation_messages获取
message = get_error_message(ErrorCode.SYMBOL_INVALID_FORMAT)
# message == CommonMessages.SYMBOL_INVALID_FORMAT

# 所有错误消息都是中文
print(message)  # "股票代码格式不正确，应为6位数字或6位数字.交易所后缀(如600519.SH)"
```

---

## ✅ 验收标准

使用错误码体系后，所有API端点应满足:

- ✅ 所有错误都有对应的错误码
- ✅ 错误码正确映射到HTTP状态码
- ✅ 错误消息都是中文且用户友好
- ✅ 客户端错误(4xx)和服务器错误(5xx)明确区分
- ✅ 错误响应格式统一
- ✅ 前端可根据错误码实现不同的错误处理逻辑

---

## 📚 相关文档

- **验证器使用指南**: `docs/guides/VALIDATION_GUIDE.md`
- **统一响应格式**: `web/backend/app/schemas/common_schemas.py`
- **OpenAPI模板**: `docs/api/openapi_template.yaml`

---

**文档版本**: 1.0
**更新时间**: 2025-12-29
**维护者**: CLI-2 Backend API Architect
