"""
Trading Signals Analyzer for MyStocks Advanced Quantitative Analysis
A股量化分析平台交易信号分析功能

This module provides multi-level trading signals system including:
- Multi-timeframe signal generation and confluence detection
- Real-time monitoring and intelligent alerts
- Signal strength assessment and filtering
- Risk-adjusted signal validation
"""

from datetime import datetime
from typing import List


from src.advanced_analysis import AnalysisResult, AnalysisType

def _assess_signal_risk(self, signals: List[TradingSignal]) -> str:
    """评估信号风险水平"""
    if not signals:
        return "low"

    # 计算信号一致性
    buy_signals = [s for s in signals if s.signal_type == "buy"]
    sell_signals = [s for s in signals if s.signal_type == "sell"]

    if len(buy_signals) > 0 and len(sell_signals) > 0:
        # 信号冲突，高风险
        return "high"
    elif len(signals) >= 3:
        # 多个一致信号，中等风险
        return "medium"
    else:
        # 信号较少，低风险
        return "low"


def _check_signal_consistency(self, signals: List[TradingSignal]) -> float:
    """检查信号一致性"""
    if not signals:
        return 0.0

    buy_count = sum(1 for s in signals if s.signal_type == "buy")
    sell_count = sum(1 for s in signals if s.signal_type == "sell")

    total = len(signals)
    max_consistent = max(buy_count, sell_count)

    return max_consistent / total if total > 0 else 0.0


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.TRADING_SIGNALS,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"交易信号分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )


