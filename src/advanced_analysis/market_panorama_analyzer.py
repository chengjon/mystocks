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

import warnings

from src.advanced_analysis import BaseAnalyzer
from src.advanced_analysis._market_panorama_analyzer_mixin import MarketPanoramaAnalyzerMixin

# GPU acceleration support
try:
    pass

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    warnings.warn("GPU libraries not available. Market panorama analysis will run on CPU.")


class MarketPanoramaAnalyzer(MarketPanoramaAnalyzerMixin, BaseAnalyzer):
    """
    市场全景分析器

    提供全面的市场全景分析，包括：
    - 资金流向全景分析
    - 交易活跃度全景分析
    - 市场趋势全景分析
    - 估值分布全景分析
    - 市场情绪动态分析
    """
