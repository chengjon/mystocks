"""MarketDataService 方法级拆分包"""

from .part1 import MarketDataServiceCoreMixin
from .part2 import MarketDataServiceFetchAndSaveMixin
from .part3 import MarketDataServiceChipRaceQueryMixin


class MarketDataService(
    MarketDataServiceCoreMixin,
    MarketDataServiceFetchAndSaveMixin,
    MarketDataServiceChipRaceQueryMixin,
):
    """MarketDataService - 组合所有方法集"""


__all__ = ["MarketDataService"]
