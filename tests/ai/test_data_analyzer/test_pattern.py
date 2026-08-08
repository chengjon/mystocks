#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI测试数据分析器
提供智能测试数据分析、模式识别和预测
"""

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

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


