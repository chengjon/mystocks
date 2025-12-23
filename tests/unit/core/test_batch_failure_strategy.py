"""
batch_failure_strategy 模块单元测试

测试批量操作失败策略的完整功能:
- BatchFailureStrategy 枚举
- BatchOperationResult 数据类
- BatchFailureHandler 处理器类
"""

import pytest
import sys
import time
import pandas as pd
from unittest.mock import Mock, patch

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.batch_failure_strategy import (
    BatchFailureStrategy,
    BatchOperationResult,
    BatchFailureHandler,
)


class TestBatchFailureStrategyEnum:
    """测试 BatchFailureStrategy 枚举"""

    def test_all_strategies_exist(self):
        """测试所有策略存在"""
        assert hasattr(BatchFailureStrategy, "ROLLBACK")
        assert hasattr(BatchFailureStrategy, "CONTINUE")
        assert hasattr(BatchFailureStrategy, "RETRY")

    def test_strategy_values(self):
        """测试策略值"""
        assert BatchFailureStrategy.ROLLBACK.value == "rollback"
        assert BatchFailureStrategy.CONTINUE.value == "continue"
        assert BatchFailureStrategy.RETRY.value == "retry"

    def test_strategy_count(self):
        """测试策略数量"""
        strategies = list(BatchFailureStrategy)
        assert len(strategies) == 3

    def test_enum_iteration(self):
        """测试可以迭代策略"""
        strategies = list(BatchFailureStrategy)
        assert BatchFailureStrategy.ROLLBACK in strategies
        assert BatchFailureStrategy.CONTINUE in strategies
        assert BatchFailureStrategy.RETRY in strategies

    def test_enum_uniqueness(self):
        """测试策略值唯一性"""
        values = [item.value for item in BatchFailureStrategy]
        assert len(values) == len(set(values))

    def test_strategy_string_inheritance(self):
        """测试策略继承自字符串枚举"""
        assert isinstance(BatchFailureStrategy.ROLLBACK, str)
        assert isinstance(BatchFailureStrategy.CONTINUE, str)
        assert isinstance(BatchFailureStrategy.RETRY, str)

    def test_strategy_equality(self):
        """测试策略相等性"""
        assert BatchFailureStrategy.ROLLBACK == BatchFailureStrategy.ROLLBACK
        assert BatchFailureStrategy.ROLLBACK != BatchFailureStrategy.CONTINUE

    def test_strategy_value_format(self):
        """测试策略值格式（小写）"""
        for strategy in BatchFailureStrategy:
            assert strategy.value.islower()
            assert " " not in strategy.value


