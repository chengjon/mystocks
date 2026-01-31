"""
AkShare Stock Profile Mixin

拆分自 src/adapters/akshare/market_data.py
"""

from typing import Any, Dict

import akshare as ak
import pandas as pd


class StockProfileMixin:
    """个股信息数据方法集合"""

    async def get_stock_individual_info_em(self, symbol: str) -> Dict[str, Any]:
        """
        获取个股信息查询-东财 (akshare.stock_individual_info_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取个股信息，东财数据源，股票: %s", symbol)

            @self._retry_api_call
            async def _get_stock_info():
                return ak.stock_individual_info_em(symbol=symbol)

            df = await _get_stock_info()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的东财个股信息", symbol)
                return {"symbol": symbol, "error": "No data found"}

            self.logger.info("[Akshare] 成功获取股票 %s 的东财个股信息，共 %s 条记录", symbol, len(df))

            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            info_dict["query_timestamp"] = pd.Timestamp.now().isoformat()
            return info_dict

        except Exception as e:
            self.logger.error("[Akshare] 获取个股信息失败，东财数据源，股票 %s: %s", symbol, e, exc_info=True)
            return {"symbol": symbol, "error": str(e)}

    async def get_stock_individual_basic_info_xq(self, symbol: str) -> Dict[str, Any]:
        """
        获取个股信息查询-雪球 (akshare.stock_individual_basic_info_xq)
        """
        try:
            self.logger.info("[Akshare] 开始获取个股基本信息，雪球数据源，股票: %s", symbol)

            @self._retry_api_call
            async def _get_stock_basic_xq():
                return ak.stock_individual_basic_info_xq(symbol=symbol)

            df = await _get_stock_basic_xq()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的雪球个股基本信息", symbol)
                return {"symbol": symbol, "error": "No data found"}

            self.logger.info("[Akshare] 成功获取股票 %s 的雪球个股基本信息，共 %s 条记录", symbol, len(df))

            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            info_dict["query_timestamp"] = pd.Timestamp.now().isoformat()
            return info_dict

        except Exception as e:
            self.logger.error("[Akshare] 获取个股基本信息失败，雪球数据源，股票 %s: %s", symbol, e, exc_info=True)
            return {"symbol": symbol, "error": str(e)}

    async def get_stock_zyjs_ths(self, symbol: str) -> Dict[str, Any]:
        """
        获取主营介绍-同花顺 (akshare.stock_zyjs_ths)
        """
        try:
            self.logger.info("[Akshare] 开始获取主营介绍，同花顺数据源，股票: %s", symbol)

            @self._retry_api_call
            async def _get_zyjs_ths():
                return ak.stock_zyjs_ths(symbol=symbol)

            df = await _get_zyjs_ths()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的同花顺主营介绍", symbol)
                return {"symbol": symbol, "error": "No data found"}

            self.logger.info("[Akshare] 成功获取股票 %s 的同花顺主营介绍，共 %s 条记录", symbol, len(df))

            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            info_dict["query_timestamp"] = pd.Timestamp.now().isoformat()
            return info_dict

        except Exception as e:
            self.logger.error("[Akshare] 获取主营介绍失败，同花顺数据源，股票 %s: %s", symbol, e, exc_info=True)
            return {"symbol": symbol, "error": str(e)}

    async def get_stock_zygc_em(self, symbol: str) -> pd.DataFrame:
        """
        获取主营构成-东财 (akshare.stock_zygc_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取主营构成，东财数据源，股票: %s", symbol)

            @self._retry_api_call
            async def _get_zygc_em():
                return ak.stock_zygc_em(symbol=symbol)

            df = await _get_zygc_em()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的东财主营构成", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的东财主营构成，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "业务板块": "business_segment",
                    "营业收入": "revenue",
                    "收入占比": "revenue_ratio",
                    "利润": "profit",
                    "利润占比": "profit_ratio",
                    "报告期": "report_date",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取主营构成失败，东财数据源，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()


__all__ = ["StockProfileMixin"]
