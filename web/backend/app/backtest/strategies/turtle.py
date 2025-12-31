"""
Turtle Trading Strategy

海龟交易策略 - 经典的趋势跟踪系统
基于Richard Dennis和William Eckhardt的传奇交易策略
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.backtest.strategies.base import BaseStrategy, StrategySignal, SignalType


class TurtleStrategy(BaseStrategy):
    """
    海龟交易策略

    核心逻辑:
    - 唐奇安通道突破入场 (20日/55日高点)
    - ATR基础的仓位管理 (1 Unit = 1% / N)
    - 金字塔加仓 (最多4个单位, 每1/2N加仓)
    - 2N止损, 10日/20日低点退出
    - 严格的风险控制和资金管理

    原版海龟规则:
    - System 1 (快速): 20日突破入场, 10日低点退出
    - System 2 (慢速): 55日突破入场, 20日低点退出
    - N值 (波动率): 20日ATR
    - 单位大小: 账户的1% / N
    """

    def _init_parameters(self):
        """初始化策略参数"""
        self.description = "海龟交易策略 - 唐奇安突破 + ATR仓位管理 + 金字塔加仓"

        defaults = self.get_default_parameters()
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters[key] = value

        # 跟踪持仓单位
        self.units = {}  # {symbol: [(entry_price, quantity, stop_loss), ...]}
        self.last_add_price = {}  # 最后一次加仓价格

    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        return {
            # 系统选择
            "system": 1,  # 1=System1 (快速), 2=System2 (慢速)
            # 突破参数
            "entry_period_s1": 20,  # System1 入场周期
            "exit_period_s1": 10,  # System1 退出周期
            "entry_period_s2": 55,  # System2 入场周期
            "exit_period_s2": 20,  # System2 退出周期
            # ATR和N值
            "atr_period": 20,  # ATR计算周期 (N值)
            "n_multiplier": 1.0,  # N值倍数 (用于计算单位大小)
            # 仓位管理
            "risk_per_unit": 0.01,  # 每单位风险 (账户的1%)
            "max_units": 4,  # 单个市场最大单位数
            "add_unit_threshold": 0.5,  # 加仓阈值 (0.5N)
            # 止损
            "stop_loss_n": 2.0,  # 止损N倍数 (2N)
            "use_breakeven_stop": True,  # 盈利后移至保本
            # 过滤器
            "skip_on_loss": True,  # System1失败后跳过入场
            "min_volume_ratio": 0.5,  # 最小成交量倍数
        }

    @classmethod
    def get_parameter_schema(cls) -> List[Dict[str, Any]]:
        return [
            {"name": "system", "type": "int", "min": 1, "max": 2, "label": "系统类型"},
            {
                "name": "entry_period_s1",
                "type": "int",
                "min": 10,
                "max": 40,
                "label": "S1入场周期",
            },
            {
                "name": "exit_period_s1",
                "type": "int",
                "min": 5,
                "max": 20,
                "label": "S1退出周期",
            },
            {
                "name": "entry_period_s2",
                "type": "int",
                "min": 40,
                "max": 100,
                "label": "S2入场周期",
            },
            {
                "name": "exit_period_s2",
                "type": "int",
                "min": 10,
                "max": 40,
                "label": "S2退出周期",
            },
            {
                "name": "atr_period",
                "type": "int",
                "min": 10,
                "max": 30,
                "label": "ATR周期",
            },
            {
                "name": "max_units",
                "type": "int",
                "min": 1,
                "max": 6,
                "label": "最大单位数",
            },
        ]

    def _calculate_n(self, symbol: str) -> Optional[float]:
        """计算N值 (真实波动幅度)"""
        history = self.price_history.get(symbol, [])
        atr_period = self.parameters["atr_period"]

        if len(history) < atr_period:
            return None

        return self.atr(history, atr_period)

    def _calculate_unit_size(self, symbol: str, account_value: float, n_value: float) -> int:
        """
        计算单位大小

        海龟规则: 1 Unit = (账户价值 × 1%) / N

        Args:
            symbol: 股票代码
            account_value: 账户总值
            n_value: N值 (ATR)

        Returns:
            单位数量 (股数)
        """
        risk_per_unit = self.parameters["risk_per_unit"]
        dollar_volatility = n_value * self.parameters["n_multiplier"]

        if dollar_volatility == 0:
            return 0

        # 单位价值 = 账户 × 风险百分比
        unit_value = account_value * risk_per_unit

        # 单位数量 = 单位价值 / 美元波动
        quantity = int(unit_value / dollar_volatility)

        # 至少100股 (A股最小交易单位)
        return max(100, (quantity // 100) * 100)

    def _check_entry_signal(self, symbol: str, current_data: Dict[str, Any]) -> bool:
        """检查是否有入场信号 (突破N日高点)"""
        system = self.parameters["system"]

        if system == 1:
            entry_period = self.parameters["entry_period_s1"]
        else:
            entry_period = self.parameters["entry_period_s2"]

        history = self.price_history.get(symbol, [])
        if len(history) < entry_period + 1:
            return False

        # 计算N日最高价 (不包括当天)
        highs = [d["high"] for d in history[-(entry_period + 1) : -1]]
        n_day_high = max(highs)

        current_price = float(current_data["close"])

        # 突破条件: 收盘价 > N日最高价
        return current_price > n_day_high

    def _check_exit_signal(self, symbol: str, current_data: Dict[str, Any]) -> bool:
        """检查是否有退出信号 (跌破N日低点)"""
        system = self.parameters["system"]

        if system == 1:
            exit_period = self.parameters["exit_period_s1"]
        else:
            exit_period = self.parameters["exit_period_s2"]

        history = self.price_history.get(symbol, [])
        if len(history) < exit_period + 1:
            return False

        # 计算N日最低价 (不包括当天)
        lows = [d["low"] for d in history[-(exit_period + 1) : -1]]
        n_day_low = min(lows)

        current_price = float(current_data["close"])

        # 退出条件: 收盘价 < N日最低价
        return current_price < n_day_low

    def _can_add_unit(self, symbol: str, current_price: float, n_value: float) -> bool:
        """
        检查是否可以加仓

        海龟规则: 价格每上涨1/2N可以加仓一次, 最多4个单位
        """
        max_units = self.parameters["max_units"]
        current_units = self.units.get(symbol, [])

        # 已达最大单位数
        if len(current_units) >= max_units:
            return False

        # 没有持仓, 不能加仓
        if not current_units:
            return False

        # 检查价格是否上涨了足够的距离
        last_add_price = self.last_add_price.get(symbol, current_units[-1][0])
        price_increase = current_price - last_add_price
        add_threshold = n_value * self.parameters["add_unit_threshold"]

        return price_increase >= add_threshold

    def _calculate_stop_loss(self, entry_price: float, n_value: float) -> float:
        """计算止损价格 (入场价 - 2N)"""
        stop_n = self.parameters["stop_loss_n"]
        return entry_price - (n_value * stop_n)

    def generate_signal(
        self,
        symbol: str,
        current_data: Dict[str, Any],
        position: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategySignal]:
        """生成交易信号"""

        self.update_history(symbol, current_data)

        current_price = float(current_data["close"])
        self.price_history.get(symbol, [])

        # 计算N值
        n_value = self._calculate_n(symbol)
        if n_value is None:
            return None

        has_position = position and position.get("quantity", 0) > 0
        current_units = self.units.get(symbol, [])

        # === 退出信号检查 ===
        if has_position:
            # 1. 跌破N日低点 - 退出所有单位
            if self._check_exit_signal(symbol, current_data):
                # 清空单位记录
                self.units[symbol] = []
                self.last_add_price.pop(symbol, None)

                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    strength=1.0,
                    reason=(
                        f"退出信号: 价格{current_price:.2f}跌破"
                        f"{self.parameters.get(
                            'exit_period_s1' if self.parameters['system'] == 1 else 'exit_period_s2'
                        )}日低点"
                    ),
                )

            # 2. 止损检查 - 任何单位触发止损则全部退出
            for unit_entry_price, _, unit_stop in current_units:
                if current_price <= unit_stop:
                    self.units[symbol] = []
                    self.last_add_price.pop(symbol, None)

                    return StrategySignal(
                        symbol=symbol,
                        signal_type=SignalType.EXIT,
                        strength=1.0,
                        reason=f"止损: 价格{current_price:.2f} <= 止损价{unit_stop:.2f}",
                    )

        # === 入场和加仓信号 ===

        # 新入场信号
        if not has_position:
            if self._check_entry_signal(symbol, current_data):
                # 计算单位大小 (假设账户价值, 实际应从position获取)
                account_value = 100000  # TODO: 从回测引擎获取实际账户价值
                quantity = self._calculate_unit_size(symbol, account_value, n_value)

                if quantity == 0:
                    return None

                # 计算止损
                stop_loss = self._calculate_stop_loss(current_price, n_value)

                # 记录第一个单位
                self.units[symbol] = [(current_price, quantity, stop_loss)]
                self.last_add_price[symbol] = current_price

                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.LONG,
                    strength=0.25,  # 初始仓位25% (1/4单位)
                    reason=(
                        f"海龟入场: 突破"
                        f"{self.parameters.get(
                            'entry_period_s1' if self.parameters['system'] == 1 else 'entry_period_s2'
                        )}日高点, "
                        f"N={n_value:.2f}"
                    ),
                    stop_loss=Decimal(str(stop_loss)),
                    metadata={
                        "unit_size": quantity,
                        "n_value": n_value,
                        "max_units": self.parameters["max_units"],
                    },
                )

        # 加仓信号
        elif self._can_add_unit(symbol, current_price, n_value):
            account_value = 100000
            quantity = self._calculate_unit_size(symbol, account_value, n_value)

            if quantity == 0:
                return None

            # 计算新的止损
            stop_loss = self._calculate_stop_loss(current_price, n_value)

            # 添加新单位
            current_units.append((current_price, quantity, stop_loss))
            self.units[symbol] = current_units
            self.last_add_price[symbol] = current_price

            # 如果使用保本止损, 更新所有单位的止损
            if self.parameters.get("use_breakeven_stop"):
                # 计算平均成本
                total_cost = sum(price * qty for price, qty, _ in current_units)
                total_qty = sum(qty for _, qty, _ in current_units)
                avg_cost = total_cost / total_qty if total_qty > 0 else 0

                # 如果有盈利, 移至保本
                if current_price > avg_cost:
                    breakeven_stop = avg_cost
                    self.units[symbol] = [(price, qty, max(stop, breakeven_stop)) for price, qty, stop in current_units]

            unit_number = len(current_units)
            strength = unit_number * 0.25  # 每个单位25%

            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=min(strength, 1.0),
                reason=(
                    f"海龟加仓: 第{unit_number}单位, "
                    f"价格上涨{(current_price - self.last_add_price[symbol]) / n_value:.2f}N"
                ),
                stop_loss=Decimal(str(stop_loss)),
                metadata={
                    "unit_number": unit_number,
                    "unit_size": quantity,
                    "total_units": len(current_units),
                },
            )

        return None

    def on_fill(self, symbol: str, action: str, price: float, quantity: int):
        """成交回调 (供回测引擎调用)"""
        if action == "SELL":
            # 清空单位记录
            self.units[symbol] = []
            self.last_add_price.pop(symbol, None)
