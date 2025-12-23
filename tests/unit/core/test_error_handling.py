"""
错误处理模块测试

测试综合错误处理和恢复机制的核心模块

测试覆盖:
- 错误严重程度和分类枚举
- 可重试和不可重试错误类
- 具体错误类型（数据库、网络、验证等）
- 错误恢复策略（指数退避、线性退避）
- 错误处理器和统计
- 装饰器功能
- 熔断器模式
- 数据框验证和安全执行
"""

import pytest
import asyncio
import time
import pandas as pd
from unittest.mock import patch

from src.core.error_handling import (
    ErrorSeverity,
    ErrorCategory,
    RetryableError,
    NonRetryableError,
    DatabaseConnectionError,
    DatabaseQueryError,
    NetworkTimeoutError,
    ValidationError,
    ResourceExhaustionError,
    ErrorRecoveryStrategy,
    ErrorHandler,
    get_error_handler,
    handle_errors,
    CircuitBreaker,
    validate_dataframe,
    safe_execute,
)


class TestErrorSeverity:
    """错误严重程度枚举测试"""

    def test_severity_values(self):
        """测试严重程度枚举值"""
        assert ErrorSeverity.LOW == "low"
        assert ErrorSeverity.MEDIUM == "medium"
        assert ErrorSeverity.HIGH == "high"
        assert ErrorSeverity.CRITICAL == "critical"

    def test_severity_comparison(self):
        """测试严重程度比较（基于枚举值）"""
        # 枚举值可以比较，基于定义顺序
        assert ErrorSeverity.LOW.value < ErrorSeverity.CRITICAL.value
        assert ErrorSeverity.MEDIUM.value < ErrorSeverity.HIGH.value

    def test_severity_enum_properties(self):
        """测试严重程度枚举属性"""
        low = ErrorSeverity.LOW
        assert low.name == "LOW"
        assert low.value == "low"
        assert isinstance(low.value, str)


class TestErrorCategory:
    """错误分类枚举测试"""

    def test_category_values(self):
        """测试分类枚举值"""
        assert ErrorCategory.DATABASE == "database"
        assert ErrorCategory.NETWORK == "network"
        assert ErrorCategory.VALIDATION == "validation"
        assert ErrorCategory.SYSTEM == "system"
        assert ErrorCategory.BUSINESS == "business"
        assert ErrorCategory.TIMEOUT == "timeout"
        assert ErrorCategory.RESOURCE == "resource"

    def test_category_enum_properties(self):
        """测试分类枚举属性"""
        database = ErrorCategory.DATABASE
        assert database.name == "DATABASE"
        assert database.value == "database"
        assert isinstance(database.value, str)


class TestRetryableError:
    """可重试错误基类测试"""

    def test_retryable_error_basic(self):
        """测试基本可重试错误"""
        error = RetryableError(
            message="Test error",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
        )

        assert str(error) == "Test error"
        assert error.category == ErrorCategory.DATABASE
        assert error.severity == ErrorSeverity.HIGH
        assert error.retry_count == 0

    def test_retryable_error_default_severity(self):
        """测试默认严重程度"""
        error = RetryableError(message="Test error", category=ErrorCategory.NETWORK)

        assert error.severity == ErrorSeverity.MEDIUM

    def test_retryable_error_increases_retry_count(self):
        """测试重试计数增加"""
        error = RetryableError(message="Test error", category=ErrorCategory.DATABASE)

        assert error.retry_count == 0
        error.retry_count += 1
        assert error.retry_count == 1

    def test_retryable_error_is_exception(self):
        """测试是Exception子类"""
        assert issubclass(RetryableError, Exception)
        error = RetryableError("Test", ErrorCategory.DATABASE)
        assert isinstance(error, Exception)


