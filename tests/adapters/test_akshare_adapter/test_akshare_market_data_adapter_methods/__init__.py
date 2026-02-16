"""TestAkshareMarketDataAdapter 方法级拆分包"""
from .part1 import TestAkshareMarketDataAdapterCoreMixin
from .part2 import TestAkshareMarketDataAdapterTestGetStockMixin


class TestAkshareMarketDataAdapter(
    TestAkshareMarketDataAdapterCoreMixin,
    TestAkshareMarketDataAdapterTestGetStockMixin,
):
    """TestAkshareMarketDataAdapter - 组合所有方法集"""
    pass


__all__ = ["TestAkshareMarketDataAdapter"]
