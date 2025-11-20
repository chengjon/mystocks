"""
data_manager 模块单元测试

测试DataManager核心数据管理类的功能:
- _NullMonitoring空对象模式
- DataManager初始化和配置
- 适配器注册管理
- 数据路由决策
- 数据保存和加载
- 健康检查和统计
"""

import pytest
import sys
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from datetime import datetime

# 确保能导入src模块
sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.core.data_classification import DataClassification, DatabaseTarget


class TestNullMonitoring:
    """测试_NullMonitoring空对象模式"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_null_monitoring_log_operation_start(self, mock_pg, mock_td):
        """测试log_operation_start返回固定ID"""
        from src.core.data_manager import _NullMonitoring

        null_monitor = _NullMonitoring()
        result = null_monitor.log_operation_start("test", key="value")

        assert result == "null_operation_id"

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_null_monitoring_log_operation_result(self, mock_pg, mock_td):
        """测试log_operation_result总是返回True"""
        from src.core.data_manager import _NullMonitoring

        null_monitor = _NullMonitoring()
        result = null_monitor.log_operation_result("op_id", success=True)

        assert result is True

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_null_monitoring_log_operation(self, mock_pg, mock_td):
        """测试log_operation总是返回True"""
        from src.core.data_manager import _NullMonitoring

        null_monitor = _NullMonitoring()
        result = null_monitor.log_operation("test_operation")

        assert result is True

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_null_monitoring_record_performance_metric(self, mock_pg, mock_td):
        """测试record_performance_metric总是返回True"""
        from src.core.data_manager import _NullMonitoring

        null_monitor = _NullMonitoring()
        result = null_monitor.record_performance_metric("metric", value=100)

        assert result is True

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_null_monitoring_record_operation(self, mock_pg, mock_td):
        """测试record_operation总是返回True"""
        from src.core.data_manager import _NullMonitoring

        null_monitor = _NullMonitoring()
        result = null_monitor.record_operation("operation", duration=50)

        assert result is True

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_null_monitoring_log_quality_check(self, mock_pg, mock_td):
        """测试log_quality_check总是返回True"""
        from src.core.data_manager import _NullMonitoring

        null_monitor = _NullMonitoring()
        result = null_monitor.log_quality_check("check", passed=True)

        assert result is True


class TestDataManagerInitialization:
    """测试DataManager初始化"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_initialization_without_monitoring(self, mock_pg, mock_td):
        """测试不启用监控的初始化"""
        from src.core.data_manager import DataManager

        dm = DataManager(enable_monitoring=False)

        assert dm.enable_monitoring is False
        assert dm._monitoring_db is not None  # Should be _NullMonitoring
        assert dm._performance_monitor is not None
        assert dm._tdengine is not None
        assert dm._postgresql is not None
        assert isinstance(dm._adapters, dict)
        assert len(dm._adapters) == 0

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_initialization_databases_created(self, mock_pg, mock_td):
        """测试数据库访问层被创建"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        # 验证数据库访问层被创建
        assert mock_td.called
        assert mock_pg.called

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_routing_map_complete(self, mock_pg, mock_td):
        """测试路由映射包含所有数据分类"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        # 验证路由映射包含所有分类
        all_classifications = list(DataClassification)
        for classification in all_classifications:
            target = dm._ROUTING_MAP.get(classification)
            assert target is not None
            assert isinstance(target, DatabaseTarget)


