"""
Time Series Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台时间序列分析功能

This module provides advanced time series analysis capabilities including:
- Turning point detection and segmentation
- Pattern matching and prediction
- Time series decomposition and trend analysis
- Seasonal and cyclical pattern recognition
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

# GPU acceleration support
try:
    pass

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Time series analysis will run on CPU.")

# Additional libraries for time series analysis
try:
    from scipy.signal import find_peaks

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("SciPy/Sklearn not available. Some time series features will be limited.")


@dataclass
class TurningPoint:
    """转折点数据结构"""

    index: int
    timestamp: datetime
    price: float
    point_type: str  # 'peak', 'valley', 'inflection'
    significance: float  # 重要性评分 (0-1)
    confidence: float  # 置信度 (0-1)
    duration: Optional[int] = None  # 持续周期


@dataclass
class TimeSeriesSegment:
    """时间序列分段"""

    start_index: int
    end_index: int
    start_timestamp: datetime
    end_timestamp: datetime
    segment_type: str  # 'uptrend', 'downtrend', 'sideways', 'volatile'
    duration: int  # 持续周期数
    magnitude: float  # 变化幅度
    trend_strength: float  # 趋势强度 (0-1)
    volatility: float  # 波动率
    pattern_match: Optional[str] = None  # 匹配的模式


@dataclass
class PatternMatch:
    """模式匹配结果"""

    pattern_name: str
    start_index: int
    end_index: int
    similarity_score: float  # 相似度 (0-1)
    predicted_direction: str  # 预测方向
    confidence: float  # 预测置信度
    expected_return: Optional[float] = None  # 预期收益率


class TimeSeriesAnalyzer(BaseAnalyzer):
    """
    时间序列分析器

    提供高级时间序列分析功能，包括：
    - 转折点检测和分段
    - 模式匹配和预测
    - 时间序列分解和趋势分析
    - 季节性和周期性模式识别
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 转折点检测参数
    self.turning_point_params = {
        "min_prominence": 0.02,  # 最小突出度
        "min_distance": 5,  # 最小距离
        "peak_width": 3,  # 峰值宽度
        "valley_width": 3,  # 谷值宽度
    }

    # 分段参数
    self.segmentation_params = {
        "min_segment_length": 10,  # 最小分段长度
        "trend_threshold": 0.001,  # 趋势阈值
        "volatility_window": 20,  # 波动率计算窗口
    }

    # 模式识别参数
    self.pattern_params = {
        "min_pattern_length": 10,  # 最小模式长度
        "max_pattern_length": 50,  # 最大模式长度
        "similarity_threshold": 0.8,  # 相似度阈值
        "dtw_window": 5,  # DTW窗口大小
    }

    # 预定义模式库
    self.pattern_library = {
        "head_shoulders": self._detect_head_shoulders_pattern,
        "double_top": self._detect_double_top_pattern,
        "double_bottom": self._detect_double_bottom_pattern,
        "triangle": self._detect_triangle_pattern,
        "wedge": self._detect_wedge_pattern,
        "cup_handle": self._detect_cup_handle_pattern,
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行时间序列分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数
            - analysis_period: 分析周期 (默认: 365天)
            - detect_turning_points: 是否检测转折点 (默认: True)
            - perform_segmentation: 是否进行分段分析 (默认: True)
            - pattern_matching: 是否进行模式匹配 (默认: True)
            - include_predictions: 是否包含预测 (默认: True)

    Returns:
        AnalysisResult: 分析结果
    """
    analysis_period = kwargs.get("analysis_period", 365)
    detect_turning_points = kwargs.get("detect_turning_points", True)
    perform_segmentation = kwargs.get("perform_segmentation", True)
    pattern_matching = kwargs.get("pattern_matching", True)
    include_predictions = kwargs.get("include_predictions", True)

    try:
        # 获取历史数据
        data = self._get_historical_data(stock_code, days=analysis_period, data_type="1d")
        if data.empty:
            return self._create_error_result(stock_code, "No historical data available for time series analysis")

        # 转折点检测
        turning_points = []
        if detect_turning_points:
            turning_points = self._detect_turning_points(data)

        # 时间序列分段
        segments = []
        if perform_segmentation:
            segments = self._perform_segmentation(data, turning_points)

        # 模式匹配
        patterns = []
        if pattern_matching:
            patterns = self._perform_pattern_matching(data)

        # 趋势分析
        trend_analysis = self._analyze_trend(data)

        # 季节性和周期性分析
        seasonal_analysis = self._analyze_seasonal_patterns(data)

        # 预测分析
        predictions = {}
        if include_predictions:
            predictions = self._generate_predictions(data, patterns)

        # 计算综合得分
        scores = self._calculate_ts_scores(data, turning_points, segments, patterns)

        # 生成信号
        signals = self._generate_ts_signals(turning_points, segments, patterns, predictions)

        # 投资建议
        recommendations = self._generate_ts_recommendations(trend_analysis, seasonal_analysis, predictions)

        # 风险评估
        risk_assessment = self._assess_ts_risk(turning_points, segments, patterns)

        # 元数据
        metadata = {
            "analysis_period_days": analysis_period,
            "data_points": len(data),
            "turning_points_detected": len(turning_points),
            "segments_identified": len(segments),
            "patterns_found": len(patterns),
            "trend_direction": trend_analysis.get("direction"),
            "trend_strength": trend_analysis.get("strength"),
            "seasonal_patterns": bool(seasonal_analysis.get("has_seasonality")),
            "volatility_level": data["close"].pct_change().std() * np.sqrt(252) if len(data) > 1 else 0,
            "last_analysis_timestamp": datetime.now(),
        }

        return AnalysisResult(
            analysis_type=AnalysisType.TIME_SERIES,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=data if kwargs.get("include_raw_data", False) else None,
        )

    except Exception as e:
        return self._create_error_result(stock_code, str(e))


def _detect_turning_points(self, data: pd.DataFrame) -> List[TurningPoint]:
    """检测转折点"""
    if data.empty or "close" not in data.columns:
        return []

    try:
        prices = data["close"].values
        indices = np.arange(len(prices))

        # 使用scipy.signal.find_peaks检测峰值和谷值
        if SCIPY_AVAILABLE:
            # 检测峰值
            peaks, peak_properties = find_peaks(
                prices,
                prominence=np.std(prices) * self.turning_point_params["min_prominence"],
                distance=self.turning_point_params["min_distance"],
                width=self.turning_point_params["peak_width"],
            )

            # 检测谷值
            valleys, valley_properties = find_peaks(
                -prices,  # 取负值检测谷值
                prominence=np.std(prices) * self.turning_point_params["min_prominence"],
                distance=self.turning_point_params["min_distance"],
                width=self.turning_point_params["valley_width"],
            )

            turning_points = []

            # 处理峰值
            for i, peak_idx in enumerate(peaks):
                prominence = peak_properties["prominences"][i] if i < len(peak_properties["prominences"]) else 0
                significance = min(prominence / np.std(prices), 1.0)

                turning_point = TurningPoint(
                    index=int(peak_idx),
                    timestamp=data.index[peak_idx].to_pydatetime(),
                    price=prices[peak_idx],
                    point_type="peak",
                    significance=significance,
                    confidence=0.8,
                )
                turning_points.append(turning_point)

            # 处理谷值
            for i, valley_idx in enumerate(valleys):
                prominence = valley_properties["prominences"][i] if i < len(valley_properties["prominences"]) else 0
                significance = min(prominence / np.std(prices), 1.0)

                turning_point = TurningPoint(
                    index=int(valley_idx),
                    timestamp=data.index[valley_idx].to_pydatetime(),
                    price=prices[valley_idx],
                    point_type="valley",
                    significance=significance,
                    confidence=0.8,
                )
                turning_points.append(turning_point)

            # 按索引排序
            turning_points.sort(key=lambda x: x.index)

            return turning_points
        else:
            # 简化的转折点检测（当scipy不可用时）
            return self._simple_turning_point_detection(data)

    except Exception as e:
        print(f"Error detecting turning points: {e}")
        return []


def _simple_turning_point_detection(self, data: pd.DataFrame) -> List[TurningPoint]:
    """简化的转折点检测"""
    prices = data["close"].values
    turning_points = []

    # 使用移动平均和差分检测转折点
    ma_short = pd.Series(prices).rolling(window=5).mean()
    ma_long = pd.Series(prices).rolling(window=20).mean()

    # 计算趋势变化
    trend_change = np.sign(ma_short - ma_long).diff()

    # 找出趋势变化点
    change_points = np.where(trend_change != 0)[0]

    for idx in change_points:
        if idx < len(prices):
            point_type = "peak" if trend_change.iloc[idx] < 0 else "valley"
            turning_point = TurningPoint(
                index=int(idx),
                timestamp=data.index[idx].to_pydatetime(),
                price=prices[idx],
                point_type=point_type,
                significance=0.5,
                confidence=0.6,
            )
            turning_points.append(turning_point)

    return turning_points


def _perform_segmentation(self, data: pd.DataFrame, turning_points: List[TurningPoint]) -> List[TimeSeriesSegment]:
    """执行时间序列分段"""
    if data.empty:
        return []

    try:
        prices = data["close"].values
        segments = []

        # 使用转折点作为分段边界
        if turning_points:
            segment_boundaries = [0] + [tp.index for tp in turning_points] + [len(data) - 1]

            for i in range(len(segment_boundaries) - 1):
                start_idx = segment_boundaries[i]
                end_idx = segment_boundaries[i + 1]

                if end_idx - start_idx >= self.segmentation_params["min_segment_length"]:
                    segment = self._analyze_segment(data, start_idx, end_idx)
                    if segment:
                        segments.append(segment)
        else:
            # 如果没有转折点，将整个序列作为一个分段
            segment = self._analyze_segment(data, 0, len(data) - 1)
            if segment:
                segments.append(segment)

        return segments

    except Exception as e:
        print(f"Error performing segmentation: {e}")
        return []


def _analyze_segment(self, data: pd.DataFrame, start_idx: int, end_idx: int) -> Optional[TimeSeriesSegment]:
    """分析单个分段"""
    try:
        segment_data = data.iloc[start_idx : end_idx + 1]
        prices = segment_data["close"].values

        if len(prices) < 2:
            return None

        # 计算趋势强度
        start_price = prices[0]
        end_price = prices[-1]
        price_change = (end_price - start_price) / start_price

        # 计算波动率
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) if len(returns) > 0 else 0

        # 确定分段类型
        if abs(price_change) < self.segmentation_params["trend_threshold"]:
            segment_type = "sideways"
            trend_strength = 0.0
        elif price_change > 0:
            segment_type = "uptrend"
            trend_strength = min(abs(price_change) * 10, 1.0)  # 归一化
        else:
            segment_type = "downtrend"
            trend_strength = min(abs(price_change) * 10, 1.0)

        # 如果波动率很高，标记为波动型
        if volatility > np.mean(np.abs(returns)) * 2:
            segment_type = "volatile"

        magnitude = abs(price_change)

        return TimeSeriesSegment(
            start_index=start_idx,
            end_index=end_idx,
            start_timestamp=data.index[start_idx].to_pydatetime(),
            end_timestamp=data.index[end_idx].to_pydatetime(),
            segment_type=segment_type,
            duration=end_idx - start_idx + 1,
            magnitude=magnitude,
            trend_strength=trend_strength,
            volatility=volatility,
        )

    except Exception as e:
        print(f"Error analyzing segment {start_idx}-{end_idx}: {e}")
        return None


def _perform_pattern_matching(self, data: pd.DataFrame) -> List[PatternMatch]:
    """执行模式匹配"""
    if data.empty:
        return []

    patterns = []

    # 对每个预定义模式进行匹配
    for pattern_name, pattern_func in self.pattern_library.items():
        try:
            pattern_matches = pattern_func(data)
            patterns.extend(pattern_matches)
        except Exception as e:
            print(f"Error matching pattern {pattern_name}: {e}")
            continue

    # 按相似度排序
    patterns.sort(key=lambda x: x.similarity_score, reverse=True)

    return patterns


def _detect_head_shoulders_pattern(self, data: pd.DataFrame) -> List[PatternMatch]:
    """检测头肩顶模式"""
    # 简化的头肩顶检测实现
    # 实际实现需要更复杂的形态识别算法
    return []


def _detect_double_top_pattern(self, data: pd.DataFrame) -> List[PatternMatch]:
    """检测双顶模式"""
    # 简化的双顶检测实现
    return []


def _detect_double_bottom_pattern(self, data: pd.DataFrame) -> List[PatternMatch]:
    """检测双底模式"""
    # 简化的双底检测实现
    return []


def _detect_triangle_pattern(self, data: pd.DataFrame) -> List[PatternMatch]:
    """检测三角形模式"""
    # 简化的三角形检测实现
    return []


def _detect_wedge_pattern(self, data: pd.DataFrame) -> List[PatternMatch]:
    """检测楔形模式"""
    # 简化的楔形检测实现
    return []


def _detect_cup_handle_pattern(self, data: pd.DataFrame) -> List[PatternMatch]:
    """检测杯柄模式"""
    # 简化的杯柄检测实现
    return []


def _analyze_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
    """分析趋势"""
    if data.empty or len(data) < 10:
        return {"direction": "unknown", "strength": 0.0}

    try:
        prices = data["close"].values

        # 计算长期趋势
        long_ma = pd.Series(prices).rolling(window=50).mean()
        short_ma = pd.Series(prices).rolling(window=20).mean()

        if len(long_ma) < 2 or len(short_ma) < 2:
            return {"direction": "unknown", "strength": 0.0}

        # 趋势方向
        current_long = long_ma.iloc[-1]
        current_short = short_ma.iloc[-1]

        if current_short > current_long * 1.01:  # 1%阈值
            direction = "uptrend"
        elif current_short < current_long * 0.99:
            direction = "downtrend"
        else:
            direction = "sideways"

        # 趋势强度
        trend_slope = np.polyfit(range(len(long_ma.dropna())), long_ma.dropna(), 1)[0]
        strength = min(abs(trend_slope) * 1000, 1.0)  # 归一化

        return {
            "direction": direction,
            "strength": strength,
            "slope": trend_slope,
            "long_ma": current_long,
            "short_ma": current_short,
        }

    except Exception as e:
        print(f"Error analyzing trend: {e}")
        return {"direction": "unknown", "strength": 0.0}


def _analyze_seasonal_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
    """分析季节性模式"""
    if data.empty or len(data) < 60:  # 需要至少60个数据点
        return {"has_seasonality": False, "patterns": []}

    try:
        # 简化的季节性分析
        # 检查月度季节性
        if "close" in data.columns:
            data_with_month = data.copy()
            data_with_month["month"] = data_with_month.index.month

            # 计算每月平均收益率
            monthly_returns = (
                data_with_month.groupby("month")["close"].pct_change().groupby(data_with_month["month"]).mean()
            )

            # 检查是否有显著的季节性模式
            monthly_std = monthly_returns.std()
            monthly_mean = monthly_returns.mean()

            has_seasonality = monthly_std > abs(monthly_mean) * 0.5  # 标准差大于平均值的一半

            return {
                "has_seasonality": has_seasonality,
                "monthly_patterns": monthly_returns.to_dict(),
                "seasonal_strength": monthly_std / abs(monthly_mean) if monthly_mean != 0 else 0,
            }
        else:
            return {"has_seasonality": False, "patterns": []}

    except Exception as e:
        print(f"Error analyzing seasonal patterns: {e}")
        return {"has_seasonality": False, "patterns": []}


def _generate_predictions(self, data: pd.DataFrame, patterns: List[PatternMatch]) -> Dict[str, Any]:
    """生成预测"""
    predictions = {}

    try:
        if patterns and len(patterns) > 0:
            # 基于最相似的模式进行预测
            best_pattern = max(patterns, key=lambda x: x.similarity_score)

            predictions["pattern_based"] = {
                "predicted_direction": best_pattern.predicted_direction,
                "confidence": best_pattern.confidence,
                "expected_return": best_pattern.expected_return,
                "time_horizon": 20,  # 20个交易日
                "pattern_name": best_pattern.pattern_name,
            }

        # 基于趋势的预测
        trend_analysis = self._analyze_trend(data)
        predictions["trend_based"] = {
            "predicted_direction": trend_analysis["direction"],
            "confidence": trend_analysis["strength"],
            "time_horizon": 10,  # 10个交易日
        }

        # 综合预测
        if "pattern_based" in predictions and "trend_based" in predictions:
            pattern_conf = predictions["pattern_based"]["confidence"]
            trend_conf = predictions["trend_based"]["confidence"]

            if pattern_conf > trend_conf:
                final_direction = predictions["pattern_based"]["predicted_direction"]
                final_confidence = pattern_conf
            else:
                final_direction = predictions["trend_based"]["predicted_direction"]
                final_confidence = trend_conf

            predictions["combined"] = {
                "predicted_direction": final_direction,
                "confidence": final_confidence,
                "method": "pattern" if pattern_conf > trend_conf else "trend",
            }

    except Exception as e:
        print(f"Error generating predictions: {e}")

    return predictions


def _calculate_ts_scores(
    self,
    data: pd.DataFrame,
    turning_points: List[TurningPoint],
    segments: List[TimeSeriesSegment],
    patterns: List[PatternMatch],
) -> Dict[str, float]:
    """计算时间序列分析得分"""
    scores = {}

    try:
        # 转折点重要性得分
        if turning_points:
            avg_significance = np.mean([tp.significance for tp in turning_points])
            scores["turning_point_significance"] = avg_significance
        else:
            scores["turning_point_significance"] = 0.0

        # 分段趋势强度得分
        if segments:
            avg_trend_strength = np.mean([seg.trend_strength for seg in segments])
            scores["segment_trend_strength"] = avg_trend_strength
        else:
            scores["segment_trend_strength"] = 0.0

        # 模式匹配得分
        if patterns:
            avg_similarity = np.mean([p.similarity_score for p in patterns])
            scores["pattern_similarity"] = avg_similarity
        else:
            scores["pattern_similarity"] = 0.0

        # 整体时间序列稳定性得分
        if len(data) > 10:
            returns = data["close"].pct_change().dropna()
            volatility = returns.std()
            stability_score = max(0, 1 - volatility * 10)  # 波动率越低得分越高
            scores["stability_score"] = stability_score
        else:
            scores["stability_score"] = 0.5

        # 综合得分
        weights = {
            "turning_point_significance": 0.25,
            "segment_trend_strength": 0.30,
            "pattern_similarity": 0.25,
            "stability_score": 0.20,
        }

        overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        scores["overall_score"] = overall_score

    except Exception as e:
        print(f"Error calculating TS scores: {e}")
        scores = {"overall_score": 0.0, "error": True}

    return scores


def _generate_ts_signals(
    self,
    turning_points: List[TurningPoint],
    segments: List[TimeSeriesSegment],
    patterns: List[PatternMatch],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """生成时间序列信号"""
    signals = []

    # 转折点信号
    for tp in turning_points[-5:]:  # 只取最近5个转折点
        signal_type = "turning_point"
        severity = "high" if tp.significance > 0.7 else "medium" if tp.significance > 0.5 else "low"

        signals.append(
            {
                "type": signal_type,
                "severity": severity,
                "message": f"{tp.point_type.upper()}转折点检测 - 重要性: {tp.significance:.2f}",
                "details": {
                    "point_type": tp.point_type,
                    "significance": tp.significance,
                    "confidence": tp.confidence,
                    "timestamp": tp.timestamp.isoformat(),
                },
            }
        )

    # 分段信号
    if segments:
        latest_segment = segments[-1]
        signal_type = f"segment_{latest_segment.segment_type}"
        severity = "high" if latest_segment.trend_strength > 0.7 else "medium"

        signals.append(
            {
                "type": signal_type,
                "severity": severity,
                "message": f"当前分段: {latest_segment.segment_type} - 趋势强度: {latest_segment.trend_strength:.2f}",
                "details": {
                    "segment_type": latest_segment.segment_type,
                    "trend_strength": latest_segment.trend_strength,
                    "volatility": latest_segment.volatility,
                    "duration": latest_segment.duration,
                },
            }
        )

    # 模式匹配信号
    for pattern in patterns[:3]:  # 只取最相似的3个模式
        signal_type = f"pattern_{pattern.pattern_name}"
        severity = "high" if pattern.similarity_score > 0.85 else "medium"

        signals.append(
            {
                "type": signal_type,
                "severity": severity,
                "message": f"模式匹配: {pattern.pattern_name} - 相似度: {pattern.similarity_score:.2f}",
                "details": {
                    "pattern_name": pattern.pattern_name,
                    "similarity_score": pattern.similarity_score,
                    "predicted_direction": pattern.predicted_direction,
                    "confidence": pattern.confidence,
                },
            }
        )

    # 预测信号
    if "combined" in predictions:
        pred = predictions["combined"]
        signal_type = f"prediction_{pred['predicted_direction']}"
        severity = "medium"

        signals.append(
            {
                "type": signal_type,
                "severity": severity,
                "message": f"预测方向: {pred['predicted_direction']} - 置信度: {pred['confidence']:.2f}",
                "details": {
                    "predicted_direction": pred["predicted_direction"],
                    "confidence": pred["confidence"],
                    "method": pred.get("method", "unknown"),
                },
            }
        )

    return signals


def _generate_ts_recommendations(
    self, trend_analysis: Dict[str, Any], seasonal_analysis: Dict[str, Any], predictions: Dict[str, Any]
) -> Dict[str, Any]:
    """生成时间序列建议"""
    recommendations = {}

    try:
        # 基于趋势的建议
        trend_direction = trend_analysis.get("direction", "unknown")
        trend_strength = trend_analysis.get("strength", 0.0)

        if trend_direction == "uptrend" and trend_strength > 0.6:
            primary_signal = "buy"
            action = "趋势向上，可考虑买入"
            confidence = "high"
        elif trend_direction == "downtrend" and trend_strength > 0.6:
            primary_signal = "sell"
            action = "趋势向下，建议观望或卖出"
            confidence = "high"
        else:
            primary_signal = "hold"
            action = "趋势不明，建议观望"
            confidence = "medium"

        # 考虑季节性因素
        if seasonal_analysis.get("has_seasonality", False):
            seasonal_strength = seasonal_analysis.get("seasonal_strength", 0)
            if seasonal_strength > 0.5:
                action += f" (季节性因素显著: {seasonal_strength:.2f})"

        # 考虑预测结果
        if "combined" in predictions:
            pred_direction = predictions["combined"].get("predicted_direction")
            pred_confidence = predictions["combined"].get("confidence", 0)

            if pred_confidence > 0.7:
                if pred_direction == primary_signal:
                    action += f" (预测确认{primary_signal}信号)"
                    confidence = "high"
                else:
                    action += " (预测与趋势存在分歧，需谨慎)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "trend_analysis": trend_analysis,
                "seasonal_factors": seasonal_analysis.get("has_seasonality", False),
                "prediction_available": bool(predictions),
            }
        )

    except Exception as e:
        print(f"Error generating TS recommendations: {e}")
        recommendations = {
            "primary_signal": "hold",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_ts_risk(
    self, turning_points: List[TurningPoint], segments: List[TimeSeriesSegment], patterns: List[PatternMatch]
) -> Dict[str, Any]:
    """评估时间序列风险"""
    risk_assessment = {}

    try:
        # 转折点风险
        if turning_points:
            high_significance_points = [tp for tp in turning_points if tp.significance > 0.7]
            turning_point_risk = len(high_significance_points) / max(len(turning_points), 1)

            if turning_point_risk > 0.5:
                risk_level = "high"  # 太多重要转折点，风险高
            elif turning_point_risk > 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
        else:
            risk_level = "medium"  # 没有检测到转折点，可能数据不足

        risk_assessment.update(
            {
                "turning_point_risk": turning_point_risk if "turning_point_risk" in locals() else 0,
                "overall_risk_level": risk_level,
                "volatility_risk": self._assess_volatility_risk(segments),
                "pattern_risk": self._assess_pattern_risk(patterns),
            }
        )

    except Exception as e:
        print(f"Error assessing TS risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _assess_volatility_risk(self, segments: List[TimeSeriesSegment]) -> str:
    """评估波动率风险"""
    if not segments:
        return "medium"

    avg_volatility = np.mean([seg.volatility for seg in segments])
    volatile_segments = sum(1 for seg in segments if seg.segment_type == "volatile")

    volatility_ratio = volatile_segments / len(segments)

    if avg_volatility > 0.05 or volatility_ratio > 0.4:  # 5%日波动率或40%波动分段
        return "high"
    elif avg_volatility > 0.03 or volatility_ratio > 0.2:
        return "medium"
    else:
        return "low"


def _assess_pattern_risk(self, patterns: List[PatternMatch]) -> str:
    """评估模式风险"""
    if not patterns:
        return "medium"

    # 计算看跌模式的比例
    bearish_patterns = sum(1 for p in patterns if p.predicted_direction in ["down", "bearish"])
    bearish_ratio = bearish_patterns / len(patterns)

    if bearish_ratio > 0.6:
        return "high"  # 大多模式看跌，风险高
    elif bearish_ratio > 0.4:
        return "medium"
    else:
        return "low"


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.TIME_SERIES,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"时间序列分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
