"""
Market Data Context Value Objects
定义标准化的行情数据结构
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Bar:
    """K线数据 (OHLCV)"""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    frequency: str = "1d"  # 1d, 1m, 5m, etc.


@dataclass(frozen=True)
class Tick:
    """分笔数据 (逐笔交易)"""

    symbol: str
    timestamp: datetime
    price: float
    volume: int
    direction: int  # 1: Buy, -1: Sell, 0: Neutral


@dataclass(frozen=True)
class Quote:
    """实时报价 (盘口数据)"""

    symbol: str
    timestamp: datetime
    last_price: float
    open_price: float
    high_price: float
    low_price: float
    prev_close: float
    volume: float
    amount: float
    # 简化的五档盘口
    bid_price1: float
    bid_volume1: int
    ask_price1: float
    ask_volume1: int