class TestNonRetryableError:
    """不可重试错误基类测试"""

    def test_non_retryable_error_basic(self):
        """测试基本不可重试错误"""
        error = NonRetryableError(
            message="Test error",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
        )

        assert str(error) == "Test error"
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.HIGH

    def test_non_retryable_error_default_severity(self):
        """测试默认严重程度"""
        error = NonRetryableError(message="Test error", category=ErrorCategory.BUSINESS)

        assert error.severity == ErrorSeverity.HIGH

    def test_non_retryable_error_is_exception(self):
        """测试是Exception子类"""
        assert issubclass(NonRetryableError, Exception)
        error = NonRetryableError("Test", ErrorCategory.VALIDATION)
        assert isinstance(error, Exception)


class TestSpecificErrorTypes:
    """具体错误类型测试"""

    def test_database_connection_error(self):
        """测试数据库连接错误"""
        error = DatabaseConnectionError("Connection failed")

        assert str(error) == "Connection failed"
        assert error.category == ErrorCategory.DATABASE
        assert error.severity == ErrorSeverity.HIGH
        assert isinstance(error, RetryableError)

    def test_database_query_error(self):
        """测试数据库查询错误"""
        error = DatabaseQueryError("Query failed")

        assert str(error) == "Query failed"
        assert error.category == ErrorCategory.DATABASE
        assert error.severity == ErrorSeverity.MEDIUM
        assert isinstance(error, RetryableError)

    def test_network_timeout_error(self):
        """测试网络超时错误"""
        error = NetworkTimeoutError("Request timeout")

        assert str(error) == "Request timeout"
        assert error.category == ErrorCategory.TIMEOUT
        assert error.severity == ErrorSeverity.MEDIUM
        assert isinstance(error, RetryableError)

    def test_validation_error(self):
        """测试数据验证错误"""
        error = ValidationError("Invalid data")

        assert str(error) == "Invalid data"
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.MEDIUM
        assert isinstance(error, NonRetryableError)

    def test_resource_exhaustion_error(self):
        """测试资源耗尽错误"""
        error = ResourceExhaustionError("Memory exhausted")

        assert str(error) == "Memory exhausted"
        assert error.category == ErrorCategory.RESOURCE
        assert error.severity == ErrorSeverity.HIGH
        assert isinstance(error, RetryableError)

    def test_all_specific_errors_are_exceptions(self):
        """测试所有具体错误都是异常"""
        assert issubclass(DatabaseConnectionError, Exception)
        assert issubclass(DatabaseQueryError, Exception)
        assert issubclass(NetworkTimeoutError, Exception)
        assert issubclass(ValidationError, Exception)
        assert issubclass(ResourceExhaustionError, Exception)


