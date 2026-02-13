# pylint: disable=all
"""
AkShare市场总貌数据模块

提供上海/深圳交易所的市场总貌数据获取功能
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class MarketOverviewAdapter:
    """市场总貌数据适配器 - AkShare实现"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _add_timestamp(self, df: pd.DataFrame) -> None:
        """添加查询时间戳"""
        if df is not None and not df.empty:
            df["query_timestamp"] = pd.Timestamp.now()

    def _standardize_columns(self, df: pd.DataFrame, column_mapping: dict) -> None:
        """标准化DataFrame列名"""
        if df is not None and not df.empty:
            df.rename(columns=column_mapping, inplace=True)

    def get_market_overview_sse(self) -> pd.DataFrame:
        """
        获取上海证券交易所市场总貌数据

        Returns:
            pd.DataFrame: 上海市场总貌数据
        """
        try:
            import akshare as ak

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
            self.logger.error("[Akshare] 获取上海证券交易所市场总貌数据失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_market_overview_szse(self, date: str = "最新") -> pd.DataFrame:
        """
        获取深圳证券交易所市场总貌数据

        Args:
            date: 日期，默认为最新

        Returns:
            pd.DataFrame: 深圳市场总貌数据
        """
        try:
            import akshare as ak

            self.logger.info("[Akshare] 开始获取深圳证券交易所市场总貌数据，日期: %s", date)

            df = ak.stock_szse_summary(date=date)

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到深圳证券交易所市场总貌数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳证券交易所市场总貌数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "证券类别": "security_type",
                    "股票代码": "symbol",
                    "股票名称": "name",
                    "总市值": "total_market_value",
                    "流通市值": "circulating_market_value",
                    "上市公司家数": "company_count",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取深圳证券交易所市场总貌数据失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_trading_stats_szse(self, date: str = "最新") -> pd.DataFrame:
        """
        获取深圳地区交易排序数据

        Args:
            date: 日期，默认为最新

        Returns:
            pd.DataFrame: 交易排序数据
        """
        try:
            import akshare as ak

            self.logger.info("[Akshare] 开始获取深圳地区交易排序数据，日期: %s", date)

            df = ak.stock_szse_trading_stats(date=date)

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到深圳地区交易排序数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳地区交易排序数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "项目": "item",
                    "数量": "count",
                    "金额": "amount",
                    "占总计": "percentage",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取深圳地区交易排序数据失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_industry_trading_stats_szse(self, date: str = "最新") -> pd.DataFrame:
        """
        获取深圳行业成交数据

        Args:
            date: 日期，默认为最新

        Returns:
            pd.DataFrame: 行业成交数据
        """
        try:
            import akshare as ak

            self.logger.info("[Akshare] 开始获取深圳行业成交数据，日期: %s", date)

            df = ak.stock_szse_industry_trading_stats(date=date)

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到深圳行业成交数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳行业成交数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "行业名称": "industry_name",
                    "涨跌幅": "change_percent",
                    "成交额": "amount",
                    "成交量": "volume",
                    "家数": "company_count",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取深圳行业成交数据失败: %s", str(e), exc_info=True)
            return pd.DataFrame()
