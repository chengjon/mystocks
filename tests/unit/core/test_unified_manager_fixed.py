#!/usr/bin/env python3
"""
统一管理器模块单元测试 - 源代码覆盖率测试 (修复版)

测试MyStocks系统中统一数据管理器的完整功能，包括委托模式、故障恢复和监控集成
"""

import pytest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.unified_manager import MyStocksUnifiedManager
from src.core.data_classification import DataClassification
from src.core.batch_failure_strategy import (
    BatchFailureStrategy,
    BatchOperationResult,
    BatchFailureHandler,
)


class TestMyStocksUnifiedManager:
    """测试统一管理器类"""

    @pytest.fixture
    def sample_dataframe(self):
        """创建示例DataFrame"""
        return pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=5, freq="1min"),
                "symbol": ["600000"] * 5,
                "price": [10.5, 10.6, 10.7, 10.8, 10.9],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

    @pytest.fixture
    def empty_dataframe(self):
        """创建空DataFrame"""
        return pd.DataFrame()

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_initialization_with_monitoring_enabled(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试初始化 - 启用监控"""
        # Mock监控组件可用
        with patch("src.core.unified_manager.MONITORING_AVAILABLE", True):
            with (
                patch(
                    "src.core.unified_manager.get_monitoring_database"
                ) as mock_monitoring_db,
                patch(
                    "src.core.unified_manager.get_performance_monitor"
                ) as mock_perf_monitor,
                patch(
                    "src.core.unified_manager.get_quality_monitor"
                ) as mock_quality_monitor,
                patch(
                    "src.core.unified_manager.get_alert_manager"
                ) as mock_alert_manager,
            ):
                manager = MyStocksUnifiedManager(enable_monitoring=True)

                # 验证DataManager被创建
                mock_data_manager.assert_called_once_with(enable_monitoring=True)

                # 验证监控组件被初始化
                mock_monitoring_db.assert_called_once()
                mock_perf_monitor.assert_called_once()
                mock_quality_monitor.assert_called_once()
                mock_alert_manager.assert_called_once()

                # 验证故障恢复队列被创建
                mock_recovery_queue.assert_called_once()

                # 验证属性设置
                assert manager.enable_monitoring is True
                assert manager._data_manager is not None
                assert manager.recovery_queue is not None

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_initialization_with_monitoring_disabled(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试初始化 - 禁用监控"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        # 验证DataManager被创建
        mock_data_manager.assert_called_once_with(enable_monitoring=False)

        # 验证监控组件未被初始化
        assert manager.enable_monitoring is False
        assert manager.monitoring_db is None
        assert manager.performance_monitor is None
        assert manager.quality_monitor is None
        assert manager.alert_manager is None

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_initialization_monitoring_unavailable(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试初始化 - 监控组件不可用"""
        with patch("src.core.unified_manager.MONITORING_AVAILABLE", False):
            manager = MyStocksUnifiedManager(enable_monitoring=True)

            # 验证监控被禁用
            assert manager.enable_monitoring is False
            assert manager.monitoring_db is None

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_initialization_monitoring_initialization_failure(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试初始化 - 监控组件初始化失败"""
        with patch("src.core.unified_manager.MONITORING_AVAILABLE", True):
            with patch(
                "src.core.unified_manager.get_monitoring_database",
                side_effect=Exception("监控初始化失败"),
            ):
                manager = MyStocksUnifiedManager(enable_monitoring=True)

                # 验证监控被禁用（回退机制）
                assert manager.enable_monitoring is False
                assert manager.monitoring_db is None

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_save_data_by_classification_success(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试按分类保存数据 - 成功"""
        # 设置Mock返回值
        mock_data_manager.return_value.save_data.return_value = True

        manager = MyStocksUnifiedManager()

        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA, sample_dataframe, "tick_600000"
        )

        assert result is True
        mock_data_manager.return_value.save_data.assert_called_once_with(
            DataClassification.TICK_DATA, sample_dataframe, "tick_600000"
        )

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_save_data_by_classification_empty_data(
        self, mock_recovery_queue, mock_data_manager, empty_dataframe
    ):
        """测试按分类保存数据 - 空数据"""
        manager = MyStocksUnifiedManager()

        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA, empty_dataframe, "tick_600000"
        )

        assert result is True
        # 验证DataManager未被调用
        mock_data_manager.return_value.save_data.assert_not_called()

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_save_data_by_classification_failure_with_recovery(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试按分类保存数据 - 失败并加入故障恢复队列"""
        # 设置Mock抛出异常
        mock_data_manager.return_value.save_data.side_effect = Exception(
            "数据库连接失败"
        )
        mock_recovery_queue_instance = mock_recovery_queue.return_value

        manager = MyStocksUnifiedManager()

        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA,
            sample_dataframe,
            "tick_600000",
            extra_param="test",
        )

        assert result is False
        # 验证故障恢复队列被调用
        mock_recovery_queue_instance.add_failed_operation.assert_called_once_with(
            operation_type="save",
            classification=DataClassification.TICK_DATA.value,
            data=sample_dataframe,
            table_name="tick_600000",
            kwargs={"extra_param": "test"},
            error="数据库连接失败",
        )

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_load_data_by_classification_success(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试按分类加载数据 - 成功"""
        # 设置Mock返回值
        mock_data_manager.return_value.load_data.return_value = sample_dataframe

        manager = MyStocksUnifiedManager()

        result = manager.load_data_by_classification(
            DataClassification.DAILY_KLINE, "daily_kline", symbol="600000"
        )

        assert result is not None
        assert len(result) == 5
        mock_data_manager.return_value.load_data.assert_called_once_with(
            DataClassification.DAILY_KLINE, "daily_kline", symbol="600000"
        )

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_load_data_by_classification_without_filters(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试按分类加载数据 - 无过滤条件"""
        # 设置Mock返回值
        mock_data_manager.return_value.load_data.return_value = sample_dataframe

        manager = MyStocksUnifiedManager()

        result = manager.load_data_by_classification(
            DataClassification.DAILY_KLINE, "daily_kline"
        )

        assert result is not None
        mock_data_manager.return_value.load_data.assert_called_once_with(
            DataClassification.DAILY_KLINE, "daily_kline"
        )

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_load_data_by_classification_failure(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试按分类加载数据 - 失败"""
        # 设置Mock抛出异常
        mock_data_manager.return_value.load_data.side_effect = Exception(
            "数据库查询失败"
        )

        manager = MyStocksUnifiedManager()

        result = manager.load_data_by_classification(
            DataClassification.DAILY_KLINE, "daily_kline"
        )

        assert result is None

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_get_routing_info(self, mock_recovery_queue, mock_data_manager):
        """测试获取路由信息"""
        # 设置Mock返回值
        from src.core.data_classification import DatabaseTarget

        mock_data_manager.return_value.get_target_database.return_value = (
            DatabaseTarget.POSTGRESQL
        )

        manager = MyStocksUnifiedManager()

        result = manager.get_routing_info(DataClassification.DAILY_KLINE)

        expected = {
            "classification": DataClassification.DAILY_KLINE.value,
            "target_db": DatabaseTarget.POSTGRESQL.value,
        }
        assert result == expected
        mock_data_manager.return_value.get_target_database.assert_called_once_with(
            DataClassification.DAILY_KLINE
        )

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_save_data_batch_with_strategy_continue_on_failure(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试批量保存数据 - 失败时继续策略"""
        # 创建一个简单的BatchFailureHandler mock
        with patch.object(BatchFailureHandler, "__init__", return_value=None):
            with patch.object(BatchFailureHandler, "get_result") as mock_get_result:
                # 设置Mock结果
                mock_result = BatchOperationResult(
                    total_records=5,
                    successful_records=3,
                    failed_records=2,
                    strategy_used=BatchFailureStrategy.CONTINUE,
                    execution_time_ms=100.0,
                )
                mock_get_result.return_value = mock_result

                manager = MyStocksUnifiedManager()

                # Mock save_data_by_classification方法
                manager.save_data_by_classification = Mock(
                    side_effect=[True, False, True]
                )

                result = manager.save_data_batch_with_strategy(
                    DataClassification.TICK_DATA,
                    sample_dataframe,
                    "tick_600000",
                    batch_size=2,
                    failure_strategy=BatchFailureStrategy.CONTINUE,
                )

                assert isinstance(result, BatchOperationResult)
                # 验证save_data_by_classification被调用了3次
                assert manager.save_data_by_classification.call_count == 3

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_save_data_batch_with_strategy_rollback_on_failure(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试批量保存数据 - 失败时回滚策略"""
        # 创建一个简单的BatchFailureHandler mock
        with patch.object(BatchFailureHandler, "__init__", return_value=None):
            with patch.object(BatchFailureHandler, "get_result") as mock_get_result:
                # 设置Mock结果
                mock_result = BatchOperationResult(
                    total_records=5,
                    successful_records=2,
                    failed_records=3,
                    strategy_used=BatchFailureStrategy.ROLLBACK,
                    execution_time_ms=100.0,
                    rollback_executed=True,
                )
                mock_get_result.return_value = mock_result

                manager = MyStocksUnifiedManager()

                # Mock save_data_by_classification方法
                manager.save_data_by_classification = Mock(side_effect=[True, False])

                result = manager.save_data_batch_with_strategy(
                    DataClassification.TICK_DATA,
                    sample_dataframe,
                    "tick_600000",
                    batch_size=2,
                    failure_strategy=BatchFailureStrategy.ROLLBACK,
                )

                assert isinstance(result, BatchOperationResult)
                # 验证save_data_by_classification被调用了2次
                assert manager.save_data_by_classification.call_count == 2

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_get_monitoring_statistics_with_monitoring_enabled(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试获取监控统计信息 - 启用监控"""
        # 设置Mock
        mock_data_manager.return_value.get_routing_stats.return_value = {
            "total_operations": 100
        }
        mock_perf_monitor = Mock()
        mock_perf_monitor.get_statistics.return_value = {"avg_response_time": 0.5}

        with patch("src.core.unified_manager.MONITORING_AVAILABLE", True):
            with patch(
                "src.core.unified_manager.get_performance_monitor",
                return_value=mock_perf_monitor,
            ):
                manager = MyStocksUnifiedManager(enable_monitoring=True)
                manager.performance_monitor = mock_perf_monitor

                result = manager.get_monitoring_statistics()

                assert (
                    result["manager_type"] == "MyStocksUnifiedManager (US3 Simplified)"
                )
                assert result["data_manager_stats"] == {"total_operations": 100}
                assert result["monitoring_enabled"] is True
                assert "performance" in result
                assert result["performance"] == {"avg_response_time": 0.5}
                assert "timestamp" in result

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_get_monitoring_statistics_with_monitoring_disabled(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试获取监控统计信息 - 禁用监控"""
        mock_data_manager.return_value.get_routing_stats.return_value = {
            "total_operations": 50
        }

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.get_monitoring_statistics()

        assert result["manager_type"] == "MyStocksUnifiedManager (US3 Simplified)"
        assert result["data_manager_stats"] == {"total_operations": 50}
        assert result["monitoring_enabled"] is False
        assert "performance" not in result
        assert "timestamp" in result

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_get_monitoring_statistics_performance_monitor_exception(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试获取监控统计信息 - 性能监控器异常"""
        # 设置Mock
        mock_data_manager.return_value.get_routing_stats.return_value = {
            "total_operations": 100
        }
        mock_perf_monitor = Mock()
        mock_perf_monitor.get_statistics.side_effect = Exception("监控异常")

        with patch("src.core.unified_manager.MONITORING_AVAILABLE", True):
            with patch(
                "src.core.unified_manager.get_performance_monitor",
                return_value=mock_perf_monitor,
            ):
                manager = MyStocksUnifiedManager(enable_monitoring=True)
                manager.performance_monitor = mock_perf_monitor

                result = manager.get_monitoring_statistics()

                # 验证异常被处理，性能统计不包含在结果中
                assert "performance" not in result
                assert result["monitoring_enabled"] is True

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_check_data_quality_success(
        self, mock_recovery_queue, mock_data_manager, sample_dataframe
    ):
        """测试检查数据质量 - 成功"""
        # 设置Mock
        mock_data_manager.return_value.load_data.return_value = sample_dataframe

        manager = MyStocksUnifiedManager()

        result = manager.check_data_quality(
            DataClassification.TICK_DATA, "tick_600000", symbol="600000"
        )

        assert result["classification"] == DataClassification.TICK_DATA.value
        assert result["table_name"] == "tick_600000"
        assert result["status"] == "success"
        assert result["row_count"] == 5
        assert result["column_count"] == 4
        assert "null_counts" in result
        assert "timestamp" in result

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_check_data_quality_no_data(self, mock_recovery_queue, mock_data_manager):
        """测试检查数据质量 - 无数据"""
        # 设置Mock返回None
        mock_data_manager.return_value.load_data.return_value = None

        manager = MyStocksUnifiedManager()

        result = manager.check_data_quality(DataClassification.TICK_DATA, "tick_600000")

        assert result["classification"] == DataClassification.TICK_DATA.value
        assert result["table_name"] == "tick_600000"
        assert result["status"] == "no_data"
        assert "timestamp" in result

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_check_data_quality_error(self, mock_recovery_queue, mock_data_manager):
        """测试检查数据质量 - 异常"""
        # 设置Mock抛出异常
        mock_data_manager.return_value.load_data.side_effect = Exception("查询失败")

        manager = MyStocksUnifiedManager()

        result = manager.check_data_quality(DataClassification.TICK_DATA, "tick_600000")

        assert result["classification"] == DataClassification.TICK_DATA.value
        assert result["table_name"] == "tick_600000"
        assert result["status"] == "error"
        assert result["error"] == "查询失败"
        assert "timestamp" in result

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_close_all_connections_success(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试关闭所有数据库连接 - 成功"""
        # 设置Mock数据库连接
        mock_tdengine = Mock()
        mock_postgresql = Mock()
        mock_data_manager.return_value._tdengine = mock_tdengine
        mock_data_manager.return_value._postgresql = mock_postgresql

        manager = MyStocksUnifiedManager()

        manager.close_all_connections()

        mock_tdengine.close.assert_called_once()
        mock_postgresql.close.assert_called_once()

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_close_all_connections_no_close_method(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试关闭所有数据库连接 - 连接对象没有close方法"""
        # 设置Mock数据库连接（没有close方法）
        mock_tdengine = Mock()
        mock_postgresql = Mock()
        del mock_tdengine.close
        del mock_postgresql.close

        mock_data_manager.return_value._tdengine = mock_tdengine
        mock_data_manager.return_value._postgresql = mock_postgresql

        manager = MyStocksUnifiedManager()

        # 应该不抛出异常
        manager.close_all_connections()

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_close_all_connections_exception(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试关闭所有数据库连接 - 异常"""
        # 设置Mock数据库连接抛出异常
        mock_tdengine = Mock()
        mock_postgresql = Mock()
        mock_tdengine.close.side_effect = Exception("关闭失败")

        mock_data_manager.return_value._tdengine = mock_tdengine
        mock_data_manager.return_value._postgresql = mock_postgresql

        manager = MyStocksUnifiedManager()

        # 应该不抛出异常，只记录日志
        manager.close_all_connections()

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_destructor_calls_close_all_connections(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试析构函数调用关闭所有连接"""
        manager = MyStocksUnifiedManager()
        manager.close_all_connections = Mock()

        # 调用析构函数
        manager.__del__()

        manager.close_all_connections.assert_called_once()

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_destructor_exception_handling(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试析构函数异常处理"""
        manager = MyStocksUnifiedManager()
        manager.close_all_connections = Mock(side_effect=Exception("析构异常"))

        # 调用析构函数应该不抛出异常
        try:
            manager.__del__()
        except Exception:
            pytest.fail("析构函数不应该抛出异常")

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_backward_compatibility_attributes(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试向后兼容性属性"""
        mock_tdengine = Mock()
        mock_postgresql = Mock()
        mock_data_manager.return_value._tdengine = mock_tdengine
        mock_data_manager.return_value._postgresql = mock_postgresql

        manager = MyStocksUnifiedManager()

        # 验证向后兼容性属性
        assert manager.tdengine is mock_tdengine
        assert manager.postgresql is mock_postgresql


class TestEdgeCasesAndIntegration:
    """测试边界情况和集成"""

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_large_dataframe_batch_processing(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试大DataFrame的批量处理"""
        # 创建大DataFrame（100行）
        large_df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=100, freq="1min"),
                "value": range(100),
            }
        )

        mock_data_manager.return_value.save_data.return_value = True

        manager = MyStocksUnifiedManager()

        # Mock BatchFailureHandler
        with patch.object(BatchFailureHandler, "__init__", return_value=None):
            with patch.object(BatchFailureHandler, "get_result") as mock_get_result:
                mock_get_result.return_value = BatchOperationResult(
                    total_records=100,
                    successful_records=100,
                    failed_records=0,
                    strategy_used=BatchFailureStrategy.CONTINUE,
                    execution_time_ms=200.0,
                )

                result = manager.save_data_batch_with_strategy(
                    DataClassification.TICK_DATA, large_df, "large_table", batch_size=25
                )

                assert isinstance(result, BatchOperationResult)
                assert result.total_records == 100

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_dataclassification_all_values(
        self, mock_recovery_queue, mock_data_manager
    ):
        """测试所有数据分类值"""
        mock_data_manager.return_value.save_data.return_value = True
        mock_data_manager.return_value.load_data.return_value = pd.DataFrame(
            {"test": [1]}
        )
        from src.core.data_classification import DatabaseTarget

        mock_data_manager.return_value.get_target_database.return_value = (
            DatabaseTarget.POSTGRESQL
        )

        manager = MyStocksUnifiedManager()
        sample_df = pd.DataFrame({"test": [1]})

        # 测试所有数据分类枚举值
        for classification in DataClassification:
            # 测试保存
            save_result = manager.save_data_by_classification(
                classification, sample_df, "test_table"
            )
            assert isinstance(save_result, bool)

            # 测试加载
            load_result = manager.load_data_by_classification(
                classification, "test_table"
            )
            assert load_result is not None

            # 测试路由信息
            routing_info = manager.get_routing_info(classification)
            assert "classification" in routing_info
            assert "target_db" in routing_info

    @patch("src.core.unified_manager.DataManager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    def test_batch_failure_strategies_all(self, mock_recovery_queue, mock_data_manager):
        """测试所有批量故障策略"""
        sample_df = pd.DataFrame({"test": range(10)})
        mock_data_manager.return_value.save_data.return_value = True

        manager = MyStocksUnifiedManager()

        # 测试所有故障策略
        for strategy in BatchFailureStrategy:
            with patch.object(BatchFailureHandler, "__init__", return_value=None):
                with patch.object(BatchFailureHandler, "get_result") as mock_get_result:
                    mock_get_result.return_value = BatchOperationResult(
                        total_records=10,
                        successful_records=10,
                        failed_records=0,
                        strategy_used=strategy,
                        execution_time_ms=100.0,
                    )

                    result = manager.save_data_batch_with_strategy(
                        DataClassification.TICK_DATA,
                        sample_df,
                        "test_table",
                        batch_size=3,
                        failure_strategy=strategy,
                    )

                    assert isinstance(result, BatchOperationResult)
                    assert result.strategy_used == strategy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
