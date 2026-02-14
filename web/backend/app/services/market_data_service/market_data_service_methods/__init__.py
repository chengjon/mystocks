"""MarketDataService 方法级拆分包"""
from .part1 import MarketDataServiceCoreMixin
from .part2 import MarketDataServiceFetchAndSaveMixin


class MarketDataService(
    MarketDataServiceCoreMixin,
    MarketDataServiceFetchAndSaveMixin,
):
    """MarketDataService - 组合所有方法集"""
    pass


__all__ = ["MarketDataService"]
