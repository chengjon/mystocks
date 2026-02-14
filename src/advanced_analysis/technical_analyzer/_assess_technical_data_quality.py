"""
Technical Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台技术分析功能

This module provides advanced technical analysis capabilities including:
- Custom technical indicators and pattern recognition
- Multi-timeframe analysis and confluence detection
- Market regime identification (trending vs ranging)
- Advanced pattern analysis (turtle channels, volatility breakouts)
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer
from src.indicators.indicator_factory import IndicatorFactory

def _assess_technical_data_quality(self, data: pd.DataFrame) -> float:
    """评估技术数据质量"""
    if data.empty:
        return 0.0

    quality_score = 100.0

    # 检查数据完整性
    required_columns = ["open", "high", "low", "close", "volume"]
    for col in required_columns:
        if col not in data.columns:
            quality_score -= 20

    # 检查数据合理性
    if "close" in data.columns:
        # 检查价格合理性
        negative_prices = (data["close"] <= 0).sum()
        if negative_prices > 0:
            quality_score -= negative_prices * 5

        # 检查价格连续性
        price_changes = data["close"].pct_change().abs()
        extreme_changes = (price_changes > 0.2).sum()  # 超过20%的变动
        quality_score -= extreme_changes * 2

    return max(0.0, min(100.0, quality_score))


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.TECHNICAL,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"技术分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )


