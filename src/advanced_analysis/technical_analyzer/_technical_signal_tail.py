"""Tail helpers for `technical_signal.py`."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis.technical_analyzer.technical_signal_models import (
    MarketRegime,
    PatternResult,
    TechnicalSignal,
)


class TechnicalAnalyzerTailMixin:
    def _calculate_composite_signal(
        self, signals: List[TechnicalSignal], patterns: List[PatternResult], market_regime: Optional[MarketRegime]
    ) -> Dict[str, Any]:
        """计算综合信号"""
        # 信号权重计算
        buy_signals = [s for s in signals if s.signal_type == "buy"]
        sell_signals = [s for s in signals if s.signal_type == "sell"]

        buy_strength = np.mean([s.strength * s.confidence for s in buy_signals]) if buy_signals else 0
        sell_strength = np.mean([s.strength * s.confidence for s in sell_signals]) if sell_signals else 0

        # 形态信号
        pattern_buy_strength = (
            np.mean([p.strength * p.confidence for p in patterns if p.direction == "bullish"]) if patterns else 0
        )
        pattern_sell_strength = (
            np.mean([p.strength * p.confidence for p in patterns if p.direction == "bearish"]) if patterns else 0
        )

        # 市场状态调整
        regime_multiplier = 1.0
        if market_regime:
            if market_regime.primary_regime == "trending":
                regime_multiplier = 1.2  # 趋势市场信号更可靠
            elif market_regime.volatility_regime == "high_vol":
                regime_multiplier = 0.9  # 高波动市场信号更不可靠

        # 综合信号
        total_buy = (buy_strength * 0.7 + pattern_buy_strength * 0.3) * regime_multiplier
        total_sell = (sell_strength * 0.7 + pattern_sell_strength * 0.3) * regime_multiplier

        if total_buy > total_sell and total_buy > 0.5:
            signal = "buy"
            strength = min(total_buy, 1.0)
        elif total_sell > total_buy and total_sell > 0.5:
            signal = "sell"
            strength = min(total_sell, 1.0)
        else:
            signal = "hold"
            strength = 0.5

        confidence = min((abs(total_buy - total_sell) + 0.5), 1.0)

        return {
            "signal": signal,
            "strength": strength,
            "confidence": confidence,
            "components": {
                "technical_signals": len(signals),
                "pattern_signals": len(patterns),
                "buy_strength": total_buy,
                "sell_strength": total_sell,
            },
        }


    def _filter_signals(self, signals: List[TechnicalSignal], threshold: float) -> List[TechnicalSignal]:
        """过滤信号"""
        return [s for s in signals if s.strength * s.confidence >= threshold]


    def _generate_recommendation(self, composite_signal: Dict[str, Any], market_regime: Optional[MarketRegime]) -> str:
        """生成推荐"""
        signal = composite_signal.get("signal", "hold")
        strength = composite_signal.get("strength", 0.0)

        if signal == "buy" and strength > 0.7:
            if market_regime and market_regime.primary_regime == "trending":
                return "强烈推荐买入，趋势市场机会较大"
            else:
                return "推荐买入，注意风险控制"
        elif signal == "sell" and strength > 0.7:
            return "建议卖出，获利了结"
        else:
            if market_regime and market_regime.volatility_regime == "high_vol":
                return "观望为主，高波动环境建议等待"
            else:
                return "观望，等待更明确信号"


    def _assess_risk_level(self, signals: List[TechnicalSignal], patterns: List[PatternResult]) -> str:
        """评估风险水平"""
        # 基于信号一致性和强度评估风险
        signal_consistency = self._check_signal_consistency(signals)

        if signal_consistency < 0.3:
            return "high"  # 信号不一致，风险高
        elif len(signals) > 5 and signal_consistency > 0.7:
            return "low"  # 多重确认信号，风险低
        else:
            return "medium"


    def _check_signal_consistency(self, signals: List[TechnicalSignal]) -> float:
        """检查信号一致性"""
        if not signals:
            return 0.0

        buy_count = sum(1 for s in signals if s.signal_type == "buy")
        sell_count = sum(1 for s in signals if s.signal_type == "sell")

        total = len(signals)
        max_consistent = max(buy_count, sell_count)

        return max_consistent / total if total > 0 else 0.0


    def _detect_divergences(self, indicators: Dict[str, pd.Series]) -> List[str]:
        """检测背离"""
        divergences = []

        # 价格与RSI背离检测
        if "rsi_14" in indicators:
            price_trend = indicators.get("sma_20", pd.Series())
            rsi_trend = indicators["rsi_14"]

            if len(price_trend) > 10 and len(rsi_trend) > 10:
                # 简化的背离检测逻辑
                price_peak = price_trend.iloc[-1] > price_trend.iloc[-5:-1].max()
                rsi_valley = rsi_trend.iloc[-1] < rsi_trend.iloc[-5:-1].min()

                if price_peak and rsi_valley:
                    divergences.append("价格与RSI看跌背离")

        return divergences
