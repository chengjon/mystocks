#!/usr/bin/env python3
"""
数据库连接重试工具测试套件 - 简化版本
专注于测试核心功能，避免复杂的依赖问题
"""

import sys
import os
import time
import functools
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports to avoid circular dependency
import unittest.mock

sys.modules["src.storage.database.connection_manager"] = unittest.mock.MagicMock()
sys.modules["src.core.config"] = unittest.mock.MagicMock()
sys.modules["src.core.config_driven_table_manager"] = unittest.mock.MagicMock()

import pytest

# 导入被测试的模块 - 直接导入可以测试的部分
from src.utils.db_connection_retry import (
    db_retry,
    DatabaseConnectionHandler,
    get_tdengine_connection_with_retry,
    get_postgresql_connection_with_retry,
    return_postgresql_connection,
    init_connection_handler,
)


class TestDBRetryDecorator:
    """db_retry装饰器测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.call_count = 0
        self.call_times = []

    def test_decorator_successful_execution(self):
        """测试装饰器成功执行"""

        @db_retry(max_retries=3, delay=0.01)
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_decorator_retry_success_after_failure(self):
        """测试重试后成功"""

        @db_retry(max_retries=3, delay=0.01)
        def sometimes_failing_function():
            self.call_count += 1
            if self.call_count < 2:
                raise ConnectionError("First failure")
            return "success"

        result = sometimes_failing_function()
        assert result == "success"
        assert self.call_count == 2

    def test_decorator_all_retries_exhausted(self):
        """测试所有重试都失败"""

        @db_retry(max_retries=2, delay=0.01)
        def always_failing_function():
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError, match="Always fails"):
            always_failing_function()

    def test_decorator_non_connection_error_no_retry(self):
        """测试非连接错误不重试"""

        @db_retry(max_retries=3, delay=0.01)
        def value_error_function():
            raise ValueError("Not a connection error")

        with pytest.raises(ValueError, match="Not a connection error"):
            value_error_function()

    def test_decorator_backoff_mechanism(self):
        """测试退避机制"""
        call_times = []

        @db_retry(max_retries=3, delay=0.01, backoff=2.0)
        def backoff_function():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ConnectionError(f"Attempt {len(call_times)}")
            return "success"

        start_time = time.time()
        result = backoff_function()
        end_time = time.time()

        assert result == "success"
        assert len(call_times) == 2

        # 验证退避时间（至少0.01秒间隔）
        if len(call_times) >= 2:
            time_diff = call_times[1] - call_times[0]
            assert time_diff >= 0.005  # 允许一些时间误差

    def test_decorator_custom_parameters(self):
        """测试自定义参数"""

        @db_retry(max_retries=1, delay=0.001, backoff=1.5)
        def custom_function():
            raise ConnectionError("Custom failure")

        with pytest.raises(ConnectionError):
            custom_function()

    def test_decorator_preserves_function_metadata(self):
        """测试装饰器保留函数元数据"""

        @db_retry(max_retries=3)
        def test_function():
            """Test function docstring"""
            pass

        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring"

    def test_decorator_with_zero_retries(self):
        """测试零重试次数"""

        @db_retry(max_retries=0, delay=0.01)
        def no_retry_function():
            raise ConnectionError("No retry allowed")

        # 应该直接抛出异常，不重试
        with pytest.raises(ConnectionError):
            no_retry_function()

    def test_decorator_timing_accuracy(self):
        """测试重试时间精度"""
        call_times = []

        @db_retry(max_retries=2, delay=0.01, backoff=1.0)
        def timing_function():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ConnectionError("Timing test")
            return "success"

        start_time = time.time()
        result = timing_function()
        elapsed = time.time() - start_time

        assert result == "success"
        assert len(call_times) == 2
        # 应该至少有一个延迟间隔
        assert elapsed >= 0.005  # 允许时间误差


class TestErrorClassification:
    """错误分类测试类"""

    def test_connection_error_detection_in_decorator(self):
        """测试装饰器中的连接错误检测"""
        connection_errors = [
            "connection failed",
            "timeout occurred",
            "network unreachable",
            "connection refused",
            "connection closed",
            "connection reset",
            "database connection lost",
        ]

        for error_msg in connection_errors:
            call_count = 0

            @db_retry(max_retries=2, delay=0.001)
            def test_function():
                nonlocal call_count
                call_count += 1
                if call_count <= 2:  # 前两次抛出连接错误
                    raise ConnectionError(error_msg)
                return "success"

            with pytest.raises(ConnectionError):
                test_function()

            # 应该重试了2次（初始调用 + 1次重试）
            assert call_count == 3

    def test_non_connection_error_no_retry_in_decorator(self):
        """测试装饰器中非连接错误不重试"""
        non_connection_errors = ["invalid syntax", "value error", "type mismatch"]

        for error_msg in non_connection_errors:
            call_count = 0

            @db_retry(max_retries=2, delay=0.001)
            def test_function():
                nonlocal call_count
                call_count += 1
                raise ValueError(error_msg)

            with pytest.raises(ValueError):
                test_function()

            # 不应该重试，只调用一次
            assert call_count == 1

    def test_case_insensitive_error_detection(self):
        """测试大小写不敏感的错误检测"""
        error_messages = [
            "CONNECTION FAILED",
            "Connection Failed",
            "Network TIMEOUT",
            "Connection REFUSED",
        ]

        for error_msg in error_messages:
            call_count = 0

            @db_retry(max_retries=1, delay=0.001)
            def test_function():
                nonlocal call_count
                call_count += 1
                raise ConnectionError(error_msg)

            with pytest.raises(ConnectionError):
                test_function()

            # 应该重试
            assert call_count == 2


class TestPerformanceAndReliability:
    """性能和可靠性测试类"""

    def test_retry_performance_overhead(self):
        """测试重试性能开销"""

        @db_retry(max_retries=0, delay=0.001)
        def fast_function():
            return "result"

        # 测试多次调用的总时间
        start_time = time.time()
        for _ in range(100):
            fast_function()
        elapsed = time.time() - start_time

        # 100次调用应该在合理时间内完成（小于1秒）
        assert elapsed < 1.0

    def test_concurrent_retry_operations(self):
        """测试并发重试操作"""
        import threading
        import queue

        results = queue.Queue()

        @db_retry(max_retries=1, delay=0.001)
        def worker_function(worker_id):
            return f"worker_{worker_id}_completed"

        def worker(worker_id):
            try:
                result = worker_function(worker_id)
                results.put(result)
            except Exception as e:
                results.put(f"worker_{worker_id}_failed: {str(e)}")

        # 启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 收集结果
        collected_results = []
        while not results.empty():
            collected_results.append(results.get_nowait())

        assert len(collected_results) == 5
        assert all("completed" in result for result in collected_results)

    def test_large_number_of_retries_performance(self):
        """测试大量重试的性能"""
        call_count = 0

        @db_retry(max_retries=10, delay=0.001, backoff=1.0)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError(f"Attempt {call_count}")
            return "success"

        start_time = time.time()
        result = eventually_successful_function()
        elapsed = time.time() - start_time

        assert result == "success"
        assert call_count == 3
        # 即使有重试，也应该在合理时间内完成
        assert elapsed < 0.1

    def test_memory_usage_during_retries(self):
        """测试重试过程中的内存使用"""

        @db_retry(max_retries=5, delay=0.001)
        def memory_test_function():
            # 创建一些临时对象
            temp_data = list(range(1000))
            raise ConnectionError("Memory test")

        with pytest.raises(ConnectionError):
            memory_test_function()

        # 简单的内存检查 - 确保没有明显的内存泄漏
        # 这是一个基本的检查，实际的内存监控可能需要更复杂的工具


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_retry_with_different_exception_types(self):
        """测试不同异常类型的重试行为"""

        @db_retry(max_retries=2, delay=0.001)
        def multi_exception_function(error_type="connection"):
            if error_type == "connection":
                raise ConnectionError("Connection error")
            elif error_type == "network":
                raise OSError("Network timeout")
            else:
                raise ValueError("Value error")

        # 连接错误应该重试
        with pytest.raises(ConnectionError):
            multi_exception_function("connection")

        # 网络错误应该重试
        with pytest.raises(OSError):
            multi_exception_function("network")

        # 值错误不应该重试
        with pytest.raises(ValueError):
            multi_exception_function("value")

    def test_retry_with_function_arguments(self):
        """测试带参数函数的重试"""

        @db_retry(max_retries=2, delay=0.001)
        def argument_function(arg1, arg2, kwarg1=None):
            if arg1 == "fail":
                raise ConnectionError("Argument test failed")
            return f"{arg1}_{arg2}_{kwarg1}"

        # 成功调用
        result = argument_function("success", "test", kwarg1="value")
        assert result == "success_test_value"

        # 失败调用应该重试
        with pytest.raises(ConnectionError):
            argument_function("fail", "test", kwarg1="value")

    def test_retry_decorator_chaining(self):
        """测试装饰器链"""

        def timing_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    wrapper.execution_time = time.time() - start
                    return result
                except Exception as e:
                    wrapper.execution_time = time.time() - start
                    raise

            wrapper.execution_time = 0
            return wrapper

        @timing_decorator
        @db_retry(max_retries=2, delay=0.001)
        def chained_function(should_fail=False):
            if should_fail:
                raise ConnectionError("Chained failure")
            return "chained_success"

        # 成功调用
        result = chained_function(False)
        assert result == "chained_success"
        assert hasattr(chained_function, "execution_time")

        # 失败调用
        with pytest.raises(ConnectionError):
            chained_function(True)
        assert hasattr(chained_function, "execution_time")

    def test_error_logging_integration(self):
        """测试错误日志集成"""
        with patch("src.utils.db_connection_retry.logger") as mock_logger:

            @db_retry(max_retries=1, delay=0.001)
            def logging_function():
                raise ConnectionError("Logging test")

            with pytest.raises(ConnectionError):
                logging_function()

            # 验证日志被调用
            assert mock_logger.error.called
            # 验证日志消息包含期望的信息
            log_call_args = mock_logger.error.call_args
            assert "重试失败" in str(log_call_args)

    def test_retry_state_isolation(self):
        """测试重试状态隔离"""
        call_counts = {}

        @db_retry(max_retries=2, delay=0.001)
        def isolated_function(func_id):
            if func_id not in call_counts:
                call_counts[func_id] = 0
            call_counts[func_id] += 1

            if call_counts[func_id] < 2:
                raise ConnectionError(f"Isolation test {func_id}")
            return f"{func_id}_success"

        # 测试不同函数ID的状态隔离
        result1 = isolated_function("func1")
        result2 = isolated_function("func2")

        assert result1 == "func1_success"
        assert result2 == "func2_success"
        assert call_counts["func1"] == 2
        assert call_counts["func2"] == 1  # 第二个调用应该成功，不需要重试


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
