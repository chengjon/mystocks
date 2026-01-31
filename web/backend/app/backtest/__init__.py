"""
Backtest Engine Package

事件驱动的回测引擎系统，用于策略回测和性能评估
"""

from app.backtest.backtest_engine import BacktestEngine
from app.backtest.events import Event, FillEvent, MarketEvent, OrderEvent, SignalEvent
from app.backtest.execution_handler import ExecutionHandler
from app.backtest.performance_metrics import PerformanceMetrics
from app.backtest.portfolio_manager import PortfolioManager
from app.backtest.risk_manager import RiskManager

__all__ = [
    "Event",
    "MarketEvent",
    "SignalEvent",
    "OrderEvent",
    "FillEvent",
    "BacktestEngine",
    "PortfolioManager",
    "RiskManager",
    "ExecutionHandler",
    "PerformanceMetrics",
]
