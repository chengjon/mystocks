"""
Strategy Templates Package

预置策略模板系统
"""

from app.backtest.strategies.base import BaseStrategy, StrategySignal
from app.backtest.strategies.momentum import MomentumStrategy
from app.backtest.strategies.mean_reversion import MeanReversionStrategy
from app.backtest.strategies.breakout import BreakoutStrategy
from app.backtest.strategies.grid import GridStrategy
from app.backtest.strategies.factory import StrategyFactory

__all__ = [
    "BaseStrategy",
    "StrategySignal",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "BreakoutStrategy",
    "GridStrategy",
    "StrategyFactory",
]
