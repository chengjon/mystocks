"""
统一异常处理框架 - MyStocks 业务异常和全局异常处理器
"""

from fastapi import HTTPException, status

# 使用新的状态码常量（避免弃用警告）
HTTP_422_UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY
from logging import getLogger
from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse

logger = getLogger(__name__)


# 自定义业务异常类
class BusinessException(HTTPException):
    """
    业务逻辑异常类 - 用于业务层面的错误

    特点：
    - 自动记录错误日志
    - 统一的错误响应格式
    - 包含错误详情和状态码
    """

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or f"HTTP_{status_code}"

        # 统一记录异常日志
        logger.error("业务异常：%(detail)s（状态码：%(status_code)s, 错误码：{self.error_code}）")


# 数据验证异常
class ValidationException(BusinessException):
    """数据验证失败异常"""

    def __init__(self, detail: str, field: Optional[str] = None):
        error_detail = f"验证失败：{detail}"
        if field:
            error_detail = f"字段 '{field}' {detail}"

        super().__init__(
            detail=error_detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, error_code="VALIDATION_ERROR"
        )


# 资源未找到异常
class NotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, resource: str, identifier: Any):
        error_detail = f"{resource} '{identifier}' 不存在"
        super().__init__(detail=error_detail, status_code=status.HTTP_404_NOT_FOUND, error_code="RESOURCE_NOT_FOUND")


# 权限不足异常
class ForbiddenException(BusinessException):
    """权限不足异常"""

    def __init__(self, detail: str = "权限不足"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN, error_code="FORBIDDEN")


# 认证失败异常
class UnauthorizedException(BusinessException):
    """认证失败异常"""

    def __init__(self, detail: str = "认证失败"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED, error_code="UNAUTHORIZED")


# 配置错误异常
class ConfigurationException(Exception):
    """配置相关异常 - 非HTTP异常，用于启动时配置验证"""

    def __init__(self, detail: str):
        super().__init__(detail)
        logger.error("配置异常：%(detail)s")


# 全局通用异常处理（挂载到FastAPI app）
def register_exception_handlers(app):
    """
    注册全局异常处理器到FastAPI应用

    Args:
        app: FastAPI应用实例
    """

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request, exc: BusinessException):
        """处理业务异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.error_code,
                "message": exc.detail,
                "data": None,
                "path": str(request.url.path),
                "timestamp": None,  # 可在中间件中添加时间戳
            },
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request, exc: ValidationException):
        """处理验证异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.error_code,
                "message": exc.detail,
                "data": None,
                "path": str(request.url.path),
                "timestamp": None,
            },
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request, exc: NotFoundException):
        """处理资源未找到异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.error_code,
                "message": exc.detail,
                "data": None,
                "path": str(request.url.path),
                "timestamp": None,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """处理标准的HTTP异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "data": None,
                "path": str(request.url.path),
                "timestamp": None,
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """处理未捕获的异常"""
        logger.error("未处理的异常：{exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
                "data": None,
                "path": str(request.url.path),
                "timestamp": None,
            },
        )

    logger.info("✅ 全局异常处理器已注册")


# 便捷的异常抛出函数
def raise_business_error(detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
    """便捷函数：抛出业务异常"""
    raise BusinessException(detail=detail, status_code=status_code)


def raise_validation_error(detail: str, field: Optional[str] = None):
    """便捷函数：抛出验证异常"""
    raise ValidationException(detail=detail, field=field)


def raise_not_found(resource: str, identifier: Any):
    """便捷函数：抛出资源未找到异常"""
    raise NotFoundException(resource=resource, identifier=identifier)


def raise_forbidden(detail: str = "权限不足"):
    """便捷函数：抛出权限不足异常"""
    raise ForbiddenException(detail=detail)


def raise_unauthorized(detail: str = "认证失败"):
    """便捷函数：抛出认证失败异常"""
    raise UnauthorizedException(detail=detail)
