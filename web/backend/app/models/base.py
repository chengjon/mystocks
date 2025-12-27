"""
统一API响应模型 (Pydantic)

提供标准化的API响应格式，确保前后端接口一致性

模型说明:
- BaseResponse: 通用响应包装器，支持泛型数据
- PagedResponse: 分页列表响应，包含分页元数据
- ErrorResponse: 错误响应，包含错误码和详情
- HealthCheckResponse: 健康检查响应

使用示例:
    # 成功响应
    return BaseResponse(
        success=True,
        message="查询成功",
        data={"items": [...]}
    )

    # 分页响应
    return PagedResponse(
        success=True,
        data=items,
        total=100,
        page=1,
        page_size=20
    )

    # 错误响应
    return ErrorResponse(
        success=False,
        message="参数错误",
        error_code="INVALID_PARAMETER",
        details={"field": "symbol", "reason": "格式不正确"}
    )
"""

from typing import Generic, TypeVar, Optional, Any, List, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# 泛型类型变量，用于BaseResponse和PagedResponse
T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    通用API响应模型（泛型）

    所有API响应的基础模型，支持任意类型的data字段

    Attributes:
        success: 请求是否成功
        message: 响应消息（成功提示或错误描述）
        data: 响应数据（泛型，可以是任意类型）
        timestamp: 响应时间戳
        request_id: 请求追踪ID（可选）

    Examples:
        # 简单数据响应
        BaseResponse[dict](
            success=True,
            message="查询成功",
            data={"symbol": "600000", "name": "浦发银行"}
        )

        # 列表数据响应
        BaseResponse[List[dict]](
            success=True,
            message="查询成功",
            data=[{"symbol": "600000"}, {"symbol": "600519"}]
        )

        # 无数据响应
        BaseResponse[None](
            success=True,
            message="操作成功"
        )
    """

    success: bool = Field(..., description="请求是否成功")
    message: str = Field("", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求追踪ID")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "查询成功",
                "data": {"symbol": "600000", "name": "浦发银行"},
                "timestamp": "2025-10-25T10:30:00Z",
                "request_id": "req_123456",
            }
        }


class PagedResponse(BaseModel, Generic[T]):
    """
    分页响应模型（泛型）

    用于返回分页列表数据，包含完整的分页元数据

    Attributes:
        success: 请求是否成功
        message: 响应消息
        data: 当前页数据列表（泛型）
        total: 总记录数
        page: 当前页码（从1开始）
        page_size: 每页记录数
        total_pages: 总页数
        has_next: 是否有下一页
        has_prev: 是否有上一页
        timestamp: 响应时间戳

    Examples:
        PagedResponse[dict](
            success=True,
            message="查询成功",
            data=[
                {"symbol": "600000", "name": "浦发银行"},
                {"symbol": "600519", "name": "贵州茅台"}
            ],
            total=100,
            page=1,
            page_size=20
        )
    """

    success: bool = Field(True, description="请求是否成功")
    message: str = Field("", description="响应消息")
    data: List[T] = Field(default_factory=list, description="当前页数据列表")
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码（从1开始）", ge=1)
    page_size: int = Field(20, description="每页记录数", ge=1, le=100)
    total_pages: int = Field(0, description="总页数")
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")

    def __init__(self, **data):
        """初始化时自动计算分页元数据"""
        super().__init__(**data)

        # 自动计算总页数
        if self.total > 0 and self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 0

        # 自动计算是否有上一页/下一页
        self.has_prev = self.page > 1
        self.has_next = self.page < self.total_pages

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "查询成功",
                "data": [
                    {"symbol": "600000", "name": "浦发银行"},
                    {"symbol": "600519", "name": "贵州茅台"},
                ],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False,
                "timestamp": "2025-10-25T10:30:00Z",
            }
        }


class ErrorResponse(BaseModel):
    """
    错误响应模型

    用于返回详细的错误信息，包含错误码和调试信息

    Attributes:
        success: 固定为False
        message: 错误消息（用户友好）
        error_code: 错误代码（用于前端错误处理）
        details: 错误详细信息（可选，调试用）
        timestamp: 错误发生时间戳
        path: 请求路径（可选）
        request_id: 请求追踪ID（可选）

    Common Error Codes:
        INVALID_PARAMETER: 无效参数
        RESOURCE_NOT_FOUND: 资源不存在
        UNAUTHORIZED: 未授权
        FORBIDDEN: 禁止访问
        INTERNAL_ERROR: 内部错误
        DATABASE_ERROR: 数据库错误
        EXTERNAL_API_ERROR: 外部API错误
        VALIDATION_ERROR: 数据验证错误

    Examples:
        # 参数错误
        ErrorResponse(
            message="股票代码格式不正确",
            error_code="INVALID_PARAMETER",
            details={"field": "symbol", "value": "abc", "expected": "6位数字"}
        )

        # 资源不存在
        ErrorResponse(
            message="股票不存在",
            error_code="RESOURCE_NOT_FOUND",
            details={"symbol": "999999"}
        )

        # 内部错误
        ErrorResponse(
            message="数据查询失败",
            error_code="DATABASE_ERROR",
            details={"error": "Connection timeout"}
        )
    """

    success: Literal[False] = Field(False, description="固定为False")
    message: str = Field(..., description="错误消息（用户友好）")
    error_code: str = Field(..., description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详细信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="错误发生时间")
    path: Optional[str] = Field(None, description="请求路径")
    request_id: Optional[str] = Field(None, description="请求追踪ID")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "股票代码格式不正确",
                "error_code": "INVALID_PARAMETER",
                "details": {"field": "symbol", "value": "abc", "expected": "6位数字"},
                "timestamp": "2025-10-25T10:30:00Z",
                "path": "/api/stock/quote",
                "request_id": "req_123456",
            }
        }


class HealthCheckResponse(BaseModel):
    """
    健康检查响应模型

    用于系统健康检查接口，返回系统运行状态

    Attributes:
        status: 健康状态（healthy, degraded, unhealthy）
        version: 系统版本
        uptime: 运行时长（秒）
        timestamp: 检查时间戳
        services: 各服务状态详情（可选）

    Examples:
        HealthCheckResponse(
            status="healthy",
            version="2.0.0",
            uptime=86400.5,
            services={
                "database": {"status": "healthy", "latency_ms": 5},
                "redis": {"status": "healthy", "latency_ms": 1},
                "tdengine": {"status": "healthy", "latency_ms": 8}
            }
        )
    """

    status: str = Field(..., description="健康状态: healthy, degraded, unhealthy")
    version: str = Field(..., description="系统版本")
    uptime: float = Field(..., description="运行时长（秒）")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="检查时间戳")
    services: Optional[Dict[str, Any]] = Field(None, description="各服务状态详情")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "uptime": 86400.5,
                "timestamp": "2025-10-25T10:30:00Z",
                "services": {
                    "postgresql": {"status": "healthy", "latency_ms": 5},
                    "tdengine": {"status": "healthy", "latency_ms": 8},
                    "monitoring": {"status": "healthy", "latency_ms": 3},
                },
            }
        }


# ============================================================================
# 辅助函数
# ============================================================================


def success_response(data: Any = None, message: str = "操作成功", request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    快速创建成功响应

    Args:
        data: 响应数据
        message: 成功消息
        request_id: 请求追踪ID

    Returns:
        Dict格式的响应（FastAPI会自动转换为JSON）

    Examples:
        return success_response(
            data={"symbol": "600000", "name": "浦发银行"},
            message="查询成功"
        )
    """
    return BaseResponse(success=True, message=message, data=data, request_id=request_id).model_dump()