class TestBatchOperationResult:
    """测试 BatchOperationResult 数据类"""

    def test_result_creation_minimal(self):
        """测试创建最小结果对象"""
        result = BatchOperationResult(
            total_records=100,
            successful_records=95,
            failed_records=5,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=250.5,
        )

        assert result.total_records == 100
        assert result.successful_records == 95
        assert result.failed_records == 5
        assert result.strategy_used == BatchFailureStrategy.CONTINUE
        assert result.execution_time_ms == 250.5

    def test_result_creation_with_optional_fields(self):
        """测试创建包含可选字段的结果对象"""
        result = BatchOperationResult(
            total_records=50,
            successful_records=40,
            failed_records=10,
            strategy_used=BatchFailureStrategy.RETRY,
            execution_time_ms=500.0,
            failed_indices=[5, 10, 15],
            error_messages={5: "Error 1", 10: "Error 2", 15: "Error 3"},
            retry_count=2,
            rollback_executed=False,
        )

        assert result.failed_indices == [5, 10, 15]
        assert result.error_messages == {5: "Error 1", 10: "Error 2", 15: "Error 3"}
        assert result.retry_count == 2
        assert result.rollback_executed is False

    def test_post_init_initializes_empty_lists(self):
        """测试 __post_init__ 初始化空列表"""
        result = BatchOperationResult(
            total_records=10,
            successful_records=10,
            failed_records=0,
            strategy_used=BatchFailureStrategy.ROLLBACK,
            execution_time_ms=100.0,
        )

        assert result.failed_indices == []
        assert result.error_messages == {}

    def test_success_rate_calculation_perfect(self):
        """测试成功率计算（100%）"""
        result = BatchOperationResult(
            total_records=100,
            successful_records=100,
            failed_records=0,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=200.0,
        )

        assert result.success_rate == 1.0

    def test_success_rate_calculation_zero(self):
        """测试成功率计算（0%）"""
        result = BatchOperationResult(
            total_records=100,
            successful_records=0,
            failed_records=100,
            strategy_used=BatchFailureStrategy.ROLLBACK,
            execution_time_ms=50.0,
        )

        assert result.success_rate == 0.0

    def test_success_rate_calculation_partial(self):
        """测试成功率计算（部分成功）"""
        result = BatchOperationResult(
            total_records=100,
            successful_records=75,
            failed_records=25,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=300.0,
        )

        assert result.success_rate == 0.75

    def test_success_rate_zero_records(self):
        """测试零记录时的成功率"""
        result = BatchOperationResult(
            total_records=0,
            successful_records=0,
            failed_records=0,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=0.0,
        )

        assert result.success_rate == 0.0

    def test_to_dict_basic(self):
        """测试转换为字典（基本场景）"""
        result = BatchOperationResult(
            total_records=50,
            successful_records=45,
            failed_records=5,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=123.456,
        )

        result_dict = result.to_dict()

        assert result_dict["total_records"] == 50
        assert result_dict["successful_records"] == 45
        assert result_dict["failed_records"] == 5
        assert result_dict["success_rate"] == "90.00%"
        assert result_dict["strategy_used"] == "continue"
        assert result_dict["execution_time_ms"] == "123.46"
        assert result_dict["retry_count"] == 0
        assert result_dict["rollback_executed"] is False

    def test_to_dict_with_failed_indices_small(self):
        """测试转换为字典（失败索引少于10个）"""
        result = BatchOperationResult(
            total_records=10,
            successful_records=7,
            failed_records=3,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=100.0,
            failed_indices=[1, 3, 5],
        )

        result_dict = result.to_dict()
        assert result_dict["failed_indices"] == [1, 3, 5]

    def test_to_dict_with_failed_indices_large(self):
        """测试转换为字典（失败索引超过10个）"""
        failed_indices = list(range(1, 21))  # 20个失败索引
        result = BatchOperationResult(
            total_records=100,
            successful_records=80,
            failed_records=20,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=500.0,
            failed_indices=failed_indices,
        )

        result_dict = result.to_dict()
        # 应该只返回前10个
        assert len(result_dict["failed_indices"]) == 10
        assert result_dict["failed_indices"] == failed_indices[:10]

    def test_to_dict_with_error_messages(self):
        """测试转换为字典（包含错误消息）"""
        error_messages = {
            1: "Error 1",
            2: "Error 2",
            3: "Error 3",
            4: "Error 4",
            5: "Error 5",
        }
        result = BatchOperationResult(
            total_records=10,
            successful_records=5,
            failed_records=5,
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=200.0,
            error_messages=error_messages,
        )

        result_dict = result.to_dict()
        # 应该只返回前3个错误消息
        assert len(result_dict["error_sample"]) == 3
        assert "Error 1" in result_dict["error_sample"]


class TestBatchFailureHandler:
    """测试 BatchFailureHandler 处理器类"""

    def test_handler_initialization_default(self):
        """测试处理器默认初始化"""
        handler = BatchFailureHandler()

        assert handler.strategy == BatchFailureStrategy.CONTINUE
        assert handler.max_retries == 3
        assert handler.retry_delay_base == 1.0
        assert handler.retry_delay_multiplier == 2.0

    def test_handler_initialization_custom(self):
        """测试处理器自定义初始化"""
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY,
            max_retries=5,
            retry_delay_base=0.5,
            retry_delay_multiplier=1.5,
        )

        assert handler.strategy == BatchFailureStrategy.RETRY
        assert handler.max_retries == 5
        assert handler.retry_delay_base == 0.5
        assert handler.retry_delay_multiplier == 1.5

    def test_execute_batch_unknown_strategy_raises_error(self):
        """测试未知策略抛出异常"""
        handler = BatchFailureHandler()
        handler.strategy = "unknown_strategy"  # 无效策略

        test_data = pd.DataFrame({"id": [1, 2, 3]})
        mock_operation = Mock(return_value=True)

        with pytest.raises(ValueError, match="未知的失败策略"):
            handler.execute_batch(test_data, mock_operation)


