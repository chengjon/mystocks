"""
基础数据源工具类
统一管理股票数据源的连接和数据获取
支持AkShare和Tushare双数据源
"""

import time
import akshare as ak
import tushare as ts
from typing import Dict, List, Optional
import pandas as pd
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseDataSource:
    """
    基础数据源工具类，封装数据源连接逻辑
    支持AkShare和Tushare双数据源，提供重试机制和标准化数据格式
    """
    
    def __init__(self):
        """
        初始化数据源
        优先使用AkShare，如果失败则使用Tushare
        """
        self.use_tushare = False
        self.tushare_token = os.getenv('TUSHARE_TOKEN', '')
        
        # 检查是否配置了Tushare token
        if self.tushare_token:
            ts.set_token(self.tushare_token)
            self.pro = ts.pro_api()
            logger.info("Tushare已配置")
        else:
            logger.info("未配置Tushare token，将优先使用AkShare")
    
    def _retry_request(self, func, max_retries: int = 3, delay: int = 2, *args, **kwargs):
        """
        重试装饰器，用于数据请求失败时重试
        
        Args:
            func: 要执行的函数
            max_retries: 最大重试次数
            delay: 重试间隔（秒）
            *args, **kwargs: 函数参数
        
        Returns:
            函数执行结果
        """
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"请求失败，已达到最大重试次数 {max_retries}: {e}")
                    raise e
                logger.warning(f"请求失败，{delay}秒后重试 ({attempt + 1}/{max_retries}): {e}")
                time.sleep(delay)
    
    def get_stock_basic_info(self) -> List[Dict]:
        """
        获取股票基础信息
        
        Returns:
            包含股票基础信息的字典列表
            格式: [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "industry": "",  # AkShare股票基础信息中不直接提供行业信息
                    "area": "",
                    "market": "SZ",
                    "list_date": "",
                }
            ]
        """
        def _fetch_basic_info():
            if not self.use_tushare:
                try:
                    # 使用AkShare获取股票基础信息
                    stock_info = ak.stock_info_a_code_name()
                    
                    # 转换数据格式
                    result = []
                    for _, row in stock_info.iterrows():
                        symbol = str(row['code'])
                        name = row['name']
                        
                        # 确定市场
                        market = 'SZ' if symbol.startswith('0') or symbol.startswith('2') or symbol.startswith('3') else 'SH'
                        # 添加市场后缀
                        symbol_with_suffix = f"{symbol}.{market}"
                        
                        result.append({
                            "symbol": symbol_with_suffix,
                            "name": name,
                            "industry": "",  # AkShare股票基础信息中不直接提供行业信息
                            "area": "",
                            "market": market,
                            "list_date": ""
                        })
                    
                    return result
                except Exception as e:
                    logger.error(f"AkShare获取股票基础信息失败: {e}")
                    # 如果AkShare失败，切换到Tushare
                    if self.tushare_token:
                        logger.info("切换到Tushare数据源")
                        self.use_tushare = True
                    else:
                        raise e
            
            if self.use_tushare:
                # 使用Tushare获取股票基础信息
                try:
                    stock_info = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
                    
                    # 转换数据格式
                    result = []
                    for _, row in stock_info.iterrows():
                        result.append({
                            "symbol": row['ts_code'],
                            "name": row['name'],
                            "industry": row['industry'] if pd.notna(row['industry']) else "",
                            "area": row['area'] if pd.notna(row['area']) else "",
                            "market": row['market'] if pd.notna(row['market']) else "",
                            "list_date": str(row['list_date']) if pd.notna(row['list_date']) else ""
                        })
                    
                    return result
                except Exception as e:
                    logger.error(f"Tushare获取股票基础信息失败: {e}")
                    raise e
        
        return self._retry_request(_fetch_basic_info)
    
    def get_stock_kline_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        获取单只股票K线数据
        
        Args:
            symbol: 股票代码，格式如 "000001.SZ" 或 "600000.SH"
            start_date: 开始日期，格式 "YYYY-MM-DD"
            end_date: 结束日期，格式 "YYYY-MM-DD"
        
        Returns:
            包含K线数据的字典列表
            格式: [
                {
                    "symbol": "000001.SZ",
                    "trade_date": "2023-01-01",
                    "open": 10.0,
                    "high": 10.5,
                    "low": 9.8,
                    "close": 10.3,
                    "volume": 1000000,
                    "amount": 10300000.0
                }
            ]
        """
        def _fetch_kline_data():
            if not self.use_tushare:
                try:
                    # 使用AkShare获取股票历史数据
                    logger.info(f"正在使用AkShare获取股票 {symbol} 的K线数据，日期范围: {start_date} 到 {end_date}")
                    
                    # 移除后缀获取纯股票代码
                    if '.' in symbol:
                        code = symbol.split('.')[0]
                        market = symbol.split('.')[1]
                    else:
                        code = symbol
                        # 根据代码前缀判断市场
                        market = 'SZ' if code.startswith('0') or code.startswith('2') or code.startswith('3') else 'SH'
                    
                    stock_zh_a_hist_df = ak.stock_zh_a_hist(
                        symbol=code,
                        period="daily",
                        start_date=start_date.replace("-", ""),
                        end_date=end_date.replace("-", ""),
                        adjust=""
                    )
                    
                    if stock_zh_a_hist_df.empty:
                        logger.warning(f"未获取到股票 {symbol} 在 {start_date} 到 {end_date} 的数据")
                        return []
                    
                    logger.info(f"成功获取到 {len(stock_zh_a_hist_df)} 条K线数据")
                    
                    # 转换数据格式
                    result = []
                    for _, row in stock_zh_a_hist_df.iterrows():
                        # 确保添加市场后缀
                        full_symbol = f"{code}.{market}"
                        
                        result.append({
                            "symbol": full_symbol,
                            "trade_date": str(row['日期']),
                            "open": float(row['开盘']),
                            "high": float(row['最高']),
                            "low": float(row['最低']),
                            "close": float(row['收盘']),
                            "volume": int(row['成交量']) if pd.notna(row['成交量']) else 0,
                            "amount": float(row['成交额']) if pd.notna(row['成交额']) else 0.0
                        })
                    
                    return result
                except Exception as e:
                    logger.error(f"AkShare获取股票 {symbol} K线数据失败: {type(e).__name__}: {e}")
                    # 如果AkShare失败，切换到Tushare
                    if self.tushare_token:
                        logger.info("切换到Tushare数据源")
                        self.use_tushare = True
                    else:
                        raise e
            
            if self.use_tushare:
                # 使用Tushare获取股票历史数据
                try:
                    logger.info(f"正在使用Tushare获取股票 {symbol} 的K线数据，日期范围: {start_date} 到 {end_date}")
                    
                    # Tushare需要将日期格式转换为YYYYMMDD
                    ts_start_date = start_date.replace("-", "")
                    ts_end_date = end_date.replace("-", "")
                    
                    kline_data = self.pro.daily(ts_code=symbol, start_date=ts_start_date, end_date=ts_end_date)
                    
                    if kline_data.empty:
                        logger.warning(f"未获取到股票 {symbol} 在 {start_date} 到 {end_date} 的数据")
                        return []
                    
                    logger.info(f"成功获取到 {len(kline_data)} 条K线数据")
                    
                    # 转换数据格式
                    result = []
                    for _, row in kline_data.iterrows():
                        result.append({
                            "symbol": row['ts_code'],
                            "trade_date": row['trade_date'],  # Tushare已经是YYYYMMDD格式
                            "open": float(row['open']),
                            "high": float(row['high']),
                            "low": float(row['low']),
                            "close": float(row['close']),
                            "volume": int(row['vol']) * 100,  # Tushare的成交量单位是手，需要转换为股
                            "amount": float(row['amount']) if pd.notna(row['amount']) else 0.0
                        })
                    
                    return result
                except Exception as e:
                    logger.error(f"Tushare获取股票 {symbol} K线数据失败: {type(e).__name__}: {e}")
                    raise e
        
        return self._retry_request(_fetch_kline_data)
    
    def get_stock_industry_info(self) -> List[Dict]:
        """
        获取股票行业信息
        
        Returns:
            包含股票行业信息的字典列表
        """
        def _fetch_industry_info():
            if not self.use_tushare:
                try:
                    # AkShare获取行业信息
                    stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
                    
                    result = []
                    for _, row in stock_board_industry_name_em_df.iterrows():
                        symbol = str(row['代码'])
                        # 确定市场
                        market = 'SZ' if symbol.startswith('0') or symbol.startswith('2') or symbol.startswith('3') else 'SH'
                        symbol_with_suffix = f"{symbol}.{market}"
                        
                        result.append({
                            "symbol": symbol_with_suffix,
                            "industry": row['板块名称'],
                            "industry_code": row['板块代码']
                        })
                    
                    return result
                except Exception as e:
                    logger.warning(f"AkShare获取股票行业信息失败: {e}")
                    # 如果AkShare失败，切换到Tushare
                    if self.tushare_token:
                        logger.info("切换到Tushare数据源")
                        self.use_tushare = True
                    else:
                        return []
            
            if self.use_tushare:
                # Tushare获取行业信息
                try:
                    stock_industry_df = self.pro.stock_basic(exchange='', fields='ts_code,industry')
                    
                    result = []
                    for _, row in stock_industry_df.iterrows():
                        if pd.notna(row['industry']):
                            result.append({
                                "symbol": row['ts_code'],
                                "industry": row['industry']
                            })
                    
                    return result
                except Exception as e:
                    logger.error(f"Tushare获取股票行业信息失败: {e}")
                    return []
        
        return self._retry_request(_fetch_industry_info)


if __name__ == "__main__":
    # 测试数据源功能
    logger.info("开始测试数据源功能")
    
    ds = BaseDataSource()
    
    # 测试获取股票基础信息
    try:
        basic_info = ds.get_stock_basic_info()
        logger.info(f"获取到 {len(basic_info[:5])} 条股票基础信息（显示前5条）")
        for i, info in enumerate(basic_info[:5]):
            print(f"  {i+1}. {info}")
    except Exception as e:
        logger.error(f"获取股票基础信息失败: {e}")
    
    # 测试获取K线数据
    try:
        kline_data = ds.get_stock_kline_data("000001.SZ", "2024-11-10", "2024-11-16")
        logger.info(f"获取到 {len(kline_data)} 条K线数据")
        for i, data in enumerate(kline_data[:3]):
            print(f"  {i+1}. {data}")
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
    
    logger.info("数据源功能测试完成")