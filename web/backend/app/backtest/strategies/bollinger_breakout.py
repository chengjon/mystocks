"""
Bollinger Bands Breakout Strategy

布林带突破策略 - 波动率突破交易
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class BollingerBreakoutStrategy(BaseStrategy):
    """
    布林带突破策略

    核心逻辑:
    - 上轨突破: 价格突破上轨买入 (动量突破)
    - 下轨反弹: 价格触及下轨买入 (超卖反弹)
    - 中轨止盈: 价格回到中轨附近止盈
    - 带宽过滤: 只在波动率适中时交易

    策略类型:
    1. 突破型: 突破上轨追涨 (趋势跟踪)
    2. 反转型: 触及下轨抄底 (均值回归)
    3. 混合型: 根据市场状态动态选择
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "布林带突破策略 - 上轨突破追涨，下轨反弹抄底，波动率自适应"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 状态跟踪
        self.last_signal_type = {}
        self.entry_band = {}  # 记录入场带位 ('upper', 'lower', 'middle')

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # 布林带参数
            "bb_period": 20,  # 布林带周期
            "bb_std": 2.0,  # 标准差倍数
            "bb_ma_type": "sma",  # 均线类型 (sma/ema)
            # 策略模式
            "strategy_mode": "mixed",  # 模式: breakout/reversal/mixed
            # 突破型参数
            "breakout_threshold": 1.01,  # 突破确认 (价格>上轨*1.01)
            "breakout_volume_ratio": 1.5,  # 突破成交量倍数
            # 反转型参数
            "reversal_rsi_threshold": 30,  # RSI超卖阈值
            "reversal_confirm_period": 2,  # 反转确认周期
            # 带宽过滤
            "use_bandwidth_filter": True,  # 使用带宽过滤
            "min_bandwidth_pct": 0.02,  # 最小带宽% (避免盘整)
            "max_bandwidth_pct": 0.15,  # 最大带宽% (避免剧烈波动)
            # 止损止盈
            "use_middle_band_exit": True,  # 中轨止盈
            "stop_loss_pct": 0.05,  # 固定止损%
            "use_opposite_band_stop": True,  # 对侧轨道止损
            # 仓位管理
            "position_sizing": "bandwidth",  # 仓位大小: fixed/bandwidth
            "base_position_size": 0.3,  # 基础仓位大小
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
                "name": "strategy_mode",
                "type": "select",
                "options": ["breakout", "reversal", "mixed"],
                "label": "策略模式",
            },
            {
                "name": "breakout_threshold",
                "type": "float",
                "min": 1.00,
                "max": 1.05,
                "label": "突破阈值",
            },
        ]

    def _calculate_bandwidth(self, upper: float, lower: float, middle: float) -> float:
        """计算带宽百分比"""
        if middle == 0:
            return 0
        return (upper - lower) / middle

    def _calculate_band_position(self, price: float, upper: float, lower: float) -> float:
        """
        计算价格在布林带中的位置

        Returns:
            0.0 = 下轨, 0.5 = 中轨, 1.0 = 上轨
        """
        if upper == lower:
            return 0.5
        return (price - lower) / (upper - lower)

    def _check_breakout_signal(
        self,
        symbol: str,
        current_price: float,
        upper: float,
        middle: float,
        current_data: Dict[str, Any],
    ) -> bool:
        """检查上轨突破信号"""
        breakout_price = upper * self.parameters["breakout_threshold"]

        # 价格突破上轨
        if current_price < breakout_price:
            return False

        # 成交量确认
        volume_ratio = self.parameters.get("breakout_volume_ratio", 1.5)
        if volume_ratio > 1.0:
            volumes = self.get_volumes(symbol)
            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                current_volume = int(current_data.get("volume", 0))
                if current_volume < avg_volume * volume_ratio:
                    return False

        return True

    def _check_reversal_signal(self, symbol: str, current_price: float, lower: float, middle: float) -> bool:
        """检查下轨反转信号"""
        # 价格触及下轨
        if current_price > lower * 1.02:  # 允许2%偏差
            return False

        # RSI超卖确认
        rsi_threshold = self.parameters.get("reversal_rsi_threshold", 30)
        closes = self.get_closes(symbol)
        if len(closes) >= 14:
            rsi = self.rsi(closes, 14)
            if rsi and rsi > rsi_threshold:
                return False

        return True

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
        bb_result = self.bollinger_bands(closes, bb_period, self.parameters["bb_std"])

        if not bb_result:
            return None

        upper, middle, lower = bb_result
        current_price = float(current_data["close"])
        has_position = position and position.get("quantity", 0) > 0

        # === 带宽过滤 ===
        if self.parameters.get("use_bandwidth_filter"):
            bandwidth = self._calculate_bandwidth(upper, lower, middle)
            min_bw = self.parameters["min_bandwidth_pct"]
            max_bw = self.parameters["max_bandwidth_pct"]

            if bandwidth < min_bw or bandwidth > max_bw:
                # 带宽不在合适范围，不交易
                return None

        # 计算价格在布林带中的位置
        band_position = self._calculate_band_position(current_price, upper, lower)

        # === 退出信号 ===
        if has_position:
            entry_band = self.entry_band.get(symbol)

            # 1. 中轨止盈
            if self.parameters.get("use_middle_band_exit"):
                # 如果从上轨入场，回到中轨附近止盈
                if entry_band == "upper" and band_position <= 0.55:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"中轨止盈: 价格{current_price:.2f}回到中轨{middle:.2f}附近",
                    )

                # 如果从下轨入场，涨到中轨附近止盈
                if entry_band == "lower" and band_position >= 0.45:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"中轨止盈: 价格{current_price:.2f}回到中轨{middle:.2f}附近",
                    )

            # 2. 对侧轨道止损
            if self.parameters.get("use_opposite_band_stop"):
                # 从上轨入场，跌破下轨止损
                if entry_band == "upper" and current_price <= lower:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"对侧止损: 价格{current_price:.2f}跌破下轨{lower:.2f}",
                    )

                # 从下轨入场，突破上轨后跌破止损
                if entry_band == "lower" and current_price <= lower:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"跌破下轨止损: 价格{current_price:.2f} <= {lower:.2f}",
                    )

            # 3. 固定百分比止损
            if position:
                avg_cost = float(position.get("avg_cost", current_price))
                stop_loss_pct = self.parameters.get("stop_loss_pct", 0.05)
                stop_price = avg_cost * (1 - stop_loss_pct)

                if current_price <= stop_price:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"固定止损: 价格{current_price:.2f} <= {stop_price:.2f} (-{stop_loss_pct * 100}%)",
                    )

        # === 入场信号 ===
        if not has_position:
            strategy_mode = self.parameters["strategy_mode"]

            # 突破型信号
            if strategy_mode in ["breakout", "mixed"]:
                if self._check_breakout_signal(symbol, current_price, upper, middle, current_data):
                    # 计算仓位大小
                    strength = self.parameters["base_position_size"]
                    if self.parameters["position_sizing"] == "bandwidth":
                        bandwidth = self._calculate_bandwidth(upper, lower, middle)
                        # 带宽越大，仓位越小 (风险控制)
                        strength = min(
                            0.5,
                            self.parameters["base_position_size"] / (bandwidth * 10),
                        )

                    # 记录入场带位
                    self.entry_band[symbol] = "upper"

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"上轨突破: 价格{current_price:.2f}突破上轨{upper:.2f}",
                        target_price=Decimal(str(middle)),  # 目标价为中轨
                        metadata={
                            "entry_band": "upper",
                            "upper": upper,
                            "middle": middle,
                            "lower": lower,
                            "bandwidth": self._calculate_bandwidth(upper, lower, middle),
                        },
                    )

            # 反转型信号
            if strategy_mode in ["reversal", "mixed"]:
                if self._check_reversal_signal(symbol, current_price, lower, middle):
                    strength = self.parameters["base_position_size"]
                    if self.parameters["position_sizing"] == "bandwidth":
                        bandwidth = self._calculate_bandwidth(upper, lower, middle)
                        # 带宽越小，信号越可靠 (盘整后突破)
                        strength = min(
                            0.5,
                            self.parameters["base_position_size"] * (0.05 / bandwidth),
                        )

                    # 记录入场带位
                    self.entry_band[symbol] = "lower"

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"下轨反弹: 价格{current_price:.2f}触及下轨{lower:.2f}，RSI超卖",
                        target_price=Decimal(str(middle)),  # 目标价为中轨
                        metadata={
                            "entry_band": "lower",
                            "upper": upper,
                            "middle": middle,
                            "lower": lower,
                            "bandwidth": self._calculate_bandwidth(upper, lower, middle),
                        },
                    )

        return None

    def on_fill(self, symbol: str, action: str, price: float, quantity: int):
        """成交回调"""
        if action == "SELL":
            # 清空入场记录
            self.entry_band.pop(symbol, None)