def error_response(
    message: str,
    error_code: str = "INTERNAL_ERROR",
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    快速创建错误响应

    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详情
        path: 请求路径
        request_id: 请求追踪ID

    Returns:
        Dict格式的响应（FastAPI会自动转换为JSON）

    Examples:
        return error_response(
            message="股票代码格式不正确",
            error_code="INVALID_PARAMETER",
            details={"field": "symbol", "value": "abc"}
        )
    """
    return ErrorResponse(
        message=message,
        error_code=error_code,
        details=details,
        path=path,
        request_id=request_id,
    ).model_dump()


def paged_response(
    data: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "查询成功",
) -> Dict[str, Any]:
    """
    快速创建分页响应

    Args:
        data: 当前页数据列表
        total: 总记录数
        page: 当前页码（从1开始）
        page_size: 每页记录数
        message: 响应消息

    Returns:
        Dict格式的响应（FastAPI会自动转换为JSON）

    Examples:
        return paged_response(
            data=stock_list,
            total=100,
            page=1,
            page_size=20,
            message="股票列表查询成功"
        )
    """
    return PagedResponse(
        success=True,
        message=message,
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    ).model_dump()


# ============================================================================
# 错误码常量
# ============================================================================


class ErrorCode:
    """错误码常量类"""

    # 通用错误 (1xxx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # 资源错误 (2xxx)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"

    # 认证/授权错误 (3xxx)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"

    # 数据库错误 (4xxx)
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    QUERY_TIMEOUT = "QUERY_TIMEOUT"

    # 外部服务错误 (5xxx)
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

    # 业务逻辑错误 (6xxx)
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    DUPLICATE_OPERATION = "DUPLICATE_OPERATION"
