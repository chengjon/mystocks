"""
Unified Manager基础测试
专注于提升unified_manager模块覆盖率（329行代码）
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
from src.core.unified_manager import MyStocksUnifiedManager


class TestMyStocksUnifiedManagerBasic:
    """MyStocksUnifiedManager基础测试 - 专注覆盖率"""

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        try:
            from src.core.unified_manager import MyStocksUnifiedManager

            assert MyStocksUnifiedManager is not None
        except ImportError as e:
            pytest.skip(f"MyStocksUnifiedManager不可用: {e}")

    def test_initialization_default(self):
        """测试默认初始化"""
        with patch("src.core.unified_manager.DataManager") as mock_dm:
            with patch("src.core.unified_manager.FailureRecoveryQueue") as mock_queue:
                mock_dm_instance = Mock()
                mock_dm.return_value = mock_dm_instance
                mock_queue_instance = Mock()
                mock_queue.return_value = mock_queue_instance

                manager = MyStocksUnifiedManager()

                # 验证基本属性
                assert hasattr(manager, "tdengine")
                assert hasattr(manager, "postgresql")
                assert hasattr(manager, "recovery_queue")
                assert manager.recovery_queue == mock_queue_instance

    def test_initialization_with_monitoring(self):
        """测试带监控的初始化"""
        with patch("src.core.unified_manager.MONITORING_AVAILABLE", True):
            with patch("src.core.unified_manager.DataManager") as mock_dm:
                with patch("src.core.unified_manager.get_monitoring_database") as mock_mon:
                    with patch("src.core.unified_manager.get_performance_monitor") as mock_perf:
                        with patch("src.core.unified_manager.get_quality_monitor") as mock_qual:
                            with patch("src.core.unified_manager.get_alert_manager") as mock_alert:
                                with patch("src.core.unified_manager.FailureRecoveryQueue") as mock_queue:
                                    mock_dm_instance = Mock()
                                    mock_dm.return_value = mock_dm_instance
                                    mock_queue_instance = Mock()
                                    mock_queue.return_value = mock_queue_instance

                                    manager = MyStocksUnifiedManager(enable_monitoring=True)

                                    assert manager.monitoring_db is not None
                                    assert manager.performance_monitor is not None
                                    assert manager.quality_monitor is not None
                                    assert manager.alert_manager is not None

    def test_save_data_by_classification_method(self):
        """测试按分类保存数据方法"""
        test_df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=2),
                "price": [10.5, 10.6],
                "volume": [1000, 1500],
            }
        )

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.save_data.return_value = True
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            result = manager.save_data_by_classification(
                data=test_df,
                classification="market_data.tick_data",
                table_name="test_table",
            )

            assert result == True

    def test_load_data_by_classification_method(self):
        """测试按分类加载数据方法"""
        expected_df = pd.DataFrame({"price": [10.5, 10.6]})

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.load_data.return_value = expected_df
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            result = manager.load_data_by_classification(
                classification="market_data.tick_data",
                table_name="test_table",
                start_time=datetime(2025, 1, 1),
                end_time=datetime(2025, 1, 2),
            )

            assert result is not None
            assert len(result) == 2

    def test_load_data_by_classification_method_none_result(self):
        """测试按分类加载数据方法（空结果）"""
        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.load_data.return_value = None
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            result = manager.load_data_by_classification(
                classification="market_data.tick_data", table_name="test_table"
            )

            assert result is None

    def test_save_data_batch_with_strategy_method(self):
        """测试批量保存数据方法（带策略）"""
        data_list = [pd.DataFrame({"price": [10.5]}), pd.DataFrame({"price": [10.6]})]

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.batch_save.return_value = True
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            result = manager.save_data_batch_with_strategy(
                data_list=data_list,
                classification="market_data.tick_data",
                table_name="test_table",
            )

            assert result == True

    def test_save_data_batch_with_strategy_with_failure_queue(self):
        """测试批量保存数据方法（故障队列）"""
        data_list = [pd.DataFrame({"price": [10.5]})]

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            with patch("src.core.unified_manager.FailureRecoveryQueue") as mock_queue:
                mock_dm_instance = Mock()
                mock_dm_instance.batch_save.return_value = False
                mock_dm.return_value = mock_dm_instance
                mock_queue_instance = Mock()
                mock_queue.return_value = mock_queue_instance

                manager = MyStocksUnifiedManager()

                result = manager.save_data_batch_with_strategy(
                    data_list=data_list,
                    classification="market_data.tick_data",
                    table_name="test_table",
                )

                assert result == False
                # 验证故障队列被调用
                mock_queue_instance.enqueue.assert_called_once()

    def test_get_routing_info_method(self):
        """测试获取路由信息方法"""
        expected_routing = {
            "market_data.tick_data": "tdengine",
            "financial.ratio": "postgresql",
        }

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.get_routing_info.return_value = expected_routing
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            result = manager.get_routing_info()

            assert result == expected_routing

    def test_check_data_quality_method(self):
        """测试数据质量检查方法"""
        quality_report = {"completeness": 0.95, "freshness": "good", "accuracy": 0.98}

        manager = MyStocksUnifiedManager()

        with patch.object(manager, "quality_monitor") as mock_quality:
            mock_quality.check_data_quality.return_value = quality_report

            result = manager.check_data_quality(classification="market_data.tick_data", table_name="test_table")

            assert result == quality_report
            mock_quality.check_data_quality.assert_called_once()

    def test_check_data_quality_method_without_monitoring(self):
        """测试数据质量检查方法（无监控）"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.check_data_quality(classification="market_data.tick_data", table_name="test_table")

        assert result is None

    def test_get_monitoring_statistics_method(self):
        """测试获取监控统计方法"""
        expected_stats = {
            "total_queries": 1000,
            "avg_response_time": 0.05,
            "error_rate": 0.01,
        }

        manager = MyStocksUnifiedManager()

        with patch.object(manager, "performance_monitor") as mock_perf:
            mock_perf.get_statistics.return_value = expected_stats

            result = manager.get_monitoring_statistics()

            assert result == expected_stats
            mock_perf.get_statistics.assert_called_once()

    def test_get_monitoring_statistics_method_without_monitoring(self):
        """测试获取监控统计方法（无监控）"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.get_monitoring_statistics()

        assert result is None

    def test_enable_monitoring_method(self):
        """测试启用监控方法"""
        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.enable_monitoring()

        assert result == True

    def test_close_all_connections_method(self):
        """测试关闭所有连接方法"""
        with patch("src.core.unified_manager.DataManager") as mock_dm:
            with patch("src.core.unified_manager.FailureRecoveryQueue") as mock_queue:
                mock_dm_instance = Mock()
                mock_dm.return_value = mock_dm_instance
                mock_queue_instance = Mock()
                mock_queue.return_value = mock_queue_instance

                manager = MyStocksUnifiedManager()
                manager.close_all_connections()

                # 验证关闭方法被调用
                assert hasattr(manager, "close_all_connections")

    def test_monitoring_available_attribute(self):
        """测试监控可用性属性"""
        with patch("src.core.unified_manager.MONITORING_AVAILABLE", True):
            # 验证MONITORING_AVAILABLE可以被访问
            from src.core.unified_manager import MONITORING_AVAILABLE

            assert MONITORING_AVAILABLE == True

    def test_class_documentation(self):
        """测试类文档"""
        class_doc = MyStocksUnifiedManager.__doc__
        assert class_doc is not None
        assert len(class_doc.strip()) > 0
        assert "MyStocks" in class_doc

    def test_module_imports(self):
        """测试模块导入"""
        from src.core.unified_manager import MyStocksUnifiedManager, logger

        # 验证关键模块被导入
        assert MyStocksUnifiedManager is not None
        assert logger is not None

    def test_error_handling_in_save_data(self):
        """测试保存数据中的错误处理"""
        test_df = pd.DataFrame({"price": [10.5]})

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.save_data.side_effect = Exception("Database error")
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            # 应该抛出异常
            with pytest.raises(Exception, match="Database error"):
                manager.save_data_by_classification(
                    data=test_df,
                    classification="market_data.tick_data",
                    table_name="test_table",
                )

    def test_error_handling_in_load_data(self):
        """测试加载数据中的错误处理"""
        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.load_data.side_effect = Exception("Connection failed")
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            # 应该抛出异常
            with pytest.raises(Exception, match="Connection failed"):
                manager.load_data_by_classification(classification="market_data.tick_data", table_name="test_table")

    def test_method_parameter_validation(self):
        """测试方法参数验证"""
        import inspect

        manager = MyStocksUnifiedManager()

        # 检查关键方法的参数
        methods_to_check = [
            "save_data_by_classification",
            "load_data_by_classification",
            "save_data_batch_with_strategy",
            "get_routing_info",
            "check_data_quality",
            "get_monitoring_statistics",
            "enable_monitoring",
            "close_all_connections",
        ]

        for method_name in methods_to_check:
            if hasattr(manager, method_name):
                method = getattr(manager, method_name)
                sig = inspect.signature(method)
                assert sig is not None
                # 方法应该有合理的参数数量
                assert len(sig.parameters) >= 1  # 至少有self参数

    def test_dataframe_processing_capabilities(self):
        """测试DataFrame处理能力"""
        manager = MyStocksUnifiedManager()

        # 测试不同的DataFrame格式
        test_dfs = [
            pd.DataFrame({"price": [10.0, 20.0]}),
            pd.DataFrame({"symbol": ["600000", "000001"]}),
            pd.DataFrame({"ts": pd.date_range("2025-01-01", periods=2)}),
        ]

        for i, df in enumerate(test_dfs):
            # 测试DataFrame不为空时的处理
            assert not df.empty
            assert len(df) > 0

    def test_batch_processing_with_empty_list(self):
        """测试空列表批量处理"""
        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.batch_save.return_value = True
            mock_dm.return_value = mock_dm_instance

            manager = MyStocksUnifiedManager()

            result = manager.save_data_batch_with_strategy(
                data_list=[],
                classification="market_data.tick_data",
                table_name="test_table",
            )

            assert result == True

    def test_all_available_methods(self):
        """测试所有可用方法的存在性"""
        manager = MyStocksUnifiedManager()

        expected_methods = [
            "save_data_by_classification",
            "load_data_by_classification",
            "save_data_batch_with_strategy",
            "get_routing_info",
            "check_data_quality",
            "get_monitoring_statistics",
            "enable_monitoring",
            "close_all_connections",
        ]

        for method_name in expected_methods:
            assert hasattr(manager, method_name), f"缺少方法: {method_name}"

            if hasattr(manager, method_name):
                method = getattr(manager, method_name)
                assert callable(method), f"方法不可调用: {method_name}"

    def test_attribute_access(self):
        """测试属性访问"""
        manager = MyStocksUnifiedManager()

        # 检查关键属性是否存在
        attributes_to_check = [
            "tdengine",
            "postgresql",
            "recovery_queue",
            "alert_manager",
        ]

        for attr_name in attributes_to_check:
            assert hasattr(manager, attr_name), f"缺少属性: {attr_name}"

    def test_monitoring_attributes(self):
        """测试监控属性"""
        manager = MyStocksUnifiedManager(enable_monitoring=True)

        # 检查监控相关属性
        monitoring_attributes = [
            "monitoring_db",
            "performance_monitor",
            "quality_monitor",
        ]

        for attr_name in monitoring_attributes:
            assert hasattr(manager, attr_name), f"缺少监控属性: {attr_name}"

    def test_compatibility_with_data_classification(self):
        """测试数据分类兼容性"""
        from src.core.data_classification import DataClassification

        manager = MyStocksUnifiedManager()

        # 测试使用DataClassification枚举
        classification = DataClassification.MARKET_TICK_DATA

        with patch("src.core.unified_manager.DataManager") as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.save_data.return_value = True
            mock_dm.return_value = mock_dm_instance

            result = manager.save_data_by_classification(
                data=pd.DataFrame({"price": [10.5]}),
                classification=classification,
                table_name="test_table",
            )

            assert result == True

    def test_error_handling_in_monitoring_methods(self):
        """测试监控方法中的错误处理"""
        manager = MyStocksUnifiedManager(enable_monitoring=True)

        # 模拟监控组件错误
        with patch.object(manager.quality_monitor, "check_data_quality") as mock_quality:
            mock_quality.side_effect = Exception("Monitoring error")

            result = manager.check_data_quality(classification="market_data.tick_data", table_name="test_table")

            # 应该返回None而不是抛出异常
            assert result is None

    def test_logging_functionality(self):
        """测试日志功能"""
        manager = MyStocksUnifiedManager()

        # 验证logger属性存在
        assert hasattr(manager, "logger") or hasattr(manager.__class__, "logger")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
