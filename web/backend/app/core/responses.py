"""
统一API响应格式模块

提供标准化的API响应模型，确保所有端点返回一致的响应格式。

版本: 1.0.0
日期: 2025-12-01
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """统一API成功响应模型"""

    success: bool = Field(True, description="操作是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    message: Optional[str] = Field("操作成功", description="响应消息")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="响应时间戳"
    )
    request_id: Optional[str] = Field(None, description="请求ID，用于追踪")


class ErrorResponse(BaseModel):
    """统一API错误响应模型"""

    success: bool = Field(False, description="操作是否成功")
    error: Dict[str, Any] = Field(..., description="错误详情")
    message: str = Field(..., description="错误消息")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="响应时间戳"
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
        # 计算总记录数：优先使用提供的total，否则根据data类型处理
        if total is not None:
            calculated_total = total
        elif isinstance(data, list):
            calculated_total = len(data)
        elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            # 对于包装的列表数据（如 {"items": [...]}），使用items长度
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


def create_success_response(
    data: Optional[Dict[str, Any]] = None,
    message: str = "操作成功",
    request_id: Optional[str] = None,
) -> APIResponse:
    """创建成功响应"""
    return APIResponse(success=True, data=data, message=message, request_id=request_id)


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """创建错误响应"""
    error_info = {"code": error_code, "message": message}

    if details:
        error_info["details"] = details

    return ErrorResponse(error=error_info, message=message, request_id=request_id)


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
        "timestamp": datetime.utcnow().isoformat(),
    }

    if details:
        health_data.update(details)

    return create_success_response(
        data=health_data, message=f"服务{service}状态检查", request_id=request_id
    )


# 标准错误代码
class ErrorCodes:
    """标准错误代码常量"""

    # 通用错误
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"

    # 业务错误
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    OPERATION_FAILED = "OPERATION_FAILED"

    # 系统错误
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# 标准响应消息
class ResponseMessages:
    """标准响应消息常量"""

    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    NOT_FOUND = "资源未找到"
    INVALID_REQUEST = "请求参数无效"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "禁止访问"
    INTERNAL_ERROR = "内部服务器错误"
    SERVICE_UNAVAILABLE = "服务暂不可用"
