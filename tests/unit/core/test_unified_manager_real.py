"""
unified_manager 模块单元测试

测试 MyStocksUnifiedManager 的核心功能:
- 初始化和监控集成
- 数据库路由逻辑
- 数据保存和加载 (使用Mock避免真实数据库依赖)
- 批量操作和故障恢复
- 监控统计和数据质量检查
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from src.core.data_classification import DataClassification, DatabaseTarget


class TestUnifiedManagerInitialization:
    """测试MyStocksUnifiedManager初始化"""

    @patch("src.core.unified_manager.get_monitoring_database")
    @patch("src.core.unified_manager.get_performance_monitor")
    @patch("src.core.unified_manager.get_quality_monitor")
    @patch("src.core.unified_manager.get_alert_manager")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_initialization_with_monitoring_enabled(
        self,
        mock_pg,
        mock_td,
        mock_queue,
        mock_alert,
        mock_quality,
        mock_perf,
        mock_monitoring,
    ):
        """测试启用监控的初始化"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=True)

        assert manager.enable_monitoring is True
        assert manager.tdengine is not None
        assert manager.postgresql is not None
        mock_monitoring.assert_called_once()
        mock_perf.assert_called_once()
        mock_quality.assert_called_once()
        mock_alert.assert_called_once()

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_initialization_with_monitoring_disabled(
        self, mock_pg, mock_td, mock_queue
    ):
        """测试禁用监控的初始化"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        assert manager.enable_monitoring is False
        assert manager.monitoring_db is None
        assert manager.performance_monitor is None
        assert manager.quality_monitor is None
        assert manager.alert_manager is None

    @patch("src.core.unified_manager.get_monitoring_database")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_initialization_monitoring_failure_graceful(
        self, mock_pg, mock_td, mock_queue, mock_monitoring
    ):
        """测试监控初始化失败时的优雅降级"""
        # Mock监控初始化失败
        mock_monitoring.side_effect = Exception("监控数据库连接失败")

        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=True)

        # 应该优雅降级,禁用监控但系统继续运行
        assert manager.enable_monitoring is False
        assert manager.monitoring_db is None


class TestUnifiedManagerRoutingLogic:
    """测试数据库路由决策"""

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_get_target_database_tick_data(self, mock_pg, mock_td, mock_queue):
        """测试TICK_DATA路由到TDengine"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)
        target = manager._get_target_database(DataClassification.TICK_DATA)

        assert target == DatabaseTarget.TDENGINE

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_get_target_database_minute_kline(self, mock_pg, mock_td, mock_queue):
        """测试MINUTE_KLINE路由到TDengine"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)
        target = manager._get_target_database(DataClassification.MINUTE_KLINE)

        assert target == DatabaseTarget.TDENGINE

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_get_target_database_daily_kline(self, mock_pg, mock_td, mock_queue):
        """测试DAILY_KLINE路由到PostgreSQL"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)
        target = manager._get_target_database(DataClassification.DAILY_KLINE)

        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_get_target_database_symbols_info(self, mock_pg, mock_td, mock_queue):
        """测试SYMBOLS_INFO路由到PostgreSQL"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)
        target = manager._get_target_database(DataClassification.SYMBOLS_INFO)

        assert target == DatabaseTarget.POSTGRESQL

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_get_target_database_default_postgresql(self, mock_pg, mock_td, mock_queue):
        """测试未知分类默认路由到PostgreSQL"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)
        # 使用一个不在路由规则中的分类
        target = manager._get_target_database(DataClassification.FUNDAMENTAL_METRICS)

        assert target == DatabaseTarget.POSTGRESQL


