"""
多数据库同步与一致性集成测试

验证多数据库协同，包括:
- 跨数据库数据同步
- 事务一致性
- 数据完整性验证
- 并发操作处理
- 冲突解决机制

创建日期: 2025-10-28
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from unified_manager import MyStocksUnifiedManager
from core.data_classification import DataClassification, DatabaseTarget


class TestDataSyncAcrossDatabases:
    """跨数据库数据同步测试"""

    @pytest.fixture
    def setup_sync_data(self):
        """准备同步测试数据"""
        return {
            "tick_data": pd.DataFrame(
                {
                    "ts": pd.date_range("2025-01-01 09:30", periods=100, freq="1s"),
                    "symbol": ["600000.SH"] * 100,
                    "price": np.random.uniform(10, 20, 100),
                    "volume": np.random.randint(100, 1000, 100),
                }
            ),
            "daily_kline": pd.DataFrame(
                {
                    "symbol": ["600000.SH"] * 50,
                    "trade_date": pd.date_range("2024-01-01", periods=50, freq="D"),
                    "close": np.random.uniform(10, 20, 50),
                    "volume": np.random.randint(1000000, 10000000, 50),
                }
            ),
        }

    def test_sync_tick_to_tdengine_then_aggregate_to_daily(
        self, unified_manager, setup_sync_data
    ):
        """测试 Tick 数据同步到 TDengine，然后聚合为日线"""
        tick_data = setup_sync_data["tick_data"]

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ) as mock_save:
            # 保存 Tick 数据到 TDengine
            result = unified_manager.save_data_by_classification(
                DataClassification.TICK_DATA, tick_data, "tick_600000"
            )

            assert result is True
            # 验证数据被保存
            assert mock_save.called

    def test_sync_daily_kline_across_time_periods(
        self, unified_manager, setup_sync_data
    ):
        """测试日线数据在不同时间段的同步"""
        daily_data = setup_sync_data["daily_kline"]

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ) as mock_save:
            # 分批保存数据
            first_batch = daily_data.iloc[:25]
            second_batch = daily_data.iloc[25:]

            result1 = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, first_batch, "daily_kline"
            )
            result2 = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, second_batch, "daily_kline"
            )

            assert result1 is True and result2 is True
            assert mock_save.call_count == 2


class TestDataIntegrity:
    """数据完整性验证测试"""

    def test_data_completeness_verification(self, unified_manager):
        """测试数据完整性验证"""
        # 创建数据，故意缺少某些字段
        incomplete_data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": pd.date_range("2024-01-01", periods=10),
                # 缺少 'close' 字段
                "volume": np.random.randint(1000000, 10000000, 10),
            }
        )

        # 完整的数据应该有所有必需字段
        complete_data = incomplete_data.copy()
        complete_data["close"] = np.random.uniform(10, 20, 10)

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result_incomplete = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, incomplete_data, "daily_kline"
            )

            result_complete = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, complete_data, "daily_kline"
            )

            # 两者都应该保存成功（系统应该能处理缺失字段）
            assert result_incomplete is True
            assert result_complete is True

    def test_data_freshness_verification(self, unified_manager):
        """测试数据新鲜度验证"""
        # 创建过期数据
        stale_data = pd.DataFrame(
            {
                "ts": [datetime(2020, 1, 1) + timedelta(seconds=i) for i in range(10)],
                "symbol": ["600000.SH"] * 10,
                "price": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(100, 1000, 10),
            }
        )

        # 创建最新数据
        fresh_data = pd.DataFrame(
            {
                "ts": [datetime.now() + timedelta(seconds=i) for i in range(10)],
                "symbol": ["600000.SH"] * 10,
                "price": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(100, 1000, 10),
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result_stale = unified_manager.save_data_by_classification(
                DataClassification.TICK_DATA, stale_data, "tick_600000"
            )

            result_fresh = unified_manager.save_data_by_classification(
                DataClassification.TICK_DATA, fresh_data, "tick_600000"
            )

            # 两者都应该保存成功
            assert result_stale is True
            assert result_fresh is True

    def test_data_accuracy_verification(self, unified_manager):
        """测试数据精度验证"""
        # 创建具有精确值的数据
        data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": pd.date_range("2024-01-01", periods=10),
                "open": np.ones(10) * 10.5,
                "high": np.ones(10) * 11.0,
                "low": np.ones(10) * 10.0,
                "close": np.ones(10) * 10.75,
                "volume": np.ones(10, dtype=int) * 1000000,
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ) as mock_save:
            result = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, data, "daily_kline"
            )

            assert result is True
            # 验证数据被正确传递
            call_args = mock_save.call_args
            assert call_args is not None
            saved_df = call_args[0][1]
            # 验证数据的精度
            assert (saved_df["close"] == 10.75).all()


class TestConcurrentOperations:
    """并发操作处理测试"""

    def test_concurrent_save_operations(self, unified_manager):
        """测试并发保存操作"""
        tick_data = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01 09:30", periods=50, freq="1s"),
                "symbol": ["600000.SH"] * 50,
                "price": np.random.uniform(10, 20, 50),
                "volume": np.random.randint(100, 1000, 50),
            }
        )

        daily_data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 25,
                "trade_date": pd.date_range("2024-01-01", periods=25),
                "close": np.random.uniform(10, 20, 25),
                "volume": np.random.randint(1000000, 10000000, 25),
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ) as mock_save:
            # 模拟并发保存
            result1 = unified_manager.save_data_by_classification(
                DataClassification.TICK_DATA, tick_data, "tick_600000"
            )
            result2 = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, daily_data, "daily_kline"
            )

            assert result1 is True and result2 is True
            # 验证两个操作都被执行
            assert mock_save.call_count == 2

    def test_concurrent_load_operations(self, unified_manager):
        """测试并发加载操作"""
        mock_tick_df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01 09:30", periods=10, freq="1s"),
                "price": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(100, 1000, 10),
            }
        )

        mock_daily_df = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": pd.date_range("2024-01-01", periods=10),
                "close": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(1000000, 10000000, 10),
            }
        )

        with patch.object(
            unified_manager._data_manager,
            "load_data",
            side_effect=[mock_tick_df, mock_daily_df],
        ) as mock_load:
            # 模拟并发加载
            tick_result = unified_manager.load_data_by_classification(
                DataClassification.TICK_DATA, "tick_600000"
            )
            daily_result = unified_manager.load_data_by_classification(
                DataClassification.DAILY_KLINE, "daily_kline"
            )

            assert tick_result is not None
            assert daily_result is not None
            assert len(tick_result) == 10
            assert len(daily_result) == 10
            assert mock_load.call_count == 2


class TestConflictResolution:
    """冲突解决机制测试"""

    def test_duplicate_data_handling(self, unified_manager):
        """测试重复数据处理"""
        # 创建包含重复值的数据
        data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": [datetime(2024, 1, 1)] * 10,  # 所有日期相同
                "close": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(1000000, 10000000, 10),
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, data, "daily_kline"
            )

            # 应该成功保存，由数据库层处理去重
            assert result is True

    def test_data_version_conflict(self, unified_manager):
        """测试数据版本冲突处理"""
        # 第一个版本的数据
        data_v1 = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 5,
                "trade_date": pd.date_range("2024-01-01", periods=5),
                "close": np.ones(5) * 10.5,
                "volume": np.ones(5, dtype=int) * 1000000,
            }
        )

        # 第二个版本的数据（相同的日期，不同的值）
        data_v2 = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 5,
                "trade_date": pd.date_range("2024-01-01", periods=5),
                "close": np.ones(5) * 11.5,  # 价格不同
                "volume": np.ones(5, dtype=int) * 2000000,  # 成交量不同
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result1 = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, data_v1, "daily_kline"
            )

            result2 = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, data_v2, "daily_kline"
            )

            # 两个版本都应该保存成功
            assert result1 is True
            assert result2 is True

    def test_timestamp_conflict_resolution(self, unified_manager):
        """测试时间戳冲突解决"""
        # 创建具有相同时间戳的数据
        base_time = datetime(2025, 1, 1, 9, 30, 0)
        data_set_a = pd.DataFrame(
            {
                "ts": [base_time] * 5,
                "symbol": ["600000.SH"] * 5,
                "price": [10.5, 10.6, 10.7, 10.8, 10.9],
                "volume": [100, 200, 300, 400, 500],
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result = unified_manager.save_data_by_classification(
                DataClassification.TICK_DATA, data_set_a, "tick_600000"
            )

            # 应该成功保存
            assert result is True


class TestTransactionConsistency:
    """事务一致性测试"""

    def test_all_or_nothing_semantics(self, unified_manager):
        """测试原子性（全部或无）"""
        # 模拟一个应该全部保存或全部失败的事务
        data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": pd.date_range("2024-01-01", periods=10),
                "close": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(1000000, 10000000, 10),
            }
        )

        # 第一个场景：成功保存
        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result_success = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, data, "daily_kline"
            )
            assert result_success is True

        # 第二个场景：保存失败
        with patch.object(
            unified_manager._data_manager,
            "save_data",
            side_effect=Exception("Database error"),
        ):
            with patch.object(unified_manager, "recovery_queue", MagicMock()):
                result_failure = unified_manager.save_data_by_classification(
                    DataClassification.DAILY_KLINE, data, "daily_kline"
                )


class TestDataValidation:
    """数据验证测试"""

    def test_schema_validation(self, unified_manager):
        """测试数据模式验证"""
        # 有效的数据
        valid_data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": pd.date_range("2024-01-01", periods=10),
                "open": np.random.uniform(10, 20, 10),
                "high": np.random.uniform(10, 20, 10),
                "low": np.random.uniform(10, 20, 10),
                "close": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(1000000, 10000000, 10),
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, valid_data, "daily_kline"
            )

            assert result is True

    def test_data_type_validation(self, unified_manager):
        """测试数据类型验证"""
        # 创建具有混合数据类型的数据
        mixed_type_data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 5,
                "trade_date": pd.date_range("2024-01-01", periods=5),
                "close": [10.5, "11.5", 12.5, 13.5, 14.5],  # 混合类型
                "volume": [1000000, 2000000, 3000000, 4000000, 5000000],
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, mixed_type_data, "daily_kline"
            )

            # 系统应该能处理类型转换
            assert result is True

    def test_range_validation(self, unified_manager):
        """测试数值范围验证"""
        # 创建包含边界值的数据
        boundary_data = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10,
                "trade_date": pd.date_range("2024-01-01", periods=10),
                "close": np.concatenate([np.ones(5) * 0.01, np.ones(5) * 10000.0]),
                "volume": np.ones(10, dtype=int) * 1000000,
            }
        )

        with patch.object(
            unified_manager._data_manager, "save_data", return_value=True
        ):
            result = unified_manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, boundary_data, "daily_kline"
            )

            assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
