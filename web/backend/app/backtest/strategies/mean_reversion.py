"""
Mean Reversion Strategy

均值回归策略模板 - 低买高卖
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.backtest.strategies.base import BaseStrategy, SignalType, StrategySignal


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略

    核心逻辑：
    - 价格偏离均值过多时买入（超卖）
    - 价格回归均值时卖出
    - 使用布林带或标准差判断偏离程度
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "均值回归策略 - 价格偏离均值时反向操作，低买高卖"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            "bb_period": 20,  # 布林带周期
            "bb_std": 2.0,  # 布林带标准差倍数
            "entry_std": 2.0,  # 入场标准差
            "exit_std": 0.5,  # 出场标准差（回归到均值附近）
            "rsi_period": 14,  # RSI周期
            "rsi_oversold": 30,  # RSI超卖
            "rsi_overbought": 70,  # RSI超买
            "max_hold_days": 10,  # 最大持仓天数
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "bb_period",
                "type": "int",
                "min": 10,
                "max": 50,
                "label": "布林带周期",
            },
            {
                "name": "bb_std",
                "type": "float",
                "min": 1.0,
                "max": 3.0,
                "label": "标准差倍数",
            },
            {
                "name": "entry_std",
                "type": "float",
                "min": 1.5,
                "max": 3.0,
                "label": "入场标准差",
            },
            {
                "name": "exit_std",
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "label": "出场标准差",
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

        bb_period = self.parameters["bb_period"]
        closes = self.get_closes(symbol)

        if len(closes) < bb_period:
            return None

        # 计算布林带
        bb = self.bollinger_bands(closes, bb_period, self.parameters["bb_std"])
        if bb is None:
            return None

        upper, middle, lower = bb
        current_price = float(current_data["close"])
        has_position = position and position.get("quantity", 0) > 0

        # 计算价格相对于布林带的位置
        import numpy as np

        std = np.std(closes[-bb_period:])
        z_score = (current_price - middle) / std if std > 0 else 0

        # 买入信号：价格触及下轨
        if not has_position:
            if current_price <= lower or z_score <= -self.parameters["entry_std"]:
                # 检查RSI确认超卖
                rsi = self.rsi(closes, self.parameters["rsi_period"])
                if rsi and rsi < self.parameters["rsi_oversold"]:
                    strength = min(1.0, abs(z_score) / 3)
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"价格{current_price:.2f}触及布林下轨{lower:.2f}，Z={z_score:.2f}",
                        target_price=Decimal(str(middle)),
                    )

        # 卖出信号：价格回归均值
        if has_position:
            # 回归均值附近出场
            if abs(z_score) <= self.parameters["exit_std"]:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"价格{current_price:.2f}回归均值{middle:.2f}，Z={z_score:.2f}",
                )

            # 价格触及上轨也出场
            if current_price >= upper or z_score >= self.parameters["entry_std"]:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"价格{current_price:.2f}触及布林上轨{upper:.2f}",
                )

        return None
