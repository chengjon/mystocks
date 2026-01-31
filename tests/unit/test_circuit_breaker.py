"""
单元测试: CircuitBreaker
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.core.data_source.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


class TestCircuitBreaker:
    """CircuitBreaker 单元测试"""

    def test_closed_state_normal_call(self):
        """测试 CLOSED 状态正常调用"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.get_state() == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.total_successes == 1

    def test_open_state_after_threshold(self):
        """测试达到阈值后进入 OPEN 状态"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def failing_func():
            raise ValueError("Intentional failure")

        # 连续失败 3 次
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        # 应该进入 OPEN 状态
        assert cb.get_state() == CircuitState.OPEN
        assert cb.failure_count == 3

        # 下一次调用应该被拒绝
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(failing_func)

    def test_half_open_state_after_timeout(self):
        """测试超时后进入 HALF_OPEN 状态"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

        def failing_func():
            raise ValueError("Intentional failure")

        # 连续失败 3 次，进入 OPEN 状态
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        assert cb.get_state() == CircuitState.OPEN

        # 等待超时
        time.sleep(1.5)

        # 下一次调用应该触发状态转换到 HALF_OPEN
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.get_state() == CircuitState.HALF_OPEN

    def test_recover_to_closed_after_half_open_success(self):
        """测试试探成功后回到 CLOSED 状态"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

        def failing_func():
            raise ValueError("Intentional failure")

        def success_func():
            return "success"

        # 连续失败 3 次，进入 OPEN 状态
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        # 等待超时
        time.sleep(1.5)

        # 第一次试探成功
        result = cb.call(success_func)
        assert result == "success"
        assert cb.get_state() == CircuitState.HALF_OPEN

        # 第二次试探成功，应该回到 CLOSED
        result = cb.call(success_func)
        assert result == "success"
        assert cb.get_state() == CircuitState.CLOSED

    def test_back_to_open_after_half_open_failure(self):
        """测试试探失败后回到 OPEN 状态"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

        def failing_func():
            raise ValueError("Intentional failure")

        def success_func():
            return "success"

        # 连续失败 3 次，进入 OPEN 状态
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        # 等待超时
        time.sleep(1.5)

        # 第一次试探成功
        result = cb.call(success_func)
        assert result == "success"
        assert cb.get_state() == CircuitState.HALF_OPEN

        # 第二次试探失败，应该回到 OPEN
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.get_state() == CircuitState.OPEN

    def test_concurrent_state_transitions(self):
        """测试并发状态转换 (10 线程并发)"""
        cb = CircuitBreaker(failure_threshold=10, recovery_timeout=60)
        errors = []

        def worker(worker_id):
            try:
                if worker_id % 2 == 0:
                    # 偶数线程: 成功调用
                    def success_func():
                        return "success"

                    cb.call(success_func)
                else:
                    # 奇数线程: 失败调用
                    def failing_func():
                        raise ValueError("Failure")

                    cb.call(failing_func)
            except Exception as e:
                errors.append((worker_id, e))

        # 启动 10 个并发线程
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for future in futures:
                future.result()

        # 检查是否有非预期的错误
        unexpected_errors = [
            (worker_id, e) for worker_id, e in errors if not isinstance(e, (ValueError, CircuitBreakerOpenError))
        ]
        assert len(unexpected_errors) == 0, f"Unexpected errors: {unexpected_errors}"

        # 验证状态一致性
        stats = cb.get_stats()
        assert stats["total_calls"] == 10
        assert stats["total_failures"] > 0

    def test_remaining_time_feedback(self):
        """测试剩余时间反馈"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10)

        def failing_func():
            raise ValueError("Failure")

        # 触发熔断
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        # 尝试调用，应该返回剩余时间
        try:
            cb.call(failing_func)
        except CircuitBreakerOpenError as e:
            assert "Retry after" in str(e)
            remaining = cb.get_stats()["remaining_time"]
            assert remaining > 0

        # 等待一半时间
        time.sleep(5)

        try:
            cb.call(failing_func)
        except CircuitBreakerOpenError as e:
            remaining = cb.get_stats()["remaining_time"]
            assert remaining > 0
            assert remaining < 5

    def test_configurable_threshold(self):
        """测试可配置阈值"""
        # 使用不同的阈值创建熔断器
        cb_low = CircuitBreaker(failure_threshold=2, recovery_timeout=60, name="low")
        cb_high = CircuitBreaker(failure_threshold=10, recovery_timeout=60, name="high")

        def failing_func():
            raise ValueError("Failure")

        # 低阈值熔断器应该更快熔断
        for _ in range(2):
            with pytest.raises(ValueError):
                cb_low.call(failing_func)

        assert cb_low.get_state() == CircuitState.OPEN

        # 高阈值熔断器应该还未熔断
        for _ in range(5):
            with pytest.raises(ValueError):
                cb_high.call(failing_func)

        assert cb_high.get_state() == CircuitState.CLOSED

    def test_reset(self):
        """测试手动重置"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def failing_func():
            raise ValueError("Failure")

        # 触发熔断
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        assert cb.get_state() == CircuitState.OPEN

        # 手动重置
        cb.reset()

        assert cb.get_state() == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.opened_at is None

    def test_get_stats(self):
        """测试获取统计信息"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def success_func():
            return "success"

        def failing_func():
            raise ValueError("Failure")

        # 成功调用
        cb.call(success_func)
        cb.call(success_func)

        # 失败调用
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        stats = cb.get_stats()
        assert stats["total_calls"] == 4
        assert stats["total_successes"] == 2
        assert stats["total_failures"] == 2
        assert stats["failure_count"] == 2
        assert stats["success_rate"] == 0.5
        assert stats["state"] == CircuitState.CLOSED.value

    def test_expected_exception(self):
        """测试预期的异常类型"""
        # 只捕获 ValueError
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exception=ValueError)

        def value_error_func():
            raise ValueError("Expected error")

        def runtime_error_func():
            raise RuntimeError("Unexpected error")

        # ValueError 应该被捕获
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(value_error_func)

        assert cb.get_state() == CircuitState.OPEN

        # 重置
        cb.reset()

        # RuntimeError 不应该被捕获，不影响熔断器状态
        with pytest.raises(RuntimeError):
            cb.call(runtime_error_func)

        assert cb.get_state() == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_str_representation(self):
        """测试字符串表示"""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="test_cb")

        str_repr = str(cb)
        assert "test_cb" in str_repr
        assert "CLOSED" in str_repr
        assert "0/5" in str_repr
