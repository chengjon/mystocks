#!/usr/bin/env python3
"""
DataManager Phase 6 测试套件
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
目标：将data_manager.py的覆盖率从42%提升到95%+
"""

import sys
import os
import time
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.core.data_manager import DataManager, _NullMonitoring
from src.core.data_classification import DataClassification, DatabaseTarget
from datetime import datetime


class TestNullMonitoring:
    """_NullMonitoring类的全面测试"""

    def test_log_operation_start(self):
        """测试操作开始记录"""
        monitor = _NullMonitoring()
        operation_id = monitor.log_operation_start("test_operation", {"param": "value"})
        assert operation_id == "null_operation_id"

    def test_log_operation_result(self):
        """测试操作结果记录"""
        monitor = _NullMonitoring()
        result = monitor.log_operation_result("operation_id", True, {"result": "data"})
        assert result is True

    def test_log_operation(self):
        """测试操作记录"""
        monitor = _NullMonitoring()
        result = monitor.log_operation("test_operation", True, 0.1)
        assert result is True

    def test_record_performance_metric(self):
        """测试性能指标记录"""
        monitor = _NullMonitoring()
        result = monitor.record_performance_metric(
            "metric_name", 0.5, {"tags": ["test"]}
        )
        assert result is True

    def test_record_operation(self):
        """测试操作记录"""
        monitor = _NullMonitoring()
        result = monitor.record_operation("operation", {"details": "test"})
        assert result is True

    def test_log_quality_check(self):
        """测试质量检查记录"""
        monitor = _NullMonitoring()
        result = monitor.log_quality_check("check_name", True, {"issues": []})
        assert result is True


class TestDataManagerInitialization:
    """DataManager初始化测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_init_default_monitoring_disabled(self, mock_db_manager):
        """测试默认禁用监控的初始化"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        assert manager.enable_monitoring is False
        assert isinstance(manager.monitoring, _NullMonitoring)
        assert manager.db_manager is not None

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_init_with_monitoring_enabled(self, mock_db_manager):
        """测试启用监控的初始化"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=True)

        assert manager.enable_monitoring is True

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_init_with_custom_db_manager(self, mock_db_manager):
        """测试自定义数据库管理器初始化"""
        custom_manager = Mock()
        manager = DataManager(enable_monitoring=False, db_manager=custom_manager)

        assert manager.db_manager is custom_manager

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_init_adapter_dict_initialization(self, mock_db_manager):
        """测试适配器字典初始化"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        assert hasattr(manager, "adapters")
        assert isinstance(manager.adapters, dict)
        assert len(manager.adapters) == 0

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_init_routing_stats_initialization(self, mock_db_manager):
        """测试路由统计初始化"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        assert hasattr(manager, "routing_stats")
        assert isinstance(manager.routing_stats, dict)


class TestDataManagerAdapterManagement:
    """适配器管理功能测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_register_adapter_success(self, mock_db_manager):
        """测试成功注册适配器"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        mock_adapter = Mock()
        manager.register_adapter("test_adapter", mock_adapter)

        assert "test_adapter" in manager.adapters
        assert manager.adapters["test_adapter"] is mock_adapter

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_register_adapter_overwrite(self, mock_db_manager):
        """测试覆盖现有适配器"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        adapter1 = Mock()
        adapter2 = Mock()

        manager.register_adapter("test_adapter", adapter1)
        manager.register_adapter("test_adapter", adapter2)  # 应该覆盖

        assert manager.adapters["test_adapter"] is adapter2

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_unregister_adapter_success(self, mock_db_manager):
        """测试成功注销适配器"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        mock_adapter = Mock()
        manager.register_adapter("test_adapter", mock_adapter)
        result = manager.unregister_adapter("test_adapter")

        assert result is True
        assert "test_adapter" not in manager.adapters

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_unregister_adapter_not_found(self, mock_db_manager):
        """测试注销不存在的适配器"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        result = manager.unregister_adapter("nonexistent_adapter")

        assert result is False

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_list_adapters_empty(self, mock_db_manager):
        """测试列出空适配器列表"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        adapters = manager.list_adapters()
        assert adapters == []

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_list_adapters_with_data(self, mock_db_manager):
        """测试列出有数据的适配器列表"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        manager.register_adapter("adapter1", Mock())
        manager.register_adapter("adapter2", Mock())

        adapters = manager.list_adapters()
        assert set(adapters) == {"adapter1", "adapter2"}

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_adapter_success(self, mock_db_manager):
        """测试成功获取适配器"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        mock_adapter = Mock()
        manager.register_adapter("test_adapter", mock_adapter)

        result = manager.get_adapter("test_adapter")
        assert result is mock_adapter

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_adapter_not_found(self, mock_db_manager):
        """测试获取不存在的适配器"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        result = manager.get_adapter("nonexistent_adapter")
        assert result is None


