"""
TDX通达信数据源适配器

提供TDX通达信协议的数据获取功能，支持股票行情、板块数据、技术指标等
"""

from typing import Dict, List, Optional

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class TDXAdapter(BaseAdapter):
    """TDX通达信数据源适配器"""

    def __init__(self):
        super().__init__(name="TDX", source_type="tdx")
        self.db_service = db_service
        self.quality_monitor = get_data_quality_monitor()
        self.connection_pool = None
        self.max_connections = 5

        logger.info(f"初始化{TDX}适配器")

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
                list_date_num as list_date_num
            FROM tdx_stocks
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
                }
                self._log_data_quality(stock_info, "get_stock_basic")
                return stock_info
            else:
                self._log_request_error("get_stock_basic", Exception("股票不存在"))
                return None

        except Exception as e:
            self._log_request_error("get_stock_basic", e)
            return None

    async def get_stock_daily(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """获取日线数据"""
        try:
            self._log_request_start(
                "get_stock_daily", {"stock_code": stock_code, "start_date": start_date, "end_date": end_date}
            )

            sql = f"""
            SELECT 
                date as trade_date,
                open as open,
                high as high,
                low as low,
                close as close,
                volume as volume,
                amount as amount
            FROM tdx_daily_data
            WHERE code = '{stock_code}'
              AND date >= '{start_date}'
              AND date <= '{end_date}'
            ORDER BY date ASC
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
            for stock_code in stock_codes[:100]:
                sql = f"""
                SELECT 
                    code as symbol,
                    name as name,
                    price as price,
                    change as change,
                    volume as volume,
                    amount as amount,
                    time as quote_time
                FROM tdx_realtime_quotes
                WHERE code = '{stock_code}'
                ORDER BY time DESC
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
                            "volume": result["volume"],
                            "amount": result["amount"],
                            "quote_time": result["quote_time"].isoformat() if result["quote_time"] else "",
                        }
                    )

            self._log_request_success("get_realtime_quotes", f"返回{len(quotes)}条实时行情")
            self._log_data_quality(quotes, "get_realtime_quotes")
            return quotes

        except Exception as e:
            self._log_request_error("get_realtime_quotes", e)
            return []

    async def get_board_data(self, board_type: str = "lhb") -> Optional[List[Dict]]:
        """获取龙虎榜数据"""
        try:
            self._log_request_start("get_board_data", {"board_type": board_type})

            sql = f"""
            SELECT 
                code as symbol,
                name as name,
                board_date as board_date,
                rank as rank,
                reason as reason
                main_buy as main_buy,
                main_sell as main_sell,
                retail_buy as retail_buy,
                retail_sell as retail_sell
            FROM tdx_board_data
            WHERE board_type = '{board_type}'
            ORDER BY board_date DESC, rank ASC
            LIMIT 50
            """

            results = await self.db_service.fetch_many(sql)

            if results:
                self._log_request_success("get_board_data", f"返回{len(results)}条{board_type}数据")
                board_data = []
                for result in results:
                    board_data.append(
                        {
                            "symbol": result["symbol"],
                            "name": result["name"],
                            "board_date": result["board_date"].isoformat() if result["board_date"] else "",
                            "rank": result["rank"],
                            "reason": result["reason"],
                            "main_buy": result["main_buy"],
                            "main_sell": result["main_sell"],
                            "retail_buy": result["retail_buy"],
                            "retail_sell": result["retail_sell"],
                        }
                    )
                self._log_data_quality(board_data, "get_board_data")
                return board_data
            else:
                self._log_request_error("get_board_data", Exception("未返回数据"))
                return []

        except Exception as e:
            self._log_request_error("get_board_data", e)
            return []

    async def check_health(self) -> Optional[str]:
        """检查健康状态"""
        try:
            self._log_request_start("check_health", {})

            sql = """
            SELECT COUNT(*) as count
            FROM tdx_stocks
            """

            result = await self.db_service.fetch_one(sql)

            if result and result["count"] > 0:
                self._log_request_success("check_health", "TDX数据源健康")
                return "healthy"
            else:
                self._log_request_error("check_health", Exception("TDX数据源不可用"))
                return "unhealthy"

        except Exception as e:
            self._log_request_error("check_health", e)
            return f"error: {e}"
