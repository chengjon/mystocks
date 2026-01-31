"""
统一响应模型使用示例

展示如何在 FastAPI 路由中使用 base.py 的响应模型
"""

from typing import Dict, List

from fastapi import APIRouter, Query

from app.models.base import (
    BaseResponse,
    ErrorCode,
    HealthCheckResponse,
    PagedResponse,
    error_response,
    paged_response,
    success_response,
)

# 创建示例路由
router = APIRouter()


# ============================================================================
# 示例 1: 使用 BaseResponse 返回单个对象
# ============================================================================


@router.get("/stock/{symbol}", response_model=BaseResponse[Dict])
async def get_stock_info(symbol: str):
    """
    获取股票信息（使用 BaseResponse 模型）

    返回格式:
    {
        "success": true,
        "message": "查询成功",
        "data": {"symbol": "600000", "name": "浦发银行", "price": 10.50},
        "timestamp": "2025-10-25T10:30:00Z"
    }
    """
    try:
        # 模拟从数据库查询
        stock_data = {
            "symbol": symbol,
            "name": "浦发银行",
            "price": 10.50,
            "volume": 1000000,
        }

        # 方式1: 使用辅助函数（推荐）
        return success_response(data=stock_data, message="查询成功")

        # 方式2: 直接构造模型
        # return BaseResponse(
        #     success=True,
        #     message="查询成功",
        #     data=stock_data
        # ).model_dump()

    except Exception as e:
        # 返回错误响应
        return error_response(
            message=f"查询失败: {str(e)}",
            error_code=ErrorCode.DATABASE_ERROR,
            details={"symbol": symbol, "error": str(e)},
        )


# ============================================================================
# 示例 2: 使用 PagedResponse 返回分页列表
# ============================================================================


@router.get("/stocks", response_model=PagedResponse[Dict])
async def list_stocks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    market: str = Query("cn", description="市场类型"),
):
    """
    获取股票列表（使用 PagedResponse 模型）

    返回格式:
    {
        "success": true,
        "message": "查询成功",
        "data": [
            {"symbol": "600000", "name": "浦发银行"},
            {"symbol": "600519", "name": "贵州茅台"}
        ],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5,
        "has_next": true,
        "has_prev": false,
        "timestamp": "2025-10-25T10:30:00Z"
    }
    """
    try:
        # 模拟数据查询
        total_count = 100
        stock_list = [
            {"symbol": "600000", "name": "浦发银行", "price": 10.50},
            {"symbol": "600519", "name": "贵州茅台", "price": 1800.00},
            {"symbol": "000001", "name": "平安银行", "price": 15.20},
        ]

        # 使用辅助函数创建分页响应（推荐）
        return paged_response(
            data=stock_list,
            total=total_count,
            page=page,
            page_size=page_size,
            message="股票列表查询成功",
        )

        # 或直接构造模型
        # return PagedResponse(
        #     success=True,
        #     message="查询成功",
        #     data=stock_list,
        #     total=total_count,
        #     page=page,
        #     page_size=page_size
        # ).model_dump()

    except Exception as e:
        return error_response(
            message=f"查询失败: {str(e)}",
            error_code=ErrorCode.DATABASE_ERROR,
            details={"market": market, "error": str(e)},
        )


# ============================================================================
# 示例 3: 使用 ErrorResponse 返回错误
# ============================================================================


@router.post("/order/create")
async def create_order(symbol: str, quantity: int, price: float):
    """
    创建订单（演示错误响应）

    错误响应格式:
    {
        "success": false,
        "message": "股票代码格式不正确",
        "error_code": "INVALID_PARAMETER",
        "details": {
            "field": "symbol",
            "value": "abc",
            "expected": "6位数字"
        },
        "timestamp": "2025-10-25T10:30:00Z",
        "path": "/api/order/create"
    }
    """
    # 参数验证
    if not symbol or len(symbol) != 6 or not symbol.isdigit():
        return error_response(
            message="股票代码格式不正确",
            error_code=ErrorCode.INVALID_PARAMETER,
            details={"field": "symbol", "value": symbol, "expected": "6位数字"},
            path="/api/order/create",
        )

    if quantity <= 0:
        return error_response(
            message="数量必须大于0",
            error_code=ErrorCode.INVALID_PARAMETER,
            details={"field": "quantity", "value": quantity},
        )

    if price <= 0:
        return error_response(
            message="价格必须大于0",
            error_code=ErrorCode.INVALID_PARAMETER,
            details={"field": "price", "value": price},
        )

    # 模拟业务逻辑错误
    user_balance = 10000.0
    order_amount = quantity * price

    if order_amount > user_balance:
        return error_response(
            message="余额不足",
            error_code=ErrorCode.INSUFFICIENT_BALANCE,
            details={
                "balance": user_balance,
                "required": order_amount,
                "shortage": order_amount - user_balance,
            },
        )

    # 成功创建订单
    order_data = {
        "order_id": "ORD123456",
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "status": "pending",
    }

    return success_response(data=order_data, message="订单创建成功")


