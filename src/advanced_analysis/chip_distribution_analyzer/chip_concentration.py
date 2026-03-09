"""
Chip Distribution Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台筹码分布分析功能

This module provides comprehensive chip distribution analysis including:
- Cost distribution analysis based on cost transformation principles
- Chip concentration and peak analysis
- Winning probability calculation based on chip distribution
- Chip flow dynamics and cost area identification
- Long-term vs short-term chip distribution analysis
"""

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis.chip_distribution_analyzer._chip_concentration_mixin import ChipDistributionAnalyzerMixin
from src.advanced_analysis.chip_distribution_analyzer._generate_chip_recommendations import (
    _assess_chip_risk,
    _create_error_result,
    _generate_chip_recommendations,
)
from src.advanced_analysis.chip_distribution_analyzer.chip_models import (
    ChipConcentration,
    ChipFlowDynamics,
    CostAreaAnalysis,
    WinningProbability,
)


class ChipDistributionAnalyzer(ChipDistributionAnalyzerMixin, BaseAnalyzer):
    """
    筹码分布分析器

    基于成本转换原理提供全面的筹码分布分析，包括：
    - 筹码集中度和峰值分析
    - 筹码流动动态分析
    - 基于筹码分布的获胜概率计算
    - 成本区识别和支撑阻力分析
    - 长期vs短期筹码分布对比
    """


ChipDistributionAnalyzer._generate_chip_recommendations = _generate_chip_recommendations
ChipDistributionAnalyzer._assess_chip_risk = _assess_chip_risk
ChipDistributionAnalyzer._create_error_result = _create_error_result

__init__ = ChipDistributionAnalyzer.__init__
analyze = ChipDistributionAnalyzer.analyze
_calculate_chip_distribution = ChipDistributionAnalyzer._calculate_chip_distribution
_analyze_chip_concentration = ChipDistributionAnalyzer._analyze_chip_concentration
_analyze_chip_flow_dynamics = ChipDistributionAnalyzer._analyze_chip_flow_dynamics
_calculate_winning_probability = ChipDistributionAnalyzer._calculate_winning_probability
_analyze_cost_areas = ChipDistributionAnalyzer._analyze_cost_areas
_find_peaks = ChipDistributionAnalyzer._find_peaks
_identify_support_areas = ChipDistributionAnalyzer._identify_support_areas
_identify_resistance_areas = ChipDistributionAnalyzer._identify_resistance_areas
_group_consecutive_prices = ChipDistributionAnalyzer._group_consecutive_prices
_calculate_chip_scores = ChipDistributionAnalyzer._calculate_chip_scores
_generate_chip_signals = ChipDistributionAnalyzer._generate_chip_signals
