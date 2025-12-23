#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试趋势分析模块

提供测试数据的时间序列分析、趋势预测和模式识别功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TrendDirection(Enum):
    """趋势方向"""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class SeasonalityType(Enum):
    """季节性类型"""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendConfidence(Enum):
    """趋势置信度"""

    VERY_LOW = 0.0
    LOW = 0.33
    MEDIUM = 0.66
    HIGH = 1.0


@dataclass
class TimeSeriesPoint:
    """时间序列数据点"""

    timestamp: datetime
    value: float
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysisResult:
    """趋势分析结果"""

    metric_name: str
    direction: TrendDirection
    confidence: TrendConfidence
    slope: float
    r_squared: float
    p_value: float
    prediction: Optional[float] = None
    forecast: Optional[List[float]] = None
    seasonality: SeasonalityType = SeasonalityType.NONE
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)


@dataclass
class ForecastingConfig:
    """预测配置"""

    forecast_periods: int = 24
    confidence_interval: float = 0.95
    include_seasonality: bool = True
    use_machine_learning: bool = True
    smoothing_factor: float = 0.3


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self, config: Optional[ForecastingConfig] = None):
        self.config = config or ForecastingConfig()
        self.historical_data: Dict[str, List[TimeSeriesPoint]] = {}
        self.analysis_cache: Dict[str, TrendAnalysisResult] = {}
        self.patterns_cache: Dict[str, List[Dict[str, Any]]] = {}

    def add_historical_data(self, metric_name: str, data: List[TimeSeriesPoint]):
        """添加历史数据"""
        self.historical_data[metric_name] = sorted(data, key=lambda x: x.timestamp)
        self.analysis_cache.pop(metric_name, None)  # 清除缓存
        self.patterns_cache.pop(metric_name, None)  # 清除缓存

    def analyze_trend(self, metric_name: str) -> TrendAnalysisResult:
        """分析趋势"""
        if metric_name in self.analysis_cache:
            return self.analysis_cache[metric_name]

        if metric_name not in self.historical_data:
            raise ValueError(f"No historical data for metric: {metric_name}")

        data = self.historical_data[metric_name]
        values = [point.value for point in data]
        timestamps = [point.timestamp for point in data]

        # 准备回归分析数据
        x_values = np.array(
            [(t - timestamps[0]).total_seconds() / 3600 for t in timestamps]
        ).reshape(-1, 1)
        y_values = np.array(values)

        # 线性回归分析
        model = LinearRegression()
        model.fit(x_values, y_values)

        # 预测值
        y_pred = model.predict(x_values)

        # 计算统计指标
        slope = model.coef_[0]
        r_squared = model.score(x_values, y_values)
        p_value = self._calculate_p_value(x_values.flatten(), y_values, y_pred)

        # 确定趋势方向
        direction = self._determine_direction(slope, r_squared, p_value)
        confidence = self._determine_confidence(r_squared, p_value)

        # 检测季节性
        seasonality = self._detect_seasonality(data, timestamps, values)

        # 检测异常值
        anomalies = self._detect_anomalies(values, timestamps)

        # 识别模式
        patterns = self._identify_patterns(data, values)

        # 生成洞察
        insights = self._generate_insights(
            metric_name,
            direction,
            confidence,
            slope,
            r_squared,
            anomalies,
            patterns,
            seasonality,
        )

        # 生成预测
        prediction = None
        forecast = None
        if len(data) >= 10:  # 至少需要10个数据点进行预测
            last_timestamp = timestamps[-1]
            prediction = self._predict_next_value(
                model, last_timestamp, x_values[-1][0]
            )
            forecast = self._generate_forecast(model, last_timestamp, x_values[-1][0])

        # 创建分析结果
        result = TrendAnalysisResult(
            metric_name=metric_name,
            direction=direction,
            confidence=confidence,
            slope=slope,
            r_squared=r_squared,
            p_value=p_value,
            prediction=prediction,
            forecast=forecast,
            seasonality=seasonality,
            anomalies=anomalies,
            patterns=patterns,
            insights=insights,
        )

        # 缓存结果
        self.analysis_cache[metric_name] = result

        return result

    def _calculate_p_value(
        self, x: np.ndarray, y: np.ndarray, y_pred: np.ndarray
    ) -> float:
        """计算p值"""
        n = len(x)
        if n <= 2:
            return 1.0

        # 计算残差平方和
        residuals = y - y_pred
        rss = np.sum(residuals**2)

        # 计算总平方和
        y_mean = np.mean(y)
        tss = np.sum((y - y_mean) ** 2)

        # 计算F统计量
        if tss == 0:
            return 0.0

        f_statistic = (tss - rss) / 1 / (rss / (n - 2))

        # 计算p值
        p_value = 1 - stats.f.cdf(f_statistic, 1, n - 2)
        return p_value

    def _determine_direction(
        self, slope: float, r_squared: float, p_value: float
    ) -> TrendDirection:
        """确定趋势方向"""
        if p_value > 0.05:  # 不显著
            return TrendDirection.STABLE

        if abs(slope) < 0.01:  # 变化非常小
            return TrendDirection.STABLE

        if r_squared < 0.1:  # 拟合度很低
            return TrendDirection.VOLATILE

        if slope > 0:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.DECREASING

    def _determine_confidence(
        self, r_squared: float, p_value: float
    ) -> TrendConfidence:
        """确定趋势置信度"""
        if p_value > 0.05 or r_squared < 0.3:
            return TrendConfidence.VERY_LOW
        elif p_value > 0.01 or r_squared < 0.6:
            return TrendConfidence.LOW
        elif p_value > 0.001 or r_squared < 0.8:
            return TrendConfidence.MEDIUM
        else:
            return TrendConfidence.HIGH

    def _detect_seasonality(
        self,
        data: List[TimeSeriesPoint],
        timestamps: List[datetime],
        values: List[float],
    ) -> SeasonalityType:
        """检测季节性"""
        if len(data) < 24:  # 数据太少，无法检测季节性
            return SeasonalityType.NONE

        # 转换为pandas DataFrame
        df = pd.DataFrame(
            {
                "timestamp": timestamps,
                "value": values,
                "hour": [t.hour for t in timestamps],
                "day_of_week": [t.weekday() for t in timestamps],
                "day_of_month": [t.day for t in timestamps],
                "month": [t.month for t in timestamps],
            }
        )

        # 检测不同的季节性模式
        patterns = {
            SeasonalityType.DAILY: self._test_seasonality(df, "hour"),
            SeasonalityType.WEEKLY: self._test_seasonality(df, "day_of_week"),
            SeasonalityType.MONTHLY: self._test_seasonality(df, "month"),
        }

        # 选择最强的季节性模式
        strongest_season = max(patterns.keys(), key=lambda k: patterns[k])

        if patterns[strongest_season] > 0.3:  # 阈值
            return strongest_season

        return SeasonalityType.NONE

    def _test_seasonality(self, df: pd.DataFrame, column: str) -> float:
        """测试特定列的季节性"""
        from scipy.stats import f_oneway

        # 按季节分组
        groups = [df[df[column] == val]["value"] for val in df[column].unique()]

        # 如果只有一个组，无法进行ANOVA
        if len(groups) < 2:
            return 0.0

        # ANOVA检验
        try:
            f_stat, p_value = f_oneway(*groups)
            return 1.0 - p_value  # 返回显著性程度
        except:
            return 0.0

    def _detect_anomalies(
        self, values: List[float], timestamps: List[datetime]
    ) -> List[Dict[str, Any]]:
        """检测异常值"""
        if len(values) < 10:
            return []

        # 使用IQR方法检测异常值
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        anomalies = []
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            if value < lower_bound or value > upper_bound:
                anomaly_type = "low" if value < lower_bound else "high"
                anomalies.append(
                    {
                        "index": i,
                        "timestamp": timestamp.isoformat(),
                        "value": value,
                        "type": anomaly_type,
                        "severity": "high"
                        if abs(value - (q1 + q3) / 2) > 2 * iqr
                        else "medium",
                    }
                )

        return anomalies

    def _identify_patterns(
        self, data: List[TimeSeriesPoint], values: List[float]
    ) -> List[Dict[str, Any]]:
        """识别数据模式"""
        patterns = []

        # 检测连续上升/下降模式
        patterns.extend(self._detect_trend_patterns(values))

        # 检测周期性模式
        if len(values) >= 20:
            patterns.extend(self._detect_cyclic_patterns(values))

        # 检测突变模式
        patterns.extend(self._detect_change_points(values))

        return patterns

    def _detect_trend_patterns(self, values: List[float]) -> List[Dict[str, Any]]:
        """检测趋势模式"""
        patterns = []

        # 滑动窗口检测
        window_size = min(5, len(values) // 4)

        for i in range(len(values) - window_size + 1):
            window = values[i : i + window_size]

            # 计算窗口内的趋势
            if len(window) >= 2:
                trend = np.polyfit(range(len(window)), window, 1)[0]

                if abs(trend) > 1.0:  # 阈值
                    direction = "increasing" if trend > 0 else "decreasing"
                    patterns.append(
                        {
                            "type": f"{direction}_trend",
                            "start_index": i,
                            "end_index": i + window_size - 1,
                            "strength": abs(trend),
                            "direction": direction,
                        }
                    )

        return patterns

    def _detect_cyclic_patterns(self, values: List[float]) -> List[Dict[str, Any]]:
        """检测周期性模式"""
        patterns = []

        # 使用FFT检测周期性
        fft_values = np.fft.fft(values)
        frequencies = np.fft.fftfreq(len(values))

        # 找到主要频率
        power_spectrum = np.abs(fft_values) ** 2
        peak_indices = np.argsort(power_spectrum)[-3:]  # 前3个峰值

        for idx in peak_indices:
            if frequencies[idx] > 0:  # 忽略0频率
                period = 1.0 / frequencies[idx]
                if period < len(values) / 2:  # 合理的周期
                    patterns.append(
                        {
                            "type": "cyclic",
                            "period": period,
                            "frequency": frequencies[idx],
                            "power": power_spectrum[idx],
                            "confidence": min(
                                power_spectrum[idx] / np.max(power_spectrum), 1.0
                            ),
                        }
                    )

        return patterns

    def _detect_change_points(self, values: List[float]) -> List[Dict[str, Any]]:
        """检测突变点"""
        change_points = []

        # 使用CUSUM方法检测突变
        if len(values) < 10:
            return change_points

        # 计算均值和标准差
        baseline_mean = np.mean(values[: len(values) // 2])
        baseline_std = np.std(values[: len(values) // 2])

        cusum = 0
        threshold = 5 * baseline_std  # CUSUM阈值

        for i in range(len(values) // 2, len(values)):
            cusum += values[i] - baseline_mean
            if abs(cusum) > threshold:
                change_points.append(
                    {
                        "type": "change_point",
                        "index": i,
                        "timestamp": None,  # 需要外部传入
                        "magnitude": abs(cusum) / threshold,
                        "direction": "increase" if cusum > 0 else "decrease",
                    }
                )
                # 重置CUSUM
                cusum = 0

        return change_points

    def _generate_insights(
        self,
        metric_name: str,
        direction: TrendDirection,
        confidence: TrendConfidence,
        slope: float,
        r_squared: float,
        anomalies: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        seasonality: SeasonalityType,
    ) -> List[str]:
        """生成洞察"""
        insights = []

        # 基本趋势洞察
        if confidence == TrendConfidence.HIGH:
            if direction == TrendDirection.INCREASING:
                insights.append(f"{metric_name}呈显著上升趋势，斜率: {slope:.4f}")
            elif direction == TrendDirection.DECREASING:
                insights.append(f"{metric_name}呈显著下降趋势，斜率: {slope:.4f}")
            else:
                insights.append(f"{metric_name}保持稳定")

        # 异常洞察
        if anomalies:
            high_anomalies = [a for a in anomalies if a["severity"] == "high"]
            if high_anomalies:
                insights.append(f"检测到{len(high_anomalies)}个高风险异常值")

        # 模式洞察
        cyclic_patterns = [p for p in patterns if p["type"] == "cyclic"]
        if cyclic_patterns:
            main_pattern = max(cyclic_patterns, key=lambda p: p["confidence"])
            insights.append(
                f"发现周期性模式，周期: {main_pattern['period']:.1f}个数据点"
            )

        # 季节性洞察
        if seasonality != SeasonalityType.NONE:
            insights.append(f"存在{seasonality.value}季节性模式")

        return insights

    def _predict_next_value(
        self, model, last_timestamp: datetime, last_x: float
    ) -> float:
        """预测下一个值"""
        # 预测下一个时间点
        next_x = last_x + 1  # 1小时后
        prediction = model.predict([[next_x]])[0]
        return float(prediction)

    def _generate_forecast(
        self, model, last_timestamp: datetime, last_x: float
    ) -> List[float]:
        """生成未来预测"""
        forecast = []

        for i in range(1, self.config.forecast_periods + 1):
            next_x = last_x + i
            predicted_value = model.predict([[next_x]])[0]
            forecast.append(float(predicted_value))

        return forecast

    def create_visualization(self, metric_name: str) -> Dict[str, Any]:
        """创建趋势可视化图表"""
        if metric_name not in self.historical_data:
            raise ValueError(f"No historical data for metric: {metric_name}")

        data = self.historical_data[metric_name]
        result = self.analyze_trend(metric_name)

        # 创建子图
        fig = make_subplots(
            rows=3,
            cols=1,
            subplot_titles=("原始数据趋势", "季节性分析", "预测和置信区间"),
            vertical_spacing=0.1,
        )

        # 原始数据趋势
        timestamps = [point.timestamp for point in data]
        values = [point.value for point in data]

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=values,
                mode="lines+markers",
                name="原始数据",
                line=dict(color="blue"),
            ),
            row=1,
            col=1,
        )

        # 添加趋势线
        if len(data) >= 2:
            x_numeric = [(t - timestamps[0]).total_seconds() / 3600 for t in timestamps]
            trend_line = result.slope * np.array(x_numeric) + np.mean(values)
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=trend_line,
                    mode="lines",
                    name="趋势线",
                    line=dict(color="red", dash="dash"),
                ),
                row=1,
                col=1,
            )

        # 季节性分析
        if result.seasonality != SeasonalityType.NONE:
            # 按季节性分组展示
            if result.seasonality == SeasonalityType.DAILY:
                df = pd.DataFrame(
                    {
                        "timestamp": timestamps,
                        "value": values,
                        "hour": [t.hour for t in timestamps],
                    }
                )
                seasonal_avg = df.groupby("hour")["value"].mean()
                fig.add_trace(
                    go.Scatter(
                        x=seasonal_avg.index,
                        y=seasonal_avg.values,
                        mode="lines+markers",
                        name="小时均值",
                        line=dict(color="green"),
                    ),
                    row=2,
                    col=1,
                )

        # 预测图
        if result.forecast:
            forecast_timestamps = []
            last_time = timestamps[-1]
            for i in range(len(result.forecast)):
                forecast_timestamps.append(last_time + timedelta(hours=i + 1))

            # 预测线
            fig.add_trace(
                go.Scatter(
                    x=forecast_timestamps,
                    y=result.forecast,
                    mode="lines+markers",
                    name="预测值",
                    line=dict(color="orange"),
                ),
                row=3,
                col=1,
            )

            # 置信区间（简化版）
            if result.confidence == TrendConfidence.HIGH:
                std_dev = np.std(values[-10:]) if len(values) >= 10 else np.std(values)
                upper_bound = [f + std_dev for f in result.forecast]
                lower_bound = [f - std_dev for f in result.forecast]

                fig.add_trace(
                    go.Scatter(
                        x=forecast_timestamps,
                        y=upper_bound,
                        mode="lines",
                        name="置信区间上限",
                        line=dict(color="rgba(255,165,0,0.3)", showlegend=False),
                    ),
                    row=3,
                    col=1,
                )

                fig.add_trace(
                    go.Scatter(
                        x=forecast_timestamps,
                        y=lower_bound,
                        mode="lines",
                        name="置信区间下限",
                        line=dict(
                            color="rgba(255,165,0,0.3)",
                            fill="tonexty",
                            showlegend=False,
                        ),
                    ),
                    row=3,
                    col=1,
                )

        # 异常值标记
        for anomaly in result.anomalies:
            anomaly_time = datetime.fromisoformat(anomaly["timestamp"])
            fig.add_trace(
                go.Scatter(
                    x=[anomaly_time],
                    y=[anomaly["value"]],
                    mode="markers",
                    name="异常值",
                    marker=dict(color="red", size=10),
                ),
                row=1,
                col=1,
            )

        # 更新布局
        fig.update_layout(title=f"{metric_name} 趋势分析", height=800, showlegend=True)

        return fig.to_dict()

    def get_trend_summary(self, metrics: List[str]) -> Dict[str, Any]:
        """获取多个指标的总体趋势摘要"""
        summary = {"metrics_count": len(metrics), "trends": {}, "overall_insights": []}

        trend_directions = []
        confidences = []

        for metric in metrics:
            try:
                result = self.analyze_trend(metric)
                summary["trends"][metric] = {
                    "direction": result.direction.value,
                    "confidence": result.confidence.value,
                    "slope": result.slope,
                    "r_squared": result.r_squared,
                    "anomalies_count": len(result.anomalies),
                    "patterns_count": len(result.patterns),
                }

                trend_directions.append(result.direction)
                confidences.append(result.confidence)

            except Exception as e:
                summary["trends"][metric] = {"error": str(e)}

        # 总体趋势分析
        from collections import Counter

        direction_counter = Counter(trend_directions)
        main_direction = direction_counter.most_common(1)[0][0]

        if main_direction == TrendDirection.INCREASING:
            summary["overall_insights"].append("多数指标呈上升趋势")
        elif main_direction == TrendDirection.DECREASING:
            summary["overall_insights"].append("多数指标呈下降趋势")
        else:
            summary["overall_insights"].append("多数指标保持稳定")

        # 高置信度指标比例
        high_confidence_count = sum(1 for c in confidences if c.value >= 0.66)
        confidence_ratio = (
            high_confidence_count / len(confidences) if confidences else 0
        )
        summary["confidence_ratio"] = confidence_ratio

        if confidence_ratio > 0.7:
            summary["overall_insights"].append("大部分趋势分析结果置信度较高")

        return summary


# 使用示例
def demo_trend_analysis():
    """演示趋势分析功能"""
    print("📈 演示趋势分析功能")

    # 创建趋势分析器
    analyzer = TrendAnalyzer()

    # 生成模拟数据 - 测试成功率
    success_rates = []
    timestamps = []
    base_rate = 95.0

    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=100 - i)
        # 添加一些趋势和噪声
        trend = -0.05 * i  # 轻微下降趋势
        noise = np.random.normal(0, 2)
        rate = base_rate + trend + noise
        rate = max(80, min(100, rate))  # 限制在80-100之间

        success_rates.append(rate)
        timestamps.append(timestamp)

    # 创建时间序列数据
    test_success_data = [
        TimeSeriesPoint(timestamp=t, value=v, category="test_success")
        for t, v in zip(timestamps, success_rates)
    ]

    # 添加数据到分析器
    analyzer.add_historical_data("test_success_rate", test_success_data)

    # 添加API响应时间数据（上升趋势）
    response_times = []
    for i in range(80):
        timestamp = datetime.now() - timedelta(hours=100 - i)
        # 上升趋势
        trend = 2.0 * i
        noise = np.random.normal(0, 10)
        response_time = 100 + trend + noise
        response_time = max(50, response_time)  # 最小50ms

        response_times.append(response_time)
        timestamps.append(timestamp)

    api_response_data = [
        TimeSeriesPoint(timestamp=t, value=v, category="api_response")
        for t, v in zip(timestamps[:80], response_times)
    ]
    analyzer.add_historical_data("api_response_time", api_response_data)

    # 分析趋势
    print("\n📊 测试成功率趋势分析:")
    success_result = analyzer.analyze_trend("test_success_rate")
    print(f"  趋势方向: {success_result.direction.value}")
    print(f"  置信度: {success_result.confidence.value}")
    print(f"  斜率: {success_result.slope:.4f}")
    print(f"  R²: {success_result.r_squared:.4f}")
    print(f"  p值: {success_result.p_value:.4f}")
    print(f"  预测下一值: {success_result.prediction:.2f}")
    print(f"  异常值数量: {len(success_result.anomalies)}")
    print(f"  模式数量: {len(success_result.patterns)}")
    print("  洞察:")
    for insight in success_result.insights:
        print(f"    - {insight}")

    print("\n⚡ API响应时间趋势分析:")
    api_result = analyzer.analyze_trend("api_response_time")
    print(f"  趋势方向: {api_result.direction.value}")
    print(f"  置信度: {api_result.confidence.value}")
    print(f"  斜率: {api_result.slope:.4f}")
    print(f"  R²: {api_result.r_squared:.4f}")
    print(f"  p值: {api_result.p_value:.4f}")
    print(f"  预测下一值: {api_result.prediction:.2f}")
    print("  洞察:")
    for insight in api_result.insights:
        print(f"    - {insight}")

    # 创建可视化
    print("\n🎨 创建可视化图表:")
    try:
        success_chart = analyzer.create_visualization("test_success_rate")
        print(
            f"  ✅ 测试成功率图表已生成 (包含 {len(success_chart.get('data', []))} 个数据系列)"
        )

        api_chart = analyzer.create_visualization("api_response_time")
        print(
            f"  ✅ API响应时间图表已生成 (包含 {len(api_chart.get('data', []))} 个数据系列)"
        )
    except Exception as e:
        print(f"  ❌ 图表生成失败: {e}")

    # 获取总体摘要
    print("\n📋 总体趋势摘要:")
    summary = analyzer.get_trend_summary(["test_success_rate", "api_response_time"])
    print(f"  指标数量: {summary['metrics_count']}")
    print(f"  高置信度指标比例: {summary['confidence_ratio']:.2f}")
    print("  总体洞察:")
    for insight in summary["overall_insights"]:
        print(f"    - {insight}")

    return analyzer


if __name__ == "__main__":
    analyzer = demo_trend_analysis()
    print("\n✅ 趋势分析演示完成")
