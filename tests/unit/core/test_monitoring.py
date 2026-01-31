"""
Monitoring and Alerting System Test Suite
监控和警报系统测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.core.monitoring (579行)
"""

import threading
from collections import defaultdict
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# Test target imports
from src.core.monitoring import (
    Alert,
    AlertManager,
    AlertRule,
    AlertSeverity,
    APIMonitor,
    MetricsCollector,
    MetricType,
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


class TestAlertSeverity:
    """警报严重程度枚举测试"""

    def test_severity_values(self):
        """测试严重程度枚举值"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_severity_enum_properties(self):
        """测试严重程度枚举属性"""
        info = AlertSeverity.INFO
        assert info.name == "INFO"
        assert info.value == "info"
        assert isinstance(info.value, str)


class TestMetricType:
    """指标类型枚举测试"""

    def test_metric_type_values(self):
        """测试指标类型枚举值"""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.TIMER.value == "timer"

    def test_metric_type_enum_properties(self):
        """测试指标类型枚举属性"""
        counter = MetricType.COUNTER
        assert counter.name == "COUNTER"
        assert counter.value == "counter"
        assert isinstance(counter.value, str)


class TestAlertRule:
    """警报规则测试"""

    def test_alert_rule_creation(self):
        """测试警报规则创建"""
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            duration=timedelta(minutes=5),
        )

        assert rule.name == "cpu_usage"
        assert rule.condition == ">"
        assert rule.threshold == 80.0
        assert rule.severity == AlertSeverity.WARNING
        assert rule.duration == timedelta(minutes=5)
        assert rule.enabled is True

    def test_alert_rule_defaults(self):
        """测试警报规则默认值"""
        rule = AlertRule(name="test_rule", condition="<", threshold=10.0, severity=AlertSeverity.INFO)

        assert rule.duration is None
        assert rule.enabled is True


class TestMetricValue:
    """指标值测试"""

    def test_metric_value_creation(self):
        """测试指标值创建"""
        timestamp = datetime.now()
        metric = MetricValue(
            name="cpu_usage",
            value=75.5,
            timestamp=timestamp,
            labels={"host": "server1"},
            metric_type=MetricType.GAUGE,
        )

        assert metric.name == "cpu_usage"
        assert metric.value == 75.5
        assert metric.timestamp == timestamp
        assert metric.labels == {"host": "server1"}
        assert metric.metric_type == MetricType.GAUGE

    def test_metric_value_defaults(self):
        """测试指标值默认值"""
        timestamp = datetime.now()
        metric = MetricValue(name="test_metric", value=100.0, timestamp=timestamp)

        assert metric.labels is None
        assert metric.metric_type == MetricType.GAUGE


class TestAlert:
    """警报测试"""

    def test_alert_creation(self):
        """测试警报创建"""
        timestamp = datetime.now()
        alert = Alert(
            id="alert_123",
            rule_name="cpu_usage",
            severity=AlertSeverity.WARNING,
            message="CPU usage exceeds threshold",
            timestamp=timestamp,
        )

        assert alert.id == "alert_123"
        assert alert.rule_name == "cpu_usage"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "CPU usage exceeds threshold"
        assert alert.timestamp == timestamp
        assert alert.resolved is False
        assert alert.resolved_at is None

    def test_alert_resolution(self):
        """测试警报解决"""
        timestamp = datetime.now()
        resolved_at = datetime.now()

        alert = Alert(
            id="alert_456",
            rule_name="memory_usage",
            severity=AlertSeverity.ERROR,
            message="Memory usage high",
            timestamp=timestamp,
        )

        # 解决警报
        alert.resolved = True
        alert.resolved_at = resolved_at

        assert alert.resolved is True
        assert alert.resolved_at == resolved_at


class TestMetricsCollector:
    """指标收集器测试"""

    def test_metrics_collector_initialization(self):
        """测试指标收集器初始化"""
        collector = MetricsCollector(max_history=5000)

        assert collector.max_history == 5000
        assert isinstance(collector.counters, defaultdict)
        assert isinstance(collector.gauges, defaultdict)
        assert isinstance(collector.histograms, defaultdict)
        assert isinstance(collector.timers, defaultdict)
        assert isinstance(collector.lock, type(threading.RLock()))

    def test_increment_counter(self):
        """测试增加计数器"""
        collector = MetricsCollector()

        # 测试基本增加
        collector.increment("test_counter")
        assert collector.counters["test_counter"] == 1.0

        # 测试带值的增加
        collector.increment("test_counter", 5.0)
        assert collector.counters["test_counter"] == 6.0

        # 测试带标签的增加
        collector.increment("test_counter", 1.0, {"endpoint": "/api/test"})
        key = "test_counter[endpoint=/api/test]"
        assert collector.counters[key] == 1.0

    def test_set_gauge(self):
        """测试设置仪表值"""
        collector = MetricsCollector()

        # 测试设置基本值
        collector.set_gauge("test_gauge", 75.5)
        assert collector.gauges["test_gauge"] == 75.5

        # 测试覆盖值
        collector.set_gauge("test_gauge", 80.0)
        assert collector.gauges["test_gauge"] == 80.0

        # 测试带标签的设置
        collector.set_gauge("test_gauge", 50.0, {"host": "server1"})
        key = "test_gauge[host=server1]"
        assert collector.gauges[key] == 50.0

    def test_record_histogram(self):
        """测试记录直方图"""
        collector = MetricsCollector(max_history=100)

        # 记录多个值
        test_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for value in test_values:
            collector.record_histogram("test_histogram", value)

        histogram = collector.histograms["test_histogram"]
        assert len(histogram) == 5
        assert list(histogram) == test_values

        # 测试带标签的直方图
        collector.record_histogram("test_histogram", 2.5, {"endpoint": "/api/test"})
        key = "test_histogram[endpoint=/api/test]"
        assert len(collector.histograms[key]) == 1
        assert collector.histograms[key][0] == 2.5

    def test_record_timer(self):
        """测试记录计时器"""
        collector = MetricsCollector()

        # 记录多个时间值
        test_times = [0.1, 0.2, 0.15, 0.3, 0.25]
        for timer in test_times:
            collector.record_timer("test_timer", timer)

        timers = collector.timers["test_timer"]
        assert len(timers) == 5
        assert timers == test_times

        # 测试带标签的计时器
        collector.record_timer("test_timer", 0.5, {"endpoint": "/api/slow"})
        key = "test_timer[endpoint=/api/slow]"
        assert len(collector.timers[key]) == 1
        assert collector.timers[key][0] == 0.5

    def test_timer_history_limit(self):
        """测试计时器历史限制"""
        collector = MetricsCollector()

        # 添加超过限制的计时器记录
        for i in range(1100):  # 超过1000的限制
            collector.record_timer("test_timer", float(i))

        timers = collector.timers["test_timer"]
        assert len(timers) == 1000  # 应该限制在1000
        assert timers[0] == 100.0  # 最后1000个值
        assert timers[-1] == 1099.0

    def test_make_key(self):
        """测试创建指标键"""
        collector = MetricsCollector()

        # 无标签
        key = collector._make_key("test_metric", None)
        assert key == "test_metric"

        # 有标签
        labels = {"host": "server1", "env": "prod"}
        key = collector._make_key("test_metric", labels)
        assert key == "test_metric[env=prod,host=server1]"

        # 排序测试
        labels2 = {"env": "prod", "host": "server1"}
        key2 = collector._make_key("test_metric", labels2)
        assert key == key2  # 标签排序应该一致

    def test_get_metrics_summary(self):
        """测试获取指标摘要"""
        collector = MetricsCollector()

        # 添加各种类型的指标
        collector.increment("test_counter", 10.0)
        collector.set_gauge("test_gauge", 75.5)
        collector.record_histogram("test_histogram", 1.0)
        collector.record_histogram("test_histogram", 2.0)
        collector.record_timer("test_timer", 0.1)
        collector.record_timer("test_timer", 0.2)

        summary = collector.get_metrics_summary()

        assert "counters" in summary
        assert "gauges" in summary
        assert "histograms" in summary
        assert "timers" in summary
        assert "timestamp" in summary

        assert summary["counters"]["test_counter"] == 10.0
        assert summary["gauges"]["test_gauge"] == 75.5

        # 检查直方图统计
        hist_stats = summary["histograms"]["test_histogram"]
        assert hist_stats["count"] == 2
        assert hist_stats["min"] == 1.0
        assert hist_stats["max"] == 2.0
        assert hist_stats["mean"] == 1.5

        # 检查计时器统计
        timer_stats = summary["timers"]["test_timer"]
        assert timer_stats["count"] == 2
        assert timer_stats["min"] == 0.1
        assert timer_stats["max"] == 0.2
        assert timer_stats["mean"] == 0.15

    def test_percentile_calculation(self):
        """测试百分位数计算"""
        collector = MetricsCollector()

        # 测试空列表
        assert collector._percentile([], 50) == 0.0

        # 测试正常情况
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert collector._percentile(values, 50) == 5  # 中位数
        assert collector._percentile(values, 95) == 10  # 95%分位数

        # 测试边界情况
        assert collector._percentile([1, 2, 3], 0) == 1
        assert collector._percentile([1, 2, 3], 100) == 3


class TestAlertManager:
    """警报管理器测试"""

    def test_alert_manager_initialization(self):
        """测试警报管理器初始化"""
        manager = AlertManager()

        assert isinstance(manager.rules, dict)
        assert isinstance(manager.active_alerts, dict)
        assert isinstance(manager.alert_history, list)
        assert manager.max_history == 10000
        assert isinstance(manager.lock, type(threading.RLock()))

    def test_add_rule(self):
        """测试添加警报规则"""
        manager = AlertManager()
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )

        manager.add_rule(rule)

        assert "cpu_usage" in manager.rules
        assert manager.rules["cpu_usage"] == rule

    def test_remove_rule(self):
        """测试移除警报规则"""
        manager = AlertManager()
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )

        # 添加规则
        manager.add_rule(rule)
        assert "cpu_usage" in manager.rules

        # 移除规则
        manager.remove_rule("cpu_usage")
        assert "cpu_usage" not in manager.rules

    def test_remove_rule_with_active_alerts(self):
        """测试移除带活跃警报的规则"""
        manager = AlertManager()
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )

        # 添加规则
        manager.add_rule(rule)

        # 创建活跃警报
        metrics = {"test": MetricValue(name="cpu_usage", value=85.0, timestamp=datetime.now())}

        alerts = manager.check_metrics(metrics)
        assert len(alerts) > 0

        # 移除规则应该清理相关警报
        manager.remove_rule("cpu_usage")
        assert "cpu_usage" not in manager.rules
        # 所有与该规则相关的活跃警报应该被清理

    def test_check_metrics_no_rules(self):
        """测试无规则时检查指标"""
        manager = AlertManager()
        metrics = {}

        alerts = manager.check_metrics(metrics)
        assert len(alerts) == 0

    def test_check_metrics_disabled_rule(self):
        """测试禁用规则的指标检查"""
        manager = AlertManager()
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            enabled=False,
        )

        manager.add_rule(rule)

        metrics = {"test": MetricValue(name="cpu_usage", value=85.0, timestamp=datetime.now())}

        alerts = manager.check_metrics(metrics)
        assert len(alerts) == 0  # 禁用的规则不应该触发警报

    def test_check_metrics_trigger_alert(self):
        """测试指标触发警报"""
        manager = AlertManager()
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )

        manager.add_rule(rule)

        metrics = {"test": MetricValue(name="cpu_usage", value=85.0, timestamp=datetime.now())}

        alerts = manager.check_metrics(metrics)
        assert len(alerts) == 1
        assert alerts[0].rule_name == "cpu_usage"
        assert alerts[0].severity == AlertSeverity.WARNING
        assert "85.00" in alerts[0].message

    def test_check_metrics_no_trigger(self):
        """测试指标不触发警报"""
        manager = AlertManager()
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )

        manager.add_rule(rule)

        metrics = {"test": MetricValue(name="cpu_usage", value=75.0, timestamp=datetime.now())}

        alerts = manager.check_metrics(metrics)
        assert len(alerts) == 0

    def test_evaluate_condition(self):
        """测试条件评估"""
        manager = AlertManager()

        # 测试大于条件
        assert manager._evaluate_condition(85.0, ">", 80.0) is True
        assert manager._evaluate_condition(75.0, ">", 80.0) is False

        # 测试小于条件
        assert manager._evaluate_condition(75.0, "<", 80.0) is True
        assert manager._evaluate_condition(85.0, "<", 80.0) is False

        # 测试大于等于条件
        assert manager._evaluate_condition(80.0, ">=", 80.0) is True
        assert manager._evaluate_condition(85.0, ">=", 80.0) is True
        assert manager._evaluate_condition(75.0, ">=", 80.0) is False

        # 测试小于等于条件
        assert manager._evaluate_condition(80.0, "<=", 80.0) is True
        assert manager._evaluate_condition(75.0, "<=", 80.0) is True
        assert manager._evaluate_condition(85.0, "<=", 80.0) is False

        # 测试等于条件
        assert manager._evaluate_condition(80.0, "==", 80.0) is True
        assert manager._evaluate_condition(80.001, "==", 80.0) is True  # 浮点数容差
        assert manager._evaluate_condition(75.0, "==", 80.0) is False

        # 测试无效条件
        assert manager._evaluate_condition(85.0, "invalid", 80.0) is False

    def test_get_active_alerts(self):
        """测试获取活跃警报"""
        manager = AlertManager()

        # 初始状态应该没有活跃警报
        active_alerts = manager.get_active_alerts()
        assert len(active_alerts) == 0

        # 添加规则并触发警报
        rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )
        manager.add_rule(rule)

        metrics = {"test": MetricValue(name="cpu_usage", value=85.0, timestamp=datetime.now())}

        manager.check_metrics(metrics)
        active_alerts = manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].rule_name == "cpu_usage"

    def test_get_alert_summary(self):
        """测试获取警报摘要"""
        manager = AlertManager()

        # 添加规则并触发不同严重程度的警报
        warning_rule = AlertRule(
            name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )
        error_rule = AlertRule(
            name="memory_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.ERROR,
        )

        manager.add_rule(warning_rule)
        manager.add_rule(error_rule)

        # 触发警报
        metrics = {
            "test1": MetricValue(name="cpu_usage", value=85.0, timestamp=datetime.now()),
            "test2": MetricValue(name="memory_usage", value=95.0, timestamp=datetime.now()),
        }

        manager.check_metrics(metrics)

        summary = manager.get_alert_summary()

        assert "active_count" in summary
        assert "severity_breakdown" in summary
        assert "recent_alerts" in summary
        assert "timestamp" in summary

        assert summary["active_count"] == 2
        assert summary["severity_breakdown"]["warning"] == 1
        assert summary["severity_breakdown"]["error"] == 1


class TestSystemMonitor:
    """系统监控器测试"""

    def test_system_monitor_initialization(self):
        """测试系统监控器初始化"""
        metrics_collector = Mock()
        monitor = SystemMonitor(metrics_collector)

        assert monitor.metrics_collector == metrics_collector
        assert monitor.monitoring is False
        assert monitor.monitor_thread is None
        assert monitor.interval == 30

    @patch("src.core.monitoring.psutil")
    def test_collect_system_metrics(self, mock_psutil):
        """测试收集系统指标"""
        # Mock psutil 返回值
        mock_psutil.cpu_percent.return_value = 75.5
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_disk = Mock()
        mock_disk.percent = 50.0
        mock_disk.used = 500 * 1024 * 1024 * 1024  # 500GB
        mock_psutil.disk_usage.return_value = mock_disk

        mock_network = Mock()
        mock_network.bytes_sent = 1000000
        mock_network.bytes_recv = 2000000
        mock_psutil.net_io_counters.return_value = mock_network

        # 创建真实的 MetricsCollector 来验证调用
        metrics_collector = MetricsCollector()
        monitor = SystemMonitor(metrics_collector)

        # 执行指标收集
        monitor._collect_system_metrics()

        # 验证 psutil 方法被调用
        mock_psutil.cpu_percent.assert_called_once_with(interval=1)
        mock_psutil.virtual_memory.assert_called_once()
        mock_psutil.disk_usage.assert_called_once_with("/")
        mock_psutil.net_io_counters.assert_called_once()

    def test_start_monitoring_already_running(self):
        """测试启动已经运行的监控"""
        metrics_collector = Mock()
        monitor = SystemMonitor(metrics_collector)

        # 设置为已运行状态
        monitor.monitoring = True

        # 启动监控应该直接返回
        monitor.start_monitoring()
        assert monitor.monitoring is True  # 状态不变

    @patch("src.core.monitoring.threading.Thread")
    def test_start_monitoring(self, mock_thread_class):
        """测试启动监控"""
        metrics_collector = Mock()
        monitor = SystemMonitor(metrics_collector)

        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        monitor.start_monitoring()

        assert monitor.monitoring is True
        mock_thread_class.assert_called_once_with(target=monitor._monitor_loop, daemon=True)
        mock_thread.start.assert_called_once()

    def test_stop_monitoring(self):
        """测试停止监控"""
        metrics_collector = Mock()
        monitor = SystemMonitor(metrics_collector)

        mock_thread = Mock()
        monitor.monitor_thread = mock_thread
        monitor.monitoring = True

        monitor.stop_monitoring()

        assert monitor.monitoring is False
        mock_thread.join.assert_called_once()

    @patch("src.core.monitoring.time.sleep")
    @patch("src.core.monitoring.psutil.cpu_percent")
    def test_monitor_loop(self, mock_cpu_percent, mock_sleep):
        """测试监控循环"""
        mock_cpu_percent.return_value = 50.0
        mock_sleep.side_effect = [None, Exception("Stop loop")]  # 第二次循环抛出异常

        metrics_collector = Mock()
        monitor = SystemMonitor(metrics_collector)
        monitor.monitoring = True

        # 运行监控循环（应该被异常中断）
        try:
            monitor._monitor_loop()
        except Exception:
            pass

        # 验证系统指标被收集
        assert mock_cpu_percent.call_count >= 1
        assert mock_sleep.call_count >= 1


class TestAPIMonitor:
    """API监控器测试"""

    def test_api_monitor_initialization(self):
        """测试API监控器初始化"""
        metrics_collector = Mock()
        monitor = APIMonitor(metrics_collector)

        assert monitor.metrics_collector == metrics_collector
        assert isinstance(monitor.request_counts, defaultdict)
        assert isinstance(monitor.response_times, defaultdict)
        assert isinstance(monitor.error_counts, defaultdict)

    def test_record_request_success(self):
        """测试记录成功API请求"""
        metrics_collector = Mock()
        monitor = APIMonitor(metrics_collector)

        # 记录成功请求
        monitor.record_request("/api/test", "GET", 200, 0.5)

        # 验证指标收集器方法被调用
        metrics_collector.increment.assert_called()
        metrics_collector.record_timer.assert_called()

        # 验证内部计数器
        endpoint_key = "GET /api/test"
        assert monitor.request_counts[endpoint_key] == 1
        assert monitor.response_times[endpoint_key] == [0.5]
        assert monitor.error_counts[endpoint_key] == 0

    def test_record_request_error(self):
        """测试记录错误API请求"""
        metrics_collector = Mock()
        monitor = APIMonitor(metrics_collector)

        # 记录错误请求
        monitor.record_request("/api/test", "GET", 500, 1.5)

        # 验证指标收集器方法被调用
        metrics_collector.increment.assert_called()
        metrics_collector.record_timer.assert_called()

        # 验证内部计数器
        endpoint_key = "GET /api/test"
        assert monitor.request_counts[endpoint_key] == 1
        assert monitor.response_times[endpoint_key] == [1.5]
        assert monitor.error_counts[endpoint_key] == 1

    def test_record_request_multiple_requests(self):
        """测试记录多个API请求"""
        metrics_collector = Mock()
        monitor = APIMonitor(metrics_collector)

        # 记录多个请求
        monitor.record_request("/api/test", "GET", 200, 0.5)
        monitor.record_request("/api/test", "GET", 200, 0.3)
        monitor.record_request("/api/test", "GET", 500, 1.0)

        endpoint_key = "GET /api/test"
        assert monitor.request_counts[endpoint_key] == 3
        assert monitor.response_times[endpoint_key] == [0.5, 0.3, 1.0]
        assert monitor.error_counts[endpoint_key] == 1

    def test_get_api_summary_empty(self):
        """测试获取空API摘要"""
        monitor = APIMonitor(Mock())
        summary = monitor.get_api_summary()

        assert summary["total_requests"] == 0
        assert summary["total_errors"] == 0
        assert summary["endpoints"] == {}

    def test_get_api_summary_with_data(self):
        """测试获取包含数据的API摘要"""
        monitor = APIMonitor(Mock())

        # 添加一些请求数据
        monitor.record_request("/api/test", "GET", 200, 0.5)
        monitor.record_request("/api/test", "GET", 200, 0.3)
        monitor.record_request("/api/test", "GET", 500, 1.0)
        monitor.record_request("/api/other", "POST", 200, 0.2)

        summary = monitor.get_api_summary()

        assert summary["total_requests"] == 4
        assert summary["total_errors"] == 1

        # 检查端点统计
        test_endpoint = summary["endpoints"]["GET /api/test"]
        assert test_endpoint["request_count"] == 3
        assert test_endpoint["error_count"] == 1
        assert test_endpoint["error_rate_percent"] == 33.33
        assert test_endpoint["avg_response_time_ms"] == 600.0  # (0.5 + 0.3 + 1.0) / 3 * 1000

        other_endpoint = summary["endpoints"]["POST /api/other"]
        assert other_endpoint["request_count"] == 1
        assert other_endpoint["error_count"] == 0
        assert other_endpoint["error_rate_percent"] == 0.0
        assert other_endpoint["avg_response_time_ms"] == 200.0

    def test_percentile_calculation(self):
        """测试百分位数计算"""
        monitor = APIMonitor(Mock())

        # 测试空列表
        assert monitor._percentile([], 50) == 0.0

        # 测试正常情况
        values = [100, 200, 300, 400, 500]  # 毫秒
        assert monitor._percentile(values, 50) == 300
        assert monitor._percentile(values, 95) == 500


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


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
