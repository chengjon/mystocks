"""Tail helpers for `trading_signal.py`."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis.trading_signals_analyzer.trading_signal_models import SignalConfluence, TradingSignal


class TradingSignalAnalyzerTailMixin:
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """计算ATR值"""
        if data.empty or "high" not in data.columns or "low" not in data.columns or "close" not in data.columns:
            return 0.0

        try:
            high = data["high"]
            low = data["low"]
            close = data["close"].shift(1)

            tr = pd.concat([high - low, (high - close).abs(), (low - close).abs()], axis=1).max(axis=1)

            atr = tr.rolling(window=period).mean().iloc[-1]
            return atr if not pd.isna(atr) else 0.0

        except Exception:
            return 0.0


    def _calculate_overall_signal_strength(
        self, signals: List[TradingSignal], confluence: Optional[SignalConfluence]
    ) -> float:
        """计算整体信号强度"""
        if not signals:
            return 0.0

        # 基础信号强度
        avg_strength = np.mean([s.strength * s.confidence for s in signals])

        # 汇合加成
        confluence_bonus = confluence.confluence_score * 0.2 if confluence else 0.0

        # 信号一致性加成
        buy_signals = [s for s in signals if s.signal_type == "buy"]
        sell_signals = [s for s in signals if s.signal_type == "sell"]
        consistency_ratio = max(len(buy_signals), len(sell_signals)) / len(signals)
        consistency_bonus = consistency_ratio * 0.1

        return min(avg_strength + confluence_bonus + consistency_bonus, 1.0)


    def _generate_trading_recommendation(
        self, signals: List[TradingSignal], confluence: Optional[SignalConfluence]
    ) -> Dict[str, Any]:
        """生成交易建议"""
        if not signals:
            return {"signal": "hold", "action": "观望", "confidence": "low", "reason": "无有效信号"}

        # 计算各类型信号数量
        buy_signals = [s for s in signals if s.signal_type == "buy"]
        sell_signals = [s for s in signals if s.signal_type == "sell"]

        # 基于信号数量和强度决定建议
        buy_strength = np.mean([s.strength * s.confidence for s in buy_signals]) if buy_signals else 0
        sell_strength = np.mean([s.strength * s.confidence for s in sell_signals]) if sell_signals else 0

        # 考虑汇合分析
        if confluence and confluence.confluence_score > 0.7:
            if confluence.overall_signal == "buy" and buy_strength > sell_strength:
                signal = "buy"
                action = "强烈买入"
                confidence = "high"
                stop_loss = min([s.stop_loss for s in buy_signals if s.stop_loss] or [None])
                take_profit = max([s.take_profit for s in buy_signals if s.take_profit] or [None])
            elif confluence.overall_signal == "sell" and sell_strength > buy_strength:
                signal = "sell"
                action = "强烈卖出"
                confidence = "high"
                stop_loss = max([s.stop_loss for s in sell_signals if s.stop_loss] or [None])
                take_profit = min([s.take_profit for s in sell_signals if s.take_profit] or [None])
            else:
                signal = "hold"
                action = "观望"
                confidence = "medium"
                stop_loss = None
                take_profit = None
        else:
            if buy_strength > sell_strength and buy_strength > 0.6:
                signal = "buy"
                action = "考虑买入"
                confidence = "medium"
                stop_loss = min([s.stop_loss for s in buy_signals if s.stop_loss] or [None])
                take_profit = max([s.take_profit for s in buy_signals if s.take_profit] or [None])
            elif sell_strength > buy_strength and sell_strength > 0.6:
                signal = "sell"
                action = "考虑卖出"
                confidence = "medium"
                stop_loss = max([s.stop_loss for s in sell_signals if s.stop_loss] or [None])
                take_profit = min([s.take_profit for s in sell_signals if s.take_profit] or [None])
            else:
                signal = "hold"
                action = "观望"
                confidence = "low"
                stop_loss = None
                take_profit = None

        return {
            "signal": signal,
            "action": action,
            "confidence": confidence,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
        }
