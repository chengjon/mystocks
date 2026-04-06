"""
Financial Valuation Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台财务估值分析功能

This module provides comprehensive financial valuation analysis including:
- DCF (Discounted Cash Flow) valuation models
- Multi-model valuation comparison (PE, PB, EV/EBITDA)
- DuPont analysis for financial health decomposition
- Modern financial engineering pricing methods
- Industry-relative valuation benchmarking
"""

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis.financial_valuation_analyzer._calculate_valuation_scores import (
    _assess_valuation_risk,
    _calculate_valuation_scores,
    _create_error_result,
    _generate_valuation_recommendations,
    _generate_valuation_signals,
)
from src.advanced_analysis.financial_valuation_analyzer._dcf_valuation_mixin import (
    FinancialValuationAnalyzerMixin,
)


class FinancialValuationAnalyzer(FinancialValuationAnalyzerMixin, BaseAnalyzer):
    """
    财务估值分析器

    提供全面的财务估值分析，包括：
    - DCF估值模型和现金流折现
    - 多模型相对估值比较
    - 杜邦分析财务健康分解
    - 现代金融工程定价方法
    - 行业相对估值基准
    """


FinancialValuationAnalyzer._calculate_valuation_scores = _calculate_valuation_scores
FinancialValuationAnalyzer._generate_valuation_signals = _generate_valuation_signals
FinancialValuationAnalyzer._generate_valuation_recommendations = _generate_valuation_recommendations
FinancialValuationAnalyzer._assess_valuation_risk = _assess_valuation_risk
FinancialValuationAnalyzer._create_error_result = _create_error_result

__init__ = FinancialValuationAnalyzer.__init__
analyze = FinancialValuationAnalyzer.analyze
_get_financial_data = FinancialValuationAnalyzer._get_financial_data
_generate_mock_financial_data = FinancialValuationAnalyzer._generate_mock_financial_data
_get_current_price = FinancialValuationAnalyzer._get_current_price
_calculate_dcf_valuation = FinancialValuationAnalyzer._calculate_dcf_valuation
_calculate_historical_growth_rate = FinancialValuationAnalyzer._calculate_historical_growth_rate
_calculate_wacc = FinancialValuationAnalyzer._calculate_wacc
_assess_dcf_confidence = FinancialValuationAnalyzer._assess_dcf_confidence
_calculate_relative_valuation = FinancialValuationAnalyzer._calculate_relative_valuation
_calculate_industry_percentile = FinancialValuationAnalyzer._calculate_industry_percentile
_perform_dupont_analysis = FinancialValuationAnalyzer._perform_dupont_analysis
_calculate_modern_valuation = FinancialValuationAnalyzer._calculate_modern_valuation
_calculate_historical_volatility = FinancialValuationAnalyzer._calculate_historical_volatility
_calculate_valuation_consensus = FinancialValuationAnalyzer._calculate_valuation_consensus