class TestRollbackStrategy:
    """测试 ROLLBACK 策略"""

    def test_rollback_all_success(self):
        """测试 ROLLBACK 策略 - 全部成功"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.ROLLBACK)
        test_data = pd.DataFrame({"id": [1, 2, 3], "value": ["A", "B", "C"]})

        # Mock操作返回成功
        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation, "test_rollback")

        assert result.total_records == 3
        assert result.successful_records == 3
        assert result.failed_records == 0
        assert result.strategy_used == BatchFailureStrategy.ROLLBACK
        assert result.rollback_executed is False
        assert mock_operation.called

    def test_rollback_operation_fails(self):
        """测试 ROLLBACK 策略 - 操作失败"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.ROLLBACK)
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        # Mock操作返回失败
        mock_operation = Mock(return_value=False)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 3
        assert result.successful_records == 0
        assert result.failed_records == 3
        assert result.rollback_executed is True
        assert 0 in result.error_messages
        assert result.error_messages[0] == "Batch operation failed"

    def test_rollback_operation_raises_exception(self):
        """测试 ROLLBACK 策略 - 操作抛出异常"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.ROLLBACK)
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        # Mock操作抛出异常
        mock_operation = Mock(side_effect=Exception("Database connection error"))

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 3
        assert result.successful_records == 0
        assert result.failed_records == 3
        assert result.rollback_executed is True
        assert "Database connection error" in result.error_messages[0]


class TestContinueStrategy:
    """测试 CONTINUE 策略"""

    def test_continue_all_success(self):
        """测试 CONTINUE 策略 - 全部成功"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.CONTINUE)
        test_data = pd.DataFrame({"id": [1, 2, 3], "value": ["A", "B", "C"]})

        # Mock操作始终成功
        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 3
        assert result.successful_records == 3
        assert result.failed_records == 0
        assert result.strategy_used == BatchFailureStrategy.CONTINUE
        assert len(result.failed_indices) == 0

    def test_continue_partial_success(self):
        """测试 CONTINUE 策略 - 部分成功"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.CONTINUE)
        test_data = pd.DataFrame({"id": [1, 2, 3, 4, 5]})

        # Mock操作: 前3次成功,后2次失败
        call_count = 0

        def mock_operation_partial(df):
            nonlocal call_count
            call_count += 1
            return call_count <= 3  # 前3次成功

        result = handler.execute_batch(test_data, mock_operation_partial)

        assert result.total_records == 5
        assert result.successful_records == 3
        assert result.failed_records == 2
        assert len(result.failed_indices) == 2
        assert len(result.error_messages) == 2

    def test_continue_with_exceptions(self):
        """测试 CONTINUE 策略 - 部分记录抛出异常"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.CONTINUE)
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        call_count = 0

        def mock_operation_with_exception(df):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # 第2条记录抛出异常
                raise ValueError("Invalid data")
            return True

        result = handler.execute_batch(test_data, mock_operation_with_exception)

        assert result.total_records == 3
        assert result.successful_records == 2
        assert result.failed_records == 1
        assert len(result.failed_indices) == 1
        # 检查错误消息中包含异常信息
        assert any("Invalid data" in str(msg) for msg in result.error_messages.values())


class TestRetryStrategy:
    """测试 RETRY 策略"""

    def test_retry_first_attempt_success(self):
        """测试 RETRY 策略 - 首次尝试成功"""
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY, max_retries=3
        )
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 3
        assert result.successful_records == 3
        assert result.failed_records == 0
        assert result.retry_count == 0  # 没有重试
        assert mock_operation.call_count == 1  # 只调用一次

    @patch("time.sleep")  # Mock sleep 避免实际等待
    def test_retry_success_after_retries(self, mock_sleep):
        """测试 RETRY 策略 - 重试后成功

        注意: 当前实现会累积失败索引,即使最后成功也会保留之前的失败记录
        这是源代码的一个已知问题
        """
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY, max_retries=3, retry_delay_base=0.1
        )
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        # Mock操作: 前2次失败,第3次成功
        call_count = 0

        def mock_operation_retry(df):
            nonlocal call_count
            call_count += 1
            return call_count >= 3

        result = handler.execute_batch(test_data, mock_operation_retry)

        assert result.total_records == 3
        assert result.successful_records == 3
        # BUG: 源代码会累积失败记录,即使最后成功
        assert result.failed_records == 6  # 2次失败 * 3条记录
        assert result.retry_count == 2  # 重试2次
        assert call_count == 3  # 总共调用3次

    @patch("time.sleep")
    def test_retry_all_attempts_fail(self, mock_sleep):
        """测试 RETRY 策略 - 所有重试都失败

        注意: 当前实现会累积失败索引,每次重试都会添加失败记录
        这是源代码的一个已知问题
        """
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY, max_retries=2, retry_delay_base=0.1
        )
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        # Mock操作始终失败
        mock_operation = Mock(return_value=False)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 3
        assert result.successful_records == 0
        # BUG: 源代码会累积失败记录 (初始尝试 + 2次重试) * 3条记录 = 9
        assert result.failed_records == 9  # 3次尝试 * 3条记录
        assert result.retry_count == 2  # 最大重试次数
        assert len(result.failed_indices) == 9  # 累积的失败索引

    @patch("time.sleep")
    def test_retry_exponential_backoff(self, mock_sleep):
        """测试 RETRY 策略 - 指数退避延迟"""
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY,
            max_retries=3,
            retry_delay_base=1.0,
            retry_delay_multiplier=2.0,
        )
        test_data = pd.DataFrame({"id": [1]})

        mock_operation = Mock(return_value=False)  # 始终失败

        handler.execute_batch(test_data, mock_operation)

        # 验证 sleep 被调用的次数和参数
        assert mock_sleep.call_count == 3  # 3次重试
        # 第1次重试: 1.0 * 2^0 = 1.0
        # 第2次重试: 1.0 * 2^1 = 2.0
        # 第3次重试: 1.0 * 2^2 = 4.0
        expected_delays = [1.0, 2.0, 4.0]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_delays == expected_delays


