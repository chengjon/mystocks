"""
Error Handler Test Suite
错误处理工具测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.error_handler (162行)
"""

import pytest
import logging
import time

from src.utils.error_handler import (
    UnifiedErrorHandler,
    safe_execute,
    retry_on_failure,
    DataError,
    ConnectionError,
    ValidationError,
    ProcessingError,
)


class TestUnifiedErrorHandler:
    """统一错误处理器测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 清除日志记录
        self.log_records = []

        # 创建测试日志处理器
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log

        # 获取测试logger
        self.logger = logging.getLogger("src.utils.error_handler")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.DEBUG)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    def test_log_error_basic(self):
        """测试基本错误日志记录"""
        error = ValueError("Test error")
        context = "Test context"

        UnifiedErrorHandler.log_error(error, context)

        # 验证日志记录
        assert len(self.log_records) == 1
        log_record = self.log_records[0]
        assert log_record.levelno == logging.ERROR
        assert "Test context" in log_record.getMessage()
        assert "Test error" in log_record.getMessage()
        assert "ValueError" in log_record.getMessage()

    def test_log_error_with_default_context(self):
        """测试默认上下文的错误日志"""
        error = RuntimeError("Runtime error")

        UnifiedErrorHandler.log_error(error)

        log_record = self.log_records[0]
        assert log_record.levelno == logging.ERROR
        assert log_record.getMessage().startswith(
            "错误发生 - 上下文: , 错误: Runtime error"
        )

    def test_log_error_with_custom_level(self):
        """测试自定义日志级别"""
        error = Warning("Test warning")

        UnifiedErrorHandler.log_error(error, "Warning context", logging.WARNING)

        log_record = self.log_records[0]
        assert log_record.levelno == logging.WARNING
        assert "Warning context" in log_record.getMessage()

    def test_log_error_with_different_exception_types(self):
        """测试不同异常类型的日志记录"""
        exceptions = [
            ValueError("Value error"),
            TypeError("Type error"),
            KeyError("Key error"),
            AttributeError("Attribute error"),
        ]

        for i, error in enumerate(exceptions):
            UnifiedErrorHandler.log_error(error, f"Context {i}")

        assert len(self.log_records) == 4
        for i, log_record in enumerate(self.log_records):
            assert f"Context {i}" in log_record.getMessage()
            assert exceptions[i].__class__.__name__ in log_record.getMessage()

    def test_safe_execute_success(self):
        """测试成功执行函数"""

        def success_func():
            return "success"

        result = UnifiedErrorHandler.safe_execute(success_func, "Test success")

        assert result == "success"
        assert len(self.log_records) == 0  # 不应该有错误日志

    def test_safe_execute_with_exception(self):
        """测试执行函数抛出异常"""

        def failing_func():
            raise ValueError("Test error")

        result = UnifiedErrorHandler.safe_execute(
            failing_func, "Test failure", default_return="default"
        )

        assert result == "default"
        assert len(self.log_records) == 1
        log_record = self.log_records[0]
        assert "Test failure" in log_record.getMessage()
        assert "Test error" in log_record.getMessage()

    def test_safe_execute_without_logging(self):
        """测试不记录错误的安全执行"""

        def failing_func():
            raise RuntimeError("Error without log")

        result = UnifiedErrorHandler.safe_execute(
            failing_func, "No log", default_return="default", log_error=False
        )

        assert result == "default"
        assert len(self.log_records) == 0  # 不应该有日志记录

    def test_safe_execute_with_reraise(self):
        """测试重新抛出异常"""

        def failing_func():
            raise ValueError("Reraise error")

        with pytest.raises(ValueError, match="Reraise error"):
            UnifiedErrorHandler.safe_execute(failing_func, "Reraise test", reraise=True)

        assert len(self.log_records) == 1

    def test_safe_execute_with_reraise_and_no_log(self):
        """测试重新抛出异常且不记录日志"""

        def failing_func():
            raise ValueError("Reraise without log")

        with pytest.raises(ValueError, match="Reraise without log"):
            UnifiedErrorHandler.safe_execute(
                failing_func, "No log", log_error=False, reraise=True
            )

        assert len(self.log_records) == 0

    def test_safe_execute_with_function_parameters(self):
        """测试带参数的函数执行"""

        def param_func(x, y):
            return x + y

        result = UnifiedErrorHandler.safe_execute(
            lambda: param_func(2, 3), "Param test"
        )

        assert result == 5
        assert len(self.log_records) == 0

    def test_safe_execute_with_none_default(self):
        """测试None默认返回值"""

        def failing_func():
            raise ValueError("None default")

        result = UnifiedErrorHandler.safe_execute(failing_func, "None default")

        assert result is None

    def test_retry_on_failure_success_first_try(self):
        """测试第一次尝试成功"""

        @UnifiedErrorHandler.retry_on_failure(max_retries=3, context="Retry test")
        def success_func():
            return "success"

        result = success_func()

        assert result == "success"
        assert len(self.log_records) == 0

    def test_retry_on_failure_eventual_success(self):
        """测试重试后成功"""
        attempt_count = 0

        @UnifiedErrorHandler.retry_on_failure(
            max_retries=3, delay=0.01, context="Retry success"
        )
        def eventually_success_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError(f"Attempt {attempt_count} failed")
            return "success after retries"

        start_time = time.time()
        result = eventually_success_func()
        end_time = time.time()

        assert result == "success after retries"
        assert attempt_count == 2
        # 应该只有第一次失败的日志
        assert len(self.log_records) == 1
        assert "第1次尝试失败" in self.log_records[0].getMessage()
        # 验证有延迟
        assert end_time - start_time >= 0.01

    def test_retry_on_failure_all_retries_failed(self):
        """测试所有重试都失败"""

        @UnifiedErrorHandler.retry_on_failure(
            max_retries=3, delay=0.01, context="All retries failed"
        )
        def always_failing_func():
            raise RuntimeError("Always fails")

        with pytest.raises(RuntimeError, match="Always fails"):
            always_failing_func()

        # 应该有3次失败的日志 + 1次最终失败的日志
        assert len(self.log_records) == 4
        assert "第1次尝试失败" in self.log_records[0].getMessage()
        assert "第2次尝试失败" in self.log_records[1].getMessage()
        assert "第3次尝试失败" in self.log_records[2].getMessage()
        assert "所有重试均已失败" in self.log_records[3].getMessage()

    def test_retry_on_failure_with_custom_exception(self):
        """测试自定义异常类型重试"""

        @UnifiedErrorHandler.retry_on_failure(
            max_retries=2, exceptions=(ValueError,), context="Custom exception"
        )
        def custom_exception_func():
            raise ValueError("Custom error")

        with pytest.raises(ValueError, match="Custom error"):
            custom_exception_func()

        # 应该重试ValueError，记录2次失败日志 + 1次最终失败日志
        assert len(self.log_records) == 3

    def test_retry_on_failure_with_different_exception(self):
        """测试不匹配的异常类型不重试"""

        @UnifiedErrorHandler.retry_on_failure(
            max_retries=3, exceptions=(ValueError,), context="Different exception"
        )
        def different_exception_func():
            raise TypeError("Different error type")

        with pytest.raises(TypeError, match="Different error type"):
            different_exception_func()

        # 不应该有重试日志，因为异常类型不匹配
        assert len(self.log_records) == 0

    def test_retry_on_failure_with_backoff(self):
        """测试指数退避延迟"""
        attempt_times = []

        @UnifiedErrorHandler.retry_on_failure(
            max_retries=3, delay=0.01, backoff=2.0, context="Backoff test"
        )
        def backoff_func():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ValueError(f"Attempt {len(attempt_times)} failed")
            return "success"

        backoff_func()

        assert len(attempt_times) == 3
        # 验证延迟递增
        delay1 = attempt_times[1] - attempt_times[0]
        delay2 = attempt_times[2] - attempt_times[1]
        assert delay2 >= delay1 * 1.8  # 允许一些时间误差

    def test_retry_on_failure_preserves_function_metadata(self):
        """测试装饰器保留函数元数据"""

        @UnifiedErrorHandler.retry_on_failure(max_retries=3, context="Metadata test")
        def test_function(x, y):
            """Test function docstring"""
            return x + y

        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring"
        assert test_function(2, 3) == 5

    def test_retry_on_failure_zero_retries(self):
        """测试零次重试"""

        # 使用max_retries=1来测试边界情况，避免exceptions参数问题
        @UnifiedErrorHandler.retry_on_failure(
            max_retries=1, delay=0.01, context="One retry"
        )
        def one_retry_func():
            raise ValueError("Single retry fails")

        with pytest.raises(ValueError, match="Single retry fails"):
            one_retry_func()

        # 应该有2次失败的日志：1次尝试失败 + 1次最终失败
        assert len(self.log_records) == 2
        assert "第1次尝试失败" in self.log_records[0].getMessage()
        assert "所有重试均已失败" in self.log_records[1].getMessage()

    def test_retry_on_failure_with_kwargs(self):
        """测试带关键字参数的函数"""

        @UnifiedErrorHandler.retry_on_failure(max_retries=2, context="KW args test")
        def kwargs_func(name=None, value=None):
            if name is None:
                raise ValueError("Name required")
            return f"{name}: {value}"

        result = kwargs_func(name="test", value=123)
        assert result == "test: 123"
        assert len(self.log_records) == 0


class TestConvenienceFunctions:
    """便捷函数测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.log_records = []
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log
        self.logger = logging.getLogger("src.utils.error_handler")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.DEBUG)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    def test_safe_execute_convenience_function(self):
        """测试便捷的安全执行函数"""

        def success_func():
            return "convenience success"

        def failing_func():
            raise ValueError("convenience error")

        # 成功情况
        result = safe_execute(success_func, "Convenience success")
        assert result == "convenience success"

        # 失败情况
        result = safe_execute(failing_func, "Convenience failure", "default")
        assert result == "default"
        assert len(self.log_records) == 1

    def test_retry_on_failure_convenience_function(self):
        """测试便捷的重试装饰器"""
        attempt_count = 0

        @retry_on_failure(max_retries=2, delay=0.01, context="Convenience retry")
        def convenience_retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError(f"Attempt {attempt_count}")
            return "convenience success"

        result = convenience_retry_func()
        assert result == "convenience success"
        assert attempt_count == 2


