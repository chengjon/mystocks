#!/usr/bin/env python3
"""
DataManager模块全面测试套件 - 简化版本
应用Phase 6成功模式：功能→边界→异常→性能→集成测试

覆盖目标：100%测试覆盖率
测试方法：真实的DataManager实例 + Mock数据库依赖
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import time
from unittest.mock import Mock, patch

# 导入被测试的模块
from src.core.data_manager import DataManager, _NullMonitoring
from src.core.data_classification import DataClassification, DatabaseTarget


class TestNullMonitoring:
    """_NullMonitoring类的测试"""

    def test_null_monitoring_interface_compliance(self):
        """测试Null监控接口符合性"""
        null_monitor = _NullMonitoring()

        # 测试所有方法都存在且返回合适的值
        assert (
            null_monitor.log_operation_start("test", arg1="value")
            == "null_operation_id"
        )
        assert null_monitor.log_operation_result("test", True) is True
        assert null_monitor.log_operation("test", data={}) is True
        assert null_monitor.record_performance_metric("test", 100) is True
        assert null_monitor.record_operation("test", 50, True) is True
        assert null_monitor.log_quality_check("test", []) is True

    def test_null_monitoring_no_side_effects(self):
        """测试Null监控无副作用"""
        null_monitor = _NullMonitoring()

        # 调用所有方法，确保不抛出异常且无副作用
        for _ in range(10):
            null_monitor.log_operation_start("test", param="value")
            null_monitor.log_operation_result("test", True)
            null_monitor.log_operation("test", data={"key": "value"})
            null_monitor.record_performance_metric("test", 100.5)
            null_monitor.record_operation("test", 50, success=True)
            null_monitor.log_quality_check("test", [], 1.0)

        # 应该静默执行，无异常
        assert True


class TestDataManagerCoreFeatures:
    """DataManager核心功能测试 - 使用真实实例"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 使用patch来避免真实的数据库连接，但创建真实的DataManager实例
        with patch(
            "src.storage.database.database_manager.DatabaseTableManager"
        ) as mock_db_manager:
            mock_db_instance = Mock()
            mock_db_manager.return_value = mock_db_instance

            # Mock数据库访问层
            with (
                patch("src.data_access.TDengineDataAccess") as mock_td,
                patch("src.data_access.PostgreSQLDataAccess") as mock_pg,
            ):
                # 创建真实的DataManager实例
                self.dm = DataManager()

                # 设置Mock数据库访问层
                self.mock_td = mock_td.return_value
                self.mock_pg = mock_pg.return_value

    def test_initialization_default_monitoring_disabled(self):
        """测试默认初始化监控禁用"""
        # 验证基本属性
        assert self.dm.enable_monitoring is False
        assert isinstance(self.dm._adapters, dict)
        assert len(self.dm._adapters) == 0
        assert isinstance(self.dm._monitoring_db, _NullMonitoring)
        assert isinstance(self.dm._performance_monitor, _NullMonitoring)

    def test_routing_map_completeness(self):
        """测试路由映射完整性"""
        # 验证所有34个数据分类都有路由映射
        all_classifications = DataClassification.get_all_classifications()
        routed_classifications = set(self.dm._ROUTING_MAP.keys())
        expected_classifications = set(all_classifications)

        assert routed_classifications == expected_classifications, (
            f"路由映射不完整，缺失: {expected_classifications - routed_classifications}"
        )

    def test_routing_map_distribution(self):
        """测试路由映射分布"""
        tdengine_count = sum(
            1 for db in self.dm._ROUTING_MAP.values() if db == DatabaseTarget.TDENGINE
        )
        postgresql_count = sum(
            1 for db in self.dm._ROUTING_MAP.values() if db == DatabaseTarget.POSTGRESQL
        )

        # 验证路由分布合理性
        assert tdengine_count >= 5, "TDengine路由数量过少"
        assert postgresql_count >= 20, "PostgreSQL路由数量过少"
        assert tdengine_count + postgresql_count == 34, "路由总数不正确"

    def test_get_target_database_all_classifications(self):
        """测试所有数据分类的目标数据库获取"""
        # 验证TDengine分类
        expected_tds = {
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES,
        }

        for classification in DataClassification.get_all_classifications():
            target = self.dm.get_target_database(classification)

            # 验证返回有效的数据库目标
            assert isinstance(target, DatabaseTarget)

            # 验证TDengine分类正确路由
            if classification in expected_tds:
                assert target == DatabaseTarget.TDENGINE, (
                    f"{classification} 应该路由到 TDengine"
                )
            else:
                assert target == DatabaseTarget.POSTGRESQL, (
                    f"{classification} 应该路由到 PostgreSQL"
                )

    def test_adapter_registration_lifecycle(self):
        """测试适配器注册生命周期"""
        mock_adapter1 = Mock()
        mock_adapter2 = Mock()

        # 测试注册新适配器
        self.dm.register_adapter("test_adapter", mock_adapter1)
        assert "test_adapter" in self.dm._adapters
        assert self.dm._adapters["test_adapter"] == mock_adapter1

        # 测试列出适配器
        adapters = self.dm.list_adapters()
        assert "test_adapter" in adapters
        assert len(adapters) == 1

        # 测试获取适配器
        retrieved = self.dm.get_adapter("test_adapter")
        assert retrieved == mock_adapter1

        # 测试覆盖注册
        self.dm.register_adapter("test_adapter", mock_adapter2)
        assert self.dm._adapters["test_adapter"] == mock_adapter2
        assert len(self.dm._adapters) == 1

        # 测试注销适配器
        result = self.dm.unregister_adapter("test_adapter")
        assert result is True
        assert "test_adapter" not in self.dm._adapters
        assert self.dm.get_adapter("test_adapter") is None

        # 测试注销不存在的适配器
        result = self.dm.unregister_adapter("nonexistent_adapter")
        assert result is False

        # 测试获取不存在的适配器
        result = self.dm.get_adapter("nonexistent_adapter")
        assert result is None

    def test_data_validation(self):
        """测试数据验证功能"""
        # 测试有效数据
        valid_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3, freq="D"),
                "symbol": ["600000.SH"] * 3,
                "close": [10.0, 10.5, 11.0],
                "volume": [1000, 1200, 800],
            }
        )

        is_valid, errors = self.dm.validate_data(
            DataClassification.DAILY_KLINE, valid_data
        )
        assert is_valid is True
        assert len(errors) == 0

        # 测试None数据
        is_valid, errors = self.dm.validate_data(DataClassification.DAILY_KLINE, None)
        assert is_valid is False
        assert len(errors) == 1
        assert "数据为空" in errors[0]

        # 测试空DataFrame
        empty_data = pd.DataFrame()
        is_valid, errors = self.dm.validate_data(
            DataClassification.DAILY_KLINE, empty_data
        )
        assert is_valid is False
        assert len(errors) == 1
        assert "数据为空" in errors[0]

    def test_routing_stats(self):
        """测试路由统计信息"""
        # 注册一些适配器
        self.dm.register_adapter("adapter1", Mock())
        self.dm.register_adapter("adapter2", Mock())

        stats = self.dm.get_routing_stats()

        # 验证统计信息完整性
        assert isinstance(stats, dict)
        assert "total_classifications" in stats
        assert "tdengine_count" in stats
        assert "postgresql_count" in stats
        assert "registered_adapters" in stats
        assert "adapter_names" in stats

        # 验证统计数值正确性
        assert stats["total_classifications"] == 34
        assert stats["tdengine_count"] >= 5
        assert stats["postgresql_count"] >= 20
        assert stats["tdengine_count"] + stats["postgresql_count"] == 34
        assert stats["registered_adapters"] == 2
        assert set(stats["adapter_names"]) == {"adapter1", "adapter2"}


