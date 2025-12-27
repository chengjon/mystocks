"""
Execution Handler

订单执行处理器，模拟真实市场的订单执行、滑点和手续费
"""

from typing import Optional
from decimal import Decimal

from app.backtest.events import OrderEvent, FillEvent


class ExecutionHandler:
    """
    订单执行处理器

    模拟订单在市场中的执行过程
    """

    def __init__(
        self,
        commission_rate: Decimal = Decimal("0.0003"),  # 手续费率（默认0.03%）
        slippage_rate: Decimal = Decimal("0.001"),  # 滑点率（默认0.1%）
        min_commission: Decimal = Decimal("5.0"),  # 最小手续费（A股规则）
    ):
        """
        初始化执行处理器

        Args:
            commission_rate: 手续费率
            slippage_rate: 滑点率
            min_commission: 最小手续费
        """
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.min_commission = min_commission

    def execute_order(
        self,
        order: OrderEvent,
        current_price: Decimal,
        current_volume: int = 1000000,  # 当前成交量（用于判断是否能成交）
    ) -> Optional[FillEvent]:
        """
        执行订单并生成成交事件

        Args:
            order: 订单事件
            current_price: 当前市场价格
            current_volume: 当前成交量

        Returns:
            成交事件，如果无法成交则返回None
        """
        # 检查订单数量是否合理
        if order.quantity <= 0:
            return None

        # 检查成交量是否足够（简化模拟，实际应该更复杂）
        if order.quantity > current_volume * 0.1:  # 订单不超过当前成交量的10%
            # 成交量不足，部分成交或不成交
            # 为简化起见，这里假设全部成交，但会有更大的滑点
            pass

        # 计算滑点后的成交价格
        fill_price = self._calculate_fill_price(order, current_price)

        # 计算手续费
        commission = self._calculate_commission(order.quantity, fill_price)

        # 计算滑点成本
        slippage_cost = abs(fill_price - current_price) * Decimal(order.quantity)

        # 创建成交事件
        fill_event = FillEvent(
            symbol=order.symbol,
            trade_date=order.trade_date,
            action=order.action,
            quantity=order.quantity,
            fill_price=fill_price,
            commission=commission,
            slippage=slippage_cost,
            strategy_id=order.strategy_id,
        )

        return fill_event

    def _calculate_fill_price(self, order: OrderEvent, current_price: Decimal) -> Decimal:
        """
        计算成交价格（考虑滑点）

        Args:
            order: 订单事件
            current_price: 当前市场价格

        Returns:
            成交价格
        """
        if order.order_type == "MARKET":
            # 市价单：应用滑点
            if order.action == "BUY":
                # 买入时价格上滑
                fill_price = current_price * (Decimal("1") + self.slippage_rate)
            else:  # SELL
                # 卖出时价格下滑
                fill_price = current_price * (Decimal("1") - self.slippage_rate)

            # 价格精度（保留2位小数）
            fill_price = fill_price.quantize(Decimal("0.01"))

        elif order.order_type == "LIMIT":
            # 限价单：按指定价格成交（如果可能）
            if order.price is None:
                # 如果没有指定限价，使用当前价
                fill_price = current_price
            else:
                # 检查是否能成交
                if order.action == "BUY" and order.price >= current_price:
                    fill_price = order.price
                elif order.action == "SELL" and order.price <= current_price:
                    fill_price = order.price
                else:
                    # 限价单无法成交
                    return None

        elif order.order_type == "STOP":
            # 止损单：触发后按市价成交
            if order.price is None:
                fill_price = current_price
            else:
                # 检查是否触发止损
                if order.action == "BUY" and current_price >= order.price:
                    fill_price = current_price * (Decimal("1") + self.slippage_rate)
                elif order.action == "SELL" and current_price <= order.price:
                    fill_price = current_price * (Decimal("1") - self.slippage_rate)
                else:
                    # 止损未触发
                    return None

        else:
            # 默认使用当前价
            fill_price = current_price

        return fill_price

    def _calculate_commission(self, quantity: int, price: Decimal) -> Decimal:
        """
        计算手续费

        Args:
            quantity: 数量
            price: 价格

        Returns:
            手续费
        """
        # 交易金额
        trade_value = price * Decimal(quantity)

        # 按比例计算手续费
        commission = trade_value * self.commission_rate

        # 应用最小手续费
        commission = max(commission, self.min_commission)

        # 精度（保留2位小数）
        commission = commission.quantize(Decimal("0.01"))

        return commission

    def estimate_fill_price(self, action: str, current_price: Decimal) -> Decimal:
        """
        估算成交价格（用于策略决策）

        Args:
            action: 交易方向 ('BUY' or 'SELL')
            current_price: 当前价格

        Returns:
            估算的成交价格
        """
        if action == "BUY":
            return current_price * (Decimal("1") + self.slippage_rate)
        else:  # SELL
            return current_price * (Decimal("1") - self.slippage_rate)

    def estimate_commission(self, quantity: int, price: Decimal) -> Decimal:
        """
        估算手续费（用于资金管理）

        Args:
            quantity: 数量
            price: 价格

        Returns:
            估算的手续费
        """
        return self._calculate_commission(quantity, price)

    def get_execution_summary(self) -> dict:
        """
        获取执行器配置摘要

        Returns:
            执行器配置信息
        """
        return {
            "commission_rate": float(self.commission_rate),
            "slippage_rate": float(self.slippage_rate),
            "min_commission": float(self.min_commission),
        }
