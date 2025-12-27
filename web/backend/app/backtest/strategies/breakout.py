"""
Breakout Strategy

突破策略模板 - 突破关键价位
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class BreakoutStrategy(BaseStrategy):
    """
    突破策略

    核心逻辑：
    - 价格突破N日最高价时买入
    - 跌破N日最低价或止损点时卖出
    - 结合成交量确认突破有效性
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "突破策略 - 价格突破关键阻力位时买入"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存最高最低价
        self.highs_cache = {}
        self.lows_cache = {}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            "lookback_period": 20,  # 回溯周期
            "breakout_confirm_pct": 0.01,  # 突破确认百分比 (1%)
            "volume_multiplier": 1.5,  # 成交量倍数
            "atr_period": 14,  # ATR周期
            "stop_loss_atr": 2.0,  # 止损ATR倍数
            "take_profit_atr": 3.0,  # 止盈ATR倍数
            "min_consolidation_days": 5,  # 最小盘整天数
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "lookback_period",
                "type": "int",
                "min": 10,
                "max": 60,
                "label": "回溯周期",
            },
            {
                "name": "breakout_confirm_pct",
                "type": "float",
                "min": 0.005,
                "max": 0.05,
                "label": "突破确认%",
            },
            {
                "name": "volume_multiplier",
                "type": "float",
                "min": 1.0,
                "max": 3.0,
                "label": "成交量倍数",
            },
            {
                "name": "atr_period",
                "type": "int",
                "min": 5,
                "max": 30,
                "label": "ATR周期",
            },
        ]

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        lookback = self.parameters["lookback_period"]
        history = self.price_history.get(symbol, [])

        if len(history) < lookback + 1:
            return None

        current_price = float(current_data["close"])
        current_volume = int(current_data.get("volume", 0))
        has_position = position and position.get("quantity", 0) > 0

        # 计算N日最高价和最低价
        recent_history = history[-(lookback + 1) : -1]  # 不包括今天
        highs = [float(h["high"]) for h in recent_history]
        lows = [float(h["low"]) for h in recent_history]
        volumes = [int(h.get("volume", 0)) for h in recent_history]

        resistance = max(highs)  # 阻力位
        support = min(lows)  # 支撑位
        avg_volume = sum(volumes) / len(volumes) if volumes else 0

        # 计算ATR
        atr_value = self.atr(history, self.parameters["atr_period"])

        # 买入信号：向上突破
        if not has_position:
            breakout_price = resistance * (1 + self.parameters["breakout_confirm_pct"])

            if current_price >= breakout_price:
                # 成交量确认
                volume_confirmed = current_volume >= avg_volume * self.parameters["volume_multiplier"]

                if volume_confirmed:
                    strength = min(1.0, (current_price - resistance) / resistance / 0.05)

                    # 计算止损止盈价位
                    stop_loss = None
                    take_profit = None
                    if atr_value:
                        stop_loss = Decimal(str(current_price - atr_value * self.parameters["stop_loss_atr"]))
                        take_profit = Decimal(str(current_price + atr_value * self.parameters["take_profit_atr"]))

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"价格{current_price:.2f}突破{lookback}日高点{resistance:.2f}，成交量放大{current_volume / avg_volume:.1f}倍",
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                    )

        # 卖出信号：跌破支撑或止损
        if has_position:
            # 跌破支撑位
            breakdown_price = support * (1 - self.parameters["breakout_confirm_pct"])
            if current_price <= breakdown_price:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"价格{current_price:.2f}跌破{lookback}日低点{support:.2f}",
                )

            # ATR止损
            if atr_value:
                entry_price = position.get("avg_cost", current_price)
                stop_price = entry_price - atr_value * self.parameters["stop_loss_atr"]
                if current_price <= stop_price:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"触发ATR止损，价格{current_price:.2f} <= {stop_price:.2f}",
                    )

        return None
