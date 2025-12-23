"""
测试指标分析模块

提供测试性能指标收集、分析和可视化功能。
"""

import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional
import statistics

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"  # 计数器，只增不减
    GAUGE = "gauge"  # 测量值，可增可减
    HISTOGRAM = "histogram"  # 直方图，分布数据
    SUMMARY = "summary"  # 摘要，统计信息


@dataclass
class MetricDefinition:
    """指标定义"""

    name: str
    description: str
    type: MetricType
    unit: str = ""
    tags: List[str] = field(default_factory=list)
    aggregation: str = "avg"  # avg, sum, max, min, count
    retention_hours: int = 24  # 数据保留时间


@dataclass
class TimeSeriesPoint:
    """时间序列数据点"""

    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricCollector:
    """指标收集器"""

    def __init__(self, max_points_per_metric: int = 10000):
        self.max_points_per_metric = max_points_per_metric
        self.time_series: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_points_per_metric)
        )
        self.counter_values: Dict[str, float] = defaultdict(float)
        self.histogram_buckets: Dict[str, List[float]] = defaultdict(list)
        self.definitions: Dict[str, MetricDefinition] = {}

    def register_metric(self, definition: MetricDefinition):
        """注册指标"""
        self.definitions[definition.name] = definition
        logging.info(f"注册指标: {definition.name}")

    def record_counter(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """记录计数器指标"""
        if name not in self.definitions:
            # 自动创建默认定义
            self.definitions[name] = MetricDefinition(
                name=name,
                description=f"Counter metric: {name}",
                type=MetricType.COUNTER,
            )

        self.counter_values[name] += value
        self.time_series[name].append(
            TimeSeriesPoint(
                timestamp=datetime.now(),
                value=self.counter_values[name],
                tags=tags or {},
            )
        )

    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录测量值指标"""
        if name not in self.definitions:
            # 自动创建默认定义
            self.definitions[name] = MetricDefinition(
                name=name, description=f"Gauge metric: {name}", type=MetricType.GAUGE
            )

        self.time_series[name].append(
            TimeSeriesPoint(timestamp=datetime.now(), value=value, tags=tags or {})
        )

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录直方图指标"""
        if name not in self.definitions:
            # 自动创建默认定义
            self.definitions[name] = MetricDefinition(
                name=name,
                description=f"Histogram metric: {name}",
                type=MetricType.HISTOGRAM,
            )

        self.histogram_buckets[name].append(value)
        # 限制桶大小
        max_buckets = 1000
        if len(self.histogram_buckets[name]) > max_buckets:
            self.histogram_buckets[name] = self.histogram_buckets[name][-max_buckets:]

        # 同时记录时间序列
        self.time_series[name].append(
            TimeSeriesPoint(timestamp=datetime.now(), value=value, tags=tags or {})
        )

    def get_metric_data(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[TimeSeriesPoint]:
        """获取指标数据"""
        if name not in self.time_series:
            return []

        points = list(self.time_series[name])

        if start_time or end_time:
            filtered = []
            for point in points:
                if start_time and point.timestamp < start_time:
                    continue
                if end_time and point.timestamp > end_time:
                    continue
                filtered.append(point)
            return filtered

        return points

    def get_histogram_data(self, name: str) -> Dict[str, float]:
        """获取直方图统计信息"""
        if name not in self.histogram_buckets or not self.histogram_buckets[name]:
            return {}

        values = self.histogram_buckets[name]
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "p50": statistics.median(values),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
        }

    def get_aggregated_value(
        self, name: str, aggregation: str = "avg", window_minutes: int = 5
    ) -> Optional[float]:
        """获取聚合值"""
        if name not in self.time_series:
            return None

        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=window_minutes)

        points = self.get_metric_data(name, start_time, end_time)
        if not points:
            return None

        values = [point.value for point in points]

        if aggregation == "avg":
            return statistics.mean(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "count":
            return len(values)
        else:
            return statistics.mean(values)

    def cleanup_old_data(self, retention_hours: int = 24):
        """清理旧数据"""
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        for name, series in self.time_series.items():
            # 过滤掉旧数据
            while series and series[0].timestamp < cutoff_time:
                series.popleft()

        # 清理直方图数据
        for name, buckets in self.histogram_buckets.items():
            # 保持最近的数据
            keep_count = min(len(buckets), 1000)
            self.histogram_buckets[name] = buckets[-keep_count:]


class TestMetricsAnalyzer:
    """测试指标分析器"""

    def __init__(self, collector: MetricCollector):
        self.collector = collector

    def calculate_trend(self, name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """计算趋势"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=window_minutes)

        points = self.collector.get_metric_data(name, start_time, end_time)
        if len(points) < 2:
            return {"trend": "insufficient_data", "slope": 0, "direction": "stable"}

        # 准备回归分析数据
        times = [(p.timestamp - start_time).total_seconds() for p in points]
        values = [p.value for p in points]

        # 线性回归计算斜率
        n = len(points)
        sum_x = sum(times)
        sum_y = sum(values)
        sum_xy = sum(t * v for t, v in zip(times, values))
        sum_x2 = sum(t * t for t in times)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        # 判断趋势方向
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return {
            "trend": direction,
            "slope": slope,
            "start_value": values[0] if values else 0,
            "end_value": values[-1] if values else 0,
            "change_percent": ((values[-1] - values[0]) / values[0] * 100)
            if values and values[0] != 0
            else 0,
        }

    def detect_anomalies(
        self, name: str, window_minutes: int = 60, threshold_std: float = 3.0
    ) -> List[Dict[str, Any]]:
        """检测异常值"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=window_minutes)

        points = self.collector.get_metric_data(name, start_time, end_time)
        if len(points) < 10:  # 需要足够的数据点
            return []

        values = [p.value for p in points]
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0

        if std == 0:
            return []

        anomalies = []
        for point in points:
            z_score = abs((point.value - mean) / std)
            if z_score > threshold_std:
                anomalies.append(
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "z_score": z_score,
                        "deviation": point.value - mean,
                    }
                )

        return anomalies

    def calculate_performance_metrics(self, test_name: str) -> Dict[str, Any]:
        """计算性能指标"""
        # 获取执行时间数据
        execution_times = self.collector.get_metric_data(
            f"test_execution_time_{test_name}"
        )

        if not execution_times:
            return {}

        times = [p.value for p in execution_times]

        return {
            "total_executions": len(times),
            "avg_execution_time": statistics.mean(times),
            "min_execution_time": min(times),
            "max_execution_time": max(times),
            "p50_execution_time": statistics.median(times),
            "p95_execution_time": np.percentile(times, 95),
            "p99_execution_time": np.percentile(times, 99),
            "std_execution_time": statistics.stdev(times) if len(times) > 1 else 0,
            "success_rate": self._calculate_success_rate(test_name),
            "throughput": self._calculate_throughput(test_name),
        }

    def _calculate_success_rate(self, test_name: str) -> float:
        """计算成功率"""
        results = self.collector.get_metric_data(f"test_result_{test_name}")
        if not results:
            return 0.0

        success_count = sum(1 for r in results if r.value == 1.0)
        return success_count / len(results)

    def _calculate_throughput(self, test_name: str) -> float:
        """计算吞吐量（每分钟执行次数）"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)  # 最近1小时

        executions = self.collector.get_metric_data(
            f"test_result_{test_name}", start_time, end_time
        )
        total_minutes = 60.0

        return len(executions) / total_minutes

    def generate_test_report(
        self, test_names: List[str], output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成测试报告"""
        report = {"generated_at": datetime.now().isoformat(), "tests": {}}

        for test_name in test_names:
            metrics = self.calculate_performance_metrics(test_name)

            # 计算趋势
            trend = self.calculate_trend(f"test_execution_time_{test_name}")

            # 检测异常
            anomalies = self.detect_anomalies(f"test_execution_time_{test_name}")

            report["tests"][test_name] = {
                "performance_metrics": metrics,
                "execution_trend": trend,
                "anomalies": anomalies,
                "health_status": self._assess_test_health(test_name),
            }

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def _assess_test_health(self, test_name: str) -> str:
        """评估测试健康状态"""
        metrics = self.calculate_performance_metrics(test_name)

        if not metrics:
            return "unknown"

        # 基于多个指标评估健康状态
        issues = []

        # 检查执行时间趋势
        trend = self.calculate_trend(f"test_execution_time_{test_name}")
        if trend["trend"] == "increasing" and trend["change_percent"] > 20:
            issues.append("execution_time_increasing")

        # 检查成功率
        success_rate = metrics.get("success_rate", 1.0)
        if success_rate < 0.9:
            issues.append("low_success_rate")

        # 检查异常
        anomalies = self.detect_anomalies(f"test_execution_time_{test_name}")
        if len(anomalies) > 5:
            issues.append("high_anomaly_count")

        if not issues:
            return "healthy"
        elif len(issues) <= 2:
            return "warning"
        else:
            return "critical"


class TestVisualization:
    """测试可视化"""

    def __init__(self, analyzer: TestMetricsAnalyzer):
        self.analyzer = analyzer

    def create_execution_time_chart(
        self, test_name: str, output_path: Optional[str] = None
    ) -> str:
        """创建执行时间图表"""
        points = self.analyzer.collector.get_metric_data(
            f"test_execution_time_{test_name}"
        )

        if not points:
            return ""

        df = pd.DataFrame(
            [
                {"timestamp": p.timestamp, "value": p.value, "test_name": test_name}
                for p in points
            ]
        )

        fig = px.line(
            df,
            x="timestamp",
            y="value",
            title=f"{test_name} 执行时间趋势",
            labels={"value": "执行时间 (秒)", "timestamp": "时间"},
        )

        # 添加趋势线
        if len(df) > 1:
            z = np.polyfit(range(len(df)), df["value"], 1)
            p = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=p(range(len(df))),
                    mode="lines",
                    name="趋势线",
                    line=dict(dash="dash"),
                )
            )

        if output_path:
            fig.write_html(output_path)
            return output_path

        return fig.to_html()

    def create_performance_dashboard(
        self, test_names: List[str], output_path: Optional[str] = None
    ) -> str:
        """创建性能仪表板"""
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("执行时间趋势", "成功率对比", "吞吐量分析", "健康状态"),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        colors = px.colors.qualitative.Set1

        for i, test_name in enumerate(test_names[:5]):  # 最多显示5个测试
            # 执行时间趋势
            points = self.analyzer.collector.get_metric_data(
                f"test_execution_time_{test_name}"
            )
            if points:
                df = pd.DataFrame(
                    [
                        {"timestamp": p.timestamp, "value": p.value}
                        for p in points[-100:]  # 最近100个点
                    ]
                )

                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["value"],
                        name=f"{test_name}",
                        line=dict(color=colors[i % len(colors)]),
                    ),
                    row=1,
                    col=1,
                )

            # 成功率对比
            metrics = self.analyzer.calculate_performance_metrics(test_name)
            fig.add_trace(
                go.Bar(
                    x=[test_name],
                    y=[metrics.get("success_rate", 0) * 100],
                    name=test_name,
                    marker_color=colors[i % len(colors)],
                ),
                row=1,
                col=2,
            )

            # 吞吐量
            throughput = self.analyzer._calculate_throughput(test_name)
            fig.add_trace(
                go.Bar(
                    x=[test_name],
                    y=[throughput],
                    name=test_name,
                    marker_color=colors[i % len(colors)],
                ),
                row=2,
                col=1,
            )

            # 健康状态
            health_status = self.analyzer._assess_test_health(test_name)
            health_color = {
                "healthy": "green",
                "warning": "yellow",
                "critical": "red",
                "unknown": "gray",
            }[health_status]
            fig.add_trace(
                go.Scatter(
                    x=[test_name],
                    y=[1],
                    mode="markers",
                    name=f"{test_name} ({health_status})",
                    marker=dict(color=health_color, size=20, symbol="square"),
                ),
                row=2,
                col=2,
            )

        fig.update_layout(height=800, showlegend=True, title_text="测试性能仪表板")

        if output_path:
            fig.write_html(output_path)
            return output_path

        return fig.to_html()

    def create_anomaly_report(
        self, test_name: str, output_path: Optional[str] = None
    ) -> str:
        """创建异常报告"""
        anomalies = self.analyzer.detect_anomalies(f"test_execution_time_{test_name}")

        if not anomalies:
            return "<div>未检测到异常</div>"

        df = pd.DataFrame(anomalies)

        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("执行时间异常检测", "Z-score分布"),
            vertical_spacing=0.1,
        )

        # 时间序列图，标记异常点
        all_points = self.analyzer.collector.get_metric_data(
            f"test_execution_time_{test_name}"
        )
        if all_points:
            df_all = pd.DataFrame(
                [{"timestamp": p.timestamp, "value": p.value} for p in all_points]
            )

            fig.add_trace(
                go.Scatter(
                    x=df_all["timestamp"],
                    y=df_all["value"],
                    mode="lines+markers",
                    name="执行时间",
                ),
                row=1,
                col=1,
            )

            # 标记异常点
            fig.add_trace(
                go.Scatter(
                    x=pd.to_datetime(df["timestamp"]),
                    y=df["value"],
                    mode="markers",
                    name="异常点",
                    marker=dict(color="red", size=10),
                ),
                row=1,
                col=1,
            )

        # Z-score分布
        if not df.empty:
            fig.add_trace(
                go.Histogram(x=df["z_score"], name="Z-score分布", nbinsx=20),
                row=2,
                col=1,
            )

        fig.update_layout(
            height=600, showlegend=True, title_text=f"{test_name} 异常检测报告"
        )

        if output_path:
            fig.write_html(output_path)
            return output_path

        return fig.to_html()


