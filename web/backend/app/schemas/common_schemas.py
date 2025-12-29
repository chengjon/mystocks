"""
统一API响应格式和公共模型

该模块定义了所有API端点必须使用的标准响应格式,确保前后端协作的一致性。

核心原则:
1. Schema First - Pydantic模型是单一数据源(SSOT)
2. 统一格式 - 所有API返回相同的响应结构
3. 类型安全 - 利用Pydantic的强类型校验
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

# 定义泛型类型变量
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    统一API响应格式

    所有API端点必须返回此格式,确保前端可以统一处理响应。

    Attributes:
        success: 请求是否成功 (True=成功, False=失败)
        code: 业务错误码 (0=成功, 4xx=客户端错误, 5xx=服务端错误)
        message: 提示信息 (成功时返回"操作成功",失败时返回错误原因)
        data: 实际数据载荷 (成功时包含业务数据,失败时为None)
        request_id: 请求唯一标识 (用于日志追踪和问题排查)
        timestamp: 响应时间戳 (服务器生成时间)

    Example:
        >>> response = APIResponse(
        ...     success=True,
        ...     code=0,
        ...     message="操作成功",
        ...     data={"user_id": 123, "name": "张三"}
        ... )
    """

    success: bool = Field(default=True, description="请求是否成功")
    code: int = Field(default=0, description="业务错误码 (0=成功, 4xx=客户端错误, 5xx=服务端错误)")
    message: str = Field(default="操作成功", description="提示信息")
    data: Optional[T] = Field(default=None, description="实际数据载荷")
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="请求唯一标识 (用于日志追踪)")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

    class Config:
        """Pydantic配置"""

        json_schema_extra = {
            "example": {
                "success": True,
                "code": 0,
                "message": "操作成功",
                "data": {"user_id": 123, "name": "张三"},
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-12-29T15:30:00.000Z",
            }
        }


class CommonError(BaseModel):
    """
    统一错误响应模型

    当API调用失败时,返回此格式的错误信息。

    Attributes:
        code: 错误码 (遵循HTTP状态码规范)
        message: 错误提示信息 (面向用户的中文描述)
        data: 额外错误数据 (可选,包含详细信息)
        detail: 技术细节 (可选,包含调试信息,仅开发环境返回)

    Example:
        >>> error = CommonError(
        ...     code=400,
        ...     message="参数错误",
        ...     detail="symbol字段不能为空"
        ... )
    """

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误提示信息")
    data: Optional[dict] = Field(default=None, description="额外错误数据")
    detail: Optional[str] = Field(default=None, description="技术细节 (仅开发环境)")

    class Config:
        """Pydantic配置"""

        json_schema_extra = {
            "example": {"code": 400, "message": "参数错误", "data": None, "detail": "symbol字段不能为空"}
        }


class PaginationParams(BaseModel):
    """
    分页参数模型

    用于列表查询API的统一分页参数。

    Attributes:
        page: 页码 (从1开始)
        page_size: 每页数量 (默认20,最大100)

    Example:
        >>> params = PaginationParams(page=1, page_size=20)
    """

    page: int = Field(default=1, ge=1, description="页码 (从1开始)")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量 (默认20,最大100)")

    class Config:
        """Pydantic配置"""

        json_schema_extra = {"example": {"page": 1, "page_size": 20}}


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应模型

    用于列表查询API的统一分页响应格式。

    Attributes:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        total_pages: 总页数

    Example:
        >>> response = PaginatedResponse(
        ...     items=[user1, user2],
        ...     total=100,
        ...     page=1,
        ...     page_size=20,
        ...     total_pages=5
        ... )
    """

    items: list[T] = Field(..., description="数据列表")
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, description="每页数量")
    total_pages: int = Field(..., ge=0, description="总页数")

    class Config:
        """Pydantic配置"""

        json_schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
            }
        }


# 便捷工厂函数
def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """
    创建成功响应的便捷函数

    Args:
        data: 实际数据载荷
        message: 提示信息

    Returns:
        符合APIResponse格式的字典

    Example:
        >>> resp = success_response({"user_id": 123}, "查询成功")
    """
    return {
        "success": True,
        "code": 0,
        "message": message,
        "data": data,
        "request_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
    }


def error_response(code: int, message: str, detail: str = None) -> dict:
    """
    创建错误响应的便捷函数

    Args:
        code: 错误码
        message: 错误提示信息
        detail: 技术细节 (可选)

    Returns:
        符合CommonError格式的字典

    Example:
        >>> resp = error_response(400, "参数错误", "symbol字段不能为空")
    """
    return {"success": False, "code": code, "message": message, "data": None, "detail": detail}