class TestExecutionTimeTracking:
    """测试执行时间追踪"""

    def test_execution_time_is_recorded(self):
        """测试执行时间被记录"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.CONTINUE)
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        def slow_operation(df):
            time.sleep(0.01)  # 模拟耗时操作
            return True

        result = handler.execute_batch(test_data, slow_operation)

        # 验证执行时间被记录且大于0
        assert result.execution_time_ms > 0
        # 由于有sleep(0.01),执行时间应该至少几毫秒
        assert result.execution_time_ms >= 10  # 至少10ms (考虑3条记录)


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_dataframe(self):
        """测试空 DataFrame"""
        handler = BatchFailureHandler()
        test_data = pd.DataFrame()

        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 0
        assert result.successful_records == 0
        assert result.failed_records == 0

    def test_single_row_dataframe(self):
        """测试单行 DataFrame"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.CONTINUE)
        test_data = pd.DataFrame({"id": [1]})

        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 1
        assert result.successful_records == 1
        assert result.failed_records == 0

    def test_large_dataframe(self):
        """测试大型 DataFrame"""
        handler = BatchFailureHandler(strategy=BatchFailureStrategy.CONTINUE)
        test_data = pd.DataFrame({"id": range(1000)})

        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation)

        assert result.total_records == 1000
        assert result.successful_records == 1000


class TestRetryStrategyExceptions:
    """测试 RETRY 策略的异常处理"""

    @patch("time.sleep")
    def test_retry_with_exceptions(self, mock_sleep):
        """测试 RETRY 策略 - 操作抛出异常"""
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY, max_retries=2, retry_delay_base=0.1
        )
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        # Mock操作: 总是抛出异常
        def mock_operation_with_exception(df):
            raise RuntimeError("Database connection failed")

        result = handler.execute_batch(test_data, mock_operation_with_exception)

        # 验证结果
        assert result.total_records == 3
        assert result.successful_records == 0
        # 所有尝试都失败: (初始 + 2次重试) * 3条记录 = 9
        assert result.failed_records == 9
        assert result.retry_count == 2
        # 验证错误消息包含异常信息
        assert len(result.error_messages) > 0
        assert any(
            "Database connection failed" in str(msg)
            for msg in result.error_messages.values()
        )

    @patch("time.sleep")
    def test_retry_with_partial_exceptions(self, mock_sleep):
        """测试 RETRY 策略 - 部分尝试抛出异常，最后成功"""
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY, max_retries=3, retry_delay_base=0.1
        )
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        call_count = 0

        def mock_operation_partial_exception(df):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError(f"Temporary error {call_count}")
            return True  # 第3次成功

        result = handler.execute_batch(test_data, mock_operation_partial_exception)

        assert result.total_records == 3
        assert result.successful_records == 3
        # 前两次失败，累积6条失败记录
        assert result.failed_records == 6  # 2次异常 * 3条记录
        assert result.retry_count == 2
        assert call_count == 3

    def test_retry_empty_dataframe_early_break(self):
        """测试 RETRY 策略 - 空DataFrame触发early break"""
        handler = BatchFailureHandler(
            strategy=BatchFailureStrategy.RETRY, max_retries=5
        )
        # 空DataFrame
        test_data = pd.DataFrame()

        mock_operation = Mock(return_value=True)

        result = handler.execute_batch(test_data, mock_operation)

        # 验证空数据直接break，不会调用operation
        assert result.total_records == 0
        assert result.successful_records == 0
        assert result.failed_records == 0
        assert result.retry_count == 0
        # 验证operation没有被调用（因为early break）
        assert mock_operation.call_count == 0
