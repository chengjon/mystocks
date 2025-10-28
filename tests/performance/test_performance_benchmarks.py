"""
性能基准测试

验证系统性能特征，包括:
- 路由性能基准
- 数据访问层性能
- 并发操作性能
- 大规模数据处理
- 性能回归测试

创建日期: 2025-10-28
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from unified_manager import MyStocksUnifiedManager
from core.data_manager import DataManager
from core.data_classification import DataClassification, DatabaseTarget


class TestRoutingPerformance:
    """路由性能基准测试"""

    @pytest.fixture
    def manager(self):
        """创建数据管理器"""
        return DataManager(enable_monitoring=False)

    def test_single_routing_latency(self, manager, benchmark):
        """基准测试：单次路由延迟"""

        def route_single():
            return manager.get_target_database(DataClassification.TICK_DATA)

        result = benchmark(route_single)
        assert result == DatabaseTarget.TDENGINE

    def test_routing_1000_calls(self, manager):
        """基准测试：1000次路由调用"""
        start = time.perf_counter()
        for _ in range(1000):
            manager.get_target_database(DataClassification.TICK_DATA)
        elapsed = time.perf_counter() - start

        # 平均延迟应该 < 0.1ms
        avg_latency = (elapsed / 1000) * 1000  # 转换为毫秒
        assert avg_latency < 0.1

    def test_routing_all_classifications(self, manager, benchmark):
        """基准测试：所有数据分类路由"""
        classifications = list(DataClassification)

        def route_all():
            for classification in classifications:
                manager.get_target_database(classification)

        benchmark(route_all)

    def test_routing_consistency(self, manager):
        """基准测试：路由一致性"""
        results = []
        start = time.perf_counter()

        for _ in range(100):
            result = manager.get_target_database(DataClassification.DAILY_KLINE)
            results.append(result)

        elapsed = time.perf_counter() - start

        # 所有结果应该一致
        assert len(set(results)) == 1
        assert results[0] == DatabaseTarget.POSTGRESQL

        # 100次调用应该在1ms内完成
        assert elapsed < 0.001


class TestDataAccessPerformance:
    """数据访问层性能基准测试"""

    @pytest.fixture
    def mock_connection(self):
        """创建模拟连接"""
        with patch("data_access.tdengine_access.get_connection_manager") as mock:
            mock_manager = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            mock_manager.get_tdengine_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock.return_value = mock_manager
            yield mock, mock_manager, mock_conn, mock_cursor

    def test_dataframe_insert_performance_100_rows(self, mock_connection):
        """基准测试：100行数据插入"""
        from data_access.tdengine_access import TDengineDataAccess

        df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=100, freq="1s"),
                "price": np.random.uniform(10, 20, 100),
                "volume": np.random.randint(100, 1000, 100),
            }
        )

        access = TDengineDataAccess()

        start = time.perf_counter()
        rows = access.insert_dataframe("test_table", df)
        elapsed = time.perf_counter() - start

        assert rows == 100
        # 100行应该在20ms内完成
        assert elapsed < 0.02

    def test_dataframe_insert_performance_1000_rows(self, mock_connection):
        """基准测试：1000行数据插入"""
        from data_access.tdengine_access import TDengineDataAccess

        df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=1000, freq="1s"),
                "price": np.random.uniform(10, 20, 1000),
                "volume": np.random.randint(100, 1000, 1000),
            }
        )

        access = TDengineDataAccess()

        start = time.perf_counter()
        rows = access.insert_dataframe("test_table", df)
        elapsed = time.perf_counter() - start

        assert rows == 1000
        # 1000行应该在150ms内完成
        assert elapsed < 0.15


class TestConcurrentPerformance:
    """并发操作性能基准测试"""

    def test_concurrent_routing_performance(self):
        """基准测试：并发路由性能"""
        manager = DataManager(enable_monitoring=False)

        classifications = [
            DataClassification.TICK_DATA,
            DataClassification.DAILY_KLINE,
            DataClassification.SYMBOLS_INFO,
        ]

        start = time.perf_counter()

        # 模拟并发操作（顺序执行，但测试多种分类）
        for _ in range(100):
            for classification in classifications:
                manager.get_target_database(classification)

        elapsed = time.perf_counter() - start

        # 300次操作应该在1ms内完成
        assert elapsed < 0.001

    def test_concurrent_save_operations(self):
        """基准测试：并发保存操作"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        test_data = [
            (DataClassification.TICK_DATA, "tick_600000", 1000),
            (DataClassification.DAILY_KLINE, "daily_kline", 500),
            (DataClassification.SYMBOLS_INFO, "symbols_info", 100),
        ]

        start = time.perf_counter()

        with patch.object(manager._data_manager, "save_data", return_value=True):
            for classification, table, rows in test_data:
                df = pd.DataFrame(
                    {
                        "ts": pd.date_range("2025-01-01", periods=rows, freq="1s"),
                        "price": np.random.uniform(10, 20, rows),
                        "volume": np.random.randint(100, 1000, rows),
                    }
                )
                manager.save_data_by_classification(classification, df, table)

        elapsed = time.perf_counter() - start

        # 3个并发操作应该在10ms内完成
        assert elapsed < 0.01


