"""
统一API响应格式模块 (增强版)

提供标准化的API响应模型，确保所有端点返回一致的响应格式。

版本: 2.0.0
日期: 2025-12-24
更新:
- 添加 business_code 字段 (业务状态码)
- 添加 errors 字段 (详细错误信息数组)
- 保持向后兼容性
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# ==================== 错误详情模型 ====================


class ErrorDetail(BaseModel):
    """单个错误详情"""

    field: Optional[str] = Field(None, description="错误发生的字段名")
    code: str = Field(..., description="具体的错误代码")
    message: str = Field(..., description="具体的错误描述")


# ==================== 统一响应模型 (增强版) ====================


class UnifiedResponse(BaseModel):
    """
    统一API响应模型 (增强版)

    这是所有API响应应该遵循的标准格式。
    """

    success: bool = Field(True, description="操作是否成功")
    code: int = Field(200, description="业务状态码 (200=成功, 400=参数错误, 401=未认证, 404=未找到, 500=服务器错误)")
    message: str = Field("操作成功", description="给前端展示的消息")
    data: Optional[Any] = Field(None, description="实际的业务数据，成功时返回，失败时为null")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="响应生成的时间戳 (UTC)"
    )
    request_id: Optional[str] = Field(None, description="请求ID，用于追踪请求日志")
    errors: Optional[List[ErrorDetail]] = Field(None, description="详细错误信息数组，仅在请求失败时存在")


class APIResponse(BaseModel):
    """
    向后兼容的成功响应模型

    @deprecated 推荐使用 UnifiedResponse，保留此类以维持向后兼容性
    """

    success: bool = Field(True, description="操作是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    message: Optional[str] = Field("操作成功", description="响应消息")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="响应时间戳"
    )
    request_id: Optional[str] = Field(None, description="请求ID，用于追踪")


class ErrorResponse(BaseModel):
    """
    向后兼容的错误响应模型

    @deprecated 推荐使用 UnifiedResponse，保留此类以维持向后兼容性
    """

    success: bool = Field(False, description="操作是否成功")
    error: Dict[str, Any] = Field(..., description="错误详情")
    message: str = Field(..., description="错误消息")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="响应时间戳"
    )
    request_id: Optional[str] = Field(None, description="请求ID，用于追踪")


class PaginatedResponse(APIResponse):
    """分页响应模型"""

    pagination: Dict[str, Any] = Field(..., description="分页信息")

    @classmethod
    def create(
        cls,
        data: Any,
        page: int = 1,
        size: int = 20,
        total: Optional[int] = None,
        message: str = "操作成功",
        request_id: Optional[str] = None,
    ):
        """创建分页响应"""
        # 计算总记录数
        if total is not None:
            calculated_total = total
        elif isinstance(data, list):
            calculated_total = len(data)
        elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            calculated_total = len(data["items"])
        else:
            calculated_total = 0

        # 计算总页数
        if calculated_total > 0:
            calculated_pages = (calculated_total + size - 1) // size
        else:
            calculated_pages = 0

        return cls(
            success=True,
            data=data,
            message=message,
            request_id=request_id,
            pagination={
                "page": page,
                "size": size,
                "total": calculated_total,
                "pages": calculated_pages,
            },
        )


class UnifiedPaginatedResponse(UnifiedResponse):
    """统一分页响应模型 (增强版)"""

    pagination: Dict[str, Any] = Field(..., description="分页信息")

    @classmethod
    def create(
        cls,
        data: Any,
        page: int = 1,
        size: int = 20,
        total: Optional[int] = None,
        message: str = "操作成功",
        code: int = 200,
        request_id: Optional[str] = None,
    ):
        """创建统一分页响应"""
        # 计算总记录数
        if total is not None:
            calculated_total = total
        elif isinstance(data, list):
            calculated_total = len(data)
        elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            calculated_total = len(data["items"])
        else:
            calculated_total = 0

        # 计算总页数
        if calculated_total > 0:
            calculated_pages = (calculated_total + size - 1) // size
        else:
            calculated_pages = 0

        return cls(
            success=True,
            code=code,
            data=data,
            message=message,
            request_id=request_id,
            pagination={
                "page": page,
                "size": size,
                "total": calculated_total,
                "pages": calculated_pages,
            },
        )


# ==================== 响应创建函数 ====================


def create_success_response(
    data: Optional[Any] = None,
    message: str = "操作成功",
    request_id: Optional[str] = None,
) -> APIResponse:
    """
    创建成功响应 (向后兼容)

    推荐使用 unified_response() 替代
    """
    return APIResponse(success=True, data=data, message=message, request_id=request_id)


def create_unified_success_response(
    data: Optional[Any] = None,
    message: str = "操作成功",
    code: int = 200,
    request_id: Optional[str] = None,
) -> UnifiedResponse:
    """创建统一成功响应"""
    return UnifiedResponse(
        success=True,
        code=code,
        message=message,
        data=data,
        request_id=request_id,
    )


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """
    创建错误响应 (向后兼容)

    推荐使用 unified_error_response() 替代
    """
    error_info = {"code": error_code, "message": message}

    if details:
        error_info["details"] = details

    return ErrorResponse(error=error_info, message=message, request_id=request_id)


def create_unified_error_response(
    code: int,
    message: str,
    error_code: Optional[str] = None,
    errors: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None,
) -> UnifiedResponse:
    """
    创建统一错误响应

    Args:
        code: 业务状态码 (400, 401, 404, 500 等)
        message: 错误消息
        error_code: 错误代码 (如 VALIDATION_ERROR)
        errors: 详细错误信息数组
        request_id: 请求ID
    """
    # 如果没有提供 error_code，根据 code 生成默认值
    if error_code is None:
        error_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "DUPLICATE_RESOURCE",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "EXTERNAL_SERVICE_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        error_code = error_code_map.get(code, "UNKNOWN_ERROR")

    return UnifiedResponse(
        success=False,
        code=code,
        message=message,
        data=None,
        errors=errors,
        request_id=request_id,
    )


def create_health_response(
    service: str,
    status: str = "healthy",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> APIResponse:
    """创建健康检查响应"""
    health_data = {
        "status": status,
        "service": service,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if details:
        health_data.update(details)

    return create_success_response(
        data=health_data, message=f"服务{service}状态检查", request_id=request_id
    )


def create_validation_error_response(
    errors: List[ErrorDetail],
    request_id: Optional[str] = None,
) -> UnifiedResponse:
    """创建参数验证错误响应"""
    return UnifiedResponse(
        success=False,
        code=422,
        message="参数验证失败",
        data=None,
        errors=errors,
        request_id=request_id,
    )


# ==================== 标准错误代码 ====================


class ErrorCodes:
    """标准错误代码常量 (业务错误码)"""

    # 通用错误 (4xx)
    BAD_REQUEST = "BAD_REQUEST"  # 400
    UNAUTHORIZED = "UNAUTHORIZED"  # 401
    FORBIDDEN = "FORBIDDEN"  # 403
    NOT_FOUND = "NOT_FOUND"  # 404
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"  # 405
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"  # 409
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 422
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"  # 429

    # 服务器错误 (5xx)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"  # 500
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"  # 502
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # 503

    # 业务错误
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    OPERATION_FAILED = "OPERATION_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"

    # 验证错误细分
    INVALID_FORMAT = "INVALID_FORMAT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_VALUE = "INVALID_VALUE"
    OUT_OF_RANGE = "OUT_OF_RANGE"


# ==================== 业务状态码 ====================


class BusinessCode:
    """业务状态码常量"""

    # 成功
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # 客户端错误
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    VALIDATION_ERROR = 422
    RATE_LIMIT_EXCEEDED = 429

    # 服务器错误
    INTERNAL_ERROR = 500
    EXTERNAL_SERVICE_ERROR = 502
    SERVICE_UNAVAILABLE = 503


# ==================== 标准响应消息 ====================


class ResponseMessages:
    """标准响应消息常量"""

    # 成功消息
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    ACCEPTED = "请求已接受"

    # 错误消息
    NOT_FOUND = "资源未找到"
    INVALID_REQUEST = "请求参数无效"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "禁止访问"
    INTERNAL_ERROR = "内部服务器错误"
    SERVICE_UNAVAILABLE = "服务暂不可用"
    VALIDATION_ERROR = "参数验证失败"
    RATE_LIMIT_EXCEEDED = "请求过于频繁，请稍后再试"
    DUPLICATE_RESOURCE = "资源已存在"


# ==================== 便捷函数 ====================


def ok(data: Any = None, message: str = ResponseMessages.SUCCESS) -> UnifiedResponse:
    """快捷创建成功响应 (code=200)"""
    return UnifiedResponse(success=True, code=200, message=message, data=data)


def created(data: Any = None, message: str = ResponseMessages.CREATED) -> UnifiedResponse:
    """快捷创建创建成功响应 (code=201)"""
    return UnifiedResponse(success=True, code=201, message=message, data=data)


def bad_request(
    message: str = ResponseMessages.INVALID_REQUEST,
    errors: Optional[List[ErrorDetail]] = None,
) -> UnifiedResponse:
    """快捷创建请求错误响应 (code=400)"""
    return UnifiedResponse(
        success=False, code=400, message=message, errors=errors
    )


def unauthorized(message: str = ResponseMessages.UNAUTHORIZED) -> UnifiedResponse:
    """快捷创建未授权响应 (code=401)"""
    return UnifiedResponse(success=False, code=401, message=message)


def forbidden(message: str = ResponseMessages.FORBIDDEN) -> UnifiedResponse:
    """快捷创建禁止访问响应 (code=403)"""
    return UnifiedResponse(success=False, code=403, message=message)


def not_found(
    message: str = ResponseMessages.NOT_FOUND,
    resource: Optional[str] = None,
) -> UnifiedResponse:
    """快捷创建资源未找到响应 (code=404)"""
    if resource:
        message = f"{resource}未找到"
    return UnifiedResponse(success=False, code=404, message=message)


def validation_error(
    errors: List[ErrorDetail],
    message: str = ResponseMessages.VALIDATION_ERROR,
) -> UnifiedResponse:
    """快捷创建验证错误响应 (code=422)"""
    return UnifiedResponse(
        success=False, code=422, message=message, errors=errors
    )


def server_error(
    message: str = ResponseMessages.INTERNAL_ERROR,
) -> UnifiedResponse:
    """快捷创建服务器错误响应 (code=500)"""
    return UnifiedResponse(success=False, code=500, message=message)
