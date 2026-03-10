"""
Capital flow analysis data models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


@dataclass
class CapitalFlowCluster:
    """资金流向聚类结果。"""

    cluster_id: int
    cluster_size: int
    centroid_flow: float
    avg_institutional_flow: float
    avg_retail_flow: float
    cluster_stocks: List[str]
    flow_pattern: str
    confidence: float


@dataclass
class MainForceControl:
    """主力控盘分析。"""

    stock_code: str
    control_degree: float
    main_force_type: str
    concentration_ratio: float
    sustained_period: int
    control_stability: float
    flow_predictability: float
    institutional_dominance: float
    control_signals: List[str]


@dataclass
class FlowCorrelationNetwork:
    """资金流向相关性网络。"""

    correlation_matrix: pd.DataFrame
    strong_correlations: List[Tuple[str, str, float]]
    flow_clusters: List[CapitalFlowCluster]
    network_density: float
    dominant_flows: List[str]
    risk_contagion_potential: float


@dataclass
class SmartMoneyIndicator:
    """聪明钱指标。"""

    stock_code: str
    smart_money_score: float
    institutional_accumulation: float
    insider_activity: float
    whale_transactions: float
    flow_divergence: float
    timing_quality: float
    conviction_signals: List[str]