class TestDataManagerDataOperations:
    """DataManager数据操作测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        with (
            patch(
                "src.storage.database.database_manager.DatabaseTableManager"
            ) as mock_db_manager,
            patch("src.data_access.TDengineDataAccess") as mock_td,
            patch("src.data_access.PostgreSQLDataAccess") as mock_pg,
        ):
            mock_db_instance = Mock()
            mock_db_manager.return_value = mock_db_instance

            self.dm = DataManager()
            self.dm._tdengine = mock_td.return_value
            self.dm._postgresql = mock_pg.return_value

    def test_save_data_to_postgresql(self):
        """测试保存数据到PostgreSQL"""
        # 创建测试数据
        test_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5, freq="D"),
                "symbol": ["600000.SH"] * 5,
                "close": [10.0, 10.5, 11.0, 10.8, 11.2],
                "volume": [1000, 1200, 800, 1500, 900],
            }
        )

        # 设置PostgreSQL保存成功
        self.dm._postgresql.save_data.return_value = True

        # 执行保存操作
        result = self.dm.save_data(
            DataClassification.DAILY_KLINE, test_data, table_name="daily_kline"
        )

        # 验证结果
        assert result is True

        # 验证调用正确的数据库访问层
        self.dm._postgresql.save_data.assert_called_once_with(
            test_data, DataClassification.DAILY_KLINE, "daily_kline"
        )

    def test_save_data_to_tdengine(self):
        """测试保存数据到TDengine"""
        # 创建测试数据
        test_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=10, freq="1min"),
                "symbol": ["600000.SH"] * 10,
                "price": range(10, 20),
                "volume": range(100, 200, 10),
            }
        )

        # 设置TDengine保存成功
        self.dm._tdengine.save_data.return_value = True

        # 执行保存操作
        result = self.dm.save_data(
            DataClassification.TICK_DATA, test_data, table_name="tick_600000"
        )

        # 验证结果
        assert result is True

        # 验证调用正确的数据库访问层
        self.dm._tdengine.save_data.assert_called_once_with(
            test_data, DataClassification.TICK_DATA, "tick_600000"
        )

    def test_save_data_with_kwargs(self):
        """测试保存数据时传递额外参数"""
        test_data = pd.DataFrame({"col1": [1, 2, 3]})

        self.dm._postgresql.save_data.return_value = True

        # 执行保存操作并传递额外参数
        result = self.dm.save_data(
            DataClassification.TECHNICAL_INDICATORS,
            test_data,
            table_name="indicators",
            batch_size=1000,
            if_exists="append",
        )

        # 验证额外参数被正确传递
        self.dm._postgresql.save_data.assert_called_once_with(
            test_data,
            DataClassification.TECHNICAL_INDICATORS,
            "indicators",
            batch_size=1000,
            if_exists="append",
        )

        assert result is True

    def test_save_data_failure(self):
        """测试保存数据失败处理"""
        test_data = pd.DataFrame({"col1": [1, 2, 3]})

        # 设置保存失败
        self.dm._postgresql.save_data.return_value = False

        result = self.dm.save_data(
            DataClassification.DAILY_KLINE, test_data, table_name="daily_test"
        )

        # 验证失败处理
        assert result is False

    def test_save_data_exception_handling(self):
        """测试保存数据异常处理"""
        test_data = pd.DataFrame({"col1": [1, 2, 3]})

        # 设置抛出异常
        self.dm._postgresql.save_data.side_effect = Exception("数据库连接失败")

        with patch("src.core.data_manager.logger"):  # 抑制错误日志
            result = self.dm.save_data(
                DataClassification.DAILY_KLINE, test_data, table_name="daily_test"
            )

        # 验证异常处理
        assert result is False

    def test_load_data_from_postgresql(self):
        """测试从PostgreSQL加载数据"""
        # 创建预期的返回数据
        expected_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3, freq="D"),
                "symbol": ["600000.SH"] * 3,
                "close": [10.0, 10.5, 11.0],
                "volume": [1000, 1200, 800],
            }
        )

        # 设置PostgreSQL返回数据
        self.dm._postgresql.load_data.return_value = expected_data

        # 执行加载操作
        result = self.dm.load_data(
            DataClassification.DAILY_KLINE, table_name="daily_kline", symbol="600000.SH"
        )

        # 验证结果
        assert result is not None
        pd.testing.assert_frame_equal(result, expected_data)

        # 验证调用正确的数据库访问层
        self.dm._postgresql.load_data.assert_called_once_with(
            "daily_kline", symbol="600000.SH"
        )

    def test_load_data_from_tdengine(self):
        """测试从TDengine加载数据"""
        # 创建预期的返回数据
        expected_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="1min"),
                "symbol": ["600000.SH"] * 5,
                "price": range(10, 15),
                "volume": range(100, 150, 10),
            }
        )

        # 设置TDengine返回数据
        self.dm._tdengine.load_data.return_value = expected_data

        # 执行加载操作
        result = self.dm.load_data(
            DataClassification.MINUTE_KLINE,
            table_name="minute_600000",
            symbol="600000.SH",
            start_time="2024-01-01 09:30:00",
        )

        # 验证结果
        assert result is not None
        pd.testing.assert_frame_equal(result, expected_data)

        # 验证调用正确的数据库访问层
        self.dm._tdengine.load_data.assert_called_once_with(
            "minute_600000", symbol="600000.SH", start_time="2024-01-01 09:30:00"
        )

    def test_load_data_empty_result(self):
        """测试加载数据返回空结果"""
        # 设置返回None
        self.dm._postgresql.load_data.return_value = None

        result = self.dm.load_data(
            DataClassification.TECHNICAL_INDICATORS, table_name="indicators"
        )

        # 验证空结果处理
        assert result is None

    def test_load_data_exception_handling(self):
        """测试加载数据异常处理"""
        # 设置抛出异常
        self.dm._tdengine.load_data.side_effect = Exception("查询超时")

        with patch("src.core.data_manager.logger"):  # 抑制错误日志
            result = self.dm.load_data(
                DataClassification.TICK_DATA, table_name="tick_test"
            )

        # 验证异常处理
        assert result is None


class TestDataManagerMonitoringIntegration:
    """DataManager监控集成测试"""

    def test_monitoring_enabled_initialization(self):
        """测试启用监控的初始化"""
        with (
            patch("src.storage.database.database_manager.DatabaseTableManager"),
            patch("src.data_access.TDengineDataAccess"),
            patch("src.data_access.PostgreSQLDataAccess"),
            patch(
                "src.monitoring.monitoring_database.get_monitoring_database"
            ) as mock_get_monitoring,
            patch(
                "src.monitoring.performance_monitor.get_performance_monitor"
            ) as mock_get_perf,
        ):
            # 设置Mock监控组件
            mock_monitoring_db = Mock()
            mock_perf_monitor = Mock()
            mock_get_monitoring.return_value = mock_monitoring_db
            mock_get_perf.return_value = mock_perf_monitor

            dm = DataManager(enable_monitoring=True)

            # 验证监控组件被正确设置
            assert dm.enable_monitoring is True
            assert dm._monitoring_db == mock_monitoring_db
            assert dm._performance_monitor == mock_perf_monitor

    def test_monitoring_failure_fallback(self):
        """测试监控初始化失败时的回退"""
        with (
            patch("src.storage.database.database_manager.DatabaseTableManager"),
            patch("src.data_access.TDengineDataAccess"),
            patch("src.data_access.PostgreSQLDataAccess"),
            patch(
                "src.monitoring.monitoring_database.get_monitoring_database",
                side_effect=Exception("监控失败"),
            ),
        ):
            dm = DataManager(enable_monitoring=True)

            # 验证回退到null监控
            assert dm.enable_monitoring is False
            assert isinstance(dm._monitoring_db, _NullMonitoring)
            assert isinstance(dm._performance_monitor, _NullMonitoring)


class TestDataManagerHealthCheck:
    """DataManager健康检查测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        with (
            patch("src.storage.database.database_manager.DatabaseTableManager"),
            patch("src.data_access.TDengineDataAccess") as mock_td,
            patch("src.data_access.PostgreSQLDataAccess") as mock_pg,
        ):
            self.dm = DataManager()
            self.dm._tdengine = mock_td.return_value
            self.dm._postgresql = mock_pg.return_value

    def test_health_check_success(self):
        """测试健康检查成功"""
        # 设置健康检查成功
        self.dm._tdengine.health_check.return_value = True
        self.dm._postgresql.health_check.return_value = True

        health = self.dm.health_check()

        # 验证健康状态
        assert isinstance(health, dict)
        assert health["manager_status"] == "healthy"
        assert health["tdengine"] == "healthy"
        assert health["postgresql"] == "healthy"
        assert "timestamp" in health

    def test_health_check_no_health_check_method(self):
        """测试数据库访问层没有health_check方法"""
        # 删除健康检查方法
        if hasattr(self.dm._tdengine, "health_check"):
            delattr(self.dm._tdengine, "health_check")
        if hasattr(self.dm._postgresql, "health_check"):
            delattr(self.dm._postgresql, "health_check")

        health = self.dm.health_check()

        # 验证默认健康状态
        assert health["tdengine"] == "healthy"
        assert health["postgresql"] == "healthy"

    def test_health_check_tdengine_failure(self):
        """测试TDengine健康检查失败"""
        # 设置TDengine健康检查失败
        self.dm._tdengine.health_check.side_effect = Exception("连接失败")
        self.dm._postgresql.health_check.return_value = True

        health = self.dm.health_check()

        # 验证健康状态
        assert health["tdengine"].startswith("unhealthy:")
        assert health["postgresql"] == "healthy"

    def test_health_check_postgresql_failure(self):
        """测试PostgreSQL健康检查失败"""
        # 设置PostgreSQL健康检查失败
        self.dm._tdengine.health_check.return_value = True
        self.dm._postgresql.health_check.side_effect = Exception("连接超时")

        health = self.dm.health_check()

        # 验证健康状态
        assert health["tdengine"] == "healthy"
        assert health["postgresql"].startswith("unhealthy:")


