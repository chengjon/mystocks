#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI测试数据分析器
提供智能测试数据分析、模式识别和预测
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

class PatternRecognizer:
    """模式识别器"""

    def __init__(self):
        self.patterns = {
            "seasonal": {"min_strength": 0.3, "description": "季节性模式"},
            "trend": {"min_strength": 0.1, "description": "趋势模式"},
            "cyclical": {"min_strength": 0.2, "description": "周期性模式"},
            "spike": {"threshold": 2.0, "description": "尖峰模式"},
            "plateau": {"min_duration": 5, "description": "平台模式"},
            "noise": {"max_strength": 0.1, "description": "噪声模式"},
        }

    def recognize_patterns(self, data: pd.Series) -> List[Dict[str, Any]]:
        """识别数据模式"""
        patterns = []

        # 1. 检测尖峰模式
        spike_patterns = self._detect_spike_patterns(data)
        patterns.extend(spike_patterns)

        # 2. 检测平台模式
        plateau_patterns = self._detect_plateau_patterns(data)
        patterns.extend(plateau_patterns)

        # 3. 使用DBSCAN聚类检测模式
        cluster_patterns = self._detect_cluster_patterns(data)
        patterns.extend(cluster_patterns)

        # 4. 检测周期性模式
        cyclical_patterns = self._detect_cyclical_patterns(data)
        patterns.extend(cyclical_patterns)

        return patterns

    def _detect_spike_patterns(self, data: pd.Series) -> List[Dict[str, Any]]:
        """检测尖峰模式"""
        patterns = []
        mean_val = data.mean()
        std_val = data.std()

        spike_threshold = mean_val + self.patterns["spike"]["threshold"] * std_val

        spike_indices = data[data > spike_threshold].index
        if len(spike_indices) > 0:
            patterns.append(
                {
                    "pattern_type": "spike",
                    "description": "检测到尖峰模式",
                    "indices": spike_indices.tolist(),
                    "count": len(spike_indices),
                    "strength": (data.max() - mean_val) / std_val,
                }
            )

        return patterns

    def _detect_plateau_patterns(self, data: pd.Series) -> List[Dict[str, Any]]:
        """检测平台模式"""
        patterns = []
        min_duration = self.patterns["plateau"]["min_duration"]

        # 检测连续的相似值
        diff = data.diff().abs()
        plateaus = diff < 0.1 * data.std()

        # 找到连续的平台期
        plateau_groups = (plateaus != plateaus.shift()).cumsum()
        plateau_stats = plateaus.groupby(plateau_groups).agg(["count", "all"])

        for group, stats in plateau_stats.iterrows():
            if stats["count"] >= min_duration and stats["all"]:
                plateau_indices = data[plateaus].index[plateaus.groupby(plateau_groups).cumsum() == group]
                patterns.append(
                    {
                        "pattern_type": "plateau",
                        "description": "检测到平台模式",
                        "indices": plateau_indices.tolist(),
                        "duration": stats["count"],
                        "value": data.loc[plateau_indices[0]],
                    }
                )

        return patterns

    def _detect_cluster_patterns(self, data: pd.Series) -> List[Dict[str, Any]]:
        """使用聚类检测模式"""
        patterns = []

        # 准备数据
        values = data.values.reshape(-1, 1)

        # 使用DBSCAN聚类
        clustering = DBSCAN(eps=0.5, min_samples=5)
        labels = clustering.fit_predict(values)

        # 分析聚类结果
        unique_labels = set(labels)
        if len(unique_labels) > 1:  # 有多个聚类
            for label in unique_labels:
                if label != -1:  # 不是噪声点
                    cluster_indices = data.index[labels == label]
                    patterns.append(
                        {
                            "pattern_type": "cluster",
                            "description": f"聚类 {label}",
                            "indices": cluster_indices.tolist(),
                            "size": len(cluster_indices),
                            "values": data.loc[cluster_indices].mean(),
                        }
                    )

        return patterns

    def _detect_cyclical_patterns(self, data: pd.Series) -> List[Dict[str, Any]]:
        """检测周期性模式"""
        patterns = []

        # 简单的自相关分析
        if len(data) > 20:
            autocorr = data.autocorr(lag=10)
            if abs(autocorr) > 0.3:  # 有显著的自相关性
                patterns.append(
                    {
                        "pattern_type": "cyclical",
                        "description": "检测到周期性模式",
                        "autocorrelation": autocorr,
                        "strength": abs(autocorr),
                    }
                )

        return patterns


