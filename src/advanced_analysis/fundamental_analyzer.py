"""
Fundamental Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台基本面分析功能

This module provides comprehensive fundamental analysis capabilities including:
- Multi-dimensional financial analysis (profitability, solvency, operation, growth)
- Financial anomaly detection and red flag identification
- Industry comparison and benchmarking
- Valuation metrics and scoring
"""

import warnings

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis._fundamental_analyzer_mixin import FundamentalAnalyzerMixin

try:
    pass

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Fundamental analysis will run on CPU.")


class FundamentalAnalyzer(FundamentalAnalyzerMixin, BaseAnalyzer):
    """
    基本面分析器

    提供全面的基本面分析功能，包括：
    - 多维度财务分析
    - 财务异常检测
    - 估值分析
    - 行业比较
    """


__init__ = FundamentalAnalyzer.__init__
analyze = FundamentalAnalyzer.analyze
_get_financial_data = FundamentalAnalyzer._get_financial_data
_calculate_financial_ratios = FundamentalAnalyzer._calculate_financial_ratios
_calculate_profitability_ratios = FundamentalAnalyzer._calculate_profitability_ratios
_calculate_solvency_ratios = FundamentalAnalyzer._calculate_solvency_ratios
_calculate_operation_ratios = FundamentalAnalyzer._calculate_operation_ratios
_calculate_growth_ratios = FundamentalAnalyzer._calculate_growth_ratios
_calculate_cashflow_ratios = FundamentalAnalyzer._calculate_cashflow_ratios
_calculate_fundamental_score = FundamentalAnalyzer._calculate_fundamental_score
_score_profitability = FundamentalAnalyzer._score_profitability
_score_solvency = FundamentalAnalyzer._score_solvency
_score_operation = FundamentalAnalyzer._score_operation
_score_growth = FundamentalAnalyzer._score_growth
_score_cashflow = FundamentalAnalyzer._score_cashflow
_determine_rating = FundamentalAnalyzer._determine_rating
_calculate_industry_percentile = FundamentalAnalyzer._calculate_industry_percentile
_identify_flags_and_strengths = FundamentalAnalyzer._identify_flags_and_strengths
_analyze_valuation = FundamentalAnalyzer._analyze_valuation
_compare_with_industry = FundamentalAnalyzer._compare_with_industry
_load_industry_benchmarks = FundamentalAnalyzer._load_industry_benchmarks
_get_stock_industry = FundamentalAnalyzer._get_stock_industry
_get_current_price = FundamentalAnalyzer._get_current_price
_calculate_historical_percentile = FundamentalAnalyzer._calculate_historical_percentile
_compare_with_industry_valuation = FundamentalAnalyzer._compare_with_industry_valuation
_assess_data_quality = FundamentalAnalyzer._assess_data_quality
_generate_investment_suggestion = FundamentalAnalyzer._generate_investment_suggestion
_create_error_result = FundamentalAnalyzer._create_error_result