class TestDataManagerDatabaseRouting:
    """数据库路由功能测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_target_database_timeseries(self, mock_db_manager):
        """测试时序数据路由"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        target = manager.get_target_database(DataClassification.TIMESERIES_MARKET_DATA)
        assert target == DatabaseTarget.TDENGINE

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_target_database_reference(self, mock_db_manager):
        """测试参考数据路由"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        target = manager.get_target_database(DataClassification.REFERENCE_DATA)
        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_target_database_daily(self, mock_db_manager):
        """测试日线数据路由"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        target = manager.get_target_database(DataClassification.DAILY_MARKET_DATA)
        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_target_database_derived(self, mock_db_manager):
        """测试衍生数据路由"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        target = manager.get_target_database(DataClassification.DERIVED_DATA)
        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_target_database_transaction(self, mock_db_manager):
        """测试交易数据路由"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        target = manager.get_target_database(DataClassification.TRANSACTION_DATA)
        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_target_database_metadata(self, mock_db_manager):
        """测试元数据路由"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        target = manager.get_target_database(DataClassification.METADATA)
        assert target == DatabaseTarget.POSTGRESQL


class TestDataManagerSaveOperations:
    """数据保存操作测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_success_tdengine(self, mock_db_manager):
        """测试成功保存时序数据到TDengine"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        # Mock TDengine保存方法
        mock_db_instance.save_to_tdengine = Mock(return_value=True)

        test_data = pd.DataFrame(
            {
                "timestamp": ["2024-01-01 09:30:00"],
                "symbol": ["600000"],
                "price": [10.5],
                "volume": [1000],
            }
        )

        result = manager.save_data(
            data=test_data,
            classification=DataClassification.TIMESERIES_MARKET_DATA,
            table_name="test_table",
        )

        assert result is True
        mock_db_instance.save_to_tdengine.assert_called_once()

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_success_postgresql(self, mock_db_manager):
        """测试成功保存数据到PostgreSQL"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        # Mock PostgreSQL保存方法
        mock_db_instance.save_to_postgresql = Mock(return_value=True)

        test_data = pd.DataFrame(
            {"symbol": ["600000"], "name": ["平安银行"], "industry": ["银行"]}
        )

        result = manager.save_data(
            data=test_data,
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
        )

        assert result is True
        mock_db_instance.save_to_postgresql.assert_called_once()

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_failure_tdengine(self, mock_db_manager):
        """测试TDengine保存失败"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        # Mock保存失败
        mock_db_instance.save_to_tdengine = Mock(return_value=False)

        test_data = pd.DataFrame({"test": [1]})

        result = manager.save_data(
            data=test_data,
            classification=DataClassification.TIMESERIES_MARKET_DATA,
            table_name="test_table",
        )

        assert result is False

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_invalid_classification(self, mock_db_manager):
        """测试无效数据分类"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        test_data = pd.DataFrame({"test": [1]})

        with pytest.raises(ValueError):
            manager.save_data(
                data=test_data,
                classification="invalid_classification",
                table_name="test_table",
            )

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_empty_dataframe(self, mock_db_manager):
        """测试空DataFrame保存"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        mock_db_instance.save_to_postgresql = Mock(return_value=True)

        empty_data = pd.DataFrame()

        result = manager.save_data(
            data=empty_data,
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
        )

        assert result is True
        mock_db_instance.save_to_postgresql.assert_called_once()

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_with_validation_passed(self, mock_db_manager):
        """测试数据验证通过"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        mock_db_instance.save_to_postgresql = Mock(return_value=True)

        test_data = pd.DataFrame({"symbol": ["600000"]})

        result = manager.save_data(
            data=test_data,
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
            validate_data=True,
        )

        assert result is True

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_with_validation_failed(self, mock_db_manager):
        """测试数据验证失败"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        test_data = pd.DataFrame({"symbol": ["600000"]})

        result = manager.save_data(
            data=test_data,
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
            validate_data=True,
        )

        assert result is False  # 验证失败时不应该保存


class TestDataManagerLoadOperations:
    """数据加载操作测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_load_data_from_tdengine(self, mock_db_manager):
        """测试从TDengine加载数据"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        expected_data = pd.DataFrame({"test": [1, 2, 3]})
        mock_db_instance.load_from_tdengine = Mock(return_value=expected_data)

        result = manager.load_data(
            classification=DataClassification.TIMESERIES_MARKET_DATA,
            table_name="test_table",
            symbol="600000",
        )

        assert result.equals(expected_data)
        mock_db_instance.load_from_tdengine.assert_called_once()

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_load_data_from_postgresql(self, mock_db_manager):
        """测试从PostgreSQL加载数据"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        expected_data = pd.DataFrame({"test": [1, 2, 3]})
        mock_db_instance.load_from_postgresql = Mock(return_value=expected_data)

        result = manager.load_data(
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
            symbol="600000",
        )

        assert result.equals(expected_data)
        mock_db_instance.load_from_postgresql.assert_called_once()

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_load_data_empty_result(self, mock_db_manager):
        """测试加载空结果"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        empty_data = pd.DataFrame()
        mock_db_instance.load_from_postgresql = Mock(return_value=empty_data)

        result = manager.load_data(
            classification=DataClassification.REFERENCE_DATA, table_name="test_table"
        )

        assert result.empty

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_load_data_with_time_range(self, mock_db_manager):
        """测试带时间范围的数据加载"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        expected_data = pd.DataFrame({"test": [1, 2, 3]})
        mock_db_instance.load_from_tdengine = Mock(return_value=expected_data)

        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 2)

        result = manager.load_data(
            classification=DataClassification.TIMESERIES_MARKET_DATA,
            table_name="test_table",
            start_time=start_time,
            end_time=end_time,
        )

        assert result.equals(expected_data)