class TestErrorRecoveryStrategy:
    """错误恢复策略测试"""

    def test_exponential_backoff_basic(self):
        """测试基本指数退避"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(
            base_delay=1.0, max_delay=10.0, backoff_factor=2.0, jitter=False
        )

        assert strategy(0) == 1.0  # 1.0 * 2^0
        assert strategy(1) == 2.0  # 1.0 * 2^1
        assert strategy(2) == 4.0  # 1.0 * 2^2
        assert strategy(3) == 8.0  # 1.0 * 2^3
        assert strategy(4) == 10.0  # 超过最大值

    def test_exponential_backoff_max_delay(self):
        """测试指数退避最大延迟"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(
            base_delay=1.0, max_delay=60.0, backoff_factor=2.0
        )

        # 应该被限制在最大值
        for attempt in range(10):
            delay = strategy(attempt)
            assert delay <= 60.0

    def test_exponential_backoff_with_jitter(self):
        """测试带抖动的指数退避"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(
            base_delay=1.0, max_delay=10.0, backoff_factor=2.0, jitter=True
        )

        # 带抖动时，延迟应该在合理范围内
        for attempt in range(5):
            delay = strategy(attempt)
            expected_base = min(1.0 * (2.0**attempt), 10.0)
            # 抖动应该在50%到150%之间
            assert 0.5 * expected_base <= delay <= 1.5 * expected_base

    def test_linear_backoff_basic(self):
        """测试基本线性退避"""
        strategy = ErrorRecoveryStrategy.linear_backoff(
            base_delay=1.0, increment=0.5, max_delay=5.0
        )

        assert strategy(0) == 1.0  # 1.0 + 0.5 * 0
        assert strategy(1) == 1.5  # 1.0 + 0.5 * 1
        assert strategy(2) == 2.0  # 1.0 + 0.5 * 2
        assert strategy(3) == 2.5  # 1.0 + 0.5 * 3
        assert strategy(4) == 3.0  # 1.0 + 0.5 * 4
        assert strategy(5) == 5.0  # 超过最大值

    def test_linear_backoff_max_delay(self):
        """测试线性退避最大延迟"""
        strategy = ErrorRecoveryStrategy.linear_backoff(
            base_delay=1.0, increment=0.5, max_delay=10.0
        )

        # 应该被限制在最大值
        for attempt in range(20):
            delay = strategy(attempt)
            assert delay <= 10.0


class TestErrorHandler:
    """错误处理器测试"""

    def test_error_handler_initialization(self):
        """测试错误处理器初始化"""
        handler = ErrorHandler()

        assert handler.enable_logging is True
        assert handler.enable_metrics is True
        assert isinstance(handler.error_stats, dict)
        assert len(handler.error_stats) == 0

    def test_error_handler_initialization_with_options(self):
        """测试带选项的错误处理器初始化"""
        handler = ErrorHandler(enable_logging=False, enable_metrics=False)

        assert handler.enable_logging is False
        assert handler.enable_metrics is False

    def test_log_error(self):
        """测试错误日志记录"""
        handler = ErrorHandler()
        error = DatabaseConnectionError("Test connection error")

        # 应该不抛出异常
        handler.log_error(error, context="test_context")

        # 验证错误统计被记录
        assert "DatabaseConnectionError" in handler.error_stats
        stats = handler.error_stats["DatabaseConnectionError"]
        assert stats["count"] == 1
        assert "last_occurrence" in stats

    def test_log_error_multiple_times(self):
        """测试多次记录相同错误"""
        handler = ErrorHandler()
        error = DatabaseConnectionError("Test connection error")

        handler.log_error(error)
        handler.log_error(error)
        handler.log_error(error)

        stats = handler.error_stats["DatabaseConnectionError"]
        assert stats["count"] == 3

    def test_log_different_error_types(self):
        """测试记录不同错误类型"""
        handler = ErrorHandler()
        error1 = DatabaseConnectionError("Connection error")
        error2 = ValidationError("Validation error")

        handler.log_error(error1)
        handler.log_error(error2)

        assert len(handler.error_stats) == 2
        assert "DatabaseConnectionError" in handler.error_stats
        assert "ValidationError" in handler.error_stats

    def test_get_error_stats(self):
        """测试获取错误统计"""
        handler = ErrorHandler()
        error = DatabaseConnectionError("Test error")

        handler.log_error(error)
        stats = handler.get_error_stats()

        assert isinstance(stats, dict)
        assert "DatabaseConnectionError" in stats
        assert stats["DatabaseConnectionError"]["count"] == 1

    def test_get_error_stats_empty(self):
        """测试获取空错误统计"""
        handler = ErrorHandler()
        stats = handler.get_error_stats()

        assert isinstance(stats, dict)
        assert len(stats) == 0

    def test_reset_stats(self):
        """测试重置统计"""
        handler = ErrorHandler()
        error = DatabaseConnectionError("Test error")

        handler.log_error(error)
        assert len(handler.error_stats) == 1

        handler.reset_stats()
        assert len(handler.error_stats) == 0


class TestGlobalErrorHandler:
    """全局错误处理器测试"""

    def test_get_error_handler(self):
        """测试获取全局错误处理器"""
        handler = get_error_handler()

        assert isinstance(handler, ErrorHandler)
        assert handler.enable_logging is True
        assert handler.enable_metrics is True

    def test_get_error_handler_singleton(self):
        """测试全局错误处理器单例"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()

        # 应该返回同一个实例
        assert handler1 is handler2


