#!/usr/bin/env python3
"""
MyStocks异常系统测试套件
提供完整的异常层次结构和功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from datetime import datetime

# 导入被测试的模块
from src.core.exceptions import (
    MyStocksException,
    DataSourceException,
    DataSourceQueryError,
    DataSourceDataNotFound,
    NetworkError,
    DataFetchError,
    DataParseError,
    DataValidationError,
    DatabaseException,
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseIntegrityError,
    DatabaseNotFoundError,
    CacheException,
    CacheStoreError,
    CacheRetrievalError,
    CacheInvalidationError,
    ConfigurationException,
    ConfigNotFoundError,
    ConfigInvalidError,
    ConfigValidationError,
    ValidationException,
    SchemaValidationError,
    DataTypeError,
    RangeError,
    RequiredFieldError,
    BusinessLogicException,
    InsufficientFundsError,
    InvalidStrategyError,
    BacktestError,
    TradeExecutionError,
    AuthenticationException,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UnauthorizedAccessError,
    TimeoutException,
    NetworkTimeoutError,
    DatabaseTimeoutError,
    OperationTimeoutError,
    ExternalServiceException,
    ServiceUnavailableError,
    ServiceError,
    RateLimitError,
    UnexpectedResponseError,
    EXCEPTION_REGISTRY,
    get_exception_class,
)


class TestMyStocksException:
    """MyStocksException 基础异常类测试"""

    def test_basic_exception_creation(self):
        """测试基础异常创建"""
        exc = MyStocksException("Test message")

        assert exc.message == "Test message"
        assert exc.code == "UNKNOWN_ERROR"
        assert exc.severity == "HIGH"
        assert exc.context == {}
        assert exc.original_exception is None
        assert isinstance(exc.timestamp, datetime)

    def test_exception_with_custom_parameters(self):
        """测试带自定义参数的异常"""
        context = {"symbol": "AAPL", "action": "fetch"}
        exc = MyStocksException(
            message="Data fetch failed",
            code="CUSTOM_ERROR",
            severity="MEDIUM",
            context=context,
        )

        assert exc.message == "Data fetch failed"
        assert exc.code == "CUSTOM_ERROR"
        assert exc.severity == "MEDIUM"
        assert exc.context == context

    def test_exception_with_original_exception(self):
        """测试包含原始异常的情况"""
        original_exc = ValueError("Original error")
        exc = MyStocksException(
            message="Wrapped error", original_exception=original_exc
        )

        assert exc.original_exception == original_exc
        assert "original_error" in exc.context
        assert "original_traceback" in exc.context

    def test_exception_with_original_mystocks_exception(self):
        """测试包装MyStocksException的情况"""
        original_exc = MyStocksException("Original MyStocks error")
        exc = MyStocksException(
            message="Wrapped MyStocks error", original_exception=original_exc
        )

        assert exc.original_exception == original_exc
        assert "original_error" not in exc.context

    def test_format_message(self):
        """测试消息格式化"""
        context = {"symbol": "AAPL", "price": 100.5}
        exc = MyStocksException(
            message="Invalid price", code="PRICE_ERROR", context=context
        )

        formatted = exc.format_message()
        assert "[PRICE_ERROR] Invalid price" in formatted
        assert "symbol=AAPL" in formatted
        assert "price=100.5" in formatted

    def test_to_dict(self):
        """测试转换为字典"""
        context = {"symbol": "AAPL"}
        exc = MyStocksException(
            message="Test error", code="TEST_ERROR", context=context
        )

        result = exc.to_dict()
        assert result["type"] == "MyStocksException"
        assert result["message"] == "Test error"
        assert result["code"] == "TEST_ERROR"
        assert result["context"] == context
        assert "timestamp" in result

    def test_repr(self):
        """测试字符串表示"""
        exc = MyStocksException(
            message="Test error", code="TEST_CODE", severity="MEDIUM"
        )

        repr_str = repr(exc)
        assert "MyStocksException" in repr_str
        assert "code='TEST_CODE'" in repr_str
        assert "severity='MEDIUM'" in repr_str

    def test_severity_validation(self):
        """测试严重级别验证"""
        # 测试有效严重级别
        for severity in MyStocksException.severity_levels:
            exc = MyStocksException("Test", severity=severity)
            assert exc.severity == severity


class TestDataSourceExceptions:
    """数据源异常测试"""

    def test_data_source_exception_defaults(self):
        """测试数据源异常默认值"""
        exc = DataSourceException("Data source error")
        assert exc.code == "DATA_SOURCE_ERROR"
        assert isinstance(exc, MyStocksException)

    def test_data_source_query_error(self):
        """测试数据源查询错误"""
        exc = DataSourceQueryError("Query failed")
        assert exc.code == "DATA_SOURCE_QUERY_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc, DataSourceException)

    def test_data_source_data_not_found(self):
        """测试数据未找到错误"""
        exc = DataSourceDataNotFound("No data found")
        assert exc.code == "DATA_SOURCE_DATA_NOT_FOUND"
        assert exc.severity == "MEDIUM"

    def test_network_error(self):
        """测试网络错误"""
        exc = NetworkError("Network connection failed")
        assert exc.code == "NETWORK_ERROR"
        assert exc.severity == "HIGH"

    def test_data_fetch_error(self):
        """测试数据获取错误"""
        exc = DataFetchError("Failed to fetch data")
        assert exc.code == "DATA_FETCH_FAILED"

    def test_data_parse_error(self):
        """测试数据解析错误"""
        exc = DataParseError("JSON parse failed")
        assert exc.code == "DATA_PARSE_ERROR"
        assert exc.severity == "MEDIUM"

    def test_data_validation_error(self):
        """测试数据验证错误"""
        exc = DataValidationError("Data validation failed")
        assert exc.code == "DATA_VALIDATION_ERROR"
        assert exc.severity == "MEDIUM"


class TestDatabaseExceptions:
    """数据库异常测试"""

    def test_database_exception_defaults(self):
        """测试数据库异常默认值"""
        exc = DatabaseException("Database error")
        assert exc.code == "DATABASE_ERROR"

    def test_database_connection_error(self):
        """测试数据库连接错误"""
        exc = DatabaseConnectionError("Cannot connect to database")
        assert exc.code == "DATABASE_CONNECTION_ERROR"
        assert exc.severity == "CRITICAL"

    def test_database_operation_error(self):
        """测试数据库操作错误"""
        exc = DatabaseOperationError("Query failed")
        assert exc.code == "DATABASE_OPERATION_ERROR"
        assert exc.severity == "HIGH"

    def test_database_integrity_error(self):
        """测试数据库完整性错误"""
        exc = DatabaseIntegrityError("Constraint violation")
        assert exc.code == "DATABASE_INTEGRITY_ERROR"
        assert exc.severity == "HIGH"

    def test_database_not_found_error(self):
        """测试数据库未找到错误"""
        exc = DatabaseNotFoundError("Table not found")
        assert exc.code == "DATABASE_NOT_FOUND"
        assert exc.severity == "MEDIUM"


class TestCacheExceptions:
    """缓存异常测试"""

    def test_cache_exception_defaults(self):
        """测试缓存异常默认值"""
        exc = CacheException("Cache error")
        assert exc.code == "CACHE_ERROR"

    def test_cache_store_error(self):
        """测试缓存存储错误"""
        exc = CacheStoreError("Failed to store in cache")
        assert exc.code == "CACHE_STORE_ERROR"
        assert exc.severity == "MEDIUM"

    def test_cache_retrieval_error(self):
        """测试缓存检索错误"""
        exc = CacheRetrievalError("Failed to retrieve from cache")
        assert exc.code == "CACHE_RETRIEVAL_ERROR"

    def test_cache_invalidation_error(self):
        """测试缓存失效错误"""
        exc = CacheInvalidationError("Failed to invalidate cache")
        assert exc.code == "CACHE_INVALIDATION_ERROR"
        assert exc.severity == "LOW"


class TestConfigurationExceptions:
    """配置异常测试"""

    def test_configuration_exception_defaults(self):
        """测试配置异常默认值"""
        exc = ConfigurationException("Configuration error")
        assert exc.code == "CONFIGURATION_ERROR"

    def test_config_not_found_error(self):
        """测试配置未找到错误"""
        exc = ConfigNotFoundError("Config file not found")
        assert exc.code == "CONFIG_NOT_FOUND"
        assert exc.severity == "CRITICAL"

    def test_config_invalid_error(self):
        """测试配置无效错误"""
        exc = ConfigInvalidError("Invalid config value")
        assert exc.code == "CONFIG_INVALID"
        assert exc.severity == "HIGH"

    def test_config_validation_error(self):
        """测试配置验证错误"""
        exc = ConfigValidationError("Config validation failed")
        assert exc.code == "CONFIG_VALIDATION_ERROR"
        assert exc.severity == "HIGH"


class TestValidationExceptions:
    """验证异常测试"""

    def test_validation_exception_defaults(self):
        """测试验证异常默认值"""
        exc = ValidationException("Validation error")
        assert exc.code == "VALIDATION_ERROR"

    def test_schema_validation_error(self):
        """测试模式验证错误"""
        exc = SchemaValidationError("Schema validation failed")
        assert exc.code == "SCHEMA_VALIDATION_ERROR"
        assert exc.severity == "MEDIUM"

    def test_data_type_error(self):
        """测试数据类型错误"""
        exc = DataTypeError("Invalid data type")
        assert exc.code == "DATA_TYPE_ERROR"
        assert exc.severity == "MEDIUM"

    def test_range_error(self):
        """测试范围错误"""
        exc = RangeError("Value out of range")
        assert exc.code == "RANGE_ERROR"
        assert exc.severity == "MEDIUM"

    def test_required_field_error(self):
        """测试必填字段错误"""
        exc = RequiredFieldError("Required field missing")
        assert exc.code == "REQUIRED_FIELD_ERROR"
        assert exc.severity == "MEDIUM"


class TestBusinessLogicExceptions:
    """业务逻辑异常测试"""

    def test_business_logic_exception_defaults(self):
        """测试业务逻辑异常默认值"""
        exc = BusinessLogicException("Business logic error")
        assert exc.code == "BUSINESS_LOGIC_ERROR"

    def test_insufficient_funds_error(self):
        """测试资金不足错误"""
        exc = InsufficientFundsError("Insufficient funds")
        assert exc.code == "INSUFFICIENT_FUNDS"
        assert exc.severity == "HIGH"

    def test_invalid_strategy_error(self):
        """测试无效策略错误"""
        exc = InvalidStrategyError("Invalid strategy parameters")
        assert exc.code == "INVALID_STRATEGY"
        assert exc.severity == "HIGH"

    def test_backtest_error(self):
        """测试回测错误"""
        exc = BacktestError("Backtest failed")
        assert exc.code == "BACKTEST_ERROR"
        assert exc.severity == "HIGH"

    def test_trade_execution_error(self):
        """测试交易执行错误"""
        exc = TradeExecutionError("Trade execution failed")
        assert exc.code == "TRADE_EXECUTION_ERROR"
        assert exc.severity == "HIGH"


class TestAuthenticationExceptions:
    """认证异常测试"""

    def test_authentication_exception_defaults(self):
        """测试认证异常默认值"""
        exc = AuthenticationException("Authentication error")
        assert exc.code == "AUTHENTICATION_ERROR"

    def test_invalid_credentials_error(self):
        """测试无效凭据错误"""
        exc = InvalidCredentialsError("Invalid credentials")
        assert exc.code == "INVALID_CREDENTIALS"
        assert exc.severity == "MEDIUM"

    def test_token_expired_error(self):
        """测试令牌过期错误"""
        exc = TokenExpiredError("Token expired")
        assert exc.code == "TOKEN_EXPIRED"
        assert exc.severity == "MEDIUM"

    def test_token_invalid_error(self):
        """测试令牌无效错误"""
        exc = TokenInvalidError("Token invalid")
        assert exc.code == "TOKEN_INVALID"
        assert exc.severity == "MEDIUM"

    def test_unauthorized_access_error(self):
        """测试未授权访问错误"""
        exc = UnauthorizedAccessError("Access denied")
        assert exc.code == "UNAUTHORIZED_ACCESS"
        assert exc.severity == "MEDIUM"


class TestTimeoutExceptions:
    """超时异常测试"""

    def test_timeout_exception_defaults(self):
        """测试超时异常默认值"""
        exc = TimeoutException("Operation timeout")
        assert exc.code == "TIMEOUT_ERROR"

    def test_network_timeout_error(self):
        """测试网络超时错误"""
        exc = NetworkTimeoutError("Network timeout")
        assert exc.code == "NETWORK_TIMEOUT"
        assert exc.severity == "HIGH"

    def test_database_timeout_error(self):
        """测试数据库超时错误"""
        exc = DatabaseTimeoutError("Database timeout")
        assert exc.code == "DATABASE_TIMEOUT"
        assert exc.severity == "HIGH"

    def test_operation_timeout_error(self):
        """测试操作超时错误"""
        exc = OperationTimeoutError("Operation timeout")
        assert exc.code == "OPERATION_TIMEOUT"
        assert exc.severity == "MEDIUM"


class TestExternalServiceExceptions:
    """外部服务异常测试"""

    def test_external_service_exception_defaults(self):
        """测试外部服务异常默认值"""
        exc = ExternalServiceException("External service error")
        assert exc.code == "EXTERNAL_SERVICE_ERROR"

    def test_service_unavailable_error(self):
        """测试服务不可用错误"""
        exc = ServiceUnavailableError("Service unavailable")
        assert exc.code == "SERVICE_UNAVAILABLE"
        assert exc.severity == "HIGH"

    def test_service_error(self):
        """测试服务错误"""
        exc = ServiceError("Service error")
        assert exc.code == "SERVICE_ERROR"
        assert exc.severity == "HIGH"

    def test_rate_limit_error(self):
        """测试速率限制错误"""
        exc = RateLimitError("Rate limit exceeded")
        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert exc.severity == "MEDIUM"

    def test_unexpected_response_error(self):
        """测试意外响应错误"""
        exc = UnexpectedResponseError("Unexpected response")
        assert exc.code == "UNEXPECTED_RESPONSE"
        assert exc.severity == "MEDIUM"


class TestExceptionRegistry:
    """异常注册表测试"""

    def test_exception_registry_completeness(self):
        """测试异常注册表完整性"""
        # 验证注册表包含所有预期的异常
        expected_exceptions = [
            "DataSourceQueryError",
            "DataSourceDataNotFound",
            "NetworkError",
            "DataFetchError",
            "DataParseError",
            "DataValidationError",
            "DatabaseConnectionError",
            "DatabaseOperationError",
            "DatabaseIntegrityError",
            "DatabaseNotFoundError",
            "CacheStoreError",
            "CacheRetrievalError",
            "CacheInvalidationError",
            "ConfigNotFoundError",
            "ConfigInvalidError",
            "ConfigValidationError",
            "SchemaValidationError",
            "DataTypeError",
            "RangeError",
            "RequiredFieldError",
            "InsufficientFundsError",
            "InvalidStrategyError",
            "BacktestError",
            "TradeExecutionError",
            "InvalidCredentialsError",
            "TokenExpiredError",
            "TokenInvalidError",
            "UnauthorizedAccessError",
            "NetworkTimeoutError",
            "DatabaseTimeoutError",
            "OperationTimeoutError",
            "ServiceUnavailableError",
            "ServiceError",
            "RateLimitError",
            "UnexpectedResponseError",
        ]

        for exc_name in expected_exceptions:
            assert exc_name in EXCEPTION_REGISTRY
            assert EXCEPTION_REGISTRY[exc_name] is not None

    def test_get_exception_class_valid(self):
        """测试获取有效异常类"""
        exc_class = get_exception_class("NetworkError")
        assert exc_class == NetworkError

        exc_class = get_exception_class("DatabaseConnectionError")
        assert exc_class == DatabaseConnectionError

    def test_get_exception_class_invalid(self):
        """测试获取无效异常类"""
        exc_class = get_exception_class("NonExistentError")
        assert exc_class is None

    def test_get_exception_class_empty_string(self):
        """测试获取空字符串异常类"""
        exc_class = get_exception_class("")
        assert exc_class is None

    def test_get_exception_class_none(self):
        """测试获取None异常类"""
        exc_class = get_exception_class(None)
        assert exc_class is None


class TestExceptionHierarchy:
    """异常层次结构测试"""

    def test_inheritance_hierarchy(self):
        """测试继承层次结构"""
        # 数据源异常层次
        assert issubclass(DataSourceException, MyStocksException)
        assert issubclass(DataSourceQueryError, DataSourceException)
        assert issubclass(NetworkError, DataSourceException)

        # 数据库异常层次
        assert issubclass(DatabaseException, MyStocksException)
        assert issubclass(DatabaseConnectionError, DatabaseException)
        assert issubclass(DatabaseOperationError, DatabaseException)

        # 验证异常层次
        assert issubclass(ValidationException, MyStocksException)
        assert issubclass(SchemaValidationError, ValidationException)
        assert issubclass(DataTypeError, ValidationException)

        # 业务逻辑异常层次
        assert issubclass(BusinessLogicException, MyStocksException)
        assert issubclass(InsufficientFundsError, BusinessLogicException)
        assert issubclass(BacktestError, BusinessLogicException)

    def test_all_exceptions_inherit_from_base(self):
        """测试所有异常都继承自基类"""
        for exc_name, exc_class in EXCEPTION_REGISTRY.items():
            assert issubclass(exc_class, MyStocksException), (
                f"{exc_name} does not inherit from MyStocksException"
            )

    def test_exception_instance_creation(self):
        """测试异常实例创建"""
        # 测试创建各种异常实例
        exceptions_to_test = [
            DataSourceQueryError,
            NetworkError,
            DataFetchError,
            DatabaseConnectionError,
            DatabaseOperationError,
            CacheStoreError,
            ConfigNotFoundError,
            SchemaValidationError,
            InsufficientFundsError,
            InvalidCredentialsError,
            TokenExpiredError,
            NetworkTimeoutError,
            ServiceUnavailableError,
        ]

        for exc_class in exceptions_to_test:
            try:
                exc = exc_class("Test message")
                assert isinstance(exc, MyStocksException)
                assert exc.message == "Test message"
            except Exception as e:
                pytest.fail(f"Failed to create {exc_class.__name__}: {e}")


class TestExceptionEdgeCases:
    """异常边界情况测试"""

    def test_exception_with_empty_context(self):
        """测试空上下文的异常"""
        exc = MyStocksException("Test", context={})
        assert exc.context == {}
        assert "Context:" not in str(exc)

    def test_exception_with_none_context(self):
        """测试None上下文的异常"""
        exc = MyStocksException("Test", context=None)
        assert exc.context == {}

    def test_exception_with_complex_context(self):
        """测试复杂上下文的异常"""
        complex_context = {
            "symbol": "AAPL",
            "price": 150.25,
            "timestamp": datetime.now(),
            "nested": {"key": "value"},
            "list": [1, 2, 3],
        }
        exc = MyStocksException("Complex error", context=complex_context)

        # 验证上下文被正确处理
        assert exc.context == complex_context

    def test_exception_string_representation(self):
        """测试异常字符串表示"""
        exc = MyStocksException("Test message", code="TEST_CODE")
        str_repr = str(exc)
        assert "[TEST_CODE] Test message" in str_repr

    def test_exception_chaining(self):
        """测试异常链"""
        original = ValueError("Original error")
        wrapped = MyStocksException("Wrapped error", original_exception=original)

        # 验证异常链 - 通过字符串表示验证
        assert "Original error" in str(wrapped)

    def test_exception_serialization(self):
        """测试异常序列化"""
        exc = MyStocksException(
            "Test error", code="TEST_ERROR", severity="MEDIUM", context={"key": "value"}
        )

        # 测试to_dict方法的结果可以被JSON序列化
        import json

        exc_dict = exc.to_dict()

        try:
            json_str = json.dumps(exc_dict)
            assert json_str is not None
        except (TypeError, ValueError) as e:
            pytest.fail(f"Exception dict is not JSON serializable: {e}")


class TestExceptionPerformance:
    """异常性能测试"""

    def test_exception_creation_performance(self):
        """测试异常创建性能"""
        import time

        # 测试创建大量异常的性能
        start_time = time.time()
        for _ in range(1000):
            exc = MyStocksException(
                "Test message", code="TEST_ERROR", context={"key": "value"}
            )
        end_time = time.time()

        # 性能断言 - 应该在合理时间内完成
        processing_time = end_time - start_time
        assert processing_time < 1.0, (
            f"Exception creation too slow: {processing_time:.3f}s"
        )

    def test_exception_to_dict_performance(self):
        """测试异常转换为字典的性能"""
        exc = MyStocksException(
            "Test error", context={"key1": "value1", "key2": "value2", "key3": "value3"}
        )

        import time

        start_time = time.time()
        for _ in range(100):
            result = exc.to_dict()
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 0.5, (
            f"Exception to_dict too slow: {processing_time:.3f}s"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
