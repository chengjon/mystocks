"""
数据源工厂
负责创建具体的数据源对象

作用：
- 实现工厂模式，根据类型名称创建对应的数据源实例
- 管理已注册的数据源类型
- 提供注册新数据源的机制
- 隐藏数据源创建的复杂性

功能：
- 负责实例化具体的数据源适配器
- 使系统可以动态选择和切换不同的数据源
- 提供统一的创建接口，降低系统耦合度
- 支持运行时注册新的数据源类型
"""
from typing import Dict, Type, List
import sys
import os

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mystocks.interfaces.data_source import IDataSource
from mystocks.adapters.akshare_adapter import AkshareDataSource
from mystocks.adapters.baostock_adapter import BaostockDataSource
# 为新数据源预留导入空间
# from mystocks.adapters.tushare_adapter import TushareDataSource
# from mystocks.adapters.efinance_adapter import EfinanceDataSource  
# from mystocks.adapters.easyquotation_adapter import EasyquotationDataSource
# from mystocks.adapters.biyingapi_adapter import BiyingapiDataSource
# from mystocks.adapters.custom_adapter import CustomDataSource
from mystocks.adapters.customer_adapter import CustomerDataSource
from mystocks.adapters.financial_adapter import FinancialDataSource


class DataSourceFactory:
    """数据源工厂：负责创建具体的数据源对象"""
    
    # 注册的数据源类型
    _source_types: Dict[str, Type[IDataSource]] = {
        'akshare': AkshareDataSource,
        'baostock': BaostockDataSource,
        'customer': CustomerDataSource,
        'financial': FinancialDataSource
    }
    
    @classmethod
    def register_source(cls, source_type: str, source_class: Type[IDataSource]) -> None:
        """
        注册新的数据源类型
        
        Args:
            source_type: 数据源类型名称
            source_class: 数据源类
        """
        cls._source_types[source_type.lower()] = source_class
        print(f"已注册数据源类型: {source_type}")
    
    @classmethod
    def register_multiple_sources(cls, sources: Dict[str, Type[IDataSource]]) -> None:
        """
        批量注册多个数据源
        
        Args:
            sources: 数据源字典，{source_type: source_class}
        """
        for source_type, source_class in sources.items():
            cls.register_source(source_type, source_class)
    
    @classmethod
    def get_available_sources(cls) -> List[str]:
        """
        获取所有可用的数据源类型
        
        Returns:
            List[str]: 数据源类型列表
        """
        return list(cls._source_types.keys())
    
    @classmethod
    def unregister_source(cls, source_type: str) -> bool:
        """
        取消注册数据源
        
        Args:
            source_type: 数据源类型名称
            
        Returns:
            bool: 是否成功取消注册
        """
        source_type = source_type.lower()
        if source_type in cls._source_types:
            del cls._source_types[source_type]
            print(f"已取消注册数据源: {source_type}")
            return True
        return False
    
    @classmethod
    def create_source(cls, source_type: str) -> IDataSource:
        """
        根据类型创建数据源
        
        Args:
            source_type: 数据源类型名称，如 'akshare' 或 'baostock'
            
        Returns:
            IDataSource: 实现了IDataSource接口的对象
            
        Raises:
            ValueError: 如果指定的数据源类型不存在
        """
        source_type = source_type.lower()
        if source_type not in cls._source_types:
            raise ValueError(f"不支持的数据源类型: {source_type}")
        
        # 创建并返回数据源实例
        try:
            return cls._source_types[source_type]()
        except Exception as e:
            print(f"创建数据源 {source_type} 失败: {e}")
            raise ValueError(f"数据源 {source_type} 创建失败: {e}")