"""
FastAPI全局异常处理器 (增强版 - 统一响应格式)

本模块实现FastAPI应用的全局异常处理，提供统一的错误响应格式。
与ResponseFormatMiddleware配合，自动将所有异常转换为UnifiedResponse格式。

核心功能：
1. 捕获所有MyStocks自定义异常并转换为统一HTTP响应
2. 使用UnifiedResponse格式的结构化错误响应
3. 支持errors数组详细错误信息
4. 区分不同级别的异常（客户端错误 vs 服务器错误）
5. 记录详细的错误日志便于排查

版本: 2.0.0
日期: 2025-12-24
更新:
- 使用 UnifiedResponse 格式
- 支持 code 和 errors 字段
- 自动生成 request_id
"""

import logging
import uuid
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# 导入新的统一响应格式
from app.core.responses import (
    BusinessCode,
    ErrorCodes,
    ErrorDetail,
    ResponseMessages,
    UnifiedResponse,
)

# 导入自定义异常类
try:
    from src.core.exceptions import (
        AuthenticationError,
        AuthorizationError,
        BusinessLogicException,
        ConfigException,
        DatabaseException,
        DataException,
        DataSourceConfigError,
        DataSourceConnectionError,
        DataSourceDataFormatError,
        DataSourceDataNotFound,
        DataSourceException,
        DataSourceQueryError,
        DataSourceTimeout,
        DataSourceUnavailable,
        MyStocksException,
        NetworkException,
        ProcessingException,
    )
except ImportError:
    # 兼容性处理：如果导入失败，使用基础Exception
    MyStocksException = Exception
    DataSourceException = Exception

# 配置日志
logger = logging.getLogger(__name__)


# ==================== 统一异常响应格式化 ====================


