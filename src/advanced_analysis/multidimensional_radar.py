"""
Multidimensional Radar Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台多维度雷达分析功能

This module provides comprehensive multidimensional radar analysis by integrating
all 8 core analysis dimensions:

1. Fundamental Analysis (基本面分析)
2. Technical Analysis (技术面分析)
3. Trading Signals (交易信号)
4. Time Series Analysis (时序分析)
5. Market Panorama (市场全景)
6. Capital Flow (资金流向)
7. Chip Distribution (筹码分布)
8. Anomaly Tracking (异常追踪)

The radar analysis provides:
- Multi-dimensional scoring across all analysis types
- Integrated risk assessment and recommendations
- Visual radar chart data for frontend display
- Comprehensive investment decision support
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import warnings

from src.advanced_analysis import BaseAnalyzer, AnalysisResult, AnalysisType
from src.core import DataClassification

# Import all analysis modules
from src.advanced_analysis.fundamental_analyzer import FundamentalAnalyzer
from src.advanced_analysis.technical_analyzer import TechnicalAnalyzer
from src.advanced_analysis.trading_signals_analyzer import TradingSignalAnalyzer
from src.advanced_analysis.timeseries_analyzer import TimeSeriesAnalyzer
from src.advanced_analysis.market_panorama_analyzer import MarketPanoramaAnalyzer
from src.advanced_analysis.capital_flow_analyzer import CapitalFlowAnalyzer
from src.advanced_analysis.chip_distribution_analyzer import ChipDistributionAnalyzer
from src.advanced_analysis.anomaly_tracking_analyzer import AnomalyTrackingAnalyzer

# GPU acceleration support
try:
    import cudf
    import cuml

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Multidimensional radar analysis will run on CPU.")


@dataclass
class RadarDimension:
    """雷达图维度数据"""

    name: str  # 维度名称
    score: float  # 评分 (0-100)
    weight: float  # 权重
    analysis_type: AnalysisType  # 对应的分析类型
    key_metrics: Dict[str, Any]  # 关键指标
    signals: List[Dict[str, Any]]  # 信号列表
    risk_level: str  # 风险等级


@dataclass
class RadarAnalysisResult:
    """雷达分析结果"""

    overall_score: float  # 综合评分
    risk_assessment: Dict[str, Any]  # 风险评估
    investment_recommendation: str  # 投资建议
    dimensions: List[RadarDimension]  # 各维度数据
    radar_chart_data: Dict[str, Any]  # 雷达图数据
    key_insights: List[str]  # 关键洞察
    timestamp: datetime


class MultidimensionalRadarAnalyzer(BaseAnalyzer):
    """
    多维度雷达分析器

    整合所有分析维度，提供全面的量化分析雷达图：
    - 8个核心分析维度的综合评分
    - 风险评估和投资建议
    - 可视化雷达图数据
    - 智能权重分配和综合判断
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 初始化所有分析器
    self.analyzers = {
        AnalysisType.FUNDAMENTAL: FundamentalAnalyzer(data_manager, gpu_manager),
        AnalysisType.TECHNICAL: TechnicalAnalyzer(data_manager, gpu_manager),
        AnalysisType.TRADING_SIGNALS: TradingSignalAnalyzer(data_manager, gpu_manager),
        AnalysisType.TIME_SERIES: TimeSeriesAnalyzer(data_manager, gpu_manager),
        AnalysisType.MARKET_PANORAMA: MarketPanoramaAnalyzer(data_manager, gpu_manager),
        AnalysisType.CAPITAL_FLOW: CapitalFlowAnalyzer(data_manager, gpu_manager),
        AnalysisType.CHIP_DISTRIBUTION: ChipDistributionAnalyzer(data_manager, gpu_manager),
        AnalysisType.ANOMALY_TRACKING: AnomalyTrackingAnalyzer(data_manager, gpu_manager),
    }

    # 维度权重配置（可根据市场环境动态调整）
    self.dimension_weights = {
        AnalysisType.FUNDAMENTAL: 0.20,  # 基本面：20%
        AnalysisType.TECHNICAL: 0.15,  # 技术面：15%
        AnalysisType.TRADING_SIGNALS: 0.15,  # 交易信号：15%
        AnalysisType.TIME_SERIES: 0.10,  # 时序分析：10%
        AnalysisType.CAPITAL_FLOW: 0.15,  # 资金流向：15%
        AnalysisType.CHIP_DISTRIBUTION: 0.10,  # 筹码分布：10%
        AnalysisType.ANOMALY_TRACKING: 0.10,  # 异常追踪：10%
        AnalysisType.MARKET_PANORAMA: 0.05,  # 市场全景：5%
    }

    # 风险等级映射
    self.risk_levels = {
        "low": {"threshold": 30, "description": "低风险"},
        "medium": {"threshold": 60, "description": "中等风险"},
        "high": {"threshold": 80, "description": "高风险"},
        "extreme": {"threshold": 100, "description": "极高风险"},
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行多维度雷达分析

    Args:
        stock_code: 股票代码
        **kwargs: 额外参数
            - weights: 自定义维度权重
            - focus_dimensions: 重点关注的维度列表

    Returns:
        AnalysisResult: 分析结果
    """
    try:
        # 执行多维度分析
        radar_result = self._perform_multidimensional_analysis(stock_code, **kwargs)

        # 生成综合评分和建议
        overall_score = self._calculate_overall_score(radar_result.dimensions)
        risk_assessment = self._assess_risk(radar_result)
        recommendation = self._generate_recommendation(overall_score, risk_assessment)

        # 构建分析结果
        scores = {dim.name: dim.score for dim in radar_result.dimensions}
        signals = self._aggregate_signals(radar_result.dimensions)
        recommendations = {
            "overall_recommendation": recommendation,
            "radar_analysis": radar_result.radar_chart_data,
            "key_insights": radar_result.key_insights,
        }

        return AnalysisResult(
            analysis_type=AnalysisType.MULTIDIMENSIONAL_RADAR,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata={
                "dimensions_count": len(radar_result.dimensions),
                "analysis_timestamp": radar_result.timestamp.isoformat(),
                "weights_used": self.dimension_weights,
            },
            raw_data=None,
        )

    except Exception as e:
        print(f"Error in multidimensional radar analysis for {stock_code}: {e}")
        return self._create_error_result(stock_code, str(e))


def _perform_multidimensional_analysis(self, stock_code: str, **kwargs) -> RadarAnalysisResult:
    """
    执行多维度分析

    Args:
        stock_code: 股票代码
        **kwargs: 分析参数

    Returns:
        RadarAnalysisResult: 雷达分析结果
    """
    dimensions = []
    key_insights = []

    # 自定义权重（如果提供）
    weights = kwargs.get("weights", self.dimension_weights)
    focus_dimensions = kwargs.get("focus_dimensions", list(self.analyzers.keys()))

    # GPU优化：并行执行各维度分析
    analysis_results = {}
    if GPU_AVAILABLE and self.gpu_manager and len(focus_dimensions) > 3:
        # GPU并行分析
        try:
            analysis_results = self._gpu_parallel_analysis(focus_dimensions, stock_code, **kwargs)
        except Exception as e:
            print(f"GPU parallel analysis failed, falling back to sequential: {e}")
            analysis_results = self._sequential_analysis(focus_dimensions, stock_code, **kwargs)
    else:
        # 顺序分析
        analysis_results = self._sequential_analysis(focus_dimensions, stock_code, **kwargs)

    # 处理各维度结果
    for analysis_type, result in analysis_results.items():
        if result is None:
            # 创建默认维度数据
            dimension = RadarDimension(
                name=analysis_type.value,
                score=50.0,  # 中性评分
                weight=weights.get(analysis_type, 0.1),
                analysis_type=analysis_type,
                key_metrics={},
                signals=[],
                risk_level="medium",
            )
        else:
            # 转换分析结果为雷达维度
            dimension = self._convert_to_radar_dimension(analysis_type, result, weights.get(analysis_type, 0.1))

        dimensions.append(dimension)

        # 提取关键洞察
        insights = self._extract_insights(dimension)
        key_insights.extend(insights)

    # 生成雷达图数据
    radar_chart_data = self._generate_radar_chart_data(dimensions)

    # 计算综合评分
    overall_score = self._calculate_overall_score(dimensions)

    # 风险评估
    risk_assessment = self._assess_overall_risk_from_dimensions(dimensions)

    return RadarAnalysisResult(
        overall_score=overall_score,
        risk_assessment=risk_assessment,
        investment_recommendation="",  # 将在后续步骤中设置
        dimensions=dimensions,
        radar_chart_data=radar_chart_data,
        key_insights=key_insights[:10],  # 限制为10个关键洞察
        timestamp=datetime.now(),
    )


def _gpu_parallel_analysis(
    self, analysis_types: List[AnalysisType], stock_code: str, **kwargs
) -> Dict[AnalysisType, Any]:
    """GPU并行分析多个维度"""
    import concurrent.futures

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(analysis_types), 8)) as executor:
        future_to_analysis = {
            executor.submit(self.analyzers[atype].analyze, stock_code, **kwargs): atype
            for atype in analysis_types
            if atype in self.analyzers
        }

        for future in concurrent.futures.as_completed(future_to_analysis):
            analysis_type = future_to_analysis[future]
            try:
                result = future.result()
                results[analysis_type] = result
            except Exception as e:
                print(f"GPU analysis {analysis_type.value} failed: {e}")
                results[analysis_type] = None

    return results


def _sequential_analysis(
    self, analysis_types: List[AnalysisType], stock_code: str, **kwargs
) -> Dict[AnalysisType, Any]:
    """顺序执行各维度分析"""
    analysis_results = {}
    for analysis_type in analysis_types:
        if analysis_type in self.analyzers:
            try:
                analyzer = self.analyzers[analysis_type]
                result = analyzer.analyze(stock_code, **kwargs)
                analysis_results[analysis_type] = result
            except Exception as e:
                print(f"Error analyzing {analysis_type.value} for {stock_code}: {e}")
                analysis_results[analysis_type] = None

    return analysis_results


def _convert_to_radar_dimension(
    self, analysis_type: AnalysisType, result: AnalysisResult, weight: float
) -> RadarDimension:
    """
    将分析结果转换为雷达维度

    Args:
        analysis_type: 分析类型
        result: 分析结果
        weight: 权重

    Returns:
        RadarDimension: 雷达维度
    """
    # 计算维度评分（基于scores的平均值）
    if result.scores:
        score = np.mean(list(result.scores.values())) * 100  # 转换为0-100分
        score = min(max(score, 0), 100)  # 确保在0-100范围内
    else:
        score = 50.0  # 默认中性评分

    # 确定风险等级
    risk_level = self._determine_risk_level(score)

    # 提取关键指标
    key_metrics = self._extract_key_metrics(analysis_type, result)

    return RadarDimension(
        name=analysis_type.value,
        score=score,
        weight=weight,
        analysis_type=analysis_type,
        key_metrics=key_metrics,
        signals=result.signals[:5] if result.signals else [],  # 限制信号数量
        risk_level=risk_level,
    )


def _calculate_overall_score(self, dimensions: List[RadarDimension]) -> float:
    """计算综合评分"""
    if not dimensions:
        return 50.0

    # GPU加速版本
    if GPU_AVAILABLE and self.gpu_manager and len(dimensions) > 5:
        try:
            return self._calculate_overall_score_gpu(dimensions)
        except Exception as e:
            print(f"GPU score calculation failed, falling back to CPU: {e}")

    # CPU版本
    total_weight = sum(dim.weight for dim in dimensions)
    if total_weight == 0:
        return 50.0

    weighted_score = sum(dim.score * dim.weight for dim in dimensions)
    return weighted_score / total_weight


def _calculate_overall_score_gpu(self, dimensions: List[RadarDimension]) -> float:
    """GPU加速的综合评分计算"""
    import cudf
    import numpy as np

    # 将维度数据转换为GPU DataFrame
    scores = cudf.Series([dim.score for dim in dimensions])
    weights = cudf.Series([dim.weight for dim in dimensions])

    # GPU并行计算
    total_weight = weights.sum()
    if total_weight == 0:
        return 50.0

    weighted_score = (scores * weights).sum()
    return float(weighted_score / total_weight)


def _determine_risk_level(self, score: float) -> str:
    """确定风险等级"""
    if score >= 80:
        return "low"
    elif score >= 60:
        return "medium"
    elif score >= 40:
        return "high"
    else:
        return "extreme"


def _extract_key_metrics(self, analysis_type: AnalysisType, result: AnalysisResult) -> Dict[str, Any]:
    """提取关键指标"""
    key_metrics = {}

    # 根据分析类型提取不同的关键指标
    if analysis_type == AnalysisType.FUNDAMENTAL and result.scores:
        key_metrics = {
            "profitability_score": result.scores.get("profitability", 0),
            "solvency_score": result.scores.get("solvency", 0),
            "growth_score": result.scores.get("growth", 0),
        }
    elif analysis_type == AnalysisType.TECHNICAL and result.scores:
        key_metrics = {
            "trend_score": result.scores.get("trend", 0),
            "momentum_score": result.scores.get("momentum", 0),
            "volatility_score": result.scores.get("volatility", 0),
        }
    elif analysis_type == AnalysisType.TRADING_SIGNALS:
        key_metrics = {
            "signal_count": len(result.signals) if result.signals else 0,
            "bullish_signals": (
                len([s for s in result.signals if s.get("direction") == "bullish"]) if result.signals else 0
            ),
            "bearish_signals": (
                len([s for s in result.signals if s.get("direction") == "bearish"]) if result.signals else 0
            ),
        }
    # 为其他分析类型添加关键指标提取逻辑...

    return key_metrics


def _extract_insights(self, dimension: RadarDimension) -> List[str]:
    """提取维度洞察"""
    insights = []

    score = dimension.score
    name = dimension.name

    if score >= 80:
        insights.append(f"{name}表现优秀，评分{score:.1f}分")
    elif score >= 60:
        insights.append(f"{name}表现良好，评分{score:.1f}分")
    elif score >= 40:
        insights.append(f"{name}表现一般，评分{score:.1f}分，需要关注")
    else:
        insights.append(f"{name}表现较差，评分{score:.1f}分，存在风险")

    # 基于风险等级添加洞察
    if dimension.risk_level == "extreme":
        insights.append(f"{name}风险极高，建议谨慎操作")
    elif dimension.risk_level == "high":
        insights.append(f"{name}风险较高，需要重点关注")

    return insights


def _generate_radar_chart_data(self, dimensions: List[RadarDimension]) -> Dict[str, Any]:
    """生成雷达图数据"""
    # GPU优化：对大量维度数据进行排序
    if GPU_AVAILABLE and self.gpu_manager and len(dimensions) > 8:
        try:
            return self._generate_radar_chart_data_gpu(dimensions)
        except Exception as e:
            print(f"GPU radar chart generation failed, falling back to CPU: {e}")

    # CPU版本
    labels = [dim.name for dim in dimensions]
    values = [dim.score for dim in dimensions]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "多维度评分",
                "data": values,
                "fill": True,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 2,
                "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(54, 162, 235, 1)",
            }
        ],
        "options": {
            "scales": {
                "r": {
                    "angleLines": {"display": True},
                    "suggestedMin": 0,
                    "suggestedMax": 100,
                    "ticks": {"stepSize": 20},
                }
            },
            "plugins": {
                "legend": {"display": True},
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.label + ': ' + context.parsed.r + '分'; }"
                    }
                },
            },
        },
    }


def _generate_radar_chart_data_gpu(self, dimensions: List[RadarDimension]) -> Dict[str, Any]:
    """GPU加速的雷达图数据生成"""
    import cudf
    import numpy as np

    # 将数据转换为GPU DataFrame进行排序优化
    df = cudf.DataFrame(
        {
            "name": [dim.name for dim in dimensions],
            "score": [dim.score for dim in dimensions],
            "weight": [dim.weight for dim in dimensions],
        }
    )

    # GPU排序：按权重降序排列维度
    df_sorted = df.sort_values("weight", ascending=False)
    labels = df_sorted["name"].to_pandas().tolist()
    values = df_sorted["score"].to_pandas().tolist()

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "多维度评分 (GPU优化)",
                "data": values,
                "fill": True,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 2,
                "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(54, 162, 235, 1)",
            }
        ],
        "options": {
            "scales": {
                "r": {
                    "angleLines": {"display": True},
                    "suggestedMin": 0,
                    "suggestedMax": 100,
                    "ticks": {"stepSize": 20},
                }
            },
            "plugins": {
                "legend": {"display": True},
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.label + ': ' + context.parsed.r + '分 (GPU)'; }"
                    }
                },
            },
        },
    }

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "多维度评分 (GPU优化)",
                "data": values,
                "fill": True,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 2,
                "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(54, 162, 235, 1)",
            }
        ],
        "options": {
            "scales": {
                "r": {
                    "angleLines": {"display": True},
                    "suggestedMin": 0,
                    "suggestedMax": 100,
                    "ticks": {"stepSize": 20},
                }
            },
            "plugins": {
                "legend": {"display": True},
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.label + ': ' + context.parsed.r + '分 (GPU)'; }"
                    }
                },
            },
        },
    }

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "多维度评分",
                "data": values,
                "fill": True,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 2,
                "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(54, 162, 235, 1)",
            }
        ],
        "options": {
            "scales": {
                "r": {
                    "angleLines": {"display": True},
                    "suggestedMin": 0,
                    "suggestedMax": 100,
                    "ticks": {"stepSize": 20},
                }
            },
            "plugins": {
                "legend": {"display": True},
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.label + ': ' + context.parsed.r + '分'; }"
                    }
                },
            },
        },
    }


def _assess_overall_risk_from_dimensions(self, dimensions: List[RadarDimension]) -> Dict[str, Any]:
    """基于维度列表评估整体风险"""
    # 计算各风险等级的数量
    risk_counts = {"low": 0, "medium": 0, "high": 0, "extreme": 0}
    for dim in dimensions:
        risk_counts[dim.risk_level] += 1

    # 确定整体风险等级
    if risk_counts["extreme"] > 0:
        overall_risk = "extreme"
    elif risk_counts["high"] >= len(dimensions) * 0.3:  # 30%以上维度为高风险
        overall_risk = "high"
    elif risk_counts["medium"] >= len(dimensions) * 0.5:  # 50%以上维度为中等风险
        overall_risk = "medium"
    else:
        overall_risk = "low"

    return {
        "overall_risk_level": overall_risk,
        "risk_distribution": risk_counts,
        "risk_description": self.risk_levels[overall_risk]["description"],
        "high_risk_dimensions": [dim.name for dim in dimensions if dim.risk_level in ["high", "extreme"]],
    }


def _assess_overall_risk(self, radar_result: RadarAnalysisResult) -> Dict[str, Any]:
    """评估整体风险"""
    dimensions = radar_result.dimensions

    # 计算各风险等级的数量
    risk_counts = {"low": 0, "medium": 0, "high": 0, "extreme": 0}
    for dim in dimensions:
        risk_counts[dim.risk_level] += 1

    # 确定整体风险等级
    if risk_counts["extreme"] > 0:
        overall_risk = "extreme"
    elif risk_counts["high"] >= len(dimensions) * 0.3:  # 30%以上维度为高风险
        overall_risk = "high"
    elif risk_counts["medium"] >= len(dimensions) * 0.5:  # 50%以上维度为中等风险
        overall_risk = "medium"
    else:
        overall_risk = "low"

    return {
        "overall_risk_level": overall_risk,
        "risk_distribution": risk_counts,
        "risk_description": self.risk_levels[overall_risk]["description"],
        "high_risk_dimensions": [dim.name for dim in dimensions if dim.risk_level in ["high", "extreme"]],
    }


def _assess_risk(self, radar_result: RadarAnalysisResult) -> Dict[str, Any]:
    """风险评估（兼容现有接口）"""
    return self._assess_overall_risk(radar_result)


def _aggregate_signals(self, dimensions: List[RadarDimension]) -> List[Dict[str, Any]]:
    """聚合所有维度的信号"""
    all_signals = []
    for dim in dimensions:
        all_signals.extend(dim.signals)

    # 按重要性排序（假设信号有score字段）
    all_signals.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 返回前10个最重要的信号
    return all_signals[:10]


def _generate_recommendation(self, overall_score: float, risk_assessment: Dict[str, Any]) -> str:
    """生成投资建议"""
    risk_level = risk_assessment.get("overall_risk_level", "medium")

    if overall_score >= 80 and risk_level == "low":
        return "强烈推荐买入"
    elif overall_score >= 70 and risk_level in ["low", "medium"]:
        return "推荐买入"
    elif overall_score >= 60 and risk_level != "extreme":
        return "谨慎买入"
    elif overall_score >= 40:
        return "观望"
    elif overall_score >= 20:
        return "谨慎卖出"
    else:
        return "建议卖出"


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.MULTIDIMENSIONAL_RADAR,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": 0.0},
        signals=[],
        recommendations={"error": error_msg},
        risk_assessment={"error": "Analysis failed"},
        metadata={"error": True},
        raw_data=None,
    )