class TestHandleErrorsDecorator:
    """错误处理装饰器测试"""

    def test_handle_errors_sync_success(self):
        """测试同步函数成功执行"""

        @handle_errors(max_retries=3)
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_handle_errors_sync_retryable_error(self):
        """测试同步函数可重试错误"""
        attempt_count = 0

        @handle_errors(max_retries=3, base_delay=0.1)
        def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise DatabaseConnectionError("Connection failed")
            return "success"

        result = test_function()
        assert result == "success"
        assert attempt_count == 2

    def test_handle_errors_sync_non_retryable_error(self):
        """测试同步函数不可重试错误"""

        @handle_errors(max_retries=3)
        def test_function():
            raise ValidationError("Invalid data")

        with pytest.raises(ValidationError):
            test_function()

    def test_handle_errors_sync_max_retries_exceeded(self):
        """测试同步函数超过最大重试次数"""

        @handle_errors(max_retries=2, base_delay=0.1)
        def test_function():
            raise DatabaseConnectionError("Connection failed")

        with pytest.raises(DatabaseConnectionError) as exc_info:
            test_function()

        assert exc_info.value.retry_count >= 2

    def test_handle_errors_async_success(self):
        """测试异步函数成功执行"""

        @handle_errors(max_retries=3)
        async def test_function():
            return "success"

        result = asyncio.run(test_function())
        assert result == "success"

    def test_handle_errors_async_retryable_error(self):
        """测试异步函数可重试错误"""
        attempt_count = 0

        @handle_errors(max_retries=3, base_delay=0.1)
        async def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise DatabaseConnectionError("Connection failed")
            return "success"

        result = asyncio.run(test_function())
        assert result == "success"
        assert attempt_count == 2

    def test_handle_errors_async_non_retryable_error(self):
        """测试异步函数不可重试错误"""

        @handle_errors(max_retries=3)
        async def test_function():
            raise ValidationError("Invalid data")

        with pytest.raises(ValidationError):
            asyncio.run(test_function())

    def test_handle_errors_with_custom_strategy(self):
        """测试自定义恢复策略"""
        strategy = ErrorRecoveryStrategy.linear_backoff(base_delay=0.1)

        @handle_errors(max_retries=2, delay_strategy=strategy)
        def test_function():
            raise DatabaseConnectionError("Connection failed")

        with pytest.raises(DatabaseConnectionError):
            test_function()

    def test_handle_errors_with_default_return(self):
        """测试默认返回值"""

        @handle_errors(max_retries=1, default_return="fallback")
        def test_function():
            raise ValidationError("Non-retryable error")

        result = test_function()
        assert result == "fallback"


