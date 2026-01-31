"""
Tushare专业数据源适配器

提供Tushare专业金融数据获取功能，支持股票、基金、期货、期权等高级金融数据
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class TushareAdapter(BaseAdapter):
    """Tushare专业数据源适配器"""
    
    def __init__(self):
        super().__init__(name="Tushare", source_type="tushare")
        self.db_service = db_service
        self.quality_monitor = get_data_quality_monitor()
        self.token = None
        self.account_type = "pro"
        
        logger.info(f"初始化{self.name}适配器（专业版）")
    
    def _ensure_token(self):
        """确保有访问令牌"""
        if not self.token:
            token = os.getenv('TUSHARE_TOKEN')
            if not token:
                logger.error("未找到TUSHARE_TOKEN环境变量")
                raise ValueError("Tushare访问令牌未配置")
            self.token = token
    
    async def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            self._log_request_start('get_stock_basic', {'stock_code': stock_code})
            
            self._ensure_token()
            
            import tushare as ts
            df = ts.pro_api(ts.pro_api.StockBasic, token=self.token, fields={
                'ts_code': True,
                'symbol': True,
                'name': True,
                'industry': True,
                'area': True,
                'list_date': True,
                'list_date_num': True,
                'total_share': True,
                'float_share': True,
                'total_assets': True
            }, security_token='xxxx', code=stock_code)
            
            if df.empty:
                self._log_request_error('get_stock_basic', Exception('未返回数据'))
                return None
            
            stock_info = {
                'symbol': stock_code,
                'name': df.iloc[0]['name'],
                'industry': df.iloc[0]['industry'],
                'area': df.iloc[0]['area'],
                'list_date': df.iloc[0]['list_date'].isoformat() if df.iloc[0]['list_date'] else '',
                'list_date_num': df.iloc[0]['list_date_num'],
                'total_share': df.iloc[0]['total_share'] if 'total_share' in df.columns else 0,
                'float_share': df.iloc[0]['float_share'] if 'float_share' in df.columns else 0,
                'total_assets': df.iloc[0]['total_assets'] if 'total_assets' in df.columns else 0,
                'is_st': df.iloc[0]['is_st'] if 'is_st' in df.columns else False,
                'is_hs': df.iloc[0]['is_hs'] if 'is_hs' in df.columns else False
            }
            
            self._log_request_success('get_stock_basic', stock_info)
            self._log_data_quality(stock_info, 'get_stock_basic')
            
            return stock_info
            
        except Exception as e:
            self._log_request_error('get_stock_basic', e)
            logger.error(f"{self.name}.get_stock_basic 异常: {e}")
            return None
    
    async def get_stock_daily(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """获取日线数据"""
        try:
            self._log_request_start('get_stock_daily', {
                'stock_code': stock_code,
                'start_date': start_date,
                'end_date': end_date
            })
            
            self._ensure_token()
            
            import tushare as ts
            df = ts.pro_bar(ts.pro_bar(token=self.token, security_token='xxxx', 
                freq='D', 
                adj='qfq', 
                code=stock_code,
                start_date=start_date, end_date=end_date,
                security_token='xxxx',
                fields='trade_date,open,high,low,close,vol,amount'
            )
            
            if df.empty:
                self._log_request_error('get_stock_daily', Exception('未返回数据'))
                return []
            
            daily_data = []
            for _, row in df.iterrows():
                daily_data.append({
                    'symbol': stock_code,
                    'trade_date': row['trade_date'].isoformat() if row['trade_date'] else '',
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['vol'],
                    'amount': row['amount']
                })
            
            self._log_request_success('get_stock_daily', f"返回{len(daily_data)}条日线数据")
            self._log_data_quality(daily_data, 'get_stock_daily')
            
            return daily_data
            
        except Exception as e:
            self._log_request_error('get_stock_daily', e)
            logger.error(f"{self.name}.get_stock_daily 异常: {e}")
            return []
    
    async def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """获取实时行情"""
        try:
            self._log_request_start('get_realtime_quotes', {'stock_codes': stock_codes})
            
            self._ensure_token()
            
            import tushare as ts
            quotes = []
            for stock_code in stock_codes[:100]:
                df = ts.pro_api(ts.pro_api.Realtime, token=self.token, security_token='xxxx', 
                    fields='ts_code,symbol,name,price,change,pct_chg,volume,amount,turnover,buy1,sell1,bid1,bid2,ask1,ask2,ask3,bid3,bid4,bid5',
                    code=stock_code
                )
                
                if not df.empty and len(df) > 0:
                    latest = df.iloc[0]
                    quotes.append({
                        'symbol': stock_code,
                        'name': latest['name'] if 'name' in latest else '',
                        'price': latest['price'] if 'price' in latest else 0,
                        'change': latest['pct_chg'] if 'pct_chg' in latest else 0,
                        'change_percent': latest['pct_chg'] if 'pct_chg' in latest else 0,
                        'volume': latest['vol'] if 'vol' in latest else 0,
                        'amount': latest['amount'] if 'amount' in latest else 0
                    })
                
            self._log_request_success('get_realtime_quotes', f"返回{len(quotes)}条实时行情")
            self._log_data_quality(quotes, 'get_realtime_quotes')
            
            return quotes
            
        except Exception as e:
            self._log_request_error('get_realtime_quotes', e)
            logger.error(f"{self.name}.get_realtime_quotes 异常: {e}")
            return []
    
    async def check_health(self) -> Optional[str]:
        """检查健康状态"""
        try:
            self._log_request_start('check_health', {})
            
            self._ensure_token()
            
            import tushare as ts
            df = ts.trade_cal(ts.trade_cal(token=self.token, security_token='xxxx'))
            
            if not df.empty and len(df) > 0:
                return 'healthy'
            else:
                return 'unhealthy'
                
        except Exception as e:
            self._log_request_error('check_health', e)
            return f"error: {e}"
