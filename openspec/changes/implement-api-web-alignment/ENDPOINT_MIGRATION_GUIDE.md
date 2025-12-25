# API端点迁移指南 - 统一响应格式

**版本**: 1.0.0
**日期**: 2025-12-23
**目标**: 将所有遗留端点迁移到统一响应格式

---

## 📋 概述

本文档描述如何将现有的API端点迁移到新的统一响应格式。统一响应格式确保所有API端点返回一致的数据结构，简化前端处理并提高代码可维护性。

### 统一响应格式结构

```typescript
// 成功响应
{
  "success": true,
  "data": { ... },           // 响应数据
  "message": "操作成功",      // 可选消息
  "timestamp": "2025-12-23T10:00:00Z",
  "request_id": "req-123"    // 可选请求ID
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",    // 标准错误代码
    "message": "错误描述",
    "details": { ... }       // 可选详细信息
  },
  "message": "操作失败",
  "timestamp": "2025-12-23T10:00:00Z",
  "request_id": "req-123"
}

// 分页响应
{
  "success": true,
  "data": { "items": [...] },
  "message": "操作成功",
  "timestamp": "2025-12-23T10:00:00Z",
  "request_id": "req-123",
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## 🔄 迁移步骤

### 步骤 1: 导入统一响应模块

```python
from app.core.responses import (
    APIResponse,
    ErrorResponse,
    PaginatedResponse,
    create_success_response,
    create_error_response,
    create_health_response,
    ErrorCodes,
    ResponseMessages,
)
```

### 步骤 2: 定义Pydantic响应模型

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class StockInfo(BaseModel):
    """股票信息模型"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="当前价格")
    change: float = Field(..., description="涨跌幅")

class StockListResponse(BaseModel):
    """股票列表响应模型"""
    stocks: List[StockInfo]
    total: int
```

### 步骤 3: 更新端点函数

#### 迁移前 (旧格式):

```python
@router.get("/api/stocks/{symbol}")
async def get_stock_info(symbol: str):
    try:
        stock = await stock_service.get_stock(symbol)
        return {
            "data": stock,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }
```

#### 迁移后 (新格式):

```python
@router.get("/api/stocks/{symbol}")
async def get_stock_info(symbol: str, request: Request):
    request_id = getattr(request.state, "request_id", None)

    try:
        stock = await stock_service.get_stock(symbol)
        return create_success_response(
            data=stock,
            message="获取股票信息成功",
            request_id=request_id,
        )
    except ValueError as e:
        return create_error_response(
            error_code=ErrorCodes.VALIDATION_ERROR,
            message=f"参数验证失败: {str(e)}",
            request_id=request_id,
        )
    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"获取股票信息失败: {str(e)}",
            request_id=request_id,
        )
```

### 步骤 4: 处理分页响应

```python
@router.get("/api/stocks")
async def list_stocks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    request: Request = None,
):
    request_id = getattr(request.state, "request_id", None)

    try:
        # 获取数据和总数
        stocks, total = await stock_service.list_stocks(page, size)

        return PaginatedResponse.create(
            data={"items": stocks, "summary": {...}},
            page=page,
            size=size,
            total=total,
            message="查询成功",
            request_id=request_id,
        )
    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.DATABASE_ERROR,
            message=f"查询失败: {str(e)}",
            request_id=request_id,
        )
```

---

## 🎯 常见模式

### 模式 1: 简单GET请求

```python
@router.get("/api/health")
async def health_check(request: Request):
    """健康检查端点"""
    request_id = getattr(request.state, "request_id", None)

    try:
        status = await health_service.check()
        return create_health_response(
            service="api",
            status=status,
            request_id=request_id,
        )
    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.SERVICE_UNAVAILABLE,
            message=str(e),
            request_id=request_id,
        )
```

### 模式 2: POST创建请求

