"""
TDX K线数据获取器 - 从 tdx_adapter.py 拆分
职责：K线数据获取、批量处理、缓存管理
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
import pandas as pd
from typing import Dict, Any, List, Optional
import time

# 设置日志
logger = logging.getLogger(__name__)


class TdxKlineDataFetcher:
    """TDX K线数据获取器 - 专注于K线数据获取"""

    def __init__(self):
        """初始化TDX K线数据获取器"""
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存

    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 日线数据
        """
        cache_key = f"stock_daily_{symbol}_{start_date}_{end_date}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # 获取数据
        result = self._fetch_kline_data(symbol, start_date, end_date, "daily")

        # 缓存结果
        self._set_cache(cache_key, result)

        return result

    def get_index_daily(
        self, index_code: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            index_code: 指数代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 指数日线数据
        """
        cache_key = f"index_daily_{index_code}_{start_date}_{end_date}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # 获取数据
        result = self._fetch_kline_data(
            index_code, start_date, end_date, "daily", is_index=True
        )

        # 缓存结果
        self._set_cache(cache_key, result)

        return result

    def get_stock_kline(
        self, symbol: str, period: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        获取股票K线数据

        Args:
            symbol: 股票代码
            period: 周期（1min, 5min, 15min, 30min, 60min, daily, weekly, monthly）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: K线数据
        """
        cache_key = f"stock_kline_{symbol}_{period}_{start_date}_{end_date}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # 获取数据
        result = self._fetch_kline_data(symbol, start_date, end_date, period)

        # 缓存结果
        self._set_cache(cache_key, result)

        return result

    def get_index_kline(
        self, index_code: str, period: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        获取指数K线数据

        Args:
            index_code: 指数代码
            period: 周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 指数K线数据
        """
        cache_key = f"index_kline_{index_code}_{period}_{start_date}_{end_date}"

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # 获取数据
        result = self._fetch_kline_data(
            index_code, start_date, end_date, period, is_index=True
        )

        # 缓存结果
        self._set_cache(cache_key, result)

        return result

    def fetch_kline_batch(self, symbol: str, market: int, count: int) -> List[Dict]:
        """
        批量获取K线数据

        Args:
            symbol: 股票代码
            market: 市场代码 (0=上交所, 1=深交所)
            count: 获取数量

        Returns:
            List[Dict]: K线数据列表
        """
        try:
            # 模拟批量请求
            result = self._make_batch_request(symbol, market, count)
            return result
        except Exception as e:
            logger.error(f"Failed to fetch kline batch for {symbol}: {str(e)}")
            return []

    def _fetch_kline_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str,
        is_index: bool = False,
    ) -> pd.DataFrame:
        """
        获取K线数据（内部方法）

        Args:
            symbol: 股票/指数代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期
            is_index: 是否为指数

        Returns:
            pd.DataFrame: K线数据
        """
        logger.info(
            f"Fetching kline data for {symbol} ({period}) from {start_date} to {end_date}"
        )

        # 模拟数据获取
        if is_index:
            # 指数数据模拟
            base_price = 3000.0
        else:
            # 个股数据模拟
            base_price = 10.0

        # 生成模拟数据
        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        data = []

        for i, date in enumerate(dates):
            price = base_price * (1 + 0.01 * (i % 10 - 5))  # 模拟价格波动

            data.append(
                {
                    "time": int(date.timestamp()),
                    "open": round(price * 0.995, 2),
                    "high": round(price * 1.01, 2),
                    "low": round(price * 0.99, 2),
                    "close": round(price, 2),
                    "volume": 1000 + i * 100,
                }
            )

        return pd.DataFrame(data)

    def _make_batch_request(self, symbol: str, market: int, count: int) -> List[Dict]:
        """
        批量请求（内部方法）

        Args:
            symbol: 股票代码
            market: 市场代码
            count: 数量

        Returns:
            List[Dict]: 请求数据
        """
        logger.info(
            f"Making batch request for {symbol}, market={market}, count={count}"
        )

        # 模拟批量数据
        result = []
        base_time = int(time.time()) - count * 60  # 从count分钟前开始

        for i in range(count):
            timestamp = base_time + i * 60
            price = 10.0 + (i % 20) * 0.1  # 模拟价格变化

            result.append(
                {
                    "time": timestamp,
                    "open": round(price * 0.995, 2),
                    "high": round(price * 1.005, 2),
                    "low": round(price * 0.995, 2),
                    "close": round(price, 2),
                    "volume": 100 + i * 10,
                }
            )

        return result

    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            Optional[pd.DataFrame]: 缓存数据
        """
        if key in self.cache:
            cached_data, timestamp = self.cache[key]

            # 检查是否过期
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {key}")
                return cached_data
            else:
                # 缓存过期，删除
                del self.cache[key]
                logger.debug(f"Cache expired for {key}")

        return None

    def _set_cache(self, key: str, data: pd.DataFrame):
        """
        设置缓存

        Args:
            key: 缓存键
            data: 缓存数据
        """
        if data is not None and not data.empty:
            self.cache[key] = (data.copy(), time.time())
            logger.debug(f"Cache set for {key}")

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("Cache cleared")

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
