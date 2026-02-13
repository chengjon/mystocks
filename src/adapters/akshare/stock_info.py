# pylint: disable=no-member
"""
AkShare股票信息模块

提供个股信息、概念分类等数据获取功能
"""

import logging
from typing import Optional
import pandas as pd
import akshare as ak

from .base import BaseAkshareAdapter, retry_api_call

logger = logging.getLogger(__name__)


class StockInfoAdapter(BaseAkshareAdapter):
    """股票信息适配器"""
    # 日志记录器
    pass
    @retry_api_call(max_retries=3, delay=1)
    async def get_concept_classify(self) -> pd.DataFrame:
        """
        获取概念分类数据

        Returns:
            pd.DataFrame: 概念分类数据
                - index: 概念代码
                - name: 概念名称
                - latest_price: 最新价
                - change_percent: 涨跌幅
                - change_amount: 涨跌额
                - volume: 成交量
                - amount: 成交额
                - total_market_value: 总市值
                - turnover_rate: 换手率
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - stock_count: 成分股数量
                - leader_stock: 领涨股
        """
        try:
            self.logger.info("[Akshare] 开始获取概念分类数据...")

            df = ak.stock_concept_classify()

            if df is None or df.empty:
                self.logger.info("[Akshare] 未能获取到概念分类数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取概念分类数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                    "领涨股": "leader_stock",
                }
            )

            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            self._add_timestamp(df)
            return df

        except Exception:
            self.logger.error("[Akshare] 获取概念分类数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_industry_classify(self) -> pd.DataFrame:
        """
        获取行业分类数据

        Returns:
            pd.DataFrame: 行业分类数据
                - index: 行业代码
                - name: 行业名称
                - latest_price: 最新价
                - change_percent: 涨跌幅
                - volume: 成交量
                - amount: 成交额
                - total_market_value: 总市值
                - turnover_rate: 换手率
                - up_count: 上涨家数
                - down_count: 下跌家数
                - stock_count: 成分股数量
        """
        try:
            self.logger.info("[Akshare] 开始获取行业分类数据...")

            df = ak.stock_board_industry_name_em()

            if df is None or df.empty:
                self.logger.info("[Akshare] 未能获取到行业分类数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取行业分类数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            self._add_timestamp(df)
            return df

        except Exception:
            self.logger.error("[Akshare] 获取行业分类数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_stock_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取单个股票的基本信息

        Args:
            symbol: 股票代码（如 '600000'）

        Returns:
            pd.DataFrame: 股票基本信息
        """
        try:
            self.logger.info("[Akshare] 开始获取股票 %s 的信息...", symbol)

            df = ak.stock_info_a_code_name()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的信息", symbol)
                return None

            # 筛选指定股票
            df = df[df["code"] == symbol]

            if df.empty:
                self.logger.warning("[Akshare] 未找到股票 %(symbol)s")
                return None

            self.logger.info("[Akshare] 成功获取股票 %s 的信息", symbol)

            # 标准化列名
            df = df.rename(
                columns={
                    "code": "symbol",
                    "name": "stock_name",
                    "area": "area",
                    "industry": "industry",
                    "list_date": "list_date",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception:
            self.logger.error("[Akshare] 获取股票 {symbol} 信息失败: {str(e)}", exc_info=True)
            return None

    @retry_api_call(max_retries=3, delay=1)
    async def get_sse_daily(self, date: str = "") -> pd.DataFrame:
        """
        获取上海交易所每日概况数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD，默认获取最新数据

        Returns:
            pd.DataFrame: 上海交易所每日概况数据
        """
        try:
            self.logger.info("[Akshare] 开始获取上海交易所每日概况数据，日期: %(date)s")

            # pylint: disable=no-member
            if date:
                df = ak.stock_sse_index_spot(date=date)
            else:
                df = ak.stock_sse_index_spot()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到上海交易所每日概况数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取上海交易所每日概况数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "指数代码": "index_code",
                    "指数名称": "index_name",
                    "今收盘": "close",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                }
            )

            if date:
                df["query_date"] = date

            self._add_timestamp(df)
            return df

        except Exception:
            self.logger.error("[Akshare] 获取上海交易所每日概况数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()
