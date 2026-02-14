"""Mock 数据管理器包"""
from .core import MockDataCoreMixin
from .extended_data import MockExtendedDataMixin
from .technical_data import MockTechnicalDataMixin


class UnifiedMockDataManager(MockDataCoreMixin, MockExtendedDataMixin, MockTechnicalDataMixin):
    """统一 Mock 数据管理器"""
    pass


__all__ = ["UnifiedMockDataManager"]
