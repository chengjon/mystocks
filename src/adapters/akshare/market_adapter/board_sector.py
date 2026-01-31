"""
AkShare Board & Sector Mixin

拆分自 src/adapters/akshare/market_data.py
"""

import akshare as ak
import pandas as pd


class BoardSectorMixin:
    """板块与行业相关方法集合"""

    async def get_stock_board_concept_cons_em(self, symbol: str) -> pd.DataFrame:
        """
        获取概念板块成分股 (akshare.stock_board_concept_cons_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取概念板块成分股，板块: %s", symbol)

            @self._retry_api_call
            async def _get_concept_cons():
                return ak.stock_board_concept_cons_em(symbol=symbol)

            df = await _get_concept_cons()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到概念板块成分股，板块: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取概念板块成分股，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "市值": "market_value",
                    "市盈率-动态": "pe_dynamic",
                    "市净率": "pb_ratio",
                }
            )

            df["concept_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取概念板块成分股失败，板块 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_board_concept_hist_em(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取概念板块行情 (akshare.stock_board_concept_hist_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取概念板块行情，板块: %s，日期范围: %s 到 %s", symbol, start_date, end_date)

            @self._retry_api_call
            async def _get_concept_hist():
                return ak.stock_board_concept_hist_em(symbol=symbol, start_date=start_date, end_date=end_date)

            df = await _get_concept_hist()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到概念板块行情，板块: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取概念板块行情，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "amount",
                    "振幅": "amplitude",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "换手率": "turnover_rate",
                }
            )

            df["concept_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取概念板块行情失败，板块 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_board_concept_hist_min_em(self, symbol: str) -> pd.DataFrame:
        """
        获取概念板块历史行情 (akshare.stock_board_concept_hist_min_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取概念板块历史行情，板块: %s", symbol)

            @self._retry_api_call
            async def _get_concept_hist_min():
                return ak.stock_board_concept_hist_min_em(symbol=symbol)

            df = await _get_concept_hist_min()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到概念板块历史行情，板块: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取概念板块历史行情，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "时间": "datetime",
                    "价格": "price",
                    "成交量": "volume",
                }
            )

            df["concept_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取概念板块历史行情失败，板块 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_board_industry_cons_em(self, symbol: str) -> pd.DataFrame:
        """
        获取行业板块成分股 (akshare.stock_board_industry_cons_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取行业板块成分股，板块: %s", symbol)

            @self._retry_api_call
            async def _get_industry_cons():
                return ak.stock_board_industry_cons_em(symbol=symbol)

            df = await _get_industry_cons()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到行业板块成分股，板块: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取行业板块成分股，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "市值": "market_value",
                    "市盈率-动态": "pe_dynamic",
                    "市净率": "pb_ratio",
                }
            )

            df["industry_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取行业板块成分股失败，板块 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_board_industry_hist_em(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取行业板块行情 (akshare.stock_board_industry_hist_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取行业板块行情，板块: %s，日期范围: %s 到 %s", symbol, start_date, end_date)

            @self._retry_api_call
            async def _get_industry_hist():
                return ak.stock_board_industry_hist_em(symbol=symbol, start_date=start_date, end_date=end_date)

            df = await _get_industry_hist()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到行业板块行情，板块: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取行业板块行情，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "amount",
                    "振幅": "amplitude",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "换手率": "turnover_rate",
                }
            )

            df["industry_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取行业板块行情失败，板块 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_board_industry_hist_min_em(self, symbol: str) -> pd.DataFrame:
        """
        获取行业板块分钟行情 (akshare.stock_board_industry_hist_min_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取行业板块历史行情，板块: %s", symbol)

            @self._retry_api_call
            async def _get_industry_hist_min():
                return ak.stock_board_industry_hist_min_em(symbol=symbol)

            df = await _get_industry_hist_min()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到行业板块历史行情，板块: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取行业板块历史行情，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "时间": "datetime",
                    "价格": "price",
                    "成交量": "volume",
                }
            )

            df["industry_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取行业板块历史行情失败，板块 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_sector_spot_em(self) -> pd.DataFrame:
        """
        获取热门行业排行 (akshare.stock_sector_spot_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取热门行业排行")

            @self._retry_api_call
            async def _get_sector_spot():
                return ak.stock_sector_spot_em()

            df = await _get_sector_spot()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到热门行业排行")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取热门行业排行，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "板块": "sector_name",
                    "板块代码": "sector_code",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "rise_count",
                    "下跌家数": "fall_count",
                    "领涨股": "leader_stock",
                }
            )

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取热门行业排行失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_sector_fund_flow_rank_em(self) -> pd.DataFrame:
        """
        获取行业资金流向 (akshare.stock_sector_fund_flow_rank_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取行业资金流向")

            @self._retry_api_call
            async def _get_sector_fund_flow():
                return ak.stock_sector_fund_flow_rank_em()

            df = await _get_sector_fund_flow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到行业资金流向")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取行业资金流向，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "行业板块": "sector_name",
                    "行业代码": "sector_code",
                    "主力净流入-净额": "main_net_inflow",
                    "主力净流入-净占比": "main_net_inflow_ratio",
                    "超大单净流入": "super_large_net_inflow",
                    "大单净流入": "large_net_inflow",
                    "中单净流入": "medium_net_inflow",
                    "小单净流入": "small_net_inflow",
                    "行业涨跌幅": "change_percent",
                }
            )

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取行业资金流向失败: %s", e, exc_info=True)
            return pd.DataFrame()


__all__ = ["BoardSectorMixin"]
