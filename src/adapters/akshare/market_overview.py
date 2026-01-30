"""
AkShare市场总貌数据模块

提供上海/深圳交易所的市场总貌数据获取功能
"""

import logging
from typing import Optional
import pandas as pd
import akshare as ak

from .base import BaseAkshareAdapter, retry_api_call

logger = logging.getLogger(__name__)


class MarketOverviewAdapter(BaseAkshareAdapter):
    """市场总貌数据适配器"""
    self.logger = logging.getLogger(__name__)
    # 日志记录器

    @retry_api_call(max_retries=3, delay=1)
    async def get_market_overview_sse(self) -> pd.DataFrame:
        """
        获取上海证券交易所市场总貌数据

        Returns:
            pd.DataFrame: 上海市场总貌数据
                - index_code: 指数代码
                - index_name: 指数名称
                - yesterday_close: 昨收
                - today_open: 今开
                - latest_price: 最新价
                - change_percent: 涨跌幅
                - volume: 成交量
                - amount: 成交额
                - query_timestamp: 查询时间戳
        """
        try:
            self.logger.info("[Akshare] 开始获取上海证券交易所市场总貌数据...")

            df = ak.stock_sse_summary()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到上海证券交易所市场总貌数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取上海证券交易所市场总貌数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "指数代码": "index_code",
                    "指数名称": "index_name",
                    "昨收": "yesterday_close",
                    "今开": "today_open",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取上海证券交易所市场总貌数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_market_overview_szse(self, date: str) -> pd.DataFrame:
        """
        获取深圳证券交易所市场总貌数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 深圳市场总貌数据
                - sector: 板块
                - change_percent: 涨跌幅
                - total_market_value: 总市值
                - avg_pe_ratio: 平均市盈率
                - turnover_rate: 换手率
                - up_count: 上涨家数
                - down_count: 下跌家数
                - query_date: 查询日期
                - query_timestamp: 查询时间戳
        """
        try:
            self.logger.info(f"[Akshare] 开始获取深圳证券交易所市场总貌数据，日期: {date}")

            df = ak.stock_szse_summary(date=date)

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到深圳证券交易所市场总貌数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳证券交易所市场总貌数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块": "sector",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "平均市盈率": "avg_pe_ratio",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            df["query_date"] = date
            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取深圳证券交易所市场总貌数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_szse_area_trading_summary(self, date: str) -> pd.DataFrame:
        """
        获取深圳地区交易排序数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 深圳地区交易排序数据
                - region: 地区
                - total_market_value: 总市值
                - avg_pe_ratio: 平均市盈率
                - change_percent: 涨跌幅
                - turnover_rate: 换手率
                - up_count: 上涨家数
                - down_count: 下跌家数
                - query_date: 查询日期
                - query_timestamp: 查询时间戳
        """
        try:
            self.logger.info(f"[Akshare] 开始获取深圳地区交易排序数据，日期: {date}")

            df = ak.stock_szse_area_summary(date=date)

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到深圳地区交易排序数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳地区交易排序数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "地区": "region",
                    "总市值": "total_market_value",
                    "平均市盈率": "avg_pe_ratio",
                    "涨跌幅": "change_percent",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            df["query_date"] = date
            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取深圳地区交易排序数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_szse_industry_trading_summary(self, date: str) -> pd.DataFrame:
        """
        获取深圳行业成交数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 深圳行业成交数据
                - industry: 行业
                - total_market_value: 总市值
                - avg_pe_ratio: 平均市盈率
                - change_percent: 涨跌幅
                - turnover_rate: 换手率
                - up_count: 上涨家数
                - down_count: 下跌家数
                - query_date: 查询日期
                - query_timestamp: 查询时间戳
        """
        try:
            self.logger.info(f"[Akshare] 开始获取深圳行业成交数据，日期: {date}")

            # pylint: disable=no-member
            df = ak.stock_szse_industry_summary(date=date)

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到深圳行业成交数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳行业成交数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "行业": "industry",
                    "总市值": "total_market_value",
                    "平均市盈率": "avg_pe_ratio",
                    "涨跌幅": "change_percent",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            df["query_date"] = date
            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取深圳行业成交数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    async def get_market_overview(self, market: str = "sse", date: Optional[str] = None) -> pd.DataFrame:
        """
        统一获取市场总貌数据

        Args:
            market: 市场类型 ('sse' 或 'szse')
            date: 查询日期（仅szse需要）

        Returns:
            pd.DataFrame: 市场总貌数据
        """
        if market.lower() == "sse":
            return await self.get_market_overview_sse()
        elif market.lower() == "szse":
            if not date:
                date = pd.Timestamp.now().strftime("%Y-%m-%d")
            return await self.get_market_overview_szse(date)
        else:
            raise ValueError(f"不支持的市场类型: {market}")
