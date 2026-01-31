"""
市场数据API模块

提供股票、基金、指数、期货等市场数据获取功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio

logger = __import__("logging").getLogger(__name__)


class MarketDataService:
    """市场数据服务"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_ttl = 300
        self.last_update = None

        logger.info("市场数据API模块初始化")

    async def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            cache_key = f"stock_basic_{stock_code}"

            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]

                age = (datetime.now() - cached_time).total_seconds()
                if age < self.cache_ttl:
                    self.logger.debug(f"返回缓存数据: {stock_code}")
                    return cached_data

            from app.core.database import db_service

            sql = f"""
            SELECT 
                code, name, industry, area,
                list_date, total_share,
                total_assets, is_st, is_hs
            FROM stocks
            WHERE code = '{stock_code}'
            LIMIT 1
            """

            result = await db_service.fetch_one(sql)

            if result:
                stock_data = {
                    "symbol": result["code"],
                    "name": result["name"],
                    "industry": result["industry"],
                    "area": result["area"],
                    "list_date": result["list_date"].isoformat() if result["list_date"] else "",
                    "total_share": result["total_share"],
                    "total_assets": result["total_assets"],
                    "is_st": result["is_st"],
                    "is_hs": result["is_hs"],
                }

                self.cache[cache_key] = (datetime.now(), stock_data)
                self.last_update = datetime.now()

                self.logger.info(f"获取股票基本信息: {stock_code}")
                return stock_data

            self.logger.warning(f"股票不存在: {stock_code}")
            return None

        except Exception as e:
            self.logger.error(f"获取股票基本信息失败: {stock_code}: {e}")
            return None

    async def get_stock_list(
        self, industry: Optional[str] = None, area: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """获取股票列表"""
        try:
            cache_key = f"stock_list_{industry}_{area}_{limit}"

            if cache_key in self.cache:
                return self.cache[cache_key][1]

            from app.core.database import db_service

            sql = f"""
            SELECT code, name, industry, area
            FROM stocks
            WHERE 1=1
            """

            if industry:
                sql += f" AND industry = '{industry}'"

            if area:
                sql += f" AND area = '{area}'"

            sql += f" ORDER BY code LIMIT {limit}"

            results = await db_service.fetch_many(sql)

            if not results:
                return []

            stocks = []
            for result in results:
                stocks.append(
                    {
                        "code": result["code"],
                        "name": result["name"],
                        "industry": result["industry"],
                        "area": result["area"],
                    }
                )

            self.cache[cache_key] = (datetime.now(), stocks)
            self.last_update = datetime.now()

            self.logger.info(f"获取股票列表: {len(stocks)}只")
            return stocks

        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return []

    async def get_stock_quote(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时行情"""
        try:
            cache_key = f"stock_quote_{stock_code}"

            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]

                age = (datetime.now() - cached_time).total_seconds()
                if age < self.cache_ttl:
                    self.logger.debug(f"返回缓存行情: {stock_code}")
                    return cached_data

            from app.core.database import db_service

            sql = f"""
            SELECT 
                price, change, change_percent,
                volume, amount, turnover
            FROM stock_quotes
            WHERE code = '{stock_code}'
            ORDER BY time DESC
            LIMIT 1
            """

            result = await db_service.fetch_one(sql)

            if result:
                quote_data = {
                    "symbol": stock_code,
                    "price": result["price"],
                    "change": result["change"],
                    "change_percent": result["change_percent"],
                    "volume": result["volume"],
                    "amount": result["amount"],
                    "turnover": result["turnover"],
                }

                self.cache[cache_key] = (datetime.now(), quote_data)
                self.last_update = datetime.now()

                self.logger.info(f"获取股票行情: {stock_code}")
                return quote_data

            self.logger.warning(f"股票行情不存在: {stock_code}")
            return None

        except Exception as e:
            self.logger.error(f"获取股票行情失败: {stock_code}: {e}")
            return None

    async def get_multiple_quotes(self, stock_codes: List[str]) -> List[Dict]:
        """批量获取多个股票行情"""
        try:
            quotes = []

            for stock_code in stock_codes[:100]:
                quote = await self.get_stock_quote(stock_code)
                if quote:
                    quotes.append(quote)

            self.logger.info(f"批量获取行情: {len(quotes)}/{len(stock_codes)}")
            return quotes

        except Exception as e:
            self.logger.error(f"批量获取行情失败: {e}")
            return []

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.last_update = None
        self.logger.info("市场数据缓存已清空")

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        cache_size = len(self.cache)
        total_items = sum(len(data) for time, data in self.cache.values())

        return {
            "cache_size": cache_size,
            "total_items": total_items,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }
