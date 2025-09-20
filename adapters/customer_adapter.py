"""
Customer 数据源适配器
实现了统一数据接口，提供 efinance 和 easyquotation 数据访问

示例用法：
    >>> from mystocks.adapters.customer_adapter import CustomerDataSource
    >>> adapter = CustomerDataSource()
    >>> data = adapter.get_real_time_data("sh")  # 获取上海市场实时数据
"""
import pandas as pd
from typing import Dict, List, Optional, Union
import sys
import os

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mystocks.interfaces.data_source import IDataSource


class CustomerDataSource(IDataSource):
    """Customer数据源实现（统一管理efinance和easyquotation）
    
    属性:
        efinance_available (bool): efinance库是否可用
        easyquotation_available (bool): easyquotation库是否可用
    """
    
    def __init__(self):
        """初始化Customer数据源"""
        self.efinance_available = False
        self.easyquotation_available = False
        
        # 尝试导入efinance
        try:
            import efinance as ef
            self.ef = ef
            self.efinance_available = True
            print("[Customer] efinance库导入成功")
        except ImportError:
            print("[Customer] efinance库未安装，相关功能不可用")
        except Exception as e:
            print(f"[Customer] efinance库导入失败: {e}")
            
        # 尝试导入easyquotation
        try:
            import easyquotation as eq
            self.eq = eq
            self.easyquotation_available = True
            print("[Customer] easyquotation库导入成功")
        except ImportError:
            print("[Customer] easyquotation库未安装，相关功能不可用")
        except Exception as e:
            print(f"[Customer] easyquotation库导入失败: {e}")
            
        print(f"[Customer] 数据源初始化完成 (efinance: {'可用' if self.efinance_available else '不可用'}, easyquotation: {'可用' if self.easyquotation_available else '不可用'})")
        
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据-Customer实现"""
        print(f"[Customer] 尝试获取股票日线数据: {symbol}")
        
        # efinance实现
        if self.efinance_available:
            try:
                print("[Customer] 使用efinance获取股票日线数据")
                # 使用正确的efinance API获取日线数据
                # klt=101表示日K线数据
                df = self.ef.stock.get_quote_history(symbol, beg=start_date, end=end_date, klt=101)
                if df is not None and not df.empty:
                    print(f"[Customer] efinance获取到{len(df)}行数据")
                    return df
            except Exception as e:
                print(f"[Customer] efinance获取股票日线数据失败: {e}")
        
        # easyquotation实现（如果efinance不可用）
        if self.easyquotation_available:
            try:
                print("[Customer] 使用easyquotation获取股票日线数据")
                # 注意：easyquotation主要用于实时数据，历史数据可能需要其他方式获取
                # 这里只是一个示例实现
                quotation = self.eq.use('sina')  # 使用sina源
                data = quotation.real([symbol])  # 获取实时数据
                if data:
                    # 转换为DataFrame格式
                    df = pd.DataFrame([data[symbol]])
                    print(f"[Customer] easyquotation获取到{len(df)}行数据")
                    return df
            except Exception as e:
                print(f"[Customer] easyquotation获取股票日线数据失败: {e}")
        
        print("[Customer] 所有方法均未能获取到股票日线数据")
        return pd.DataFrame()
    
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据-Customer实现"""
        print(f"[Customer] 尝试获取指数日线数据: {symbol}")
        
        # efinance实现
        if self.efinance_available:
            try:
                print("[Customer] 使用efinance获取指数日线数据")
                # 注意：需要根据efinance的实际API调整
                df = self.ef.index.get_quote_history(symbol, start_date, end_date)
                if df is not None and not df.empty:
                    print(f"[Customer] efinance获取到{len(df)}行数据")
                    return df
            except Exception as e:
                print(f"[Customer] efinance获取指数日线数据失败: {e}")
        
        print("[Customer] 未能获取到指数日线数据")
        return pd.DataFrame()
    
    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息-Customer实现"""
        print(f"[Customer] 尝试获取股票基本信息: {symbol}")
        
        # efinance实现
        if self.efinance_available:
            try:
                print("[Customer] 使用efinance获取股票基本信息")
                # 使用正确的efinance API获取股票基本信息
                info = self.ef.stock.get_base_info(symbol)
                if info is not None:
                    print("[Customer] efinance获取到股票基本信息")
                    # 将pandas.Series转换为字典
                    return info.to_dict() if hasattr(info, 'to_dict') else dict(info)
            except Exception as e:
                print(f"[Customer] efinance获取股票基本信息失败: {e}")
        
        print("[Customer] 未能获取到股票基本信息")
        return {}
    
    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股-Customer实现"""
        print(f"[Customer] 尝试获取指数成分股: {symbol}")
        
        # efinance实现
        if self.efinance_available:
            try:
                print("[Customer] 使用efinance获取指数成分股")
                # 注意：需要根据efinance的实际API调整
                components = self.ef.index.get_index_components(symbol)
                if components:
                    print(f"[Customer] efinance获取到{len(components)}个成分股")
                    return components
            except Exception as e:
                print(f"[Customer] efinance获取指数成分股失败: {e}")
        
        print("[Customer] 未能获取到指数成分股")
        return []
    
    def get_real_time_data(self, symbol: str) -> Union[pd.DataFrame, Dict, str]:
        """获取实时数据-Customer实现（重点实现efinance的沪深市场A股最新状况功能）"""
        print(f"[Customer] 尝试获取实时数据: {symbol}")
        
        # efinance实现 - 沪深市场A股最新状况
        if self.efinance_available:
            try:
                print("[Customer] 使用efinance获取沪深市场A股最新状况")
                # 根据用户需求，使用efinance获取实时行情数据
                if symbol.lower() in ['sh', 'sz', 'hs']:  # 市场代码
                    # 获取沪深市场A股最新状况
                    df = self.ef.stock.get_realtime_quotes()
                    if df is not None and not df.empty:
                        print(f"[Customer] efinance获取到{len(df)}行实时数据")
                        # 返回DataFrame
                        return df
                else:
                    # 获取特定股票的实时数据
                    # 使用正确的API获取单个股票的实时数据
                    df = self.ef.stock.get_quote_history(symbol, klt=1)  # klt=1表示1分钟K线，可以获取最新数据
                    if df is not None and not df.empty:
                        # 获取最新的数据行
                        latest_data = df.tail(1)
                        print(f"[Customer] efinance获取到股票{symbol}的实时数据")
                        return latest_data.to_dict('records')[0] if len(latest_data) > 0 else {}
            except Exception as e:
                print(f"[Customer] efinance获取实时数据失败: {e}")
        
        # easyquotation实现
        if self.easyquotation_available:
            try:
                print("[Customer] 使用easyquotation获取实时数据")
                quotation = self.eq.use('sina')  # 使用sina源
                
                if symbol.lower() in ['sh', 'sz', 'hs']:  # 市场代码
                    # 获取市场整体数据
                    # 注意：easyquotation主要用于个股数据，市场整体数据可能需要特殊处理
                    data = quotation.market_snapshot(prefix=True)  # 获取市场快照
                    if data:
                        print("[Customer] easyquotation获取到市场快照数据")
                        return data
                else:
                    # 获取特定股票的实时数据
                    data = quotation.real([symbol])
                    if data:
                        print(f"[Customer] easyquotation获取到股票{symbol}的实时数据")
                        return data.get(symbol, {})
            except Exception as e:
                print(f"[Customer] easyquotation获取实时数据失败: {e}")
        
        print("[Customer] 未能获取到实时数据")
        return {}
    
    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        """获取交易日历-Customer实现"""
        print(f"[Customer] 尝试获取交易日历: {start_date} to {end_date}")
        
        # 暂时没有直接的实现，返回空DataFrame
        print("[Customer] 交易日历功能暂未实现")
        return pd.DataFrame()
    
    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        """获取财务数据-Customer实现"""
        print(f"[Customer] 尝试获取财务数据: {symbol}, period: {period}")
        
        # efinance实现
        if self.efinance_available:
            try:
                print("[Customer] 使用efinance获取财务数据")
                # 使用efinance的get_all_company_performance方法获取财务数据
                df = self.ef.stock.get_all_company_performance()
                if df is not None and not df.empty:
                    # 过滤指定股票的数据
                    filtered_df = df[df['股票代码'] == symbol] if '股票代码' in df.columns else df[df['股票简称'] == symbol]
                    if not filtered_df.empty:
                        print(f"[Customer] efinance获取到{len(filtered_df)}行财务数据")
                        return filtered_df
                    else:
                        print(f"[Customer] efinance未找到股票{symbol}的财务数据")
            except Exception as e:
                print(f"[Customer] efinance获取财务数据失败: {e}")
        
        print("[Customer] 未能获取到财务数据")
        return pd.DataFrame()
    
    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> Union[List[Dict], str]:
        """获取新闻数据-Customer实现"""
        print(f"[Customer] 尝试获取新闻数据: {symbol}")
        
        # 暂时没有直接的实现，返回空列表
        print("[Customer] 新闻数据功能暂未实现")
        return []