"""
Monitoring and Alerting System for API Endpoints
API端点监控和警报系统

创建日期: 2025-11-26
版本: 1.0.0
"""

import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """警报严重程度"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class AlertRule:
    """警报规则"""

    name: str
    condition: str  # >, <, >=, <=, ==
    threshold: float
    severity: AlertSeverity
    duration: Optional[timedelta] = None  # 持续时间条件
    enabled: bool = True


@dataclass
class MetricValue:
    """指标值"""

    name: str
    value: float
    timestamp: datetime
    labels: Optional[Dict[str, str]] = None
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class Alert:
    """警报"""

    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class MetricsCollector:
    """指标收集器"""

    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()

    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """增加计数器"""
        key = self._make_key(name, labels)
        with self.lock:
            self.counters[key] += value

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """设置仪表值"""
        key = self._make_key(name, labels)
        with self.lock:
            self.gauges[key] = value

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """记录直方图"""
        key = self._make_key(name, labels)
        with self.lock:
            self.histograms[key].append(value)

    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None) -> None:
        """记录计时器"""
        key = self._make_key(name, labels)
        with self.lock:
            self.timers[key].append(duration)
            # 限制历史记录数量
            if len(self.timers[key]) > 1000:
                self.timers[key] = self.timers[key][-1000:]

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """创建指标键"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self.lock:
            summary = {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {},
                "timers": {},
                "timestamp": datetime.now().isoformat(),
            }

            # 计算直方图统计
            for key, values in self.histograms.items():
                if values:
                    summary["histograms"][key] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99),
                    }

            # 计算计时器统计
            for key, values in self.timers.items():
                if values:
                    summary["timers"][key] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "p95": self._percentile(values, 95),
                        "p99": self._percentile(values, 99),
                    }

            return summary

    def _percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        values_sorted = sorted(values)
        index = int(len(values_sorted) * percentile / 100)
        return values_sorted[min(index, len(values_sorted) - 1)]


class AlertManager:
    """警报管理器"""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 10000
        self.lock = threading.RLock()

    def add_rule(self, rule: AlertRule) -> None:
        """添加警报规则"""
        with self.lock:
            self.rules[rule.name] = rule

    def remove_rule(self, name: str) -> None:
        """移除警报规则"""
        with self.lock:
            if name in self.rules:
                del self.rules[name]
            # 清理相关警报
            alerts_to_remove = [alert_id for alert_id, alert in self.active_alerts.items() if alert.rule_name == name]
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]

    def check_metrics(self, metrics: Dict[str, MetricValue]) -> List[Alert]:
        """检查指标是否触发警报"""
        new_alerts = []
        current_time = datetime.now()

        with self.lock:
            for rule_name, rule in self.rules.items():
                if not rule.enabled:
                    continue

                # 查找相关指标
                matching_metrics = [m for m in metrics.values() if m.name == rule_name]

                for metric in matching_metrics:
                    if self._evaluate_condition(metric.value, rule.condition, rule.threshold):
                        alert_id = f"{rule_name}_{metric.timestamp.timestamp()}"

                        if alert_id not in self.active_alerts:
                            alert = Alert(
                                id=alert_id,
                                rule_name=rule_name,
                                severity=rule.severity,
                                message=f"{rule_name} {rule.condition} {rule.threshold} (current: {metric.value:.2f})",
                                timestamp=current_time,
                            )

                            self.active_alerts[alert_id] = alert
                            self.alert_history.append(alert)
                            new_alerts.append(alert)
                    else:
                        # 检查是否需要解决警报
                        alert_id = f"{rule_name}_{metric.timestamp.timestamp()}"
                        if alert_id in self.active_alerts:
                            alert = self.active_alerts[alert_id]
                            alert.resolved = True
                            alert.resolved_at = current_time
                            del self.active_alerts[alert_id]

        return new_alerts

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估条件"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 0.001  # 浮点数比较
        else:
            return False

    def get_active_alerts(self) -> List[Alert]:
        """获取活跃警报"""
        with self.lock:
            return list(self.active_alerts.values())

    def get_alert_summary(self) -> Dict[str, Any]:
        """获取警报摘要"""
        with self.lock:
            severity_count = defaultdict(int)
            for alert in self.active_alerts.values():
                severity_count[alert.severity.value] += 1

            return {
                "active_count": len(self.active_alerts),
                "severity_breakdown": dict(severity_count),
                "recent_alerts": [asdict(alert) for alert in self.alert_history[-10:]],
                "timestamp": datetime.now().isoformat(),
            }


class SystemMonitor:
    """系统监控器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.monitoring = False
        self.monitor_thread = None
        self.interval = 30  # 30秒监控间隔

    def start_monitoring(self) -> None:
        """开始监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System monitoring started")

    def stop_monitoring(self) -> None:
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("System monitoring stopped")

    def _monitor_loop(self) -> None:
        """监控循环"""
        while self.monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"System monitoring error: {e}")

    def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.set_gauge("system_cpu_percent", cpu_percent)

        # 内存使用率
        memory = psutil.virtual_memory()
        self.metrics_collector.set_gauge("system_memory_percent", memory.percent)
        self.metrics_collector.set_gauge("system_memory_used_mb", memory.used / 1024 / 1024)

        # 磁盘使用率
        disk = psutil.disk_usage("/")
        self.metrics_collector.set_gauge("system_disk_percent", disk.percent)
        self.metrics_collector.set_gauge("system_disk_used_gb", disk.used / 1024 / 1024 / 1024)

        # 网络IO
        network = psutil.net_io_counters()
        self.metrics_collector.increment("system_network_bytes_sent", network.bytes_sent)
        self.metrics_collector.increment("system_network_bytes_recv", network.bytes_recv)


