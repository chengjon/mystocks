# pylint: disable=all
"""
AkShare股票信息模块

提供个股信息、概念分类等数据获取功能
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class StockInfoAdapter:
    """股票信息适配器 - AkShare实现"""

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

    def get_concept_classify(self) -> pd.DataFrame:
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
            import akshare as ak

            df = ak.stock_concept_classify()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到概念分类数据")
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

        except Exception as e:
            self.logger.error("[Akshare] 获取概念分类数据失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据"""
        try:
            import akshare as ak

            df = ak.stock_board_industry_name_em()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到行业分类数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取行业分类数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块名称": "name",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                }
            )

            self._add_timestamp(df)
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取行业分类数据失败: %s", str(e), exc_info=True)
            return pd.DataFrame()

    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            import akshare as ak

            self.logger.info("[Akshare] 开始获取股票 %s 的信息...", symbol)

            df = ak.stock_individual_info_em(symbol=symbol)

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的信息", symbol)
                return {"symbol": symbol}

            # 转换为字典格式
            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            return info_dict

        except Exception as e:
            self.logger.error("[Akshare] 获取股票 %s 信息失败: %s", symbol, str(e), exc_info=True)
            return {"symbol": symbol, "error": str(e)}