class TestDataManagerValidation:
    """数据验证功能测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_validate_data_success(self, mock_db_manager):
        """测试数据验证成功"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        valid_data = pd.DataFrame(
            {"symbol": ["600000", "000001"], "price": [10.5, 15.2]}
        )

        result = manager.validate_data(valid_data)
        assert result is True

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_validate_data_empty_dataframe(self, mock_db_manager):
        """测试空DataFrame验证"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        empty_data = pd.DataFrame()

        result = manager.validate_data(empty_data)
        assert result is False

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_validate_data_null_dataframe(self, mock_db_manager):
        """测试None DataFrame验证"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        result = manager.validate_data(None)
        assert result is False


class TestDataManagerMonitoringIntegration:
    """监控集成测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_monitoring_enabled_initialization(self, mock_db_manager):
        """测试启用监控的初始化"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=True)

        assert manager.enable_monitoring is True
        assert hasattr(manager, "monitoring")

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_monitoring_failure_fallback(self, mock_db_manager):
        """测试监控失败时的回退"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)  # 禁用监控

        # 确保使用NullMonitoring
        assert isinstance(manager.monitoring, _NullMonitoring)


class TestDataManagerPerformanceAndIntegration:
    """性能测试和集成测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_routing_performance_under_1ms(self, mock_db_manager):
        """测试路由决策性能（1ms以内）"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        # 测试多次路由决策
        start_time = time.time()
        for _ in range(1000):
            manager.get_target_database(DataClassification.TIMESERIES_MARKET_DATA)
        end_time = time.time()

        avg_time = (end_time - start_time) / 1000 * 1000  # 转换为毫秒
        assert avg_time < 1.0, f"路由决策平均时间: {avg_time:.2f}ms, 应该小于1ms"

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_large_dataframe_operations(self, mock_db_manager):
        """测试大数据帧操作"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        mock_db_instance.save_to_postgresql = Mock(return_value=True)

        # 创建大型DataFrame
        large_data = pd.DataFrame({"symbol": ["600000"] * 10000, "value": range(10000)})

        start_time = time.time()
        result = manager.save_data(
            data=large_data,
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
        )
        end_time = time.time()

        assert result is True
        operation_time = (end_time - start_time) * 1000
        print(f"大数据帧操作时间: {operation_time:.2f}ms")

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_complete_routing_verification(self, mock_db_manager):
        """测试完整路由验证"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        # 测试所有数据分类的路由
        routing_map = {
            DataClassification.TIMESERIES_MARKET_DATA: DatabaseTarget.TDENGINE,
            DataClassification.DAILY_MARKET_DATA: DatabaseTarget.POSTGRESQL,
            DataClassification.REFERENCE_DATA: DatabaseTarget.POSTGRESQL,
            DataClassification.DERIVED_DATA: DatabaseTarget.POSTGRESQL,
            DataClassification.TRANSACTION_DATA: DatabaseTarget.POSTGRESQL,
            DataClassification.METADATA: DatabaseTarget.POSTGRESQL,
        }

        for classification, expected_target in routing_map.items():
            actual_target = manager.get_target_database(classification)
            assert actual_target == expected_target, (
                f"路由错误: {classification} -> {actual_target}, 期望: {expected_target}"
            )

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_complete_data_workflow(self, mock_db_manager):
        """测试完整数据工作流"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        # Mock保存和加载
        test_data = pd.DataFrame({"symbol": ["600000"], "price": [10.5]})
        mock_db_instance.save_to_postgresql = Mock(return_value=True)
        mock_db_instance.load_from_postgresql = Mock(return_value=test_data)

        # 测试工作流：注册适配器 -> 保存数据 -> 加载数据
        mock_adapter = Mock()
        manager.register_adapter("test_adapter", mock_adapter)

        # 保存数据
        save_result = manager.save_data(
            data=test_data,
            classification=DataClassification.REFERENCE_DATA,
            table_name="test_table",
        )
        assert save_result is True

        # 加载数据
        load_result = manager.load_data(
            classification=DataClassification.REFERENCE_DATA, table_name="test_table"
        )
        assert load_result.equals(test_data)

        # 验证适配器注册
        assert manager.get_adapter("test_adapter") is mock_adapter


