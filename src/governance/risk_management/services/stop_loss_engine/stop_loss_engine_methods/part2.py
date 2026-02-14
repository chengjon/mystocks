"""
止损引擎实现
Stop Loss Engine Implementation

实现波动率自适应止损和跟踪止损策略。
复用现有的监控和交易基础设施。
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np

from src.governance.risk_management.core import IStopLossEngine

# 复用现有的数据源和监控基础设施
try:
    from src.monitoring.signal_recorder import get_signal_recorder

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)


class StopLossEngineCalculateTriggerConfidenceMixin:
    """StopLossEngine 方法集 Part 2"""

    def _calculate_trigger_confidence(self, result: Dict[str, Any]) -> str:
        """计算触发信心水平"""
        confidence_score = 0

        # 价格触发贡献
        if result.get("price_triggered"):
            confidence_score += 40

        # 技术强度贡献
        technical_strength = result.get("technical_strength", 50)
        confidence_score += min(30, technical_strength * 0.6)

        # 回撤幅度贡献
        drawdown = result.get("drawdown_percentage", 0)
        if drawdown > 0.15:  # 15%以上回撤
            confidence_score += 20
        elif drawdown > 0.10:  # 10%以上回撤
            confidence_score += 10

        # 确定信心等级
        if confidence_score >= 80:
            return "high"
        elif confidence_score >= 60:
            return "medium"
        elif confidence_score >= 40:
            return "low"
        else:
            return "very_low"

    async def _analyze_trailing_performance(self, symbol: str, trailing_mode: str) -> Dict[str, Any]:
        """分析跟踪止损历史表现"""
        try:
            # 这里应该从SignalResultTracker获取历史数据
            # 暂时返回模拟数据
            return {
                "total_trades": 25,
                "successful_exits": 18,
                "average_profit_pct": 8.5,
                "max_drawdown_avoided": 12.3,
                "win_rate": 0.72,
                "avg_holding_period_days": 45,
                "best_performing_mode": "hybrid",
                "current_mode_performance": 0.85 if trailing_mode == "hybrid" else 0.78,
            }
        except Exception:
            logger.warning("分析跟踪表现失败 %(symbol)s: %(e)s")
            return {}

    def _generate_trailing_adjustments(self, result: Dict[str, Any], historical_perf: Dict[str, Any]) -> Dict[str, Any]:
        """生成跟踪止损调整建议"""
        recommendations = []

        # 基于当前表现的调整建议
        technical_strength = result.get("technical_strength", 50)
        drawdown = result.get("drawdown_percentage", 0)

        if technical_strength < 30:
            recommendations.append("技术指标疲弱，建议增加跟踪百分比至10-12%")
        elif technical_strength > 80:
            recommendations.append("技术指标强劲，可以考虑减少跟踪百分比至6-8%")

        if drawdown > 0.12:
            recommendations.append("回撤较大，建议启用加速因子或切换到波动率模式")

        # 基于历史表现的调整建议
        win_rate = historical_perf.get("win_rate", 0.5)
        if win_rate > 0.75:
            recommendations.append("历史胜率良好，可以尝试更激进的跟踪设置")
        elif win_rate < 0.60:
            recommendations.append("历史胜率较低，建议使用更保守的跟踪设置")

        return {
            "recommendations": recommendations,
            "suggested_percentage": self._suggest_trailing_percentage(result, historical_perf),
            "suggested_mode": self._suggest_trailing_mode(result, historical_perf),
        }

    def _suggest_trailing_percentage(self, result: Dict[str, Any], historical_perf: Dict[str, Any]) -> float:
        """建议跟踪百分比"""
        current_percentage = result.get("effective_trailing_percentage", 0.08)
        technical_strength = result.get("technical_strength", 50)
        win_rate = historical_perf.get("win_rate", 0.5)

        # 基于技术强度调整
        if technical_strength > 80 and win_rate > 0.7:
            return min(current_percentage * 0.8, 0.05)  # 减少至最小5%
        elif technical_strength < 40 or win_rate < 0.5:
            return min(current_percentage * 1.2, 0.15)  # 增加至最大15%

        return current_percentage

    def _suggest_trailing_mode(self, result: Dict[str, Any], historical_perf: Dict[str, Any]) -> str:
        """建议跟踪模式"""
        best_mode = historical_perf.get("best_performing_mode", "percentage")
        current_mode = result.get("trailing_mode", "percentage")

        # 如果当前模式表现不佳，建议切换
        current_performance = historical_perf.get("current_mode_performance", 0.5)
        if current_performance < 0.7 and best_mode != current_mode:
            return best_mode

        return current_mode

    async def _record_trailing_calculation(self, symbol: str, calculation_result: Dict[str, Any]):
        """记录跟踪止损计算到SignalResultTracker"""
        try:
            if self.signal_recorder:
                await self.signal_recorder.record_signal(
                    strategy_id="trailing_stop_system",
                    symbol=symbol,
                    signal_type="TRAILING_STOP_CALCULATION",
                    indicator_count=1,
                    execution_time_ms=0.0,
                    gpu_used=False,
                    metadata={
                        "trailing_mode": calculation_result.get("trailing_mode"),
                        "trailing_percentage": calculation_result.get("trailing_percentage"),
                        "acceleration_factor": calculation_result.get("acceleration_factor"),
                        "technical_strength": calculation_result.get("technical_strength"),
                        "trigger_confidence": calculation_result.get("trigger_analysis", {}).get("confidence_level"),
                        "recommended_trigger": calculation_result.get("trigger_analysis", {}).get(
                            "recommended_trigger"
                        ),
                    },
                )
                logger.debug("跟踪止损计算记录成功: %(symbol)s")
        except Exception:
            logger.warning("记录跟踪止损计算失败 %(symbol)s: %(e)s")

    async def _get_recent_market_data(self, symbol: str, days: int) -> Dict[str, Any]:
        """获取近期市场数据"""
        try:
            # 这里应该获取最近N天的市场数据
            # 暂时返回模拟数据
            return {
                "price_history": [100 + i for i in range(days)],
                "volume_history": [1000000 + i * 10000 for i in range(days)],
                "volatility": 0.15,
            }
        except Exception:
            return {}

    async def _get_rsi(self, symbol: str, period: int) -> Optional[float]:
        """获取RSI指标"""
        try:
            # 这里应该计算真实的RSI
            return 55.0  # 模拟中性RSI
        except Exception:
            return None

    async def _check_price_near_support(self, symbol: str, current_price: float) -> bool:
        """检查价格是否接近支撑位"""
        try:
            # 这里应该分析技术支撑位
            return False  # 模拟结果
        except Exception:
            return False

    async def _check_volume_confirmation(self, symbol: str) -> bool:
        """检查成交量确认"""
        try:
            # 这里应该分析成交量配合
            return True  # 模拟结果
        except Exception:
            return False

    def _calculate_technical_strength(self, confirmations: Dict[str, bool]) -> int:
        """计算技术强度评分"""
        score = 50  # 基础分

        # 各确认条件的权重
        weights = {
            "ma_20_broken": 20,
            "ma_50_broken": 15,
            "rsi_oversold": 25,
            "price_near_support": 10,
            "volume_confirmation": 30,
        }

        for condition, weight in weights.items():
            if confirmations.get(condition, False):
                score += weight

        return min(100, score)

