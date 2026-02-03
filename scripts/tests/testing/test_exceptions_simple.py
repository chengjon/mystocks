#!/usr/bin/env python3
"""
Exceptions 简化但有效的Phase 6测试套件
专注于核心异常功能测试，避免导入复杂性
目标：将exceptions.py的覆盖率从初始状态提升到90%+
"""

import sys
import time
from pathlib import Path
import pytest
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestMyStocksExceptionCore:
    """测试MyStocksException核心功能"""

    def test_basic_functionality(self):
        """测试基本功能"""
        from src.core.exceptions import MyStocksException

        # 基本初始化
        exc = MyStocksException("Test message")
        assert exc.message == "Test message"
        assert exc.code == "UNKNOWN_ERROR"
        assert exc.severity == "HIGH"
        assert isinstance(exc.timestamp, datetime)

        # 完整初始化
        context = {"key": "value", "number": 42}
        exc = MyStocksException(
            message="Detailed error",
            code="CUSTOM_CODE",
            severity="MEDIUM",
            context=context,
        )
        assert exc.message == "Detailed error"
        assert exc.code == "CUSTOM_CODE"
        assert exc.severity == "MEDIUM"
        assert exc.context == context

    def test_message_formatting(self):
        """测试消息格式化"""
        from src.core.exceptions import MyStocksException

        # 无上下文
        exc = MyStocksException("Simple message")
        formatted = str(exc)
        assert "[UNKNOWN_ERROR] Simple message" in formatted

        # 有上下文
        exc = MyStocksException("Complex message", context={"field": "value"})
        formatted = str(exc)
        assert "Complex message" in formatted
        assert "field=value" in formatted

    def test_serialization(self):
        """测试序列化功能"""
        from src.core.exceptions import MyStocksException

        context = {"test": "data", "number": 123}
        exc = MyStocksException("Serialization test", context=context)

        result = exc.to_dict()
        assert result["type"] == "MyStocksException"
        assert result["message"] == "Serialization test"
        assert result["code"] == "UNKNOWN_ERROR"
        assert result["context"] == context
        assert "timestamp" in result

    def test_original_exception_handling(self):
        """测试原始异常处理"""
        from src.core.exceptions import MyStocksException

        try:
            raise ValueError("Original error")
        except ValueError as original:
            exc = MyStocksException("Wrapped error", original_exception=original)

            assert exc.original_exception == original
            assert "Original error" in exc.context["original_error"]


class TestDataSourceExceptions:
    """测试数据源异常"""

    def test_data_source_hierarchy(self):
        """测试数据源异常层次结构"""
        from src.core.exceptions import (
            DataSourceException,
            NetworkError,
            DataFetchError,
            DataParseError,
            DataValidationError,
        )

        # 测试基类
        base_exc = DataSourceException("Base error")
        assert isinstance(base_exc, MyStocksException)
        assert base_exc.code == "DATA_SOURCE_ERROR"

        # 测试子类
        network_exc = NetworkError("Network failed")
        assert isinstance(network_exc, DataSourceException)
        assert network_exc.code == "NETWORK_ERROR"
        assert network_exc.severity == "HIGH"

        fetch_exc = DataFetchError("Fetch failed")
        assert isinstance(fetch_exc, DataSourceException)
        assert fetch_exc.code == "DATA_FETCH_FAILED"

        parse_exc = DataParseError("Parse failed")
        assert isinstance(parse_exc, DataSourceException)
        assert parse_exc.code == "DATA_PARSE_ERROR"
        assert parse_exc.severity == "MEDIUM"

        validation_exc = DataValidationError("Validation failed")
        assert isinstance(validation_exc, DataSourceException)
        assert validation_exc.code == "DATA_VALIDATION_ERROR"
        assert validation_exc.severity == "MEDIUM"


