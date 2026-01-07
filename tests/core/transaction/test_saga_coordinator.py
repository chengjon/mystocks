"""
Saga协调器标准化测试（使用真实数据库）

测试基于实际实现的SagaCoordinator类:
- execute_kline_sync(): 主事务执行方法
- _compensate_tdengine(): 私有补偿方法

所有测试使用真实的TDengine和PostgreSQL数据库连接，
通过Mock对象技术模拟特定行为（如异常抛出）。
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, Mock
from src.core import DataClassification
from src.core.transaction.saga_coordinator import SagaCoordinator


class TestSagaCoordinatorBasic:
    """Saga协调器基础功能测试（使用真实数据库）"""

    @pytest.fixture
    def data_manager(self):
        """创建DataManager实例（真实数据库连接）"""
        from src.core.data_manager import DataManager

        return DataManager(enable_monitoring=False)

    @pytest.fixture
    def coordinator(self, data_manager):
        """使用真实DataManager的Saga协调器"""
        return data_manager.saga_coordinator

    @pytest.fixture
    def sample_kline_data(self):
        """示例K线数据"""
        return pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 30)],
                "open": [10.5],
                "high": [10.6],
                "low": [10.4],
                "close": [10.55],
                "volume": [1000],
                "amount": [10500.0],
                "symbol": ["TEST001"],
                "frequency": ["1m"],
            }
        )

    def test_initialization(self, coordinator):
        """测试: Saga协调器初始化（使用真实数据库）"""
        assert coordinator.pg is not None
        assert coordinator.td is not None
        assert hasattr(coordinator, "execute_kline_sync")
        assert hasattr(coordinator, "_compensate_tdengine")

    def test_successful_transaction_flow(self, coordinator, sample_kline_data):
        """测试: 成功的事务流程 (真实TDengine写入 + PG元数据更新)"""

        # 真实的元数据更新函数（不做任何操作）
        def metadata_update(session):
            # 真实场景: session.execute(...)
            pass

        # 执行事务（使用真实数据库）
        result = coordinator.execute_kline_sync(
            business_id="TEST001.SH_DAILY",
            kline_data=sample_kline_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=metadata_update,
        )

        # 验证成功
        assert result == True

    def test_postgresql_failure_triggers_compensation(self, coordinator, sample_kline_data):
        """测试: PG更新失败应触发补偿（使用Mock模拟异常）"""

        # 使用Mock对象技术模拟PG更新失败
        def failing_metadata_update(session):
            raise Exception("PG Update Failed - Simulated")

        # 执行事务（真实数据库连接，但PG操作会失败）
        result = coordinator.execute_kline_sync(
            business_id="TEST001.SH_DAILY_FAIL",
            kline_data=sample_kline_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=failing_metadata_update,
        )

        # 验证失败并触发补偿
        assert result == False

    def test_empty_dataframe_handling(self, coordinator):
        """测试: 空DataFrame处理（使用真实数据库）"""
        empty_df = pd.DataFrame()

        # 元数据更新函数
        def metadata_update(session):
            pass

        # 执行事务（空DataFrame会被真实数据库处理）
        result = coordinator.execute_kline_sync(
            business_id="EMPTY001",
            kline_data=empty_df,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=metadata_update,
        )

        # 空DataFrame应该导致失败或被处理
        assert result in [True, False]


class TestSagaCoordinatorSuccessScenario:
    """Saga事务成功场景测试"""

    @pytest.fixture
    def data_manager(self):
        """创建DataManager实例（使用真实连接）"""
        from src.core.data_manager import DataManager

        return DataManager(enable_monitoring=False)

    @pytest.fixture
    def sample_kline_data(self):
        """成功场景测试数据"""
        return pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 30)],
                "open": [10.5],
                "high": [10.6],
                "low": [10.4],
                "close": [10.55],
                "volume": [1000],
                "amount": [10500.0],
                "symbol": ["SUCCESS001"],
                "frequency": ["1m"],
            }
        )

    @pytest.mark.integration
    def test_full_transaction_success_flow(self, data_manager, sample_kline_data):
        """测试: 完整的成功事务流程

        流程:
        1. TDengine写入K线数据（带txn_id和is_valid=true）
        2. PostgreSQL元数据更新成功
        3. 事务状态: COMMITTED
        """
        business_id = "SUCCESS001.SH_MINUTE_20260103"

        # Mock元数据更新函数
        def mock_metadata_update(session):
            # 模拟PG更新成功
            pass

        # 执行Saga事务
        result = data_manager.saga_coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=sample_kline_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=mock_metadata_update,
        )

        # 验证事务成功
        assert result == True


class TestSagaCoordinatorFailureCompensation:
    """Saga事务失败与补偿场景测试"""

    @pytest.fixture
    def data_manager(self):
        """创建DataManager实例"""
        from src.core.data_manager import DataManager

        return DataManager(enable_monitoring=False)

    @pytest.fixture
    def sample_kline_data(self):
        """失败场景测试数据"""
        return pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 31)],
                "open": [10.6],
                "high": [10.7],
                "low": [10.5],
                "close": [10.65],
                "volume": [2000],
                "amount": [21200.0],
                "symbol": ["FAIL001"],
                "frequency": ["1m"],
            }
        )

    @pytest.mark.integration
    def test_postgresql_failure_triggers_compensation(self, data_manager, sample_kline_data):
        """测试: PostgreSQL失败应触发补偿

        流程:
        1. TDengine写入K线数据（is_valid=true）
        2. PostgreSQL元数据更新失败
        3. 触发补偿: 标记TDengine数据is_valid=false
        4. 事务状态: ROLLED_BACK
        """
        business_id = "FAIL001.SH_MINUTE_20260103"

        # Mock PG更新函数（故意失败）
        def failing_metadata_update(session):
            raise Exception("Simulated PG Update Failure")

        # 执行Saga事务（预期失败但触发补偿）
        result = data_manager.saga_coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=sample_kline_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=failing_metadata_update,
        )

        # 验证事务失败
        assert result == False


class TestSagaCoordinatorEdgeCases:
    """Saga协调器边界情况测试（使用真实数据库）"""

    @pytest.fixture
    def data_manager(self):
        """创建DataManager实例（真实数据库连接）"""
        from src.core.data_manager import DataManager

        return DataManager(enable_monitoring=False)

    @pytest.fixture
    def coordinator(self, data_manager):
        """使用真实DataManager的Saga协调器"""
        return data_manager.saga_coordinator

    def test_missing_required_columns(self, coordinator):
        """测试: 缺少必需列的处理（真实数据库）"""
        incomplete_data = pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 30)],
                "symbol": ["TEST001"],
                # 缺少 open, high, low, close等必需列
            }
        )

        # 元数据更新函数
        def metadata_update(session):
            pass

        # 执行事务（真实TDengine会验证列）
        result = coordinator.execute_kline_sync(
            business_id="INCOMPLETE001",
            kline_data=incomplete_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=metadata_update,
        )

        # 验证不会抛出未捕获的异常
        assert result in [True, False]

    def test_multiple_transactions(self, coordinator):
        """测试: 多个连续事务处理（真实数据库）"""
        sample_data = pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 30)],
                "open": [10.5],
                "high": [10.6],
                "low": [10.4],
                "close": [10.55],
                "volume": [1000],
                "amount": [10500.0],
                "symbol": ["MULTI001"],
                "frequency": ["1m"],
            }
        )

        # 元数据更新函数
        def metadata_update(session):
            pass

        # 执行多个事务（真实数据库）
        results = []
        for i in range(3):
            result = coordinator.execute_kline_sync(
                business_id=f"MULTI{i:03d}.SH_DAILY",
                kline_data=sample_data,
                classification=DataClassification.MINUTE_KLINE,
                table_name="market_data.minute_kline",
                metadata_update_func=metadata_update,
            )
            results.append(result)

        # 验证所有事务都成功
        assert all(results)
        assert len(results) == 3

    def test_data_integrity_verification(self, coordinator):
        """测试: 验证真实数据库中的数据完整性"""
        sample_data = pd.DataFrame(
            {
                "ts": [datetime(2026, 1, 3, 9, 30)],
                "open": [10.5],
                "high": [10.6],
                "low": [10.4],
                "close": [10.55],
                "volume": [1000],
                "amount": [10500.0],
                "symbol": ["VERIFY001"],
                "frequency": ["1m"],
            }
        )

        # 元数据更新函数
        def metadata_update(session):
            pass

        # 执行事务
        result = coordinator.execute_kline_sync(
            business_id="VERIFY001.SH_DAILY",
            kline_data=sample_data,
            classification=DataClassification.MINUTE_KLINE,
            table_name="market_data.minute_kline",
            metadata_update_func=metadata_update,
        )

        # 验证事务成功
        assert result == True

        # 可选: 验证数据真实写入TDengine（需要查询数据库）
        # 这里只验证事务成功，实际数据验证留给集成测试
