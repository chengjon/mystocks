"""
Trading Signals Analyzer for MyStocks Advanced Quantitative Analysis
A股量化分析平台交易信号分析功能

This module provides multi-level trading signals system including:
- Multi-timeframe signal generation and confluence detection
- Real-time monitoring and intelligent alerts
- Signal strength assessment and filtering
- Risk-adjusted signal validation
"""

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis.trading_signals_analyzer._assess_signal_risk import (
    _assess_signal_risk,
    _check_signal_consistency,
    _create_error_result,
)
from src.advanced_analysis.trading_signals_analyzer._trading_signal_mixin import TradingSignalAnalyzerMixin
from src.advanced_analysis.trading_signals_analyzer.trading_signal_models import SignalConfluence, TradingSignal


class TradingSignalAnalyzer(TradingSignalAnalyzerMixin, BaseAnalyzer):
    """
    交易信号分析器

    提供多层级交易信号系统，包括：
    - 多时间框架信号生成和汇合检测
    - 实时监控和智能告警
    - 信号强度评估和过滤
    - 风险调整信号验证
    """


TradingSignalAnalyzer._assess_signal_risk = _assess_signal_risk
TradingSignalAnalyzer._check_signal_consistency = _check_signal_consistency
TradingSignalAnalyzer._create_error_result = _create_error_result

__init__ = TradingSignalAnalyzer.__init__
analyze = TradingSignalAnalyzer.analyze
_generate_timeframe_signals = TradingSignalAnalyzer._generate_timeframe_signals
_generate_rsi_signals = TradingSignalAnalyzer._generate_rsi_signals
_generate_macd_signals = TradingSignalAnalyzer._generate_macd_signals
_generate_bollinger_signals = TradingSignalAnalyzer._generate_bollinger_signals
_generate_ma_signals = TradingSignalAnalyzer._generate_ma_signals
_generate_volume_signals = TradingSignalAnalyzer._generate_volume_signals
_generate_sr_signals = TradingSignalAnalyzer._generate_sr_signals
_analyze_signal_confluence = TradingSignalAnalyzer._analyze_signal_confluence
_apply_risk_adjustments = TradingSignalAnalyzer._apply_risk_adjustments
_calculate_atr = TradingSignalAnalyzer._calculate_atr
_calculate_overall_signal_strength = TradingSignalAnalyzer._calculate_overall_signal_strength
_generate_trading_recommendation = TradingSignalAnalyzer._generate_trading_recommendation