class TestDataManagerAdapterManagement:
    """测试DataManager适配器管理"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_register_adapter(self, mock_pg, mock_td):
        """测试注册适配器"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        mock_adapter = Mock()

        dm.register_adapter("test_adapter", mock_adapter)

        assert "test_adapter" in dm._adapters
        assert dm._adapters["test_adapter"] == mock_adapter

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_register_adapter_overwrite(self, mock_pg, mock_td):
        """测试覆盖已存在的适配器"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        old_adapter = Mock()
        new_adapter = Mock()

        dm.register_adapter("adapter", old_adapter)
        dm.register_adapter("adapter", new_adapter)

        assert dm._adapters["adapter"] == new_adapter

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_unregister_adapter_success(self, mock_pg, mock_td):
        """测试注销适配器成功"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        mock_adapter = Mock()
        dm.register_adapter("adapter", mock_adapter)

        result = dm.unregister_adapter("adapter")

        assert result is True
        assert "adapter" not in dm._adapters

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_unregister_adapter_not_found(self, mock_pg, mock_td):
        """测试注销不存在的适配器"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        result = dm.unregister_adapter("nonexistent")

        assert result is False

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_list_adapters_empty(self, mock_pg, mock_td):
        """测试列出空适配器列表"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        adapters = dm.list_adapters()

        assert adapters == []

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_list_adapters_multiple(self, mock_pg, mock_td):
        """测试列出多个适配器"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        dm.register_adapter("adapter1", Mock())
        dm.register_adapter("adapter2", Mock())
        dm.register_adapter("adapter3", Mock())

        adapters = dm.list_adapters()

        assert len(adapters) == 3
        assert "adapter1" in adapters
        assert "adapter2" in adapters
        assert "adapter3" in adapters

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_adapter_exists(self, mock_pg, mock_td):
        """测试获取存在的适配器"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        mock_adapter = Mock()
        dm.register_adapter("adapter", mock_adapter)

        result = dm.get_adapter("adapter")

        assert result == mock_adapter

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_adapter_not_exists(self, mock_pg, mock_td):
        """测试获取不存在的适配器"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        result = dm.get_adapter("nonexistent")

        assert result is None


class TestDataManagerRouting:
    """测试DataManager路由决策"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_target_database_tick_data(self, mock_pg, mock_td):
        """测试TICK_DATA路由到TDengine"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        target = dm.get_target_database(DataClassification.TICK_DATA)

        assert target == DatabaseTarget.TDENGINE

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_target_database_daily_kline(self, mock_pg, mock_td):
        """测试DAILY_KLINE路由到PostgreSQL"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        target = dm.get_target_database(DataClassification.DAILY_KLINE)

        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_target_database_symbols_info(self, mock_pg, mock_td):
        """测试SYMBOLS_INFO路由到PostgreSQL"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        target = dm.get_target_database(DataClassification.SYMBOLS_INFO)

        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_target_database_all_tdengine_routes(self, mock_pg, mock_td):
        """测试所有应该路由到TDengine的分类"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        tdengine_classifications = [
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES,
        ]

        for classification in tdengine_classifications:
            target = dm.get_target_database(classification)
            assert target == DatabaseTarget.TDENGINE, f"{classification} should route to TDengine"


class TestDataManagerSaveData:
    """测试DataManager保存数据"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_save_data_to_tdengine(self, mock_pg, mock_td):
        """测试保存数据到TDengine"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.save_data = Mock(return_value=True)

        dm = DataManager()
        test_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        result = dm.save_data(
            DataClassification.TICK_DATA, test_df, "tick_table"
        )

        assert result is True
        mock_td_instance.save_data.assert_called_once()

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_save_data_to_postgresql(self, mock_pg, mock_td):
        """测试保存数据到PostgreSQL"""
        from src.core.data_manager import DataManager

        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.save_data = Mock(return_value=True)

        dm = DataManager()
        test_df = pd.DataFrame({"symbol": ["600000"], "price": [10.5]})

        result = dm.save_data(
            DataClassification.DAILY_KLINE, test_df, "daily_kline_table"
        )

        assert result is True
        mock_pg_instance.save_data.assert_called_once()

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_save_data_failure(self, mock_pg, mock_td):
        """测试保存数据失败"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.save_data = Mock(return_value=False)

        dm = DataManager()
        test_df = pd.DataFrame({"col": [1]})

        result = dm.save_data(
            DataClassification.TICK_DATA, test_df, "table"
        )

        assert result is False

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_save_data_exception(self, mock_pg, mock_td):
        """测试保存数据异常"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.save_data = Mock(side_effect=Exception("Database error"))

        dm = DataManager()
        test_df = pd.DataFrame({"col": [1]})

        result = dm.save_data(
            DataClassification.TICK_DATA, test_df, "table"
        )

        assert result is False


