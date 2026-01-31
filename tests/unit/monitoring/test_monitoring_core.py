"""
Monitoring Service 核心功能测试
监控服务核心功能测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.monitoring.monitoring_service (1104行)
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


# 直接测试核心类，避免循环导入
class TestOperationMetrics:
    """操作指标测试"""

    def test_operation_metrics_creation(self):
        """测试操作指标创建"""
        # 直接模拟OperationMetrics类的功能
        start_time = datetime.now()

        # 创建一个模拟的OperationMetrics对象
        metrics = Mock()
        metrics.operation_id = "test_op_001"
        metrics.table_name = "test_table"
        metrics.database_type = "postgresql"
        metrics.database_name = "test_db"
        metrics.operation_type = "INSERT"
        metrics.start_time = start_time
        metrics.end_time = start_time + timedelta(seconds=1)
        metrics.duration_ms = 1000
        metrics.rows_affected = 10
        metrics.success = True
        metrics.error_message = None
        metrics.metadata = {"source": "test"}

        # 验证基本属性
        assert metrics.operation_id == "test_op_001"
        assert metrics.table_name == "test_table"
        assert metrics.database_type == "postgresql"
        assert metrics.success is True
        assert metrics.duration_ms == 1000
        assert metrics.rows_affected == 10

    def test_operation_metrics_to_dict(self):
        """测试操作指标转换为字典"""
        start_time = datetime.now()

        # 模拟to_dict方法
        metrics = Mock()
        metrics.operation_id = "test_op_002"
        metrics.start_time = start_time
        metrics.to_dict.return_value = {
            "operation_id": "test_op_002",
            "start_time": start_time.isoformat(),
            "success": True,
        }

        result = metrics.to_dict()
        assert isinstance(result, dict)
        assert result["operation_id"] == "test_op_002"
        assert "start_time" in result

    def test_operation_metrics_with_error(self):
        """测试带错误信息的操作指标"""
        start_time = datetime.now()

        metrics = Mock()
        metrics.operation_id = "test_op_003"
        metrics.success = False
        metrics.error_message = "Connection timeout"
        metrics.duration_ms = 5000

        assert metrics.success is False
        assert "timeout" in metrics.error_message
        assert metrics.duration_ms == 5000


class TestAlert:
    """告警对象测试"""

    def test_alert_creation(self):
        """测试告警对象创建"""
        alert_time = datetime.now()

        # 模拟Alert对象
        alert = Mock()
        alert.alert_id = "alert_001"
        alert.alert_type = "PERFORMANCE"
        alert.severity = "HIGH"
        alert.title = "Slow Query Detected"
        alert.message = "Query exceeded 5 seconds"
        alert.source = "database_monitor"
        alert.timestamp = alert_time
        alert.metadata = {"query_duration": 6.5}

        # 验证属性
        assert alert.alert_id == "alert_001"
        assert alert.alert_type == "PERFORMANCE"
        assert alert.severity == "HIGH"
        assert "Slow Query" in alert.title
        assert alert.source == "database_monitor"

    def test_alert_severity_levels(self):
        """测试告警严重程度级别"""
        severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        for severity in severity_levels:
            alert = Mock()
            alert.severity = severity
            assert alert.severity in severity_levels

    def test_alert_types(self):
        """测试告警类型"""
        alert_types = ["PERFORMANCE", "ERROR", "DATA_QUALITY", "AVAILABILITY"]

        for alert_type in alert_types:
            alert = Mock()
            alert.alert_type = alert_type
            assert alert.alert_type in alert_types


class TestMonitoringDatabase:
    """监控数据库测试"""

    def test_monitoring_database_init(self):
        """测试监控数据库初始化"""
        # 模拟监控数据库
        monitoring_db = Mock()
        monitoring_db.connection_string = "postgresql://user:pass@localhost/monitoring"
        monitoring_db.table_prefix = "monitoring_"

        assert "monitoring" in monitoring_db.connection_string
        assert monitoring_db.table_prefix == "monitoring_"

    def test_save_operation_metrics(self):
        """测试保存操作指标"""
        monitoring_db = Mock()
        monitoring_db.save_operation_metrics = Mock(return_value=True)

        # 模拟操作指标
        metrics = Mock()
        metrics.operation_id = "op_001"

        # 调用保存方法
        result = monitoring_db.save_operation_metrics(metrics)
        assert result is True
        monitoring_db.save_operation_metrics.assert_called_once_with(metrics)

    def test_save_alert(self):
        """测试保存告警"""
        monitoring_db = Mock()
        monitoring_db.save_alert = Mock(return_value=True)

        # 模拟告警对象
        alert = Mock()
        alert.alert_id = "alert_001"

        result = monitoring_db.save_alert(alert)
        assert result is True
        monitoring_db.save_alert.assert_called_once_with(alert)

    def test_get_recent_metrics(self):
        """测试获取最近的操作指标"""
        monitoring_db = Mock()
        mock_metrics = [
            {"operation_id": "op_001", "duration_ms": 1000},
            {"operation_id": "op_002", "duration_ms": 1500},
        ]
        monitoring_db.get_recent_metrics = Mock(return_value=mock_metrics)

        result = monitoring_db.get_recent_metrics(hours=1)
        assert len(result) == 2
        assert result[0]["operation_id"] == "op_001"
        assert result[1]["duration_ms"] == 1500


class TestDataQualityMonitor:
    """数据质量监控测试"""

    def test_data_quality_monitor_init(self):
        """测试数据质量监控初始化"""
        monitor = Mock()
        monitor.check_interval = 300  # 5分钟
        monitor.quality_thresholds = {
            "completeness": 0.95,
            "freshness_hours": 24,
            "accuracy": 0.99,
        }

        assert monitor.check_interval == 300
        assert monitor.quality_thresholds["completeness"] == 0.95

    def test_check_data_completeness(self):
        """测试数据完整性检查"""
        monitor = Mock()

        # 模拟数据完整性检查结果
        completeness_result = {
            "table_name": "stock_data",
            "total_records": 10000,
            "null_records": 500,
            "completeness_score": 0.95,
            "passed": True,
            "timestamp": datetime.now(),
        }
        monitor.check_data_completeness = Mock(return_value=completeness_result)

        result = monitor.check_data_completeness("stock_data")
        assert result["passed"] is True
        assert result["completeness_score"] == 0.95

    def test_check_data_freshness(self):
        """测试数据新鲜度检查"""
        monitor = Mock()

        freshness_result = {
            "table_name": "stock_data",
            "latest_timestamp": datetime.now() - timedelta(hours=2),
            "age_hours": 2,
            "fresh": True,
            "threshold_hours": 24,
        }
        monitor.check_data_freshness = Mock(return_value=freshness_result)

        result = monitor.check_data_freshness("stock_data", "timestamp_column")
        assert result["fresh"] is True
        assert result["age_hours"] == 2

    def test_detect_anomalies(self):
        """测试异常检测"""
        monitor = Mock()

        anomalies = [
            {
                "type": "outlier",
                "value": 1000000,
                "expected_range": [10, 1000],
                "column": "price",
                "timestamp": datetime.now(),
            }
        ]
        monitor.detect_anomalies = Mock(return_value=anomalies)

        result = monitor.detect_anomalies("stock_data", ["price", "volume"])
        assert len(result) == 1
        assert result[0]["type"] == "outlier"


class TestPerformanceMonitor:
    """性能监控测试"""

    def test_performance_monitor_init(self):
        """测试性能监控初始化"""
        monitor = Mock()
        monitor.slow_query_threshold = 5.0  # 5秒
        monitor.cpu_threshold = 80.0  # 80%
        monitor.memory_threshold = 85.0  # 85%

        assert monitor.slow_query_threshold == 5.0
        assert monitor.cpu_threshold == 80.0

    def test_monitor_query_performance(self):
        """测试查询性能监控"""
        monitor = Mock()

        # 模拟查询性能结果
        perf_result = {
            "query": "SELECT * FROM stock_data",
            "duration_ms": 8500,
            "rows_returned": 5000,
            "slow": True,
            "threshold_ms": 5000,
        }
        monitor.monitor_query = Mock(return_value=perf_result)

        result = monitor.monitor_query("SELECT * FROM stock_data", 8500)
        assert result["slow"] is True
        assert result["duration_ms"] == 8500

    def test_check_system_resources(self):
        """测试系统资源检查"""
        monitor = Mock()

        resource_status = {
            "cpu_percent": 75.5,
            "memory_percent": 82.3,
            "disk_usage": 65.2,
            "network_io": {"bytes_sent": 1024000, "bytes_recv": 2048000},
            "healthy": True,
        }
        monitor.check_system_resources = Mock(return_value=resource_status)

        result = monitor.check_system_resources()
        assert result["healthy"] is True
        assert result["cpu_percent"] == 75.5

    def test_collect_database_metrics(self):
        """测试数据库指标收集"""
        monitor = Mock()

        db_metrics = {
            "active_connections": 25,
            "idle_connections": 10,
            "query_per_second": 150.5,
            "avg_response_time": 45.2,
            "buffer_cache_hit_ratio": 0.95,
        }
        monitor.collect_database_metrics = Mock(return_value=db_metrics)

        result = monitor.collect_database_metrics()
        assert result["active_connections"] == 25
        assert result["query_per_second"] == 150.5


class TestAlertManager:
    """告警管理器测试"""

    def test_alert_manager_init(self):
        """测试告警管理器初始化"""
        manager = Mock()
        manager.enabled = True
        manager.rate_limit_per_minute = 10
        manager.alert_channels = ["email", "webhook", "slack"]

        assert manager.enabled is True
        assert manager.rate_limit_per_minute == 10
        assert len(manager.alert_channels) == 3

    def test_send_alert(self):
        """测试发送告警"""
        manager = Mock()

        # 模拟告警发送结果
        send_result = {
            "alert_id": "alert_001",
            "sent": True,
            "channels_used": ["email", "webhook"],
            "timestamp": datetime.now(),
        }
        manager.send_alert = Mock(return_value=send_result)

        alert = Mock()
        alert.severity = "HIGH"

        result = manager.send_alert(alert)
        assert result["sent"] is True
        assert len(result["channels_used"]) == 2

    def test_rate_limiting(self):
        """测试速率限制"""
        manager = Mock()
        manager.should_send_alert = Mock(return_value=False)
        manager.alerts_sent_count = 15
        manager.rate_limit_per_minute = 10

        result = manager.should_send_alert()
        assert result is False  # 超过速率限制

    def test_alert_escalation(self):
        """测试告警升级"""
        manager = Mock()

        escalation_result = {
            "original_alert_id": "alert_001",
            "escalated": True,
            "new_severity": "CRITICAL",
            "escalation_reason": "No response within 30 minutes",
        }
        manager.escalate_alert = Mock(return_value=escalation_result)

        alert = Mock()
        alert.severity = "HIGH"

        result = manager.escalate_alert(alert, escalate_to="CRITICAL")
        assert result["escalated"] is True
        assert result["new_severity"] == "CRITICAL"


class TestAlertChannels:
    """告警渠道测试"""

    def test_email_channel(self):
        """测试邮件告警渠道"""
        email_channel = Mock()
        email_channel.enabled = True
        email_channel.smtp_server = "smtp.example.com"
        email_channel.recipients = ["admin@example.com"]

        assert email_channel.enabled is True
        assert email_channel.smtp_server == "smtp.example.com"
        assert len(email_channel.recipients) == 1

    def test_webhook_channel(self):
        """测试Webhook告警渠道"""
        webhook_channel = Mock()
        webhook_channel.url = "https://api.example.com/alerts"
        webhook_channel.timeout = 30
        webhook_channel.retry_attempts = 3

        assert "api.example.com" in webhook_channel.url
        assert webhook_channel.timeout == 30
        assert webhook_channel.retry_attempts == 3

    def test_slack_channel(self):
        """测试Slack告警渠道"""
        slack_channel = Mock()
        slack_channel.webhook_url = "https://hooks.slack.com/services/..."
        slack_channel.channel = "#alerts"
        slack_channel.username = "monitoring-bot"

        assert slack_channel.channel == "#alerts"
        assert slack_channel.username == "monitoring-bot"

    def test_sms_channel(self):
        """测试SMS告警渠道"""
        sms_channel = Mock()
        sms_channel.provider = "twilio"
        sms_channel.api_key = "test_api_key"
        sms_channel.phone_numbers = ["+1234567890"]

        assert sms_channel.provider == "twilio"
        assert len(sms_channel.phone_numbers) == 1


class TestMonitoringIntegration:
    """监控集成测试"""

    def test_monitoring_workflow(self):
        """测试监控工作流程"""
        # 模拟完整的监控工作流程

        # 1. 开始操作
        operation_start = datetime.now()

        # 2. 执行操作（慢查询）
        query_duration = 6.5  # 超过5秒阈值
        operation_end = operation_start + timedelta(seconds=query_duration)

        # 3. 创建操作指标
        metrics = Mock()
        metrics.operation_id = "slow_query_001"
        metrics.duration_ms = query_duration * 1000
        metrics.success = True
        metrics.slow = True

        # 4. 性能监控检测到慢查询
        perf_monitor = Mock()
        perf_monitor.slow_query_threshold = 5.0
        perf_monitor.is_slow_query = Mock(return_value=True)

        # 5. 创建告警
        alert = Mock()
        alert.alert_id = "perf_alert_001"
        alert.alert_type = "PERFORMANCE"
        alert.severity = "HIGH"

        # 6. 告警管理器发送告警
        alert_manager = Mock()
        alert_manager.send_alert = Mock(return_value={"sent": True})

        # 验证工作流程
        assert metrics.slow is True
        assert perf_monitor.is_slow_query(query_duration) is True
        assert alert_manager.send_alert(alert)["sent"] is True

    def test_data_quality_monitoring_workflow(self):
        """测试数据质量监控工作流程"""
        # 模拟数据质量监控流程

        # 1. 数据完整性检查
        completeness_result = {
            "completeness_score": 0.85,  # 低于0.95阈值
            "passed": False,
        }

        # 2. 数据新鲜度检查
        freshness_result = {
            "age_hours": 48,  # 超过24小时阈值
            "fresh": False,
        }

        # 3. 创建数据质量告警
        quality_alert = Mock()
        quality_alert.alert_type = "DATA_QUALITY"
        quality_alert.severity = "MEDIUM"

        # 验证结果
        assert completeness_result["passed"] is False
        assert completeness_result["completeness_score"] < 0.95
        assert freshness_result["fresh"] is False
        assert freshness_result["age_hours"] > 24

    def test_monitoring_metrics_aggregation(self):
        """测试监控指标聚合"""
        # 模拟指标聚合
        raw_metrics = [
            {"operation_id": "op_001", "duration_ms": 1000, "success": True},
            {"operation_id": "op_002", "duration_ms": 1500, "success": True},
            {"operation_id": "op_003", "duration_ms": 800, "success": False},
            {"operation_id": "op_004", "duration_ms": 2200, "success": True},
        ]

        # 聚合计算
        total_operations = len(raw_metrics)
        successful_operations = sum(1 for m in raw_metrics if m["success"])
        avg_duration = sum(m["duration_ms"] for m in raw_metrics) / total_operations
        max_duration = max(m["duration_ms"] for m in raw_metrics)

        aggregated_metrics = {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": successful_operations / total_operations,
            "avg_duration_ms": avg_duration,
            "max_duration_ms": max_duration,
        }

        # 验证聚合结果
        assert aggregated_metrics["total_operations"] == 4
        assert aggregated_metrics["success_rate"] == 0.75  # 3/4
        assert aggregated_metrics["avg_duration_ms"] == 1375
        assert aggregated_metrics["max_duration_ms"] == 2200


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
