"""
MyStocks Core Exceptions

核心异常类定义，提供统一的错误处理机制。
所有业务异常都应该继承自这些基础异常类。
"""

from typing import Any, Dict, Optional


class MyStocksException(Exception):
    """
    MyStocks 基础异常类

    所有自定义异常的基类，提供统一的错误信息格式。
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        self.status_code = status_code


class DataException(MyStocksException):
    """数据相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DATA_ERROR", status_code=400, **kwargs)


class DatabaseException(MyStocksException):
    """数据库相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", status_code=500, **kwargs)


# Additional database exceptions
class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DATABASE_CONNECTION_ERROR", status_code=503, **kwargs)


# 数据库特定异常
class DatabaseNotFoundError(DatabaseException):
    """数据库不存在异常"""

    def __init__(self, database_name: str, **kwargs):
        message = f"Database '{database_name}' not found"
        super().__init__(message, error_code="DATABASE_NOT_FOUND", status_code=404, **kwargs)


class DatabaseOperationError(DatabaseException):
    """数据库操作异常"""

    def __init__(self, operation: str, details: str = "", **kwargs):
        message = f"Database operation '{operation}' failed"
        if details:
            message += f": {details}"
        super().__init__(message, error_code="DATABASE_OPERATION_ERROR", status_code=500, **kwargs)


# 数据操作异常
class DataFetchError(DataException):
    """数据获取异常"""

    def __init__(self, source: str, details: str = "", **kwargs):
        message = f"Failed to fetch data from '{source}'"
        if details:
            message += f": {details}"
        super().__init__(message, error_code="DATA_FETCH_ERROR", status_code=503, **kwargs)


class DataValidationError(DataException):
    """数据验证异常"""

    def __init__(self, field: str, value: Any, expected: str, **kwargs):
        message = f"Data validation failed for field '{field}': got {value}, expected {expected}"
        super().__init__(message, error_code="DATA_VALIDATION_ERROR", status_code=400, **kwargs)


class DataNotFoundError(DataException):
    """数据不存在异常"""

    def __init__(self, resource: str, identifier: Any, **kwargs):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, error_code="DATA_NOT_FOUND", status_code=404, **kwargs)


class NetworkException(MyStocksException):
    """网络相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", status_code=503, **kwargs)


class NetworkError(NetworkException):
    """网络错误异常 (别名，兼容旧代码)"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", status_code=503, **kwargs)


class ServiceError(MyStocksException):
    """服务相关异常"""

    def __init__(self, service: str, message: str, **kwargs):
        full_message = f"Service '{service}': {message}"
        super().__init__(full_message, error_code="SERVICE_ERROR", status_code=503, **kwargs)


class ProcessingException(MyStocksException):
    """数据处理相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="PROCESSING_ERROR", status_code=500, **kwargs)


class BusinessLogicException(MyStocksException):
    """业务逻辑异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", status_code=400, **kwargs)


class DataSourceException(MyStocksException):
    """数据源相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DATA_SOURCE_ERROR", status_code=503, **kwargs)


# 网络异常
class ConnectionError(NetworkException):
    """连接异常"""

    def __init__(self, host: str, port: Optional[int] = None, **kwargs):
        message = f"Connection failed to {host}"
        if port:
            message += f":{port}"
        super().__init__(message, error_code="CONNECTION_ERROR", status_code=503, **kwargs)


class TimeoutError(NetworkException):
    """超时异常"""

    def __init__(self, operation: str, timeout: float, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout}s"
        super().__init__(message, error_code="TIMEOUT_ERROR", status_code=504, **kwargs)


class AuthenticationError(NetworkException):
    """认证异常"""

    def __init__(self, service: str, **kwargs):
        message = f"Authentication failed for service '{service}'"
        super().__init__(message, error_code="AUTHENTICATION_ERROR", status_code=401, **kwargs)


# 数据源特定异常
class DataSourceConnectionError(DataSourceException):
    """数据源连接异常"""

    def __init__(self, source_name: str, **kwargs):
        message = f"Failed to connect to data source '{source_name}'"
        super().__init__(
            message,
            error_code="DATA_SOURCE_CONNECTION_ERROR",
            status_code=503,
            **kwargs,
        )


class DataSourceConfigError(DataSourceException):
    """数据源配置异常"""

    def __init__(self, source_name: str, config_issue: str, **kwargs):
        message = f"Data source '{source_name}' configuration error: {config_issue}"
        super().__init__(message, error_code="DATA_SOURCE_CONFIG_ERROR", status_code=500, **kwargs)


# 业务逻辑异常
class InvalidParameterError(BusinessLogicException):
    """无效参数异常"""

    def __init__(self, parameter: str, value: Any, reason: str, **kwargs):
        message = f"Invalid parameter '{parameter}' with value '{value}': {reason}"
        super().__init__(message, error_code="INVALID_PARAMETER", status_code=400, **kwargs)


class InsufficientPermissionsError(BusinessLogicException):
    """权限不足异常"""

    def __init__(self, operation: str, required_role: str, **kwargs):
        message = f"Insufficient permissions for operation '{operation}'. Required role: {required_role}"
        super().__init__(message, error_code="INSUFFICIENT_PERMISSIONS", status_code=403, **kwargs)


class ResourceLimitExceededError(BusinessLogicException):
    """资源限制异常"""

    def __init__(self, resource: str, limit: Any, current: Any, **kwargs):
        message = f"Resource limit exceeded for '{resource}': limit={limit}, current={current}"
        super().__init__(message, error_code="RESOURCE_LIMIT_EXCEEDED", status_code=429, **kwargs)


# 导出所有异常类
__all__ = [
    # 基础异常
    "MyStocksException",
    "DataException",
    "DatabaseException",
    "ConfigException",
    "NetworkException",
    "NetworkError",
    "ServiceError",
    "ProcessingException",
    "BusinessLogicException",
    "DataSourceException",
    # 数据库异常
    "DatabaseConnectionError",
    "DatabaseNotFoundError",
    "DatabaseOperationError",
    # 数据异常
    "DataFetchError",
    "DataValidationError",
    "DataNotFoundError",
    # 网络异常
    "ConnectionError",
    "TimeoutError",
    "AuthenticationError",
    # 数据源异常
    "DataSourceConnectionError",
    "DataSourceConfigError",
    # 业务逻辑异常
    "InvalidParameterError",
    "InsufficientPermissionsError",
    "ResourceLimitExceededError",
]
