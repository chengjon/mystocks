"""
Position Aggregate Root
持仓聚合根

管理投资组合中的持仓状态和成本计算。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any
from uuid import uuid4
from decimal import Decimal

from ..value_objects.order_side import OrderSide


@dataclass
class PositionOpenedEvent:
    """持仓开仓事件"""

    position_id: str
    portfolio_id: str
    symbol: str
    quantity: int
    price: float
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "PositionOpenedEvent"


@dataclass
class PositionIncreasedEvent:
    """持仓加仓事件"""

    position_id: str
    symbol: str
    added_quantity: int
    new_total_quantity: int
    new_avg_price: float
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "PositionIncreasedEvent"


@dataclass
class PositionDecreasedEvent:
    """持仓减仓事件"""

    position_id: str
    symbol: str
    decreased_quantity: int
    remaining_quantity: int
    realized_profit: float
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "PositionDecreasedEvent"


@dataclass
class StopLossTriggeredEvent:
    """止损触发事件"""

    position_id: str
    portfolio_id: str
    symbol: str
    stop_loss_price: float
    current_price: float
    quantity: int
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "StopLossTriggeredEvent"


@dataclass
class Position:
    """
    持仓聚合根

    职责：
    - 管理持仓数量和成本
    - 处理加仓、减仓逻辑
    - 计算实现盈亏
    - 发送持仓变更事件

    不变量：
    - 持仓数量不能为负（空头用负数表示）
    - 平均成本必须为正（持仓不为零时）
    - 减仓数量不能超过当前持仓
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    portfolio_id: str = ""
    symbol: str = ""
    quantity: int = 0  # 持仓数量（正数为多头，负数为空头）
    avg_price: float = 0.0  # 平均成本价
    stop_loss_price: Optional[float] = None  # 止损价
    take_profit_price: Optional[float] = None  # 止盈价
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 领域事件集合
    _domain_events: List[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """验证持仓"""
        if self.quantity == 0 and self.avg_price != 0:
            raise ValueError(f"Avg price must be 0 when quantity is 0: {self.avg_price}")

        if self.quantity != 0 and self.avg_price <= 0:
            raise ValueError(f"Avg price must be positive when holding position: {self.avg_price}")

    @classmethod
    def open_position(
        cls,
        portfolio_id: str,
        symbol: str,
        quantity: int,
        price: float,
        side: OrderSide,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> "Position":
        """
        开仓

        Args:
            portfolio_id: 投资组合ID
            symbol: 标的代码
            quantity: 数量
            price: 成交价格
            side: 方向
            stop_loss: 止损价
            take_profit: 止盈价

        Returns:
            Position实例
        """
        # 根据方向确定数量符号
        actual_quantity = quantity if side == OrderSide.BUY else -quantity

        position = cls(
            portfolio_id=portfolio_id,
            symbol=symbol,
            quantity=actual_quantity,
            avg_price=price,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
        )

        # 发送开仓事件
        position._add_domain_event(
            PositionOpenedEvent(
                position_id=position.id,
                portfolio_id=portfolio_id,
                symbol=symbol,
                quantity=actual_quantity,
                price=price,
            )
        )

        return position

    def increase_position(self, added_quantity: int, price: float) -> None:
        """
        加仓

        Args:
            added_quantity: 增加数量（绝对值）
            price: 成交价格

        不变量：
        - 加仓后持仓方向不变
        """
        if added_quantity <= 0:
            raise ValueError(f"Added quantity must be positive: {added_quantity}")

        # 根据当前持仓方向确定实际增减
        if self.quantity >= 0:
            actual_added = added_quantity
        else:
            actual_added = -added_quantity

        # 计算新的平均成本
        total_cost = (self.quantity * self.avg_price) + (actual_added * price)
        new_quantity = self.quantity + actual_added
        new_avg_price = total_cost / new_quantity if new_quantity != 0 else 0.0

        # 更新持仓
        self.quantity = new_quantity
        self.avg_price = new_avg_price
        self.updated_at = datetime.now()

        # 发送加仓事件
        self._add_domain_event(
            PositionIncreasedEvent(
                position_id=self.id,
                symbol=self.symbol,
                added_quantity=actual_added,
                new_total_quantity=new_quantity,
                new_avg_price=new_avg_price,
            )
        )

    def decrease_position(self, decreased_quantity: int, price: float) -> float:
        """
        减仓

        Args:
            decreased_quantity: 减少数量（绝对值）
            price: 成交价格

        Returns:
            实现盈亏

        不变量：
        - 减仓数量不能超过当前持仓
        """
        if decreased_quantity <= 0:
            raise ValueError(f"Decreased quantity must be positive: {decreased_quantity}")

        # 根据当前持仓方向确定实际增减
        if self.quantity >= 0:
            actual_decreased = decreased_quantity
        else:
            actual_decreased = -decreased_quantity

        if abs(actual_decreased) > abs(self.quantity):
            raise ValueError(f"Cannot decrease {decreased_quantity} when holding {self.quantity}")

        # 计算实现盈亏
        if self.quantity > 0:
            # 多头减仓
            realized_profit = (price - self.avg_price) * actual_decreased
        else:
            # 空头减仓
            realized_profit = (self.avg_price - price) * abs(actual_decreased)

        # 更新持仓
        remaining_quantity = self.quantity - actual_decreased
        self.quantity = remaining_quantity
        self.updated_at = datetime.now()

        # 如果持仓为零，重置平均成本
        if self.quantity == 0:
            self.avg_price = 0.0

        # 发送减仓事件
        self._add_domain_event(
            PositionDecreasedEvent(
                position_id=self.id,
                symbol=self.symbol,
                decreased_quantity=actual_decreased,
                remaining_quantity=remaining_quantity,
                realized_profit=realized_profit,
            )
        )

        return realized_profit

    def check_stop_loss(self, current_price: float) -> bool:
        """
        检查止损是否触发

        Args:
            current_price: 当前价格

        Returns:
            是否触发止损
        """
        if self.stop_loss_price is None or self.quantity == 0:
            return False

        triggered = False

        if self.quantity > 0:
            # 多头止损：价格跌破止损价
            triggered = current_price <= self.stop_loss_price
        else:
            # 空头止损：价格突破止损价
            triggered = current_price >= self.stop_loss_price

        if triggered:
            # 发送止损触发事件
            self._add_domain_event(
                StopLossTriggeredEvent(
                    position_id=self.id,
                    portfolio_id=self.portfolio_id,
                    symbol=self.symbol,
                    stop_loss_price=self.stop_loss_price,
                    current_price=current_price,
                    quantity=self.quantity,
                )
            )

        return triggered

    def check_take_profit(self, current_price: float) -> bool:
        """
        检查止盈是否触发

        Args:
            current_price: 当前价格

        Returns:
            是否触发止盈
        """
        if self.take_profit_price is None or self.quantity == 0:
            return False

        if self.quantity > 0:
            # 多头止盈：价格突破止盈价
            return current_price >= self.take_profit_price
        else:
            # 空头止盈：价格跌破止盈价
            return current_price <= self.take_profit_price

    def set_stop_loss(self, stop_loss_price: float) -> None:
        """
        设置止损价

        Args:
            stop_loss_price: 止损价格
        """
        if stop_loss_price <= 0:
            raise ValueError(f"Stop loss price must be positive: {stop_loss_price}")

        # 验证止损价合理性
        if self.quantity > 0 and stop_loss_price >= self.avg_price:
            raise ValueError(f"Long position stop loss ({stop_loss_price}) must be below avg price ({self.avg_price})")

        if self.quantity < 0 and stop_loss_price <= self.avg_price:
            raise ValueError(f"Short position stop loss ({stop_loss_price}) must be above avg price ({self.avg_price})")

        self.stop_loss_price = stop_loss_price
        self.updated_at = datetime.now()

    def set_take_profit(self, take_profit_price: float) -> None:
        """
        设置止盈价

        Args:
            take_profit_price: 止盈价格
        """
        if take_profit_price <= 0:
            raise ValueError(f"Take profit price must be positive: {take_profit_price}")

        # 验证止盈价合理性
        if self.quantity > 0 and take_profit_price <= self.avg_price:
            raise ValueError(
                f"Long position take profit ({take_profit_price}) must be above avg price ({self.avg_price})"
            )

        if self.quantity < 0 and take_profit_price >= self.avg_price:
            raise ValueError(
                f"Short position take profit ({take_profit_price}) must be below avg price ({self.avg_price})"
            )

        self.take_profit_price = take_profit_price
        self.updated_at = datetime.now()

    def _add_domain_event(self, event: Any) -> None:
        """添加领域事件"""
        self._domain_events.append(event)

    def get_domain_events(self) -> List[Any]:
        """获取并清空领域事件"""
        events = self._domain_events
        self._domain_events = []
        return events

    @property
    def market_value(self, current_price: float) -> float:
        """
        计算市值

        Args:
            current_price: 当前市场价格

        Returns:
            市值
        """
        return abs(self.quantity * current_price)

    @property
    def total_cost(self) -> float:
        """总成本"""
        return abs(self.quantity * self.avg_price)

    @property
    def is_long(self) -> bool:
        """是否为多头持仓"""
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """是否为空头持仓"""
        return self.quantity < 0

    @property
    def is_closed(self) -> bool:
        """是否已平仓"""
        return self.quantity == 0

    def unrealized_profit(self, current_price: float) -> float:
        """
        计算未实现盈亏

        Args:
            current_price: 当前市场价格

        Returns:
            未实现盈亏
        """
        if self.is_closed:
            return 0.0

        if self.is_long:
            return (current_price - self.avg_price) * self.quantity
        else:
            return (self.avg_price - current_price) * abs(self.quantity)

    def profit_ratio(self, current_price: float) -> float:
        """
        计算盈亏比例

        Args:
            current_price: 当前市场价格

        Returns:
            盈亏比例（百分比）
        """
        if self.avg_price == 0:
            return 0.0

        if self.is_long:
            return ((current_price - self.avg_price) / self.avg_price) * 100
        else:
            return ((self.avg_price - current_price) / self.avg_price) * 100

    def __str__(self) -> str:
        direction = "LONG" if self.is_long else "SHORT" if self.is_short else "FLAT"
        return (
            f"Position(id={self.id[:8]}, symbol={self.symbol}, "
            f"direction={direction}, quantity={self.quantity}, "
            f"avg_price={self.avg_price:.2f})"
        )
