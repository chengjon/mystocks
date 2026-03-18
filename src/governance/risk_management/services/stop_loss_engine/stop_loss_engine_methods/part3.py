"""
止损引擎风险评估方法集。
"""

import logging
from typing import Any, Dict

import numpy as np

logger = logging.getLogger(__name__)


class StopLossEngineRiskAssessmentMixin:
    """StopLossEngine 方法集 Part 3"""

    async def _assess_comprehensive_risk(
        self, symbol: str, entry_price: float, stop_loss_price: float, atr_data: Dict[int, float]
    ) -> Dict[str, Any]:
        """评估综合风险水平"""
        try:
            current_price = await self._get_current_price(symbol)
            stop_distance = entry_price - stop_loss_price
            stop_percentage = (stop_distance / entry_price) * 100
            risk_factors = {
                "stop_percentage": stop_percentage,
                "atr_stability": self._calculate_atr_stability(atr_data),
                "price_position": self._assess_price_position(current_price, entry_price),
                "market_condition": await self._assess_market_condition(),
            }
            risk_score = self._calculate_risk_score(risk_factors)
            if risk_score >= 75:
                risk_level = "high"
            elif risk_score >= 50:
                risk_level = "medium"
            elif risk_score >= 25:
                risk_level = "low"
            else:
                risk_level = "very_low"
            return {"level": risk_level, "score": risk_score, "factors": risk_factors}
        except Exception:
            logger.error("评估综合风险失败 %(symbol)s: %(e)s")
            return {"level": "unknown", "score": 50, "factors": {}}

    def _calculate_atr_stability(self, atr_data: Dict[int, float]) -> float:
        """计算ATR稳定性 (0-1, 1表示非常稳定)"""
        if len(atr_data) < 2:
            return 0.5
        atr_values = list(atr_data.values())
        mean_atr = np.mean(atr_values)
        std_atr = np.std(atr_values)
        if mean_atr == 0:
            return 0.5
        cv = std_atr / mean_atr
        return max(0, 1 - cv * 2)

    def _assess_price_position(self, current_price: float, entry_price: float) -> str:
        """评估价格位置"""
        change_pct = (current_price - entry_price) / entry_price * 100
        if change_pct > 5:
            return "strong_uptrend"
        if change_pct > 1:
            return "moderate_uptrend"
        if change_pct > -1:
            return "sideways"
        if change_pct > -5:
            return "moderate_downtrend"
        return "strong_downtrend"

    async def _assess_market_condition(self) -> str:
        """评估市场状况"""
        try:
            market_volatility = await self._get_market_volatility()
            if market_volatility > 0.3:
                return "high_volatility"
            if market_volatility > 0.2:
                return "moderate_volatility"
            if market_volatility > 0.1:
                return "low_volatility"
            return "very_low_volatility"
        except Exception:
            return "unknown"

    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> int:
        """计算综合风险评分"""
        score = 50
        stop_pct = risk_factors.get("stop_percentage", 5.0)
        if stop_pct > 8:
            score -= 20
        elif stop_pct > 5:
            score -= 10
        elif stop_pct < 2:
            score += 20
        elif stop_pct < 3:
            score += 10
        atr_stability = risk_factors.get("atr_stability", 0.5)
        score += int((atr_stability - 0.5) * 20)
        price_position = risk_factors.get("price_position", "sideways")
        if price_position in ["strong_uptrend"]:
            score -= 10
        elif price_position in ["strong_downtrend"]:
            score += 10
        market_condition = risk_factors.get("market_condition", "unknown")
        if market_condition == "high_volatility":
            score += 15
        elif market_condition == "low_volatility":
            score -= 5
        return max(0, min(100, score))

    def _generate_execution_recommendation(self, risk_assessment: Dict[str, Any], stop_percentage: float) -> str:
        """生成执行建议"""
        risk_level = risk_assessment.get("level", "medium")
        if risk_level == "high":
            return f"高风险环境，建议使用更保守的止损策略 (当前{stop_percentage:.1f}%)"
        if risk_level == "medium":
            return f"中风险环境，当前止损设置{stop_percentage:.1f}%合理"
        if risk_level == "low":
            return f"低风险环境，可以考虑稍微放宽止损至{stop_percentage * 1.2:.1f}%"
        return "极低风险环境，建议减少止损幅度以锁定利润"
