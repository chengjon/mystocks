"""
全局异常处理器 (Global Exception Handler)

统一处理所有异常,转换为标准APIResponse格式
与error_codes.py和common_schemas.py集成
"""

import os
import traceback
from typing import Union
from datetime import datetime

from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.error_codes import (
    ErrorCode,
    get_http_status,
    get_error_message,
    is_client_error,
)
from app.schemas.common_schemas import APIResponse


# ==================== 配置 ====================


class ExceptionHandlerConfig:
    """异常处理器配置"""

    # 生产环境: 不暴露详细错误信息
    PRODUCTION: bool = os.getenv("ENVIRONMENT", "development") == "production"

    # 是否记录完整堆栈跟踪到日志
    LOG_STACK_TRACE: bool = True

    # 是否在响应中包含堆栈跟踪（仅开发环境）
    INCLUDE_STACK_TRACE: bool = not PRODUCTION

    # 是否在响应中包含请求信息（仅开发环境）
    INCLUDE_REQUEST_INFO: bool = not PRODUCTION


config = ExceptionHandlerConfig()


# ==================== 异常处理器 ====================


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器 - 处理所有未捕获的异常

    Args:
        request: FastAPI请求对象
        exc: 异常对象

    Returns:
        JSONResponse - 统一错误响应格式
    """
    # 获取请求ID
    request_id = getattr(request.state, "request_id", "unknown")

    # 确定错误码和HTTP状态码
    error_code, http_status = _determine_error_code_and_status(exc)

    # 获取错误消息
    error_message = get_error_message(error_code)

    # 构建错误详情
    error_detail = _build_error_detail(exc, request, error_code)

    # 记录错误日志
    _log_error(exc, request, error_code, error_detail)

    # 构建响应内容
    response_content = APIResponse(
        success=False,
        code=error_code.value,
        message=error_message,
        data=None,
        request_id=request_id,
        timestamp=datetime.now(),
    )

    # 在开发环境中添加额外信息
    if not config.PRODUCTION:
        response_content.detail = error_detail

    return JSONResponse(
        status_code=http_status,
        content=response_content.model_dump(exclude_none=True, exclude_unset=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP异常处理器 - 处理HTTPException

    Args:
        request: FastAPI请求对象
        exc: HTTPException对象

    Returns:
        JSONResponse - 统一错误响应格式
    """
    # 获取请求ID
    request_id = getattr(request.state, "request_id", "unknown")

    # 确定错误码和HTTP状态码
    error_code = _map_http_status_to_error_code(exc.status_code)
    http_status = exc.status_code

    # 获取错误消息
    error_message = get_error_message(error_code)

    # 如果exception中包含detail,使用它作为消息
    if exc.detail:
        # 如果detail是字典,提取message
        if isinstance(exc.detail, dict):
            error_message = exc.detail.get("message", error_message)
        elif isinstance(exc.detail, str):
            # 生产环境不暴露原始错误消息
            if not config.PRODUCTION or is_client_error(error_code):
                error_message = exc.detail

    # 构建错误详情
    error_detail = _build_error_detail(exc, request, error_code)

    # 记录错误日志
    _log_error(exc, request, error_code, error_detail)

    # 构建响应内容
    response_content = APIResponse(
        success=False,
        code=error_code.value,
        message=error_message,
        data=None,
        request_id=request_id,
        timestamp=datetime.now(),
    )

    # 在开发环境中添加额外信息
    if not config.PRODUCTION:
        response_content.detail = error_detail

    return JSONResponse(
        status_code=http_status,
        content=response_content.model_dump(exclude_none=True, exclude_unset=True),
    )


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    验证异常处理器 - 处理Pydantic验证错误

    Args:
        request: FastAPI请求对象
        exc: 验证异常对象

    Returns:
        JSONResponse - 统一错误响应格式
    """
    # 获取请求ID
    request_id = getattr(request.state, "request_id", "unknown")

    # 确定错误码
    error_code = ErrorCode.VALIDATION_ERROR
    http_status = get_http_status(error_code)

    # 获取错误消息
    error_message = get_error_message(error_code)

    # 解析验证错误
    validation_errors = _parse_validation_errors(exc)

    # 构建错误详情
    error_detail = {
        "validation_errors": validation_errors,
        "error_count": len(validation_errors),
    }

    # 记录错误日志
    _log_error(exc, request, error_code, error_detail)

    # 构建响应内容
    response_content = APIResponse(
        success=False,
        code=error_code.value,
        message=error_message,
        data=None,
        request_id=request_id,
        timestamp=datetime.now(),
    )

    # 在开发环境中添加额外信息
    if not config.PRODUCTION:
        response_content.detail = error_detail

    return JSONResponse(
        status_code=http_status,
        content=response_content.model_dump(exclude_none=True, exclude_unset=True),
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    数据库异常处理器 - 处理SQLAlchemy异常

    Args:
        request: FastAPI请求对象
        exc: SQLAlchemy异常对象

    Returns:
        JSONResponse - 统一错误响应格式
    """
    # 获取请求ID
    request_id = getattr(request.state, "request_id", "unknown")

    # 确定错误码
    error_code = ErrorCode.DATABASE_ERROR
    http_status = get_http_status(error_code)

    # 获取错误消息
    error_message = get_error_message(error_code)

    # 生产环境不暴露数据库错误详情
    if config.PRODUCTION:
        error_detail = {"type": "DatabaseError"}
    else:
        error_detail = {
            "type": type(exc).__name__,
            "message": str(exc),
            "original_error": _format_exception(exc),
        }

    # 记录错误日志
    _log_error(exc, request, error_code, error_detail)

    # 构建响应内容
    response_content = APIResponse(
        success=False,
        code=error_code.value,
        message=error_message,
        data=None,
        request_id=request_id,
        timestamp=datetime.now(),
    )

    # 在开发环境中添加额外信息
    if not config.PRODUCTION:
        response_content.detail = error_detail

    return JSONResponse(
        status_code=http_status,
        content=response_content.model_dump(exclude_none=True, exclude_unset=True),
    )


