"""
数据源工厂类
通过配置动态切换数据源（Mock / 真实数据）
"""

import os
from typing import Optional
from src.interfaces.data_source_interface import DataSourceInterface
from src.data_sources.mock_data_source import MockDataSource
from src.data_sources.real_data_source import RealDataSource


class DataSourceFactory:
    """
    数据源工厂类
    通过配置动态切换数据源（Mock / 真实数据）
    """
    
    _instance: Optional['DataSourceFactory'] = None
    _data_source: Optional[DataSourceInterface] = None
    
    def __new__(cls) -> 'DataSourceFactory':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._data_source is None:
            self._initialize_data_source()
    
    def _initialize_data_source(self) -> None:
        """
        初始化数据源
        根据环境变量USE_MOCK_DATA决定使用Mock数据还是真实数据
        """
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        if use_mock:
            self._data_source = MockDataSource()
        else:
            self._data_source = RealDataSource()
    
    def get_data_source(self) -> DataSourceInterface:
        """
        获取数据源实例
        
        Returns:
            DataSourceInterface: 数据源实例
        """
        if self._data_source is None:
            self._initialize_data_source()
        return self._data_source
    
    def switch_to_mock(self) -> None:
        """
        切换到Mock数据源
        """
        self._data_source = MockDataSource()
    
    def switch_to_real(self) -> None:
        """
        切换到真实数据源
        """
        self._data_source = RealDataSource()
    
    def is_using_mock(self) -> bool:
        """
        检查当前是否使用Mock数据源
        
        Returns:
            bool: 是否使用Mock数据源
        """
        return isinstance(self._data_source, MockDataSource)


# 全局数据源工厂实例
data_source_factory = DataSourceFactory()


def get_data_source() -> DataSourceInterface:
    """
    获取数据源实例的便捷函数
    
    Returns:
        DataSourceInterface: 数据源实例
    """
    return data_source_factory.get_data_source()