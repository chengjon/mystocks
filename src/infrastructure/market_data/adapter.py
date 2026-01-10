"""
DataSourceV2 Adapter
将现有的 DataSourceManagerV2 适配到 DDD 的 IMarketDataRepository 接口
"""
import logging
from typing import List
from datetime import datetime
import pandas as pd

from src.domain.market_data.repository import IMarketDataRepository
from src.domain.market_data.value_objects import Bar, Quote
from src.core.data_source_manager_v2 import DataSourceManagerV2

logger = logging.getLogger(__name__)

class DataSourceV2Adapter(IMarketDataRepository):
    """
    数据源适配器 (Implementation of ACL)
    """
    
    def __init__(self):
        # 依赖注入或直接实例化
        self.manager = DataSourceManagerV2()
        
    def get_history_kline(self, symbol: str, start_date: str, end_date: str) -> List[Bar]:
        """
        获取历史K线
        调用 manager.get_stock_daily (智能路由)
        """
        try:
            # 调用 V2 接口
            df = self.manager.get_stock_daily(symbol, start_date, end_date)
            
            if df is None or df.empty:
                logger.warning(f"No kline data found for {symbol}")
                return []
                
            bars = []
            for _, row in df.iterrows():
                # 处理日期格式
                trade_date = row.get('trade_date')
                if isinstance(trade_date, str):
                    timestamp = datetime.strptime(trade_date, "%Y-%m-%d")
                elif isinstance(trade_date, datetime):
                    timestamp = trade_date
                else:
                    timestamp = datetime.now() # Fallback
                    
                bars.append(Bar(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=float(row.get('open', 0)),
                    high=float(row.get('high', 0)),
                    low=float(row.get('low', 0)),
                    close=float(row.get('close', 0)),
                    volume=float(row.get('volume', 0)),
                    amount=float(row.get('amount', 0)) if 'amount' in row else None
                ))
            return bars
            
        except Exception as e:
            logger.error(f"Failed to get history kline: {e}")
            return []

    def get_realtime_quote(self, symbols: List[str]) -> List[Quote]:
        """
        获取实时行情
        调用 manager.get_stock_realtime
        """
        try:
            df = self.manager.get_stock_realtime(symbols)
            
            if df is None or df.empty:
                return []
                
            quotes = []
            for _, row in df.iterrows():
                quotes.append(Quote(
                    symbol=row.get('symbol', ''),
                    timestamp=datetime.now(), # 实时接口通常需要取当前时间
                    last_price=float(row.get('price', 0)),
                    open_price=float(row.get('open', 0)),
                    high_price=float(row.get('high', 0)),
                    low_price=float(row.get('low', 0)),
                    prev_close=float(row.get('pre_close', 0)),
                    volume=float(row.get('volume', 0)),
                    amount=float(row.get('amount', 0)),
                    # 简化处理盘口，V2接口可能不返回所有档位
                    bid_price1=float(row.get('bid1_price', 0)),
                    bid_volume1=int(row.get('bid1_volume', 0)),
                    ask_price1=float(row.get('ask1_price', 0)),
                    ask_volume1=int(row.get('ask1_volume', 0))
                ))
            return quotes
            
        except Exception as e:
            logger.error(f"Failed to get realtime quote: {e}")
            return []

    def get_latest_price(self, symbol: str) -> float:
        """获取最新价格"""
        quotes = self.get_realtime_quote([symbol])
        if quotes:
            return quotes[0].last_price
        return 0.0
