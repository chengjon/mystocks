"""
Capital Flow Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台资金流向与主力控盘分析功能

This module provides comprehensive capital flow analysis including:
- Capital flow clustering and pattern analysis
- Main force control detection and analysis
- Capital flow correlation and network analysis
- Institutional vs retail flow dynamics
- Smart money tracking and identification
"""

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis.capital_flow_analyzer._capital_flow_cluster_mixin import CapitalFlowClusterMixin
from src.advanced_analysis.capital_flow_analyzer.capital_flow_models import (
    CapitalFlowCluster,
    FlowCorrelationNetwork,
    MainForceControl,
    SmartMoneyIndicator,
)


class CapitalFlowAnalyzer(CapitalFlowClusterMixin, BaseAnalyzer):
    """
    资金流向分析器

    提供全面的资金流向与主力控盘分析，包括：
    - 资金流向聚类和模式分析
    - 主力控盘能力检测
    - 资金流向相关性和网络分析
    - 机构vs散户资金动态
    - 聪明钱追踪和识别
    """


__init__ = CapitalFlowClusterMixin.__init__
analyze = CapitalFlowClusterMixin.analyze
_get_capital_flow_data = CapitalFlowClusterMixin._get_capital_flow_data
_generate_mock_capital_flow_data = CapitalFlowClusterMixin._generate_mock_capital_flow_data
_analyze_flow_clustering = CapitalFlowClusterMixin._analyze_flow_clustering
_extract_clustering_features = CapitalFlowClusterMixin._extract_clustering_features
_perform_kmeans_clustering = CapitalFlowClusterMixin._perform_kmeans_clustering
_classify_flow_pattern = CapitalFlowClusterMixin._classify_flow_pattern
_calculate_cluster_confidence = CapitalFlowClusterMixin._calculate_cluster_confidence
_analyze_main_force_control = CapitalFlowClusterMixin._analyze_main_force_control
_calculate_control_degree = CapitalFlowClusterMixin._calculate_control_degree
_identify_main_force_type = CapitalFlowClusterMixin._identify_main_force_type
_calculate_concentration_ratio = CapitalFlowClusterMixin._calculate_concentration_ratio
_calculate_sustained_period = CapitalFlowClusterMixin._calculate_sustained_period
_calculate_control_stability = CapitalFlowClusterMixin._calculate_control_stability
_calculate_flow_predictability = CapitalFlowClusterMixin._calculate_flow_predictability
_calculate_institutional_dominance = CapitalFlowClusterMixin._calculate_institutional_dominance
_generate_control_signals = CapitalFlowClusterMixin._generate_control_signals
_analyze_smart_money = CapitalFlowClusterMixin._analyze_smart_money
_calculate_smart_money_score = CapitalFlowClusterMixin._calculate_smart_money_score
_calculate_institutional_accumulation = CapitalFlowClusterMixin._calculate_institutional_accumulation
_calculate_insider_activity = CapitalFlowClusterMixin._calculate_insider_activity
_calculate_whale_transactions = CapitalFlowClusterMixin._calculate_whale_transactions
_calculate_flow_divergence = CapitalFlowClusterMixin._calculate_flow_divergence
_calculate_timing_quality = CapitalFlowClusterMixin._calculate_timing_quality
_generate_conviction_signals = CapitalFlowClusterMixin._generate_conviction_signals
_analyze_market_context = CapitalFlowClusterMixin._analyze_market_context
_calculate_capital_flow_scores = CapitalFlowClusterMixin._calculate_capital_flow_scores
