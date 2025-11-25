"""
MyStocks重构版接口定义 - 接口分离和简化
基于Interface Segregation Principle的现代化接口设计

版本: 3.0.0
创建日期: 2025-11-14
作者: Claude Code
"""

import abc
import pandas as pd
from typing import Dict, List, Union, Optional, Any
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# 标准化响应格式
# =============================================================================

@dataclass
class DataResponse:
    """标准数据响应格式 - 统一所有数据源的返回格式"""
    
    success: bool
    data: Optional[Union[pd.DataFrame, Dict, List, str]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
    
    @classmethod
    def create_success(cls, data: Union[pd.DataFrame, Dict, List, str], metadata: Optional[Dict] = None) -> 'DataResponse':
        """创建成功响应"""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def create_error(cls, error_msg: str, metadata: Optional[Dict] = None) -> 'DataResponse':
        """创建错误响应"""
        return cls(success=False, error=error_msg, metadata=metadata)
    
    @classmethod
    def empty(cls, message: str = "No data available") -> 'DataResponse':
        """创建空数据响应"""
        return cls(success=False, error=message)


# =============================================================================
# 核心价格数据接口 (所有数据源必须实现)
# =============================================================================

class IPriceDataSource(abc.ABC):
    """核心价格数据接口 - 所有数据源的基础要求
    
    这个接口定义了数据源必须实现的核心价格数据功能。
    所有适配器必须实现这些基础方法。
    """

    @abc.abstractmethod
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> DataResponse:
        """获取股票日线数据
        
        Args:
            symbol: 股票代码，如 '600000', '000001'
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            DataResponse: 包含日线数据的响应
                - success=True时，data为包含['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'amount']的DataFrame
                - success=False时，error包含错误信息
        """
        pass
    
    @abc.abstractmethod  
    def get_real_time_data(self, symbol: str) -> DataResponse:
        """获取实时数据
        
        Args:
            symbol: 股票代码，如 '600000', '000001'
            
        Returns:
            DataResponse: 包含实时数据的响应
                - success=True时，data为包含最新价格、成交量等信息的字典
                - success=False时，error包含错误信息
        """
        pass


# =============================================================================
# 指数数据接口 (可选实现)
# =============================================================================

class IIndexDataSource(abc.ABC):
    """指数数据接口 - 仅需要指数功能的实现
    
    这个接口定义了指数相关的功能。
    仅当数据源支持指数数据时才需要实现。
    """

    @abc.abstractmethod
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> DataResponse:
        """获取指数日线数据
        
        Args:
            symbol: 指数代码，如 '000001', '399001'
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            DataResponse: 包含指数日线数据的响应
        """
        pass
    
    @abc.abstractmethod
    def get_index_components(self, symbol: str) -> DataResponse:
        """获取指数成分股
        
        Args:
            symbol: 指数代码，如 '000001', '399001'
            
        Returns:
            DataResponse: 包含成分股列表的响应
                - success=True时，data为包含股票代码的List[str]
                - success=False时，error包含错误信息
        """
        pass


# =============================================================================
# 基础信息接口 (可选实现)
# =============================================================================

class IBasicInfoSource(abc.ABC):
    """基础信息接口 - 仅需要基础信息的实现
    
    这个接口定义了股票基本信息和市场日历等基础功能。
    仅当数据源支持基础信息时才需要实现。
    """

    @abc.abstractmethod
    def get_stock_basic(self, symbol: str) -> DataResponse:
        """获取股票基本信息
        
        Args:
            symbol: 股票代码，如 '600000', '000001'
            
        Returns:
            DataResponse: 包含股票基本信息的响应
                - success=True时，data为包含['code', 'name', 'industry', 'area']等信息的字典
                - success=False时，error包含错误信息
        """
        pass
    
    @abc.abstractmethod
    def get_market_calendar(self, start_date: str, end_date: str) -> DataResponse:
        """获取交易日历
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            DataResponse: 包含交易日历的响应
                - success=True时，data为包含交易日信息的DataFrame
                - success=False时，error包含错误信息
        """
        pass


# =============================================================================
# 高级数据接口 (可选实现)
# =============================================================================

class IAdvancedDataSource(abc.ABC):
    """高级数据接口 - 需要财务和新闻数据的实现
    
    这个接口定义了财务数据和新闻数据等高级功能。
    仅当数据源支持高级数据时才需要实现。
    """

    @abc.abstractmethod
    def get_financial_data(self, symbol: str, period: str = "annual") -> DataResponse:
        """获取财务数据
        
        Args:
            symbol: 股票代码，如 '600000', '000001'
            period: 报告期间，"annual"(年度)或"quarterly"(季度)
            
        Returns:
            DataResponse: 包含财务数据的响应
                - success=True时，data为包含财务指标的DataFrame
                - success=False时，error包含错误信息
        """
        pass
    
    @abc.abstractmethod
    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> DataResponse:
        """获取新闻数据
        
        Args:
            symbol: 股票代码，为None时获取市场新闻
            limit: 返回数量限制，默认10条
            
        Returns:
            DataResponse: 包含新闻数据的响应
                - success=True时，data为包含新闻信息的List[Dict]
                - success=False时，error包含错误信息
        """
        pass


# =============================================================================
# 组合接口 (向后兼容)
# =============================================================================

class IDataSource(IPriceDataSource, IIndexDataSource, IBasicInfoSource, IAdvancedDataSource):
    """完整数据接口 - 向后兼容的组合接口
    
    这个接口提供了完整的向后兼容性。
    现有代码可以继续使用这个接口，新的适配器可以选择实现特化的子接口。
    
    注意: 实现这个接口需要实现所有8个方法。
    建议新开发的数据源实现相应的特化接口。
    """
    pass


# =============================================================================
# 适配器工厂模式 (支持接口版本管理)
# =============================================================================

class DataSourceFactory:
    """数据源工厂 - 支持接口版本管理和动态适配"""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, data_source_class: type):
        """注册数据源类"""
        cls._registry[name] = data_source_class
    
    @classmethod
    def create(cls, name: str, **kwargs) -> IPriceDataSource:
        """创建数据源实例"""
        if name not in cls._registry:
            raise ValueError(f"Unknown data source: {name}")
        
        return cls._registry[name](**kwargs)
    
    @classmethod
    def get_supported_sources(cls) -> List[str]:
        """获取支持的数据源列表"""
        return list(cls._registry.keys())


