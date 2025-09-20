"""
财务数据适配器
专门用于处理财务数据的适配器，支持efinance和easyquotation双数据源
"""
import pandas as pd
from typing import Dict, List, Optional, Union
import sys
import os

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mystocks.interfaces.data_source import IDataSource

class FinancialDataSource(IDataSource):
    """财务数据适配器：专门用于处理财务数据，支持efinance和easyquotation双数据源"""
    
    def __init__(self):
        """初始化财务数据适配器"""
        print("[Financial] 初始化财务数据适配器...")
        self.efinance_available = False
        self.easyquotation_available = False
        self._init_data_sources()
        print(f"[Financial] 数据源初始化完成 (efinance: {'可用' if self.efinance_available else '不可用'}, easyquotation: {'可用' if self.easyquotation_available else '不可用'})")
    
    def _init_data_sources(self):
        """初始化数据源"""
        # 初始化efinance
        try:
            import efinance as ef
            self.ef = ef
            self.efinance_available = True
            print("[Financial] efinance库导入成功")
        except ImportError:
            print("[Financial] efinance库导入失败")
            self.efinance_available = False
        
        # 初始化easyquotation
        try:
            import easyquotation as eq
            self.eq = eq
            self.easyquotation_available = True
            print("[Financial] easyquotation库导入成功")
        except ImportError:
            print("[Financial] easyquotation库导入失败")
            self.easyquotation_available = False
    
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 包含股票日线数据的DataFrame
        """
        print(f"[Financial] 尝试获取股票日线数据: {symbol}")
        
        # 首先尝试使用efinance获取数据
        if self.efinance_available:
            try:
                # 使用efinance获取股票日线数据
                print("[Financial] 使用efinance获取股票日线数据")
                print(f"[Financial] 请求参数: symbol={symbol}, beg={start_date}, end={end_date}")
                data = self.ef.stock.get_quote_history(symbol, beg=start_date, end=end_date)
                print(f"[Financial] efinance返回数据类型: {type(data)}")
                if isinstance(data, pd.DataFrame):
                    print(f"[Financial] efinance返回数据行数: {len(data)}")
                    if not data.empty:
                        print(f"[Financial] efinance获取到{len(data)}行日线数据")
                        # 确保列名是中文
                        expected_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']
                        if all(col in data.columns for col in expected_columns):
                            print("[Financial] 数据格式正确")
                            return data
                        else:
                            print(f"[Financial] 数据列名不匹配，实际列名: {list(data.columns)}")
                            # 尝试重命名列
                            return self._rename_columns(data)
                    else:
                        print("[Financial] efinance返回空数据")
                        # 尝试更广泛的日期范围
                        print("[Financial] 尝试更广泛的日期范围...")
                        broader_data = self.ef.stock.get_quote_history(symbol, beg='2020-01-01', end='2024-12-31')
                        if not broader_data.empty:
                            print(f"[Financial] 更广泛日期范围获取到{len(broader_data)}行数据")
                            # 过滤日期范围
                            broader_data['日期'] = pd.to_datetime(broader_data['日期'])
                            start_date_dt = pd.to_datetime(start_date)
                            end_date_dt = pd.to_datetime(end_date)
                            filtered_data = broader_data[
                                (broader_data['日期'] >= start_date_dt) & 
                                (broader_data['日期'] <= end_date_dt)
                            ]
                            if not filtered_data.empty:
                                print(f"[Financial] 过滤后得到{len(filtered_data)}行数据")
                                return filtered_data
                            else:
                                print("[Financial] 过滤后数据为空")
                                return pd.DataFrame()
                        else:
                            print("[Financial] 更广泛日期范围也未获取到数据")
                            return pd.DataFrame()
                else:
                    print(f"[Financial] efinance返回数据类型不正确: {type(data)}")
            except Exception as e:
                print(f"[Financial] efinance获取日线数据失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 如果efinance不可用或失败，尝试使用easyquotation
        if self.easyquotation_available:
            try:
                print("[Financial] 使用easyquotation获取股票数据")
                # 使用easyquotation获取实时数据作为替代
                quotation = self.eq.use('sina')  # 使用sina源
                data = quotation.real([symbol])  # 获取实时数据
                if data and symbol in data:
                    print("[Financial] easyquotation获取到股票数据")
                    # 转换为DataFrame格式
                    df_data = data[symbol]
                    df = pd.DataFrame([df_data])
                    # 添加必要的列以匹配预期格式
                    if 'date' not in df.columns and 'datetime' in df.columns:
                        df['date'] = df['datetime'].str[:10]  # 从datetime提取日期
                    elif 'date' not in df.columns:
                        df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    # 重命名列以匹配预期格式
                    column_mapping = {
                        'date': '日期',
                        'open': '开盘',
                        'close': '收盘',
                        'high': '最高',
                        'low': '最低',
                        'volume': '成交量',
                        'amount': '成交额'
                    }
                    df = df.rename(columns=column_mapping)
                    # 确保包含所有必要列
                    expected_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']
                    for col in expected_columns:
                        if col not in df.columns:
                            df[col] = 0  # 默认值
                    return df[expected_columns]  # 按预期顺序返回列
                else:
                    print("[Financial] easyquotation未获取到股票数据")
            except Exception as e:
                print(f"[Financial] easyquotation获取股票数据失败: {e}")
                import traceback
                traceback.print_exc()
        
        print("[Financial] 所有方法均未能获取到股票日线数据")
        return pd.DataFrame()
    
    def _rename_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        重命名列名以匹配预期格式
        
        Args:
            data: 原始数据
            
        Returns:
            DataFrame: 重命名后的数据
        """
        # 这里可以根据实际返回的列名进行映射
        column_mapping = {
            # 可能的英文列名映射
            'date': '日期',
            'open': '开盘',
            'close': '收盘',
            'high': '最高',
            'low': '最低',
            'volume': '成交量',
            'amount': '成交额'
        }
        
        # 应用列名映射
        renamed_data = data.rename(columns=column_mapping)
        return renamed_data
    
    def get_index_daily(self, index_code, start_date=None, end_date=None):
        """
        获取指数日线数据
        
        Args:
            index_code (str): 指数代码
            start_date (str, optional): 开始日期，格式为'YYYY-MM-DD'
            end_date (str, optional): 结束日期，格式为'YYYY-MM-DD'
            
        Returns:
            pd.DataFrame: 指数日线数据
        """
        if not self.efinance_available:
            print("[Financial] efinance库不可用")
            return pd.DataFrame()
            
        try:
            # 格式化指数代码，使用东方财富的指数代码格式
            if index_code == '000300':
                formatted_code = '399300'  # 沪深300指数在东方财富的代码为399300
            else:
                formatted_code = index_code
            
            print(f"[Financial] 尝试获取指数 {index_code} 的日线数据...")
            print(f"[Financial] 使用格式化代码: {formatted_code}")
            
            # 获取历史行情数据
            if start_date and end_date:
                data = self.ef.stock.get_quote_history(formatted_code, beg=start_date, end=end_date)
            elif start_date:
                data = self.ef.stock.get_quote_history(formatted_code, beg=start_date)
            elif end_date:
                data = self.ef.stock.get_quote_history(formatted_code, end=end_date)
            else:
                data = self.ef.stock.get_quote_history(formatted_code)
            
            # 如果使用日期参数没有获取到数据，则获取全部数据并进行过滤
            if (start_date or end_date) and (data is None or data.empty):
                print(f"[Financial] 使用日期参数未获取到数据，尝试获取全部数据并过滤...")
                data = self.ef.stock.get_quote_history(formatted_code)
                if data is not None and not data.empty:
                    # 过滤日期范围
                    if start_date:
                        data = data[data['日期'] >= start_date]
                    if end_date:
                        data = data[data['日期'] <= end_date]
            
            if data is not None and not data.empty:
                print(f"[Financial] 成功获取指数 {index_code} 的日线数据，共 {len(data)} 条记录")
                return data
            else:
                print(f"[Financial] 警告: 未获取到指数 {index_code} 的日线数据")
                return pd.DataFrame()
        except Exception as e:
            print(f"[Financial] 获取指数 {index_code} 日线数据时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_stock_basic(self, symbol: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            Dict: 包含股票基本信息的字典
        """
        print(f"[Financial] 尝试获取股票基本信息: {symbol}")
        
        # 首先尝试使用efinance获取数据
        if self.efinance_available:
            try:
                # 使用efinance获取股票基本信息
                print("[Financial] 使用efinance获取股票基本信息")
                data = self.ef.stock.get_base_info(symbol)
                if data is not None:
                    print("[Financial] efinance获取到股票基本信息")
                    # 如果data是DataFrame，转换第一行为字典
                    if isinstance(data, pd.DataFrame):
                        if not data.empty:
                            return data.iloc[0].to_dict()
                        else:
                            return {}
                    # 如果data是Series，转换为字典
                    elif isinstance(data, pd.Series):
                        return data.to_dict()
                    # 如果data已经是字典，直接返回
                    elif isinstance(data, dict):
                        return data
                    else:
                        # 其他情况尝试直接返回
                        return data if data else {}
                else:
                    print("[Financial] efinance未获取到股票基本信息")
            except Exception as e:
                print(f"[Financial] efinance获取股票基本信息失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 如果efinance不可用或失败，尝试使用easyquotation
        if self.easyquotation_available:
            try:
                print("[Financial] 使用easyquotation获取股票基本信息")
                quotation = self.eq.use('sina')  # 使用sina源
                data = quotation.real([symbol])  # 获取实时数据，其中包含基本信息
                if data and symbol in data:
                    print("[Financial] easyquotation获取到股票数据")
                    # 转换为DataFrame格式
                    df = pd.DataFrame([data[symbol]])
                    return df
                else:
                    print("[Financial] easyquotation未获取到股票数据")
            except Exception as e:
                print(f"[Financial] easyquotation获取股票基本信息失败: {e}")
                import traceback
                traceback.print_exc()
        
        print("[Financial] 所有方法均未能获取到股票基本信息")
        return {}
    
    def get_index_components(self, index_code):
        """
        获取指数的成分股数据
        
        Args:
            index_code (str): 指数代码或名称
            
        Returns:
            pd.DataFrame: 指数成分股数据
        """
        if not self.efinance_available and not self.easyquotation_available:
            print("[Financial] 数据源未初始化或不可用")
            return pd.DataFrame()
            
        try:
            # 使用efinance的stock.get_members方法获取指数成分股
            df = self.ef.stock.get_members(index_code)
            
            # 检查返回的数据是否有效
            if df is not None and not df.empty:
                print(f"[Financial] 成功获取指数{index_code}的成分股数据，共{len(df)}只股票")
                return df
            else:
                print(f"[Financial] 获取指数{index_code}的成分股数据为空")
                return pd.DataFrame()
        except Exception as e:
            print(f"[Financial] 获取指数{index_code}的成分股数据时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_real_time_data(self, symbol: str = None, market: str = "CN") -> pd.DataFrame:
        """
        获取实时数据
        
        Args:
            symbol: 股票代码（可选）
            market: 市场代码（CN: A股市场, US: 美股市场, HK: 港股市场）
            
        Returns:
            DataFrame: 包含实时数据的DataFrame
        """
        print(f"[Financial] 尝试获取实时数据: symbol={symbol}, market={market}")
        
        # 首先尝试使用efinance获取数据
        if self.efinance_available:
            try:
                if symbol:
                    # 获取特定股票的实时数据
                    print(f"[Financial] 获取特定股票实时数据: {symbol}")
                    data = self.ef.stock.get_realtime_quotes(symbol=symbol)
                else:
                    # 获取市场快照
                    print(f"[Financial] 获取{market}市场快照")
                    # 增强市场快照处理能力
                    if market == "CN":
                        # 对于A股市场，获取主要指数的实时数据作为市场快照
                        major_indices = ['000001', '399001', '399006']  # 上证指数、深证成指、创业板指
                        data = pd.DataFrame()
                        for index_code in major_indices:
                            try:
                                index_data = self.ef.stock.get_realtime_quotes(symbol=index_code)
                                if isinstance(index_data, pd.DataFrame) and not index_data.empty:
                                    data = pd.concat([data, index_data], ignore_index=True)
                            except Exception as e:
                                print(f"[Financial] 获取指数{index_code}数据失败: {e}")
                    else:
                        # 其他市场使用默认方法
                        data = self.ef.stock.get_realtime_quotes(market=market)
                
                print(f"[Financial] efinance返回数据类型: {type(data)}")
                if isinstance(data, pd.DataFrame):
                    print(f"[Financial] efinance返回数据行数: {len(data)}")
                    if not data.empty:
                        print(f"[Financial] efinance获取到{len(data)}行实时数据")
                        return data
                    else:
                        print("[Financial] efinance返回空数据")
                else:
                    print(f"[Financial] efinance返回数据类型不正确: {type(data)}")
            except Exception as e:
                print(f"[Financial] efinance获取实时数据失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 如果efinance不可用或失败，尝试使用easyquotation
        if self.easyquotation_available:
            try:
                print("[Financial] 使用easyquotation获取实时数据")
                quotation = self.eq.use('sina')  # 使用sina源
                
                if symbol:
                    # 获取特定股票的实时数据
                    print(f"[Financial] 获取特定股票实时数据: {symbol}")
                    data = quotation.real([symbol])
                    if data and symbol in data:
                        print("[Financial] easyquotation获取到股票数据")
                        # 转换为DataFrame格式
                        df = pd.DataFrame([data[symbol]])
                        return df
                    else:
                        print("[Financial] easyquotation未获取到指定股票数据")
                else:
                    # 获取市场快照
                    print(f"[Financial] 获取市场快照: {market}")
                    if market == "CN":
                        # 获取A股市场快照（需要提供股票代码列表）
                        # 扩展股票代码列表以获取更全面的市场快照
                        stock_codes = [
                            '000001', '000002', '600000', '600036',  # 平安银行、万科A、浦发银行、招商银行
                            '600519', '000858', '002594', '300750',  # 贵州茅台、五粮液、比亚迪、宁德时代
                            '399001', '399006', '000001'  # 深证成指、创业板指、上证指数
                        ]
                        data = quotation.real(stock_codes)
                        if data:
                            print(f"[Financial] easyquotation获取到{len(data)}只股票数据")
                            # 转换为DataFrame格式
                            df = pd.DataFrame(data).T  # 转置以使每行代表一只股票
                            return df
                        else:
                            print("[Financial] easyquotation未获取到市场快照数据")
                    else:
                        print(f"[Financial] easyquotation暂不支持{market}市场")
                
            except Exception as e:
                print(f"[Financial] easyquotation获取实时数据失败: {e}")
                import traceback
                traceback.print_exc()
        
        print("[Financial] 所有方法均未能获取到实时数据")
        return pd.DataFrame()
    
    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """
        获取股票财务数据
        
        Args:
            symbol: 股票代码
            period: 报告期类型 ("annual" 或 "quarterly")
            
        Returns:
            DataFrame: 包含股票财务数据的DataFrame
        """
        print(f"[Financial] 尝试获取财务数据: {symbol}, period: {period}")
        if not self.efinance_available:
            print("[Financial] efinance库不可用")
            return pd.DataFrame()
        
        try:
            # 使用efinance获取所有公司的财务数据
            print("[Financial] 使用efinance获取财务数据")
            all_data = self.ef.stock.get_all_company_performance()
            
            if not all_data.empty:
                # 筛选出指定股票的数据
                filtered_data = all_data[
                    (all_data['股票代码'] == symbol) | 
                    (all_data['股票简称'].str.contains(symbol, na=False))
                ]
                
                if not filtered_data.empty:
                    print(f"[Financial] efinance获取到{len(filtered_data)}行财务数据")
                    return filtered_data
                else:
                    print("[Financial] 未找到指定股票的财务数据")
                    return pd.DataFrame()
            else:
                print("[Financial] efinance未获取到财务数据")
                return pd.DataFrame()
        except Exception as e:
            print(f"[Financial] efinance获取财务数据失败: {e}")
            return pd.DataFrame()
    
    def get_market_calendar(self) -> pd.DataFrame:
        """
        获取交易日历
        
        Returns:
            DataFrame: 包含交易日历的DataFrame
        """
        print("[Financial] 尝试获取交易日历")
        if not self.efinance_available:
            print("[Financial] efinance库不可用")
            return pd.DataFrame()
        
        try:
            # 使用efinance获取交易日历
            print("[Financial] 使用efinance获取交易日历")
            data = self.ef.stock.get_all_report_dates()
            if not data.empty:
                print(f"[Financial] efinance获取到{len(data)}个交易日")
                return data
            else:
                print("[Financial] efinance未获取到交易日历")
                return pd.DataFrame()
        except Exception as e:
            print(f"[Financial] efinance获取交易日历失败: {e}")
            return pd.DataFrame()
    
    def get_news_data(self, symbol: str) -> pd.DataFrame:
        """
        获取股票新闻数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            DataFrame: 包含股票新闻数据的DataFrame
        """
        print(f"[Financial] 尝试获取股票新闻数据: {symbol}")
        if not self.efinance_available:
            print("[Financial] efinance库不可用")
            return pd.DataFrame()
        
        try:
            # 使用efinance获取股票新闻数据
            print("[Financial] 使用efinance获取股票新闻数据")
            # 注意：efinance可能没有直接获取新闻数据的接口
            # 这里返回空DataFrame作为占位符
            print("[Financial] efinance暂不支持获取新闻数据")
            return pd.DataFrame()
        except Exception as e:
            print(f"[Financial] efinance获取股票新闻数据失败: {e}")
            return pd.DataFrame()