# ==================== 辅助函数 ====================


def _determine_error_code_and_status(exc: Exception) -> tuple[ErrorCode, int]:
    """
    根据异常类型确定错误码和HTTP状态码

    Args:
        exc: 异常对象

    Returns:
        (错误码, HTTP状态码) 元组
    """
    # HTTPException
    if isinstance(exc, HTTPException):
        error_code = _map_http_status_to_error_code(exc.status_code)
        return error_code, exc.status_code

    # 验证错误
    if isinstance(exc, (RequestValidationError, ValidationError)):
        error_code = ErrorCode.VALIDATION_ERROR
        return error_code, get_http_status(error_code)

    # 数据库错误
    if isinstance(exc, SQLAlchemyError):
        error_code = ErrorCode.DATABASE_ERROR
        return error_code, get_http_status(error_code)

    # 权限错误
    if isinstance(exc, PermissionError):
        error_code = ErrorCode.AUTHORIZATION_FAILED
        return error_code, get_http_status(error_code)

    # 值错误 (通常是业务逻辑验证失败)
    if isinstance(exc, ValueError):
        # 尝试从错误消息中推断具体的错误码
        error_message = str(exc).lower()

        # 股票代码相关
        if "symbol" in error_message or "股票代码" in error_message:
            return ErrorCode.SYMBOL_INVALID, get_http_status(ErrorCode.SYMBOL_INVALID)

        # 日期相关
        if "date" in error_message or "日期" in error_message:
            return ErrorCode.DATE_INVALID, get_http_status(ErrorCode.DATE_INVALID)

        # 数量相关
        if "quantity" in error_message or "数量" in error_message:
            return ErrorCode.QUANTITY_INVALID, get_http_status(ErrorCode.QUANTITY_INVALID)

        # 资金相关
        if "cash" in error_message or "资金" in error_message:
            return ErrorCode.INSUFFICIENT_CASH, get_http_status(ErrorCode.INSUFFICIENT_CASH)

        # 默认验证错误
        error_code = ErrorCode.VALIDATION_ERROR
        return error_code, get_http_status(error_code)

    # 默认服务器内部错误
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    return error_code, get_http_status(error_code)