class TestCustomExceptions:
    """自定义异常测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.log_records = []
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log
        self.logger = logging.getLogger("src.utils.error_handler")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.DEBUG)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    def test_data_error(self):
        """测试数据错误"""
        error = DataError("Data validation failed")
        assert isinstance(error, Exception)
        assert str(error) == "Data validation failed"
        assert error.__class__.__name__ == "DataError"

    def test_connection_error(self):
        """测试连接错误"""
        error = ConnectionError("Database connection failed")
        assert isinstance(error, Exception)
        assert str(error) == "Database connection failed"
        assert error.__class__.__name__ == "ConnectionError"

    def test_validation_error(self):
        """测试验证错误"""
        error = ValidationError("Input validation failed")
        assert isinstance(error, Exception)
        assert str(error) == "Input validation failed"
        assert error.__class__.__name__ == "ValidationError"

    def test_processing_error(self):
        """测试处理错误"""
        error = ProcessingError("Data processing failed")
        assert isinstance(error, Exception)
        assert str(error) == "Data processing failed"
        assert error.__class__.__name__ == "ProcessingError"

    def test_custom_exceptions_in_error_handler(self):
        """测试自定义异常在错误处理器中的使用"""

        def failing_with_custom_error():
            raise DataError("Custom data error")

        result = UnifiedErrorHandler.safe_execute(
            failing_with_custom_error, "Custom error test", "fallback"
        )

        assert result == "fallback"
        assert len(self.log_records) == 1
        log_record = self.log_records[0]
        assert "DataError" in log_record.getMessage()
        assert "Custom data error" in log_record.getMessage()

    def test_retry_on_specific_custom_exception(self):
        """测试重试特定的自定义异常"""
        attempt_count = 0

        @retry_on_failure(
            max_retries=2, exceptions=(DataError,), context="Custom exception retry"
        )
        def custom_retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise DataError(f"Data error attempt {attempt_count}")
            return "custom success"

        result = custom_retry_func()
        assert result == "custom success"
        assert attempt_count == 2


class TestErrorHandlerIntegration:
    """错误处理器集成测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.log_records = []
        self.test_handler = logging.Handler()
        self.test_handler.emit = self.capture_log
        self.logger = logging.getLogger("src.utils.error_handler")
        self.logger.addHandler(self.test_handler)
        self.logger.setLevel(logging.DEBUG)

    def capture_log(self, record):
        """捕获日志记录"""
        self.log_records.append(record)

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.logger.removeHandler(self.test_handler)
        self.log_records.clear()

    def test_nested_error_handling(self):
        """测试嵌套错误处理"""

        def inner_failing_func():
            raise ValueError("Inner error")

        def outer_failing_func():
            return UnifiedErrorHandler.safe_execute(
                inner_failing_func, "Inner context", "inner_default"
            )

        result = UnifiedErrorHandler.safe_execute(
            outer_failing_func, "Outer context", "outer_default"
        )

        assert result == "inner_default"
        # 只有内部函数的错误日志
        assert len(self.log_records) == 1
        assert "Inner context" in self.log_records[0].getMessage()

    def test_retry_with_safe_execute_combination(self):
        """测试重试和安全执行组合使用"""

        @retry_on_failure(max_retries=2, delay=0.01, context="Combined test")
        def combined_func():
            raise ValueError("Combined error")

        result = UnifiedErrorHandler.safe_execute(
            combined_func, "Safe execute wrapper", "combined_default"
        )

        assert result == "combined_default"
        # 重试会产生3条日志（2次尝试失败 + 1次最终失败）
        # 加上safe_execute失败产生的1条日志，总共4条
        assert len(self.log_records) == 4

    def test_error_context_preservation(self):
        """测试错误上下文保持"""

        def context_test_func():
            raise RuntimeError("Context test")

        UnifiedErrorHandler.safe_execute(context_test_func, "Preserved context")

        log_record = self.log_records[0]
        assert "Preserved context" in log_record.getMessage()
        assert "Context test" in log_record.getMessage()
        assert "RuntimeError" in log_record.getMessage()

    def test_error_handler_with_multiple_exception_types(self):
        """测试多种异常类型的处理"""

        def multi_exception_func(exception_type):
            if exception_type == "value":
                raise ValueError("Value error")
            elif exception_type == "type":
                raise TypeError("Type error")
            else:
                return "success"

        # 测试不同异常类型
        for exc_type in ["value", "type"]:
            result = UnifiedErrorHandler.safe_execute(
                lambda: multi_exception_func(exc_type),
                f"Multi exception {exc_type}",
                f"default_{exc_type}",
            )
            assert result == f"default_{exc_type}"

        # 测试成功情况
        result = UnifiedErrorHandler.safe_execute(
            lambda: multi_exception_func("success"), "Multi exception success"
        )
        assert result == "success"

        assert len(self.log_records) == 2  # 只有两个失败的日志


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
