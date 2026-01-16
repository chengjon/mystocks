"""
AkShare资金流向模块

提供股票资金流向数据获取功能
"""

import logging
from typing import Optional
import pandas as pd
import akshare as ak

from .base import BaseAkshareAdapter, retry_api_call

logger = logging.getLogger(__name__)


class FundFlowAdapter(BaseAkshareAdapter):
    """资金流向适配器"""

    @retry_api_call(max_retries=3, delay=1)
    async def get_fund_flow(self, symbol: str = "000001", days: int = 5) -> pd.DataFrame:
        """
        获取股票资金流向数据

        Args:
            symbol: 股票代码（默认 '000001' 上证指数）
            days: 获取天数（默认5天）

        Returns:
            pd.DataFrame: 资金流向数据
                - date: 日期
                - net_inflow_main: 主力净流入
                - net_inflow_small: 小单净流入
                - net_inflow_medium: 中单净流入
                - net_inflow_large: 大单净流入
                - net_inflow_super: 超大单净流入
                - main_ratio: 主力占比
        """
        try:
            self.logger.info(f"[Akshare] 开始获取股票 {symbol} 的资金流向数据，近 {days} 天...")

            df = ak.stock_fund_flow_summary(symbol=symbol)

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的资金流向数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的资金流向数据，共 {len(df)} 条记录")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "主力净流入": "net_inflow_main",
                    "小单净流入": "net_inflow_small",
                    "中单净流入": "net_inflow_medium",
                    "大单净流入": "net_inflow_large",
                    "超大单净流入": "net_inflow_super",
                    "主力净流入占比": "main_ratio",
                }
            )

            # 限制返回天数
            if len(df) > days:
                df = df.head(days)

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(
                f"[Akshare] 获取股票 {symbol} 资金流向数据失败: {str(e)}",
                exc_info=True,
            )
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_fund_flow_hot(self, market: str = "all") -> pd.DataFrame:
        """
        获取资金流向热门股票数据

        Args:
            market: 市场类型 ('all', 'sh', 'sz')

        Returns:
            pd.DataFrame: 资金流向热门股票数据
                - symbol: 股票代码
                - name: 股票名称
                - net_inflow: 净流入
                - net_inflow_rate: 净流入率
                - price_change: 涨跌幅
                - turnover_rate: 换手率
        """
        try:
            self.logger.info(f"[Akshare] 开始获取资金流向热门股票数据，市场: {market}")

            if market == "sh":
                df = ak.stock_fund_flow_rank(indicator="sh")
            elif market == "sz":
                df = ak.stock_fund_flow_rank(indicator="sz")
            else:
                df = ak.stock_fund_flow_rank(indicator="all")

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到资金流向热门股票数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取资金流向热门股票数据，共 {len(df)} 条记录")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票名称": "name",
                    "净流入": "net_inflow",
                    "净流入率": "net_inflow_rate",
                    "涨跌幅": "price_change",
                    "换手率": "turnover_rate",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取资金流向热门股票数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_market_fund_flow(self) -> pd.DataFrame:
        """
        获取市场整体资金流向数据

        Returns:
            pd.DataFrame: 市场资金流向数据
                - market: 市场名称
                - net_inflow: 净流入
                - net_inflow_rate: 净流入率
        """
        try:
            self.logger.info("[Akshare] 开始获取市场整体资金流向数据...")

            df = ak.stock_market_fund_flow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到市场整体资金流向数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取市场整体资金流向数据，共 {len(df)} 条记录")

            # 标准化列名
            df = df.rename(
                columns={
                    "市场": "market",
                    "净流入": "net_inflow",
                    "净流入率": "net_inflow_rate",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取市场整体资金流向数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_sector_fund_flow(self, symbol: str = "000001") -> pd.DataFrame:
        """
        获取板块资金流向数据

        Args:
            symbol: 股票代码，用于获取所属板块

        Returns:
            pd.DataFrame: 板块资金流向数据
        """
        try:
            self.logger.info(f"[Akshare] 开始获取板块资金流向数据，股票: {symbol}")

            df = ak.stock_sector_fund_flow(symbol=symbol)

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到板块资金流向数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取板块资金流向数据，共 {len(df)} 条记录")

            # 标准化列名
            df = df.rename(
                columns={
                    "板块": "sector",
                    "净流入": "net_inflow",
                    "净流入占比": "net_inflow_ratio",
                    "涨跌幅": "price_change",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取板块资金流向数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()
