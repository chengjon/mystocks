#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仪表盘

提供实时测试监控、可视化界面和交互式控制面板
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import webbrowser
from pathlib import Path

import psutil
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import plotly.graph_objects as go


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


# 创建仪表盘模板
def create_dashboard_templates():
    """创建HTML模板"""
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)

    dashboard_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStocks 测试仪表盘</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .metric-name {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        .metric-icon {
            font-size: 24px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .metric-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #666;
        }
        .trend-up { color: #e74c3c; }
        .trend-down { color: #27ae60; }
        .trend-neutral { color: #7f8c8d; }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        .test-executions {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .test-execution {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .test-execution:last-child {
            border-bottom: none;
        }
        .test-name {
            font-weight: 500;
            color: #333;
        }
        .test-status {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-running { background: #e3f2fd; color: #1976d2; }
        .status-passed { background: #e8f5e8; color: #2e7d32; }
        .status-failed { background: #ffebee; color: #c62828; }
        .status-skipped { background: #fff3e0; color: #f57c00; }
        .status-pending { background: #f5f5f5; color: #757575; }
        .progress-bar {
            width: 100px;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: #667eea;
            transition: width 0.3s ease;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-indicator-running { background: #1976d2; animation: pulse 2s infinite; }
        .status-indicator-passed { background: #2e7d32; }
        .status-indicator-failed { background: #c62828; }
        .status-indicator-skipped { background: #f57c00; }
        .status-indicator-pending { background: #757575; }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .alert-critical { background: #ffebee; border-left: 4px solid #c62828; }
        .alert-high { background: #fff3e0; border-left: 4px solid #f57c00; }
        .alert-medium { background: #fff8e1; border-left: 4px solid #ffa000; }
        .alert-low { background: #f3e5f5; border-left: 4px solid #7b1fa2; }
        .last-updated {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🚀 MyStocks 测试仪表盘</h1>
            <p>实时监控测试执行状态和系统性能</p>
        </div>

        <div class="metrics-grid" id="metrics-grid">
            <!-- 指标卡片将在这里动态生成 -->
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">测试执行状态分布</div>
                <div id="test-status-chart"></div>
            </div>
            <div class="chart-container">
                <div class="chart-title">CPU使用率趋势</div>
                <div id="cpu-trend-chart"></div>
            </div>
            <div class="chart-container">
                <div class="chart-title">资源监控</div>
                <div id="resource-gauges"></div>
            </div>
        </div>

        <div class="test-executions">
            <div class="chart-title">测试执行状态</div>
            <div id="test-executions-list">
                <!-- 测试执行列表将在这里动态生成 -->
            </div>
        </div>

        <div class="last-updated" id="last-updated">
            最后更新: --
        </div>
    </div>

    <script>
        // Socket.IO连接
        const socket = io();

        // 连接成功
        socket.on('connected', function(data) {
            console.log('已连接到仪表盘服务器');
            loadDashboardData();
        });

        // 指标更新
        socket.on('metrics_update', function(data) {
            updateMetrics(data);
        });

        // 测试执行更新
        socket.on('test_execution_update', function(data) {
            updateTestExecution(data);
        });

        // 告警触发
        socket.on('alert_triggered', function(data) {
            showAlert(data);
        });

        // 加载仪表盘数据
        function loadDashboardData() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => updateMetrics(data));

            fetch('/api/test-executions')
                .then(response => response.json())
                .then(data => updateTestExecutions(data));

            updateCharts();
        }

        // 更新指标显示
        function updateMetrics(data) {
            const metricsGrid = document.getElementById('metrics-grid');
            metricsGrid.innerHTML = '';

            data.metrics.forEach(metric => {
                const card = document.createElement('div');
                card.className = 'metric-card';

                const trendClass = `trend-${metric.trend}`;
                const trendIcon = metric.trend === 'up' ? '↗️' : metric.trend === 'down' ? '↘️' : '➡️';

                card.innerHTML = `
                    <div class="metric-header">
                        <span class="metric-name">${metric.name}</span>
                        <span class="metric-icon">${metric.icon}</span>
                    </div>
                    <div class="metric-value">${metric.value} ${metric.unit}</div>
                    <div class="metric-details">
                        <span class="${trendClass}">${trendIcon} ${Math.abs(metric.change).toFixed(1)}%</span>
                        <span>阈值: ${metric.threshold || '无'}</span>
                    </div>
                `;

                metricsGrid.appendChild(card);
            });

            document.getElementById('last-updated').textContent =
                `最后更新: ${new Date().toLocaleString()}`;
        }

        // 更新测试执行列表
        function updateTestExecutions(data) {
            const listContainer = document.getElementById('test-executions-list');
            listContainer.innerHTML = '';

            data.executions.forEach(execution => {
                const item = document.createElement('div');
                item.className = 'test-execution';

                const statusClass = `status-${execution.status}`;
                const statusIcon = getStatusIcon(execution.status);
                const progressWidth = (execution.progress * 100) + '%';

                item.innerHTML = `
                    <div>
                        <div class="test-name">
                            <span class="status-indicator status-indicator-${execution.status}"></span>
                            ${execution.name}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            ${execution.current_step || '等待执行...'}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="test-status ${statusClass}">${execution.status.toUpperCase()}</div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            ${execution.duration.toFixed(1)}s
                        </div>
                        <div class="progress-bar" style="width: 100px; margin: 5px 0;">
                            <div class="progress-fill" style="width: ${progressWidth}"></div>
                        </div>
                    </div>
                `;

                listContainer.appendChild(item);
            });
        }

        // 更新图表
        function updateCharts() {
            // 更新测试状态饼图
            fetch('/api/test-executions')
                .then(response => response.json())
                .then(data => {
                    const statusCounts = {};
                    data.executions.forEach(execution => {
                        statusCounts[execution.status] = (statusCounts[execution.status] || 0) + 1;
                    });

                    const trace = {
                        values: Object.values(statusCounts),
                        labels: Object.keys(statusCounts),
                        type: 'pie',
                        hole: 0.3
                    };

                    const layout = {
                        title: '测试执行状态分布',
                        title_x: 0.5
                    };

                    Plotly.newPlot('test-status-chart', [trace], layout);
                });

            // 更新CPU趋势图
            fetch('/api/history/1h')
                .then(response => response.json())
                .then(data => {
                    const cpuData = data.cpu_usage || [];
                    if (cpuData.length > 0) {
                        const trace = {
                            x: cpuData.map(d => d.timestamp),
                            y: cpuData.map(d => d.value),
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: 'CPU使用率'
                        };

                        const layout = {
                            title: 'CPU使用率趋势',
                            xaxis: { title: '时间' },
                            yaxis: { title: '使用率(%)' },
                            title_x: 0.5
                        };

                        Plotly.newPlot('cpu-trend-chart', [trace], layout);
                    }
                });
        }

        // 获取状态图标
        function getStatusIcon(status) {
            const icons = {
                'running': '🔄',
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'pending': '⏳'
            };
            return icons[status] || '❓';
        }

        // 显示告警
        function showAlert(alertData) {
            const alertContainer = document.createElement('div');
            alertContainer.className = `alert alert-${alertData.severity}`;

            alertContainer.innerHTML = `
                <strong>🚨 ${alertData.name}</strong><br>
                ${alertData.message}<br>
                <small>时间: ${new Date(alertData.timestamp).toLocaleString()}</small>
            `;

            document.body.insertBefore(alertContainer, document.body.firstChild);

            // 5秒后自动移除
            setTimeout(() => {
                alertContainer.remove();
            }, 5000);
        }

        // 定期刷新数据
        setInterval(loadDashboardData, 10000);
    </script>
</body>
</html>
    """

    with open(template_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(dashboard_template)


# 使用示例
def demo_test_dashboard():
    """演示测试仪表盘功能"""
    print("🚀 演示测试仪表盘功能")

    # 创建仪表盘
    dashboard = TestDashboard(host="localhost", port=5000, debug=True)

    # 添加一些示例指标
    dashboard.add_metric(
        DashboardMetric(
            name="测试覆盖率",
            value=85.5,
            unit="%",
            trend="up",
            change=5.2,
            threshold=80.0,
            color="green",
            icon="📈",
            description="当前测试覆盖率",
        )
    )

    dashboard.add_metric(
        DashboardMetric(
            name="API响应时间",
            value=234.5,
            unit="ms",
            trend="down",
            change=-12.3,
            threshold=500.0,
            color="blue",
            icon="⚡",
            description="平均API响应时间",
        )
    )

    dashboard.add_metric(
        DashboardMetric(
            name="测试成功率",
            value=98.2,
            unit="%",
            trend="neutral",
            change=0.0,
            threshold=95.0,
            color="green",
            icon="🎯",
            description="测试执行成功率",
        )
    )

    # 添加测试执行
    demo_test = TestExecutionStatus(
        test_id="test_001",
        name="用户登录测试",
        status="running",
        progress=0.65,
        start_time=datetime.now() - timedelta(minutes=5),
        duration=300.0,
        current_step="验证登录接口响应",
        total_steps=5,
        completed_steps=3,
    )
    dashboard.add_test_execution(demo_test)

    demo_test2 = TestExecutionStatus(
        test_id="test_002",
        name="数据库连接测试",
        status="passed",
        progress=1.0,
        start_time=datetime.now() - timedelta(minutes=10),
        duration=45.2,
        total_steps=3,
        completed_steps=3,
    )
    dashboard.add_test_execution(demo_test2)

    # 创建模板文件
    create_dashboard_templates()

    print("✅ 仪表盘准备完成")
    print(f"📊 指标数量: {len(dashboard.metrics)}")
    print(f"🔄 测试执行: {len(dashboard.test_executions)}")
    print(f"🚨 告警规则: {len(dashboard.alerts)}")
    print(f"🌐 访问地址: http://{dashboard.host}:{dashboard.port}")
    print("📋 API端点: /api/metrics, /api/test-executions, /api/alerts")

    return dashboard


if __name__ == "__main__":
    # 启动仪表盘
    dashboard = demo_test_dashboard()
    try:
        dashboard.start_dashboard()
    except KeyboardInterrupt:
        print("\n正在停止仪表盘...")
        dashboard.stop_dashboard()
