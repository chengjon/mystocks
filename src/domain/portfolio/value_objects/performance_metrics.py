"""
Portfolio Context Value Objects
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class PerformanceMetrics:
    """绩效指标值对象 - 简化版，用于演示"""
    total_return: float     # 总收益率百分比 (例如 10.5 表示 +10.5%)
    holdings_value: float   # 持仓市值
    cash_balance: float     # 现金余额
    win_rate: float         # 胜率百分比
    trade_count: int        # 交易次数
    calculated_at: datetime = datetime.now()

@dataclass(frozen=True)
class DetailedPerformanceMetrics:
    """详细绩效指标值对象 - 用于完整分析"""
    total_value: float      # 总资产
    total_return: float     # 总收益额
    return_rate: float      # 收益率 (0.1 = 10%)
    daily_pnl: float        # 当日盈亏
    max_drawdown: float     # 最大回撤 (0.2 = 20%)
    sharpe_ratio: Optional[float] = None
    calculated_at: datetime = datetime.now()

@dataclass
class PositionInfo:
    """
    组合内的持仓信息
    注意：这是 Portfolio Context 内部的持仓视图，区别于 Trading Context 的 Position
    这里更关注市值和占比
    """
    symbol: str
    quantity: int
    average_cost: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.average_cost) * self.quantity