```python
@router.post("/api/strategies")
async def create_strategy(
    strategy_data: StrategyCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """创建策略"""
    request_id = getattr(request.state, "request_id", None)

    try:
        strategy = await strategy_service.create(
            strategy_data,
            user_id=current_user.id,
        )
        return create_success_response(
            data=strategy,
            message=ResponseMessages.CREATED,
            request_id=request_id,
        )
    except ValidationError as e:
        return create_error_response(
            error_code=ErrorCodes.VALIDATION_ERROR,
            message="请求数据验证失败",
            details={"errors": e.errors()},
            request_id=request_id,
        )
    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.OPERATION_FAILED,
            message=f"创建策略失败: {str(e)}",
            request_id=request_id,
        )
```

### 模式 3: PUT更新请求

```python
@router.put("/api/strategies/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdateRequest,
    request: Request,
):
    """更新策略"""
    request_id = getattr(request.state, "request_id", None)

    try:
        strategy = await strategy_service.update(strategy_id, strategy_data)
        return create_success_response(
            data=strategy,
            message=ResponseMessages.UPDATED,
            request_id=request_id,
        )
    except NotFoundError:
        return create_error_response(
            error_code=ErrorCodes.DATA_NOT_FOUND,
            message=f"策略 {strategy_id} 不存在",
            request_id=request_id,
        )
    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.OPERATION_FAILED,
            message=f"更新策略失败: {str(e)}",
            request_id=request_id,
        )
```

### 模式 4: DELETE删除请求

```python
@router.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    request: Request,
):
    """删除策略"""
    request_id = getattr(request.state, "request_id", None)

    try:
        await strategy_service.delete(strategy_id)
        return create_success_response(
            data={"deleted_id": strategy_id},
            message=ResponseMessages.DELETED,
            request_id=request_id,
        )
    except NotFoundError:
        return create_error_response(
            error_code=ErrorCodes.DATA_NOT_FOUND,
            message=f"策略 {strategy_id} 不存在",
            request_id=request_id,
        )
```

---

## 📊 错误代码映射

使用 `ErrorCodes` 类中的标准错误代码：

| 错误类型 | 错误代码 | HTTP状态码 | 使用场景 |
|---------|---------|-----------|---------|
| 参数错误 | `VALIDATION_ERROR` | 400 | 请求数据验证失败 |
| 未授权 | `UNAUTHORIZED` | 401 | 未登录或token无效 |
| 禁止访问 | `FORBIDDEN` | 403 | 权限不足 |
| 未找到 | `NOT_FOUND` | 404 | 资源不存在 |
| 数据未找到 | `DATA_NOT_FOUND` | 404 | 查询数据为空 |
| 重复资源 | `DUPLICATE_RESOURCE` | 409 | 资源已存在 |
| 数据库错误 | `DATABASE_ERROR` | 500 | 数据库操作失败 |
| 外部服务错误 | `EXTERNAL_SERVICE_ERROR` | 502 | 外部API调用失败 |
| 服务不可用 | `SERVICE_UNAVAILABLE` | 503 | 服务暂时不可用 |
| 内部错误 | `INTERNAL_SERVER_ERROR` | 500 | 其他未捕获错误 |

---

## ✅ 迁移检查清单

完成端点迁移后，确认以下项目：

- [ ] 导入了统一的响应模块
- [ ] 所有成功响应使用 `create_success_response()` 或 `create_health_response()`
- [ ] 所有错误响应使用 `create_error_response()`
- [ ] 分页响应使用 `PaginatedResponse.create()`
- [ ] 使用了标准 `ErrorCodes`
- [ ] 使用了标准 `ResponseMessages`
- [ ] 从 `request.state` 获取 `request_id`
- [ ] 正确处理了 `ValidationError` (返回400)
- [ ] 正确处理了 `NotFoundError` (返回404)
- [ ] 所有异常都被捕获并返回统一格式
- [ ] 端点文档已更新

---

## 🔧 待迁移端点列表

### 高优先级 (高流量端点)

