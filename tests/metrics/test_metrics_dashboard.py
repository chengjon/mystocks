#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 测试质量指标仪表盘

提供实时质量指标监控、可视化展示和交互式分析功能。
"""

import asyncio
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from .test_quality_metrics import TestQualityMetrics, TestSuiteMetrics, TestResult


class AlertLevel(Enum):
    """告警级别"""

    CRITICAL = "critical"  # 严重
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中等
    LOW = "low"  # 低
    INFO = "info"  # 信息


class MetricStatus(Enum):
    """指标状态"""

    HEALTHY = "healthy"  # 健康
    WARNING = "warning"  # 警告
    CRITICAL = "critical"  # 严重
    UNKNOWN = "unknown"  # 未知


@dataclass
class QualityAlert:
    """质量告警"""

    id: str
    metric_name: str
    current_value: float
    threshold_value: float
    alert_level: AlertLevel
    message: str
    timestamp: datetime
    is_resolved: bool = False
    resolution_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricVisualization:
    """指标可视化数据"""

    metric_name: str
    chart_type: str  # "line", "bar", "pie", "gauge", "heatmap"
    data: List[Union[float, Dict[str, Any]]]
    labels: List[str]
    colors: List[str]
    options: Dict[str, Any] = field(default_factory=dict)


class TestMetricsMonitor:
    """测试指标监控器"""

    def __init__(self):
        self.quality_metrics = TestQualityMetrics()
        self.alerts: List[QualityAlert] = []
        self.monitoring_config = {
            "check_interval": 60,  # 秒
            "alert_thresholds": {
                "quality_score": {"critical": 60, "high": 75, "medium": 85, "low": 95},
                "pass_rate": {"critical": 85, "high": 90, "medium": 95, "low": 98},
                "coverage": {"critical": 70, "high": 80, "medium": 90, "low": 95},
            },
        }
        self.monitoring_history = []
        self.is_monitoring = False

    async def start_monitoring(self):
        """启动监控"""
        print("🔴 启动质量指标监控...")
        self.is_monitoring = True

        while self.is_monitoring:
            try:
                await self._check_quality_metrics()
                await asyncio.sleep(self.monitoring_config["check_interval"])
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                await asyncio.sleep(60)  # 出错后等待60秒再重试

    def stop_monitoring(self):
        """停止监控"""
        print("🟢 停止质量指标监控")
        self.is_monitoring = False

    async def _check_quality_metrics(self):
        """检查质量指标"""
        print(f"📊 执行质量指标检查 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

        # 生成模拟测试结果用于监控
        test_results = self._generate_monitoring_test_results()
        code_files = ["src/main.py", "src/services.py", "src/utils.py"]

        # 计算质量指标
        suite_metrics = self.quality_metrics.calculate_test_suite_metrics(
            test_results, code_files
        )

        if suite_metrics:
            # 生成可视化数据
            visualizations = self._generate_visualizations(suite_metrics)

            # 检查告警
            alerts = self._check_alerts(suite_metrics)

            # 记录监控历史
            self._record_monitoring_event(suite_metrics, visualizations, alerts)

            # 打印监控摘要
            self._print_monitoring_summary(suite_metrics, alerts)

    def _generate_monitoring_test_results(self) -> List[TestResult]:
        """生成用于监控的测试结果"""
        test_results = []
        num_tests = np.random.randint(50, 200)

        for i in range(num_tests):
            # 模拟测试状态分布
            status_prob = np.random.random()
            if status_prob < 0.85:  # 85% 通过
                status = "passed"
                duration = np.random.exponential(1.0)  # 指数分布
            elif status_prob < 0.92:  # 7% 失败
                status = "failed"
                duration = np.random.uniform(0.5, 5.0)
            elif status_prob < 0.97:  # 5% 错误
                status = "error"
                duration = np.random.uniform(0.3, 3.0)
            else:  # 3% 跳过
                status = "skipped"
                duration = np.random.uniform(0.1, 0.5)

            test_result = TestResult(
                test_id=f"monitor_test_{i + 1:03d}",
                test_name=f"Monitoring Test {i + 1}",
                status=status,
                duration=duration,
                timestamp=datetime.now()
                - timedelta(seconds=np.random.randint(0, 3600)),
                error_message=f"Monitor error {i}"
                if status in ["failed", "error"]
                else None,
                metadata={
                    "error_type": np.random.choice(
                        ["assertion", "timeout", "network", "unknown"]
                    ),
                    "category": np.random.choice(
                        ["unit", "integration", "e2e", "performance"]
                    ),
                },
            )
            test_results.append(test_result)

        return test_results

    def _generate_visualizations(
        self, suite_metrics: TestSuiteMetrics
    ) -> Dict[str, MetricVisualization]:
        """生成可视化数据"""
        visualizations = {}

        # 测试结果饼图
        visualizations["test_results_pie"] = MetricVisualization(
            metric_name="测试结果分布",
            chart_type="pie",
            data=[
                suite_metrics.passed_tests,
                suite_metrics.failed_tests,
                suite_metrics.skipped_tests,
                suite_metrics.error_tests,
            ],
            labels=["通过", "失败", "跳过", "错误"],
            colors=["#28a745", "#dc3545", "#ffc107", "#6c757d"],
            options={"title": "测试结果分布", "legend_position": "bottom"},
        )

        # 质量得分趋势图
        if len(self.quality_metrics.quality_history) >= 2:
            recent_history = self.quality_metrics.quality_history[-20:]
            visualizations["quality_trend"] = MetricVisualization(
                metric_name="质量得分趋势",
                chart_type="line",
                data=[m.quality_score for m in recent_history],
                labels=[m.timestamp.strftime("%m-%d %H:%M") for m in recent_history],
                colors=["#007bff"],
                options={
                    "title": "质量得分趋势",
                    "y_axis_label": "得分",
                    "x_axis_label": "时间",
                },
            )

        # 覆盖率进度条
        visualizations["coverage_gauge"] = MetricVisualization(
            metric_name="代码覆盖率",
            chart_type="gauge",
            data=[suite_metrics.coverage_percentage],
            labels=["覆盖率"],
            colors=["#17a2b8"],
            options={"title": "代码覆盖率", "max_value": 100, "min_value": 0},
        )

        # 性能指标柱状图
        visualizations["performance_bar"] = MetricVisualization(
            metric_name="性能指标",
            chart_type="bar",
            data=[
                suite_metrics.average_duration * 1000,  # 转换为毫秒
                suite_metrics.total_duration * 1000,
                suite_metrics.reliability_score,
                suite_metrics.performance_score,
            ],
            labels=["平均耗时(ms)", "总耗时(ms)", "可靠性得分", "性能得分"],
            colors=["#fd7e14", "#6f42c1", "#20c997", "#e83e8c"],
            options={"title": "性能指标对比"},
        )

        # 按类别分组的测试热力图
        category_counts = {}
        for result in suite_metrics.test_results:
            category = result.metadata.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        visualizations["category_heatmap"] = MetricVisualization(
            metric_name="按类别分组的测试",
            chart_type="heatmap",
            data=[{"name": k, "value": v} for k, v in category_counts.items()],
            labels=list(category_counts.keys()),
            colors=["#fff3cd", "#ffeaa7", "#fab1a0", "#e17055"],
            options={"title": "测试类别分布"},
        )

        return visualizations

    def _check_alerts(self, suite_metrics: TestSuiteMetrics) -> List[QualityAlert]:
        """检查质量指标并生成告警"""
        new_alerts = []
        thresholds = self.monitoring_config["alert_thresholds"]

        # 检查质量得分
        self._check_metric_alert(
            suite_metrics.quality_score,
            thresholds["quality_score"],
            "综合质量得分",
            suite_metrics,
            new_alerts,
        )

        # 检查通过率
        self._check_metric_alert(
            suite_metrics.pass_rate,
            thresholds["pass_rate"],
            "测试通过率",
            suite_metrics,
            new_alerts,
        )

        # 检查覆盖率
        self._check_metric_alert(
            suite_metrics.coverage_percentage,
            thresholds["coverage"],
            "代码覆盖率",
            suite_metrics,
            new_alerts,
        )

        # 检查异常
        self._check_anomaly_alerts(suite_metrics, new_alerts)

        # 添加到告警列表
        self.alerts.extend(new_alerts)

        # 清理已解决的告警
        self._cleanup_resolved_alerts()

        return new_alerts

    def _check_metric_alert(
        self,
        value: float,
        thresholds: Dict[str, float],
        metric_name: str,
        suite_metrics: TestSuiteMetrics,
        alerts: List[QualityAlert],
    ):
        """检查单个指标的告警"""
        if value < thresholds["critical"]:
            level = AlertLevel.CRITICAL
            message = f"{metric_name} 严重不足 ({value:.1f} < {thresholds['critical']})"
        elif value < thresholds["high"]:
            level = AlertLevel.HIGH
            message = f"{metric_name} 较低 ({value:.1f} < {thresholds['high']})"
        elif value < thresholds["medium"]:
            level = AlertLevel.MEDIUM
            message = f"{metric_name} 接近阈值 ({value:.1f} < {thresholds['medium']})"
        elif value < thresholds["low"]:
            level = AlertLevel.LOW
            message = f"{metric_name} 接近目标 ({value:.1f} < {thresholds['low']})"
        else:
            return

        alert = QualityAlert(
            id=f"alert_{int(time.time())}_{len(self.alerts)}",
            metric_name=metric_name,
            current_value=value,
            threshold_value=thresholds.get("low", 100),
            alert_level=level,
            message=message,
            timestamp=datetime.now(),
            metadata={"suite_name": suite_metrics.suite_name, "thresholds": thresholds},
        )
        alerts.append(alert)

    def _check_anomaly_alerts(
        self, suite_metrics: TestSuiteMetrics, alerts: List[QualityAlert]
    ):
        """检查异常告警"""
        # 检查测试执行时间异常
        durations = [r.duration for r in suite_metrics.test_results]
        if durations:
            avg_duration = statistics.mean(durations)
            std_duration = statistics.stdev(durations) if len(durations) > 1 else 0

            # 检查是否有异常慢的测试
            slow_tests = [
                r
                for r in suite_metrics.test_results
                if r.duration > avg_duration + 3 * std_duration
            ]
            if slow_tests:
                slow_test_ids = [t.test_id for t in slow_tests[:3]]
                alert = QualityAlert(
                    id=f"anomaly_slow_{int(time.time())}",
                    metric_name="性能异常",
                    current_value=len(slow_tests),
                    threshold_value=0,
                    alert_level=AlertLevel.MEDIUM,
                    message=f"检测到 {len(slow_tests)} 个执行异常缓慢的测试",
                    timestamp=datetime.now(),
                    metadata={"slow_test_ids": slow_test_ids},
                )
                alerts.append(alert)

    def _cleanup_resolved_alerts(self):
        """清理已解决的告警"""
        self.alerts = [
            alert
            for alert in self.alerts
            if not alert.is_resolved
            or (alert.is_resolved and (datetime.now() - alert.resolution_time).days < 7)
        ]

    def _record_monitoring_event(
        self,
        suite_metrics: TestSuiteMetrics,
        visualizations: Dict,
        alerts: List[QualityAlert],
    ):
        """记录监控事件"""
        event = {
            "timestamp": datetime.now(),
            "suite_metrics": suite_metrics.__dict__,
            "visualizations": {k: v.__dict__ for k, v in visualizations.items()},
            "alert_count": len(alerts),
            "alert_levels": {
                alert.alert_level.value: len(
                    [a for a in alerts if a.alert_level == alert.alert_level]
                )
                for alert in alerts
            },
        }
        self.monitoring_history.append(event)

        # 只保留最近100条记录
        if len(self.monitoring_history) > 100:
            self.monitoring_history = self.monitoring_history[-100:]

    def _print_monitoring_summary(
        self, suite_metrics: TestSuiteMetrics, alerts: List[QualityAlert]
    ):
        """打印监控摘要"""
        print("\n📊 质量指标监控摘要")
        print(f"   ┌─ 综合质量得分: {suite_metrics.quality_score:.1f}")
        print(f"   ├─ 测试通过率: {suite_metrics.pass_rate:.1f}%")
        print(f"   ├─ 代码覆盖率: {suite_metrics.coverage_percentage:.1f}%")
        print(f"   ├─ 平均耗时: {suite_metrics.average_duration:.2f}s")
        print(f"   ├─ 总测试数: {suite_metrics.total_tests}")
        print(f"   └─ 活跃告警: {len(alerts)}")

        if alerts:
            print("   ⚠️  告警详情:")
            for alert in alerts[:3]:  # 显示前3个告警
                print(f"      • {alert.alert_level.value.upper()}: {alert.message}")

    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """获取监控仪表盘数据"""
        if not self.monitoring_history:
            return {"status": "no_data"}

        latest_event = self.monitoring_history[-1]
        latest_metrics = TestSuiteMetrics(**latest_event["suite_metrics"])

        return {
            "current_status": {
                "quality_score": latest_metrics.quality_score,
                "pass_rate": latest_metrics.pass_rate,
                "coverage_percentage": latest_metrics.coverage_percentage,
                "total_tests": latest_metrics.total_tests,
                "average_duration": latest_metrics.average_duration,
                "timestamp": latest_event["timestamp"].isoformat(),
            },
            "alerts": {
                "total": len(self.alerts),
                "by_level": {
                    level.value: len([a for a in self.alerts if a.alert_level == level])
                    for level in AlertLevel
                },
                "active": len([a for a in self.alerts if not a.is_resolved]),
                "recent_alerts": [a.__dict__ for a in self.alerts[-5:]],
            },
            "historical_trends": {
                "timestamps": [
                    e["timestamp"].strftime("%Y-%m-%d %H:%M")
                    for e in self.monitoring_history[-20:]
                ],
                "quality_scores": [
                    e["suite_metrics"]["quality_score"]
                    for e in self.monitoring_history[-20:]
                ],
                "pass_rates": [
                    e["suite_metrics"]["pass_rate"]
                    for e in self.monitoring_history[-20:]
                ],
                "coverage_percentages": [
                    e["suite_metrics"]["coverage_percentage"]
                    for e in self.monitoring_history[-20:]
                ],
            },
            "visualizations": {
                name: viz.__dict__
                for name, viz in latest_event.get("visualizations", {}).items()
            },
            "system_health": self._assess_system_health(),
        }

    def _assess_system_health(self) -> Dict[str, Any]:
        """评估系统健康状态"""
        if not self.monitoring_history:
            return {"status": "unknown"}

        # 基于最近的监控数据评估
        recent_events = self.monitoring_history[-10:]  # 最近10次检查

        avg_quality = statistics.mean(
            [e["suite_metrics"]["quality_score"] for e in recent_events]
        )
        avg_pass_rate = statistics.mean(
            [e["suite_metrics"]["pass_rate"] for e in recent_events]
        )
        avg_coverage = statistics.mean(
            [e["suite_metrics"]["coverage_percentage"] for e in recent_events]
        )

        # 计算稳定性
        quality_stability = (
            100
            - statistics.stdev(
                [e["suite_metrics"]["quality_score"] for e in recent_events]
            )
            if len(recent_events) > 1
            else 100
        )

        # 确定健康状态
        if (
            avg_quality >= 90
            and avg_pass_rate >= 95
            and avg_coverage >= 85
            and quality_stability >= 90
        ):
            health_status = "excellent"
        elif (
            avg_quality >= 80
            and avg_pass_rate >= 90
            and avg_coverage >= 80
            and quality_stability >= 80
        ):
            health_status = "good"
        elif (
            avg_quality >= 70
            and avg_pass_rate >= 85
            and avg_coverage >= 75
            and quality_stability >= 70
        ):
            health_status = "fair"
        else:
            health_status = "poor"

        return {
            "status": health_status,
            "average_quality": round(avg_quality, 2),
            "average_pass_rate": round(avg_pass_rate, 2),
            "average_coverage": round(avg_coverage, 2),
            "stability": round(quality_stability, 2),
            "recommendations": self._generate_health_recommendations(
                health_status, avg_quality, avg_pass_rate, avg_coverage
            ),
        }

    def _generate_health_recommendations(
        self, status: str, quality: float, pass_rate: float, coverage: float
    ) -> List[str]:
        """生成健康状态建议"""
        recommendations = []

        if status == "excellent":
            recommendations.append("系统健康状态良好，继续保持最佳实践")
            recommendations.append("考虑引入更多自动化测试和高级功能")
        elif status == "good":
            recommendations.append("系统健康状态良好，仍有改进空间")
            if coverage < 85:
                recommendations.append("建议提高代码覆盖率")
        elif status == "fair":
            recommendations.append("系统健康状态一般，需要关注")
            if pass_rate < 90:
                recommendations.append("建议修复失败的测试用例")
            if quality < 80:
                recommendations.append("建议优化测试质量和可靠性")
        else:  # poor
            recommendations.append("系统健康状态较差，需要立即改进")
            recommendations.append("建议进行全面的质量评估和优化")

        return recommendations

    def export_monitoring_report(
        self, format: str = "json", file_path: str = None
    ) -> str:
        """导出监控报告"""
        dashboard_data = self.get_monitoring_dashboard()

        if format == "json":
            output = json.dumps(
                dashboard_data, ensure_ascii=False, indent=2, default=str
            )
        elif format == "html":
            output = self._generate_html_monitoring_report(dashboard_data)
        else:
            raise ValueError(f"不支持的格式: {format}")

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 监控报告已保存到: {file_path}")
            return file_path
        else:
            return output

    def _generate_html_monitoring_report(self, dashboard_data: Dict[str, Any]) -> str:
        """生成HTML格式的监控报告"""
        current = dashboard_data["current_status"]
        alerts = dashboard_data["alerts"]
        health = dashboard_data["system_health"]

        html_template = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>测试质量监控报告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }
                .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
                .metric-label { color: #6c757d; font-size: 0.9em; }
                .alert-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .health-status { padding: 10px 20px; border-radius: 5px; color: white; text-align: center; }
                .excellent { background-color: #28a745; }
                .good { background-color: #17a2b8; }
                .fair { background-color: #ffc107; color: #212529; }
                .poor { background-color: #dc3545; }
                .alert-list { max-height: 300px; overflow-y: auto; }
                .alert-item { padding: 10px; margin: 5px 0; border-radius: 5px; }
                .critical { background-color: #f8d7da; border-left: 4px solid #dc3545; }
                .high { background-color: #fff3cd; border-left: 4px solid #ffc107; }
                .medium { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
                .low { background-color: #d4edda; border-left: 4px solid #28a745; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #dee2e6; padding: 8px; text-align: left; }
                th { background-color: #f8f9fa; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>测试质量监控报告</h1>
                <p>生成时间: {generated_at}</p>
                <div class="health-status {health_class}">{health_status}</div>
            </div>

            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">{quality_score}</div>
                    <div class="metric-label">综合质量得分</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{pass_rate}%</div>
                    <div class="metric-label">测试通过率</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{coverage}%</div>
                    <div class="metric-label">代码覆盖率</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{duration}s</div>
                    <div class="metric-label">平均耗时</div>
                </div>
            </div>

            <div class="alert-section">
                <h2>告警概览</h2>
                <table>
                    <tr><th>严重级别</th><th>数量</th><th>活跃告警</th></tr>
                    {alert_table}
                </table>
                <div class="alert-list">
                    {recent_alerts}
                </div>
            </div>

            <div class="alert-section">
                <h2>健康建议</h2>
                <ul>
                    {recommendations}
                </ul>
            </div>
        </body>
        </html>
        """

        # 生成告警表格
        alert_table = ""
        for level, count in alerts["by_level"].items():
            active_count = len(
                [a for a in alerts["recent_alerts"] if a.get("alert_level") == level]
            )
            alert_table += f"<tr><td>{level.upper()}</td><td>{count}</td><td>{active_count}</td></tr>"

        # 生成最近告警
        recent_alerts = ""
        for alert in alerts["recent_alerts"][:5]:
            level_class = alert.get("alert_level", "low")
            recent_alerts += f"""
            <div class="alert-item {level_class}">
                <strong>{level_class.upper()}</strong> - {alert.get("message", "Unknown alert")}
                <br><small>{alert.get("timestamp", "")}</small>
            </div>
            """

        # 生成建议
        recommendations_html = ""
        for rec in health.get("recommendations", []):
            recommendations_html += f"<li>{rec}</li>"

        return html_template.format(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            health_class=health["status"],
            health_status=f"系统健康状态: {health['status'].upper()}",
            quality_score=current["quality_score"],
            pass_rate=current["pass_rate"],
            coverage=current["coverage_percentage"],
            duration=round(current["average_duration"], 2),
            alert_table=alert_table,
            recent_alerts=recent_alerts,
            recommendations=recommendations_html,
        )