class APIMonitor:
    """API监控器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)

    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float) -> None:
        """记录API请求"""
        endpoint_key = f"{method} {endpoint}"

        # 记录请求计数
        self.metrics_collector.increment("api_requests_total", labels={"endpoint": endpoint, "method": method})
        self.request_counts[endpoint_key] += 1

        # 记录响应时间
        self.metrics_collector.record_timer(
            "api_response_time",
            response_time,
            labels={"endpoint": endpoint, "method": method},
        )
        self.response_times[endpoint_key].append(response_time)

        # 记录状态码
        self.metrics_collector.increment(f"api_status_{status_code}", labels={"endpoint": endpoint, "method": method})

        # 记录错误
        if status_code >= 400:
            self.metrics_collector.increment(
                "api_errors_total",
                labels={
                    "endpoint": endpoint,
                    "method": method,
                    "status": str(status_code),
                },
            )
            self.error_counts[endpoint_key] += 1

    def get_api_summary(self) -> Dict[str, Any]:
        """获取API摘要"""
        summary = {
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "endpoints": {},
        }

        for endpoint, count in self.request_counts.items():
            error_count = self.error_counts.get(endpoint, 0)
            error_rate = (error_count / count * 100) if count > 0 else 0

            response_times = self.response_times.get(endpoint, [])
            avg_response_time = statistics.mean(response_times) if response_times else 0
            p95_response_time = self._percentile(response_times, 95) if response_times else 0

            summary["endpoints"][endpoint] = {
                "request_count": count,
                "error_count": error_count,
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "p95_response_time_ms": round(p95_response_time * 1000, 2),
            }

        return summary

    def _percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        values_sorted = sorted(values)
        index = int(len(values_sorted) * percentile / 100)
        return values_sorted[min(index, len(values_sorted) - 1)]


# 全局实例
_metrics_collector: Optional[MetricsCollector] = None
_alert_manager: Optional[AlertManager] = None
_system_monitor: Optional[SystemMonitor] = None
_api_monitor: Optional[APIMonitor] = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_alert_manager() -> AlertManager:
    """获取全局警报管理器"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def get_system_monitor() -> SystemMonitor:
    """获取全局系统监控器"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor(get_metrics_collector())
    return _system_monitor


def get_api_monitor() -> APIMonitor:
    """获取全局API监控器"""
    global _api_monitor
    if _api_monitor is None:
        _api_monitor = APIMonitor(get_metrics_collector())
    return _api_monitor


def setup_default_alert_rules() -> None:
    """设置默认警报规则"""
    alert_manager = get_alert_manager()

    # 系统警报规则
    alert_manager.add_rule(
        AlertRule(
            name="system_cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )
    )

    alert_manager.add_rule(
        AlertRule(
            name="system_memory_percent",
            condition=">",
            threshold=85.0,
            severity=AlertSeverity.WARNING,
        )
    )

    alert_manager.add_rule(
        AlertRule(
            name="api_response_time",
            condition=">",
            threshold=2.0,
            severity=AlertSeverity.ERROR,
        )  # 2秒
    )

    alert_manager.add_rule(
        AlertRule(
            name="api_errors_total",
            condition=">",
            threshold=10.0,
            severity=AlertSeverity.CRITICAL,
        )  # 10个错误
    )


def initialize_monitoring() -> None:
    """初始化监控系统"""
    logger.info("Initializing monitoring and alerting system...")

    # 设置默认警报规则
    setup_default_alert_rules()

    # 启动系统监控
    system_monitor = get_system_monitor()
    system_monitor.start_monitoring()

    logger.info("Monitoring and alerting system initialized")


def get_monitoring_dashboard() -> Dict[str, Any]:
    """获取监控仪表板数据"""
    metrics_collector = get_metrics_collector()
    alert_manager = get_alert_manager()
    api_monitor = get_api_monitor()

    return {
        "metrics": metrics_collector.get_metrics_summary(),
        "alerts": alert_manager.get_alert_summary(),
        "api": api_monitor.get_api_summary(),
        "system": {"timestamp": datetime.now().isoformat(), "status": "running"},
    }


if __name__ == "__main__":
    print("Testing monitoring and alerting system...")

    # 初始化监控系统
    initialize_monitoring()

    # 模拟API请求
    api_monitor = get_api_monitor()
    import random

    for i in range(100):
        endpoint = "/api/stocks/basic"
        method = "GET"
        status_code = 200 if random.random() > 0.1 else 500  # 10%错误率
        response_time = random.uniform(0.1, 3.0)  # 0.1-3.0秒响应时间

        api_monitor.record_request(endpoint, method, status_code, response_time)

    # 获取监控数据
    dashboard = get_monitoring_dashboard()

    print("\nMonitoring Dashboard:")
    print(f"Total API Requests: {dashboard['api']['total_requests']}")
    print(f"Total API Errors: {dashboard['api']['total_errors']}")
    print(f"Active Alerts: {dashboard['alerts']['active_count']}")

    print("\nMonitoring and alerting system basic functionality implemented")
    print("Main features:")
    print("  - Metrics collection (counters, gauges, histograms, timers)")
    print("  - Alert rules and management")
    print("  - System monitoring (CPU, memory, disk, network)")
    print("  - API performance monitoring")
    print("  - Real-time dashboard data")
    print("  - Default alert rules setup")