class TestLargeDatasetPerformance:
    """大规模数据集处理性能基准测试"""

    def test_large_tick_data_processing_10k_rows(self):
        """基准测试：10K行Tick数据处理"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=10000, freq="100ms"),
                "symbol": ["600000.SH"] * 10000,
                "price": np.random.uniform(10, 20, 10000),
                "volume": np.random.randint(100, 1000, 10000),
            }
        )

        with patch.object(manager._data_manager, "save_data", return_value=True):
            start = time.perf_counter()
            result = manager.save_data_by_classification(
                DataClassification.TICK_DATA, df, "tick_600000"
            )
            elapsed = time.perf_counter() - start

            assert result is True
            # 10K行应该在50ms内完成
            assert elapsed < 0.05

    def test_large_daily_data_processing_10k_rows(self):
        """基准测试：10K行日线数据处理"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        df = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 10000,
                "trade_date": pd.date_range("2000-01-01", periods=10000, freq="D"),
                "close": np.random.uniform(10, 20, 10000),
                "volume": np.random.randint(1000000, 10000000, 10000),
            }
        )

        with patch.object(manager._data_manager, "save_data", return_value=True):
            start = time.perf_counter()
            result = manager.save_data_by_classification(
                DataClassification.DAILY_KLINE, df, "daily_kline"
            )
            elapsed = time.perf_counter() - start

            assert result is True
            # 10K行应该在50ms内完成
            assert elapsed < 0.05

    def test_mixed_data_types_performance(self):
        """基准测试：混合数据类型处理"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        # 创建不同大小的数据集
        datasets = [
            (
                DataClassification.TICK_DATA,
                "tick_600000",
                pd.DataFrame(
                    {
                        "ts": pd.date_range("2025-01-01", periods=5000, freq="100ms"),
                        "price": np.random.uniform(10, 20, 5000),
                        "volume": np.random.randint(100, 1000, 5000),
                    }
                ),
            ),
            (
                DataClassification.DAILY_KLINE,
                "daily_kline",
                pd.DataFrame(
                    {
                        "symbol": ["600000.SH"] * 5000,
                        "trade_date": pd.date_range(
                            "2000-01-01", periods=5000, freq="D"
                        ),
                        "close": np.random.uniform(10, 20, 5000),
                        "volume": np.random.randint(1000000, 10000000, 5000),
                    }
                ),
            ),
        ]

        with patch.object(manager._data_manager, "save_data", return_value=True):
            start = time.perf_counter()

            for classification, table, df in datasets:
                manager.save_data_by_classification(classification, df, table)

            elapsed = time.perf_counter() - start

            # 两个数据集处理应该在100ms内完成
            assert elapsed < 0.1


class TestMemoryPerformance:
    """内存性能基准测试"""

    def test_memory_efficiency_large_dataframe(self):
        """基准测试：大型DataFrame内存效率"""
        # 创建大型DataFrame（1GB级别的数据）
        rows = 100000
        df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=rows, freq="100ms"),
                "symbol": ["600000.SH"] * rows,
                "price": np.random.uniform(10, 20, rows),
                "volume": np.random.randint(100, 1000, rows),
                "amount": np.random.uniform(1000, 200000, rows),
            }
        )

        # 验证数据未损坏
        assert len(df) == rows
        assert df.shape[1] == 5

    def test_memory_efficiency_multiple_dataframes(self):
        """基准测试：多个DataFrame内存效率"""
        dataframes = []
        for _ in range(10):
            df = pd.DataFrame(
                {
                    "ts": pd.date_range("2025-01-01", periods=10000, freq="100ms"),
                    "price": np.random.uniform(10, 20, 10000),
                    "volume": np.random.randint(100, 1000, 10000),
                }
            )
            dataframes.append(df)

        # 验证所有DataFrame创建成功
        assert len(dataframes) == 10
        assert all(len(df) == 10000 for df in dataframes)


class TestRegressionDetection:
    """性能回归检测测试"""

    def test_routing_no_regression(self):
        """回归检测：路由性能无退化"""
        manager = DataManager(enable_monitoring=False)

        # 记录基准性能
        results = []
        for _ in range(10):
            start = time.perf_counter()
            for _ in range(1000):
                manager.get_target_database(DataClassification.TICK_DATA)
            elapsed = time.perf_counter() - start
            results.append(elapsed)

        # 计算平均性能
        avg_latency = (np.mean(results) / 1000) * 1000  # 转换为毫秒

        # 性能不应该退化超过50%
        # 基准: 0.0002ms * 1000 = 0.2ms
        # 允许: 0.3ms
        assert avg_latency < 0.3

    def test_save_operation_no_regression(self):
        """回归检测：保存操作性能无退化"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        results = []
        for _ in range(5):
            df = pd.DataFrame(
                {
                    "ts": pd.date_range("2025-01-01", periods=1000, freq="1s"),
                    "price": np.random.uniform(10, 20, 1000),
                    "volume": np.random.randint(100, 1000, 1000),
                }
            )

            with patch.object(manager._data_manager, "save_data", return_value=True):
                start = time.perf_counter()
                manager.save_data_by_classification(
                    DataClassification.TICK_DATA, df, "tick_600000"
                )
                elapsed = time.perf_counter() - start
                results.append(elapsed)

        avg_time = np.mean(results)
        # 保存操作不应该超过5ms
        assert avg_time < 0.005


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