async def demo_metrics_dashboard():
    """演示质量指标仪表盘"""
    print("🚀 演示质量指标仪表盘功能")

    # 创建监控器
    monitor = TestMetricsMonitor()

    # 模拟一些初始数据
    print("📊 添加初始监控数据...")
    for i in range(3):
        test_results = monitor._generate_monitoring_test_results()
        suite_metrics = monitor.quality_metrics.calculate_test_suite_metrics(
            test_results, ["src/main.py", "src/services.py"]
        )
        if suite_metrics:
            visualizations = monitor._generate_visualizations(suite_metrics)
            alerts = monitor._check_alerts(suite_metrics)
            monitor._record_monitoring_event(suite_metrics, visualizations, alerts)
            print(f"   ✓ 添加监控批次 {i + 1}")

    # 获取仪表盘数据
    dashboard_data = monitor.get_monitoring_dashboard()
    print(f"\n📈 系统健康状态: {dashboard_data['system_health']['status']}")
    print(f"🔔 活跃告警数: {dashboard_data['alerts']['active']}")

    # 导出报告
    html_file = monitor.export_monitoring_report(
        "html", "/tmp/test_metrics_dashboard.html"
    )
    print(f"📄 监控报告已保存: {html_file}")

    # 启动实时监控（演示5秒后停止）
    print("\n🔴 启动实时监控演示...")
    monitor_task = asyncio.create_task(monitor.start_monitoring())

    # 等待5秒
    await asyncio.sleep(5)

    # 停止监控
    monitor.stop_monitoring()
    await monitor_task

    print("✅ 监控演示完成")


if __name__ == "__main__":
    asyncio.run(demo_metrics_dashboard())
