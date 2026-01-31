"""
Grid Strategy

网格策略模板 - 区间震荡套利
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.backtest.strategies.base import BaseStrategy, SignalType, StrategySignal


class GridStrategy(BaseStrategy):
    """
    网格策略

    核心逻辑：
    - 设置价格区间和网格数量
    - 价格下跌到网格线时买入
    - 价格上涨到网格线时卖出
    - 适合震荡行情
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "网格策略 - 在价格区间内低买高卖，赚取震荡收益"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 初始化网格
        self.grid_levels = []
        self.grid_positions = {}  # {price_level: quantity}

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            "grid_count": 10,  # 网格数量
            "price_range_pct": 0.20,  # 价格区间百分比 (±20%)
            "grid_spacing_pct": 0.02,  # 网格间距百分比 (2%)
            "base_quantity": 100,  # 基础买入数量
            "auto_adjust": True,  # 自动调整网格
            "adjustment_period": 20,  # 调整周期（天）
            "trend_filter": True,  # 趋势过滤
            "ma_period": 50,  # 均线周期（用于趋势判断）
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "grid_count",
                "type": "int",
                "min": 5,
                "max": 20,
                "label": "网格数量",
            },
            {
                "name": "price_range_pct",
                "type": "float",
                "min": 0.10,
                "max": 0.50,
                "label": "价格区间%",
            },
            {
                "name": "grid_spacing_pct",
                "type": "float",
                "min": 0.01,
                "max": 0.05,
                "label": "网格间距%",
            },
            {
                "name": "base_quantity",
                "type": "int",
                "min": 100,
                "max": 1000,
                "label": "基础数量",
            },
        ]

    def _initialize_grid(self, center_price: float):
        """初始化网格线"""
        grid_count = self.parameters["grid_count"]
        spacing_pct = self.parameters["grid_spacing_pct"]

        self.grid_levels = []
        for i in range(-grid_count // 2, grid_count // 2 + 1):
            level_price = center_price * (1 + i * spacing_pct)
            self.grid_levels.append(round(level_price, 2))

        self.grid_levels.sort()

    def _find_nearest_grid_level(self, price: float, direction: str) -> Optional[float]:
        """
        找到最近的网格线

        Args:
            price: 当前价格
            direction: 'below'查找下方网格线, 'above'查找上方网格线
        """
        if direction == "below":
            levels_below = [level for level in self.grid_levels if level < price]
            return max(levels_below) if levels_below else None
        else:  # above
            levels_above = [level for level in self.grid_levels if level > price]
            return min(levels_above) if levels_above else None

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        current_price = float(current_data["close"])
        closes = self.get_closes(symbol)

        # 初始化网格
        if not self.grid_levels:
            # 使用最近N天的平均价作为中心价
            n = min(20, len(closes))
            if n > 0:
                center = sum(closes[-n:]) / n
                self._initialize_grid(center)

        if not self.grid_levels:
            return None

        # 趋势过滤（可选）
        if self.parameters.get("trend_filter"):
            ma_period = self.parameters["ma_period"]
            if len(closes) >= ma_period:
                ma = self.sma(closes, ma_period)
                # 在下降趋势中不建议使用网格策略
                if current_price < ma * 0.95:  # 价格低于均线5%
                    return None

        has_position = position and position.get("quantity", 0) > 0
        current_quantity = position.get("quantity", 0) if position else 0

        # 买入信号：价格触及下方网格线
        if True:  # 网格策略可以一直买卖
            buy_level = self._find_nearest_grid_level(current_price, "below")

            if buy_level and abs(current_price - buy_level) / buy_level < 0.005:  # 允许0.5%偏差
                # 检查是否已在该价位买入
                if buy_level not in self.grid_positions:
                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.LONG,
                        strength=0.5,  # 网格策略使用固定仓位
                        reason=f"价格{current_price:.2f}触及网格买入线{buy_level:.2f}",
                        target_price=Decimal(str(buy_level)),
                    )

        # 卖出信号：价格触及上方网格线
        if has_position and current_quantity > 0:
            sell_level = self._find_nearest_grid_level(current_price, "above")

            if sell_level and abs(current_price - sell_level) / sell_level < 0.005:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=0.5,  # 部分卖出
                    reason=f"价格{current_price:.2f}触及网格卖出线{sell_level:.2f}",
                    target_price=Decimal(str(sell_level)),
                )

        return None

    def on_fill(self, symbol: str, action: str, price: float, quantity: int):
        """记录成交（供回测引擎调用）"""
        price_level = round(price, 2)

        if action == "BUY":
            self.grid_positions[price_level] = self.grid_positions.get(price_level, 0) + quantity
        elif action == "SELL":
            # 从最近的买入价位减去
            if price_level in self.grid_positions:
                self.grid_positions[price_level] = max(0, self.grid_positions[price_level] - quantity)
                if self.grid_positions[price_level] == 0:
                    del self.grid_positions[price_level]
