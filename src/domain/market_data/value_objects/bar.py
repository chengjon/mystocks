"""
Bar Value Object
K线数据值对象

表示OHLCV格式的K线数据。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Bar:
    """
    K线数据值对象（OHLCV格式）

    职责：
    - 表示OHLCV格式的K线数据
    - 提供K线数据验证
    - 支持不同时间周期（tick, 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly）

    属性：
    - symbol: 标的代码
    - timestamp: 时间戳
    - open: 开盘价
    - high: 最高价
    - low: 最低价
    - close: 收盘价
    - volume: 成交量
    - amount: 成交额（可选）
    - period: 时间周期（可选，如"1min", "daily"等）

    不变量：
    - 开盘价、最高价、最低价、收盘价必须为正数
    - 最高价 >= 最低价
    - 最高价 >= 开盘价、收盘价
    - 最低价 <= 开盘价、收盘价
    - 成交量和成交额必须为非负数
    """

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: Optional[float] = None
    period: Optional[str] = None

    def __post_init__(self):
        """验证K线数据"""
        # 价格必须为正数
        if self.open <= 0:
            raise ValueError(f"Open price must be positive: {self.open}")
        if self.high <= 0:
            raise ValueError(f"High price must be positive: {self.high}")
        if self.low <= 0:
            raise ValueError(f"Low price must be positive: {self.low}")
        if self.close <= 0:
            raise ValueError(f"Close price must be positive: {self.close}")

        # 价格关系验证
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) must be >= low ({self.low})")
        if self.high < self.open:
            raise ValueError(f"High ({self.high}) must be >= open ({self.open})")
        if self.high < self.close:
            raise ValueError(f"High ({self.high}) must be >= close ({self.close})")
        if self.low > self.open:
            raise ValueError(f"Low ({self.low}) must be <= open ({self.open})")
        if self.low > self.close:
            raise ValueError(f"Low ({self.low}) must be <= close ({self.close})")

        # 成交量和成交额必须为非负数
        if self.volume < 0:
            raise ValueError(f"Volume cannot be negative: {self.volume}")
        if self.amount is not None and self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")

    @property
    def is_bullish(self) -> bool:
        """是否阳线（收盘价 > 开盘价）"""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """是否阴线（收盘价 < 开盘价）"""
        return self.close < self.open

    @property
    def body_size(self) -> float:
        """实体大小（收盘价 - 开盘价的绝对值）"""
        return abs(self.close - self.open)

    @property
    def upper_shadow(self) -> float:
        """上影线长度（最高价 - max(开盘价, 收盘价)）"""
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> float:
        """下影线长度（min(开盘价, 收盘价) - 最低价）"""
        return min(self.open, self.close) - self.low

    @property
    def range_pct(self) -> float:
        """振幅百分比（(最高价 - 最低价) / 开盘价 * 100）"""
        return ((self.high - self.low) / self.open) * 100 if self.open > 0 else 0.0

    @property
    def change_pct(self) -> float:
        """涨跌幅百分比（(收盘价 - 开盘价) / 开盘价 * 100）"""
        return ((self.close - self.open) / self.open) * 100 if self.open > 0 else 0.0

    def __str__(self) -> str:
        return (
            f"Bar(symbol={self.symbol}, timestamp={self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, "
            f"O={self.open:.2f}, H={self.high:.2f}, L={self.low:.2f}, C={self.close:.2f}, "
            f"V={self.volume}, change={self.change_pct:.2f}%)"
        )