# =============================================================================
# 实用工具函数
# =============================================================================

def validate_symbol(symbol: str) -> bool:
    """验证股票代码格式
    
    Args:
        symbol: 股票代码
        
    Returns:
        bool: 是否为有效的股票代码格式
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # 基本的股票代码格式检查 (6位数字)
    return len(symbol) == 6 and symbol.isdigit()


def validate_date(date_str: str) -> bool:
    """验证日期格式
    
    Args:
        date_str: 日期字符串
        
    Returns:
        bool: 是否为有效的日期格式 (YYYY-MM-DD)
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def standardize_response(data: Union[pd.DataFrame, Dict, List], 
                        metadata: Optional[Dict] = None) -> DataResponse:
    """标准化响应格式
    
    Args:
        data: 要包装的数据
        metadata: 元数据信息
        
    Returns:
        DataResponse: 标准化的响应
    """
    return DataResponse.create_success(data=data, metadata=metadata)


# =============================================================================
# 示例实现
# =============================================================================

class BaseDataSource(IPriceDataSource):
    """数据源基类 - 提供通用功能"""
    
    def __init__(self, name: str):
        self.name = name
        self._initialized = False
    
    def _validate_inputs(self, symbol: str, start_date: str, end_date: str) -> Optional[str]:
        """验证输入参数"""
        if not validate_symbol(symbol):
            return f"Invalid symbol format: {symbol}"
        
        if not validate_date(start_date):
            return f"Invalid start_date format: {start_date}"
            
        if not validate_date(end_date):
            return f"Invalid end_date format: {end_date}"
        
        return None
    
    def _create_error_response(self, error: str) -> DataResponse:
        """创建错误响应"""
        return DataResponse.create_error(error_msg=error, metadata={"source": self.name})


# =============================================================================
# 测试代码
# =============================================================================

if __name__ == "__main__":
    # 测试DataResponse
    print("=== 测试DataResponse ===")
    
    # 成功响应
    success_resp = DataResponse.create_success(data={"test": "data"})
    print(f"成功响应: {success_resp}")

    # 错误响应
    error_resp = DataResponse.create_error(error_msg="Test error")
    print(f"错误响应: {error_resp}")
    
    # 测试验证函数
    print("\n=== 测试验证函数 ===")
    print(f"有效股票代码 '600000': {validate_symbol('600000')}")
    print(f"无效股票代码 'ABC': {validate_symbol('ABC')}")
    print(f"有效日期 '2024-01-01': {validate_date('2024-01-01')}")
    print(f"无效日期 '2024/01/01': {validate_date('2024/01/01')}")
    
    # 测试工厂模式
    print("\n=== 测试工厂模式 ===")
    print(f"支持的源列表: {DataSourceFactory.get_supported_sources()}")