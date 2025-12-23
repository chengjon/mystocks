"""
MyStocks Custom Exception Hierarchy

This module defines all custom exceptions used throughout the MyStocks application.
For details, see docs/guides/PHASE1_EXCEPTION_HIERARCHY.md
"""

import traceback
from datetime import datetime
from typing import Any, Dict, Optional


class MyStocksException(Exception):
    """Base exception class for all MyStocks application exceptions."""

    severity_levels = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    default_code = "UNKNOWN_ERROR"
    default_severity = "HIGH"

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        severity: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        self.message = message
        self.code = code or self.default_code
        self.severity = severity or self.default_severity
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()

        if original_exception and not isinstance(original_exception, MyStocksException):
            self.context["original_error"] = str(original_exception)
            self.context["original_traceback"] = traceback.format_exc()

        super().__init__(self.format_message())

    def format_message(self) -> str:
        parts = [f"[{self.code}] {self.message}"]
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "severity": self.severity,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "original_exception": str(self.original_exception)
            if self.original_exception
            else None,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(code={self.code!r}, severity={self.severity!r})"
        )


# Data Source Exceptions
class DataSourceException(MyStocksException):
    """Base exception for data source operations."""

    default_code = "DATA_SOURCE_ERROR"


class NetworkError(DataSourceException):
    """Raised when network operation fails."""

    default_code = "NETWORK_ERROR"
    default_severity = "HIGH"


class DataFetchError(DataSourceException):
    """Raised when data fetch operation fails."""

    default_code = "DATA_FETCH_FAILED"
    default_severity = "HIGH"


class DataParseError(DataSourceException):
    """Raised when data parsing/deserialization fails."""

    default_code = "DATA_PARSE_ERROR"
    default_severity = "MEDIUM"


class DataValidationError(DataSourceException):
    """Raised when data validation fails."""

    default_code = "DATA_VALIDATION_ERROR"
    default_severity = "MEDIUM"


# Database Exceptions
class DatabaseException(MyStocksException):
    """Base exception for database operations."""

    default_code = "DATABASE_ERROR"


class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails."""

    default_code = "DATABASE_CONNECTION_ERROR"
    default_severity = "CRITICAL"


class DatabaseOperationError(DatabaseException):
    """Raised when database query/insert/update/delete fails."""

    default_code = "DATABASE_OPERATION_ERROR"
    default_severity = "HIGH"


class DatabaseIntegrityError(DatabaseException):
    """Raised when database constraint is violated."""

    default_code = "DATABASE_INTEGRITY_ERROR"
    default_severity = "HIGH"


class DatabaseNotFoundError(DatabaseException):
    """Raised when requested database resource is not found."""

    default_code = "DATABASE_NOT_FOUND"
    default_severity = "MEDIUM"


# Cache Exceptions
class CacheException(MyStocksException):
    """Base exception for caching operations."""

    default_code = "CACHE_ERROR"


class CacheStoreError(CacheException):
    """Raised when failed to store value in cache."""

    default_code = "CACHE_STORE_ERROR"
    default_severity = "MEDIUM"


class CacheRetrievalError(CacheException):
    """Raised when failed to retrieve value from cache."""

    default_code = "CACHE_RETRIEVAL_ERROR"
    default_severity = "MEDIUM"


class CacheInvalidationError(CacheException):
    """Raised when cache invalidation fails."""

    default_code = "CACHE_INVALIDATION_ERROR"
    default_severity = "LOW"


# Configuration Exceptions
class ConfigurationException(MyStocksException):
    """Base exception for configuration errors."""

    default_code = "CONFIGURATION_ERROR"


class ConfigNotFoundError(ConfigurationException):
    """Raised when required configuration is missing."""

    default_code = "CONFIG_NOT_FOUND"
    default_severity = "CRITICAL"


class ConfigInvalidError(ConfigurationException):
    """Raised when configuration value is invalid."""

    default_code = "CONFIG_INVALID"
    default_severity = "HIGH"


class ConfigValidationError(ConfigurationException):
    """Raised when configuration validation fails."""

    default_code = "CONFIG_VALIDATION_ERROR"
    default_severity = "HIGH"


# Validation Exceptions
class ValidationException(MyStocksException):
    """Base exception for data validation failures."""

    default_code = "VALIDATION_ERROR"


class SchemaValidationError(ValidationException):
    """Raised when data schema doesn't match expected format."""

    default_code = "SCHEMA_VALIDATION_ERROR"
    default_severity = "MEDIUM"


class DataTypeError(ValidationException):
    """Raised when data type doesn't match expected type."""

    default_code = "DATA_TYPE_ERROR"
    default_severity = "MEDIUM"


class RangeError(ValidationException):
    """Raised when value is out of acceptable range."""

    default_code = "RANGE_ERROR"
    default_severity = "MEDIUM"


class RequiredFieldError(ValidationException):
    """Raised when required field is missing."""

    default_code = "REQUIRED_FIELD_ERROR"
    default_severity = "MEDIUM"


# Business Logic Exceptions
class BusinessLogicException(MyStocksException):
    """Base exception for business rule violations."""

    default_code = "BUSINESS_LOGIC_ERROR"


class InsufficientFundsError(BusinessLogicException):
    """Raised when account has insufficient funds for operation."""

    default_code = "INSUFFICIENT_FUNDS"
    default_severity = "HIGH"