class TestCircuitBreaker:
    """熔断器测试"""

    def test_circuit_breaker_initialization(self):
        """测试熔断器初始化"""
        breaker = CircuitBreaker(
            failure_threshold=3, recovery_timeout=1.0, expected_exception=Exception
        )

        assert breaker.failure_threshold == 3
        assert breaker.recovery_timeout == 1.0
        assert breaker.failure_count == 0
        assert breaker.last_failure_time is None
        assert breaker.state == "CLOSED"

    def test_circuit_breaker_success(self):
        """测试熔断器成功调用"""
        breaker = CircuitBreaker(failure_threshold=3)

        @breaker
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"
        assert breaker.failure_count == 0
        assert breaker.state == "CLOSED"

    def test_circuit_breaker_failure_below_threshold(self):
        """测试熔断器失败但未达到阈值"""
        breaker = CircuitBreaker(failure_threshold=3)

        @breaker
        def test_function():
            raise ValueError("Test error")

        # 第一次失败
        with pytest.raises(ValueError):
            test_function()
        assert breaker.failure_count == 1
        assert breaker.state == "CLOSED"

        # 第二次失败
        with pytest.raises(ValueError):
            test_function()
        assert breaker.failure_count == 2
        assert breaker.state == "CLOSED"

    def test_circuit_breaker_failure_above_threshold(self):
        """测试熔断器失败达到阈值"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        @breaker
        def test_function():
            raise ValueError("Test error")

        # 失败两次达到阈值
        with pytest.raises(ValueError):
            test_function()
        with pytest.raises(ValueError):
            test_function()

        assert breaker.failure_count >= 2
        assert breaker.state == "OPEN"

    def test_circuit_breaker_open_state_blocks_calls(self):
        """测试熔断器开启状态阻止调用"""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        @breaker
        def test_function():
            raise ValueError("Test error")

        # 触发熔断器开启
        with pytest.raises(ValueError):
            test_function()

        assert breaker.state == "OPEN"

        # 熔断器开启时直接返回错误，不调用函数
        with pytest.raises(Exception, match="Circuit breaker is open"):
            test_function()

    def test_circuit_breaker_recovery(self):
        """测试熔断器恢复"""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        call_count = 0

        @breaker
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Test error")
            return "success"

        # 第一次失败触发熔断器
        with pytest.raises(ValueError):
            test_function()
        assert breaker.state == "OPEN"

        # 等待恢复超时
        time.sleep(0.2)

        # 下次调用应该成功并重置熔断器
        result = test_function()
        assert result == "success"
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0

    def test_circuit_breaker_custom_exception_filter(self):
        """测试熔断器自定义异常过滤"""
        breaker = CircuitBreaker(failure_threshold=1, expected_exception=ValueError)

        @breaker
        def test_function():
            raise TypeError("Different error type")

        # 不同类型的异常不应该触发熔断器
        with pytest.raises(TypeError):
            test_function()

        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0


class TestValidateDataFrame:
    """数据框验证测试"""

    def test_validate_dataframe_valid(self):
        """测试有效数据框"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "close": [10.5, 11.0],
                "volume": [1000, 1200],
            }
        )

        # 应该不抛出异常
        validate_dataframe(df, required_columns=["date", "close"])

    def test_validate_dataframe_missing_columns(self):
        """测试缺少必需列"""
        df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "close": [10.5, 11.0]})

        with pytest.raises(ValidationError, match="Missing required columns"):
            validate_dataframe(df, required_columns=["date", "close", "volume"])

    def test_validate_dataframe_empty_dataframe(self):
        """测试空数据框"""
        df = pd.DataFrame()

        with pytest.raises(ValidationError, match="Empty DataFrame"):
            validate_dataframe(df)

    def test_validate_dataframe_with_min_rows(self):
        """测试最小行数验证"""
        df = pd.DataFrame({"col": [1, 2]})  # 只有2行

        with pytest.raises(ValidationError, match="Minimum rows requirement not met"):
            validate_dataframe(df, min_rows=5)

    def test_validate_dataframe_invalid_columns(self):
        """测试无效列数据"""
        df = pd.DataFrame(
            {"date": ["2024-01-01", "invalid_date"], "close": [10.5, "not_a_number"]}
        )

        with pytest.raises(ValidationError):
            validate_dataframe(df)

    def test_validate_dataframe_duplicate_columns(self):
        """测试重复列"""
        df = pd.DataFrame({"col": [1, 2, 3]})
        df.columns = ["col", "col"]  # 创建重复列名

        with pytest.raises(ValidationError, match="Duplicate columns"):
            validate_dataframe(df)


class TestSafeExecute:
    """安全执行测试"""

    def test_safe_execute_success(self):
        """测试成功执行"""

        def test_func(x, y):
            return x + y

        result = safe_execute(test_func, 2, 3)
        assert result == 5

    def test_safe_execute_with_exception(self):
        """测试执行时异常"""

        def test_func():
            raise ValueError("Test error")

        result = safe_execute(test_func)
        assert result is None

    def test_safe_execute_with_default_return(self):
        """测试自定义默认返回值"""

        def test_func():
            raise ValueError("Test error")

        result = safe_execute(test_func, default_return="fallback")
        assert result == "fallback"

    def test_safe_execute_log_errors_true(self):
        """测试记录错误"""

        def test_func():
            raise ValueError("Test error")

        with patch("src.core.error_handling.logger") as mock_logger:
            result = safe_execute(test_func, log_errors=True)
            assert result is None
            # 验证错误被记录
            mock_logger.error.assert_called_once()

    def test_safe_execute_log_errors_false(self):
        """测试不记录错误"""

        def test_func():
            raise ValueError("Test error")

        with patch("src.core.error_handling.logger") as mock_logger:
            result = safe_execute(test_func, log_errors=False)
            assert result is None
            mock_logger.error.assert_not_called()

    def test_safe_execute_with_args_kwargs(self):
        """测试传递参数"""

        def test_func(x, y, z=None):
            return x + y + (z or 0)

        result = safe_execute(test_func, 2, 3, z=4)
        assert result == 9

    def test_safe_execute_nested_function(self):
        """测试嵌套函数调用"""

        def outer_func(x):
            def inner_func(y):
                return x + y

            return safe_execute(inner_func, 5)

        result = outer_func(10)
        assert result == 15


