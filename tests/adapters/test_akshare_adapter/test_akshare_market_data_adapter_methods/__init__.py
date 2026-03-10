"""TestAkshareMarketDataAdapter 方法级拆分包"""
from .part1 import TestAkshareMarketDataAdapterCoreMixin
from .part2 import TestAkshareMarketDataAdapterTestGetStockMixin
from .part3 import TestAkshareMarketDataAdapterAnalyticsMixin


class TestAkshareMarketDataAdapter(
    TestAkshareMarketDataAdapterCoreMixin,
    TestAkshareMarketDataAdapterTestGetStockMixin,
    TestAkshareMarketDataAdapterAnalyticsMixin,
):
    """TestAkshareMarketDataAdapter - 组合所有方法集"""
    pass


__all__ = ["TestAkshareMarketDataAdapter"]