class TestUnifiedManagerSaveData:
    """测试保存数据功能"""

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_empty_dataframe(self, mock_pg, mock_td, mock_queue):
        """测试保存空DataFrame"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        empty_df = pd.DataFrame()
        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA, empty_df, "test_table"
        )

        # 空DataFrame应该直接返回True,不实际保存
        assert result is True

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_data_to_tdengine_success(self, mock_pg, mock_td, mock_queue):
        """测试成功保存数据到TDengine"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock TDengine保存成功 (实际调用insert_dataframe)
        mock_td_instance = mock_td.return_value
        mock_td_instance.insert_dataframe = Mock(return_value=1)

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        test_df = pd.DataFrame({"symbol": ["600000"], "price": [10.0]})
        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA, test_df, "tick_table"
        )

        assert result is True
        mock_td_instance.insert_dataframe.assert_called_once()

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_data_to_postgresql_success(self, mock_pg, mock_td, mock_queue):
        """测试成功保存数据到PostgreSQL"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock PostgreSQL保存成功 (实际调用insert_dataframe)
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.insert_dataframe = Mock(return_value=1)

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        test_df = pd.DataFrame({"symbol": ["600000"], "close": [15.0]})
        result = manager.save_data_by_classification(
            DataClassification.DAILY_KLINE, test_df, "daily_kline"
        )

        assert result is True
        mock_pg_instance.insert_dataframe.assert_called_once()

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_data_database_failure_recovery_queue(
        self, mock_pg, mock_td, mock_queue
    ):
        """测试数据库故障时数据加入恢复队列"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock数据库保存失败
        mock_td_instance = mock_td.return_value
        mock_td_instance.insert_dataframe = Mock(
            side_effect=Exception("数据库连接失败")
        )

        # Mock恢复队列
        mock_queue_instance = mock_queue.return_value
        mock_queue_instance.enqueue = Mock()

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        test_df = pd.DataFrame({"symbol": ["600000"], "price": [10.0]})
        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA, test_df, "tick_table"
        )

        # 保存失败时,系统会捕获异常并加入恢复队列,返回False(保存失败)
        assert result is False
        mock_queue_instance.enqueue.assert_called_once()