class TestDataAnalyzer:
    """增强的测试数据分析器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.anomaly_detector = AnomalyDetector(contamination=self.config.get("contamination", 0.1))
        self.trend_analyzer = TrendAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.analysis_history = []

    def analyze_test_metrics(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """分析测试指标数据"""
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "metrics_summary": {},
            "anomaly_detection": {},
            "trend_analysis": {},
            "pattern_recognition": {},
            "recommendations": [],
        }

        # 1. 指标摘要统计
        for metric_name, values in metrics_data.items():
            if values:
                series = pd.Series(values)
                analysis_result["metrics_summary"][metric_name] = {
                    "count": len(values),
                    "mean": series.mean(),
                    "std": series.std(),
                    "min": series.min(),
                    "max": series.max(),
                    "median": series.median(),
                    "skewness": series.skew(),
                    "kurtosis": series.kurtosis(),
                    "coefficient_variation": series.std() / series.mean() if series.mean() != 0 else 0,
                }

        # 2. 异常检测
        for metric_name, values in metrics_data.items():
            if len(values) > 10:  # 需要足够的数据点
                try:
                    data_array = np.array(values).reshape(-1, 1)
                    anomalies, scores = self.anomaly_detector.detect(data_array)

                    analysis_result["anomaly_detection"][metric_name] = {
                        "anomaly_count": int(np.sum(anomalies == -1)),
                        "anomaly_rate": float(np.mean(anomalies == -1)),
                        "anomaly_scores": scores.tolist(),
                        "summary": self.anomaly_detector.get_anomaly_summary(),
                    }
                except Exception as e:
                    analysis_result["anomaly_detection"][metric_name] = {"error": str(e)}

        # 3. 趋势分析（如果有时间序列数据）
        if "timestamp" in metrics_data and len(metrics_data["timestamp"]) > 10:
            try:
                # 创建时间序列
                timestamps = pd.to_datetime(metrics_data["timestamp"])
                for metric_name in [k for k in metrics_data.keys() if k != "timestamp"]:
                    if len(metrics_data[metric_name]) == len(timestamps):
                        time_series = pd.Series(metrics_data[metric_name], index=timestamps)
                        trend_result = self.trend_analyzer.analyze_trend(time_series)
                        analysis_result["trend_analysis"][metric_name] = trend_result
            except Exception as e:
                analysis_result["trend_analysis"]["error"] = str(e)

        # 4. 模式识别
        for metric_name, values in metrics_data.items():
            if len(values) > 20:
                try:
                    series = pd.Series(values)
                    patterns = self.pattern_recognizer.recognize_patterns(series)
                    analysis_result["pattern_recognition"][metric_name] = patterns
                except Exception as e:
                    analysis_result["pattern_recognition"][metric_name] = {"error": str(e)}

        # 5. 生成建议
        analysis_result["recommendations"] = self._generate_recommendations(analysis_result)

        # 记录分析历史
        self.analysis_history.append(analysis_result)

        return analysis_result

    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """基于分析结果生成建议"""
        recommendations = []

        # 检查异常率
        for metric_name, anomaly_data in analysis_result["anomaly_detection"].items():
            if isinstance(anomaly_data, dict) and "anomaly_rate" in anomaly_data:
                anomaly_rate = anomaly_data["anomaly_rate"]
                if anomaly_rate > 0.2:  # 异常率超过20%
                    recommendations.append(f"{metric_name} 异常率较高 ({anomaly_rate:.2%})，建议检查测试环境或数据源")

        # 检查趋势
        for metric_name, trend_data in analysis_result["trend_analysis"].items():
            if isinstance(trend_data, dict) and "trend_direction" in trend_data:
                direction = trend_data["trend_direction"]
                strength = trend_data.get("trend_strength", 0)
                if direction == "upward" and strength > 0.5:
                    recommendations.append(f"{metric_name} 呈上升趋势 (强度: {strength:.2f})，可能存在性能退化")
                elif direction == "downward" and strength > 0.5:
                    recommendations.append(f"{metric_name} 呈下降趋势 (强度: {strength:.2f})，性能正在改善")

        # 检查波动性
        for metric_name, summary in analysis_result["metrics_summary"].items():
            cv = summary.get("coefficient_variation", 0)
            if cv > 0.5:  # 变异系数超过50%
                recommendations.append(f"{metric_name} 波动较大 (CV: {cv:.2f})，建议增加稳定性测试")

        return recommendations

    def generate_analysis_report(self, output_format: str = "html") -> str:
        """生成分析报告"""
        if not self.analysis_history:
            return "暂无分析历史数据"

        latest_analysis = self.analysis_history[-1]

        if output_format == "html":
            return self._generate_html_report(latest_analysis)
        elif output_format == "markdown":
            return self._generate_markdown_report(latest_analysis)
        else:
            return json.dumps(latest_analysis, indent=2, ensure_ascii=False)

    def _generate_html_report(self, analysis: Dict[str, Any]) -> str:
        """生成HTML报告"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试数据分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .metric {{ background-color: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .anomaly {{ color: red; }}
                .trend-up {{ color: green; }}
                .trend-down {{ color: blue; }}
                .pattern {{ background-color: #e8f4f8; padding: 5px; margin: 5px 0; }}
                .recommendation {{ background-color: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>测试数据分析报告</h1>
            <p>生成时间: {analysis["timestamp"]}</p>

            <div class="section">
                <h2>指标摘要</h2>
                {self._format_metrics_summary(analysis["metrics_summary"])}
            </div>

            <div class="section">
                <h2>异常检测</h2>
                {self._format_anomaly_detection(analysis["anomaly_detection"])}
            </div>

            <div class="section">
                <h2>趋势分析</h2>
                {self._format_trend_analysis(analysis["trend_analysis"])}
            </div>

            <div class="section">
                <h2>模式识别</h2>
                {self._format_pattern_recognition(analysis["pattern_recognition"])}
            </div>

            <div class="section">
                <h2>建议</h2>
                {self._format_recommendations(analysis["recommendations"])}
            </div>
        </body>
        </html>
        """
        return html_template

    def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """生成Markdown报告"""
        md_template = f"""# 测试数据分析报告

生成时间: {analysis["timestamp"]}

## 指标摘要

{self._format_metrics_summary_md(analysis["metrics_summary"])}

## 异常检测

{self._format_anomaly_detection_md(analysis["anomaly_detection"])}

## 趋势分析

{self._format_trend_analysis_md(analysis["trend_analysis"])}

## 模式识别

{self._format_pattern_recognition_md(analysis["pattern_recognition"])}

## 建议

{self._format_recommendations_md(analysis["recommendations"])}
"""
        return md_template

    def _format_metrics_summary(self, summary: Dict[str, Any]) -> str:
        """格式化指标摘要（HTML）"""
        html = ""
        for metric, stats in summary.items():
            html += f"""
            <div class="metric">
                <h3>{metric}</h3>
                <p>平均值: {stats["mean"]:.2f} | 标准差: {stats["std"]:.2f} |
                   最小值: {stats["min"]:.2f} | 最大值: {stats["max"]:.2f}</p>
                <p>偏度: {stats["skewness"]:.2f} | 峰度: {stats["kurtosis"]:.2f} |
                   变异系数: {stats["coefficient_variation"]:.2f}</p>
            </div>
            """
        return html

    def _format_anomaly_detection(self, anomaly_data: Dict[str, Any]) -> str:
        """格式化异常检测结果（HTML）"""
        html = ""
        for metric, data in anomaly_data.items():
            if isinstance(data, dict) and "anomaly_rate" in data:
                anomaly_class = "anomaly" if data["anomaly_rate"] > 0.1 else ""
                html += f"""
                <div class="metric {anomaly_class}">
                    <h3>{metric}</h3>
                    <p>异常数量: {data["anomaly_count"]} | 异常率: {data["anomaly_rate"]:.2%}</p>
                </div>
                """
            elif "error" in data:
                html += f"<p>错误: {data['error']}</p>"
        return html

    def _format_trend_analysis(self, trend_data: Dict[str, Any]) -> str:
        """格式化趋势分析结果（HTML）"""
        html = ""
        for metric, data in trend_data.items():
            if isinstance(data, dict) and "trend_direction" in data:
                trend_class = f"trend-{data['trend_direction']}"
                html += f"""
                <div class="metric {trend_class}">
                    <h3>{metric}</h3>
                    <p>趋势方向: {data["trend_direction"]} | 趋势强度: {data["trend_strength"]:.2f}</p>
                    <p>季节性强度: {data["seasonality_strength"]:.2f} | 波动性: {data["volatility"]:.2f}</p>
                </div>
                """
        return html

    def _format_pattern_recognition(self, pattern_data: Dict[str, Any]) -> str:
        """格式化模式识别结果（HTML）"""
        html = ""
        for metric, patterns in pattern_data.items():
            if isinstance(patterns, list):
                html += f"<h3>{metric}</h3>"
                for pattern in patterns:
                    html += f"""
                    <div class="pattern">
                        <strong>{pattern["pattern_type"]}</strong>: {pattern["description"]}
                        <ul>
                            <li>数量: {pattern.get("count", pattern.get("size", "N/A"))}</li>
                            <li>强度: {pattern.get("strength", pattern.get("autocorrelation", "N/A")):.2f}</li>
                        </ul>
                    </div>
                    """
        return html

    def _format_recommendations(self, recommendations: List[str]) -> str:
        """格式化建议（HTML）"""
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        return html

    def _format_metrics_summary_md(self, summary: Dict[str, Any]) -> str:
        """格式化指标摘要（Markdown）"""
        md = ""
        for metric, stats in summary.items():
            md += f"""
### {metric}

- **平均值**: {stats["mean"]:.2f}
- **标准差**: {stats["std"]:.2f}
- **最小值**: {stats["min"]:.2f}
- **最大值**: {stats["max"]:.2f}
- **中位数**: {stats["median"]:.2f}
- **偏度**: {stats["skewness"]:.2f}
- **峰度**: {stats["kurtosis"]:.2f}
- **变异系数**: {stats["coefficient_variation"]:.2f}

"""
        return md

    def _format_anomaly_detection_md(self, anomaly_data: Dict[str, Any]) -> str:
        """格式化异常检测结果（Markdown）"""
        md = ""
        for metric, data in anomaly_data.items():
            if isinstance(data, dict) and "anomaly_rate" in data:
                md += f"""
#### {metric}

- **异常数量**: {data["anomaly_count"]}
- **异常率**: {data["anomaly_rate"]:.2%}

"""
            elif "error" in data:
                md += f"#### {metric}\n\n错误: {data['error']}\n\n"
        return md

    def _format_trend_analysis_md(self, trend_data: Dict[str, Any]) -> str:
        """格式化趋势分析结果（Markdown）"""
        md = ""
        for metric, data in trend_data.items():
            if isinstance(data, dict) and "trend_direction" in data:
                md += f"""
#### {metric}

- **趋势方向**: {data["trend_direction"]}
- **趋势强度**: {data["trend_strength"]:.2f}
- **季节性强度**: {data["seasonality_strength"]:.2f}
- **波动性**: {data["volatility"]:.2f}

"""
        return md

    def _format_pattern_recognition_md(self, pattern_data: Dict[str, Any]) -> str:
        """格式化模式识别结果（Markdown）"""
        md = ""
        for metric, patterns in pattern_data.items():
            if isinstance(patterns, list):
                md += f"#### {metric}\n\n"
                for pattern in patterns:
                    md += f"""
- **{pattern["pattern_type"]}**: {pattern["description"]}
  - 数量: {pattern.get("count", pattern.get("size", "N/A"))}
  - 强度: {pattern.get("strength", pattern.get("autocorrelation", "N/A")):.2f}

"""
        return md

    def _format_recommendations_md(self, recommendations: List[str]) -> str:
        """格式化建议（Markdown）"""
        md = ""
        for rec in recommendations:
            md += f"- {rec}\n"
        return md


async def demo_enhanced_data_analyzer():
    """演示增强的数据分析器功能"""
    print("🚀 演示增强的数据分析器功能")

    # 创建分析器
    analyzer = TestDataAnalyzer({"contamination": 0.05})  # 5%的异常率

    # 模拟测试指标数据
    test_metrics = {
        "response_time": [45, 42, 48, 43, 47, 150, 44, 46, 45, 43, 49, 151, 47, 45, 44],
        "throughput": [
            1200,
            1180,
            1220,
            1190,
            1210,
            800,
            1170,
            1230,
            1190,
            1210,
            1180,
            750,
            1200,
            1190,
            1220,
        ],
        "error_rate": [
            0.01,
            0.02,
            0.01,
            0.03,
            0.01,
            0.15,
            0.02,
            0.01,
            0.01,
            0.02,
            0.01,
            0.20,
            0.01,
            0.02,
            0.01,
        ],
        "timestamp": [
            "2024-01-01 09:00:00",
            "2024-01-01 09:01:00",
            "2024-01-01 09:02:00",
            "2024-01-01 09:03:00",
            "2024-01-01 09:04:00",
            "2024-01-01 09:05:00",
            "2024-01-01 09:06:00",
            "2024-01-01 09:07:00",
            "2024-01-01 09:08:00",
            "2024-01-01 09:09:00",
            "2024-01-01 09:10:00",
            "2024-01-01 09:11:00",
            "2024-01-01 09:12:00",
            "2024-01-01 09:13:00",
            "2024-01-01 09:14:00",
        ],
    }

    # 执行分析
    analysis_result = analyzer.analyze_test_metrics(test_metrics)

    # 输出结果
    print("\n📊 分析结果摘要:")
    print(f"分析时间: {analysis_result['timestamp']}")
    print(f"建议数量: {len(analysis_result['recommendations'])}")

    print("\n🔍 异常检测结果:")
    for metric, data in analysis_result["anomaly_detection"].items():
        if isinstance(data, dict) and "anomaly_rate" in data:
            print(f"  {metric}: {data['anomaly_count']} 个异常 ({data['anomaly_rate']:.2%})")

    print("\n📈 趋势分析结果:")
    for metric, data in analysis_result["trend_analysis"].items():
        if isinstance(data, dict) and "trend_direction" in data:
            print(f"  {metric}: {data['trend_direction']} (强度: {data['trend_strength']:.2f})")

    print("\n🔮 识别到的模式:")
    for metric, patterns in analysis_result["pattern_recognition"].items():
        if isinstance(patterns, list):
            print(f"  {metric}: {len(patterns)} 个模式")
            for pattern in patterns[:2]:  # 显示前2个模式
                print(f"    - {pattern['pattern_type']}: {pattern['description']}")

    print("\n💡 建议:")
    for i, rec in enumerate(analysis_result["recommendations"], 1):
        print(f"  {i}. {rec}")

    # 生成HTML报告
    html_report = analyzer.generate_analysis_report("html")
    with open("analysis_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("\n✅ HTML报告已生成: analysis_report.html")

    # 生成Markdown报告
    md_report = analyzer.generate_analysis_report("markdown")
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(md_report)
    print("✅ Markdown报告已生成: analysis_report.md")


def test_anomaly_detection():
    """测试异常检测"""
    analyzer = AITestDataAnalyzer()

    # 模拟测试结果
    test_results = [
        {
            "function_name": "get_stock_price",
            "status": "passed",
            "duration": 100,
            "timestamp": "2024-12-12T10:00:00",
            "memory_usage": 50.5,
        },
        {
            "function_name": "get_stock_price",
            "status": "passed",
            "duration": 105,
            "timestamp": "2024-12-12T10:01:00",
            "memory_usage": 51.2,
        },
        {
            "function_name": "get_stock_price",
            "status": "failed",
            "duration": 5000,  # 异常慢
            "timestamp": "2024-12-12T10:02:00",
            "memory_usage": 200.0,  # 异常高内存
        },
    ]

    # 检测异常
    anomalies = analyzer.detect_test_anomalies(test_results)

    print(f"检测到 {len(anomalies)} 个异常:")
    for anomaly in anomalies:
        print(f"  - {anomaly.description} (置信度: {anomaly.confidence_score:.2f})")


def test_pattern_analysis():
    """测试模式分析"""
    analyzer = AITestDataAnalyzer()

    # 模拟测试结果
    test_results = []
    for i in range(50):
        test_results.append(
            {
                "function_name": "get_stock_price",
                "status": "passed" if i % 10 != 0 else "failed",
                "duration": 100 + i % 20,
                "timestamp": f"2024-12-12T10:{i:02d}:00",
            }
        )

    # 分析模式
    patterns = analyzer.analyze_test_patterns(test_results)

    print(f"识别到 {len(patterns)} 个模式:")
    for pattern in patterns[:5]:
        print(f"  - {pattern.pattern_name}: 频率={pattern.frequency}, 成功率={pattern.success_rate:.2%}")


def test_trend_prediction():
    """测试趋势预测"""
    analyzer = AITestDataAnalyzer()

    # 模拟测试结果（模拟性能下降趋势）
    test_results = []
    base_duration = 100
    for i in range(30):
        # 模拟性能逐渐下降
        duration = base_duration + (i * 5)
        test_results.append(
            {
                "function_name": "calculate_indicators",
                "status": "passed",
                "duration": duration,
                "timestamp": f"2024-12-12T{i:02d}:00:00",
            }
        )

    # 预测趋势
    trends = analyzer.predict_test_trends(test_results)

    print("预测的趋势:")
    for trend in trends:
        print(f"  - {trend.trend_name}: {trend.direction} (变化率: {trend.change_rate:.2%})")


