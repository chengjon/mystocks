"""
统一异常定义模块
定义MyStocks系统中所有自定义异常类型
"""

from typing import Any, Dict, List, Optional


class MyStocksException(Exception):
    """MyStocks系统基础异常类"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "MSE0001"
        self.details = details or {}
        self.timestamp = self._get_timestamp()

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message} | Details: {self.details}"


class DataException(MyStocksException):
    """数据相关异常基类"""
    pass


class DataNotFoundException(DataException):
    """数据未找到异常"""
    def __init__(self, message: str, symbol: Optional[str] = None, data_type: Optional[str] = None):
        details = {"symbol": symbol, "data_type": data_type}
        super().__init__(message, "MSE1001", details)


class DataValidationError(DataException):
    """数据验证异常"""
    def __init__(self, message: str, validation_errors: Optional[List[Any]] = None):
        details = {"validation_errors": validation_errors}
        super().__init__(message, "MSE1002", details)


class DataIntegrityException(DataException):
    """数据完整性异常"""
    def __init__(self, message: str, table_name: Optional[str] = None, record_id: Optional[str] = None):
        details = {"table_name": table_name, "record_id": record_id}
        super().__init__(message, "MSE1003", details)


class DataQualityException(DataException):
    """数据质量异常"""
    def __init__(self, message: str, quality_issues: Optional[List[Any]] = None):
        details = {"quality_issues": quality_issues}
        super().__init__(message, "MSE1004", details)


class DatabaseException(MyStocksException):
    """数据库相关异常"""
    pass


class DatabaseConnectionError(DatabaseException):
    """数据库连接异常"""
    def __init__(self, message: str, db_type: Optional[str] = None, connection_info: Optional[Dict[str, Any]] = None):
        details = {"db_type": db_type, "connection_info": connection_info}
        super().__init__(message, "MSE2001", details)


class DatabaseQueryError(DatabaseException):
    """数据库查询异常"""
    def __init__(self, message: str, query: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        details = {"query": query, "params": params}
        super().__init__(message, "MSE2002", details)


class DatabaseIntegrityError(DatabaseException):
    """数据库完整性异常"""
    def __init__(self, message: str, constraint: Optional[str] = None, table: Optional[str] = None):
        details = {"constraint": constraint, "table": table}
        super().__init__(message, "MSE2003", details)


class ConfigException(MyStocksException):
    """配置相关异常"""
    pass


class ConfigFileNotFound(ConfigException):
    """配置文件未找到异常"""
    def __init__(self, file_path: str):
        details = {"file_path": file_path}
        super().__init__(f"配置文件未找到: {file_path}", "MSE3001", details)


class ConfigValueError(ConfigException):
    """配置值错误异常"""
    def __init__(self, key: str, value: Any, expected_type: Optional[str] = None):
        details = {"key": key, "value": value, "expected_type": expected_type}
        super().__init__(f"配置值错误: {key}={value}", "MSE3002", details)


class ConfigValidationFailed(ConfigException):
    """配置验证失败异常"""
    def __init__(self, validation_errors: list):
        details = {"validation_errors": validation_errors}
        super().__init__("配置验证失败", "MSE3003", details)


class NetworkException(MyStocksException):
    """网络相关异常"""
    pass


class NetworkConnectionError(NetworkException):
    """网络连接异常"""
    def __init__(self, message: str, url: Optional[str] = None, timeout: Optional[float] = None):
        details = {"url": url, "timeout": timeout}
        super().__init__(message, "MSE4001", details)


class NetworkTimeoutError(NetworkException):
    """网络超时异常"""
    def __init__(self, message: str, timeout: Optional[float] = None, url: Optional[str] = None):
        details = {"timeout": timeout, "url": url}
        super().__init__(message, "MSE4002", details)


class HTTPError(NetworkException):
    """HTTP错误异常"""
    def __init__(self, status_code: int, message: str, url: Optional[str] = None, response: Optional[str] = None):
        details = {"status_code": status_code, "url": url, "response": response}
        super().__init__(f"HTTP错误: {status_code} - {message}", "MSE4003", details)


class SecurityException(MyStocksException):
    """安全相关异常"""
    pass


class AuthenticationError(SecurityException):
    """认证错误异常"""
    def __init__(self, message: str, user_id: Optional[str] = None):
        details = {"user_id": user_id}
        super().__init__(message, "MSE5001", details)


class AuthorizationError(SecurityException):
    """授权错误异常"""
    def __init__(self, message: str, user_id: Optional[str] = None, resource: Optional[str] = None):
        details = {"user_id": user_id, "resource": resource}
        super().__init__(message, "MSE5002", details)


class DataAccessError(SecurityException):
    """数据访问错误异常"""
    def __init__(self, message: str, user_id: Optional[str] = None, table_name: Optional[str] = None):
        details = {"user_id": user_id, "table_name": table_name}
        super().__init__(message, "MSE5003", details)


class ProcessingException(MyStocksException):
    """数据处理相关异常"""
    pass


class BatchProcessingError(ProcessingException):
    """批量处理错误异常"""
    def __init__(self, message: str, failed_records: Optional[List[Any]] = None, total_records: Optional[int] = None):
        details = {"failed_records": failed_records or [], "total_records": total_records}
        super().__init__(message, "MSE6001", details)


class DataFormatError(ProcessingException):
    """数据格式错误异常"""
    def __init__(self, message: str, expected_format: Optional[str] = None, actual_format: Optional[str] = None):
        details = {"expected_format": expected_format, "actual_format": actual_format}
        super().__init__(message, "MSE6002", details)


class ValidationException(ProcessingException):
    """验证错误异常"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None, validation_rule: Optional[str] = None):
        details = {"field": field, "value": value, "validation_rule": validation_rule}
        super().__init__(message, "MSE6003", details)


class BusinessLogicException(MyStocksException):
    """业务逻辑相关异常"""
    pass


class TradingRuleViolation(BusinessLogicException):
    """交易规则违反异常"""
    def __init__(self, message: str, rule: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        details = {"rule": rule, "context": context}
        super().__init__(message, "MSE7001", details)


class RiskControlException(BusinessLogicException):
    """风控相关异常"""
    def __init__(self, message: str, risk_level: Optional[str] = None, risk_factors: Optional[List[Any]] = None):
        details = {"risk_level": risk_level, "risk_factors": risk_factors}
        super().__init__(message, "MSE7002", details)


class UnsupportedOperation(BusinessLogicException):
    """不支持的操作异常"""
    def __init__(self, operation: str, reason: Optional[str] = None):
        details = {"operation": operation, "reason": reason}
        super().__init__(f"不支持的操作: {operation}", "MSE7003", details)


# 全局异常处理装饰器
def handle_exceptions(default_return: Any = None, reraise: bool = False, logger: Any = None) -> Any:
    """
    异常处理装饰器

    Args:
        default_return: 异常发生时的默认返回值
        reraise: 是否重新抛出异常
        logger: 日志记录器实例
    """
    from functools import wraps

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except MyStocksException:
                # MyStocks自定义异常直接处理
                raise
            except Exception as e:
                # 记录原始异常信息
                if logger:
                    logger.error(
                        f"函数 {func.__name__} 执行出错: {str(e)}",
                        exc_info=True,
                        extra={
                            "function": func.__name__,
                            "args": str(args)[:200],  # 限制长度
                            "kwargs": str(kwargs)[:200]  # 限制长度
                        }
                    )

                if reraise:
                    raise

                return default_return
        return wrapper
    return decorator