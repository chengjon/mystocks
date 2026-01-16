#!/usr/bin/env python3
"""
Exceptions Phase 6 测试套件
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
目标：将exceptions.py的覆盖率从初始状态提升到95%+
覆盖38个异常类的完整层次结构
"""

import sys
import os
import time
from pathlib import Path
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入所有异常类
from src.core.exceptions import (
    # Base exception
    MyStocksException,

    # Data Source Exceptions
    DataSourceException, NetworkError, DataFetchError,
    DataParseError, DataValidationError,

    # Database Exceptions
    DatabaseException, DatabaseConnectionError, DatabaseOperationError,
    DatabaseIntegrityError, DatabaseNotFoundError,

    # Cache Exceptions
    CacheException, CacheStoreError, CacheRetrievalError, CacheInvalidationError,

    # Configuration Exceptions
    ConfigurationException, ConfigNotFoundError, ConfigInvalidError, ConfigValidationError,

    # Validation Exceptions
    ValidationException, SchemaValidationError, DataTypeError, RangeError, RequiredFieldError,

    # Business Logic Exceptions
    BusinessLogicException, InsufficientFundsError, InvalidStrategyError,
    BacktestError, TradeExecutionError,

    # Authentication Exceptions
    AuthenticationException, InvalidCredentialsError, TokenExpiredError,
    TokenInvalidError, UnauthorizedAccessError,

    # Timeout Exceptions
    TimeoutException, NetworkTimeoutError, DatabaseTimeoutError, OperationTimeoutError,

    # External Service Exceptions
    ExternalServiceException, ServiceUnavailableError, ServiceError,
    RateLimitError, UnexpectedResponseError
)


class TestMyStocksExceptionBase:
    """测试MyStocksException基类功能"""

    def test_basic_initialization(self):
        """测试基本初始化"""
        exc = MyStocksException("Test message")
        assert exc.message == "Test message"
        assert exc.code == "UNKNOWN_ERROR"
        assert exc.severity == "HIGH"
        assert exc.context == {}
        assert exc.original_exception is None
        assert isinstance(exc.timestamp, datetime)

    def test_full_initialization(self):
        """测试完整参数初始化"""
        context = {"key": "value", "number": 42}
        original_exc = ValueError("Original error")

        exc = MyStocksException(
            message="Test error",
            code="CUSTOM_CODE",
            severity="MEDIUM",
            context=context,
            original_exception=original_exc
        )

        assert exc.message == "Test error"
        assert exc.code == "CUSTOM_CODE"
        assert exc.severity == "MEDIUM"
        assert exc.context == context
        assert exc.original_exception == original_exc
        assert "original_error" in exc.context
        assert "original_traceback" in exc.context

    def test_format_message(self):
        """测试消息格式化"""
        # 无上下文
        exc = MyStocksException("Test message")
        assert "[UNKNOWN_ERROR] Test message" in str(exc)

        # 有上下文
        exc = MyStocksException("Test", context={"key": "value"})
        formatted = str(exc)
        assert "[UNKNOWN_ERROR] Test" in formatted
        assert "Context: key=value" in formatted

    def test_to_dict(self):
        """测试转换为字典"""
        context = {"test": "data"}
        exc = MyStocksException("Test", context=context)

        result = exc.to_dict()

        assert result["type"] == "MyStocksException"
        assert result["message"] == "Test"
        assert result["code"] == "UNKNOWN_ERROR"
        assert result["severity"] == "HIGH"
        assert result["context"] == context
        assert "timestamp" in result
        assert result["original_exception"] is None

    def test_repr(self):
        """测试repr方法"""
        exc = MyStocksException("Test")
        result = repr(exc)
        assert "MyStocksException" in result
        assert "code='UNKNOWN_ERROR'" in result
        assert "severity='HIGH'" in result

    def test_severity_levels_constant(self):
        """测试严重级别常量"""
        expected_levels = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
        assert MyStocksException.severity_levels == expected_levels

    def test_original_exception_handling(self):
        """测试原始异常处理"""
        original = ValueError("Test")

        # MyStocksException作为原始异常
        mystocks_exc = MyStocksException("Wrapped", original_exception=original)
        assert "original_error" not in mystocks_exc.context

        # 另一个MyStocksException作为原始异常
        another_mystocks = MyStocksException("Another")
        wrapped_exc = MyStocksException("Wrapped", original_exception=another_mystocks)
        assert "original_error" not in wrapped_exc.context