class TestDataManagerLoadData:
    """测试DataManager加载数据"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_load_data_from_tdengine(self, mock_pg, mock_td):
        """测试从TDengine加载数据"""
        from src.core.data_manager import DataManager

        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_td_instance = mock_td.return_value
        mock_td_instance.load_data = Mock(return_value=expected_df)

        dm = DataManager()

        result = dm.load_data(
            DataClassification.TICK_DATA, "tick_table", symbol="600000"
        )

        assert result is not None
        assert len(result) == 2
        mock_td_instance.load_data.assert_called_once()

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_load_data_from_postgresql(self, mock_pg, mock_td):
        """测试从PostgreSQL加载数据"""
        from src.core.data_manager import DataManager

        expected_df = pd.DataFrame({"symbol": ["600000"], "close": [10.5]})
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.load_data = Mock(return_value=expected_df)

        dm = DataManager()

        result = dm.load_data(
            DataClassification.DAILY_KLINE, "daily_kline", symbol="600000"
        )

        assert result is not None
        assert len(result) == 1
        mock_pg_instance.load_data.assert_called_once()

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_load_data_not_found(self, mock_pg, mock_td):
        """测试加载不存在的数据"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.load_data = Mock(return_value=None)

        dm = DataManager()

        result = dm.load_data(
            DataClassification.TICK_DATA, "nonexistent_table"
        )

        assert result is None

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_load_data_exception(self, mock_pg, mock_td):
        """测试加载数据异常"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.load_data = Mock(side_effect=Exception("Connection error"))

        dm = DataManager()

        result = dm.load_data(DataClassification.TICK_DATA, "table")

        assert result is None


class TestDataManagerStatistics:
    """测试DataManager统计功能"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_routing_stats_no_adapters(self, mock_pg, mock_td):
        """测试获取路由统计（无适配器）"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        stats = dm.get_routing_stats()

        assert "total_classifications" in stats
        assert stats["total_classifications"] > 0
        assert "tdengine_count" in stats
        assert "postgresql_count" in stats
        assert stats["registered_adapters"] == 0
        assert stats["adapter_names"] == []

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_routing_stats_with_adapters(self, mock_pg, mock_td):
        """测试获取路由统计（有适配器）"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        dm.register_adapter("akshare", Mock())
        dm.register_adapter("baostock", Mock())

        stats = dm.get_routing_stats()

        assert stats["registered_adapters"] == 2
        assert "akshare" in stats["adapter_names"]
        assert "baostock" in stats["adapter_names"]

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_get_routing_stats_database_distribution(self, mock_pg, mock_td):
        """测试路由统计的数据库分布"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        stats = dm.get_routing_stats()

        # 验证TDengine和PostgreSQL的数量加起来等于总数
        assert (stats["tdengine_count"] + stats["postgresql_count"]) == stats["total_classifications"]


class TestDataManagerValidation:
    """测试DataManager数据验证"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_validate_data_valid(self, mock_pg, mock_td):
        """测试验证有效数据"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        test_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        is_valid, errors = dm.validate_data(DataClassification.TICK_DATA, test_df)

        assert is_valid is True
        assert len(errors) == 0

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_validate_data_none(self, mock_pg, mock_td):
        """测试验证None数据"""
        from src.core.data_manager import DataManager

        dm = DataManager()

        is_valid, errors = dm.validate_data(DataClassification.TICK_DATA, None)

        assert is_valid is False
        assert "数据为空" in errors

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_validate_data_empty_dataframe(self, mock_pg, mock_td):
        """测试验证空DataFrame"""
        from src.core.data_manager import DataManager

        dm = DataManager()
        empty_df = pd.DataFrame()

        is_valid, errors = dm.validate_data(DataClassification.TICK_DATA, empty_df)

        assert is_valid is False
        assert "数据为空" in errors


class TestDataManagerHealthCheck:
    """测试DataManager健康检查"""

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_health_check_both_healthy(self, mock_pg, mock_td):
        """测试健康检查（两个数据库都健康）"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.health_check = Mock(return_value=True)

        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.health_check = Mock(return_value=True)

        dm = DataManager()

        health = dm.health_check()

        assert health["manager_status"] == "healthy"
        assert health["tdengine"] == "healthy"
        assert health["postgresql"] == "healthy"
        assert "timestamp" in health

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_health_check_tdengine_unhealthy(self, mock_pg, mock_td):
        """测试健康检查（TDengine不健康）"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.health_check = Mock(side_effect=Exception("Connection failed"))

        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.health_check = Mock(return_value=True)

        dm = DataManager()

        health = dm.health_check()

        assert "unhealthy" in health["tdengine"]
        assert health["postgresql"] == "healthy"

    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_health_check_no_health_check_method(self, mock_pg, mock_td):
        """测试健康检查（数据库访问层没有health_check方法）"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        # 不设置health_check方法

        mock_pg_instance = mock_pg.return_value
        # 不设置health_check方法

        dm = DataManager()

        health = dm.health_check()

        # 应该使用默认值True
        assert health["tdengine"] == "healthy"
        assert health["postgresql"] == "healthy"


    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_health_check_postgresql_exception(self, mock_pg, mock_td):
        """测试健康检查（PostgreSQL抛出异常）"""
        from src.core.data_manager import DataManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.health_check = Mock(return_value=True)

        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.health_check = Mock(side_effect=Exception("Database locked"))

        dm = DataManager()

        health = dm.health_check()

        assert health["tdengine"] == "healthy"
        assert "unhealthy" in health["postgresql"]
        assert "Database locked" in health["postgresql"]


