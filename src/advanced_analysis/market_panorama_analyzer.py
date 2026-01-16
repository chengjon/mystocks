"""
Market Panorama Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台市场全景分析功能

This module provides comprehensive market panorama analysis including:
- Capital flow analysis across market segments
- Trading activity and volume analysis
- Trend analysis across different market levels
- Market valuation distribution analysis
- Dynamic market sentiment indicators
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

# GPU acceleration support
try:
    import cudf
    import cuml

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Market panorama analysis will run on CPU.")


@dataclass
class CapitalFlowData:
    """资金流向数据"""

    main_inflow: float  # 主力流入
    main_outflow: float  # 主力流出
    retail_inflow: float  # 散户流入
    retail_outflow: float  # 散户流出
    net_flow: float  # 净流入
    flow_ratio: float  # 资金流向比例
    concentration: float  # 资金集中度


@dataclass
class TradingActivityData:
    """交易活跃度数据"""

    volume_ratio: float  # 成交量比例
    turnover_rate: float  # 换手率
    activity_score: float  # 活跃度评分
    momentum_score: float  # 动量评分
    participation_rate: float  # 参与率


@dataclass
class TrendAnalysisData:
    """趋势分析数据"""

    market_trend: str  # 市场趋势
    sector_rotation: Dict[str, float]  # 板块轮动
    leadership_change: List[str]  # 领涨板块变化
    trend_strength: float  # 趋势强度
    reversal_probability: float  # 反转概率


@dataclass
class ValuationDistribution:
    """估值分布数据"""

    pe_distribution: Dict[str, float]  # PE分布分位数
    pb_distribution: Dict[str, float]  # PB分布分位数
    valuation_extremes: Dict[str, List[str]]  # 估值极值股票
    sector_valuation: Dict[str, float]  # 板块估值
    market_valuation_percentile: float  # 市场整体估值分位数


@dataclass
class MarketSentiment:
    """市场情绪数据"""

    sentiment_index: float  # 情绪指数
    fear_greed_index: float  # 恐惧贪婪指数
    put_call_ratio: float  # 认沽认购比
    vix_level: float  # 波动率指数
    sentiment_trend: str  # 情绪趋势


class MarketPanoramaAnalyzer(BaseAnalyzer):
    """
    市场全景分析器

    提供全面的市场全景分析，包括：
    - 资金流向全景分析
    - 交易活跃度全景分析
    - 市场趋势全景分析
    - 估值分布全景分析
    - 市场情绪动态分析
    """


def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    # 市场指数配置
    self.market_indices = {
        "000001": "上证指数",
        "399001": "深证成指",
        "399006": "创业板指",
        "000300": "沪深300",
        "000905": "中证500",
        "000852": "中证1000",
    }

    # 板块分类
    self.sectors = {
        "finance": ["银行", "证券", "保险"],
        "technology": ["电子", "计算机", "通信"],
        "consumer": ["食品饮料", "家用电器", "汽车"],
        "healthcare": ["医药生物", "医疗器械"],
        "energy": ["煤炭", "石油石化"],
        "materials": ["有色金属", "化工", "钢铁"],
        "industrials": ["机械设备", "电气设备"],
    }

    # 分析时间窗口
    self.analysis_windows = {
        "short_term": 5,  # 短期：5天
        "medium_term": 20,  # 中期：20天
        "long_term": 60,  # 长期：60天
    }


def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """
    执行市场全景分析

    Args:
        stock_code: 股票代码 (此分析器分析整个市场，不针对特定股票)
        **kwargs: 额外参数

    Returns:
        AnalysisResult: 分析结果
    """
    try:
        # 市场全景分析不针对特定股票，而是分析整体市场状况
        market_data = self.analyze_market_overview()

        # 转换结果为标准格式
        scores = {}
        signals = []
        recommendations = {
            "market_health_score": market_data.get("market_health_score", 0.0),
            "market_status": market_data.get("market_status", "unknown"),
            "key_insights": market_data.get("key_insights", []),
        }
        risk_assessment = {
            "market_risk_level": "medium",  # 基于健康度评分确定
            "market_condition": market_data.get("market_status", "unknown"),
        }

        # 如果有资金流向数据，提取一些关键指标作为评分
        if "capital_flow" in market_data:
            capital_flow = market_data["capital_flow"]
            if "market_summary" in capital_flow:
                flow_summary = capital_flow["market_summary"]
                scores["capital_flow_intensity"] = 1.0 if flow_summary.get("flow_intensity") == "strong" else 0.5
                scores["capital_flow_status"] = 1.0 if flow_summary.get("flow_status") == "资金净流入" else 0.0

        return AnalysisResult(
            analysis_type=AnalysisType.MARKET_PANORAMA,
            stock_code=stock_code,  # 虽然不针对特定股票，但保持接口一致性
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata={
                "analysis_scope": "market_wide",
                "data_sources": ["market_indices", "capital_flow", "trading_activity"],
                "analysis_period": "current_market_conditions",
            },
            raw_data=None,
        )

    except Exception as e:
        print(f"Error in market panorama analysis: {e}")
        return AnalysisResult(
            analysis_type=AnalysisType.MARKET_PANORAMA,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores={"error": 0.0},
            signals=[],
            recommendations={"error": str(e)},
            risk_assessment={"error": "Analysis failed"},
            metadata={"error": True},
            raw_data=None,
        )


def analyze_market_overview(self) -> Dict[str, Any]:
    """
    获取市场全景分析总览

    Returns:
        包含所有市场全景分析数据的字典
    """
    try:
        # 资金流向分析
        capital_flow = self._analyze_capital_flow()

        # 交易活跃度分析
        trading_activity = self._analyze_trading_activity()

        # 趋势分析
        trend_analysis = self._analyze_market_trends()

        # 估值分布分析
        valuation_distribution = self._analyze_valuation_distribution()

        # 市场情绪分析
        market_sentiment = self._analyze_market_sentiment()

        # 综合市场健康度评分
        market_health_score = self._calculate_market_health_score(
            capital_flow, trading_activity, trend_analysis, valuation_distribution, market_sentiment
        )

        return {
            "timestamp": datetime.now(),
            "market_health_score": market_health_score,
            "capital_flow": capital_flow,
            "trading_activity": trading_activity,
            "trend_analysis": trend_analysis,
            "valuation_distribution": valuation_distribution,
            "market_sentiment": market_sentiment,
            "market_status": self._determine_market_status(market_health_score),
            "key_insights": self._generate_market_insights(
                capital_flow, trading_activity, trend_analysis, valuation_distribution, market_sentiment
            ),
        }

    except Exception as e:
        print(f"Error in market overview analysis: {e}")
        return {"error": str(e), "timestamp": datetime.now(), "market_health_score": 0.0}


def _analyze_capital_flow(self) -> Dict[str, Any]:
    """分析资金流向"""
    try:
        capital_flow_data = {}

        # 获取市场整体资金流向数据
        for index_code, index_name in self.market_indices.items():
            try:
                # 获取资金流向数据（这里需要从数据源获取实际的资金流向数据）
                # 暂时使用模拟数据
                flow_data = self._get_capital_flow_data(index_code)

                capital_flow_data[index_name] = {
                    "main_inflow": flow_data.main_inflow,
                    "main_outflow": flow_data.main_outflow,
                    "retail_inflow": flow_data.retail_inflow,
                    "retail_outflow": flow_data.retail_outflow,
                    "net_flow": flow_data.net_flow,
                    "flow_ratio": flow_data.flow_ratio,
                    "concentration": flow_data.concentration,
                }

            except Exception as e:
                print(f"Error analyzing capital flow for {index_name}: {e}")
                continue

        # 计算市场整体资金流向
        if capital_flow_data:
            total_net_flow = sum(data["net_flow"] for data in capital_flow_data.values())
            avg_concentration = np.mean([data["concentration"] for data in capital_flow_data.values()])

            market_flow_status = "资金净流入" if total_net_flow > 0 else "资金净流出"
            flow_intensity = (
                "strong"
                if abs(total_net_flow) > 1000000000
                else "moderate" if abs(total_net_flow) > 500000000 else "weak"
            )

            capital_flow_data["market_summary"] = {
                "total_net_flow": total_net_flow,
                "avg_concentration": avg_concentration,
                "flow_status": market_flow_status,
                "flow_intensity": flow_intensity,
                "dominant_force": "主力资金" if avg_concentration > 0.6 else "散户资金",
            }

        return capital_flow_data

    except Exception as e:
        print(f"Error in capital flow analysis: {e}")
        return {}


def _analyze_trading_activity(self) -> Dict[str, Any]:
    """分析交易活跃度"""
    try:
        activity_data = {}

        for index_code, index_name in self.market_indices.items():
            try:
                # 获取交易数据
                trading_data = self._get_trading_activity_data(index_code)

                activity_data[index_name] = {
                    "volume_ratio": trading_data.volume_ratio,
                    "turnover_rate": trading_data.turnover_rate,
                    "activity_score": trading_data.activity_score,
                    "momentum_score": trading_data.momentum_score,
                    "participation_rate": trading_data.participation_rate,
                }

            except Exception as e:
                print(f"Error analyzing trading activity for {index_name}: {e}")
                continue

        # 计算市场活跃度综合指标
        if activity_data:
            avg_activity_score = np.mean([data["activity_score"] for data in activity_data.values()])
            avg_momentum_score = np.mean([data["momentum_score"] for data in activity_data.values()])
            avg_participation = np.mean([data["participation_rate"] for data in activity_data.values()])

            # 确定市场活跃度水平
            if avg_activity_score > 0.8 and avg_participation > 0.7:
                activity_level = "极度活跃"
            elif avg_activity_score > 0.6 and avg_participation > 0.5:
                activity_level = "较为活跃"
            elif avg_activity_score > 0.4:
                activity_level = "一般活跃"
            else:
                activity_level = "低迷"

            activity_data["market_summary"] = {
                "avg_activity_score": avg_activity_score,
                "avg_momentum_score": avg_momentum_score,
                "avg_participation_rate": avg_participation,
                "activity_level": activity_level,
                "momentum_trend": "上涨动能" if avg_momentum_score > 0.5 else "下跌动能",
            }

        return activity_data

    except Exception as e:
        print(f"Error in trading activity analysis: {e}")
        return {}


def _analyze_market_trends(self) -> Dict[str, Any]:
    """分析市场趋势"""
    try:
        trend_data = {}

        # 分析主要指数趋势
        for index_code, index_name in self.market_indices.items():
            try:
                # 获取历史数据进行趋势分析
                data = self._get_historical_data(index_code, days=60, data_type="daily")

                if not data.empty:
                    trend_analysis = self._calculate_index_trend(data)
                    trend_data[index_name] = {
                        "trend": trend_analysis["market_trend"],
                        "strength": trend_analysis["trend_strength"],
                        "reversal_probability": trend_analysis["reversal_probability"],
                    }

            except Exception as e:
                print(f"Error analyzing trend for {index_name}: {e}")
                continue

        # 板块轮动分析
        sector_rotation = self._analyze_sector_rotation()

        # 领涨板块分析
        leadership_changes = self._analyze_leadership_changes()

        # 综合趋势分析
        if trend_data:
            uptrend_count = sum(1 for data in trend_data.values() if data["trend"] == "uptrend")
            downtrend_count = sum(1 for data in trend_data.values() if data["trend"] == "downtrend")

            if uptrend_count > downtrend_count:
                market_trend = "uptrend"
            elif downtrend_count > uptrend_count:
                market_trend = "downtrend"
            else:
                market_trend = "sideways"

            avg_trend_strength = np.mean([data["strength"] for data in trend_data.values()])

            trend_data["market_summary"] = {
                "overall_trend": market_trend,
                "avg_trend_strength": avg_trend_strength,
                "consistency_ratio": max(uptrend_count, downtrend_count) / len(trend_data),
                "sector_rotation": sector_rotation,
                "leadership_changes": leadership_changes,
            }

        return trend_data

    except Exception as e:
        print(f"Error in market trend analysis: {e}")
        return {}


def _analyze_valuation_distribution(self) -> Dict[str, Any]:
    """分析估值分布"""
    try:
        valuation_data = {}

        # 分析主要指数估值分布
        for index_code, index_name in self.market_indices.items():
            try:
                # 获取指数成分股权值数据
                pe_dist, pb_dist = self._get_valuation_distribution(index_code)

                valuation_data[index_name] = {
                    "pe_distribution": pe_dist,
                    "pb_distribution": pb_dist,
                    "valuation_percentile": self._calculate_market_valuation_percentile(pe_dist, pb_dist),
                }

            except Exception as e:
                print(f"Error analyzing valuation for {index_name}: {e}")
                continue

        # 板块估值分析
        sector_valuations = self._analyze_sector_valuations()

        # 估值极值分析
        valuation_extremes = self._identify_valuation_extremes()

        # 市场整体估值评估
        if valuation_data:
            avg_percentile = np.mean([data["valuation_percentile"] for data in valuation_data.values()])

            if avg_percentile > 0.8:
                valuation_level = "显著高估"
            elif avg_percentile > 0.6:
                valuation_level = "相对高估"
            elif avg_percentile > 0.4:
                valuation_level = "合理估值"
            elif avg_percentile > 0.2:
                valuation_level = "相对低估"
            else:
                valuation_level = "显著低估"

            valuation_data["market_summary"] = {
                "avg_valuation_percentile": avg_percentile,
                "valuation_level": valuation_level,
                "sector_valuations": sector_valuations,
                "valuation_extremes": valuation_extremes,
            }

        return valuation_data

    except Exception as e:
        print(f"Error in valuation distribution analysis: {e}")
        return {}


def _analyze_market_sentiment(self) -> Dict[str, Any]:
    """分析市场情绪"""
    try:
        # 情绪指标计算
        sentiment_index = self._calculate_sentiment_index()
        fear_greed_index = self._calculate_fear_greed_index()
        put_call_ratio = self._get_put_call_ratio()
        vix_level = self._get_vix_level()

        # 情绪趋势分析
        sentiment_trend = self._analyze_sentiment_trend(sentiment_index, fear_greed_index)

        # 情绪解读
        if sentiment_index > 0.7:
            sentiment_level = "极度乐观"
            risk_level = "high"
        elif sentiment_index > 0.6:
            sentiment_level = "乐观"
            risk_level = "medium"
        elif sentiment_index > 0.4:
            sentiment_level = "中性"
            risk_level = "low"
        elif sentiment_index > 0.3:
            sentiment_level = "谨慎"
            risk_level = "medium"
        else:
            sentiment_level = "极度悲观"
            risk_level = "high"

        return {
            "sentiment_index": sentiment_index,
            "fear_greed_index": fear_greed_index,
            "put_call_ratio": put_call_ratio,
            "vix_level": vix_level,
            "sentiment_trend": sentiment_trend,
            "sentiment_level": sentiment_level,
            "risk_level": risk_level,
        }

    except Exception as e:
        print(f"Error in market sentiment analysis: {e}")
        return {"sentiment_index": 0.5, "error": str(e)}


def _calculate_market_health_score(
    self,
    capital_flow: Dict,
    trading_activity: Dict,
    trend_analysis: Dict,
    valuation_distribution: Dict,
    market_sentiment: Dict,
) -> float:
    """计算市场健康度综合评分"""
    try:
        scores = []

        # 资金流向评分 (权重: 0.25)
        if "market_summary" in capital_flow:
            flow_status = capital_flow["market_summary"]
            if flow_status["flow_intensity"] == "strong" and flow_status["flow_status"] == "资金净流入":
                scores.append(0.25 * 0.9)  # 强势流入，评分高
            elif flow_status["flow_status"] == "资金净流入":
                scores.append(0.25 * 0.7)  # 温和流入
            else:
                scores.append(0.25 * 0.3)  # 资金流出

        # 交易活跃度评分 (权重: 0.20)
        if "market_summary" in trading_activity:
            activity = trading_activity["market_summary"]
            activity_score = activity["avg_activity_score"] * 0.2
            scores.append(activity_score)

        # 趋势一致性评分 (权重: 0.20)
        if "market_summary" in trend_analysis:
            trend_consistency = trend_analysis["market_summary"]["consistency_ratio"] * 0.2
            scores.append(trend_consistency)

        # 估值合理性评分 (权重: 0.20)
        if "market_summary" in valuation_distribution:
            valuation_percentile = valuation_distribution["market_summary"]["avg_valuation_percentile"]
            # 估值越合理（接近0.5）评分越高
            valuation_score = (1 - abs(valuation_percentile - 0.5) * 2) * 0.2
            scores.append(max(0, valuation_score))

        # 市场情绪评分 (权重: 0.15)
        sentiment_score = market_sentiment.get("sentiment_index", 0.5)
        # 情绪过于极端（太乐观或太悲观）会降低评分
        sentiment_penalty = abs(sentiment_score - 0.5) * 0.3
        emotion_score = (0.5 - sentiment_penalty) * 2 * 0.15
        scores.append(max(0, emotion_score))

        return min(1.0, sum(scores))

    except Exception as e:
        print(f"Error calculating market health score: {e}")
        return 0.5


def _determine_market_status(self, health_score: float) -> str:
    """确定市场状态"""
    if health_score > 0.8:
        return "健康乐观"
    elif health_score > 0.6:
        return "相对健康"
    elif health_score > 0.4:
        return "一般状态"
    elif health_score > 0.2:
        return "偏弱状态"
    else:
        return "疲弱状态"


def _generate_market_insights(
    self,
    capital_flow: Dict,
    trading_activity: Dict,
    trend_analysis: Dict,
    valuation_distribution: Dict,
    market_sentiment: Dict,
) -> List[str]:
    """生成市场洞察"""
    insights = []

    try:
        # 资金流向洞察
        if "market_summary" in capital_flow:
            flow_data = capital_flow["market_summary"]
            if flow_data["flow_status"] == "资金净流入" and flow_data["flow_intensity"] == "strong":
                insights.append("资金大幅净流入，市场做多情绪浓厚")
            elif flow_data["flow_status"] == "资金净流出":
                insights.append("资金持续净流出，市场风险偏好下降")

        # 交易活跃度洞察
        if "market_summary" in trading_activity:
            activity_data = trading_activity["market_summary"]
            if activity_data["activity_level"] == "极度活跃":
                insights.append("市场交易极为活跃，投资者参与度高")
            elif activity_data["activity_level"] == "低迷":
                insights.append("市场交易低迷，投资者观望情绪较重")

        # 趋势洞察
        if "market_summary" in trend_analysis:
            trend_data = trend_analysis["market_summary"]
            if trend_data["consistency_ratio"] > 0.8:
                insights.append("各主要指数趋势高度一致，市场整体方向明确")
            else:
                insights.append("各指数走势分化，市场面临选择方向的压力")

        # 估值洞察
        if "market_summary" in valuation_distribution:
            valuation_data = valuation_distribution["market_summary"]
            if valuation_data["valuation_level"] == "显著高估":
                insights.append("市场整体估值显著高估，风险较高")
            elif valuation_data["valuation_level"] == "显著低估":
                insights.append("市场整体估值显著低估，机会较多")

        # 情绪洞察
        sentiment_level = market_sentiment.get("sentiment_level", "中性")
        if sentiment_level in ["极度乐观", "极度悲观"]:
            insights.append(f"市场情绪{sentiment_level}，可能存在情绪过激风险")

    except Exception as e:
        print(f"Error generating market insights: {e}")

    return insights


# 辅助方法 - 数据获取
def _get_capital_flow_data(self, index_code: str) -> CapitalFlowData:
    """获取资金流向数据"""
    # 使用工厂模式获取数据源，由环境变量决定使用mock还是真实数据
    from src.data_sources.factory import get_timeseries_source

    timeseries_source = get_timeseries_source()

    # 这里应该调用真实的数据源API
    # 暂时使用随机数据作为示例，实际实现会从数据源获取
    np.random.seed(int(index_code) if index_code.isdigit() else 42)

    main_inflow = np.random.uniform(1000000, 50000000)
    main_outflow = np.random.uniform(800000, 40000000)
    retail_inflow = np.random.uniform(500000, 20000000)
    retail_outflow = np.random.uniform(400000, 18000000)

    net_flow = (main_inflow + retail_inflow) - (main_outflow + retail_outflow)
    total_flow = main_inflow + main_outflow + retail_inflow + retail_outflow
    flow_ratio = net_flow / total_flow if total_flow > 0 else 0

    # 资金集中度：主力资金占比
    main_total = main_inflow + main_outflow
    total_all = main_total + retail_inflow + retail_outflow
    concentration = main_total / total_all if total_all > 0 else 0

    return CapitalFlowData(
        main_inflow=main_inflow,
        main_outflow=main_outflow,
        retail_inflow=retail_inflow,
        retail_outflow=retail_outflow,
        net_flow=net_flow,
        flow_ratio=flow_ratio,
        concentration=concentration,
    )


def _get_trading_activity_data(self, index_code: str) -> TradingActivityData:
    """获取交易活跃度数据"""
    np.random.seed(int(index_code) if index_code.isdigit() else 42)

    volume_ratio = np.random.uniform(0.8, 1.5)
    turnover_rate = np.random.uniform(0.5, 3.0)
    activity_score = min(1.0, (volume_ratio * turnover_rate) / 2)
    momentum_score = np.random.uniform(0.3, 0.8)
    participation_rate = np.random.uniform(0.4, 0.9)

    return TradingActivityData(
        volume_ratio=volume_ratio,
        turnover_rate=turnover_rate,
        activity_score=activity_score,
        momentum_score=momentum_score,
        participation_rate=participation_rate,
    )


def _calculate_index_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
    """计算指数趋势"""
    if data.empty or len(data) < 10:
        return {"market_trend": "unknown", "trend_strength": 0.0, "reversal_probability": 0.5}

    try:
        prices = data["close"].values
        short_ma = pd.Series(prices).rolling(window=5).mean()
        long_ma = pd.Series(prices).rolling(window=20).mean()

        if len(short_ma) < 2 or len(long_ma) < 2:
            return {"market_trend": "unknown", "trend_strength": 0.0, "reversal_probability": 0.5}

        # 趋势方向
        current_short = short_ma.iloc[-1]
        current_long = long_ma.iloc[-1]

        if current_short > current_long * 1.01:
            trend = "uptrend"
        elif current_short < current_long * 0.99:
            trend = "downtrend"
        else:
            trend = "sideways"

        # 趋势强度
        trend_slope = np.polyfit(range(len(long_ma.dropna())), long_ma.dropna(), 1)[0]
        strength = min(abs(trend_slope) * 1000, 1.0)

        # 反转概率（基于趋势持续时间和强度）
        trend_duration = len(
            [
                x
                for x in long_ma.dropna()
                if (x > long_ma.dropna().iloc[0] * 1.05) or (x < long_ma.dropna().iloc[0] * 0.95)
            ]
        )
        reversal_prob = min(trend_duration / len(long_ma.dropna()) * 0.8, 0.9)

        return {"market_trend": trend, "trend_strength": strength, "reversal_probability": reversal_prob}

    except Exception as e:
        print(f"Error calculating index trend: {e}")
        return {"market_trend": "unknown", "trend_strength": 0.0, "reversal_probability": 0.5}


def _analyze_sector_rotation(self) -> Dict[str, float]:
    """分析板块轮动"""
    # 简化的板块轮动分析
    sector_performance = {}
    for sector_name in self.sectors.keys():
        # 模拟板块表现
        performance = np.random.uniform(-0.05, 0.08)
        sector_performance[sector_name] = performance

    return sector_performance


def _analyze_leadership_changes(self) -> List[str]:
    """分析领涨板块变化"""
    # 简化的领涨板块分析
    sectors = list(self.sectors.keys())
    leadership = np.random.choice(sectors, size=3, replace=False)
    return leadership.tolist()


def _get_valuation_distribution(self, index_code: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """获取模拟估值分布数据"""
    np.random.seed(int(index_code) if index_code.isdigit() else 42)

    pe_distribution = {
        "p10": np.random.uniform(10, 15),
        "p25": np.random.uniform(15, 20),
        "p50": np.random.uniform(20, 25),
        "p75": np.random.uniform(25, 35),
        "p90": np.random.uniform(35, 50),
    }

    pb_distribution = {
        "p10": np.random.uniform(0.8, 1.2),
        "p25": np.random.uniform(1.2, 1.5),
        "p50": np.random.uniform(1.5, 2.0),
        "p75": np.random.uniform(2.0, 2.5),
        "p90": np.random.uniform(2.5, 3.5),
    }

    return pe_distribution, pb_distribution


def _calculate_market_valuation_percentile(self, pe_dist: Dict, pb_dist: Dict) -> float:
    """计算市场估值分位数"""
    # 简化的估值分位数计算
    pe_median = pe_dist.get("p50", 25)
    pb_median = pb_dist.get("p50", 2.0)

    # 基于历史数据估算分位数
    pe_percentile = min(pe_median / 30, 1.0)  # 假设30是历史高点
    pb_percentile = min(pb_median / 3.0, 1.0)  # 假设3.0是历史高点

    return (pe_percentile + pb_percentile) / 2


def _analyze_sector_valuations(self) -> Dict[str, float]:
    """分析板块估值"""
    sector_valuations = {}
    for sector_name in self.sectors.keys():
        valuation = np.random.uniform(0.3, 0.9)  # 估值分位数
        sector_valuations[sector_name] = valuation

    return sector_valuations


def _identify_valuation_extremes(self) -> Dict[str, List[str]]:
    """识别估值极值"""
    return {
        "overvalued": ["股票A", "股票B"],  # 高估股票
        "undervalued": ["股票C", "股票D"],  # 低估股票
    }


def _calculate_sentiment_index(self) -> float:
    """计算情绪指数"""
    # 基于交易量、波动率等指标计算情绪
    return np.random.uniform(0.2, 0.8)


def _calculate_fear_greed_index(self) -> float:
    """计算恐惧贪婪指数"""
    return np.random.uniform(0.1, 0.9)


def _get_put_call_ratio(self) -> float:
    """获取认沽认购比"""
    return np.random.uniform(0.8, 1.3)


def _get_vix_level(self) -> float:
    """获取波动率指数水平"""
    return np.random.uniform(10, 40)


def _analyze_sentiment_trend(self, sentiment_index: float, fear_greed_index: float) -> str:
    """分析情绪趋势"""
    if sentiment_index > 0.6 and fear_greed_index > 0.6:
        return "乐观情绪上升"
    elif sentiment_index < 0.4 and fear_greed_index < 0.4:
        return "悲观情绪加深"
    else:
        return "情绪相对稳定"