class TestDataSourceExceptions:
    """测试数据源异常层次结构"""

    def test_data_source_exception_defaults(self):
        """测试DataSourceException默认值"""
        exc = DataSourceException("Data source error")
        assert exc.code == "DATA_SOURCE_ERROR"
        assert exc.severity == "HIGH"  # 继承自基类默认值
        assert isinstance(exc, MyStocksException)

    def test_network_error_defaults(self):
        """测试NetworkError默认值"""
        exc = NetworkError("Network failed")
        assert exc.code == "NETWORK_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc, DataSourceException)

    def test_data_fetch_error_defaults(self):
        """测试DataFetchError默认值"""
        exc = DataFetchError("Fetch failed")
        assert exc.code == "DATA_FETCH_FAILED"
        assert exc.severity == "HIGH"
        assert isinstance(exc, DataSourceException)

    def test_data_parse_error_defaults(self):
        """测试DataParseError默认值"""
        exc = DataParseError("Parse failed")
        assert exc.code == "DATA_PARSE_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, DataSourceException)

    def test_data_validation_error_defaults(self):
        """测试DataValidationError默认值"""
        exc = DataValidationError("Validation failed")
        assert exc.code == "DATA_VALIDATION_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, DataSourceException)

    def test_exception_hierarchy(self):
        """测试异常层次关系"""
        exc = NetworkError("Test")
        assert isinstance(exc, DataSourceException)
        assert isinstance(exc, MyStocksException)
        assert isinstance(exc, Exception)


class TestDatabaseExceptions:
    """测试数据库异常层次结构"""

    def test_database_exception_base(self):
        """测试DatabaseException基类"""
        exc = DatabaseException("Database error")
        assert exc.code == "DATABASE_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_database_connection_error(self):
        """测试DatabaseConnectionError"""
        exc = DatabaseConnectionError("Connection failed")
        assert exc.code == "DB_CONNECTION_ERROR"
        assert exc.severity == "CRITICAL"
        assert isinstance(exc, DatabaseException)

    def test_database_operation_error(self):
        """测试DatabaseOperationError"""
        exc = DatabaseOperationError("Operation failed")
        assert exc.code == "DB_OPERATION_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc, DatabaseException)

    def test_database_integrity_error(self):
        """测试DatabaseIntegrityError"""
        exc = DatabaseIntegrityError("Integrity violation")
        assert exc.code == "DB_INTEGRITY_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc, DatabaseException)

    def test_database_not_found_error(self):
        """测试DatabaseNotFoundError"""
        exc = DatabaseNotFoundError("Database not found")
        assert exc.code == "DB_NOT_FOUND"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, DatabaseException)


class TestCacheExceptions:
    """测试缓存异常层次结构"""

    def test_cache_exception_base(self):
        """测试CacheException基类"""
        exc = CacheException("Cache error")
        assert exc.code == "CACHE_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_cache_store_error(self):
        """测试CacheStoreError"""
        exc = CacheStoreError("Store failed")
        assert exc.code == "CACHE_STORE_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, CacheException)

    def test_cache_retrieval_error(self):
        """测试CacheRetrievalError"""
        exc = CacheRetrievalError("Retrieval failed")
        assert exc.code == "CACHE_RETRIEVAL_ERROR"
        assert exc.severity == "LOW"
        assert isinstance(exc, CacheException)

    def test_cache_invalidation_error(self):
        """测试CacheInvalidationError"""
        exc = CacheInvalidationError("Invalidation failed")
        assert exc.code == "CACHE_INVALIDATION_ERROR"
        assert exc.severity == "LOW"
        assert isinstance(exc, CacheException)