| 端点 | 文件 | 优先级 | 状态 |
|-----|------|-------|-----|
| `/api/market/overview` | market.py | P0 | 待迁移 |
| `/api/market/realtime` | market.py | P0 | 待迁移 |
| `/api/strategy/list` | strategy_management.py | P0 | 待迁移 |
| `/api/backtest/run` | backtest_ws.py | P0 | 待迁移 |
| `/api/watchlist/*` | watchlist.py | P0 | 待迁移 |

### 中优先级

| 端点 | 文件 | 优先级 | 状态 |
|-----|------|-------|-----|
| `/api/market/fund-flow` | market.py | P1 | 部分完成 |
| `/api/technical/analyze` | technical_analysis.py | P1 | 待迁移 |
| `/api/trade/order` | trade/routes.py | P1 | 待迁移 |
| `/api/notification/*` | notification.py | P1 | 待迁移 |

### 低优先级

| 端点 | 文件 | 优先级 | 状态 |
|-----|------|-------|-----|
| `/api/monitoring/*` | monitoring/routes.py | P2 | 待迁移 |
| `/api/system/*` | system.py | P2 | 待迁移 |
| `/api/data-quality/*` | data_quality.py | P2 | 待迁移 |

---

## 📝 迁移模板

复制以下模板开始迁移：

```python
"""
[模块名] API 路由
统一响应格式版本
"""

from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel, ValidationError

from app.core.responses import (
    create_success_response,
    create_error_response,
    ErrorCodes,
    ResponseMessages,
)
from app.core.security import get_current_user, User
from app.services.[service_module] import [ServiceClass]

router = APIRouter(prefix="/api/[module]", tags=["[模块名]"])


# ============================================================================
# 响应模型
# ============================================================================

class [Resource]Response(BaseModel):
    """[资源]响应模型"""
    # 定义字段...
    pass


# ============================================================================
# 端点实现
# ============================================================================

@router.[method]("/[endpoint]")
async def [function_name](
    [params],
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    [端点描述]

    参数:
        - [param1]: [描述]
        - [param2]: [描述]

    返回:
        统一格式的响应
    """
    request_id = getattr(request.state, "request_id", None)

    try:
        # 业务逻辑
        result = await service.[method]([params])

        return create_success_response(
            data=result,
            message=ResponseMessages.SUCCESS,
            request_id=request_id,
        )

    except ValidationError as e:
        return create_error_response(
            error_code=ErrorCodes.VALIDATION_ERROR,
            message="数据验证失败",
            details={"errors": e.errors()},
            request_id=request_id,
        )

    except [CustomNotFoundError] as e:
        return create_error_response(
            error_code=ErrorCodes.DATA_NOT_FOUND,
            message=str(e),
            request_id=request_id,
        )

    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"操作失败: {str(e)}",
            request_id=request_id,
        )
```

---

## 🧪 测试迁移后的端点

使用 pytest 测试迁移后的端点：

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_success_response_format():
    """测试成功响应格式"""
    response = client.get("/api/stocks/600519")

    assert response.status_code == 200
    data = response.json()

    # 验证统一响应格式
    assert data["success"] is True
    assert "data" in data
    assert "message" in data
    assert "timestamp" in data
    assert "request_id" in data

def test_error_response_format():
    """测试错误响应格式"""
    response = client.get("/api/stocks/invalid_symbol")

    assert response.status_code in [400, 404, 500]
    data = response.json()

    # 验证统一错误格式
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]

def test_paginated_response_format():
    """测试分页响应格式"""
    response = client.get("/api/stocks?page=1&size=20")

    assert response.status_code == 200
    data = response.json()

    # 验证分页格式
    assert data["success"] is True
    assert "pagination" in data
    assert "page" in data["pagination"]
    assert "size" in data["pagination"]
    assert "total" in data["pagination"]
    assert "pages" in data["pagination"]
```

---

## 📚 参考资料

- **统一响应模块**: `web/backend/app/core/responses.py`
- **已迁移示例**: `web/backend/app/api/health.py`
- **单元测试**: `web/backend/tests/test_responses.py`
- **任务跟踪**: `openspec/changes/implement-api-web-alignment/tasks.md`

---

**最后更新**: 2025-12-23
**维护者**: Backend Team
