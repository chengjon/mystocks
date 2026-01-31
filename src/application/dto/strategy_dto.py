"""
Strategy Application DTOs
"""

from typing import List

from pydantic import BaseModel


class BacktestRequest(BaseModel):
    """回测请求"""

    strategy_id: str
    symbols: List[str]
    start_date: str
    end_date: str
    initial_cash: float = 100000.0


class SignalDTO(BaseModel):
    """交易信号 DTO"""

    symbol: str
    side: str
    price: float
    reason: str
    timestamp: float


class BacktestResultDTO(BaseModel):
    """回测结果"""

    total_returns: float
    sharpe_ratio: float
    max_drawdown: float
    signal_count: int
    trade_count: int
