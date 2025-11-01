'''
# 功能：数据源工厂类，负责创建和管理数据源适配器实例
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
'''

from typing import Dict, Type, List
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from interfaces.data_source import IDataSource

# 尝试导入各个适配器，如果失败则跳过
adapters_dict = {}

try:
    from adapters.akshare_adapter import AkshareDataSource
    adapters_dict['akshare'] = AkshareDataSource
except ImportError as e:
    print(f"警告: Akshare适配器导入失败: {e}")

try:
    from adapters.baostock_adapter import BaostockDataSource
    adapters_dict['baostock'] = BaostockDataSource
except ImportError as e:
    print(f"警告: Baostock适配器导入失败: {e}")

try:
    from adapters.customer_adapter import CustomerDataSource
    adapters_dict['customer'] = CustomerDataSource
except ImportError as e:
    print(f"警告: Customer适配器导入失败: {e}")

try:
    from adapters.financial_adapter import FinancialDataSource
    adapters_dict['financial'] = FinancialDataSource
except ImportError as e:
    print(f"警告: Financial适配器导入失败: {e}")

try:
    from adapters.akshare_proxy_adapter import AkshareProxyAdapter
    adapters_dict['akshare_proxy'] = AkshareProxyAdapter
except ImportError as e:
    pass  # 代理适配器是可选的


class DataSourceFactory:
    """数据源工厂：负责创建具体的数据源对象"""

    # 注册的数据源类型（使用成功导入的适配器）
    _source_types: Dict[str, Type[IDataSource]] = adapters_dict.copy()
    
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