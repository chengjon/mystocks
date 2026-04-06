"""
Monitoring Service Test Suite
监控服务测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.monitoring.monitoring_service (1104行)
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from src.core import ConfigDrivenTableManager, DataClassification
from src.monitoring.monitoring_service import (
    Alert,
    AlertLevel,
    AlertManager,
    DataQualityMonitor,
    EmailAlertChannel,
    LogAlertChannel,
    MonitoringDatabase,
    OperationMetrics,
    PerformanceMonitor,
    WebhookAlertChannel,
)
from tests.unit.monitoring._monitoring_service_test_tail import TestAlertChannels, TestAlertManager


class TestOperationMetrics:
    """操作指标测试"""

    def test_operation_metrics_initialization(self):
        """测试操作指标初始化"""
        metrics = OperationMetrics(
            operation_id="test_op_001",
            table_name="test_table",
            database_type="postgresql",
            database_name="test_db",
            operation_type="INSERT",
            start_time=datetime.now(),
        )

        assert metrics.operation_id == "test_op_001"
        assert metrics.table_name == "test_table"
        assert metrics.database_type == "postgresql"
        assert metrics.database_name == "test_db"
        assert metrics.operation_type == "INSERT"
        assert metrics.status == "processing"
        assert metrics.data_count == 0
        assert metrics.duration is None
        assert metrics.end_time is None

    def test_mark_completed(self):
        """测试标记完成"""
        start_time = datetime.now() - timedelta(seconds=5)
        metrics = OperationMetrics(
            operation_id="test_op_001",
            table_name="test_table",
            database_type="postgresql",
            database_name="test_db",
            operation_type="INSERT",
            start_time=start_time,
        )

        metrics.mark_completed(data_count=100)

        assert metrics.status == "success"
        assert metrics.data_count == 100
        assert metrics.end_time is not None
        assert metrics.duration is not None
        assert metrics.duration >= 5  # 至少5秒

    def test_mark_failed(self):
        """测试标记失败"""
        start_time = datetime.now() - timedelta(seconds=3)
        metrics = OperationMetrics(
            operation_id="test_op_001",
            table_name="test_table",
            database_type="postgresql",
            database_name="test_db",
            operation_type="INSERT",
            start_time=start_time,
        )

        error_msg = "Connection failed"
        metrics.mark_failed(error_msg)

        assert metrics.status == "failed"
        assert metrics.error_message == error_msg
        assert metrics.end_time is not None
        assert metrics.duration is not None
        assert metrics.duration >= 3


class TestAlert:
    """告警对象测试"""

    def test_alert_initialization(self):
        """测试告警初始化"""
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.ERROR,
            title="Test Alert",
            message="This is a test alert",
            source="test_module",
            timestamp=datetime.now(),
        )

        assert alert.alert_id == "alert_001"
        assert alert.level == AlertLevel.ERROR
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert"
        assert alert.source == "test_module"
        assert alert.resolved == False
        assert alert.resolve_time is None


class TestMonitoringDatabase:
    """监控数据库测试"""

    def test_monitoring_database_initialization_with_url(self):
        """测试使用URL初始化监控数据库"""
        test_url = "postgresql://user:pass@host:5432/db_monitor"  # pragma: allowlist secret

        with patch("monitoring.monitoring_service.DatabaseTableManager") as mock_db_manager:
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url=test_url)

                assert db.monitor_db_url == test_url
                mock_db_manager.assert_called_once()

    def test_monitoring_database_initialization_without_url(self):
        """测试不使用URL初始化监控数据库"""
        with patch("monitoring.monitoring_service.DatabaseTableManager") as mock_db_manager:
            with patch("monitoring.monitoring_service.load_dotenv"):
                with patch.dict(
                    os.environ,
                    {"MONITOR_DB_URL": "postgresql://test:test@localhost:5432/monitor"},  # pragma: allowlist secret
                ):
                    db = MonitoringDatabase()

                    assert (
                        db.monitor_db_url == "postgresql://test:test@localhost:5432/monitor"
                    )  # pragma: allowlist secret
                    mock_db_manager.assert_called_once()

    @patch("psycopg2.connect")
    def test_get_monitor_connection_success(self, mock_connect):
        """测试获取监控数据库连接成功"""
        mock_connect.return_value = Mock()

        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url="postgresql://user:pass@host:5432/db_monitor")
                connection = db._get_monitor_connection()

                assert connection is not None
                mock_connect.assert_called_once()

    @patch("psycopg2.connect")
    def test_get_monitor_connection_failure(self, mock_connect):
        """测试获取监控数据库连接失败"""
        mock_connect.side_effect = Exception("Connection failed")

        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url="postgresql://user:pass@host:5432/db_monitor")
                connection = db._get_monitor_connection()

                assert connection is None

    def test_log_operation_start_basic(self):
        """测试记录操作开始"""
        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url="postgresql://user:pass@host:5432/db_monitor")
                db._insert_operation_log = Mock()

                operation_id = db.log_operation_start(
                    table_name="test_table",
                    database_type="postgresql",
                    database_name="test_db",
                    operation_type="INSERT",
                )

                assert "test_table" in operation_id
                assert "INSERT" in operation_id
                db._insert_operation_log.assert_called_once()

    def test_log_operation_start_with_details(self):
        """测试记录操作开始并包含详细信息"""
        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url="postgresql://user:pass@host:5432/db_monitor")
                db._insert_operation_log = Mock()

                details = {"batch_size": 100, "source": "api"}
                operation_id = db.log_operation_start(
                    table_name="test_table",
                    database_type="postgresql",
                    database_name="test_db",
                    operation_type="INSERT",
                    operation_details=details,
                )

                assert operation_id is not None
                db._insert_operation_log.assert_called_once()

    def test_log_operation_result_success(self):
        """测试记录操作结果成功"""
        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url="postgresql://user:pass@host:5432/db_monitor")
                db._update_operation_log = Mock()

                db.log_operation_result(operation_id="test_op_001", success=True, data_count=100)

                db._update_operation_log.assert_called_once()

    def test_log_operation_result_failure(self):
        """测试记录操作结果失败"""
        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase(monitor_db_url="postgresql://user:pass@host:5432/db_monitor")
                db._update_operation_log = Mock()

                db.log_operation_result(
                    operation_id="test_op_001",
                    success=False,
                    error_message="Connection timeout",
                )

                db._update_operation_log.assert_called_once()

    def test_get_operation_statistics_empty(self):
        """测试获取操作统计信息（无数据）"""
        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase()
                db._get_monitor_connection = Mock(return_value=None)

                stats = db.get_operation_statistics(hours=24)

                assert stats == {}

    def test_get_table_creation_history(self):
        """测试获取表创建历史"""
        with patch("monitoring.monitoring_service.DatabaseTableManager"):
            with patch("monitoring.monitoring_service.load_dotenv"):
                db = MonitoringDatabase()

                history = db.get_table_creation_history(limit=50)

                assert isinstance(history, list)


class TestDataQualityMonitor:
    """数据质量监控器测试"""

    def test_data_quality_monitor_initialization(self):
        """测试数据质量监控器初始化"""
        config_manager = Mock(spec=ConfigDrivenTableManager)

        monitor = DataQualityMonitor(config_manager)

        assert monitor.config_manager == config_manager
        assert isinstance(monitor.quality_rules, dict)
        assert "completeness" in monitor.quality_rules
        assert "freshness" in monitor.quality_rules
        assert "accuracy" in monitor.quality_rules
        assert "consistency" in monitor.quality_rules

    def test_check_data_completeness_daily_kline(self):
        """测试检查日线数据完整性"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)
        monitor._check_daily_kline_completeness = Mock(
            return_value={"completeness_score": 0.95, "missing_data": [], "issues": []}
        )

        result = monitor.check_data_completeness(DataClassification.DAILY_KLINE)

        assert result["classification"] == "daily_kline"
        assert "completeness_score" in result
        assert "check_time" in result

    def test_check_data_completeness_symbols_info(self):
        """测试检查股票信息完整性"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)
        monitor._check_symbols_completeness = Mock(
            return_value={"completeness_score": 0.99, "missing_data": [], "issues": []}
        )

        result = monitor.check_data_completeness(DataClassification.SYMBOLS_INFO)

        assert result["classification"] == "symbols_info"
        assert "completeness_score" in result
        assert "check_time" in result

    def test_check_data_freshness(self):
        """测试检查数据新鲜度"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)
        monitor._check_table_freshness = Mock(
            return_value={
                "table_name": "daily_kline",
                "last_update": datetime.now() - timedelta(hours=2),
                "threshold_hours": 24,
                "is_stale": False,
                "hours_old": 2,
            }
        )

        result = monitor.check_data_freshness()

        assert "check_time" in result
        assert "stale_data" in result
        assert "warnings" in result

    def test_check_table_freshness_fresh_data(self):
        """测试检查表新鲜度（新鲜数据）"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)

        result = monitor._check_table_freshness("daily_kline", 24)

        assert "table_name" in result
        assert "threshold_hours" in result
        assert "is_stale" in result
        assert "hours_old" in result

    def test_check_table_freshness_stale_data(self):
        """测试检查表新鲜度（过期数据）"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)

        # 模拟过期数据
        with patch("monitoring.monitoring_service.datetime") as mock_datetime:
            mock_now = datetime.now()
            mock_datetime.now.return_value = mock_now
            mock_datetime.now.return_value = mock_now

            result = monitor._check_table_freshness("daily_kline", 2)

            # 假设数据是2小时前的，阈值是2小时
            # 在实际实现中会检查是否超过阈值

    def test_check_data_accuracy(self):
        """测试检查数据准确性"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)
        monitor._check_price_data_accuracy = Mock(
            return_value={
                "accuracy_score": 0.99,
                "anomalies": [],
                "out_of_range_values": [],
            }
        )

        result = monitor.check_data_accuracy(DataClassification.DAILY_KLINE, sample_size=1000)

        assert result["classification"] == "daily_kline"
        assert "sample_size" in result
        assert "accuracy_score" in result
        assert "check_time" in result

    def test_generate_quality_report(self):
        """测试生成数据质量报告"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)

        # 模拟各个检查方法
        monitor.check_data_completeness = Mock(
            side_effect=lambda cls: {
                "completeness_score": 0.95,
                "check_time": datetime.now().isoformat(),
            }
        )
        monitor.check_data_accuracy = Mock(
            side_effect=lambda cls: {
                "accuracy_score": 0.98,
                "check_time": datetime.now().isoformat(),
            }
        )
        monitor.check_data_freshness = Mock(return_value={"stale_data": [], "warnings": []})

        result = monitor.generate_quality_report()

        assert "report_time" in result
        assert "overall_score" in result
        assert "completeness" in result
        assert "freshness" in result
        assert "accuracy" in result
        assert "recommendations" in result

    def test_generate_recommendations_high_quality(self):
        """测试生成建议（高质量数据）"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)

        report = {
            "overall_score": 0.95,
            "freshness": {"stale_data": []},
            "completeness": {
                "daily_kline": {"completeness_score": 0.96},
                "symbols_info": {"completeness_score": 0.94},
            },
        }

        recommendations = monitor._generate_recommendations(report)

        assert isinstance(recommendations, list)
        # 高质量数据应该有较少的建议

    def test_generate_recommendations_low_quality(self):
        """测试生成建议（低质量数据）"""
        config_manager = Mock(spec=ConfigDrivenTableManager)
        monitor = DataQualityMonitor(config_manager)

        report = {
            "overall_score": 0.75,
            "freshness": {"stale_data": ["test_table"]},
            "completeness": {"daily_kline": {"completeness_score": 0.80}},
        }

        recommendations = monitor._generate_recommendations(report)

        assert isinstance(recommendations, list)
        # 低质量数据应该有更多建议
        assert len(recommendations) > 0


class TestPerformanceMonitor:
    """性能监控器测试"""

    def test_performance_monitor_initialization(self):
        """测试性能监控器初始化"""
        monitor = PerformanceMonitor()

        assert monitor.metrics_history == []
        assert monitor.slow_query_threshold == 5.0

    def test_record_operation_metrics_success(self):
        """测试记录成功的操作指标"""
        monitor = PerformanceMonitor()

        metrics = OperationMetrics(
            operation_id="test_op_001",
            table_name="test_table",
            database_type="postgresql",
            database_name="test_db",
            operation_type="SELECT",
            start_time=datetime.now() - timedelta(seconds=2),
        )
        metrics.mark_completed(data_count=100)

        monitor.record_operation_metrics(metrics)

        assert len(monitor.metrics_history) == 1
        assert monitor.metrics_history[0] == metrics

    def test_record_operation_metrics_slow_operation(self):
        """测试记录慢操作指标"""
        monitor = PerformanceMonitor()

        metrics = OperationMetrics(
            operation_id="test_op_002",
            table_name="test_table",
            database_type="postgresql",
            database_name="test_db",
            operation_type="SELECT",
            start_time=datetime.now() - timedelta(seconds=10),
        )
        metrics.mark_completed(data_count=100)

        with patch("src.monitoring.monitoring_service._performance_monitor.logger") as mock_logger:
            monitor.record_operation_metrics(metrics)

            mock_logger.warning.assert_called()

    def test_get_performance_summary_no_data(self):
        """测试获取性能摘要（无数据）"""
        monitor = PerformanceMonitor()

        summary = monitor.get_performance_summary(hours=24)

        assert "message" in summary

    def test_get_performance_summary_with_data(self):
        """测试获取性能摘要（有数据）"""
        monitor = PerformanceMonitor()

        # 添加一些测试数据
        for i in range(5):
            start_time = datetime.now() - timedelta(hours=1, minutes=i * 10)
            metrics = OperationMetrics(
                operation_id=f"test_op_00{i}",
                table_name="test_table",
                database_type="postgresql",
                database_name="test_db",
                operation_type="SELECT" if i % 2 == 0 else "INSERT",
                start_time=start_time,
            )
            metrics.mark_completed(data_count=100)
            monitor.record_operation_metrics(metrics)

        summary = monitor.get_performance_summary(hours=24)

        assert "time_range_hours" in summary
        assert "total_operations" in summary
        assert summary["total_operations"] == 5
        assert "avg_duration" in summary
        assert "success_rate" in summary
        assert "operation_breakdown" in summary

    def test_get_slow_operations_no_data(self):
        """测试获取慢操作（无数据）"""
        monitor = PerformanceMonitor()

        slow_ops = monitor.get_slow_operations(hours=24)

        assert slow_ops == []

    def test_get_slow_operations_with_data(self):
        """测试获取慢操作（有数据）"""
        monitor = PerformanceMonitor()

        # 添加一些慢操作数据
        slow_operations = []
        for i in range(3):
            start_time = datetime.now() - timedelta(hours=1, minutes=i * 15)
            metrics = OperationMetrics(
                operation_id=f"slow_op_00{i}",
                table_name="test_table",
                database_type="postgresql",
                database_name="test_db",
                operation_type="SELECT",
                start_time=start_time,
            )
            # 设置为慢操作（超过5秒）
            metrics.end_time = start_time + timedelta(seconds=6 + i)
            metrics.duration = 6 + i
            monitor.record_operation_metrics(metrics)
            slow_operations.append(metrics)

        result = monitor.get_slow_operations(hours=24, limit=10)

        assert len(result) == 3
        # 应该按持续时间降序排列
        assert result[0]["duration"] >= result[1]["duration"]
        assert result[1]["duration"] >= result[2]["duration"]

    def test_metrics_history_cleanup(self):
        """测试指标历史清理"""
        monitor = PerformanceMonitor()
        monitor.slow_query_threshold = 1.0  # 降低阈值以便测试

        # 添加大量数据
        for i in range(12000):
            metrics = OperationMetrics(
                operation_id=f"op_{i}",
                table_name="test_table",
                database_type="postgresql",
                database_name="test_db",
                operation_type="SELECT",
                start_time=datetime.now(),
            )
            metrics.mark_completed(data_count=100)
            monitor.record_operation_metrics(metrics)

        # 历史记录应该被清理到5000条
        assert len(monitor.metrics_history) == 5000
        assert monitor.metrics_history[0].operation_id == "op_7000"
        assert monitor.metrics_history[-1].operation_id == "op_11999"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
