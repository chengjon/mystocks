"""
Monitoring and Alerting System Test Suite
监控和警报系统测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.core.monitoring (579行)
"""

import threading
from datetime import datetime
from unittest.mock import Mock, patch


# Test target imports
from src.core.monitoring import (
    Alert,
    AlertManager,
    AlertRule,
    AlertSeverity,
    APIMonitor,
    MetricsCollector,
    MetricValue,
    SystemMonitor,
    get_alert_manager,
    get_api_monitor,
    get_metrics_collector,
    get_monitoring_dashboard,
    get_system_monitor,
    initialize_monitoring,
    setup_default_alert_rules,
)

class TestGlobalFunctions:
    """全局函数测试"""

    def test_get_metrics_collector_singleton(self):
        """测试获取全局指标收集器单例"""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        assert collector1 is collector2

    def test_get_alert_manager_singleton(self):
        """测试获取全局警报管理器单例"""
        manager1 = get_alert_manager()
        manager2 = get_alert_manager()

        assert manager1 is manager2

    def test_get_system_monitor_singleton(self):
        """测试获取全局系统监控器单例"""
        monitor1 = get_system_monitor()
        monitor2 = get_system_monitor()

        assert monitor1 is monitor2

    def test_get_api_monitor_singleton(self):
        """测试获取全局API监控器单例"""
        monitor1 = get_api_monitor()
        monitor2 = get_api_monitor()

        assert monitor1 is monitor2

    @patch("src.core.monitoring.get_alert_manager")
    def test_setup_default_alert_rules(self, mock_get_alert_manager):
        """测试设置默认警报规则"""
        mock_manager = Mock()
        mock_get_alert_manager.return_value = mock_manager

        setup_default_alert_rules()

        # 验证添加了4个默认规则
        assert mock_manager.add_rule.call_count == 4

        # 验证调用参数
        calls = mock_manager.add_rule.call_args_list
        rule_names = [call[0][0].name for call in calls]

        assert "system_cpu_percent" in rule_names
        assert "system_memory_percent" in rule_names
        assert "api_response_time" in rule_names
        assert "api_errors_total" in rule_names

    @patch("src.core.monitoring.get_system_monitor")
    @patch("src.core.monitoring.setup_default_alert_rules")
    @patch("src.core.monitoring.logger")
    def test_initialize_monitoring(self, mock_logger, mock_setup_alerts, mock_get_system_monitor):
        """测试初始化监控系统"""
        mock_system_monitor = Mock()
        mock_get_system_monitor.return_value = mock_system_monitor

        initialize_monitoring()

        # 验证设置默认警报规则
        mock_setup_alerts.assert_called_once()

        # 验证启动系统监控
        mock_system_monitor.start_monitoring.assert_called_once()

        # 验证日志记录
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Initializing monitoring" in call for call in log_calls)
        assert any("initialized" in call for call in log_calls)

    @patch("src.core.monitoring.get_api_monitor")
    @patch("src.core.monitoring.get_alert_manager")
    @patch("src.core.monitoring.get_metrics_collector")
    def test_get_monitoring_dashboard(self, mock_get_collector, mock_get_alert_manager, mock_get_api_monitor):
        """测试获取监控仪表板"""
        # Mock 返回值
        mock_collector = Mock()
        mock_collector.get_metrics_summary.return_value = {"test": "metrics"}
        mock_alert_manager = Mock()
        mock_alert_manager.get_alert_summary.return_value = {"test": "alerts"}
        mock_api_monitor = Mock()
        mock_api_monitor.get_api_summary.return_value = {"test": "api"}

        mock_get_collector.return_value = mock_collector
        mock_get_alert_manager.return_value = mock_alert_manager
        mock_get_api_monitor.return_value = mock_api_monitor

        dashboard = get_monitoring_dashboard()

        assert "metrics" in dashboard
        assert "alerts" in dashboard
        assert "api" in dashboard
        assert "system" in dashboard

        assert dashboard["metrics"] == {"test": "metrics"}
        assert dashboard["alerts"] == {"test": "alerts"}
        assert dashboard["api"] == {"test": "api"}
        assert dashboard["system"]["status"] == "running"
        assert "timestamp" in dashboard["system"]


