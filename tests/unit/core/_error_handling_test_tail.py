import pytest

from src.core.error_handling import (
    CircuitBreaker,
    DatabaseConnectionError,
    ErrorCategory,
    ErrorHandler,
    ErrorRecoveryStrategy,
    handle_errors,
)


class TestEdgeCases:
    """边界情况测试"""

    def test_extreme_retry_attempts(self):
        """测试极端重试次数"""
        attempt_count = 0

        @handle_errors(max_retries=100, base_delay=0.001)
        def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 5:
                raise DatabaseConnectionError("Connection failed")
            return "success"

        result = test_function()
        assert result == "success"
        assert attempt_count == 5

    def test_very_small_delays(self):
        """测试极小延迟"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(base_delay=0.001, max_delay=0.01, backoff_factor=2.0)
        delay = strategy(1)
        assert 0.001 <= delay <= 0.01

    def test_zero_delay_backoff(self):
        """测试零延迟退避"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(base_delay=0.0, max_delay=1.0, backoff_factor=2.0)

        delay = strategy(0)
        assert delay == 0.0
        delay = strategy(1)
        assert delay == 0.0

    def test_large_delay_backoff(self):
        """测试大延迟退避"""
        strategy = ErrorRecoveryStrategy.exponential_backoff(base_delay=1000.0, max_delay=2000.0, backoff_factor=2.0)

        delay = strategy(5)
        assert delay == 2000.0

    def test_error_with_long_message(self):
        """测试长错误消息"""
        long_message = "x" * 10000
        error = DatabaseConnectionError(long_message)

        assert len(str(error)) == 10000
        assert error.category == ErrorCategory.DATABASE

    def test_circuit_breaker_zero_threshold(self):
        """测试零阈值的熔断器"""
        breaker = CircuitBreaker(failure_threshold=0)

        @breaker
        def test_function():
            raise ValueError("Test error")

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

        with pytest.raises(ValueError):
            test_function()

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
        for _ in range(1000):
            handler.log_error(error)
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 2.0
        assert handler.error_stats["DatabaseConnectionError"]["count"] == 1000

    def test_decorator_performance(self):
        """测试装饰器性能"""

        @handle_errors(max_retries=0)
        def test_function():
            return "success"

        import time

        start_time = time.time()
        for _ in range(1000):
            test_function()
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 1.0

    def test_circuit_breaker_performance(self):
        """测试熔断器性能"""
        breaker = CircuitBreaker(failure_threshold=1000)

        @breaker
        def test_function():
            return "success"

        import time

        start_time = time.time()
        for _ in range(1000):
            test_function()
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 1.0
        assert breaker.failure_count == 0