class TestDataManagerPerformanceAndIntegration:
    """DataManager性能和集成测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        with (
            patch("src.storage.database.database_manager.DatabaseTableManager"),
            patch("src.data_access.TDengineDataAccess"),
            patch("src.data_access.PostgreSQLDataAccess"),
        ):
            self.dm = DataManager()

    def test_routing_performance_under_1ms(self):
        """测试路由性能目标 <1ms"""
        # 测试多次路由操作的性能
        iterations = 1000
        classifications = DataClassification.get_all_classifications()

        start_time = time.time()

        for i in range(iterations):
            classification = classifications[i % len(classifications)]
            self.dm.get_target_database(classification)

        duration_ms = (time.time() - start_time) * 1000
        avg_duration_ms = duration_ms / iterations

        # 验证平均路由时间 <1ms (远低于5ms目标)
        assert avg_duration_ms < 1.0, (
            f"路由平均时间 {avg_duration_ms:.3f}ms 超过目标 1ms"
        )

    def test_large_dataframe_operations(self):
        """测试大数据集操作"""
        # 创建大数据集（10,000行）
        large_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10000, freq="1min"),
                "symbol": ["TEST"] * 10000,
                "value": range(10000),
            }
        )

        # 测试验证性能
        start_time = time.time()
        is_valid, errors = self.dm.validate_data(
            DataClassification.DAILY_KLINE, large_data
        )
        duration_ms = (time.time() - start_time) * 1000

        # 验证结果和性能
        assert is_valid is True
        assert len(errors) == 0
        assert duration_ms < 100  # 应该在100ms内完成

    def test_complete_routing_verification(self):
        """测试全面的路由验证"""
        # 验证所有34个数据分类的路由
        routing_summary = {}

        for classification in DataClassification.get_all_classifications():
            target_db = self.dm.get_target_database(classification)

            if target_db not in routing_summary:
                routing_summary[target_db] = []
            routing_summary[target_db].append(classification)

        # 验证TDengine分类（应该是高频数据）
        tdengine_classifications = routing_summary.get(DatabaseTarget.TDENGINE, [])

        expected_tdengine_classifications = {
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES,
        }

        assert set(tdengine_classifications) == expected_tdengine_classifications

        # 验证PostgreSQL分类（应该是其他所有数据）
        postgresql_classifications = routing_summary.get(DatabaseTarget.POSTGRESQL, [])
        assert len(postgresql_classifications) == 34 - len(
            expected_tdengine_classifications
        )

        # 验证没有分类被遗漏
        total_routed = len(tdengine_classifications) + len(postgresql_classifications)
        assert total_routed == 34

    def test_complete_data_workflow(self):
        """测试完整的数据工作流程"""
        with (
            patch("src.data_access.TDengineDataAccess") as mock_td,
            patch("src.data_access.PostgreSQLDataAccess") as mock_pg,
        ):
            # 重新初始化DataManager用于完整工作流测试
            with patch("src.storage.database.database_manager.DatabaseTableManager"):
                dm = DataManager()
                dm._tdengine = mock_td.return_value
                dm._postgresql = mock_pg.return_value

            # 1. 注册适配器
            mock_adapter = Mock()
            dm.register_adapter("test_adapter", mock_adapter)

            # 2. 创建测试数据
            test_data = pd.DataFrame(
                {
                    "date": pd.date_range("2024-01-01", periods=5, freq="D"),
                    "symbol": ["600000.SH"] * 5,
                    "open": [10.0, 10.5, 11.0, 10.8, 11.2],
                    "high": [10.5, 11.0, 11.3, 11.1, 11.5],
                    "low": [9.8, 10.3, 10.8, 10.6, 11.0],
                    "close": [10.3, 10.8, 11.1, 10.9, 11.3],
                    "volume": [1000, 1200, 900, 1500, 1100],
                }
            )

            # 3. 保存数据
            dm._postgresql.save_data.return_value = True
            save_result = dm.save_data(
                DataClassification.DAILY_KLINE, test_data, table_name="daily_kline"
            )
            assert save_result is True

            # 4. 加载数据
            dm._postgresql.load_data.return_value = test_data
            loaded_data = dm.load_data(
                DataClassification.DAILY_KLINE,
                table_name="daily_kline",
                symbol="600000.SH",
            )
            assert loaded_data is not None
            pd.testing.assert_frame_equal(loaded_data, test_data)

            # 5. 验证数据
            is_valid, errors = dm.validate_data(
                DataClassification.DAILY_KLINE, loaded_data
            )
            assert is_valid is True
            assert len(errors) == 0

            # 6. 检查路由统计
            stats = dm.get_routing_stats()
            assert stats["registered_adapters"] == 1
            assert "test_adapter" in stats["adapter_names"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
