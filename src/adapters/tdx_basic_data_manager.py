"""
TDX基础数据管理器 - 从 tdx_adapter.py 拆分
职责：基础信息获取、股票信息、指数成分
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# 设置日志
logger = logging.getLogger(__name__)


class TdxBasicDataManager:
    """TDX基础数据管理器 - 专注于基础数据管理"""

    def __init__(self):
        """初始化TDX基础数据管理器"""
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存（基础数据变化较少）

    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基础信息

        Args:
            symbol: 股票代码

        Returns:
            Dict[str, Any]: 股票基础信息
        """
        cache_key = f"stock_basic_{symbol}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # 获取股票基础信息
        basic_info = self._fetch_stock_basic_info(symbol)

        # 缓存结果
        self._set_cache(cache_key, basic_info)

        return basic_info

    def get_index_components(self, index_code: str) -> List[str]:
        """
        获取指数成分股

        Args:
            index_code: 指数代码

        Returns:
            List[str]: 成分股代码列表
        """
        cache_key = f"index_components_{index_code}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # 获取指数成分股
        components = self._fetch_index_components(index_code)

        # 缓存结果
        self._set_cache(cache_key, components)

        return components

    def get_market_calendar(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取交易日历

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict[str, Any]]: 交易日历数据
        """
        cache_key = f"market_calendar_{start_date}_{end_date}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # 获取交易日历
        calendar = self._fetch_trading_calendar(start_date, end_date)

        # 缓存结果
        self._set_cache(cache_key, calendar)

        return calendar

    def get_stock_list(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取股票列表

        Args:
            market: 市场代码 (sh, sz, None表示全部)

        Returns:
            List[Dict[str, Any]]: 股票列表
        """
        cache_key = f"stock_list_{market or 'all'}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # 获取股票列表
        stock_list = self._fetch_stock_list(market)

        # 缓存结果
        self._set_cache(cache_key, stock_list)

        return stock_list

    def get_index_list(self) -> List[Dict[str, Any]]:
        """
        获取指数列表

        Returns:
            List[Dict[str, Any]]: 指数列表
        """
        cache_key = "index_list"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        # 获取指数列表
        index_list = self._fetch_index_list()

        # 缓存结果
        self._set_cache(cache_key, index_list)

        return index_list

    def _fetch_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基础信息（内部方法）

        Args:
            symbol: 股票代码

        Returns:
            Dict[str, Any]: 股票基础信息
        """
        logger.debug("Fetching stock basic info for %s", symbol)

        # 模拟股票基础信息
        stock_info_db = {
            "000001": {
                "symbol": "000001",
                "name": "平安银行",
                "industry": "银行",
                "sector": "金融",
                "market": "深交所",
                "list_date": "1991-04-03",
                "total_share": 19405918198,
                "float_share": 19405918198,
                "is_st": False,
            },
            "000002": {
                "symbol": "000002",
                "name": "万科A",
                "industry": "房地产",
                "sector": "房地产",
                "market": "深交所",
                "list_date": "1991-01-29",
                "total_share": 11039132001,
                "float_share": 11039132001,
                "is_st": False,
            },
            "600000": {
                "symbol": "600000",
                "name": "浦发银行",
                "industry": "银行",
                "sector": "金融",
                "market": "上交所",
                "list_date": "1999-11-10",
                "total_share": 29352183296,
                "float_share": 29352183296,
                "is_st": False,
            },
        }

        return stock_info_db.get(
            symbol,
            {
                "symbol": symbol,
                "name": f"股票{symbol}",
                "industry": "未知",
                "sector": "未知",
                "market": "深交所" if symbol.startswith(("0", "3")) else "上交所",
                "list_date": "2020-01-01",
                "total_share": 100000000,
                "float_share": 50000000,
                "is_st": False,
            },
        )

    def _fetch_index_components(self, index_code: str) -> List[str]:
        """
        获取指数成分股（内部方法）

        Args:
            index_code: 指数代码

        Returns:
            List[str]: 成分股代码列表
        """
        logger.debug("Fetching index components for %s", index_code)

        # 模拟指数成分股
        index_components_db = {
            "000001": ["000001", "000002", "000858", "600000", "600036"],  # 上证指数
            "399001": ["000001", "000002", "000858", "600000", "600036"],  # 深证成指
            "399006": ["000001", "000002", "000858", "600000", "600036"],  # 创业板指
        }

        return index_components_db.get(index_code, [])

    def _fetch_trading_calendar(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取交易日历（内部方法）

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict[str, Any]]: 交易日历数据
        """
        logger.debug("Fetching trading calendar from %s to %s", start_date, end_date)

        # 模拟交易日历
        from datetime import datetime
        import random

        result = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        while current_date <= end_date_obj:
            # 简单模拟：周一到周五为交易日，排除一些随机假期
            is_weekday = current_date.weekday() < 5
            is_holiday = random.random() < 0.05  # 5%概率为假期

            if is_weekday and not is_holiday:
                result.append(
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "is_trading": True,
                        "is_holiday": False,
                    }
                )
            elif is_holiday:
                result.append(
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "is_trading": False,
                        "is_holiday": True,
                    }
                )

            current_date += timedelta(days=1)

        return result

    def _fetch_stock_list(self, market: Optional[str]) -> List[Dict[str, Any]]:
        """
        获取股票列表（内部方法）

        Args:
            market: 市场代码

        Returns:
            List[Dict[str, Any]]: 股票列表
        """
        logger.debug("Fetching stock list for market: %s", market)

        # 模拟股票列表
        all_stocks = [
            {"symbol": "000001", "name": "平安银行", "market": "sz"},
            {"symbol": "000002", "name": "万科A", "market": "sz"},
            {"symbol": "000858", "name": "五粮液", "market": "sz"},
            {"symbol": "600000", "name": "浦发银行", "market": "sh"},
            {"symbol": "600036", "name": "招商银行", "market": "sh"},
        ]

        if market:
            market = market.lower()
            return [stock for stock in all_stocks if stock["market"] == market]

        return all_stocks

    def _fetch_index_list(self) -> List[Dict[str, Any]]:
        """
        获取指数列表（内部方法）

        Returns:
            List[Dict[str, Any]]: 指数列表
        """
        logger.debug("Fetching index list")

        # 模拟指数列表
        return [
            {"symbol": "000001", "name": "上证指数", "market": "sh"},
            {"symbol": "399001", "name": "深证成指", "market": "sz"},
            {"symbol": "399006", "name": "创业板指", "market": "sz"},
            {"symbol": "000300", "name": "沪深300", "market": "sh"},
            {"symbol": "399905", "name": "中证500", "market": "sz"},
        ]

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            Optional[Any]: 缓存数据
        """
        if key in self.cache:
            data, timestamp = self.cache[key]

            # 检查是否过期
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return data
            else:
                # 缓存过期，删除
                del self.cache[key]

        return None

    def _set_cache(self, key: str, data: Any):
        """
        设置缓存

        Args:
            key: 缓存键
            data: 缓存数据
        """
        self.cache[key] = (data, datetime.now().timestamp())

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("Basic data cache cleared")

    def get_cache_status(self) -> Dict[str, Any]:
        """
        获取缓存状态

        Returns:
            Dict[str, Any]: 缓存状态
        """
        return {
            "cache_size": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "cached_keys": list(self.cache.keys()),
        }
