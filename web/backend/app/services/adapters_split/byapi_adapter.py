"""
BYAPI数据源适配器

提供BYAPI REST API数据获取功能，支持涨跌停股池、技术指标等
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
import asyncio

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class BYAPIAdapter(BaseAdapter):
    """BYAPI数据源适配器"""

    def __init__(self):
        super().__init__(name="BYAPI", source_type="byapi")
        self.db_service = db_service
        self.quality_monitor = get_data_quality_monitor()
        self.api_key = os.getenv("BYAPI_API_KEY", "")
        self.base_url = "https://api.byapi.com"
        self.max_retries = 3
        self.request_timeout = 30

        logger.info(f"初始化{self.name}适配器")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """构建API请求"""
        url = f"{self.base_url}/{endpoint}"

        if not params:
            params = {}

        params["apikey"] = self.api_key
        params["fields"] = "all"

        return {"url": url, "method": "GET", "params": params}

    async def _fetch_with_retry(self, endpoint: str, params: Dict = None, retries: int = None) -> Optional[Any]:
        """带重试机制的请求"""
        if retries is None:
            retries = self.max_retries

        last_error = None

        for attempt in range(retries):
            try:
                self._log_request_start(endpoint, params)

                request_info = self._make_request(endpoint, params)

                async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                    response = await client.get(url=request_info["url"], params=request_info["params"])

                if response.status_code == 200:
                    self._log_request_success(endpoint, response.json())
                    return response.json()
                else:
                    error_msg = f"API返回错误: {response.status_code}"
                    last_error = Exception(error_msg)

                    if attempt < retries - 1:
                        logger.warning(f"{self.name}.{endpoint} 请求失败，重试 {attempt + 1}/{retries}")
                        await asyncio.sleep(2**attempt)
                    else:
                        raise last_error

            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"{self.name}.{endpoint} 所有重试失败: {e}")
                    raise e
                else:
                    logger.warning(f"{self.name}.{endpoint} 第{attempt + 1}次重试: {e}")

            raise Exception(f"请求失败: {last_error}")

    async def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            self._log_request_start("get_stock_basic", {"stock_code": stock_code})

            result = await self._fetch_with_retry("stock/stock", {"code": stock_code})

            if result and "data" in result:
                data = result["data"][0]
                stock_info = {
                    "symbol": stock_code,
                    "name": data.get("name", ""),
                    "industry": data.get("industry", ""),
                    "area": data.get("area", ""),
                    "list_date": data.get("list_date", ""),
                    "total_share": data.get("total_share", 0),
                    "total_assets": data.get("total_assets", 0),
                }
                self._log_request_success("get_stock_basic", stock_info)
                self._log_data_quality(stock_info, "get_stock_basic")
                return stock_info
            else:
                self._log_request_error("get_stock_basic", Exception("未返回数据"))
                return None

        except Exception as e:
            self._log_request_error("get_stock_basic", e)
            logger.error(f"{self.name}.get_stock_basic 异常: {e}")
            return None

    async def get_stock_daily(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """获取日线数据"""
        try:
            self._log_request_start(
                "get_stock_daily", {"stock_code": stock_code, "start_date": start_date, "end_date": end_date}
            )

            result = await self._fetch_with_retry(
                "stock/daily", {"code": stock_code, "start_date": start_date, "end_date": end_date}
            )

            if result and "data" in result:
                daily_data = []
                for item in result["data"]:
                    daily_data.append(
                        {
                            "symbol": stock_code,
                            "trade_date": item.get("trade_date", ""),
                            "open": item.get("open", 0),
                            "high": item.get("high", 0),
                            "low": item.get("low", 0),
                            "close": item.get("close", 0),
                            "volume": item.get("volume", 0),
                            "amount": item.get("amount", 0),
                        }
                    )

                self._log_request_success("get_stock_daily", f"返回{len(daily_data)}条日线数据")
                self._log_data_quality(daily_data, "get_stock_daily")
                return daily_data
            else:
                self._log_request_error("get_stock_daily", Exception("未返回数据"))
                return []

        except Exception as e:
            self._log_request_error("get_stock_daily", e)
            logger.error(f"{self.name}.get_stock_daily 异常: {e}")
            return []

    async def get_limit_stocks(self, status: str = "up") -> Optional[List[Dict]]:
        """获取涨跌停股池"""
        try:
            self._log_request_start("get_limit_stocks", {"status": status})

            result = await self._fetch_with_retry("stock/limit", {"status": status})

            if result and "data" in result:
                limit_stocks = []
                for item in result["data"]:
                    limit_stocks.append(
                        {
                            "symbol": item.get("symbol", ""),
                            "name": item.get("name", ""),
                            "price": item.get("price", 0),
                            "change": item.get("change", 0),
                            "change_percent": item.get("change_percent", 0),
                            "volume": item.get("volume", 0),
                            "amount": item.get("amount", 0),
                            "high": item.get("high", 0),
                            "low": item.get("low", 0),
                            "limit_up": item.get("limit_up", 0),
                            "limit_down": item.get("limit_down", 0),
                        }
                    )

                self._log_request_success("get_limit_stocks", f"返回{len(limit_stocks)}条涨跌停股")
                self._log_data_quality(limit_stocks, "get_limit_stocks")
                return limit_stocks
            else:
                self._log_request_error("get_limit_stocks", Exception("未返回数据"))
                return []

        except Exception as e:
            self._log_request_error("get_limit_stocks", e)
            logger.error(f"{self.name}.get_limit_stocks 异常: {e}")
            return []

    async def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """获取实时行情"""
        try:
            self._log_request_start("get_realtime_quotes", {"stock_codes": stock_codes})

            quotes = []
            for stock_code in stock_codes[:100]:
                try:
                    result = await self._fetch_with_retry("stock/realtime", {"code": stock_code})

                    if result and "data" in result:
                        item = result["data"][0]
                        quotes.append(
                            {
                                "symbol": stock_code,
                                "name": item.get("name", ""),
                                "price": item.get("price", 0),
                                "change": item.get("change", 0),
                                "change_percent": item.get("change_percent", 0),
                                "volume": item.get("volume", 0),
                                "amount": item.get("amount", 0),
                                "quote_time": item.get("quote_time", ""),
                            }
                        )

                except Exception as stock_error:
                    logger.warning(f"获取{stock_code}实时行情失败: {stock_error}")

            self._log_request_success("get_realtime_quotes", f"返回{len(quotes)}条实时行情")
            self._log_data_quality(quotes, "get_realtime_quotes")
            return quotes

        except Exception as e:
            self._log_request_error("get_realtime_quotes", e)
            logger.error(f"{self.name}.get_realtime_quotes 异常: {e}")
            return []

    async def get_board_data(self, board_type: str = "lhb") -> Optional[List[Dict]]:
        """获取龙虎榜数据"""
        try:
            self._log_request_start("get_board_data", {"board_type": board_type})

            result = await self._fetch_with_retry("stock/board", {"board_type": board_type})

            if result and "data" in result:
                board_data = []
                for item in result["data"]:
                    board_data.append(
                        {
                            "symbol": item.get("symbol", ""),
                            "name": item.get("name", ""),
                            "board_date": item.get("board_date", ""),
                            "rank": item.get("rank", 0),
                            "reason": item.get("reason", ""),
                            "main_buy": item.get("main_buy", 0),
                            "main_sell": item.get("main_sell", 0),
                            "retail_buy": item.get("retail_buy", 0),
                            "retail_sell": item.get("retail_sell", 0),
                        }
                    )

                self._log_request_success("get_board_data", f"返回{len(board_data)}条龙虎榜数据")
                self._log_data_quality(board_data, "get_board_data")
                return board_data
            else:
                self._log_request_error("get_board_data", Exception("未返回数据"))
                return []

        except Exception as e:
            self._log_request_error("get_board_data", e)
            logger.error(f"{self.name}.get_board_data 异常: {e}")
            return []

    async def check_health(self) -> Optional[str]:
        """检查健康状态"""
        try:
            self._log_request_start("check_health", {})

            result = await self._fetch_with_retry("system/status", {})

            if result and "data" in result:
                status = result["data"].get("status", "unhealthy")

                self._log_request_success("check_health", f"BYAPI状态: {status}")
                return status
            else:
                self._log_request_error("check_health", Exception("未返回数据"))
                return "unhealthy"

        except Exception as e:
            self._log_request_error("check_health", e)
            return f"error: {e}"
