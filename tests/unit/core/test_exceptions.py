"""
异常模块单元测试

测试MyStocks系统中所有自定义异常类型
"""

import pytest
import sys

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.exceptions import (
    # 基础异常
    MyStocksException,
    # 数据相关异常
    DataException,
    DataNotFoundException,
    DataValidationError,
    DataIntegrityException,
    DataQualityException,
    # 数据库相关异常
    DatabaseException,
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseIntegrityError,
    # 配置相关异常
    ConfigException,
    ConfigFileNotFound,
    ConfigValueError,
    ConfigValidationFailed,
    # 网络相关异常
    NetworkException,
    NetworkConnectionError,
    NetworkTimeoutError,
    HTTPError,
    # 安全相关异常
    SecurityException,
    AuthenticationError,
    AuthorizationError,
    DataAccessError,
    # 处理相关异常
    BatchProcessingError,
    DataFormatError,
    ValidationException,
    # 业务逻辑异常
    TradingRuleViolation,
    RiskControlException,
    UnsupportedOperation,
    # 装饰器
    handle_exceptions,
)


class TestMyStocksException:
    """测试基础异常类"""

    def test_basic_exception_creation(self):
        """测试创建基础异常"""
        exc = MyStocksException("Test error")
        assert exc.message == "Test error"
        assert exc.error_code == "MSE0001"
        assert exc.details == {}
        assert exc.timestamp is not None

    def test_exception_with_error_code(self):
        """测试带错误码的异常"""
        exc = MyStocksException("Test error", error_code="CUSTOM001")
        assert exc.error_code == "CUSTOM001"

    def test_exception_with_details(self):
        """测试带详细信息的异常"""
        details = {"key": "value", "count": 42}
        exc = MyStocksException("Test error", details=details)
        assert exc.details == details

    def test_exception_str_representation(self):
        """测试异常字符串表示"""
        exc = MyStocksException(
            "Test error", error_code="TEST001", details={"info": "test"}
        )
        str_repr = str(exc)
        assert "TEST001" in str_repr
        assert "Test error" in str_repr
        assert "info" in str_repr

    def test_exception_timestamp_format(self):
        """测试时间戳格式"""
        exc = MyStocksException("Test error")
        # 时间戳应该是ISO格式
        assert "T" in exc.timestamp
        assert len(exc.timestamp) > 10


class TestDataExceptions:
    """测试数据相关异常"""

    def test_data_not_found_exception(self):
        """测试数据未找到异常"""
        exc = DataNotFoundException(
            "Stock not found", symbol="000001", data_type="daily_kline"
        )
        assert exc.error_code == "MSE1001"
        assert exc.details["symbol"] == "000001"
        assert exc.details["data_type"] == "daily_kline"
        assert isinstance(exc, DataException)
        assert isinstance(exc, MyStocksException)

    def test_data_validation_error(self):
        """测试数据验证异常"""
        validation_errors = ["price < 0", "volume missing"]
        exc = DataValidationError(
            "Validation failed", validation_errors=validation_errors
        )
        assert exc.error_code == "MSE1002"
        assert exc.details["validation_errors"] == validation_errors

    def test_data_integrity_exception(self):
        """测试数据完整性异常"""
        exc = DataIntegrityException(
            "Duplicate record", table_name="stock_daily", record_id="123"
        )
        assert exc.error_code == "MSE1003"
        assert exc.details["table_name"] == "stock_daily"
        assert exc.details["record_id"] == "123"

    def test_data_quality_exception(self):
        """测试数据质量异常"""
        quality_issues = ["missing_rate > 10%", "outlier detected"]
        exc = DataQualityException("Poor data quality", quality_issues=quality_issues)
        assert exc.error_code == "MSE1004"
        assert exc.details["quality_issues"] == quality_issues


class TestDatabaseExceptions:
    """测试数据库相关异常"""

    def test_database_connection_error(self):
        """测试数据库连接异常"""
        conn_info = {"host": "localhost", "port": 5432}
        exc = DatabaseConnectionError(
            "Connection failed", db_type="PostgreSQL", connection_info=conn_info
        )
        assert exc.error_code == "MSE2001"
        assert exc.details["db_type"] == "PostgreSQL"
        assert exc.details["connection_info"] == conn_info

    def test_database_query_error(self):
        """测试数据库查询异常"""
        query = "SELECT * FROM stocks WHERE symbol = ?"
        params = {"symbol": "000001"}
        exc = DatabaseQueryError("Query failed", query=query, params=params)
        assert exc.error_code == "MSE2002"
        assert exc.details["query"] == query
        assert exc.details["params"] == params

    def test_database_integrity_error(self):
        """测试数据库完整性异常"""
        exc = DatabaseIntegrityError(
            "Foreign key violation", constraint="fk_stock_symbol", table="orders"
        )
        assert exc.error_code == "MSE2003"
        assert exc.details["constraint"] == "fk_stock_symbol"
        assert exc.details["table"] == "orders"


