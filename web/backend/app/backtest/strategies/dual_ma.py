"""
Dual Moving Average Strategy

双均线策略 - 经典的趋势跟踪策略
"""

from typing import Dict, Any, Optional, List

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class DualMAStrategy(BaseStrategy):
    """
    双均线策略

    核心逻辑：
    - 短期均线上穿长期均线时买入（金叉）
    - 短期均线下穿长期均线时卖出（死叉）
    - 可选择SMA或EMA
    - 可添加成交量和趋势过滤
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "双均线策略 - 金叉买入，死叉卖出，经典趋势跟踪"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 缓存均线值
        self.ma_short_cache = {}
        self.ma_long_cache = {}
        self.prev_signal_type = {}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            "short_period": 10,  # 短期均线周期
            "long_period": 30,  # 长期均线周期
            "ma_type": "sma",  # 均线类型：sma或ema
            "crossover_confirm": 1,  # 交叉确认天数
            "volume_filter": True,  # 是否使用成交量过滤
            "volume_ma_period": 20,  # 成交量均线周期
            "volume_ratio": 1.0,  # 成交量倍数
            "trend_filter": False,  # 是否使用趋势过滤
            "trend_ma_period": 60,  # 趋势均线周期
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "short_period",
                "type": "int",
                "min": 5,
                "max": 50,
                "label": "短期均线",
            },
            {
                "name": "long_period",
                "type": "int",
                "min": 20,
                "max": 200,
                "label": "长期均线",
            },
            {
                "name": "ma_type",
                "type": "select",
                "options": ["sma", "ema"],
                "label": "均线类型",
            },
            {
                "name": "crossover_confirm",
                "type": "int",
                "min": 0,
                "max": 5,
                "label": "确认天数",
            },
        ]

    def _calculate_ma(self, prices: List[float], period: int) -> Optional[float]:
        """根据配置计算均线"""
        ma_type = self.parameters.get("ma_type", "sma")
        if ma_type == "ema":
            return self.ema(prices, period)
        else:
            return self.sma(prices, period)

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        short_period = self.parameters["short_period"]
        long_period = self.parameters["long_period"]
        closes = self.get_closes(symbol)

        if len(closes) < long_period + 1:
            return None

        # 计算双均线
        ma_short = self._calculate_ma(closes, short_period)
        ma_long = self._calculate_ma(closes, long_period)

        if ma_short is None or ma_long is None:
            return None

        # 计算前一天的均线（检测交叉）
        prev_ma_short = self._calculate_ma(closes[:-1], short_period)
        prev_ma_long = self._calculate_ma(closes[:-1], long_period)

        if prev_ma_short is None or prev_ma_long is None:
            return None

        current_price = float(current_data["close"])
        has_position = position and position.get("quantity", 0) > 0

        # 成交量过滤（可选）
        volume_confirmed = True
        if self.parameters.get("volume_filter"):
            volumes = self.get_volumes(symbol)
            if len(volumes) >= self.parameters["volume_ma_period"]:
                avg_volume = sum(volumes[-self.parameters["volume_ma_period"] :]) / self.parameters["volume_ma_period"]
                current_volume = int(current_data.get("volume", 0))
                volume_confirmed = current_volume >= avg_volume * self.parameters["volume_ratio"]

        # 趋势过滤（可选）
        trend_confirmed = True
        if self.parameters.get("trend_filter"):
            trend_period = self.parameters["trend_ma_period"]
            if len(closes) >= trend_period:
                trend_ma = self.sma(closes, trend_period)
                if trend_ma:
                    # 只在价格高于趋势均线时做多
                    trend_confirmed = current_price > trend_ma

        # 检测金叉（买入信号）
        if not has_position:
            # 当前短期均线 > 长期均线，且前一天短期均线 < 长期均线
            if ma_short > ma_long and prev_ma_short <= prev_ma_long:
                if volume_confirmed and trend_confirmed:
                    # 计算信号强度（基于均线差距）
                    gap = (ma_short - ma_long) / ma_long
                    strength = min(1.0, gap / 0.05)  # 差距5%为满强度

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=strength,
                        reason=f"金叉: MA{short_period}({ma_short:.2f}) 上穿 MA{long_period}({ma_long:.2f})",
                    )

        # 检测死叉（卖出信号）
        if has_position:
            # 当前短期均线 < 长期均线，且前一天短期均线 >= 长期均线
            if ma_short < ma_long and prev_ma_short >= prev_ma_long:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=f"死叉: MA{short_period}({ma_short:.2f}) 下穿 MA{long_period}({ma_long:.2f})",
                )

        return None