class InvalidStrategyError(BusinessLogicException):
    """Raised when strategy parameters are invalid."""

    default_code = "INVALID_STRATEGY"
    default_severity = "HIGH"


class BacktestError(BusinessLogicException):
    """Raised when backtest execution fails."""

    default_code = "BACKTEST_ERROR"
    default_severity = "HIGH"


class TradeExecutionError(BusinessLogicException):
    """Raised when trade execution fails."""

    default_code = "TRADE_EXECUTION_ERROR"
    default_severity = "HIGH"


# Authentication Exceptions
class AuthenticationException(MyStocksException):
    """Base exception for authentication failures."""

    default_code = "AUTHENTICATION_ERROR"


class InvalidCredentialsError(AuthenticationException):
    """Raised when username/password is incorrect."""

    default_code = "INVALID_CREDENTIALS"
    default_severity = "MEDIUM"


class TokenExpiredError(AuthenticationException):
    """Raised when JWT token has expired."""

    default_code = "TOKEN_EXPIRED"
    default_severity = "MEDIUM"


class TokenInvalidError(AuthenticationException):
    """Raised when JWT token is invalid or malformed."""

    default_code = "TOKEN_INVALID"
    default_severity = "MEDIUM"


class UnauthorizedAccessError(AuthenticationException):
    """Raised when access to resource is denied."""

    default_code = "UNAUTHORIZED_ACCESS"
    default_severity = "MEDIUM"


# Timeout Exceptions
class TimeoutException(MyStocksException):
    """Base exception for operation timeouts."""

    default_code = "TIMEOUT_ERROR"


class NetworkTimeoutError(TimeoutException):
    """Raised when network operation times out."""

    default_code = "NETWORK_TIMEOUT"
    default_severity = "HIGH"


class DatabaseTimeoutError(TimeoutException):
    """Raised when database query times out."""

    default_code = "DATABASE_TIMEOUT"
    default_severity = "HIGH"


class OperationTimeoutError(TimeoutException):
    """Raised when generic operation times out."""

    default_code = "OPERATION_TIMEOUT"
    default_severity = "MEDIUM"


# External Service Exceptions
class ExternalServiceException(MyStocksException):
    """Base exception for external service failures."""

    default_code = "EXTERNAL_SERVICE_ERROR"


class ServiceUnavailableError(ExternalServiceException):
    """Raised when external service is unavailable."""

    default_code = "SERVICE_UNAVAILABLE"
    default_severity = "HIGH"


class ServiceError(ExternalServiceException):
    """Raised when external service returns an error."""

    default_code = "SERVICE_ERROR"
    default_severity = "HIGH"


class RateLimitError(ExternalServiceException):
    """Raised when rate limit is exceeded."""

    default_code = "RATE_LIMIT_EXCEEDED"
    default_severity = "MEDIUM"


class UnexpectedResponseError(ExternalServiceException):
    """Raised when external service returns unexpected response."""

    default_code = "UNEXPECTED_RESPONSE"
    default_severity = "MEDIUM"


# Exception Registry
EXCEPTION_REGISTRY = {
    "NetworkError": NetworkError,
    "DataFetchError": DataFetchError,
    "DataParseError": DataParseError,
    "DataValidationError": DataValidationError,
    "DatabaseConnectionError": DatabaseConnectionError,
    "DatabaseOperationError": DatabaseOperationError,
    "DatabaseIntegrityError": DatabaseIntegrityError,
    "DatabaseNotFoundError": DatabaseNotFoundError,
    "CacheStoreError": CacheStoreError,
    "CacheRetrievalError": CacheRetrievalError,
    "CacheInvalidationError": CacheInvalidationError,
    "ConfigNotFoundError": ConfigNotFoundError,
    "ConfigInvalidError": ConfigInvalidError,
    "ConfigValidationError": ConfigValidationError,
    "SchemaValidationError": SchemaValidationError,
    "DataTypeError": DataTypeError,
    "RangeError": RangeError,
    "RequiredFieldError": RequiredFieldError,
    "InsufficientFundsError": InsufficientFundsError,
    "InvalidStrategyError": InvalidStrategyError,
    "BacktestError": BacktestError,
    "TradeExecutionError": TradeExecutionError,
    "InvalidCredentialsError": InvalidCredentialsError,
    "TokenExpiredError": TokenExpiredError,
    "TokenInvalidError": TokenInvalidError,
    "UnauthorizedAccessError": UnauthorizedAccessError,
    "NetworkTimeoutError": NetworkTimeoutError,
    "DatabaseTimeoutError": DatabaseTimeoutError,
    "OperationTimeoutError": OperationTimeoutError,
    "ServiceUnavailableError": ServiceUnavailableError,
    "ServiceError": ServiceError,
    "RateLimitError": RateLimitError,
    "UnexpectedResponseError": UnexpectedResponseError,
}


def get_exception_class(exception_name: str) -> Optional[type]:
    """Get exception class by name."""
    return EXCEPTION_REGISTRY.get(exception_name)


__all__ = list(EXCEPTION_REGISTRY.keys()) + [
    "MyStocksException",
    "EXCEPTION_REGISTRY",
    "get_exception_class",
]
