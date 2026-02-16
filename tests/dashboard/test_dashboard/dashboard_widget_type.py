#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仪表盘

提供实时测试监控、可视化界面和交互式控制面板
"""

import threading
import time
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import plotly.graph_objects as go
import psutil
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

class DashboardWidgetType(Enum):
    """仪表盘组件类型"""

    METRICS_OVERVIEW = "metrics_overview"
    TEST_EXECUTION = "test_execution"
    PERFORMANCE_CHARTS = "performance_charts"
    TREND_ANALYSIS = "trend_analysis"
    HEATMAP = "heatmap"
    GAUGE_CHART = "gauge_chart"
    REAL_TIME_MONITORING = "real_time_monitoring"
    ALERTS_NOTIFICATIONS = "alerts_notifications"
    TEST_SUITE_STATUS = "test_suite_status"
    RESOURCE_MONITORING = "resource_monitoring"


@dataclass
class DashboardMetric:
    """仪表盘指标"""

    name: str
    value: Union[int, float, str]
    unit: str = ""
    trend: str = "neutral"  # up, down, neutral
    change: float = 0.0
    threshold: Optional[float] = None
    color: str = "blue"
    icon: str = "📊"
    description: str = ""


@dataclass
class TestExecutionStatus:
    """测试执行状态"""

    test_id: str
    name: str
    status: str  # running, passed, failed, skipped, pending
    progress: float = 0.0
    start_time: Optional[datetime] = None
    duration: float = 0.0
    error_message: Optional[str] = None
    current_step: str = ""
    total_steps: int = 0
    completed_steps: int = 0


@dataclass
class AlertConfig:
    """告警配置"""

    id: str
    name: str
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    severity: str  # critical, high, medium, low
    enabled: bool = True
    message_template: str = ""
    notification_channels: List[str] = field(default_factory=list)


class TestDashboard:
    """测试仪表盘主类"""

    def __init__(self, host: str = "localhost", port: int = 5000, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # 仪表盘数据存储
        self.metrics: Dict[str, DashboardMetric] = {}
        self.test_executions: Dict[str, TestExecutionStatus] = {}
        self.alerts: List[AlertConfig] = []
        self.history_data: Dict[str, List[Dict[str, Any]]] = {}
        self.resource_data: Dict[str, List[float]] = {}

        # 实时更新控制
        self.update_interval = 2  # 秒
        self.is_running = False
        self.update_thread = None

        # 配置Flask路由
        self._setup_routes()
        self._setup_socketio_events()

        # 初始化告警
        self._init_alerts()

    def _setup_routes(self):
        """设置Flask路由"""

        @self.app.route("/")
        def index():
            """仪表盘主页"""
            return render_template("dashboard.html")

        @self.app.route("/api/metrics")
        def get_metrics():
            """获取所有指标"""
            return jsonify(
                {
                    "metrics": self._serialize_metrics(),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        @self.app.route("/api/metrics/<metric_name>")
        def get_metric(metric_name: str):
            """获取特定指标"""
            if metric_name in self.metrics:
                return jsonify(self._serialize_metric(self.metrics[metric_name]))
            return jsonify({"error": "Metric not found"}), 404

        @self.app.route("/api/test-executions")
        def get_test_executions():
            """获取测试执行状态"""
            return jsonify(
                {
                    "executions": self._serialize_test_executions(),
                    "count": len(self.test_executions),
                }
            )

        @self.app.route("/api/test-executions/<test_id>")
        def get_test_execution(test_id: str):
            """获取特定测试执行状态"""
            if test_id in self.test_executions:
                return jsonify(self._serialize_test_execution(self.test_executions[test_id]))
            return jsonify({"error": "Test execution not found"}), 404

        @self.app.route("/api/alerts")
        def get_alerts():
            """获取告警配置"""
            return jsonify(
                {
                    "alerts": self._serialize_alerts(),
                    "active_count": sum(1 for a in self.alerts if a.enabled),
                }
            )

        @self.app.route("/api/history/<period>")
        def get_history(period: str):
            """获取历史数据"""
            # period: '1h', '24h', '7d', '30d'
            return jsonify(self._get_history_data(period))

        @self.app.route("/api/resource-monitoring")
        def get_resource_monitoring():
            """获取资源监控数据"""
            return jsonify(
                {
                    "cpu": self.get_cpu_usage(),
                    "memory": self.get_memory_usage(),
                    "disk": self.get_disk_usage(),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        @self.app.route("/api/health")
        def health_check():
            """健康检查"""
            return jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "metrics_count": len(self.metrics),
                    "active_executions": len([t for t in self.test_executions.values() if t.status == "running"]),
                }
            )

    def _setup_socketio_events(self):
        """设置Socket.IO事件"""

        @self.socketio.on("connect")
        def handle_connect():
            """客户端连接"""
            print(f"客户端已连接: {request.sid}")
            emit("connected", {"status": "connected"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """客户端断开连接"""
            print(f"客户端已断开: {request.sid}")

        @self.socketio.on("subscribe_metrics")
        def handle_subscribe_metrics(data):
            """订阅指标更新"""
            emit("metrics_update", self._serialize_metrics())

        @self.socketio.on("subscribe_test_executions")
        def handle_subscribe_test_executions(data):
            """订阅测试执行状态"""
            emit("test_executions_update", self._serialize_test_executions())

    def _init_alerts(self):
        """初始化告警配置"""
        # 默认告警规则
        default_alerts = [
            AlertConfig(
                id="cpu_high",
                name="CPU使用率过高",
                metric_name="cpu_usage",
                operator=">",
                threshold=80.0,
                severity="high",
                enabled=True,
                message_template="CPU使用率达到 {value}%，超过阈值 {threshold}%",
            ),
            AlertConfig(
                id="memory_high",
                name="内存使用率过高",
                metric_name="memory_usage",
                operator=">",
                threshold=85.0,
                severity="high",
                enabled=True,
                message_template="内存使用率达到 {value}%，超过阈值 {threshold}%",
            ),
            AlertConfig(
                id="test_failure_rate_high",
                name="测试失败率过高",
                metric_name="test_failure_rate",
                operator=">",
                threshold=20.0,
                severity="critical",
                enabled=True,
                message_template="测试失败率达到 {value}%，超过阈值 {threshold}%",
            ),
            AlertConfig(
                id="response_time_high",
                name="API响应时间过长",
                metric_name="avg_response_time",
                operator=">",
                threshold=5000.0,
                severity="medium",
                enabled=True,
                message_template="平均API响应时间为 {value}ms，超过阈值 {threshold}ms",
            ),
        ]

        self.alerts.extend(default_alerts)

    def add_metric(self, metric: DashboardMetric):
        """添加仪表盘指标"""
        self.metrics[metric.name] = metric
        self._add_to_history(
            metric.name,
            {
                "timestamp": datetime.now().isoformat(),
                "value": metric.value,
                "trend": metric.trend,
                "change": metric.change,
            },
        )

    def update_metric(
        self,
        name: str,
        value: Union[int, float, str],
        trend: str = "neutral",
        change: float = 0.0,
    ):
        """更新指标值"""
        if name in self.metrics:
            self.metrics[name].value = value
            self.metrics[name].trend = trend
            self.metrics[name].change = change

            # 添加到历史数据
            self._add_to_history(
                name,
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": value,
                    "trend": trend,
                    "change": change,
                },
            )

            # 检查告警
            self._check_alerts(name, value)

    def add_test_execution(self, execution: TestExecutionStatus):
        """添加测试执行"""
        self.test_executions[execution.test_id] = execution

    def update_test_execution(self, test_id: str, **kwargs):
        """更新测试执行状态"""
        if test_id in self.test_executions:
            for key, value in kwargs.items():
                if hasattr(self.test_executions[test_id], key):
                    setattr(self.test_executions[test_id], key, value)

            # 广播更新
            self.socketio.emit(
                "test_execution_update",
                self._serialize_test_execution(self.test_executions[test_id]),
            )

    def _add_to_history(self, metric_name: str, data: Dict[str, Any]):
        """添加历史数据"""
        if metric_name not in self.history_data:
            self.history_data[metric_name] = []

        self.history_data[metric_name].append(data)

        # 保留最近1000条记录
        if len(self.history_data[metric_name]) > 1000:
            self.history_data[metric_name] = self.history_data[metric_name][-1000:]

    def _check_alerts(self, metric_name: str, value: float):
        """检查告警"""
        for alert in self.alerts:
            if not alert.enabled or alert.metric_name != metric_name:
                continue

            triggered = False
            if alert.operator == ">" and value > alert.threshold:
                triggered = True
            elif alert.operator == ">=" and value >= alert.threshold:
                triggered = True
            elif alert.operator == "<" and value < alert.threshold:
                triggered = True
            elif alert.operator == "<=" and value <= alert.threshold:
                triggered = True
            elif alert.operator == "==" and value == alert.threshold:
                triggered = True
            elif alert.operator == "!=" and value != alert.threshold:
                triggered = True

            if triggered:
                self._trigger_alert(alert, value)

    def _trigger_alert(self, alert: AlertConfig, value: float):
        """触发告警"""
        message = alert.message_template.format(value=value, threshold=alert.threshold)

        alert_data = {
            "id": f"alert_{int(time.time())}",
            "alert_config_id": alert.id,
            "name": alert.name,
            "message": message,
            "severity": alert.severity,
            "metric_name": alert.metric_name,
            "value": value,
            "threshold": alert.threshold,
            "timestamp": datetime.now().isoformat(),
        }

        # 广播告警
        self.socketio.emit("alert_triggered", alert_data)

        print(f"🚨 告警触发: {alert.name} - {message}")

    def get_cpu_usage(self) -> Dict[str, float]:
        """获取CPU使用率"""
        cpu_percent = psutil.cpu_percent(interval=1)
        return {
            "usage_percent": cpu_percent,
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True),
        }

    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "usage_percent": memory.percent,
            "cached_gb": round(memory.cached / (1024**3), 2) if hasattr(memory, "cached") else 0,
        }

    def get_disk_usage(self) -> Dict[str, Any]:
        """获取磁盘使用情况"""
        disk = psutil.disk_usage("/")
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "usage_percent": round((disk.used / disk.total) * 100, 2),
        }

    def _get_history_data(self, period: str) -> Dict[str, Any]:
        """获取历史数据"""
        now = datetime.now()
        cutoff_time = None

        if period == "1h":
            cutoff_time = now - timedelta(hours=1)
        elif period == "24h":
            cutoff_time = now - timedelta(days=1)
        elif period == "7d":
            cutoff_time = now - timedelta(days=7)
        elif period == "30d":
            cutoff_time = now - timedelta(days=30)

        history_result = {}

        for metric_name, data in self.history_data.items():
            if cutoff_time:
                filtered_data = [item for item in data if datetime.fromisoformat(item["timestamp"]) >= cutoff_time]
            else:
                filtered_data = data

            history_result[metric_name] = filtered_data[-100:]  # 返回最近100条

        return history_result

    def _serialize_metrics(self) -> List[Dict[str, Any]]:
        """序列化指标数据"""
        return [self._serialize_metric(metric) for metric in self.metrics.values()]

    def _serialize_metric(self, metric: DashboardMetric) -> Dict[str, Any]:
        """序列化单个指标"""
        return {
            "name": metric.name,
            "value": metric.value,
            "unit": metric.unit,
            "trend": metric.trend,
            "change": metric.change,
            "threshold": metric.threshold,
            "color": metric.color,
            "icon": metric.icon,
            "description": metric.description,
        }

    def _serialize_test_executions(self) -> List[Dict[str, Any]]:
        """序列化测试执行数据"""
        return [self._serialize_test_execution(execution) for execution in self.test_executions.values()]

    def _serialize_test_execution(self, execution: TestExecutionStatus) -> Dict[str, Any]:
        """序列化单个测试执行"""
        return {
            "test_id": execution.test_id,
            "name": execution.name,
            "status": execution.status,
            "progress": execution.progress,
            "start_time": execution.start_time.isoformat() if execution.start_time else None,
            "duration": execution.duration,
            "error_message": execution.error_message,
            "current_step": execution.current_step,
            "total_steps": execution.total_steps,
            "completed_steps": execution.completed_steps,
        }

    def _serialize_alerts(self) -> List[Dict[str, Any]]:
        """序列化告警配置"""
        return [
            {
                "id": alert.id,
                "name": alert.name,
                "metric_name": alert.metric_name,
                "operator": alert.operator,
                "threshold": alert.threshold,
                "severity": alert.severity,
                "enabled": alert.enabled,
                "message_template": alert.message_template,
            }
            for alert in self.alerts
        ]

    def create_charts(self):
        """创建仪表盘图表"""
        charts = {}

        # 测试执行状态饼图
        status_counts = {}
        for execution in self.test_executions.values():
            status_counts[execution.status] = status_counts.get(execution.status, 0) + 1

        if status_counts:
            charts["test_status_pie"] = go.Figure(
                data=[
                    go.Pie(
                        labels=list(status_counts.keys()),
                        values=list(status_counts.values()),
                        hole=0.3,
                    )
                ]
            )
            charts["test_status_pie"].update_layout(title="测试执行状态分布", title_x=0.5)

        # CPU使用率趋势图
        if "cpu_usage" in self.history_data:
            cpu_data = self.history_data["cpu_usage"][-50:]  # 最近50个数据点
            charts["cpu_trend"] = go.Figure(
                data=[
                    go.Scatter(
                        x=[d["timestamp"] for d in cpu_data],
                        y=[d["value"] for d in cpu_data],
                        mode="lines+markers",
                        name="CPU使用率",
                    )
                ]
            )
            charts["cpu_trend"].update_layout(
                title="CPU使用率趋势",
                xaxis_title="时间",
                yaxis_title="使用率(%)",
                title_x=0.5,
            )

        # 资源监控仪表盘
        resource_charts = {}

        # CPU仪表
        if "cpu_usage" in self.metrics:
            cpu_value = self.metrics["cpu_usage"].value
            resource_charts["cpu_gauge"] = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=cpu_value,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "CPU使用率 (%)"},
                    delta={"reference": 50},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 80], "color": "gray"},
                            {"range": [80, 100], "color": "lightcoral"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 90,
                        },
                    },
                )
            )

        # 内存仪表
        if "memory_usage" in self.metrics:
            mem_value = self.metrics["memory_usage"].value
            resource_charts["memory_gauge"] = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=mem_value,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "内存使用率 (%)"},
                    delta={"reference": 50},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkgreen"},
                        "steps": [
                            {"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 80], "color": "gray"},
                            {"range": [80, 100], "color": "lightcoral"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 90,
                        },
                    },
                )
            )

        charts["resource_monitoring"] = resource_charts

        return charts

    def start_dashboard(self):
        """启动仪表盘"""
        print(f"🚀 启动测试仪表盘 http://{self.host}:{self.port}")

        # 启动资源监控更新线程
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_resources)
        self.update_thread.daemon = True
        self.update_thread.start()

        # 自动打开浏览器
        def open_browser():
            time.sleep(2)  # 等待服务器启动
            webbrowser.open(f"http://{self.host}:{self.port}")

        threading.Thread(target=open_browser, daemon=True).start()

        # 启动Flask应用
        self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug)

    def _update_resources(self):
        """更新资源监控数据"""
        while self.is_running:
            try:
                # 更新CPU使用率
                cpu_data = self.get_cpu_usage()
                cpu_metric = DashboardMetric(
                    name="cpu_usage",
                    value=cpu_data["usage_percent"],
                    unit="%",
                    trend="up" if cpu_data["usage_percent"] > 70 else "down",
                    change=5.0,
                    threshold=80.0,
                    color="red" if cpu_data["usage_percent"] > 80 else "blue",
                    icon="💻",
                    description="当前CPU使用率",
                )
                self.add_metric(cpu_metric)

                # 更新内存使用率
                memory_data = self.get_memory_usage()
                memory_metric = DashboardMetric(
                    name="memory_usage",
                    value=memory_data["usage_percent"],
                    unit="%",
                    trend="up" if memory_data["usage_percent"] > 70 else "down",
                    change=3.0,
                    threshold=85.0,
                    color="red" if memory_data["usage_percent"] > 85 else "blue",
                    icon="🧠",
                    description="当前内存使用率",
                )
                self.add_metric(memory_metric)

                # 更新磁盘使用率
                disk_data = self.get_disk_usage()
                disk_metric = DashboardMetric(
                    name="disk_usage",
                    value=disk_data["usage_percent"],
                    unit="%",
                    trend="neutral",
                    change=0.0,
                    threshold=90.0,
                    color="orange" if disk_data["usage_percent"] > 80 else "blue",
                    icon="💾",
                    description="当前磁盘使用率",
                )
                self.add_metric(disk_metric)

                # 通过Socket.IO广播更新
                self.socketio.emit("metrics_update", self._serialize_metrics())

            except Exception as e:
                print(f"资源监控更新错误: {e}")

            time.sleep(self.update_interval)

    def stop_dashboard(self):
        """停止仪表盘"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("✅ 仪表盘已停止")


