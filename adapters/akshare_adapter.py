"""
Akshare 数据源适配器
实现了统一数据接口，提供 Akshare 数据访问

示例用法：
    >>> from mystocks.adapters.akshare_adapter import AkshareDataSource
    >>> adapter = AkshareDataSource()
    >>> data = adapter.get_stock_daily("000001", "2023-01-01", "2023-01-31")
"""
import pandas as pd
from typing import Dict, List, Optional
import akshare as ak
import sys
import os
import datetime
import time
from functools import wraps

# 常量定义
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mystocks.interfaces.data_source import IDataSource
from mystocks.utils.date_utils import normalize_date
from mystocks.utils.symbol_utils import format_stock_code_for_source, format_index_code_for_source
from mystocks.utils.column_mapper import ColumnMapper


class AkshareDataSource(IDataSource):
    """Akshare数据源实现
    
    属性:
        api_timeout (int): API请求超时时间(秒)
        max_retries (int): 最大重试次数
    """
    
    def __init__(self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES):
        """初始化Akshare数据源
        
        Args:
            api_timeout: API请求超时时间(秒)
            max_retries: 最大重试次数
        """
        self.api_timeout = api_timeout
        self.max_retries = max_retries
        print(f"[Akshare] 数据源初始化完成 (超时: {api_timeout}s, 重试: {max_retries}次)")
        
    def _retry_api_call(self, func):
        """API调用重试装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[Akshare] 第{attempt}次尝试失败: {str(e)}")
                    if attempt < self.max_retries:
                        time.sleep(RETRY_DELAY * attempt)
            raise last_exception if last_exception else Exception("未知错误")
        return wrapper
    
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据-Akshare实现"""
        try:
            # 处理股票代码格式 - 使用专门的格式化函数
            stock_code = format_stock_code_for_source(symbol, 'akshare')
            
            # 处理日期格式
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)
            
            print(f"Akshare尝试获取股票日线数据: 代码={stock_code}, 开始日期={start_date}, 结束日期={end_date}")
            
            # 尝试多种API获取股票数据
            df = None
            
            # 方法1: stock_zh_a_hist (主要API)
            try:
                # 根据文档要求，日期格式应为YYYYMMDD
                start_date_fmt = start_date.replace("-", "")
                end_date_fmt = end_date.replace("-", "")
                
                df = ak.stock_zh_a_hist(
                    symbol=stock_code, 
                    period="daily", 
                    start_date=start_date_fmt, 
                    end_date=end_date_fmt, 
                    adjust="qfq",  # 前复权
                    timeout=self.api_timeout
                )
                print(f"主要API调用成功，参数: symbol={stock_code}, start_date={start_date_fmt}, end_date={end_date_fmt}")
            except Exception as e:
                print(f"主要API调用失败: {e}")
                df = None
            
            # 方法2: stock_zh_a_spot (备用API)
            if df is None or df.empty:
                try:
                    print("尝试备用API(stock_zh_a_spot)")
                    spot_df = ak.stock_zh_a_spot()
                    if spot_df is not None and not spot_df.empty:
                        # 筛选指定股票代码
                        spot_df = spot_df[spot_df['代码'] == stock_code]
                        if not spot_df.empty:
                            # 转换为日线格式
                            df = pd.DataFrame({
                                'date': [datetime.datetime.now().strftime("%Y-%m-%d")],
                                'open': [spot_df.iloc[0]['今开']],
                                'close': [spot_df.iloc[0]['最新价']],
                                'high': [spot_df.iloc[0]['最高']],
                                'low': [spot_df.iloc[0]['最低']],
                                'volume': [spot_df.iloc[0]['成交量']],
                                'amount': [spot_df.iloc[0]['成交额']]
                            })
                except Exception as e:
                    print(f"备用API调用失败: {e}")
            
            if df is None or df.empty:
                print("Akshare返回的数据为空")
                return pd.DataFrame()
                
            print(f"Akshare获取到原始数据: {len(df)}行, 列名={df.columns.tolist()}")
            
            # 使用统一列名映射器标准化列名
            df = ColumnMapper.to_english(df)
            
            return df
        except Exception as e:
            print(f"Akshare获取股票日线数据失败: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据-Akshare实现
        使用优先级：
        1. 新浪接口(stock_zh_index_daily)
        2. 东方财富接口(stock_zh_index_daily_em)
        3. 通用接口(index_zh_a_hist)
        """
        try:
            # 处理日期格式
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)
            
            print(f"尝试获取指数数据: {symbol}")
            
            # 使用专门的格式化函数处理指数代码
            index_code = format_index_code_for_source(symbol, 'akshare')
            print(f"处理指数: {index_code}")
            
            # 方法1: 新浪接口 (stock_zh_index_daily)
            try:
                print("尝试新浪接口(stock_zh_index_daily)")
                df = ak.stock_zh_index_daily(symbol=index_code)
                
                if df is not None and not df.empty:
                    # 筛选日期范围
                    df['date'] = pd.to_datetime(df['date'])
                    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
                    df = df[mask]
                    
                    if not df.empty:
                        print(f"新浪接口获取到{len(df)}行数据")
                        return self._process_index_data(df)
            except Exception as e:
                print(f"新浪接口调用失败: {e}")
            
            # 方法2: 东方财富接口 (stock_zh_index_daily_em)
            try:
                print("尝试东方财富接口(stock_zh_index_daily_em)")
                df = ak.stock_zh_index_daily_em(symbol=index_code)
                
                if df is not None and not df.empty:
                    # 筛选日期范围
                    df['date'] = pd.to_datetime(df['date'])
                    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
                    df = df[mask]
                    
                    if not df.empty:
                        print(f"东方财富接口获取到{len(df)}行数据")
                        return self._process_index_data(df)
            except Exception as e:
                print(f"东方财富接口调用失败: {e}")
            
            # 方法3: 通用接口 (index_zh_a_hist)
            try:
                print("尝试通用接口(index_zh_a_hist)")
                # 提取纯数字代码
                pure_code = ''.join(c for c in index_code if c.isdigit())
                start_date_fmt = start_date.replace("-", "")
                end_date_fmt = end_date.replace("-", "")
                
                df = ak.index_zh_a_hist(
                    symbol=pure_code,
                    period="daily",
                    start_date=start_date_fmt,
                    end_date=end_date_fmt
                )
                
                if df is not None and not df.empty:
                    print(f"通用接口获取到{len(df)}行数据")
                    return self._process_index_data(df)
            except Exception as e:
                print(f"通用接口调用失败: {e}")
            
            print(f"所有接口均未能获取到指数 {index_code} 的数据")
            return pd.DataFrame()
                
        except Exception as e:
            print(f"Akshare获取指数日线数据失败: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def _process_index_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理指数数据统一格式"""
        # 使用统一列名映射器标准化列名
        return ColumnMapper.to_english(df)
    
    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息-Akshare实现"""
        try:
            # 处理股票代码格式 - 使用专门的格式化函数
            stock_code = format_stock_code_for_source(symbol, 'akshare')
            
            # 使用stock_individual_info_em接口获取股票基本信息
            # 参考文档: https://akshare.akfamily.xyz/data/stock/stock.html#id56
            df = ak.stock_individual_info_em(symbol=stock_code)
            
            if df is None or df.empty:
                print(f"未能获取到股票 {stock_code} 的基本信息")
                return {}
                
            # 转换为字典
            info_dict = {}
            for _, row in df.iterrows():
                info_dict[row['item']] = row['value']
                
            return info_dict
        except Exception as e:
            print(f"Akshare获取股票基本信息失败: {e}")
            return {}
    
    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股-Akshare实现"""
        try:
            # 使用index_stock_cons接口获取指数成分股
            # 参考文档: https://akshare.akfamily.xyz/data/index/index.html#id4
            df = ak.index_stock_cons(symbol=symbol)
            
            if df is None or df.empty:
                print(f"未能获取到指数 {symbol} 的成分股")
                return []
                
            # 提取股票代码
            if '品种代码' in df.columns:
                return df['品种代码'].tolist()
            elif '成分券代码' in df.columns:
                return df['成分券代码'].tolist()
            else:
                print(f"无法识别的成分股列名: {df.columns.tolist()}")
                return []
        except Exception as e:
            print(f"Akshare获取指数成分股失败: {e}")
            return []
    
    def get_real_time_data(self, symbol: str):
        """获取实时数据-Akshare实现"""
        try:
            # 使用stock_zh_a_spot接口获取股票实时数据
            df = ak.stock_zh_a_spot()
            
            if df is None or df.empty:
                print(f"未能获取到股票 {symbol} 的实时数据")
                return {}
                
            # 筛选指定股票
            filtered_df = df[df['代码'] == symbol]
            if filtered_df.empty:
                print(f"未能找到股票 {symbol} 的实时数据")
                return {}
                
            # 转换为字典
            return filtered_df.iloc[0].to_dict()
        except Exception as e:
            print(f"Akshare获取实时数据失败: {e}")
            return {}
    
    def get_market_calendar(self, start_date: str, end_date: str):
        """获取交易日历-Akshare实现"""
        try:
            # 使用tool_trade_date_hist_sina接口获取交易日历
            df = ak.tool_trade_date_hist_sina()
            
            if df is None or df.empty:
                print("未能获取到交易日历数据")
                return pd.DataFrame()
                
            # 筛选日期范围
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
            mask = (df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)
            filtered_df = df[mask]
            
            return filtered_df
        except Exception as e:
            print(f"Akshare获取交易日历失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, symbol: str, period: str = "annual"):
        """获取财务数据-Akshare实现"""
        try:
            # 使用stock_financial_abstract接口获取财务摘要数据
            stock_code = format_stock_code_for_source(symbol, 'akshare')
            df = ak.stock_financial_abstract(stock=stock_code)
            
            if df is None or df.empty:
                print(f"未能获取到股票 {symbol} 的财务数据")
                return pd.DataFrame()
                
            return df
        except Exception as e:
            print(f"Akshare获取财务数据失败: {e}")
            return pd.DataFrame()
    
    def get_news_data(self, symbol: str = None, limit: int = 10):
        """获取新闻数据-Akshare实现"""
        try:
            # 如果提供了股票代码，获取个股新闻；否则获取市场新闻
            if symbol:
                # 获取个股新闻
                stock_code = format_stock_code_for_source(symbol, 'akshare')
                df = ak.stock_news_em(symbol=stock_code, pageSize=limit)
            else:
                # 获取市场新闻
                df = ak.stock_news_em(pageSize=limit)
            
            if df is None or df.empty:
                print("未能获取到新闻数据")
                return []
                
            # 转换为字典列表
            return df.to_dict('records')
        except Exception as e:
            print(f"Akshare获取新闻数据失败: {e}")
            return []