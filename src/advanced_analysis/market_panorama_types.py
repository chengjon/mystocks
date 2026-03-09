"""
市场全景分析共享数据类型。
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CapitalFlowData:
    """资金流向数据"""

    main_inflow: float
    main_outflow: float
    retail_inflow: float
    retail_outflow: float
    net_flow: float
    flow_ratio: float
    concentration: float


@dataclass
class TradingActivityData:
    """交易活跃度数据"""

    volume_ratio: float
    turnover_rate: float
    activity_score: float
    momentum_score: float
    participation_rate: float


@dataclass
class TrendAnalysisData:
    """趋势分析数据"""

    market_trend: str
    sector_rotation: Dict[str, float]
    leadership_change: List[str]
    trend_strength: float
    reversal_probability: float


@dataclass
class ValuationDistribution:
    """估值分布数据"""

    pe_distribution: Dict[str, float]
    pb_distribution: Dict[str, float]
    valuation_extremes: Dict[str, List[str]]
    sector_valuation: Dict[str, float]
    market_valuation_percentile: float


@dataclass
class MarketSentiment:
    """市场情绪数据"""

    sentiment_index: float
    fear_greed_index: float
    put_call_ratio: float
    vix_level: float
    sentiment_trend: str