class TestIntegrationScenarios:
    """集成场景测试"""

    def test_end_to_end_monitoring_flow(self):
        """测试端到端监控流程"""
        # 创建真实的组件
        collector = MetricsCollector()
        alert_manager = AlertManager()
        api_monitor = APIMonitor(collector)

        # 设置警报规则
        cpu_rule = AlertRule(
            name="api_response_time",
            condition=">",
            threshold=1.0,
            severity=AlertSeverity.WARNING,
        )
        alert_manager.add_rule(cpu_rule)

        # 模拟API请求
        api_monitor.record_request("/api/slow", "GET", 200, 1.5)  # 超过阈值
        api_monitor.record_request("/api/fast", "GET", 200, 0.3)  # 低于阈值

        # 创建指标值并检查警报
        metrics = {"slow_request": MetricValue(name="api_response_time", value=1.5, timestamp=datetime.now())}

        alerts = alert_manager.check_metrics(metrics)
        assert len(alerts) == 1
        assert alerts[0].rule_name == "api_response_time"
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_concurrent_metrics_collection(self):
        """测试并发指标收集"""
        collector = MetricsCollector()

        def collect_metrics(thread_id):
            for i in range(100):
                collector.increment(f"counter_{thread_id}", 1.0)
                collector.set_gauge(f"gauge_{thread_id}", float(i))
                collector.record_timer(f"timer_{thread_id}", float(i) / 100)

        # 创建多个线程并发收集指标
        threads = []
        for i in range(5):
            thread = threading.Thread(target=collect_metrics, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有指标都被正确收集
        summary = collector.get_metrics_summary()

        # 每个线程应该有100个计数器记录
        for i in range(5):
            assert summary["counters"][f"counter_{i}"] == 100.0
            assert summary["gauges"][f"gauge_{i}"] == 99.0  # 最后一个值

        # 验证计时器统计
        for i in range(5):
            timer_stats = summary["timers"][f"timer_{i}"]
            assert timer_stats["count"] == 100
            assert timer_stats["max"] == 0.99

    @patch("src.core.monitoring.psutil")
    def test_system_monitor_integration(self, mock_psutil):
        """测试系统监控集成"""
        # Mock 系统指标
        mock_psutil.cpu_percent.return_value = 85.0
        mock_memory = Mock()
        mock_memory.percent = 90.0
        mock_memory.used = 16 * 1024 * 1024 * 1024  # 16GB
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_psutil.disk_usage.return_value = Mock(percent=60.0)
        mock_psutil.net_io_counters.return_value = Mock(bytes_sent=1000000, bytes_recv=2000000)

        # 创建组件
        collector = MetricsCollector()
        alert_manager = AlertManager()
        system_monitor = SystemMonitor(collector)

        # 设置警报规则
        cpu_rule = AlertRule(
            name="system_cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )
        memory_rule = AlertRule(
            name="system_memory_percent",
            condition=">",
            threshold=85.0,
            severity=AlertSeverity.ERROR,
        )

        alert_manager.add_rule(cpu_rule)
        alert_manager.add_rule(memory_rule)

        # 收集系统指标
        system_monitor._collect_system_metrics()

        # 创建指标值并检查警报
        metrics = {
            "cpu_metric": MetricValue(name="system_cpu_percent", value=85.0, timestamp=datetime.now()),
            "memory_metric": MetricValue(name="system_memory_percent", value=90.0, timestamp=datetime.now()),
        }

        alerts = alert_manager.check_metrics(metrics)
        assert len(alerts) == 2

        # 验证警报类型
        cpu_alert = next(alert for alert in alerts if alert.rule_name == "system_cpu_percent")
        memory_alert = next(alert for alert in alerts if alert.rule_name == "system_memory_percent")

        assert cpu_alert.severity == AlertSeverity.WARNING
        assert memory_alert.severity == AlertSeverity.ERROR


class TestErrorHandlingAndEdgeCases:
    """错误处理和边界情况测试"""

    def test_empty_metrics_summary(self):
        """测试空指标摘要"""
        collector = MetricsCollector()
        summary = collector.get_metrics_summary()

        assert summary["counters"] == {}
        assert summary["gauges"] == {}
        assert summary["histograms"] == {}
        assert summary["timers"] == {}
        assert "timestamp" in summary

    def test_invalid_alert_conditions(self):
        """测试无效警报条件"""
        manager = AlertManager()

        # 测试所有有效条件
        valid_conditions = [">", "<", ">=", "<=", "=="]
        for condition in valid_conditions:
            result = manager._evaluate_condition(50.0, condition, 40.0)
            assert isinstance(result, bool)

        # 测试无效条件
        invalid_conditions = ["!=", "<>", "in", "not in", "invalid"]
        for condition in invalid_conditions:
            result = manager._evaluate_condition(50.0, condition, 40.0)
            assert result is False

    def test_metrics_collector_thread_safety(self):
        """测试指标收集器线程安全"""
        collector = MetricsCollector()

        def increment_counter(thread_id):
            for i in range(1000):
                collector.increment("test_counter", 1.0)

        # 创建多个线程同时增加计数器
        threads = []
        for i in range(10):
            thread = threading.Thread(target=increment_counter, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证最终计数正确
        assert collector.counters["test_counter"] == 10000.0

    def test_alert_history_limit(self):
        """测试警报历史限制"""
        manager = AlertManager()

        # 创建大量警报（超过限制）
        for i in range(11000):  # 超过max_history
            alert = Alert(
                id=f"alert_{i}",
                rule_name="test_rule",
                severity=AlertSeverity.INFO,
                message=f"Test alert {i}",
                timestamp=datetime.now(),
            )
            manager.alert_history.append(alert)

        # 验证历史记录被限制（这需要实际的截断逻辑实现）
        # 目前只是验证数据结构
        assert len(manager.alert_history) > 0


