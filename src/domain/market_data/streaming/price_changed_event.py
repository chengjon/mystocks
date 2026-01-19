"""
Price Changed Domain Event
价格变更领域事件

当股票价格发生变化时发布此事件，触发投资组合重新计算。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from src.domain.shared.event import DomainEvent


@dataclass(kw_only=True)
class PriceChangedEvent(DomainEvent):
    """
    价格变更领域事件

    职责：
    - 表示股票价格的变化
    - 触发投资组合重新计算
    - 支持批量价格更新

    Attributes:
        symbol: 股票代码
        old_price: 旧价格（可选，None表示首次价格）
        new_price: 新价格
        price_change: 价格变化（new_price - old_price）
        price_change_pct: 价格变化百分比
        timestamp: 价格时间戳
        volume: 成交量（可选）
        bid_price: 买一价（可选）
        ask_price: 卖一价（可选）
        extra: 额外数据（可选）
    """

    symbol: str
    new_price: float
    old_price: float | None
    price_change: float
    price_change_pct: float
    timestamp: datetime
    volume: int | None = None
    bid_price: float | None = None
    ask_price: float | None = None
    extra: Dict[str, Any] = None

    def __post_init__(self):
        """验证价格变更事件"""
        if self.new_price <= 0:
            raise ValueError(f"New price must be positive: {self.new_price}")

        if self.old_price is not None and self.old_price <= 0:
            raise ValueError(f"Old price must be positive: {self.old_price}")

        if self.bid_price is not None and self.bid_price <= 0:
            raise ValueError(f"Bid price must be positive: {self.bid_price}")

        if self.ask_price is not None and self.ask_price <= 0:
            raise ValueError(f"Ask price must be positive: {self.ask_price}")

    @classmethod
    def create(cls, symbol: str, new_price: float, old_price: float | None = None, **kwargs) -> "PriceChangedEvent":
        """
        工厂方法：创建价格变更事件

        Args:
            symbol: 股票代码
            new_price: 新价格
            old_price: 旧价格（可选）
            **kwargs: 其他参数（volume, bid_price, ask_price等）

        Returns:
            PriceChangedEvent: 价格变更事件
        """
        timestamp = kwargs.get("timestamp", datetime.now())

        # 计算价格变化
        if old_price is not None and old_price > 0:
            price_change = new_price - old_price
            price_change_pct = (price_change / old_price) * 100
        else:
            price_change = 0.0
            price_change_pct = 0.0

        return cls(
            symbol=symbol,
            new_price=new_price,
            old_price=old_price,
            price_change=price_change,
            price_change_pct=price_change_pct,
            timestamp=timestamp,
            volume=kwargs.get("volume"),
            bid_price=kwargs.get("bid_price"),
            ask_price=kwargs.get("ask_price"),
            extra=kwargs.get("extra", {}),
        )

    @classmethod
    def create_batch(
        cls, prices: Dict[str, float], old_prices: Dict[str, float] | None = None, **kwargs
    ) -> list["PriceChangedEvent"]:
        """
        工厂方法：批量创建价格变更事件

        Args:
            prices: 股票代码 -> 新价格映射
            old_prices: 股票代码 -> 旧价格映射（可选）
            **kwargs: 其他参数（timestamp等）

        Returns:
            List[PriceChangedEvent]: 价格变更事件列表
        """
        events = []
        old_prices = old_prices or {}

        for symbol, new_price in prices.items():
            old_price = old_prices.get(symbol)
            event = cls.create(symbol=symbol, new_price=new_price, old_price=old_price, **kwargs)
            events.append(event)

        return events

    def is_price_up(self) -> bool:
        """价格上涨"""
        return self.price_change > 0

    def is_price_down(self) -> bool:
        """价格下跌"""
        return self.price_change < 0

    def is_significant_change(self, threshold: float = 1.0) -> bool:
        """
        是否为显著变化（默认1%）

        Args:
            threshold: 变化阈值（百分比）

        Returns:
            bool: 是否显著变化
        """
        return abs(self.price_change_pct) >= threshold