def create_unified_exception_response(
    code: int,
    message: str,
    error_code: Optional[str] = None,
    errors: Optional[list[ErrorDetail]] = None,
    request_id: Optional[str] = None,
    path: Optional[str] = None,
    include_path_in_data: bool = False,
) -> JSONResponse:
    """
    创建统一格式的异常响应

    Args:
        code: 业务状态码 (400, 401, 404, 500 等)
        message: 错误消息
        error_code: 错误代码
        errors: 详细错误信息数组
        request_id: 请求ID
        path: 请求路径
        include_path_in_data: 是否将路径包含在data中

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    data = None
    if include_path_in_data and path:
        data = {"path": path}

    unified_response = UnifiedResponse(
        success=False,
        code=code,
        message=message,
        data=data,
        errors=errors,
        request_id=request_id,
    )

    return JSONResponse(
        content=unified_response.model_dump(exclude_unset=True),
        status_code=code,
    )


# ==================== MyStocks自定义异常处理器 ====================


async def mystocks_exception_handler(request: Request, exc: MyStocksException) -> JSONResponse:
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
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 根据异常类型确定业务状态码
    if isinstance(exc, AuthenticationError):
        business_code = BusinessCode.UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        business_code = BusinessCode.FORBIDDEN
    elif isinstance(exc, DataSourceDataNotFound):
        business_code = BusinessCode.NOT_FOUND
    elif isinstance(exc, DataSourceTimeout):
        business_code = status.HTTP_504_GATEWAY_TIMEOUT
    elif isinstance(exc, DataSourceUnavailable):
        business_code = BusinessCode.SERVICE_UNAVAILABLE
    elif isinstance(exc, (DataSourceConnectionError, NetworkException)):
        business_code = BusinessCode.EXTERNAL_SERVICE_ERROR
    elif isinstance(exc, (DataSourceConfigError, DatabaseException, ConfigException)):
        business_code = BusinessCode.INTERNAL_ERROR
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
        business_code = BusinessCode.BAD_REQUEST
    elif isinstance(exc, DataSourceException):
        business_code = BusinessCode.INTERNAL_ERROR
    else:
        business_code = BusinessCode.INTERNAL_ERROR

    # 记录错误日志
    log_level = logging.ERROR if business_code >= 500 else logging.WARNING
    logger.log(
        log_level,
        f"MyStocks Exception: [{exc.error_code}] {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
            "request_id": request_id,
            "status_code": business_code,
        },
        exc_info=(business_code >= 500),
    )

    # 构建错误详情
    errors = None
    if hasattr(exc, "details") and exc.details:
        # 将details转换为ErrorDetail格式
        if isinstance(exc.details, dict):
            errors = [
                ErrorDetail(
                    code=exc.error_code,
                    message=str(exc.details.get("error", exc.message)),
                )
            ]

    # 返回统一格式响应
    return create_unified_exception_response(
        code=business_code,
        message=exc.message,
        error_code=exc.error_code,
        errors=errors,
        request_id=request_id,
        path=request.url.path,
        include_path_in_data=True,
    )


# ==================== FastAPI内置异常处理器 ====================


async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求参数验证错误

    当请求参数不符合Pydantic模型定义时触发。
    自动将Pydantic验证错误转换为ErrorDetail数组。
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 解析验证错误为ErrorDetail数组
    errors = []
    for error in exc.errors():
        # 获取字段位置
        loc = error.get("loc", [])
        field = None
        if loc:
            # 跳过 'body', 'query' 等前缀，获取实际字段名
            for item in loc[1:] if len(loc) > 1 else loc:
                if isinstance(item, str):
                    field = item
                    break

        # 获取错误类型和消息
        error_type = error.get("type", "validation_error")
        error_msg = error.get("msg", "验证失败")

        # 映射错误代码
        error_code = _map_validation_error_code(error_type)

        errors.append(
            ErrorDetail(
                field=field,
                code=error_code,
                message=error_msg,
            )
        )

    # 记录警告日志
    logger.warning(
        f"Request validation error: {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
            "request_id": request_id,
        },
    )

    # 构建错误消息
    field_names = [e.field for e in errors if e.field]
    if field_names:
        message = f"参数验证失败: {', '.join(set(field_names))}"
    else:
        message = ResponseMessages.VALIDATION_ERROR

    return create_unified_exception_response(
        code=BusinessCode.VALIDATION_ERROR,
        message=message,
        errors=errors,
        request_id=request_id,
    )


def _map_validation_error_code(error_type: str) -> str:
    """映射Pydantic错误类型到业务错误码"""
    error_map = {
        "missing": ErrorCodes.MISSING_REQUIRED_FIELD,
        "value_error.missing": ErrorCodes.MISSING_REQUIRED_FIELD,
        "value_error.str.format": ErrorCodes.INVALID_FORMAT,
        "value_error.number.not_gt": ErrorCodes.OUT_OF_RANGE,
        "value_error.number.not_ge": ErrorCodes.OUT_OF_RANGE,
        "value_error.number.not_lt": ErrorCodes.OUT_OF_RANGE,
        "value_error.number.not_le": ErrorCodes.OUT_OF_RANGE,
        "value_error.email": ErrorCodes.INVALID_FORMAT,
        "value_error.url": ErrorCodes.INVALID_FORMAT,
        "value_error.date": ErrorCodes.INVALID_FORMAT,
        "value_error.datetime": ErrorCodes.INVALID_FORMAT,
        "value_error.bool": ErrorCodes.INVALID_VALUE,
        "value_error.number": ErrorCodes.INVALID_VALUE,
        "value_error.str": ErrorCodes.INVALID_VALUE,
        "value_error.any_str.min_length": ErrorCodes.INVALID_VALUE,
        "value_error.any_str.max_length": ErrorCodes.INVALID_VALUE,
        "value_error.list.min_items": ErrorCodes.INVALID_VALUE,
        "value_error.list.max_items": ErrorCodes.INVALID_VALUE,
    }

    return error_map.get(error_type, ErrorCodes.VALIDATION_ERROR)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    处理HTTP异常

    捕获FastAPI/Starlette的HTTPException。
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 记录警告日志
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {request.url.path}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
        },
    )

    # 获取错误消息
    message = str(exc.detail) if exc.detail else _get_default_message_for_status(exc.status_code)

    # 构建错误详情
    error_code = _get_error_code_for_status(exc.status_code)
    errors = [ErrorDetail(code=error_code, message=message)]

    return create_unified_exception_response(
        code=exc.status_code,
        message=message,
        error_code=error_code,
        errors=errors,
        request_id=request_id,
        path=request.url.path,
        include_path_in_data=True,
    )


def _get_error_code_for_status(status_code: int) -> str:
    """根据HTTP状态码获取错误代码"""
    error_map = {
        400: ErrorCodes.BAD_REQUEST,
        401: ErrorCodes.UNAUTHORIZED,
        403: ErrorCodes.FORBIDDEN,
        404: ErrorCodes.NOT_FOUND,
        405: ErrorCodes.METHOD_NOT_ALLOWED,
        409: ErrorCodes.DUPLICATE_RESOURCE,
        422: ErrorCodes.VALIDATION_ERROR,
        429: ErrorCodes.RATE_LIMIT_EXCEEDED,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
        502: ErrorCodes.EXTERNAL_SERVICE_ERROR,
        503: ErrorCodes.SERVICE_UNAVAILABLE,
        504: ErrorCodes.EXTERNAL_SERVICE_ERROR,
    }

    return error_map.get(status_code, "UNKNOWN_ERROR")


def _get_default_message_for_status(status_code: int) -> str:
    """根据HTTP状态码获取默认错误消息"""
    message_map = {
        400: ResponseMessages.INVALID_REQUEST,
        401: ResponseMessages.UNAUTHORIZED,
        403: ResponseMessages.FORBIDDEN,
        404: ResponseMessages.NOT_FOUND,
        405: "方法不允许",
        409: ResponseMessages.DUPLICATE_RESOURCE,
        422: ResponseMessages.VALIDATION_ERROR,
        429: ResponseMessages.RATE_LIMIT_EXCEEDED,
        500: ResponseMessages.INTERNAL_ERROR,
        502: "外部服务错误",
        503: ResponseMessages.SERVICE_UNAVAILABLE,
        504: "网关超时",
    }

    return message_map.get(status_code, "请求处理失败")


# ==================== 通用异常处理器 ====================


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理所有未被捕获的异常

    作为兜底机制，防止异常泄露给客户端。
    记录完整堆栈信息便于排查问题。
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 记录错误日志
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "request_id": request_id,
        },
        exc_info=True,  # 记录完整堆栈
    )

    # 构建错误详情
    errors = [
        ErrorDetail(
            code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message=str(exc),
        )
    ]

    return create_unified_exception_response(
        code=BusinessCode.INTERNAL_ERROR,
        message="服务器内部错误，请稍后重试",
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        errors=errors,
        request_id=request_id,
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
        from app.core.global_exception_handlers import register_global_exception_handlers

        app = FastAPI()
        register_global_exception_handlers(app)
    """
    # MyStocks自定义异常
    try:
        app.add_exception_handler(MyStocksException, mystocks_exception_handler)
        logger.info("MyStocks exception handlers registered (UnifiedResponse format)")
    except Exception as e:
        logger.warning("Failed to register MyStocks exception handler: %(e)s")

    # FastAPI内置异常
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # 通用异常兜底
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("All global exception handlers registered successfully (UnifiedResponse format)")