class TestConfigurationExceptions:
    """测试配置异常层次结构"""

    def test_configuration_exception_base(self):
        """测试ConfigurationException基类"""
        exc = ConfigurationException("Config error")
        assert exc.code == "CONFIG_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_config_not_found_error(self):
        """测试ConfigNotFoundError"""
        exc = ConfigNotFoundError("Config file not found")
        assert exc.code == "CONFIG_NOT_FOUND"
        assert exc.severity == "HIGH"
        assert isinstance(exc, ConfigurationException)

    def test_config_invalid_error(self):
        """测试ConfigInvalidError"""
        exc = ConfigInvalidError("Invalid config format")
        assert exc.code == "CONFIG_INVALID"
        assert exc.severity == "HIGH"
        assert isinstance(exc, ConfigurationException)

    def test_config_validation_error(self):
        """测试ConfigValidationError"""
        exc = ConfigValidationError("Config validation failed")
        assert exc.code == "CONFIG_VALIDATION_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, ConfigurationException)


class TestValidationExceptions:
    """测试验证异常层次结构"""

    def test_validation_exception_base(self):
        """测试ValidationException基类"""
        exc = ValidationException("Validation error")
        assert exc.code == "VALIDATION_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_schema_validation_error(self):
        """测试SchemaValidationError"""
        exc = SchemaValidationError("Schema validation failed")
        assert exc.code == "SCHEMA_VALIDATION_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc, ValidationException)

    def test_data_type_error(self):
        """测试DataTypeError"""
        exc = DataTypeError("Invalid data type")
        assert exc.code == "DATA_TYPE_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, ValidationException)

    def test_range_error(self):
        """测试RangeError"""
        exc = RangeError("Value out of range")
        assert exc.code == "RANGE_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, ValidationException)

    def test_required_field_error(self):
        """测试RequiredFieldError"""
        exc = RequiredFieldError("Required field missing")
        assert exc.code == "REQUIRED_FIELD_ERROR"
        assert exc.severity = "HIGH"
        assert isinstance(exc, ValidationException)


class TestBusinessLogicExceptions:
    """测试业务逻辑异常层次结构"""

    def test_business_logic_exception_base(self):
        """测试BusinessLogicException基类"""
        exc = BusinessLogicException("Business logic error")
        assert exc.code == "BUSINESS_LOGIC_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_insufficient_funds_error(self):
        """测试InsufficientFundsError"""
        exc = InsufficientFundsError("Insufficient funds")
        assert exc.code == "INSUFFICIENT_FUNDS"
        assert exc.severity == "HIGH"
        assert isinstance(exc, BusinessLogicException)

    def test_invalid_strategy_error(self):
        """测试InvalidStrategyError"""
        exc = InvalidStrategyError("Invalid strategy")
        assert exc.code == "INVALID_STRATEGY"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, BusinessLogicException)

    def test_backtest_error(self):
        """测试BacktestError"""
        exc = BacktestError("Backtest failed")
        assert exc.code == "BACKTEST_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, BusinessLogicException)

    def test_trade_execution_error(self):
        """测试TradeExecutionError"""
        exc = TradeExecutionError("Trade execution failed")
        assert exc.code == "TRADE_EXECUTION_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc, BusinessLogicException)


