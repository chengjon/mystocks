# pylint: disable=all
"""
AkShare资金流向模块

提供主力资金流入流出数据
"""

import logging
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


class FundFlowAdapter:
    """资金流向适配器 - AkShare实现"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _add_timestamp(self, df: pd.DataFrame) -> None:
        """添加查询时间戳"""
        if df is not None and not df.empty:
            df["query_timestamp"] = pd.Timestamp.now()

    def _standardize_columns(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> None:
        """标准化DataFrame列名"""
        if df is not None and not df.empty:
            df.rename(columns=column_mapping, inplace=True)

    def get_fund_flow_hsgt(self) -> pd.DataFrame:
        """
        获取沪深港通资金流向数据

        Returns:
            pd.DataFrame: 资金流向数据
        """
        try:
            import akshare as ak

            df = ak.stock_hsgt_new_fund_flow_statistics()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到沪深港通资金流向数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取沪深港通资金流向数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "沪股通净流入": "sh_net_inflow",
                    "深股通净流入": "sz_net_inflow",
                    "北向净流入": "north_net_inflow",
                    "南向净流入": "south_net_inflow",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取沪深港通资金流向失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_fund_flow_rank(self, market: str = "all") -> pd.DataFrame:
        """
        获取资金流向排行数据

        Args:
            market: 市场类型 ('all', 'sh', 'sz')

        Returns:
            pd.DataFrame: 资金流向排行
        """
        try:
            import akshare as ak

            if market == "sh":
                df = ak.stock_fund_flow_rank(symbol="沪股通")
            elif market == "sz":
                df = ak.stock_fund_flow_rank(symbol="深股通")
            else:
                df = ak.stock_fund_flow_rank(symbol="全部")

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到资金流向排行数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取资金流向排行数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票名称": "name",
                    "净流入": "net_inflow",
                    "净流入率": "net_inflow_rate",
                    "成交额": "amount",
                    "涨跌幅": "change_percent",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取资金流向排行失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_market_fund_flow(self) -> pd.DataFrame:
        """
        获取市场整体资金流向数据

        Returns:
            pd.DataFrame: 市场资金流向
        """
        try:
            import akshare as ak

            df = ak.stock_market_fund_flow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到市场资金流向数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取市场资金流向数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "主力净流入": "main_net_inflow",
                    "散户净流入": "retail_net_inflow",
                    "净流入": "net_inflow",
                    "净流入率": "net_inflow_rate",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取市场资金流向失败: %s", str(e), exc_info=True)
            return pd.DataFrame()