class TestDataManagerMonitoringIntegration:
    """测试DataManager监控集成功能"""

    @patch("src.monitoring.performance_monitor.get_performance_monitor")
    @patch("src.monitoring.monitoring_database.get_monitoring_database")
    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_initialization_with_monitoring_enabled_success(
        self, mock_pg, mock_td, mock_get_monitoring_db, mock_get_perf_monitor
    ):
        """测试enable_monitoring=True时成功初始化监控组件"""
        from src.core.data_manager import DataManager

        # Mock监控组件
        mock_monitoring_db = Mock()
        mock_perf_monitor = Mock()
        mock_get_monitoring_db.return_value = mock_monitoring_db
        mock_get_perf_monitor.return_value = mock_perf_monitor

        # 初始化DataManager，启用监控
        dm = DataManager(enable_monitoring=True)

        # 验证监控已启用
        assert dm.enable_monitoring is True
        assert dm._monitoring_db is mock_monitoring_db
        assert dm._performance_monitor is mock_perf_monitor

        # 验证监控组件被正确获取
        mock_get_monitoring_db.assert_called_once()
        mock_get_perf_monitor.assert_called_once()

    @patch("src.monitoring.performance_monitor.get_performance_monitor")
    @patch("src.monitoring.monitoring_database.get_monitoring_database")
    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_initialization_with_monitoring_enabled_import_failure(
        self, mock_pg, mock_td, mock_get_monitoring_db, mock_get_perf_monitor
    ):
        """测试监控组件导入失败时的优雅降级"""
        from src.core.data_manager import DataManager, _NullMonitoring

        # Mock监控组件导入失败
        mock_get_monitoring_db.side_effect = ImportError("No module named 'src.monitoring'")

        # 初始化DataManager，启用监控
        dm = DataManager(enable_monitoring=True)

        # 验证监控被禁用，使用null实现
        assert dm.enable_monitoring is False
        assert isinstance(dm._monitoring_db, _NullMonitoring)
        assert isinstance(dm._performance_monitor, _NullMonitoring)

    @patch("src.monitoring.performance_monitor.get_performance_monitor")
    @patch("src.monitoring.monitoring_database.get_monitoring_database")
    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_save_data_with_monitoring_records_performance(
        self, mock_pg, mock_td, mock_get_monitoring_db, mock_get_perf_monitor
    ):
        """测试save_data启用监控时记录性能指标"""
        from src.core.data_manager import DataManager

        # Mock监控组件
        mock_monitoring_db = Mock()
        mock_perf_monitor = Mock()
        mock_get_monitoring_db.return_value = mock_monitoring_db
        mock_get_perf_monitor.return_value = mock_perf_monitor

        # Mock数据库访问 - TDengine的save_data方法
        mock_td_instance = mock_td.return_value
        mock_td_instance.save_data = Mock(return_value=True)

        # 初始化DataManager，启用监控
        dm = DataManager(enable_monitoring=True)

        # 准备测试数据
        test_data = pd.DataFrame({
            "timestamp": [datetime.now()],
            "symbol": ["000001"],
            "price": [10.5]
        })

        # 保存数据
        result = dm.save_data(
            DataClassification.TICK_DATA,
            test_data,
            table_name="tick_data_test"
        )

        # 验证保存成功
        assert result is True

        # 验证性能监控被调用
        mock_perf_monitor.record_operation.assert_called_once()
        call_args = mock_perf_monitor.record_operation.call_args

        # 验证参数
        assert call_args[1]["operation"] == "save_data"
        assert call_args[1]["classification"] == "TICK_DATA"
        assert call_args[1]["success"] is True
        assert "duration_ms" in call_args[1]
        assert isinstance(call_args[1]["duration_ms"], (int, float))

    @patch("src.monitoring.performance_monitor.get_performance_monitor")
    @patch("src.monitoring.monitoring_database.get_monitoring_database")
    @patch("src.data_access.TDengineDataAccess")
    @patch("src.data_access.PostgreSQLDataAccess")
    def test_load_data_with_monitoring_records_performance(
        self, mock_pg, mock_td, mock_get_monitoring_db, mock_get_perf_monitor
    ):
        """测试load_data启用监控时记录性能指标"""
        from src.core.data_manager import DataManager

        # Mock监控组件
        mock_monitoring_db = Mock()
        mock_perf_monitor = Mock()
        mock_get_monitoring_db.return_value = mock_monitoring_db
        mock_get_perf_monitor.return_value = mock_perf_monitor

        # Mock数据库访问返回数据 - TDengine的load_data方法
        mock_td_instance = mock_td.return_value
        expected_data = pd.DataFrame({
            "timestamp": [datetime.now()],
            "symbol": ["000001"],
            "price": [10.5]
        })
        mock_td_instance.load_data = Mock(return_value=expected_data)

        # 初始化DataManager，启用监控
        dm = DataManager(enable_monitoring=True)

        # 加载数据
        result = dm.load_data(
            DataClassification.TICK_DATA,
            table_name="tick_data_test",
            limit=100
        )

        # 验证加载成功
        assert result is not None
        assert len(result) == 1

        # 验证性能监控被调用
        mock_perf_monitor.record_operation.assert_called_once()
        call_args = mock_perf_monitor.record_operation.call_args

        # 验证参数
        assert call_args[1]["operation"] == "load_data"
        assert call_args[1]["classification"] == "TICK_DATA"
        assert call_args[1]["success"] is True
        assert "duration_ms" in call_args[1]
        assert isinstance(call_args[1]["duration_ms"], (int, float))