class TestAuthenticationExceptions:
    """测试认证异常层次结构"""

    def test_authentication_exception_base(self):
        """测试AuthenticationException基类"""
        exc = AuthenticationException("Auth error")
        assert exc.code == "AUTHENTICATION_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_invalid_credentials_error(self):
        """测试InvalidCredentialsError"""
        exc = InvalidCredentialsError("Invalid credentials")
        assert exc.code == "INVALID_CREDENTIALS"
        assert exc.severity == "HIGH"
        assert isinstance(exc, AuthenticationException)

    def test_token_expired_error(self):
        """测试TokenExpiredError"""
        exc = TokenExpiredError("Token expired")
        assert exc.code == "TOKEN_EXPIRED"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, AuthenticationException)

    def test_token_invalid_error(self):
        """测试TokenInvalidError"""
        exc = TokenInvalidError("Invalid token")
        assert exc.code == "TOKEN_INVALID"
        assert exc.severity == "HIGH"
        assert isinstance(exc, AuthenticationException)

    def test_unauthorized_access_error(self):
        """测试UnauthorizedAccessError"""
        exc = UnauthorizedAccessError("Unauthorized access")
        assert exc.code == "UNAUTHORIZED_ACCESS"
        assert exc.severity == "HIGH"
        assert isinstance(exc, AuthenticationException)


class TestTimeoutExceptions:
    """测试超时异常层次结构"""

    def test_timeout_exception_base(self):
        """测试TimeoutException基类"""
        exc = TimeoutException("Timeout")
        assert exc.code == "TIMEOUT_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_network_timeout_error(self):
        """测试NetworkTimeoutError"""
        exc = NetworkTimeoutError("Network timeout")
        assert exc.code == "NETWORK_TIMEOUT"
        assert exc.severity == "HIGH"
        assert isinstance(exc, TimeoutException)

    def test_database_timeout_error(self):
        """测试DatabaseTimeoutError"""
        exc = DatabaseTimeoutError("Database timeout")
        assert exc.code == "DB_TIMEOUT"
        assert exc.severity == "HIGH"
        assert isinstance(exc, TimeoutException)

    def test_operation_timeout_error(self):
        """测试OperationTimeoutError"""
        exc = OperationTimeoutError("Operation timeout")
        assert exc.code == "OPERATION_TIMEOUT"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, TimeoutException)


class TestExternalServiceExceptions:
    """测试外部服务异常层次结构"""

    def test_external_service_exception_base(self):
        """测试ExternalServiceException基类"""
        exc = ExternalServiceException("Service error")
        assert exc.code == "EXTERNAL_SERVICE_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_service_unavailable_error(self):
        """测试ServiceUnavailableError"""
        exc = ServiceUnavailableError("Service unavailable")
        assert exc.code == "SERVICE_UNAVAILABLE"
        assert exc.severity == "HIGH"
        assert isinstance(exc, ExternalServiceException)

    def test_service_error(self):
        """测试ServiceError"""
        exc = ServiceError("Service error")
        assert exc.code == "SERVICE_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, ExternalServiceException)

    def test_rate_limit_error(self):
        """测试RateLimitError"""
        exc = RateLimitError("Rate limit exceeded")
        assert exc.code == "RATE_LIMIT_ERROR"
        assert exc.severity == "MEDIUM"
        assert isinstance(exc, ExternalServiceException)

    def test_unexpected_response_error(self):
        """测试UnexpectedResponseError"""
        exc = UnexpectedResponseError("Unexpected response")
        assert exc.code == "UNEXPECTED_RESPONSE"
        assert exc.severity == "LOW"
        assert isinstance(exc, ExternalServiceException)