class TestConfigExceptions:
    """测试配置相关异常"""

    def test_config_file_not_found(self):
        """测试配置文件未找到异常"""
        exc = ConfigFileNotFound("/path/to/config.yaml")
        assert exc.error_code == "MSE3001"
        assert "/path/to/config.yaml" in exc.message
        assert exc.details["file_path"] == "/path/to/config.yaml"

    def test_config_value_error(self):
        """测试配置值错误异常"""
        exc = ConfigValueError("timeout", "invalid", expected_type="int")
        assert exc.error_code == "MSE3002"
        assert exc.details["key"] == "timeout"
        assert exc.details["value"] == "invalid"
        assert exc.details["expected_type"] == "int"

    def test_config_validation_failed(self):
        """测试配置验证失败异常"""
        validation_errors = ["Missing required field: host", "Invalid port range"]
        exc = ConfigValidationFailed(validation_errors)
        assert exc.error_code == "MSE3003"
        assert exc.details["validation_errors"] == validation_errors


class TestNetworkExceptions:
    """测试网络相关异常"""

    def test_network_connection_error(self):
        """测试网络连接异常"""
        exc = NetworkConnectionError(
            "Failed to connect", url="http://example.com", timeout=30.0
        )
        assert exc.error_code == "MSE4001"
        assert exc.details["url"] == "http://example.com"
        assert exc.details["timeout"] == 30.0

    def test_network_timeout_error(self):
        """测试网络超时异常"""
        exc = NetworkTimeoutError(
            "Request timeout", timeout=10.0, url="http://api.example.com"
        )
        assert exc.error_code == "MSE4002"
        assert exc.details["timeout"] == 10.0
        assert exc.details["url"] == "http://api.example.com"

    def test_http_error(self):
        """测试HTTP错误异常"""
        exc = HTTPError(
            404,
            "Not Found",
            url="http://example.com/api/data",
            response="Page not found",
        )
        assert exc.error_code == "MSE4003"
        assert "404" in exc.message
        assert exc.details["status_code"] == 404
        assert exc.details["url"] == "http://example.com/api/data"


class TestSecurityExceptions:
    """测试安全相关异常"""

    def test_authentication_error(self):
        """测试认证错误异常"""
        exc = AuthenticationError("Invalid credentials", user_id="user123")
        assert exc.error_code == "MSE5001"
        assert exc.details["user_id"] == "user123"

    def test_authorization_error(self):
        """测试授权错误异常"""
        exc = AuthorizationError(
            "Access denied", user_id="user123", resource="/admin/settings"
        )
        assert exc.error_code == "MSE5002"
        assert exc.details["user_id"] == "user123"
        assert exc.details["resource"] == "/admin/settings"

    def test_data_access_error(self):
        """测试数据访问错误异常"""
        exc = DataAccessError(
            "Permission denied", user_id="user123", table_name="sensitive_data"
        )
        assert exc.error_code == "MSE5003"
        assert exc.details["user_id"] == "user123"
        assert exc.details["table_name"] == "sensitive_data"


class TestProcessingExceptions:
    """测试处理相关异常"""

    def test_batch_processing_error(self):
        """测试批量处理错误异常"""
        failed_records = [{"id": 1}, {"id": 2}]
        exc = BatchProcessingError(
            "Batch failed", failed_records=failed_records, total_records=100
        )
        assert exc.error_code == "MSE6001"
        assert exc.details["failed_records"] == failed_records
        assert exc.details["total_records"] == 100

    def test_data_format_error(self):
        """测试数据格式错误异常"""
        exc = DataFormatError(
            "Invalid format", expected_format="JSON", actual_format="XML"
        )
        assert exc.error_code == "MSE6002"
        assert exc.details["expected_format"] == "JSON"
        assert exc.details["actual_format"] == "XML"

    def test_validation_exception(self):
        """测试验证错误异常"""
        exc = ValidationException(
            "Invalid value", field="price", value=-10, validation_rule="price >= 0"
        )
        assert exc.error_code == "MSE6003"
        assert exc.details["field"] == "price"
        assert exc.details["value"] == -10
        assert exc.details["validation_rule"] == "price >= 0"