class TestDataManagerHealthCheck:
    """健康检查功能测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_health_check_success(self, mock_db_manager):
        """测试健康检查成功"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        # Mock健康检查方法
        mock_db_instance.test_tdengine_connection = Mock(return_value=True)
        mock_db_instance.test_postgresql_connection = Mock(return_value=True)

        health_status = manager.health_check()

        assert isinstance(health_status, dict)
        assert "tdengine" in health_status
        assert "postgresql" in health_status
        assert "overall_status" in health_status

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_health_check_tdengine_failure(self, mock_db_manager):
        """测试TDengine健康检查失败"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        mock_db_instance.test_tdengine_connection = Mock(return_value=False)
        mock_db_instance.test_postgresql_connection = Mock(return_value=True)

        health_status = manager.health_check()

        assert health_status["tdengine"] is False
        assert health_status["postgresql"] is True

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_health_check_postgresql_failure(self, mock_db_manager):
        """测试PostgreSQL健康检查失败"""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        manager = DataManager(enable_monitoring=False)

        mock_db_instance.test_tdengine_connection = Mock(return_value=True)
        mock_db_instance.test_postgresql_connection = Mock(return_value=False)

        health_status = manager.health_check()

        assert health_status["tdengine"] is True
        assert health_status["postgresql"] is False


class TestDataManagerEdgeCasesAndErrorHandling:
    """边界条件和错误处理测试"""

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_get_routing_stats(self, mock_db_manager):
        """测试获取路由统计"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        stats = manager.get_routing_stats()

        assert isinstance(stats, dict)
        assert "total_requests" in stats
        assert "tdengine_requests" in stats
        assert "postgresql_requests" in stats

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_save_data_exception_handling(self, mock_db_manager):
        """测试保存数据异常处理"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        test_data = pd.DataFrame({"test": [1]})

        # Mock异常
        with patch.object(
            manager, "get_target_database", side_effect=Exception("Database error")
        ):
            result = manager.save_data(
                data=test_data,
                classification=DataClassification.REFERENCE_DATA,
                table_name="test_table",
            )
            assert result is False

    @patch("src.core.data_manager.DatabaseTableManager")
    def test_load_data_exception_handling(self, mock_db_manager):
        """测试加载数据异常处理"""
        mock_db_manager.return_value = Mock()
        manager = DataManager(enable_monitoring=False)

        # Mock异常
        with patch.object(
            manager, "get_target_database", side_effect=Exception("Database error")
        ):
            result = manager.load_data(
                classification=DataClassification.REFERENCE_DATA,
                table_name="test_table",
            )
            assert isinstance(result, pd.DataFrame)  # 应该返回空DataFrame


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