class TestExceptionWithComplexScenarios:
    """测试复杂异常场景"""

    def test_nested_exceptions(self):
        """测试嵌套异常"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise DataFetchError("Failed to fetch data", original_exception=e)
        except DataFetchError as e:
            assert isinstance(e, DataSourceException)
            assert isinstance(e, MyStocksException)
            assert e.original_exception.__class__.__name__ == "ValueError"
            assert "Original error" in str(e.original_exception)

    def test_exception_with_rich_context(self):
        """测试带丰富上下文的异常"""
        context = {
            "symbol": "000001",
            "date_range": "2024-01-01 to 2024-01-31",
            "source": "akshare",
            "retry_count": 3,
            "timeout": 30,
            "data_size": 1024
        }

        exc = DataValidationError(
            "Data validation failed",
            context=context
        )

        result = exc.to_dict()
        assert result["context"] == context

        formatted = str(exc)
        for key, value in context.items():
            assert f"{key}={value}" in formatted

    def test_exception_chain(self):
        """测试异常链"""
        original_error = ValueError("Base error")
        intermediate_error = NetworkError("Network failed", original_exception=original_error)
        final_error = DataFetchError("Data fetch failed", original_exception=intermediate_error)

        assert final_error.original_exception == intermediate_error
        assert intermediate_error.original_exception == original_error

    def test_exception_with_none_context(self):
        """测试None上下文处理"""
        exc = MyStocksException("Test", context=None)
        assert exc.context == {}

    def test_exception_timestamp_consistency(self):
        """测试时间戳一致性"""
        before = datetime.now()
        exc = MyStocksException("Test")
        after = datetime.now()

        assert before <= exc.timestamp <= after

    def test_exception_inheritance_chains(self):
        """测试多层继承链"""
        exc = DatabaseConnectionError("Connection failed")

        # 验证完整的继承链
        assert isinstance(exc, DatabaseConnectionError)
        assert isinstance(exc, DatabaseException)
        assert isinstance(exc, MyStocksException)
        assert isinstance(exc, Exception)

        # 验证方法解析顺序
        assert exc.code == "DB_CONNECTION_ERROR"
        assert exc.severity == "CRITICAL"


class TestExceptionPerformance:
    """测试异常处理性能"""

    def test_exception_creation_performance(self):
        """测试异常创建性能"""
        exceptions_to_create = 1000

        start_time = time.time()
        for i in range(exceptions_to_create):
            exc = DataFetchError(f"Error {i}", context={"index": i})
        creation_time = time.time() - start_time

        # 应该能在合理时间内创建大量异常
        assert creation_time < 1.0  # 1000个异常在1秒内创建
        assert creation_time / exceptions_to_create < 0.001  # 每个异常<1ms

    def test_exception_serialization_performance(self):
        """测试异常序列化性能"""
        context = {"large_data": "x" * 1000}
        exc = MyStocksException("Large context exception", context=context)

        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            result = exc.to_dict()
            formatted = str(exc)

        serialization_time = time.time() - start_time
        assert serialization_time < 0.5  # 100次序列化在0.5秒内完成


class TestExceptionIntegration:
    """测试异常集成场景"""

    def test_exception_in_try_catch_blocks(self):
        """测试在try-catch块中的异常处理"""
        try:
            raise NetworkError("Network failed", context={"url": "http://example.com"})
        except NetworkError as e:
            assert isinstance(e, DataSourceException)
            assert "url=http://example.com" in str(e)
            assert e.code == "NETWORK_ERROR"

    def test_exception_logging_simulation(self):
        """测试异常日志记录模拟"""
        exc = DatabaseConnectionError(
            "Connection failed",
            context={
                "host": "localhost",
                "port": 5432,
                "database": "mystocks"
            }
        )

        # 模拟日志记录
        log_data = exc.to_dict()
        assert log_data["type"] == "DatabaseConnectionError"
        assert log_data["severity"] == "CRITICAL"
        assert "host" in log_data["context"]

    def test_exception_api_response_format(self):
        """测试异常API响应格式"""
        exc = RateLimitError(
            "Rate limit exceeded",
            context={
                "limit": 100,
                "remaining": 0,
                "reset_time": "2024-01-01T12:00:00Z"
            }
        )

        api_response = exc.to_dict()
        required_fields = ["type", "message", "code", "severity", "timestamp"]

        for field in required_fields:
            assert field in api_response

        assert api_response["code"] == "RATE_LIMIT_ERROR"
        assert api_response["severity"] == "MEDIUM"

    def test_custom_error_code_and_severity(self):
        """测试自定义错误代码和严重级别"""
        exc = MyStocksException(
            "Custom error",
            code="CUSTOM_001",
            severity="LOW",
            context={"custom_field": "custom_value"}
        )

        assert exc.code == "CUSTOM_001"
        assert exc.severity == "LOW"
        assert "custom_field=custom_value" in str(exc)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