# ============================================================================
# 示例 4: 使用 HealthCheckResponse 返回健康检查
# ============================================================================


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    系统健康检查

    返回格式:
    {
        "status": "healthy",
        "version": "2.0.0",
        "uptime": 86400.5,
        "timestamp": "2025-10-25T10:30:00Z",
        "services": {
            "postgresql": {"status": "healthy", "latency_ms": 5},
            "tdengine": {"status": "healthy", "latency_ms": 8}
        }
    }
    """
    import time

    # 模拟服务检查
    start_time = time.time() - 86400.5  # 假设运行了1天

    services_status = {
        "postgresql": {"status": "healthy", "latency_ms": 5},
        "tdengine": {"status": "healthy", "latency_ms": 8},
        "monitoring": {"status": "healthy", "latency_ms": 3},
    }

    # 判断整体状态
    all_healthy = all(svc["status"] == "healthy" for svc in services_status.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        version="2.0.0",
        uptime=time.time() - start_time,
        services=services_status,
    ).model_dump()


# ============================================================================
# 示例 5: FastAPI 异常处理器集成
# ============================================================================

from fastapi import Request
from fastapi.responses import JSONResponse


async def custom_exception_handler(request: Request, exc: Exception):
    """
    自定义异常处理器

    捕获所有未处理的异常并返回标准错误响应
    """
    return JSONResponse(
        status_code=500,
        content=error_response(
            message=str(exc),
            error_code=ErrorCode.INTERNAL_ERROR,
            path=str(request.url),
            details={"type": type(exc).__name__},
        ),
    )


# 在 FastAPI app 中注册异常处理器:
# from fastapi import FastAPI
# app = FastAPI()
# app.add_exception_handler(Exception, custom_exception_handler)


# ============================================================================
# 示例 6: 类型提示和 IDE 自动补全
# ============================================================================


@router.get("/typed-response", response_model=BaseResponse[List[Dict]])
async def typed_response_example():
    """
    展示泛型类型提示的好处

    通过指定 BaseResponse[List[Dict]]，IDE 可以提供更好的类型检查和自动补全
    """
    data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

    # IDE 会知道 data 是 List[Dict] 类型
    # 提供更好的类型检查和自动补全
    return success_response(data=data, message="查询成功")


# ============================================================================
# 使用建议
# ============================================================================

"""
1. 统一使用 success_response(), error_response(), paged_response() 辅助函数
   - 代码更简洁
   - 自动设置默认值
   - 减少重复代码

2. 在路由装饰器中指定 response_model
   - FastAPI 会自动生成 OpenAPI 文档
   - 提供类型验证
   - 自动生成 Swagger UI

3. 使用 ErrorCode 常量类定义错误码
   - 避免硬编码字符串
   - 便于统一管理
   - IDE 自动补全

4. 记录请求追踪 ID (request_id)
   - 便于日志追踪
   - 方便排查问题
   - 可集成分布式追踪系统

5. 在异常处理器中返回标准错误响应
   - 确保所有错误格式一致
   - 前端可以统一处理
   - 提供更好的用户体验

示例代码整合到路由:
---------------------------
from fastapi import FastAPI
from app.models.base_example import router

app = FastAPI()
app.include_router(router, prefix="/api/v1", tags=["examples"])

访问示例:
- GET  /api/v1/stock/600000         # 单个对象响应
- GET  /api/v1/stocks?page=1        # 分页列表响应
- POST /api/v1/order/create         # 错误响应示例
- GET  /api/v1/health               # 健康检查响应
- GET  /api/v1/typed-response       # 类型提示示例
"""
