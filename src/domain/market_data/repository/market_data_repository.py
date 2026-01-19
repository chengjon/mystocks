"""
Market Data Repository Interface (ACL)
市场数据仓储接口（防腐层）
"""

from abc import ABC, abstractmethod
from typing import List
from ..value_objects import Bar, Quote


class IMarketDataRepository(ABC):
    """
    市场数据获取接口

    职责:
    - 提供历史K线数据
    - 提供实时报价数据
    - 屏蔽底层数据源的具体实现 (Akshare/Tushare/TDX)
    """

    @abstractmethod
    def get_history_kline(self, symbol: str, start_date: str, end_date: str) -> List[Bar]:
        """获取历史K线"""
        pass

    @abstractmethod
    def get_realtime_quote(self, symbols: List[str]) -> List[Quote]:
        """获取实时行情"""
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        """获取最新价格（便捷方法）"""
        pass
