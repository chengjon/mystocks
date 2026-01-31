"""
AkShare Market Overview Mixin

拆分自 src/adapters/akshare/market_data.py
"""

import akshare as ak
import pandas as pd


class MarketOverviewMixin:
    """市场总貌数据方法集合"""

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
        """
        try:
            self.logger.info("[Akshare] 开始获取上海证券交易所市场总貌数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            async def _get_sse_overview():
                return ak.stock_sse_summary()

            df = await _get_sse_overview()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到上海证券交易所市场总貌数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取上海证券交易所市场总貌数据，共 %s 条记录", len(df))

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

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取上海证券交易所市场总貌数据失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_market_overview_szse(self, date: str) -> pd.DataFrame:
        """
        获取深圳证券交易所市场总貌数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD
        """
        try:
            self.logger.info("[Akshare] 开始获取深圳证券交易所市场总貌数据，日期: %s", date)

            @self._retry_api_call
            async def _get_szse_overview():
                return ak.stock_szse_summary(date=date)

            df = await _get_szse_overview()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到深圳证券交易所市场总貌数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳证券交易所市场总貌数据，共 %s 条记录", len(df))

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
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取深圳证券交易所市场总貌数据失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_szse_area_trading_summary(self, date: str) -> pd.DataFrame:
        """
        获取深圳地区交易排序数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD
        """
        try:
            self.logger.info("[Akshare] 开始获取深圳地区交易排序数据，日期: %s", date)

            @self._retry_api_call
            async def _get_szse_area_trading():
                return ak.stock_szse_area_summary(date=date)

            df = await _get_szse_area_trading()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到深圳地区交易排序数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳地区交易排序数据，共 %s 条记录", len(df))

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
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取深圳地区交易排序数据失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_szse_sector_trading_summary(self, symbol: str, date: str) -> pd.DataFrame:
        """
        获取深圳行业成交数据

        Args:
            symbol: 行业代码，如 "BK0477"
            date: 查询日期，格式为YYYY-MM-DD
        """
        try:
            self.logger.info("[Akshare] 开始获取深圳行业成交数据，行业: %s，日期: %s", symbol, date)

            @self._retry_api_call
            async def _get_szse_sector_trading():
                return ak.stock_szse_sector_summary(symbol=symbol, date=date)

            df = await _get_szse_sector_trading()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到深圳行业成交数据，行业: %s，日期: %s", symbol, date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳行业成交数据，共 %s 条记录", len(df))

            df = df.rename(
                columns={
                    "板块代码": "sector_code",
                    "板块名称": "sector_name",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            df["query_symbol"] = symbol
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取深圳行业成交数据失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_sse_daily_deal_summary(self, date: str) -> pd.DataFrame:
        """
        获取上海交易所每日概况数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD
        """
        try:
            self.logger.info("[Akshare] 开始获取上海交易所每日概况数据，日期: %s", date)

            @self._retry_api_call
            async def _get_sse_daily_deal():
                return ak.stock_sse_deal_daily(date=date)

            df = await _get_sse_daily_deal()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到上海交易所每日概况数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取上海交易所每日概况数据，共 %s 条记录", len(df))

            df = df.rename(
                columns={
                    "项目": "item",
                    "数量": "count",
                    "金额": "amount",
                    "占总计": "percentage",
                }
            )

            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取上海交易所每日概况数据失败: %s", e, exc_info=True)
            return pd.DataFrame()


__all__ = ["MarketOverviewMixin"]
