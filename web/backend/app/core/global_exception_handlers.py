"""
FastAPI全局异常处理器 - 数据源架构优化 Phase 1

本模块实现FastAPI应用的全局异常处理，提供统一的错误响应格式。
与现有的decorator-based exception_handlers.py配合使用。

核心功能：
1. 捕获所有MyStocks自定义异常并转换为HTTP响应
2. 提供结构化的错误响应格式
3. 区分不同级别的异常（客户端错误 vs 服务器错误）
4. 记录详细的错误日志便于排查

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 导入自定义异常类
try:
    from src.core.exceptions import (
        MyStocksException,
        DataException,
        DatabaseException,
        ConfigException,
        NetworkException,
        SecurityException,
        ProcessingException,
        BusinessLogicException,
        DataSourceException,
        DataSourceConnectionError,
        DataSourceQueryError,
        DataSourceDataNotFound,
        DataSourceTimeout,
        DataSourceConfigError,
        DataSourceDataFormatError,
        DataSourceUnavailable,
        AuthenticationError,
        AuthorizationError,
    )
except ImportError:
    # 兼容性处理：如果导入失败，使用基础Exception
    MyStocksException = Exception
    DataSourceException = Exception

# 配置日志
logger = logging.getLogger(__name__)


# ==================== 异常响应格式化 ====================


def format_exception_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """
    格式化异常响应

    Args:
        error_code: 错误代码
        message: 错误消息
        details: 详细错误信息
        path: 请求路径
        timestamp: 错误发生时间

    Returns:
        Dict: 标准错误响应格式

    响应格式:
        {
            "error": {
                "code": "MSE8001",
                "message": "Database connection failed",
                "details": {...},
                "timestamp": "2025-11-21T10:30:00",
                "path": "/api/market/quotes"
            }
        }
    """
    return {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "path": path,
        }
    }


# ==================== MyStocks自定义异常处理器 ====================


async def mystocks_exception_handler(
    request: Request, exc: MyStocksException
) -> JSONResponse:
    """
    处理所有MyStocks自定义异常

    自动根据异常类型确定HTTP状态码：
    - 数据源异常: 根据具体类型返回400/404/500/503
    - 数据异常: 400/404
    - 数据库异常: 500
    - 配置异常: 500
    - 网络异常: 502/504
    - 安全异常: 401/403
    - 处理异常: 400
    - 业务逻辑异常: 400/422
    """
    # 根据异常类型确定HTTP状态码
    if isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, DataSourceDataNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DataSourceTimeout):
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
    elif isinstance(exc, DataSourceUnavailable):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, (DataSourceConnectionError, NetworkException)):
        status_code = status.HTTP_502_BAD_GATEWAY
    elif isinstance(exc, (DataSourceConfigError, DatabaseException, ConfigException)):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(
        exc,
        (
            DataSourceQueryError,
            DataSourceDataFormatError,
            DataException,
            ProcessingException,
            BusinessLogicException,
        ),
    ):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, DataSourceException):
        # 通用数据源异常，默认500
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        # 其他MyStocks异常，默认500
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # 记录错误日志
    log_level = logging.ERROR if status_code >= 500 else logging.WARNING
    logger.log(
        log_level,
        f"MyStocks Exception: [{exc.error_code}] {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
            "status_code": status_code,
        },
        exc_info=(status_code >= 500),  # 500错误记录完整堆栈
    )

    # 返回格式化响应
    response_data = format_exception_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        timestamp=exc.timestamp,
    )

    return JSONResponse(status_code=status_code, content=response_data)


# ==================== FastAPI内置异常处理器 ====================


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求参数验证错误

    当请求参数不符合Pydantic模型定义时触发。
    """
    logger.warning(
        f"Request validation error: {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )

    response_data = format_exception_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"validation_errors": exc.errors()},
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response_data
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    处理HTTP异常

    捕获FastAPI/Starlette的HTTPException。
    """
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {request.url.path}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )

    response_data = format_exception_response(
        error_code=f"HTTP_{exc.status_code}", message=exc.detail, path=request.url.path
    )

    return JSONResponse(status_code=exc.status_code, content=response_data)


# ==================== 通用异常处理器 ====================


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理所有未被捕获的异常

    作为兜底机制，防止异常泄露给客户端。
    记录完整堆栈信息便于排查问题。
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
        exc_info=True,  # 记录完整堆栈
    )

    response_data = format_exception_response(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Please try again later.",
        details={"exception_type": type(exc).__name__},
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_data
    )


# ==================== 异常处理器注册 ====================


def register_global_exception_handlers(app: FastAPI) -> None:
    """
    注册所有全局异常处理器到FastAPI应用

    调用此函数可一次性注册所有异常处理器。

    Args:
        app: FastAPI应用实例

    使用示例:
        from fastapi import FastAPI
        from web.backend.app.core.global_exception_handlers import register_global_exception_handlers

        app = FastAPI()
        register_global_exception_handlers(app)
    """
    # MyStocks自定义异常
    try:
        app.add_exception_handler(MyStocksException, mystocks_exception_handler)
        logger.info("MyStocks exception handlers registered")
    except Exception as e:
        logger.warning(f"Failed to register MyStocks exception handler: {e}")

    # FastAPI内置异常
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # 通用异常兜底
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("All global exception handlers registered successfully")