def _map_http_status_to_error_code(http_status: int) -> ErrorCode:
    """
    将HTTP状态码映射到错误码

    Args:
        http_status: HTTP状态码

    Returns:
        错误码枚举
    """
    mapping = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.AUTHENTICATION_FAILED,
        403: ErrorCode.AUTHORIZATION_FAILED,
        404: ErrorCode.ORDER_NOT_FOUND,  # 假设大多是资源未找到
        405: ErrorCode.METHOD_NOT_ALLOWED,
        409: ErrorCode.MARKET_CLOSED,  # 假设大多是业务冲突
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        502: ErrorCode.EXTERNAL_SERVICE_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }

    return mapping.get(http_status, ErrorCode.INTERNAL_SERVER_ERROR)


def _parse_validation_errors(exc: Union[RequestValidationError, ValidationError]) -> list[dict]:
    """
    解析Pydantic验证错误

    Args:
        exc: 验证异常对象

    Returns:
        错误列表
    """
    if isinstance(exc, RequestValidationError):
        # FastAPI RequestValidationError
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        return errors
    else:
        # Pydantic ValidationError
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        return errors


def _build_error_detail(exc: Exception, request: Request, error_code: ErrorCode) -> dict:
    """
    构建错误详情

    Args:
        exc: 异常对象
        request: FastAPI请求对象
        error_code: 错误码

    Returns:
        错误详情字典
    """
    detail = {
        "type": type(exc).__name__,
        "error_code": error_code.value,
        "error_category": "client" if is_client_error(error_code) else "server",
    }

    # 在开发环境中添加更多信息
    if not config.PRODUCTION:
        detail["message"] = str(exc)

        if config.INCLUDE_STACK_TRACE:
            detail["stack_trace"] = _format_exception(exc)

        if config.INCLUDE_REQUEST_INFO:
            detail["request"] = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client": f"{request.client.host}:{request.client.port}" if request.client else "unknown",
            }

    return detail


def _format_exception(exc: Exception) -> str:
    """
    格式化异常堆栈跟踪

    Args:
        exc: 异常对象

    Returns:
        格式化的堆栈跟踪字符串
    """
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def _log_error(exc: Exception, request: Request, error_code: ErrorCode, detail: dict):
    """
    记录错误日志

    Args:
        exc: 异常对象
        request: FastAPI请求对象
        error_code: 错误码
        detail: 错误详情
    """
    import structlog

    logger = structlog.get_logger()

    # 构建日志上下文
    log_context = {
        "error_code": error_code.value,
        "error_name": error_code.name,
        "error_category": "client" if is_client_error(error_code) else "server",
        "exception_type": type(exc).__name__,
        "request_method": request.method,
        "request_path": request.url.path,
        "request_id": getattr(request.state, "request_id", "unknown"),
    }

    # 根据错误级别选择日志级别
    if is_client_error(error_code):
        # 客户端错误 - warning级别
        logger.warning("Client error occurred", **log_context, error_message=str(exc))
    else:
        # 服务器错误 - error级别
        if config.LOG_STACK_TRACE:
            log_context["stack_trace"] = _format_exception(exc)

        logger.error("Server error occurred", **log_context, error_message=str(exc))


# ==================== 注册函数 ====================


def register_exception_handlers(app):
    """
    注册所有异常处理器到FastAPI应用

    Args:
        app: FastAPI应用实例
    """
    # 全局异常处理器 (处理所有未捕获的异常)
    app.add_exception_handler(Exception, global_exception_handler)

    # HTTP异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)

    # 验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # 数据库异常处理器
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)


# ==================== 导出 ====================


__all__ = [
    "global_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "database_exception_handler",
    "register_exception_handlers",
    "ExceptionHandlerConfig",
    "config",
]
