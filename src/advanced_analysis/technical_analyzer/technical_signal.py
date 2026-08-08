"""
Technical Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台技术分析功能

This module provides advanced technical analysis capabilities including:
- Custom technical indicators and pattern recognition
- Multi-timeframe analysis and confluence detection
- Market regime identification (trending vs ranging)
- Advanced pattern analysis (turtle channels, volatility breakouts)
"""

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis.technical_analyzer._technical_signal_mixin import TechnicalAnalyzerMixin


class TechnicalAnalyzer(TechnicalAnalyzerMixin, BaseAnalyzer):
    """
    技术分析器

    提供高级技术分析功能，包括：
    - 自定义技术指标和形态识别
    - 多时间框架分析
    - 市场状态识别
    - 信号生成和过滤
    """


__init__ = TechnicalAnalyzer.__init__
analyze = TechnicalAnalyzer.analyze
_calculate_technical_indicators = TechnicalAnalyzer._calculate_technical_indicators
_calculate_turtle_channel = TechnicalAnalyzer._calculate_turtle_channel
_calculate_volatility_breakout = TechnicalAnalyzer._calculate_volatility_breakout
_calculate_momentum_squeeze = TechnicalAnalyzer._calculate_momentum_squeeze
_calculate_adaptive_rsi = TechnicalAnalyzer._calculate_adaptive_rsi
_generate_technical_signals = TechnicalAnalyzer._generate_technical_signals
_generate_rsi_signals = TechnicalAnalyzer._generate_rsi_signals
_generate_macd_signals = TechnicalAnalyzer._generate_macd_signals
_generate_bbands_signals = TechnicalAnalyzer._generate_bbands_signals
_generate_turtle_signals = TechnicalAnalyzer._generate_turtle_signals
_generate_volatility_signals = TechnicalAnalyzer._generate_volatility_signals
_analyze_patterns = TechnicalAnalyzer._analyze_patterns
_detect_head_shoulders = TechnicalAnalyzer._detect_head_shoulders
_detect_double_top_bottom = TechnicalAnalyzer._detect_double_top_bottom
_detect_triangle = TechnicalAnalyzer._detect_triangle
_detect_wedge = TechnicalAnalyzer._detect_wedge
_analyze_market_regime = TechnicalAnalyzer._analyze_market_regime
_calculate_composite_signal = TechnicalAnalyzer._calculate_composite_signal
_filter_signals = TechnicalAnalyzer._filter_signals
_generate_recommendation = TechnicalAnalyzer._generate_recommendation
_assess_risk_level = TechnicalAnalyzer._assess_risk_level
_check_signal_consistency = TechnicalAnalyzer._check_signal_consistency
_detect_divergences = TechnicalAnalyzer._detect_divergences
