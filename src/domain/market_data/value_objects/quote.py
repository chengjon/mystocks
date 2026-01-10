"""
Quote Value Object
实时报价值对象

表示股票的实时五档行情。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Quote:
    """
    实时报价值对象

    职责：
    - 表示股票的实时五档行情
    - 提供实时报价验证
    - 支持买卖五档

    属性：
    - symbol: 标的代码
    - timestamp: 时间戳
    - last_price: 最新价
    - bid_price: 买一价
    - bid_volume: 买一量
    - ask_price: 卖一价
    - ask_volume: 卖一量
    - open_price: 开盘价
    - high_price: 最高价
    - low_price: 最低价
    - volume: 成交量
    - amount: 成交额

    不变量：
    - 价格必须为正数（如果提供）
    - 成交量和成交额必须为非负数
    - 买一价 <= 卖一价（如果两者都提供）
    """

    symbol: str
    timestamp: datetime
    last_price: float
    bid_price: Optional[float] = None
    bid_volume: Optional[int] = None
    ask_price: Optional[float] = None
    ask_volume: Optional[int] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
    amount: Optional[float] = None

    def __post_init__(self):
        """验证实时报价"""
        # 最新价必须为正数
        if self.last_price <= 0:
            raise ValueError(f"Last price must be positive: {self.last_price}")

        # 买一价和卖一价必须为正数（如果提供）
        if self.bid_price is not None and self.bid_price <= 0:
            raise ValueError(f"Bid price must be positive: {self.bid_price}")

        if self.ask_price is not None and self.ask_price <= 0:
            raise ValueError(f"Ask price must be positive: {self.ask_price}")

        # 买一量必须为非负数（如果提供）
        if self.bid_volume is not None and self.bid_volume < 0:
            raise ValueError(f"Bid volume cannot be negative: {self.bid_volume}")

        # 卖一量必须为非负数（如果提供）
        if self.ask_volume is not None and self.ask_volume < 0:
            raise ValueError(f"Ask volume cannot be negative: {self.ask_volume}")

        # 买一价 <= 卖一价（如果两者都提供）
        if self.bid_price is not None and self.ask_price is not None:
            if self.bid_price > self.ask_price:
                raise ValueError(
                    f"Bid price ({self.bid_price}) must be <= ask price ({self.ask_price})"
                )

        # 开盘价、最高价、最低价必须为正数（如果提供）
        if self.open_price is not None and self.open_price <= 0:
            raise ValueError(f"Open price must be positive: {self.open_price}")

        if self.high_price is not None and self.high_price <= 0:
            raise ValueError(f"High price must be positive: {self.high_price}")

        if self.low_price is not None and self.low_price <= 0:
            raise ValueError(f"Low price must be positive: {self.low_price}")

        # 成交量和成交额必须为非负数（如果提供）
        if self.volume is not None and self.volume < 0:
            raise ValueError(f"Volume cannot be negative: {self.volume}")

        if self.amount is not None and self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")

    @property
    def spread(self) -> Optional[float]:
        """买卖价差（卖一价 - 买一价）"""
        if self.bid_price is not None and self.ask_price is not None:
            return self.ask_price - self.bid_price
        return None

    @property
    def spread_pct(self) -> Optional[float]:
        """买卖价差百分比（价差 / 买一价 * 100）"""
        if self.spread is not None and self.bid_price is not None and self.bid_price > 0:
            return (self.spread / self.bid_price) * 100
        return None

    @property
    def mid_price(self) -> Optional[float]:
        """中间价（(买一价 + 卖一价) / 2）"""
        if self.bid_price is not None and self.ask_price is not None:
            return (self.bid_price + self.ask_price) / 2.0
        return None

    @property
    def change_from_open(self) -> Optional[float]:
        """距开盘价变化（最新价 - 开盘价）"""
        if self.open_price is not None:
            return self.last_price - self.open_price
        return None

    @property
    def change_pct_from_open(self) -> Optional[float]:
        """距开盘价变化百分比（(最新价 - 开盘价) / 开盘价 * 100）"""
        if self.open_price is not None and self.open_price > 0:
            return ((self.last_price - self.open_price) / self.open_price) * 100
        return None

    def __str__(self) -> str:
        return (
            f"Quote(symbol={self.symbol}, last={self.last_price:.2f}, "
            f"bid={self.bid_price:.2f if self.bid_price else 'N/A'} "
            f"({self.bid_volume if self.bid_volume else 'N/A'}), "
            f"ask={self.ask_price:.2f if self.ask_price else 'N/A'} "
            f"({self.ask_volume if self.ask_volume else 'N/A'}))"
        )
