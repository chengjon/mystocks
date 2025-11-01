"""
批量操作失败策略

定义批量数据操作失败时的三种处理策略:
1. ROLLBACK - 回滚整个批次
2. CONTINUE - 跳过失败记录,继续处理
3. RETRY - 自动重试失败记录

创建日期: 2025-10-11
版本: 1.0.0
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import pandas as pd
import time
from datetime import datetime


class BatchFailureStrategy(str, Enum):
    """
    批量操作失败策略枚举

    - ROLLBACK: 任何记录失败则回滚整个批次 (ACID语义)
    - CONTINUE: 跳过失败记录,继续处理剩余记录 (最大努力语义)
    - RETRY: 自动重试失败记录,使用指数退避 (最终一致性语义)
    """

    ROLLBACK = "rollback"
    """回滚策略: 任何失败都回滚整个批次,保证ACID"""

    CONTINUE = "continue"
    """继续策略: 跳过失败记录,记录错误日志,继续处理"""

    RETRY = "retry"
    """重试策略: 自动重试失败记录,使用指数退避"""


@dataclass
class BatchOperationResult:
    """
    批量操作结果

    记录批量操作的详细结果,包括成功/失败统计和错误详情
    """

    total_records: int
    """总记录数"""

    successful_records: int
    """成功记录数"""

    failed_records: int
    """失败记录数"""

    strategy_used: BatchFailureStrategy
    """使用的失败策略"""

    execution_time_ms: float
    """执行时间(毫秒)"""

    failed_indices: List[int] = None
    """失败记录的索引列表"""

    error_messages: Dict[int, str] = None
    """失败记录的错误消息 {index: error_message}"""

    retry_count: int = 0
    """重试次数"""

    rollback_executed: bool = False
    """是否执行了回滚"""

    def __post_init__(self):
        if self.failed_indices is None:
            self.failed_indices = []
        if self.error_messages is None:
            self.error_messages = {}

    @property
    def success_rate(self) -> float:
        """成功率 (0.0-1.0)"""
        if self.total_records == 0:
            return 0.0
        return self.successful_records / self.total_records

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_records': self.total_records,
            'successful_records': self.successful_records,
            'failed_records': self.failed_records,
            'success_rate': f"{self.success_rate:.2%}",
            'strategy_used': self.strategy_used.value,
            'execution_time_ms': f"{self.execution_time_ms:.2f}",
            'retry_count': self.retry_count,
            'rollback_executed': self.rollback_executed,
            'failed_indices': self.failed_indices[:10] if len(self.failed_indices) > 10 else self.failed_indices,
            'error_sample': list(self.error_messages.values())[:3] if self.error_messages else []
        }


class BatchFailureHandler:
    """
    批量失败处理器

    提供三种失败策略的具体实现逻辑
    """

    def __init__(
        self,
        strategy: BatchFailureStrategy = BatchFailureStrategy.CONTINUE,
        max_retries: int = 3,
        retry_delay_base: float = 1.0,
        retry_delay_multiplier: float = 2.0
    ):
        """
        初始化失败处理器

        Args:
            strategy: 失败策略
            max_retries: 最大重试次数 (仅RETRY策略)
            retry_delay_base: 重试基础延迟(秒)
            retry_delay_multiplier: 重试延迟倍数 (指数退避)
        """
        self.strategy = strategy
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base
        self.retry_delay_multiplier = retry_delay_multiplier

    def execute_batch(
        self,
        data: pd.DataFrame,
        operation: Callable[[pd.DataFrame], bool],
        operation_name: str = "batch_operation"
    ) -> BatchOperationResult:
        """
        执行批量操作 (根据策略处理失败)

        Args:
            data: 数据DataFrame
            operation: 操作函数 (接收DataFrame,返回bool表示成功/失败)
            operation_name: 操作名称 (用于日志)

        Returns:
            批量操作结果

        Example:
            handler = BatchFailureHandler(BatchFailureStrategy.RETRY)
            result = handler.execute_batch(
                df,
                lambda batch: mysql_access.insert_dataframe('table', batch),
                'insert_stock_data'
            )
            print(f"成功率: {result.success_rate:.2%}")
        """
        start_time = time.time()
        total_records = len(data)

        # 根据策略选择处理方法
        if self.strategy == BatchFailureStrategy.ROLLBACK:
            result = self._execute_with_rollback(data, operation, operation_name)
        elif self.strategy == BatchFailureStrategy.CONTINUE:
            result = self._execute_with_continue(data, operation, operation_name)
        elif self.strategy == BatchFailureStrategy.RETRY:
            result = self._execute_with_retry(data, operation, operation_name)
        else:
            raise ValueError(f"未知的失败策略: {self.strategy}")

        # 计算执行时间
        result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    def _execute_with_rollback(
        self,
        data: pd.DataFrame,
        operation: Callable[[pd.DataFrame], bool],
        operation_name: str
    ) -> BatchOperationResult:
        """
        ROLLBACK策略: 任何失败都回滚整个批次

        实现原理:
        1. 尝试执行整批操作
        2. 如果失败,回滚所有已完成的操作
        3. 返回失败结果
        """
        print(f"📍 执行批量操作 [{operation_name}] - 策略: ROLLBACK")

        try:
            # 尝试执行整批操作
            success = operation(data)

            if success:
                return BatchOperationResult(
                    total_records=len(data),
                    successful_records=len(data),
                    failed_records=0,
                    strategy_used=BatchFailureStrategy.ROLLBACK,
                    execution_time_ms=0.0
                )
            else:
                # 操作失败,标记为需要回滚
                print(f"❌ 批量操作失败,准备回滚")
                return BatchOperationResult(
                    total_records=len(data),
                    successful_records=0,
                    failed_records=len(data),
                    strategy_used=BatchFailureStrategy.ROLLBACK,
                    execution_time_ms=0.0,
                    rollback_executed=True,
                    error_messages={0: "Batch operation failed"}
                )

        except Exception as e:
            print(f"❌ 批量操作异常: {e}")
            return BatchOperationResult(
                total_records=len(data),
                successful_records=0,
                failed_records=len(data),
                strategy_used=BatchFailureStrategy.ROLLBACK,
                execution_time_ms=0.0,
                rollback_executed=True,
                error_messages={0: str(e)}
            )

    def _execute_with_continue(
        self,
        data: pd.DataFrame,
        operation: Callable[[pd.DataFrame], bool],
        operation_name: str
    ) -> BatchOperationResult:
        """
        CONTINUE策略: 逐条处理,跳过失败记录

        实现原理:
        1. 逐条执行操作
        2. 失败记录跳过,记录错误
        3. 继续处理剩余记录
        """
        print(f"📍 执行批量操作 [{operation_name}] - 策略: CONTINUE")

        successful_count = 0
        failed_indices = []
        error_messages = {}

        # 逐条处理
        for idx, row in data.iterrows():
            try:
                single_row_df = pd.DataFrame([row])
                success = operation(single_row_df)

                if success:
                    successful_count += 1
                else:
                    failed_indices.append(idx)
                    error_messages[idx] = "Operation returned False"
                    print(f"⚠️  记录 {idx} 失败,继续处理...")

            except Exception as e:
                failed_indices.append(idx)
                error_messages[idx] = str(e)
                print(f"⚠️  记录 {idx} 异常: {e}, 继续处理...")

        print(f"✅ 批量操作完成: {successful_count}/{len(data)} 成功")

        return BatchOperationResult(
            total_records=len(data),
            successful_records=successful_count,
            failed_records=len(failed_indices),
            strategy_used=BatchFailureStrategy.CONTINUE,
            execution_time_ms=0.0,
            failed_indices=failed_indices,
            error_messages=error_messages
        )

    def _execute_with_retry(
        self,
        data: pd.DataFrame,
        operation: Callable[[pd.DataFrame], bool],
        operation_name: str
    ) -> BatchOperationResult:
        """
        RETRY策略: 失败记录自动重试 (指数退避)

        实现原理:
        1. 首次批量执行
        2. 收集失败记录
        3. 使用指数退避重试失败记录
        4. 重复直到成功或达到最大重试次数
        """
        print(f"📍 执行批量操作 [{operation_name}] - 策略: RETRY (最多{self.max_retries}次)")

        remaining_data = data.copy()
        successful_count = 0
        total_retries = 0
        all_failed_indices = []
        all_error_messages = {}

        for attempt in range(self.max_retries + 1):
            if remaining_data.empty:
                break

            if attempt > 0:
                # 指数退避
                delay = self.retry_delay_base * (self.retry_delay_multiplier ** (attempt - 1))
                print(f"⏳ 重试 {attempt}/{self.max_retries}, 等待 {delay:.1f}秒...")
                time.sleep(delay)
                total_retries += 1

            # 尝试执行剩余数据
            try:
                success = operation(remaining_data)

                if success:
                    successful_count += len(remaining_data)
                    print(f"✅ 批量操作成功: {len(remaining_data)} 条记录")
                    break
                else:
                    # 整批失败,记录所有索引
                    for idx in remaining_data.index:
                        all_failed_indices.append(idx)
                        all_error_messages[idx] = f"Failed at attempt {attempt + 1}"

            except Exception as e:
                # 异常,记录所有索引
                for idx in remaining_data.index:
                    all_failed_indices.append(idx)
                    all_error_messages[idx] = str(e)
                print(f"❌ 批量操作异常 (尝试 {attempt + 1}): {e}")

        # 最终失败的记录
        final_failed_count = len(all_failed_indices)

        if final_failed_count > 0:
            print(f"❌ {final_failed_count} 条记录在 {total_retries} 次重试后仍失败")

        return BatchOperationResult(
            total_records=len(data),
            successful_records=successful_count,
            failed_records=final_failed_count,
            strategy_used=BatchFailureStrategy.RETRY,
            execution_time_ms=0.0,
            failed_indices=all_failed_indices,
            error_messages=all_error_messages,
            retry_count=total_retries
        )


if __name__ == "__main__":
    """测试批量失败策略"""
    print("\n" + "=" * 80)
    print("批量操作失败策略测试")
    print("=" * 80 + "\n")

    # 创建测试数据
    test_data = pd.DataFrame({
        'id': range(1, 11),
        'value': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    })

    # 模拟操作: 70%成功率
    def mock_operation(df: pd.DataFrame) -> bool:
        import random
        return random.random() > 0.3

    # 测试三种策略
    strategies = [
        BatchFailureStrategy.ROLLBACK,
        BatchFailureStrategy.CONTINUE,
        BatchFailureStrategy.RETRY
    ]

    for strategy in strategies:
        print(f"\n{'='*80}")
        print(f"测试策略: {strategy.value.upper()}")
        print(f"{'='*80}\n")

        handler = BatchFailureHandler(strategy=strategy, max_retries=2)
        result = handler.execute_batch(
            test_data,
            mock_operation,
            f"test_{strategy.value}"
        )

        print(f"\n结果统计:")
        for key, value in result.to_dict().items():
            print(f"  {key}: {value}")

    print("\n" + "=" * 80)
    print("✅ 批量失败策略测试完成")
    print("=" * 80)
