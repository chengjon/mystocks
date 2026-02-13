"""
Baostock东方财富数据源适配器

提供Baostock中国历史数据获取功能，支持复权数据、高质量历史数据等
"""

from typing import Dict, List, Optional

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class BaostockAdapter(BaseAdapter):
    """Baostock东方财富数据源适配器"""

    def __init__(self):
        super().__init__(name="Baostock", source_type="baostock")
        self.db_service = db_service
        self.quality_monitor = get_data_quality_monitor()

        logger.info(f"初始化{self.name}适配器")

    async def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            self._log_request_start("get_stock_basic", {"stock_code": stock_code})

            sql = f"""
                SELECT 
                    code as symbol,
                    name as name,
                    industry as industry,
                    area as area,
                    list_date as list_date,
                    list_date_num as list_date_num,
                    total_share as total_share,
                    total_assets as total_assets,
                    is_st as is_st,
                    is_hs as is_hs
                FROM baostock_stocks
                WHERE code = '{stock_code}'
                LIMIT 1
            """

            result = await self.db_service.fetch_one(sql)

            if result:
                self._log_request_success("get_stock_basic", result)
                stock_info = {
                    "symbol": result["symbol"],
                    "name": result["name"],
                    "industry": result["industry"],
                    "area": result["area"],
                    "list_date": result["list_date"].isoformat() if result["list_date"] else "",
                    "list_date_num": result["list_date_num"],
                    "total_share": result["total_share"],
                    "total_assets": result["total_assets"],
                    "is_st": result["is_st"],
                    "is_hs": result["is_hs"],
                }
                self._log_data_quality(stock_info, "get_stock_basic")
                return stock_info
            else:
                self._log_request_error("get_stock_basic", Exception("股票不存在"))
                return None

        except Exception as e:
            self._log_request_error("get_stock_basic", e)
            return None

    async def get_stock_daily(
        self, stock_code: str, start_date: str, end_date: str, adj_type: str = "qfq"
    ) -> Optional[List[Dict]]:
        """获取日线数据"""
        try:
            self._log_request_start(
                "get_stock_daily",
                {"stock_code": stock_code, "start_date": start_date, "end_date": end_date, "adj_type": adj_type},
            )

            sql = f"""
                SELECT 
                    trade_date,
                    open, high, low, close, volume, amount, adj_factor
                FROM baostock_daily
                WHERE code = '{stock_code}'
                  AND trade_date >= '{start_date}'
                  AND trade_date <= '{end_date}'
                ORDER BY trade_date ASC
            """

            results = await self.db_service.fetch_many(sql)

            if results:
                self._log_request_success("get_stock_daily", f"返回{len(results)}条日线数据")
                daily_data = []
                for result in results:
                    daily_data.append(
                        {
                            "symbol": stock_code,
                            "trade_date": result["trade_date"].isoformat() if result["trade_date"] else "",
                            "open": result["open"],
                            "high": result["high"],
                            "low": result["low"],
                            "close": result["close"],
                            "volume": result["volume"],
                            "amount": result["amount"],
                            "adj_factor": result["adj_factor"],
                        }
                    )
                self._log_data_quality(daily_data, "get_stock_daily")
                return daily_data
            else:
                self._log_request_error("get_stock_daily", Exception("未返回数据"))
                return []

        except Exception as e:
            self._log_request_error("get_stock_daily", e)
            return []

    async def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """获取实时行情"""
        try:
            self._log_request_start("get_realtime_quotes", {"stock_codes": stock_codes})

            quotes = []
            for stock_code in stock_codes[:50]:
                sql = f"""
                    SELECT 
                        code as symbol,
                        name as name,
                        price as price,
                        change as change,
                        pct_change as pct_change,
                        volume as volume,
                        turnover as turnover,
                        quote_time as quote_time
                    FROM baostock_realtime
                    WHERE code = '{stock_code}'
                    ORDER BY quote_time DESC
                    LIMIT 1
                """

                result = await self.db_service.fetch_one(sql)

                if result:
                    quotes.append(
                        {
                            "symbol": result["symbol"],
                            "name": result["name"],
                            "price": result["price"],
                            "change": result["change"],
                            "change_percent": result["pct_change"],
                            "volume": result["volume"],
                            "turnover": result["turnover"],
                            "quote_time": result["quote_time"].isoformat() if result["quote_time"] else "",
                        }
                    )

            self._log_request_success("get_realtime_quotes", f"返回{len(quotes)}条实时行情")
            self._log_data_quality(quotes, "get_realtime_quotes")
            return quotes

        except Exception as e:
            self._log_request_error("get_realtime_quotes", e)
            return []

    async def get_dividend_data(self, stock_code: str, year: str = "2024") -> Optional[List[Dict]]:
        """获取分红数据"""
        try:
            self._log_request_start("get_dividend_data", {"stock_code": stock_code, "year": year})

            sql = f"""
                SELECT 
                    div_date as div_date,
                    div_ratio as div_ratio,
                    div_yield as div_yield,
                    ex_div_date as ex_div_date
                    ex_div_price as ex_div_price
                    bonus_ratio as bonus_ratio
                    bonus_type as bonus_type
                FROM baostock_dividend
                WHERE code = '{stock_code}'
                  AND div_year = '{year}'
                ORDER BY div_date DESC
            """

            results = await self.db_service.fetch_many(sql)

            if results:
                self._log_request_success("get_dividend_data", f"返回{len(results)}条分红数据")
                dividend_data = []
                for result in results:
                    dividend_data.append(
                        {
                            "symbol": stock_code,
                            "div_date": result["div_date"].isoformat() if result["div_date"] else "",
                            "div_ratio": result["div_ratio"],
                            "div_yield": result["div_yield"],
                            "ex_div_date": result["ex_div_date"].isoformat() if result["ex_div_date"] else "",
                            "ex_div_price": result["ex_div_price"],
                            "bonus_ratio": result["bonus_ratio"],
                            "bonus_type": result["bonus_type"],
                        }
                    )
                self._log_data_quality(dividend_data, "get_dividend_data")
                return dividend_data
            else:
                self._log_request_error("get_dividend_data", Exception("未返回数据"))
                return []

        except Exception as e:
            self._log_request_error("get_dividend_data", e)
            return []

    async def check_health(self) -> Optional[str]:
        """检查健康状态"""
        try:
            self._log_request_start("check_health", {})

            sql = "SELECT COUNT(*) as count FROM baostock_stocks"

            result = await self.db_service.fetch_one(sql)

            if result and result["count"] > 0:
                self._log_request_success("check_health", "Baostock数据源健康")
                return "healthy"
            else:
                self._log_request_error("check_health", Exception("Baostock数据源不可用"))
                return "unhealthy"

        except Exception as e:
            self._log_request_error("check_health", e)
            return f"error: {e}"
