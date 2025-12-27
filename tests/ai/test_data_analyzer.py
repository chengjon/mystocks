#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI测试数据分析器
提供智能测试数据分析、模式识别和预测
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import logging


@dataclass
class TestPattern:
    """测试模式"""

    pattern_name: str
    frequency: int
    success_rate: float
    avg_duration: float
    confidence: float
    related_functions: List[str]


@dataclass
class TestTrend:
    """测试趋势"""

    trend_name: str
    direction: str  # increasing, decreasing, stable
    change_rate: float
    impact_level: str  # high, medium, low
    predicted_value: float
    time_frame: str


@dataclass
class AnomalyDetection:
    """异常检测结果"""

    anomaly_id: str
    severity: str
    type: str
    description: str
    affected_tests: List[str]
    confidence_score: float
    recommended_action: str


class AITestDataAnalyzer:
    """AI测试数据分析器"""

    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(__file__).parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)

    def analyze_test_patterns(self, test_results: List[Dict[str, Any]]) -> List[TestPattern]:
        """分析测试模式"""
        print("🤖 AI正在分析测试模式...")

        patterns = []
        function_results = defaultdict(list)

        # 按函数分组结果
        for result in test_results:
            func_name = result.get("function_name", "unknown")
            function_results[func_name].append(result)

        # 分析每个函数的测试模式
        for func_name, results in function_results.items():
            if len(results) >= 3:  # 至少3次结果才能形成模式
                pattern = self._extract_function_pattern(func_name, results)
                if pattern:
                    patterns.append(pattern)

        # 按频率排序
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns

    def _extract_function_pattern(self, func_name: str, results: List[Dict[str, Any]]) -> Optional[TestPattern]:
        """提取函数测试模式"""
        try:
            # 计算成功率
            success_count = sum(1 for r in results if r.get("status") == "passed")
            success_rate = success_count / len(results)

            # 计算平均执行时间
            durations = [r.get("duration", 0) for r in results if r.get("duration")]
            avg_duration = np.mean(durations) if durations else 0

            # 识别模式类型
            pattern_type = self._classify_pattern_type(func_name, results)

            # 计算置信度
            confidence = min(len(results) / 10, 1.0)  # 基于样本量

            return TestPattern(
                pattern_name=pattern_type,
                frequency=len(results),
                success_rate=success_rate,
                avg_duration=avg_duration,
                confidence=confidence,
                related_functions=[func_name],
            )

        except Exception as e:
            self.logger.error(f"模式提取失败 {func_name}: {e}")
            return None

    def _classify_pattern_type(self, func_name: str, results: List[Dict[str, Any]]) -> str:
        """分类模式类型"""
        func_lower = func_name.lower()

        # 基于函数名称分类
        if any(keyword in func_lower for keyword in ["get", "fetch", "retrieve"]):
            return "data_retrieval"
        elif any(keyword in func_lower for keyword in ["calculate", "compute", "analyze"]):
            return "calculation"
        elif any(keyword in func_lower for keyword in ["validate", "check", "verify"]):
            return "validation"
        elif any(keyword in func_lower for keyword in ["save", "store", "update"]):
            return "data_modification"
        else:
            return "general"

    def detect_test_anomalies(self, test_results: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """检测测试异常"""
        print("🤖 AI正在检测测试异常...")

        anomalies = []

        # 1. 检测执行时间异常
        time_anomalies = self._detect_time_anomalies(test_results)
        anomalies.extend(time_anomalies)

        # 2. 检测失败率异常
        failure_anomalies = self._detect_failure_anomalies(test_results)
        anomalies.extend(failure_anomalies)

        # 3. 检测模式变化异常
        pattern_anomalies = self._detect_pattern_anomalies(test_results)
        anomalies.extend(pattern_anomalies)

        # 4. 检测资源使用异常
        resource_anomalies = self._detect_resource_anomalies(test_results)
        anomalies.extend(resource_anomalies)

        return sorted(anomalies, key=lambda a: a.confidence_score, reverse=True)

    def _detect_time_anomalies(self, test_results: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """检测时间异常"""
        anomalies = []
        time_data = defaultdict(list)

        for result in test_results:
            func_name = result.get("function_name", "unknown")
            duration = result.get("duration", 0)
            time_data[func_name].append(duration)

        for func_name, durations in time_data.items():
            if len(durations) >= 5:  # 至少5次数据
                mean_time = np.mean(durations)
                std_time = np.std(durations)

                # 检测最近几次是否有异常
                recent_durations = durations[-5:]
                for duration in recent_durations:
                    if duration > mean_time + 2 * std_time:  # 超出2个标准差
                        anomaly = AnomalyDetection(
                            anomaly_id=f"time_anomaly_{func_name}_{datetime.now().timestamp()}",
                            severity="high" if duration > mean_time * 3 else "medium",
                            type="execution_time_spike",
                            description=f"函数 {func_name} 执行时间异常: {duration:.2f}ms (平均: {mean_time:.2f}ms)",
                            affected_tests=[func_name],
                            confidence_score=min((duration - mean_time) / (std_time + 1), 1.0),
                            recommended_action="检查函数是否有性能瓶颈或资源竞争",
                        )
                        anomalies.append(anomaly)

        return anomalies

    def _detect_failure_anomalies(self, test_results: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """检测失败率异常"""
        anomalies = []
        failure_data = defaultdict(list)

        for result in test_results:
            func_name = result.get("function_name", "unknown")
            status = result.get("status", "unknown")
            failure_data[func_name].append(status)

        for func_name, statuses in failure_data.items():
            if len(statuses) >= 10:  # 至少10次数据
                recent_failures = statuses[-5:]
                failure_rate = sum(1 for s in recent_failures if s != "passed") / len(recent_failures)

                # 如果最近5次失败率超过50%
                if failure_rate > 0.5:
                    anomaly = AnomalyDetection(
                        anomaly_id=f"failure_anomaly_{func_name}_{datetime.now().timestamp()}",
                        severity="high",
                        type="high_failure_rate",
                        description=f"函数 {func_name} 最近失败率过高: {failure_rate:.1%}",
                        affected_tests=[func_name],
                        confidence_score=failure_rate,
                        recommended_action="立即检查函数实现和依赖项",
                    )
                    anomalies.append(anomaly)

        return anomalies

    def _detect_pattern_anomalies(self, test_results: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """检测模式变化异常"""
        anomalies = []

        # 按时间排序
        sorted_results = sorted(test_results, key=lambda x: x.get("timestamp", ""))

        # 滑动窗口分析
        window_size = 10
        for i in range(len(sorted_results) - window_size + 1):
            window = sorted_results[i : i + window_size]

            # 分析窗口内的模式
            pattern_score = self._calculate_window_pattern_score(window)

            # 与之前的窗口对比
            if i > 0:
                prev_window = sorted_results[i - 1 : i + window_size - 1]
                prev_score = self._calculate_window_pattern_score(prev_window)

                # 模式分数变化超过30%
                if abs(pattern_score - prev_score) / prev_score > 0.3:
                    anomaly = AnomalyDetection(
                        anomaly_id=f"pattern_anomaly_{i}_{datetime.now().timestamp()}",
                        severity="medium",
                        type="pattern_change",
                        description=f"测试模式在第 {i} 次执行发生显著变化",
                        affected_tests=list(set(r.get("function_name", "") for r in window)),
                        confidence_score=min(abs(pattern_score - prev_score) / prev_score, 1.0),
                        recommended_action="检查是否有代码变更或环境变化",
                    )
                    anomalies.append(anomaly)

        return anomalies

    def _calculate_window_pattern_score(self, window: List[Dict[str, Any]]) -> float:
        """计算窗口模式分数"""
        if not window:
            return 0.0

        # 综合成功率、平均时间、函数分布等因素
        success_rate = sum(1 for r in window if r.get("status") == "passed") / len(window)

        durations = [r.get("duration", 0) for r in window if r.get("duration")]
        avg_duration = np.mean(durations) if durations else 0

        # 归一化分数
        score = success_rate * 0.7 + (1 / (1 + avg_duration / 1000)) * 0.3
        return score

    def _detect_resource_anomalies(self, test_results: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """检测资源使用异常"""
        anomalies = []

        # 检测内存使用异常
        memory_data = defaultdict(list)
        for result in test_results:
            if "memory_usage" in result:
                func_name = result.get("function_name", "unknown")
                memory_data[func_name].append(result["memory_usage"])

        for func_name, usages in memory_data.items():
            if len(usages) >= 5:
                mean_usage = np.mean(usages)
                recent_usage = usages[-1]

                # 如果最近使用量超过平均值的3倍
                if recent_usage > mean_usage * 3:
                    anomaly = AnomalyDetection(
                        anomaly_id=f"memory_anomaly_{func_name}_{datetime.now().timestamp()}",
                        severity="high",
                        type="memory_spike",
                        description=f"函数 {func_name} 内存使用异常: {recent_usage:.2f}MB (平均: {mean_usage:.2f}MB)",
                        affected_tests=[func_name],
                        confidence_score=min((recent_usage - mean_usage) / (mean_usage + 1), 1.0),
                        recommended_action="检查内存泄漏或大数据处理逻辑",
                    )
                    anomalies.append(anomaly)

        return anomalies

    def predict_test_trends(self, test_results: List[Dict[str, Any]]) -> List[TestTrend]:
        """预测测试趋势"""
        print("🤖 AI正在预测测试趋势...")

        trends = []

        # 1. 覆盖率趋势预测
        coverage_trend = self._predict_coverage_trend(test_results)
        trends.append(coverage_trend)

        # 2. 性能趋势预测
        performance_trend = self._predict_performance_trend(test_results)
        trends.append(performance_trend)

        # 3. 失败率趋势预测
        failure_trend = self._predict_failure_trend(test_results)
        trends.append(failure_trend)

        # 4. 执行时间趋势预测
        duration_trend = self._predict_duration_trend(test_results)
        trends.append(duration_trend)

        return trends

    def _predict_coverage_trend(self, test_results: List[Dict[str, Any]]) -> TestTrend:
        """预测覆盖率趋势"""
        # 按时间分组计算覆盖率
        time_groups = defaultdict(lambda: {"total": 0, "covered": 0})

        for result in test_results:
            timestamp = result.get("timestamp", datetime.now().isoformat())
            func_name = result.get("function_name", "unknown")

            # 简单按天分组
            date_key = timestamp.split("T")[0]
            time_groups[date_key]["total"] += 1
            if result.get("status") == "passed":
                time_groups[date_key]["covered"] += 1

        # 计算覆盖率变化
        coverage_values = []
        for date in sorted(time_groups.keys()):
            coverage = time_groups[date]["covered"] / time_groups[date]["total"]
            coverage_values.append(coverage)

        if len(coverage_values) >= 3:
            # 简单线性预测
            recent_coverage = np.mean(coverage_values[-3:])
            previous_coverage = np.mean(coverage_values[-6:-3]) if len(coverage_values) >= 6 else recent_coverage

            change_rate = (recent_coverage - previous_coverage) / previous_coverage if previous_coverage > 0 else 0

            if change_rate > 0.05:
                direction = "increasing"
            elif change_rate < -0.05:
                direction = "decreasing"
            else:
                direction = "stable"

            return TestTrend(
                trend_name="test_coverage",
                direction=direction,
                change_rate=change_rate,
                impact_level="medium",
                predicted_value=recent_coverage * (1 + change_rate),
                time_frame="next_week",
            )

        return TestTrend(
            trend_name="test_coverage",
            direction="stable",
            change_rate=0.0,
            impact_level="low",
            predicted_value=0.8,
            time_frame="next_week",
        )

    def _predict_performance_trend(self, test_results: List[Dict[str, Any]]) -> TestTrend:
        """预测性能趋势"""
        durations = [r.get("duration", 0) for r in test_results if r.get("duration")]

        if len(durations) >= 10:
            recent_avg = np.mean(durations[-5:])
            previous_avg = np.mean(durations[-10:-5])

            change_rate = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0

            if change_rate > 0.1:
                direction = "increasing"  # 性能下降
            elif change_rate < -0.1:
                direction = "decreasing"  # 性能提升
            else:
                direction = "stable"

            return TestTrend(
                trend_name="performance",
                direction=direction,
                change_rate=change_rate,
                impact_level="high",
                predicted_value=recent_avg * (1 + change_rate),
                time_frame="next_week",
            )

        return TestTrend(
            trend_name="performance",
            direction="stable",
            change_rate=0.0,
            impact_level="medium",
            predicted_value=100.0,
            time_frame="next_week",
        )

    def _predict_failure_trend(self, test_results: List[Dict[str, Any]]) -> TestTrend:
        """预测失败率趋势"""
        failure_rates = []

        # 按时间分组计算失败率
        for i in range(0, len(test_results), 10):
            batch = test_results[i : i + 10]
            failures = sum(1 for r in batch if r.get("status") != "passed")
            failure_rate = failures / len(batch) if batch else 0
            failure_rates.append(failure_rate)

        if len(failure_rates) >= 3:
            recent_rate = np.mean(failure_rates[-3:])
            previous_rate = np.mean(failure_rates[:-3]) if len(failure_rates) > 3 else recent_rate

            change_rate = (recent_rate - previous_rate) / previous_rate if previous_rate > 0 else 0

            if change_rate > 0.2:
                direction = "increasing"
            elif change_rate < -0.2:
                direction = "decreasing"
            else:
                direction = "stable"

            return TestTrend(
                trend_name="failure_rate",
                direction=direction,
                change_rate=change_rate,
                impact_level="high",
                predicted_value=recent_rate * (1 + change_rate),
                time_frame="next_week",
            )

        return TestTrend(
            trend_name="failure_rate",
            direction="stable",
            change_rate=0.0,
            impact_level="medium",
            predicted_value=0.05,
            time_frame="next_week",
        )

    def _predict_duration_trend(self, test_results: List[Dict[str, Any]]) -> TestTrend:
        """预测执行时间趋势"""
        durations = [r.get("duration", 0) for r in test_results if r.get("duration")]

        if len(durations) >= 20:
            # 使用移动平均进行预测
            window_size = 5
            moving_avgs = []
            for i in range(window_size, len(durations)):
                avg = np.mean(durations[i - window_size : i])
                moving_avgs.append(avg)

            if len(moving_avgs) >= 3:
                recent_avg = np.mean(moving_avgs[-3:])
                previous_avg = np.mean(moving_avgs[:-3]) if len(moving_avgs) > 3 else recent_avg

                change_rate = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0

                if change_rate > 0.15:
                    direction = "increasing"
                elif change_rate < -0.15:
                    direction = "decreasing"
                else:
                    direction = "stable"

                return TestTrend(
                    trend_name="execution_duration",
                    direction=direction,
                    change_rate=change_rate,
                    impact_level="medium",
                    predicted_value=recent_avg * (1 + change_rate),
                    time_frame="next_week",
                )

        return TestTrend(
            trend_name="execution_duration",
            direction="stable",
            change_rate=0.0,
            impact_level="low",
            predicted_value=50.0,
            time_frame="next_week",
        )

    def generate_intelligence_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成智能分析报告"""
        print("🤖 AI正在生成智能分析报告...")

        report = {
            "report_id": f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "analysis_period": self._get_analysis_period(test_results),
            "summary": {},
            "patterns": [],
            "anomalies": [],
            "trends": [],
            "recommendations": [],
        }

        # 分析测试模式
        patterns = self.analyze_test_patterns(test_results)
        report["patterns"] = [self._pattern_to_dict(p) for p in patterns[:10]]  # 取前10个

        # 检测异常
        anomalies = self.detect_test_anomalies(test_results)
        report["anomalies"] = [self._anomaly_to_dict(a) for a in anomalies[:10]]  # 取前10个

        # 预测趋势
        trends = self.predict_test_trends(test_results)
        report["trends"] = [self._trend_to_dict(t) for t in trends]

        # 生成摘要
        report["summary"] = self._generate_summary(patterns, anomalies, trends)

        # 生成建议
        report["recommendations"] = self._generate_recommendations(patterns, anomalies, trends)

        return report

    def _pattern_to_dict(self, pattern: TestPattern) -> Dict[str, Any]:
        """将模式转换为字典"""
        return {
            "pattern_name": pattern.pattern_name,
            "frequency": pattern.frequency,
            "success_rate": pattern.success_rate,
            "avg_duration": pattern.avg_duration,
            "confidence": pattern.confidence,
            "related_functions": pattern.related_functions,
        }

    def _anomaly_to_dict(self, anomaly: AnomalyDetection) -> Dict[str, Any]:
        """将异常转换为字典"""
        return {
            "anomaly_id": anomaly.anomaly_id,
            "severity": anomaly.severity,
            "type": anomaly.type,
            "description": anomaly.description,
            "affected_tests": anomaly.affected_tests,
            "confidence_score": anomaly.confidence_score,
            "recommended_action": anomaly.recommended_action,
        }

    def _trend_to_dict(self, trend: TestTrend) -> Dict[str, Any]:
        """将趋势转换为字典"""
        return {
            "trend_name": trend.trend_name,
            "direction": trend.direction,
            "change_rate": trend.change_rate,
            "impact_level": trend.impact_level,
            "predicted_value": trend.predicted_value,
            "time_frame": trend.time_frame,
        }

    def _get_analysis_period(self, test_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """获取分析时间段"""
        if not test_results:
            return {"start": None, "end": None}

        timestamps = []
        for result in test_results:
            timestamp = result.get("timestamp", "")
            if timestamp:
                timestamps.append(timestamp)

        if timestamps:
            return {"start": min(timestamps), "end": max(timestamps)}
        return {"start": None, "end": None}

    def _generate_summary(
        self,
        patterns: List[TestPattern],
        anomalies: List[AnomalyDetection],
        trends: List[TestTrend],
    ) -> Dict[str, Any]:
        """生成摘要"""
        return {
            "total_patterns": len(patterns),
            "total_anomalies": len(anomalies),
            "anomaly_severity_distribution": Counter(a.severity for a in anomalies),
            "trend_directions": Counter(t.direction for t in trends),
            "most_common_pattern": max(patterns, key=lambda p: p.frequency).pattern_name if patterns else None,
            "highest_confidence_anomaly": max(anomalies, key=lambda a: a.confidence_score).type if anomalies else None,
        }

    def _generate_recommendations(
        self,
        patterns: List[TestPattern],
        anomalies: List[AnomalyDetection],
        trends: List[TestTrend],
    ) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于异常的建议
        for anomaly in anomalies:
            if anomaly.severity == "high":
                recommendations.append(f"🚨 高优先级: {anomaly.description}")
                recommendations.append(f"  推荐操作: {anomaly.recommended_action}")

        # 基于趋势的建议
        for trend in trends:
            if trend.direction == "increasing" and trend.change_rate > 0.2:
                recommendations.append(f"⚠️  {trend.trend_name} 正在快速恶化，需要关注")

        # 基于模式的建议
        if patterns:
            high_freq_patterns = [p for p in patterns if p.frequency > 20 and p.success_rate < 0.9]
            if high_freq_patterns:
                recommendations.append(f"📊 {len(high_freq_patterns)} 个高频模式成功率较低，建议优化")

        # 通用建议
        recommendations.extend(
            [
                "🔧 建议定期运行AI分析以持续监控测试质量",
                "📈 关注测试覆盖率和性能指标的趋势变化",
                "🎯 优先处理高置信度异常，防止问题扩大",
            ]
        )

        return recommendations


# Enhanced AI Testing Framework Integration
# Complete integration with the comprehensive testing solution


class AnomalyDetector:
    """高级异常检测器"""

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=100)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.anomaly_history = []

    def fit(self, data: np.ndarray) -> "AnomalyDetector":
        """训练异常检测模型"""
        scaled_data = self.scaler.fit_transform(data)
        self.model.fit(scaled_data)
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """检测异常点"""
        if not self.is_fitted:
            raise ValueError("模型未训练，请先调用fit方法")

        scaled_data = self.scaler.transform(data)
        anomalies = self.model.predict(scaled_data)
        anomaly_scores = self.model.decision_function(scaled_data)

        # 记录异常历史
        anomaly_count = np.sum(anomalies == -1)
        self.anomaly_history.append(
            {
                "timestamp": datetime.now(),
                "total_points": len(data),
                "anomaly_count": anomaly_count,
                "anomaly_rate": anomaly_count / len(data),
            }
        )

        return anomalies, anomaly_scores

    def get_anomaly_summary(self) -> Dict[str, Any]:
        """获取异常检测摘要"""
        if not self.anomaly_history:
            return {"message": "暂无异常检测历史"}

        history_df = pd.DataFrame(self.anomaly_history)
        return {
            "total_detections": len(self.anomaly_history),
            "total_anomalies": history_df["anomaly_count"].sum(),
            "average_anomaly_rate": history_df["anomaly_rate"].mean(),
            "max_anomaly_rate": history_df["anomaly_rate"].max(),
            "recent_anomalies": history_df.tail(5).to_dict("records"),
        }


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self):
        self.trend_models = {}
        self.seasonal_decomposers = {}

    def analyze_trend(self, data: pd.Series, freq: str = "D") -> Dict[str, Any]:
        """分析时间序列趋势"""
        try:
            # 确保数据是时间序列
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)

            # 填充缺失值
            data = data.fillna(method="ffill").fillna(method="bfill")

            # 季节性分解
            decomposition = seasonal_decompose(data, model="additive", period=min(freq, len(data) // 2))

            # 趋势分析
            trend = decomposition.trend.dropna()
            seasonal = decomposition.seasonal.dropna()
            residual = decomposition.resid.dropna()

            # 计算趋势指标
            trend_slope = self._calculate_trend_slope(trend)
            seasonality_strength = self._calculate_seasonality_strength(seasonal, residual)

            return {
                "trend_direction": "upward" if trend_slope > 0 else "downward" if trend_slope < 0 else "stable",
                "trend_strength": abs(trend_slope),
                "seasonality_strength": seasonality_strength,
                "volatility": residual.std(),
                "decomposition": {
                    "trend": trend.to_dict(),
                    "seasonal": seasonal.to_dict(),
                    "residual": residual.to_dict(),
                },
            }
        except Exception as e:
            return {"error": f"趋势分析失败: {str(e)}"}

    def _calculate_trend_slope(self, series: pd.Series) -> float:
        """计算趋势斜率"""
        x = np.arange(len(series))
        y = series.values
        return np.polyfit(x, y, 1)[0]

    def _calculate_seasonality_strength(self, seasonal: pd.Series, residual: pd.Series) -> float:
        """计算季节性强度"""
        var_seasonal = seasonal.var()
        var_residual = residual.var()
        return var_seasonal / (var_seasonal + var_residual) if (var_seasonal + var_residual) > 0 else 0


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


# 使用示例和测试
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


if __name__ == "__main__":
    # 运行原有测试
    print("🤖 启动AI测试数据分析器...")
    test_anomaly_detection()
    print()
    test_pattern_analysis()
    print()
    test_trend_prediction()

    # 运行增强功能演示
    print("\n" + "=" * 50)
    asyncio.run(demo_enhanced_data_analyzer())


# 测试函数
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


if __name__ == "__main__":
    # 运行测试
    print("🤖 启动AI测试数据分析器...")

    test_anomaly_detection()
    print()
    test_pattern_analysis()
    print()
    test_trend_prediction()
