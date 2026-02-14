"""TDX 数据源适配器包"""
from .core import TdxCoreMixin
from .daily_data import TdxDailyDataMixin
from .basic_block import TdxBasicBlockMixin
from .realtime_misc import TdxRealtimeMiscMixin
from .kline_classify import TdxKlineClassifyMixin


class TdxDataSource(TdxCoreMixin, TdxDailyDataMixin, TdxBasicBlockMixin, TdxRealtimeMiscMixin, TdxKlineClassifyMixin):
    """TDX 数据源"""
    pass


__all__ = ["TdxDataSource"]