class TestBusinessLogicExceptions:
    """测试业务逻辑异常"""

    def test_trading_rule_violation(self):
        """测试交易规则违反异常"""
        context = {"order_size": 10000, "max_allowed": 5000}
        exc = TradingRuleViolation(
            "Order too large", rule="max_order_size", context=context
        )
        assert exc.error_code == "MSE7001"
        assert exc.details["rule"] == "max_order_size"
        assert exc.details["context"] == context

    def test_risk_control_exception(self):
        """测试风控相关异常"""
        risk_factors = ["high_volatility", "large_position"]
        exc = RiskControlException(
            "Risk limit exceeded", risk_level="HIGH", risk_factors=risk_factors
        )
        assert exc.error_code == "MSE7002"
        assert exc.details["risk_level"] == "HIGH"
        assert exc.details["risk_factors"] == risk_factors

    def test_unsupported_operation(self):
        """测试不支持的操作异常"""
        exc = UnsupportedOperation("short_selling", reason="Market closed")
        assert exc.error_code == "MSE7003"
        assert "short_selling" in exc.message
        assert exc.details["operation"] == "short_selling"
        assert exc.details["reason"] == "Market closed"


class TestExceptionHierarchy:
    """测试异常继承层次"""

    def test_data_exception_hierarchy(self):
        """测试数据异常继承层次"""
        exc = DataNotFoundException("Test")
        assert isinstance(exc, DataNotFoundException)
        assert isinstance(exc, DataException)
        assert isinstance(exc, MyStocksException)
        assert isinstance(exc, Exception)

    def test_database_exception_hierarchy(self):
        """测试数据库异常继承层次"""
        exc = DatabaseConnectionError("Test")
        assert isinstance(exc, DatabaseConnectionError)
        assert isinstance(exc, DatabaseException)
        assert isinstance(exc, MyStocksException)

    def test_config_exception_hierarchy(self):
        """测试配置异常继承层次"""
        exc = ConfigFileNotFound("/path/to/file")
        assert isinstance(exc, ConfigFileNotFound)
        assert isinstance(exc, ConfigException)
        assert isinstance(exc, MyStocksException)

    def test_network_exception_hierarchy(self):
        """测试网络异常继承层次"""
        exc = HTTPError(404, "Not Found")
        assert isinstance(exc, HTTPError)
        assert isinstance(exc, NetworkException)
        assert isinstance(exc, MyStocksException)

    def test_security_exception_hierarchy(self):
        """测试安全异常继承层次"""
        exc = AuthenticationError("Test")
        assert isinstance(exc, AuthenticationError)
        assert isinstance(exc, SecurityException)
        assert isinstance(exc, MyStocksException)


class TestExceptionDecorator:
    """测试异常处理装饰器"""

    def test_handle_exceptions_with_default_return(self):
        """测试装饰器默认返回值"""

        @handle_exceptions(default_return="default_value")
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        assert result == "default_value"

    def test_handle_exceptions_with_reraise(self):
        """测试装饰器重新抛出异常"""

        @handle_exceptions(reraise=True)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

    def test_handle_exceptions_with_custom_exception(self):
        """测试装饰器处理自定义异常"""

        @handle_exceptions(default_return=None)
        def failing_with_custom_exception():
            raise MyStocksException("Custom error")

        # MyStocks自定义异常应该被直接抛出
        with pytest.raises(MyStocksException):
            failing_with_custom_exception()

    def test_handle_exceptions_success(self):
        """测试装饰器在成功情况下"""

        @handle_exceptions(default_return="default")
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_exceptions_with_logger(self):
        """测试装饰器带日志记录"""
        from unittest.mock import Mock

        mock_logger = Mock()

        @handle_exceptions(default_return=None, logger=mock_logger)
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()

        assert result is None
        # 验证日志记录器被调用
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "failing_function" in call_args[0][0]


class TestExceptionDefaultValues:
    """测试异常默认值处理"""

    def test_exception_with_none_details(self):
        """测试None详细信息"""
        exc = DataNotFoundException("Test")
        assert exc.details["symbol"] is None
        assert exc.details["data_type"] is None

    def test_batch_processing_error_empty_list(self):
        """测试批量处理错误空列表"""
        exc = BatchProcessingError("Test")
        assert exc.details["failed_records"] == []
        assert exc.details["total_records"] is None

    def test_config_value_error_no_expected_type(self):
        """测试配置值错误无期望类型"""
        exc = ConfigValueError("key", "value")
        assert exc.details["expected_type"] is None


class TestExceptionMessageFormat:
    """测试异常消息格式"""

    def test_config_file_not_found_message(self):
        """测试配置文件未找到消息"""
        exc = ConfigFileNotFound("/path/to/config.yaml")
        assert "配置文件未找到" in exc.message
        assert "/path/to/config.yaml" in exc.message

    def test_http_error_message(self):
        """测试HTTP错误消息"""
        exc = HTTPError(404, "Not Found", url="http://example.com")
        assert "404" in exc.message
        assert "Not Found" in exc.message

    def test_unsupported_operation_message(self):
        """测试不支持操作消息"""
        exc = UnsupportedOperation("test_operation", reason="not implemented")
        assert "不支持的操作" in exc.message
        assert "test_operation" in exc.message
