"""
K线数据值对象
Bar Value Object

表示OHLCV格式的K线数据。
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Bar:
    """
    K线数据值对象

    职责：
    - 表示OHLCV格式的K线数据
    - 提供数据验证

    Attributes:
        symbol: 标的代码
        timestamp: 时间戳
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
    """

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):
        """验证K线数据"""
        if self.open <= 0 or self.high <= 0 or self.low <= 0 or self.close <= 0:
            raise ValueError("Prices must be positive")

        if self.high < max(self.open, self.close):
            raise ValueError(f"High ({self.high}) must be >= open ({self.open}) and close ({self.close})")

        if self.low > min(self.open, self.close):
            raise ValueError(f"Low ({self.low}) must be <= open ({self.open}) and close ({self.close})")

        if self.volume < 0:
            raise ValueError("Volume cannot be negative")

    @property
    def is_bullish(self) -> bool:
        """是否为阳线（收盘价 > 开盘价）"""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """是否为阴线（收盘价 < 开盘价）"""
        return self.close < self.open

    @property
    def body_size(self) -> float:
        """实体大小（收盘价-开盘价的绝对值）"""
        return abs(self.close - self.open)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }
