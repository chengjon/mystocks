"""
新数据源注册演示脚本
展示如何注册和使用新的数据源

包含的数据源:
1. TushareDataSource - Tushare数据源
2. EfinanceDataSource - 东方财富数据源 
3. EasyquotationDataSource - 实时行情数据源
4. BiyingapiDataSource - 必应API数据源
5. CustomDataSource - 自定义爬虫数据源
"""
import sys
import os
import pandas as pd
from typing import Dict, List, Union, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from factory.data_source_factory import DataSourceFactory
from manager.unified_data_manager import UnifiedDataManager
from interfaces.data_source import IDataSource
from utils.column_mapper import ColumnMapper


# 示例：自定义数据源实现
class CustomDataSource(IDataSource):
    """自定义数据源 - 可以是爬虫或其他数据来源"""
    
    def __init__(self):
        print("自定义数据源初始化完成")
        self.available = True
    
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """返回模拟的股票数据"""
        return pd.DataFrame({
            '日期': ['2023-08-01', '2023-08-02'], 
            '股票代码': [symbol, symbol],
            '开盘': [10.0, 10.5],
            '收盘': [10.2, 10.8],
            '最高': [10.5, 11.0],
            '最低': [9.8, 10.2],
            '成交量': [1000000, 1200000],
            '涨跌幅': [1.5, 2.8]
        })
    
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """返回模拟的指数数据"""
        return pd.DataFrame({
            '日期': ['2023-08-01', '2023-08-02'],
            '指数代码': [symbol, symbol],
            '开盘': [3000.0, 3050.0],
            '收盘': [3020.0, 3080.0]
        })
    
    def get_stock_basic(self, symbol: str) -> Dict:
        """返回模拟的基本信息"""
        return {
            '股票代码': symbol,
            '股票名称': f'自定义股票_{symbol}',
            '行业': '自定义行业'
        }
    
    def get_index_components(self, symbol: str) -> List[str]:
        """返回模拟的成分股"""
        return ['600000', '000001', '000002']
    
    def get_real_time_data(self, symbol: str) -> Union[Dict, str]:
        """返回模拟的实时数据"""
        return {
            'symbol': symbol,
            'price': 10.50,
            'change': 0.30,
            'pct_chg': 2.94,
            'timestamp': '2023-08-01 15:00:00'
        }
    
    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        """返回模拟的交易日历"""
        return pd.DataFrame({
            '日期': ['2023-08-01', '2023-08-02'],
            '是否交易日': [1, 1]
        })
    
    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        """返回模拟的财务数据"""
        return pd.DataFrame({
            '股票代码': [symbol],
            '营业收入': [1000000000],
            '净利润': [100000000]
        })
    
    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> Union[List[Dict], str]:
        """返回模拟的新闻数据"""
        return [
            {
                'title': '自定义新闻标题1',
                'content': '新闻内容1',
                'timestamp': '2023-08-01 10:00:00'
            },
            {
                'title': '自定义新闻标题2', 
                'content': '新闻内容2',
                'timestamp': '2023-08-01 11:00:00'
            }
        ]


class EfinanceDataSource(IDataSource):
    """东方财富数据源模板"""
    
    def __init__(self):
        print("东方财富数据源初始化完成")
        # 这里可以添加efinance的初始化逻辑
        
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # 实现efinance的股票数据获取
        return pd.DataFrame()
    
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return pd.DataFrame()
    
    def get_stock_basic(self, symbol: str) -> Dict:
        return {}
    
    def get_index_components(self, symbol: str) -> List[str]:
        return []
    
    def get_real_time_data(self, symbol: str) -> Union[Dict, str]:
        return {}
    
    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        return pd.DataFrame()
    
    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        return pd.DataFrame()
    
    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> Union[List[Dict], str]:
        return []


