"""数据库服务包"""

from .stock_queries import StockQueriesMixin
from .technical_queries import TechnicalQueriesMixin
from .signal_history_queries import SignalHistoryQueriesMixin
from .strategy_queries import StrategyQueriesMixin
from .adapter_queries import AdapterQueriesMixin


class DatabaseService(
    StockQueriesMixin,
    TechnicalQueriesMixin,
    SignalHistoryQueriesMixin,
    StrategyQueriesMixin,
    AdapterQueriesMixin,
):
    """通用数据库服务类"""
    pass


__all__ = ["DatabaseService"]
