"""
MACD Strategy

MACD策略 - 趋势和动量双重确认
Moving Average Convergence Divergence
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.backtest.strategies.base import BaseStrategy, SignalType, StrategySignal


class MACDStrategy(BaseStrategy):
    """
    MACD策略

    核心逻辑:
    - MACD线 = EMA(12) - EMA(26)
    - Signal线 = EMA(MACD, 9)
    - Histogram = MACD - Signal
    - 金叉买入 (MACD上穿Signal)
    - 死叉卖出 (MACD下穿Signal)
    - 可选零轴过滤和柱状图确认

    优势:
    - 趋势和动量双重确认
    - 明确的买卖信号
    - 可配置的参数组合
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "MACD策略 - 金叉买入，死叉卖出，趋势动量双重确认"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存MACD值
        self.macd_cache = {}
        self.signal_cache = {}
        self.histogram_cache = {}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # MACD参数
            "fast_period": 12,  # 快速EMA周期
            "slow_period": 26,  # 慢速EMA周期
            "signal_period": 9,  # Signal线周期
            # 信号确认
            "crossover_confirm": 1,  # 交叉确认天数
            "require_histogram_confirm": True,  # 要求柱状图确认
            # 过滤器
            "zero_line_filter": True,  # 零轴过滤 (只在MACD>0时做多)
            "trend_filter": False,  # 趋势过滤
            "trend_ma_period": 50,  # 趋势均线周期
            # 强度判断
            "use_histogram_strength": True,  # 使用柱状图判断信号强度
            "min_histogram_ratio": 0.001,  # 最小柱状图比率
            # 止损止盈
            "use_dynamic_stops": True,  # 动态止损止盈
            "atr_period": 14,  # ATR周期
            "stop_loss_atr": 2.0,  # 止损ATR倍数
            "take_profit_atr": 3.0,  # 止盈ATR倍数
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "fast_period",
                "type": "int",
                "min": 5,
                "max": 20,
                "label": "快速EMA",
            },
            {
                "name": "slow_period",
                "type": "int",
                "min": 15,
                "max": 40,
                "label": "慢速EMA",
            },
            {
                "name": "signal_period",
                "type": "int",
                "min": 5,
                "max": 15,
                "label": "Signal周期",
            },
            {
                "name": "crossover_confirm",
                "type": "int",
                "min": 0,
                "max": 3,
                "label": "确认天数",
            },
        ]

    def _calculate_macd(self, prices: List[float]) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        计算MACD指标

        Returns:
            (MACD线, Signal线, Histogram)
        """
        fast_period = self.parameters["fast_period"]
        slow_period = self.parameters["slow_period"]
        signal_period = self.parameters["signal_period"]

        if len(prices) < slow_period:
            return None, None, None

        # 计算快速和慢速EMA
        fast_ema = self.ema(prices, fast_period)
        slow_ema = self.ema(prices, slow_period)

        if fast_ema is None or slow_ema is None:
            return None, None, None

        # MACD线 = 快速EMA - 慢速EMA
        macd_line = fast_ema - slow_ema

        # 计算Signal线 (MACD的EMA)
        # 需要先构建MACD历史
        macd_history = []
        for i in range(len(prices) - signal_period + 1):
            subset = prices[: len(prices) - signal_period + 1 + i]
            if len(subset) >= slow_period:
                f_ema = self.ema(subset, fast_period)
                s_ema = self.ema(subset, slow_period)
                if f_ema and s_ema:
                    macd_history.append(f_ema - s_ema)

        if len(macd_history) < signal_period:
            return macd_line, None, None

        # Signal线 = MACD的EMA
        signal_line = self.ema(macd_history, signal_period)

        if signal_line is None:
            return macd_line, None, None

        # Histogram = MACD - Signal
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def _check_golden_cross(
        self,
        macd_current: float,
        signal_current: float,
        macd_prev: float,
        signal_prev: float,
    ) -> bool:
        """检测金叉: MACD上穿Signal"""
        return macd_current > signal_current and macd_prev <= signal_prev

    def _check_death_cross(
        self,
        macd_current: float,
        signal_current: float,
        macd_prev: float,
        signal_prev: float,
    ) -> bool:
        """检测死叉: MACD下穿Signal"""
        return macd_current < signal_current and macd_prev >= signal_prev

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        closes = self.get_closes(symbol)
        slow_period = self.parameters["slow_period"]

        if len(closes) < slow_period + 1:
            return None

        # 计算当前MACD
        macd, signal_line, histogram = self._calculate_macd(closes)

        if macd is None or signal_line is None:
            return None

        # 计算前一天的MACD (用于检测交叉)
        prev_macd, prev_signal, prev_histogram = self._calculate_macd(closes[:-1])

        if prev_macd is None or prev_signal is None:
            return None

        current_price = float(current_data["close"])
        has_position = position and position.get("quantity", 0) > 0

        # === 过滤器检查 ===

        # 零轴过滤
        if self.parameters.get("zero_line_filter"):
            # 做多需要MACD > 0 (处于多头区域)
            if not has_position and macd <= 0:
                return None

        # 趋势过滤
        if self.parameters.get("trend_filter"):
            trend_period = self.parameters["trend_ma_period"]
            if len(closes) >= trend_period:
                trend_ma = self.sma(closes, trend_period)
                if trend_ma and current_price < trend_ma:
                    return None

        # 柱状图确认
        histogram_confirmed = True
        if self.parameters.get("require_histogram_confirm"):
            # 买入信号需要柱状图为正且增长
            if not has_position:
                histogram_confirmed = histogram > 0 and histogram > prev_histogram

        # === 买入信号 (金叉) ===
        if not has_position:
            if self._check_golden_cross(macd, signal_line, prev_macd, prev_signal):
                if histogram_confirmed:
                    # 计算信号强度 (基于柱状图比率)
                    strength = 1.0
                    if self.parameters.get("use_histogram_strength"):
                        histogram_ratio = abs(histogram) / abs(macd) if macd != 0 else 0
                        strength = min(
                            1.0,
                            histogram_ratio / self.parameters["min_histogram_ratio"],
                        )

                    # 动态止损止盈
                    stop_loss = None
                    take_profit = None
                    if self.parameters.get("use_dynamic_stops"):
                        history = self.price_history.get(symbol, [])
                        atr_period = self.parameters["atr_period"]
                        if len(history) >= atr_period:
                            atr = self.atr(history, atr_period)
                            if atr:
                                stop_loss = Decimal(str(current_price - atr * self.parameters["stop_loss_atr"]))
                                take_profit = Decimal(str(current_price + atr * self.parameters["take_profit_atr"]))

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"MACD金叉: MACD({macd:.4f}) 上穿 Signal({signal_line:.4f}), Hist={histogram:.4f}",
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        metadata={
                            "macd": macd,
                            "signal": signal_line,
                            "histogram": histogram,
                        },
                    )

        # === 卖出信号 (死叉) ===
        if has_position:
            if self._check_death_cross(macd, signal_line, prev_macd, prev_signal):
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"MACD死叉: MACD({macd:.4f}) 下穿 Signal({signal_line:.4f})",
                    metadata={
                        "macd": macd,
                        "signal": signal_line,
                        "histogram": histogram,
                    },
                )

            # 柱状图反转卖出 (可选)
            if self.parameters.get("require_histogram_confirm"):
                # 柱状图由正转负
                if histogram < 0 and prev_histogram >= 0:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=0.5,  # 部分退出
                        reason=f"柱状图反转: Hist从{prev_histogram:.4f}转为{histogram:.4f}",
                        metadata={
                            "macd": macd,
                            "signal": signal_line,
                            "histogram": histogram,
                        },
                    )

        return None
