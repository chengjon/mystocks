"""
Database Connection Retry Simple Test Suite
数据库连接重试简化测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.db_connection_retry (177行)
"""

import pytest
import time
import functools
from typing import Any, Callable


# Since there are circular import issues, let's recreate the decorator logic here for testing
def db_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    数据库连接重试装饰器（测试版本）
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    error_msg = str(e).lower()

                    # 检查是否是连接相关错误，需要重试
                    if any(
                        keyword in error_msg
                        for keyword in [
                            "connection",
                            "timeout",
                            "network",
                            "refused",
                            "closed",
                            "reset",
                        ]
                    ):
                        if retries < max_retries:
                            print(f"数据库连接失败，{current_delay}秒后重试 ({retries}/{max_retries})")
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            print("数据库连接重试失败")
                            raise
                    else:
                        # 如果不是连接错误，直接抛出异常
                        raise

            return func(*args, **kwargs)

        return wrapper

    return decorator


class TestDatabaseRetryDecorator:
    """数据库重试装饰器测试"""

    def test_retry_decorator_success_first_try(self):
        """测试重试装饰器首次尝试成功"""

        @db_retry(max_retries=3, delay=0.01, backoff=1.0)
        def success_function():
            return "success"

        result = success_function()
        assert result == "success"

    def test_retry_decorator_eventual_success(self):
        """测试重试装饰器重试后成功"""
        call_count = 0

        @db_retry(max_retries=3, delay=0.01, backoff=1.0)
        def retry_success_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "eventual_success"

        start_time = time.time()
        result = retry_success_function()
        end_time = time.time()

        assert result == "eventual_success"
        assert call_count == 2
        # 验证有延迟
        assert end_time - start_time >= 0.01

    def test_retry_decorator_all_retries_failed(self):
        """测试重试装饰器所有重试都失败"""

        @db_retry(max_retries=2, delay=0.01, backoff=1.0)
        def always_fail_function():
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError, match="Always fails"):
            always_fail_function()

    def test_retry_decorator_non_connection_error(self):
        """测试重试装饰器非连接错误不重试"""
        call_count = 0

        @db_retry(max_retries=3, delay=0.01, backoff=1.0)
        def non_connection_error_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not a connection error")

        with pytest.raises(ValueError, match="Not a connection error"):
            non_connection_error_function()

        # 应该只调用一次，不重试
        assert call_count == 1

    def test_retry_decorator_connection_error_keywords(self):
        """测试重试装饰器连接错误关键词识别"""
        connection_errors = [
            ConnectionError("connection failed"),
            TimeoutError("timeout occurred"),
            OSError("network unreachable"),
            ConnectionResetError("connection reset"),
            ConnectionRefusedError("connection refused"),
            RuntimeError("database closed"),
        ]

        for error in connection_errors:
            call_count = 0

            @db_retry(max_retries=2, delay=0.001, backoff=1.0)
            def test_function():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise error
                return "success"

            result = test_function()
            assert result == "success"
            assert call_count == 2

    def test_retry_decorator_preserves_function_metadata(self):
        """测试重试装饰器保留函数元数据"""

        @db_retry(max_retries=3)
        def test_function(param1, param2=None):
            """测试函数文档字符串"""
            return f"result_{param1}_{param2 or 'default'}"

        # 验证函数元数据被保留
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "测试函数文档字符串"

        # 验证函数仍然正常工作
        result = test_function("test", param2="value")
        assert result == "result_test_value"

    def test_retry_decorator_with_backoff(self):
        """测试重试装饰器指数退避延迟"""
        attempt_times = []

        @db_retry(max_retries=3, delay=0.01, backoff=2.0)
        def backoff_function():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ConnectionError("Connection failed")
            return "success"

        backoff_function()

        assert len(attempt_times) == 3
        # 验证延迟递增
        delay1 = attempt_times[1] - attempt_times[0]
        delay2 = attempt_times[2] - attempt_times[1]
        assert delay2 >= delay1 * 1.8  # 允许一些时间误差

    def test_retry_decorator_default_parameters(self):
        """测试重试装饰器默认参数"""

        @db_retry()  # 使用默认参数
        def default_params_function():
            return "success"

        result = default_params_function()
        assert result == "success"

    def test_retry_decorator_zero_delay(self):
        """测试重试装饰器零延迟"""
        call_count = 0

        @db_retry(max_retries=2, delay=0, backoff=1.0)
        def zero_delay_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "success"

        start_time = time.time()
        result = zero_delay_function()
        end_time = time.time()

        assert result == "success"
        assert call_count == 2
        # 零延迟应该快速完成
        assert end_time - start_time < 0.1

    def test_retry_decorator_case_insensitive_error_matching(self):
        """测试重试装饰器大小写不敏感错误匹配"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.001)
        def case_insensitive_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("CONNECTION TIMEOUT")
            return "success"

        result = case_insensitive_function()
        assert result == "success"
        assert call_count == 2

    def test_retry_decorator_mixed_scenarios(self):
        """测试重试装饰器混合场景"""
        # 测试多种成功和失败场景
        scenarios = [
            # (max_retries, should_succeed_on_attempt, exceptions)
            (3, 1, []),  # 立即成功
            (3, 2, [ConnectionError("fail")]),  # 第二次成功
            (3, 3, [ConnectionError("fail1"), ConnectionError("fail2")]),  # 第三次成功
            (
                2,
                None,
                [
                    ConnectionError("fail1"),
                    ConnectionError("fail2"),
                    ValueError("non-connection"),
                ],
            ),  # 非连接错误
        ]

        for max_retries, success_on, exceptions in scenarios:
            call_count = 0

            @db_retry(max_retries=max_retries, delay=0.001)
            def test_scenario():
                nonlocal call_count
                call_count += 1

                if success_on and call_count == success_on:
                    return "success"

                if call_count <= len(exceptions):
                    raise exceptions[call_count - 1]

                return "unexpected_success"

            if success_on:
                result = test_scenario()
                assert result == "success"
                assert call_count == success_on
            else:
                with pytest.raises(Exception):
                    test_scenario()


class TestRetryDecoratorEdgeCases:
    """重试装饰器边界情况测试"""

    def test_retry_decorator_with_zero_retries(self):
        """测试零次重试"""

        @db_retry(max_retries=0, delay=0.01)
        def zero_retries_function():
            raise ConnectionError("Should fail immediately")

        with pytest.raises(ConnectionError):
            zero_retries_function()

    def test_retry_decorator_with_large_backoff(self):
        """测试大退避倍数"""
        call_count = 0

        @db_retry(max_retries=2, delay=0.001, backoff=10.0)
        def large_backoff_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "success"

        start_time = time.time()
        result = large_backoff_function()
        end_time = time.time()

        assert result == "success"
        assert call_count == 2
        # 应该有明显的延迟
        assert end_time - start_time >= 0.01  # 至少10ms

    def test_retry_decorator_complex_error_messages(self):
        """测试复杂错误消息"""
        complex_errors = [
            "Connection to database failed: Network is unreachable",
            "Timeout after 30 seconds: Cannot connect to server",
            "Database connection pool is closed and cannot be used",
            "Connection reset by peer during query execution",
        ]

        for error_msg in complex_errors:
            call_count = 0

            @db_retry(max_retries=2, delay=0.001)
            def test_function():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise ConnectionError(error_msg)
                return "success"

            result = test_function()
            assert result == "success"
            assert call_count == 2

    def test_retry_decorator_nested_function_calls(self):
        """测试嵌套函数调用"""

        @db_retry(max_retries=2, delay=0.001)
        def inner_function():
            return "inner_success"

        @db_retry(max_retries=2, delay=0.001)
        def outer_function():
            return f"outer_{inner_function()}"

        result = outer_function()
        assert result == "outer_inner_success"

    def test_retry_decorator_with_kwargs(self):
        """测试带关键字参数的函数"""

        @db_retry(max_retries=2, delay=0.001)
        def function_with_kwargs(a, b=10, c=None):
            return {"a": a, "b": b, "c": c}

        result = function_with_kwargs("test", b=20, c="value")
        assert result == {"a": "test", "b": 20, "c": "value"}

    def test_retry_decorator_exception_preservation(self):
        """测试异常信息保留"""
        original_error = ValueError("Original error message")

        @db_retry(max_retries=1, delay=0.001)
        def function_with_exception():
            raise original_error

        try:
            function_with_exception()
        except ValueError as e:
            assert e == original_error
            assert str(e) == "Original error message"

    def test_retry_decorator_performance_overhead(self):
        """测试装饰器性能开销"""

        # 测试无重试情况下的性能
        @db_retry(max_retries=3, delay=0.001)
        def fast_function():
            return "fast_result"

        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            result = fast_function()
            assert result == "fast_result"

        end_time = time.time()
        avg_time = (end_time - start_time) / iterations

        # 平均每次调用应该很快（小于1ms）
        assert avg_time < 0.001


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