class TestDatabaseExceptions:
    """测试数据库异常"""

    def test_database_hierarchy(self):
        """测试数据库异常层次结构"""
        from src.core.exceptions import (
            DatabaseException,
            DatabaseConnectionError,
            DatabaseOperationError,
            DatabaseIntegrityError,
        )

        # 测试基类
        base_exc = DatabaseException("Database error")
        assert isinstance(base_exc, MyStocksException)

        # 测试子类
        conn_exc = DatabaseConnectionError("Connection failed")
        assert isinstance(conn_exc, DatabaseException)
        assert conn_exc.code == "DB_CONNECTION_ERROR"
        assert conn_exc.severity == "CRITICAL"

        op_exc = DatabaseOperationError("Operation failed")
        assert isinstance(op_exc, DatabaseException)
        assert op_exc.code == "DB_OPERATION_ERROR"

        integrity_exc = DatabaseIntegrityError("Integrity violation")
        assert isinstance(integrity_exc, DatabaseException)
        assert integrity_exc.code == "DB_INTEGRITY_ERROR"


class TestValidationExceptions:
    """测试验证异常"""

    def test_validation_hierarchy(self):
        """测试验证异常层次结构"""
        from src.core.exceptions import (
            ValidationException,
            SchemaValidationError,
            DataTypeError,
            RangeError,
            RequiredFieldError,
        )

        # 测试基类
        base_exc = ValidationException("Validation error")
        assert isinstance(base_exc, MyStocksException)

        # 测试子类
        schema_exc = SchemaValidationError("Schema error")
        assert isinstance(schema_exc, ValidationException)
        assert schema_exc.code == "SCHEMA_VALIDATION_ERROR"

        type_exc = DataTypeError("Type error")
        assert isinstance(type_exc, ValidationException)
        assert type_exc.code == "DATA_TYPE_ERROR"

        range_exc = RangeError("Range error")
        assert isinstance(range_exc, ValidationException)
        assert range_exc.code == "RANGE_ERROR"

        field_exc = RequiredFieldError("Field missing")
        assert isinstance(field_exc, ValidationException)
        assert field_exc.code == "REQUIRED_FIELD_ERROR"


class TestBusinessLogicExceptions:
    """测试业务逻辑异常"""

    def test_business_logic_hierarchy(self):
        """测试业务逻辑异常层次结构"""
        from src.core.exceptions import (
            BusinessLogicException,
            InsufficientFundsError,
            InvalidStrategyError,
            BacktestError,
        )

        # 测试基类
        base_exc = BusinessLogicException("Business error")
        assert isinstance(base_exc, MyStocksException)

        # 测试子类
        funds_exc = InsufficientFundsError("No funds")
        assert isinstance(funds_exc, BusinessLogicException)
        assert funds_exc.code == "INSUFFICIENT_FUNDS"

        strategy_exc = InvalidStrategyError("Invalid strategy")
        assert isinstance(strategy_exc, BusinessLogicException)
        assert strategy_exc.code == "INVALID_STRATEGY"

        backtest_exc = BacktestError("Backtest failed")
        assert isinstance(backtest_exc, BusinessLogicException)
        assert backtest_exc.code == "BACKTEST_ERROR"


class TestAuthenticationExceptions:
    """测试认证异常"""

    def test_authentication_hierarchy(self):
        """测试认证异常层次结构"""
        from src.core.exceptions import (
            AuthenticationException,
            InvalidCredentialsError,
            TokenExpiredError,
            UnauthorizedAccessError,
        )

        # 测试基类
        base_exc = AuthenticationException("Auth error")
        assert isinstance(base_exc, MyStocksException)

        # 测试子类
        creds_exc = InvalidCredentialsError("Invalid credentials")
        assert isinstance(creds_exc, AuthenticationException)
        assert creds_exc.code == "INVALID_CREDENTIALS"

        token_exc = TokenExpiredError("Token expired")
        assert isinstance(token_exc, AuthenticationException)
        assert token_exc.code == "TOKEN_EXPIRED"

        access_exc = UnauthorizedAccessError("Unauthorized")
        assert isinstance(access_exc, AuthenticationException)
        assert access_exc.code == "UNAUTHORIZED_ACCESS"


