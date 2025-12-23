#!/usr/bin/env python3
"""
DataManager源代码覆盖率测试
测试src/core/data_manager.py的实际业务逻辑和功能
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the actual modules we want to test
from src.core.data_manager import DataManager, _NullMonitoring
from src.core.data_classification import DataClassification, DatabaseTarget


class TestDataManagerCoverage:
    """DataManager源代码覆盖率测试"""

    @pytest.fixture
    def mock_db_manager(self):
        """Mock数据库管理器"""
        manager = MagicMock()
        manager.get_table_manager.return_value = MagicMock()
        return manager

    @pytest.fixture
    def sample_dataframe(self):
        """创建测试用的DataFrame"""
        return pd.DataFrame(
            {
                "symbol": ["600519", "000001"],
                "price": [1750.50, 12.35],
                "timestamp": [datetime.now(), datetime.now()],
                "volume": [1000, 2000],
            }
        )

    def test_null_monitoring_class(self):
        """测试_NullMonitoring类"""
        monitor = _NullMonitoring()

        # 测试所有方法都能调用而不出错
        operation_id = monitor.log_operation_start("test")
        assert operation_id == "null_operation_id"

        result = monitor.log_operation_result(operation_id, True, None)
        assert result is True

        result = monitor.log_operation("test_operation", "info", {"key": "value"})
        assert result is True

        result = monitor.record_performance_metric("test_metric", 1.5, {"unit": "ms"})
        assert result is True

    def test_data_manager_init_default(self):
        """测试DataManager默认初始化"""
        dm = DataManager()

        # 验证默认状态
        assert dm.enable_monitoring is False
        assert hasattr(dm, "_monitoring_db")
        assert hasattr(dm, "_performance_monitor")
        assert isinstance(dm._monitoring_db, _NullMonitoring)
        assert isinstance(dm._performance_monitor, _NullMonitoring)

    @patch("src.core.data_manager.get_monitoring_database")
    @patch("src.core.data_manager.get_performance_monitor")
    def test_data_manager_init_with_monitoring(self, mock_get_perf, mock_get_mon):
        """测试启用监控的初始化"""
        # 设置mock返回值
        mock_monitor = MagicMock()
        mock_perf = MagicMock()
        mock_get_mon.return_value = mock_monitor
        mock_get_perf.return_value = mock_perf

        dm = DataManager(enable_monitoring=True)

        # 验证监控组件被正确初始化
        assert dm.enable_monitoring is True
        assert dm._monitoring_db == mock_monitor
        assert dm._performance_monitor == mock_perf

    def test_data_manager_routing_map(self):
        """测试路由映射"""
        dm = DataManager()

        # 验证路由映射的正确性
        assert dm._ROUTING_MAP[DataClassification.TICK_DATA] == DatabaseTarget.TDENGINE
        assert (
            dm._ROUTING_MAP[DataClassification.DAILY_KLINE] == DatabaseTarget.POSTGRESQL
        )
        assert (
            dm._ROUTING_MAP[DataClassification.SYMBOLS_INFO]
            == DatabaseTarget.POSTGRESQL
        )
        assert (
            dm._ROUTING_MAP[DataClassification.TECHNICAL_INDICATORS]
            == DatabaseTarget.POSTGRESQL
        )
        assert (
            dm._ROUTING_MAP[DataClassification.ORDER_RECORDS]
            == DatabaseTarget.POSTGRESQL
        )
        assert (
            dm._ROUTING_MAP[DataClassification.DATA_SOURCE_STATUS]
            == DatabaseTarget.POSTGRESQL
        )

    def test_route_database_decision_time(self):
        """测试路由决策时间性能目标 (<5ms)"""
        dm = DataManager()

        import time

        # 测试路由决策性能
        start_time = time.time()
        for _ in range(1000):
            result = dm._route_database(DataClassification.TICK_DATA)
        end_time = time.time()

        avg_time = (end_time - start_time) / 1000 * 1000  # 转换为毫秒
        assert avg_time < 5.0, f"路由决策时间 {avg_time:.2f}ms 超过5ms目标"

    @patch("src.core.data_manager.get_data_access")
    @patch("src.core.data_manager.DatabaseTableManager")
    def test_route_database_method(self, mock_db_manager_class, mock_get_access):
        """测试_route_database方法"""
        dm = DataManager()

        # 测试不同数据分类的路由
        td_target = dm._route_database(DataClassification.TICK_DATA)
        assert td_target == DatabaseTarget.TDENGINE

        pg_target = dm._route_database(DataClassification.DAILY_KLINE)
        assert pg_target == DatabaseTarget.POSTGRESQL

    def test_get_database_name_classification_mapping(self):
        """测试数据分类到数据库名称的映射"""
        dm = DataManager()

        # 测试不同分类的数据库名称
        td_db = dm._get_database_name(DataClassification.TICK_DATA)
        assert td_db == "market_data"

        pg_db = dm._get_database_name(DataClassification.SYMBOLS_INFO)
        assert pg_db == "mystocks"

    @patch("src.core.data_manager.get_data_access")
    def test_get_table_name_logic(self, mock_get_access):
        """测试表名生成逻辑"""
        dm = DataManager()
        mock_access = MagicMock()
        mock_get_access.return_value = mock_access

        # 测试不同分类的表名生成
        dm._get_table_name(DataClassification.TICK_DATA, "600519")

        # 验证正确的方法被调用
        mock_access.create_table_name.assert_called_once()

    def test_logging_integration(self):
        """测试日志集成"""
        import logging

        # 创建一个测试日志捕获器
        logger = logging.getLogger("src.core.data_manager")

        with patch.object(logger, "info") as mock_info:
            dm = DataManager(enable_monitoring=False)

            # 验证初始化日志被记录
            mock_info.assert_called()

    def test_error_handling_in_init(self):
        """测试初始化中的错误处理"""
        with patch("src.core.data_manager.get_monitoring_database") as mock_get_mon:
            # 模拟监控初始化失败
            mock_get_mon.side_effect = Exception("监控初始化失败")

            dm = DataManager(enable_monitoring=True)

            # 验证错误被正确处理，回退到null监控
            assert dm.enable_monitoring is False
            assert isinstance(dm._monitoring_db, _NullMonitoring)

    def test_data_classification_coverage(self):
        """测试所有数据分类都有路由"""
        dm = DataManager()

        # 验证所有数据分类都有对应的路由
        for classification in DataClassification:
            if hasattr(classification, "value"):  # 只测试枚举值
                target = dm._route_database(classification)
                assert target in [DatabaseTarget.TDENGINE, DatabaseTarget.POSTGRESQL], (
                    f"数据分类 {classification} 没有对应的数据库路由"
                )

    def test_performance_metric_recording(self, mock_db_manager):
        """测试性能指标记录"""
        dm = DataManager(enable_monitoring=False, db_manager=mock_db_manager)

        # 测试性能指标记录不会出错
        dm._monitoring_db.record_performance_metric(
            "test_operation", 0.001, {"symbol": "600519", "table": "test_table"}
        )

    @patch("src.core.data_manager.get_data_access")
    def test_adapter_registration_logic(self, mock_get_access):
        """测试适配器注册逻辑"""
        dm = DataManager()
        mock_adapter = MagicMock()
        mock_access = MagicMock()
        mock_get_access.return_value = mock_access

        # 测试适配器注册
        dm.register_adapter("test_adapter", mock_adapter)

        # 验证适配器被正确注册
        assert "test_adapter" in dm._adapters
        assert dm._adapters["test_adapter"] == mock_adapter

    def test_database_manager_injection(self, mock_db_manager):
        """测试数据库管理器依赖注入"""
        dm = DataManager(db_manager=mock_db_manager)

        # 验证数据库管理器被正确注入
        assert dm._db_manager == mock_db_manager

    def test_resource_cleanup(self):
        """测试资源清理"""
        dm = DataManager()

        # 测试清理方法不会出错
        if hasattr(dm, "cleanup"):
            dm.cleanup()
        else:
            # 如果没有cleanup方法，验证其他资源管理
            assert hasattr(dm, "_monitoring_db")
            assert hasattr(dm, "_performance_monitor")


class TestDataManagerIntegration:
    """DataManager集成测试"""

    @pytest.fixture
    def integration_setup(self):
        """集成测试设置"""
        with (
            patch("src.core.data_manager.get_data_access") as mock_get_access,
            patch(
                "src.core.data_manager.DatabaseTableManager"
            ) as mock_db_manager_class,
        ):
            mock_access = MagicMock()
            mock_db_manager = MagicMock()
            mock_get_access.return_value = mock_access
            mock_db_manager_class.return_value = mock_db_manager

            yield {
                "dm": DataManager(db_manager=mock_db_manager),
                "mock_access": mock_access,
                "mock_db_manager": mock_db_manager,
            }

    def test_end_to_end_data_flow(self, integration_setup):
        """测试端到端数据流程"""
        dm = integration_setup["dm"]
        mock_access = integration_setup["mock_access"]
        mock_db_manager = integration_setup["mock_db_manager"]

        # 测试完整的数据流程
        classification = DataClassification.TICK_DATA
        table_name = "tick_test"

        # 验证路由决策
        target = dm._route_database(classification)
        assert target == DatabaseTarget.TDENGINE

        # 验证数据库名称获取
        db_name = dm._get_database_name(classification)
        assert db_name == "market_data"

        # 验证表名生成
        dm._get_table_name(classification, table_name)

    def test_concurrent_access_safety(self, integration_setup):
        """测试并发访问安全性"""
        dm = integration_setup["dm"]

        # 模拟并发访问
        import threading

        results = []

        def worker():
            try:
                for i in range(10):
                    target = dm._route_database(DataClassification.TICK_DATA)
                    results.append(target)
            except Exception as e:
                results.append(f"Error: {e}")

        threads = [threading.Thread(target=worker) for _ in range(5)]

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有操作都成功
        assert len(results) == 50
        assert all(r == DatabaseTarget.TDENGINE for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