class TestEdgeCases:
    """边界情况测试"""

    def test_extreme_retry_attempts(self):
        """测试极端重试次数"""
        attempt_count = 0

        @handle_errors(max_retries=100, base_delay=0.001)
        def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 5:  # 只失败5次
                raise DatabaseConnectionError("Connection failed")
            return "success"

        result = test_function()
        assert result == "success"
        assert attempt_count == 5

    def test_very_small_delays(self):
        """测试极小延迟"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(
            base_delay=0.001, max_delay=0.01, backoff_factor=2.0
        )

        delay = strategy(1)
        assert 0.001 <= delay <= 0.01

    def test_zero_delay_backoff(self):
        """测试零延迟退避"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(
            base_delay=0.0, max_delay=1.0, backoff_factor=2.0
        )

        delay = strategy(0)
        assert delay == 0.0
        delay = strategy(1)
        assert delay == 0.0

    def test_large_delay_backoff(self):
        """测试大延迟退避"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(
            base_delay=1000.0, max_delay=2000.0, backoff_factor=2.0
        )

        delay = strategy(5)
        assert delay == 2000.0  # 应该被限制在最大值

    def test_error_with_long_message(self):
        """测试长错误消息"""
        long_message = "x" * 10000  # 10KB的错误消息
        error = DatabaseConnectionError(long_message)

        assert len(str(error)) == 10000
        assert error.category == ErrorCategory.DATABASE

    def test_circuit_breaker_zero_threshold(self):
        """测试零阈值的熔断器"""
        breaker = CircuitBreaker(failure_threshold=0)

        @breaker
        def test_function():
            raise ValueError("Test error")

        # 第一次失败就应该开启熔断器
        with pytest.raises(ValueError):
            test_function()
        assert breaker.state == "OPEN"

    def test_circuit_breaker_zero_recovery_timeout(self):
        """测试零恢复超时的熔断器"""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0)

        call_count = 0

        @breaker
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Test error")
            return "success"

        # 触发熔断器
        with pytest.raises(ValueError):
            test_function()

        # 零恢复超时应该立即恢复
        result = test_function()
        assert result == "success"
        assert breaker.state == "CLOSED"


class TestPerformance:
    """性能测试"""

    def test_error_handler_performance(self):
        """测试错误处理器性能"""
        handler = ErrorHandler()
        error = DatabaseConnectionError("Test error")

        import time

        start_time = time.time()

        # 记录1000个错误
        for _ in range(1000):
            handler.log_error(error)

        end_time = time.time()
        duration = end_time - start_time

        # 应该在合理时间内完成
        assert duration < 2.0
        assert handler.error_stats["DatabaseConnectionError"]["count"] == 1000

    def test_decorator_performance(self):
        """测试装饰器性能"""

        @handle_errors(max_retries=0)
        def test_function():
            return "success"

        import time

        start_time = time.time()

        # 调用1000次装饰的函数
        for _ in range(1000):
            test_function()

        end_time = time.time()
        duration = end_time - start_time

        # 应该在合理时间内完成
        assert duration < 1.0

    def test_circuit_breaker_performance(self):
        """测试熔断器性能"""
        breaker = CircuitBreaker(failure_threshold=1000)

        @breaker
        def test_function():
            return "success"

        import time

        start_time = time.time()

        # 调用1000次熔断器保护的函数
        for _ in range(1000):
            test_function()

        end_time = time.time()
        duration = end_time - start_time

        # 应该在合理时间内完成
        assert duration < 1.0
        assert breaker.failure_count == 0