def register_all_new_sources():
    """注册所有新数据源"""
    
    print("=" * 60)
    print("新数据源注册演示")
    print("=" * 60)
    
    # 方法1: 单个注册
    print("\n1. 单个注册数据源:")
    DataSourceFactory.register_source('custom', CustomDataSource)
    DataSourceFactory.register_source('efinance', EfinanceDataSource)
    
    # 方法2: 批量注册
    print("\n2. 批量注册数据源:")
    
    # 注意：以下数据源需要相应的适配器实现
    new_sources = {
        # 'tushare': TushareDataSource,  # 需要导入
        # 'easyquotation': EasyquotationDataSource,  # 需要实现
        # 'biyingapi': BiyingapiDataSource,  # 需要实现
    }
    
    if new_sources:
        DataSourceFactory.register_multiple_sources(new_sources)
    
    # 显示所有可用数据源
    print(f"\n3. 当前可用数据源: {DataSourceFactory.get_available_sources()}")
    
    return DataSourceFactory.get_available_sources()


def test_new_data_sources():
    """测试新注册的数据源"""
    
    print("\n" + "=" * 60)
    print("新数据源功能测试")
    print("=" * 60)
    
    # 创建统一数据管理器
    manager = UnifiedDataManager()
    
    # 测试自定义数据源
    print("\n测试自定义数据源:")
    try:
        # 获取原始数据
        raw_data = manager.get_stock_daily('600000', '2023-08-01', '2023-08-02', source_type='custom')
        print("原始数据:")
        print(raw_data)
        
        # 使用列名映射器标准化
        if not raw_data.empty:
            print("\n标准化为英文列名:")
            en_data = ColumnMapper.to_english(raw_data)
            print(en_data)
            
            print("\n标准化为中文列名:")
            cn_data = ColumnMapper.to_chinese(en_data)
            print(cn_data)
            
        # 测试其他功能
        print("\n测试实时数据:")
        real_time = manager.get_source('custom').get_real_time_data('600000')
        print(real_time)
        
        print("\n测试新闻数据:")
        news = manager.get_source('custom').get_news_data('600000', limit=2)
        print(news)
        
    except Exception as e:
        print(f"测试失败: {e}")


def test_column_mapping():
    """测试列名映射功能"""
    
    print("\n" + "=" * 60)
    print("列名映射功能测试")
    print("=" * 60)
    
    # 创建测试数据 - 模拟不同数据源的列名格式
    test_cases = [
        # AKShare格式
        pd.DataFrame({
            "日期": ["2023-08-01"],
            "股票代码": ["600000"],
            "开盘": [10.0],
            "收盘": [10.2],
            "成交量": [1000000],
            "涨跌幅": [1.5]
        }),
        
        # Baostock格式
        pd.DataFrame({
            "date": ["2023-08-01"],
            "code": ["600000"],
            "open": [10.0],
            "close": [10.2],
            "volume": [1000000],
            "pctChg": [1.5]
        }),
        
        # Tushare格式
        pd.DataFrame({
            "trade_date": ["20230801"],
            "ts_code": ["600000.SH"],
            "open": [10.0],
            "close": [10.2],
            "vol": [100],  # 注意：Tushare的成交量单位不同
            "pct_chg": [1.5]
        })
    ]
    
    for i, test_df in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print("原始数据:")
        print(test_df)
        
        print("转换为标准英文列名:")
        en_df = ColumnMapper.to_english(test_df)
        print(en_df)
        
        print("转换为标准中文列名:")
        cn_df = ColumnMapper.to_chinese(en_df)
        print(cn_df)
        
        # 验证列名
        required_cols = ColumnMapper.get_standard_columns("stock_daily", "en")
        is_valid, missing, extra = ColumnMapper.validate_columns(en_df, required_cols)
        print(f"列名验证: 通过={is_valid}, 缺失={missing}, 额外={extra}")


def main():
    """主函数"""
    
    # 1. 注册新数据源
    available_sources = register_all_new_sources()
    
    # 2. 测试新数据源
    test_new_data_sources()
    
    # 3. 测试列名映射
    test_column_mapping()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print(f"当前系统支持的数据源: {available_sources}")
    print("\n要添加新数据源，请按以下步骤操作:")
    print("1. 创建实现IDataSource接口的适配器类")
    print("2. 使用DataSourceFactory.register_source()注册")
    print("3. 使用ColumnMapper标准化列名") 
    print("4. 通过UnifiedDataManager统一调用")


if __name__ == "__main__":
    main()