class TestTimeoutExceptions:
    """测试超时异常"""

    def test_timeout_hierarchy(self):
        """测试超时异常层次结构"""
        from src.core.exceptions import (
            TimeoutException,
            NetworkTimeoutError,
            DatabaseTimeoutError,
            OperationTimeoutError,
        )

        # 测试基类
        base_exc = TimeoutException("Timeout")
        assert isinstance(base_exc, MyStocksException)

        # 测试子类
        net_exc = NetworkTimeoutError("Network timeout")
        assert isinstance(net_exc, TimeoutException)
        assert net_exc.code == "NETWORK_TIMEOUT"

        db_exc = DatabaseTimeoutError("DB timeout")
        assert isinstance(db_exc, TimeoutException)
        assert db_exc.code == "DB_TIMEOUT"

        op_exc = OperationTimeoutError("Operation timeout")
        assert isinstance(op_exc, TimeoutException)
        assert op_exc.code == "OPERATION_TIMEOUT"


class TestExternalServiceExceptions:
    """测试外部服务异常"""

    def test_external_service_hierarchy(self):
        """测试外部服务异常层次结构"""
        from src.core.exceptions import (
            ExternalServiceException,
            ServiceUnavailableError,
            ServiceError,
            RateLimitError,
        )

        # 测试基类
        base_exc = ExternalServiceException("Service error")
        assert isinstance(base_exc, MyStocksException)

        # 测试子类
        unavailable_exc = ServiceUnavailableError("Service down")
        assert isinstance(unavailable_exc, ExternalServiceException)
        assert unavailable_exc.code == "SERVICE_UNAVAILABLE"

        service_exc = ServiceError("Service error")
        assert isinstance(service_exc, ExternalServiceException)
        assert service_exc.code == "SERVICE_ERROR"

        rate_exc = RateLimitError("Rate limit")
        assert isinstance(rate_exc, ExternalServiceException)
        assert rate_exc.code == "RATE_LIMIT_ERROR"


class TestExceptionScenarios:
    """测试异常使用场景"""

    def test_nested_exception_chain(self):
        """测试嵌套异常链"""
        from src.core.exceptions import DataFetchError

        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise DataFetchError("Failed to fetch", original_exception=e)
        except DataFetchError as e:
            assert isinstance(e, MyStocksException)
            assert e.original_exception.__class__.__name__ == "ValueError"

    def test_exception_with_rich_context(self):
        """测试带丰富上下文的异常"""
        from src.core.exceptions import DataValidationError

        context = {
            "symbol": "000001",
            "date_range": "2024-01-01:2024-01-31",
            "validation_rules": ["price_range", "volume_check"],
        }

        exc = DataValidationError("Validation failed", context=context)

        result = exc.to_dict()
        assert result["context"] == context

        formatted = str(exc)
        for key, value in context.items():
            assert f"{key}={value}" in formatted

    def test_exception_performance(self):
        """测试异常处理性能"""
        from src.core.exceptions import MyStocksException

        # 测试大量异常创建性能
        start_time = time.time()
        exceptions = []

        for i in range(1000):
            exc = MyStocksException(f"Error {i}", context={"index": i})
            exceptions.append(exc)

        creation_time = time.time() - start_time

        # 验证性能要求
        assert creation_time < 2.0  # 1000个异常在2秒内创建
        assert len(exceptions) == 1000

        # 测试序列化性能
        start_time = time.time()
        for exc in exceptions[:100]:  # 测试前100个
            data = exc.to_dict()
            assert data["message"] == f"Error {exceptions.index(exc)}"

        serialization_time = time.time() - start_time
        assert serialization_time < 0.5  # 100个序列化在0.5秒内完成


class TestExceptionEdgeCases:
    """测试异常边界情况"""

    def test_none_values_handling(self):
        """测试None值处理"""
        from src.core.exceptions import MyStocksException

        exc = MyStocksException("Test", context=None)
        assert exc.context == {}

    def test_empty_context(self):
        """测试空上下文"""
        from src.core.exceptions import MyStocksException

        exc = MyStocksException("Test", context={})
        assert exc.context == {}

        formatted = str(exc)
        assert "Context:" not in formatted

    def test_exception_repr(self):
        """测试异常repr"""
        from src.core.exceptions import MyStocksException

        exc = MyStocksException("Test", code="TEST_CODE", severity="LOW")
        result = repr(exc)

        assert "MyStocksException" in result
        assert "TEST_CODE" in result
        assert "LOW" in result

    def test_all_severity_levels(self):
        """测试所有严重级别"""
        from src.core.exceptions import MyStocksException

        levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

        for level in levels:
            exc = MyStocksException("Test", severity=level)
            assert exc.severity == level


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