class TestUnifiedManagerLoadData:
    """测试加载数据功能"""

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_load_data_from_tdengine_success(self, mock_pg, mock_td, mock_queue):
        """测试从TDengine成功加载数据"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock TDengine返回数据 (实际调用query_latest)
        expected_df = pd.DataFrame({"symbol": ["600000"], "price": [10.0]})
        mock_td_instance = mock_td.return_value
        mock_td_instance.query_latest = Mock(return_value=expected_df)

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.load_data_by_classification(
            DataClassification.TICK_DATA, "tick_table"
        )

        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "600000"
        mock_td_instance.query_latest.assert_called_once()

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_load_data_from_postgresql_success(self, mock_pg, mock_td, mock_queue):
        """测试从PostgreSQL成功加载数据"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock PostgreSQL返回数据 (实际调用query方法)
        expected_df = pd.DataFrame({"symbol": ["600000"], "close": [15.0]})
        mock_pg_instance = mock_pg.return_value
        # 根据源码 line 386: df = self.postgresql.query(table_name, columns, where, limit=limit)
        mock_pg_instance.query = Mock(return_value=expected_df)

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.load_data_by_classification(
            DataClassification.DAILY_KLINE, "daily_kline", filters={"symbol": "600000"}
        )

        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "600000"
        mock_pg_instance.query.assert_called_once()

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_load_data_database_failure(self, mock_pg, mock_td, mock_queue):
        """测试数据库故障时加载失败"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock数据库查询失败
        mock_td_instance = mock_td.return_value
        mock_td_instance.query_latest = Mock(side_effect=Exception("数据库连接失败"))

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        result = manager.load_data_by_classification(
            DataClassification.TICK_DATA, "tick_table"
        )

        # 失败应该返回空DataFrame
        assert result.empty


class TestUnifiedManagerBatchOperations:
    """测试批量操作"""

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_data_batch_with_strategy(self, mock_pg, mock_td, mock_queue):
        """测试使用批量故障策略保存数据"""
        from src.core.unified_manager import MyStocksUnifiedManager
        from src.core.batch_failure_strategy import BatchFailureStrategy

        # Mock PostgreSQL保存成功
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.insert_dataframe = Mock(return_value=10)  # 每批10条

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        test_df = pd.DataFrame({"symbol": [f"60000{i}" for i in range(100)]})
        result = manager.save_data_batch_with_strategy(
            DataClassification.DAILY_KLINE,
            test_df,
            "daily_kline",
            strategy=BatchFailureStrategy.CONTINUE,
            batch_size=10,
        )

        # 批量操作应该成功 (检查failed_records而不是success属性)
        assert result.total_records == 100
        assert result.successful_records == 100
        assert result.failed_records == 0
        # 确保insert_dataframe被调用（实际调用次数可能因实现而异）
        assert mock_pg_instance.insert_dataframe.called


class TestUnifiedManagerMonitoring:
    """测试监控集成"""

    @patch("src.core.unified_manager.get_monitoring_database")
    @patch("src.core.unified_manager.get_performance_monitor")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_monitoring_statistics(
        self, mock_pg, mock_td, mock_queue, mock_perf, mock_monitoring
    ):
        """测试获取监控统计信息"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock性能监控器
        mock_perf_instance = mock_perf.return_value
        mock_perf_instance.get_performance_summary = Mock(
            return_value={"avg_latency": 50, "total_queries": 1000}
        )

        manager = MyStocksUnifiedManager(enable_monitoring=True)
        stats = manager.get_monitoring_statistics()

        # 检查实际返回的键
        assert "enabled" in stats
        assert stats["enabled"] is True
        assert "performance" in stats
        assert stats["performance"]["avg_latency"] == 50

    @patch("src.core.unified_manager.get_monitoring_database")
    @patch("src.core.unified_manager.get_quality_monitor")
    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_check_data_quality(
        self, mock_pg, mock_td, mock_queue, mock_quality, mock_monitoring
    ):
        """测试数据质量检查"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock质量监控器
        mock_quality_instance = mock_quality.return_value
        mock_quality_instance.check_completeness = Mock(
            return_value={"passed": True, "completeness_rate": 0.98}
        )

        manager = MyStocksUnifiedManager(enable_monitoring=True)

        # 注意: check_data_quality需要classification, table_name, 和**kwargs
        result = manager.check_data_quality(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            check_type="completeness",
            total_records=1000,
            null_records=20,
        )

        assert "passed" in result
        assert result["passed"] is True
        mock_quality_instance.check_completeness.assert_called_once()


class TestUnifiedManagerUtilityMethods:
    """测试工具方法"""

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_get_routing_info(self, mock_pg, mock_td, mock_queue):
        """测试获取路由信息"""
        from src.core.unified_manager import MyStocksUnifiedManager

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        info = manager.get_routing_info(DataClassification.TICK_DATA)

        # 检查实际返回的键
        assert "target_db" in info
        assert info["target_db"] == "tdengine"

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_close_all_connections(self, mock_pg, mock_td, mock_queue):
        """测试关闭所有连接"""
        from src.core.unified_manager import MyStocksUnifiedManager

        mock_td_instance = mock_td.return_value
        mock_td_instance.close = Mock()
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.close_all = Mock()

        manager = MyStocksUnifiedManager(enable_monitoring=False)
        manager.close_all_connections()

        mock_td_instance.close.assert_called_once()
        mock_pg_instance.close_all.assert_called_once()


class TestUnifiedManagerEdgeCases:
    """测试边界情况"""

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_very_large_dataframe(self, mock_pg, mock_td, mock_queue):
        """测试保存超大DataFrame"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock成功保存
        mock_td_instance = mock_td.return_value
        mock_td_instance.insert_dataframe = Mock(return_value=100000)

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        # 创建10万行数据
        large_df = pd.DataFrame({"symbol": [f"60000{i % 10}" for i in range(100000)]})
        result = manager.save_data_by_classification(
            DataClassification.TICK_DATA, large_df, "tick_table"
        )

        assert result is True
        mock_td_instance.insert_dataframe.assert_called_once()

    @patch("src.core.unified_manager.FailureRecoveryQueue")
    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def test_save_single_row_dataframe(self, mock_pg, mock_td, mock_queue):
        """测试保存单行DataFrame"""
        from src.core.unified_manager import MyStocksUnifiedManager

        # Mock成功保存
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.insert_dataframe = Mock(return_value=1)

        manager = MyStocksUnifiedManager(enable_monitoring=False)

        single_row_df = pd.DataFrame({"col": [1]})
        result = manager.save_data_by_classification(
            DataClassification.DAILY_KLINE, single_row_df, "single_row_table"
        )

        assert result is True
        mock_pg_instance.insert_dataframe.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