# 使用示例
def demo_metrics_analytics():
    """演示指标分析功能"""
    print("🚀 演示测试指标分析系统")

    # 创建指标收集器
    collector = MetricCollector(max_points_per_metric=5000)

    # 注册指标
    collector.register_metric(
        MetricDefinition(
            name="test_execution_time",
            description="测试执行时间",
            type=MetricType.GAUGE,
            unit="seconds",
        )
    )

    collector.register_metric(
        MetricDefinition(
            name="test_result",
            description="测试结果",
            type=MetricType.COUNTER,
            unit="boolean",
        )
    )

    # 模拟测试执行
    for i in range(100):
        import random

        test_name = f"test_{(i % 10) + 1}"
        execution_time = random.uniform(10, 200)
        passed = random.choice([True, True, False])  # 66.7% 通过率

        collector.record_gauge(f"test_execution_time_{test_name}", execution_time)
        collector.record_counter(f"test_result_{test_name}", 1 if passed else 0)

        time.sleep(0.1)

    # 创建分析器
    analyzer = TestMetricsAnalyzer(collector)

    # 计算趋势
    trend = analyzer.calculate_trend("test_execution_time_test_1")
    print(f"\n📈 测试1的趋势分析: {trend}")

    # 检测异常
    anomalies = analyzer.detect_anomalies("test_execution_time_test_1")
    print(f"🚨 检测到 {len(anomalies)} 个异常")

    # 生成报告
    report = analyzer.generate_test_report(
        ["test_1", "test_2"], "test_metrics_report.json"
    )
    print(f"\n📄 已生成测试报告: {report['generated_at']}")

    # 创建可视化
    viz = TestVisualization(analyzer)

    # 创建执行时间图表
    chart_html = viz.create_execution_time_chart("test_1", "execution_time_chart.html")
    print("📊 已创建执行时间图表: chart_html")

    # 创建性能仪表板
    dashboard_html = viz.create_performance_dashboard(
        ["test_1", "test_2", "test_3"], "performance_dashboard.html"
    )
    print("📈 已创建性能仪表板: dashboard_html")

    # 创建异常报告
    anomaly_html = viz.create_anomaly_report("test_1", "anomaly_report.html")
    print("🚨 已创建异常报告: anomaly_html")


if __name__ == "__main__":
    demo_metrics_analytics()
