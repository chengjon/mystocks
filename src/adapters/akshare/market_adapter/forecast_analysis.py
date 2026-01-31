"""
AkShare Forecast & Analysis Mixin

拆分自 src/adapters/akshare/market_data.py
"""

import akshare as ak
import pandas as pd


class ForecastAnalysisMixin:
    """预测与技术分析方法集合"""

    async def get_stock_profit_forecast_em(self, symbol: str) -> pd.DataFrame:
        """
        获取盈利预测-东方财富 (akshare.stock_profit_forecast_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取盈利预测，东方财富数据源，股票: %s", symbol)

            @self._retry_api_call
            async def _get_profit_forecast_em():
                return ak.stock_profit_forecast_em(symbol=symbol)

            df = await _get_profit_forecast_em()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的东方财富盈利预测", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的东方财富盈利预测，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "年度": "year",
                    "季度": "quarter",
                    "预测每股收益": "eps_forecast",
                    "预测净利润": "net_profit_forecast",
                    "预测增长率": "growth_rate_forecast",
                    "分析师数量": "analyst_count",
                    "机构名称": "institution",
                }
            )

            df["forecast_source"] = "em"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取盈利预测失败，东方财富数据源，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_profit_forecast_ths(self, symbol: str) -> pd.DataFrame:
        """
        获取盈利预测-同花顺 (akshare.stock_profit_forecast_ths)
        """
        try:
            self.logger.info("[Akshare] 开始获取盈利预测，同花顺数据源，股票: %s", symbol)

            @self._retry_api_call
            async def _get_profit_forecast_ths():
                return ak.stock_profit_forecast_ths(symbol=symbol)

            df = await _get_profit_forecast_ths()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的同花顺盈利预测", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的同花顺盈利预测，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "报告日期": "report_date",
                    "预测类型": "forecast_type",
                    "每股收益预测": "eps_forecast",
                    "营收预测": "revenue_forecast",
                    "净利润预测": "net_profit_forecast",
                    "市盈率预测": "pe_forecast",
                    "分析师评级": "analyst_rating",
                }
            )

            df["forecast_source"] = "ths"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取盈利预测失败，同花顺数据源，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_technical_indicator_em(self, symbol: str) -> pd.DataFrame:
        """
        获取技术指标数据 (akshare.stock_technical_indicator_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取技术指标数据，股票: %s", symbol)

            @self._retry_api_call
            async def _get_technical_indicator():
                return ak.stock_technical_indicator_em(symbol=symbol)

            df = await _get_technical_indicator()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的技术指标数据", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的技术指标数据，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "MA5": "ma5",
                    "MA10": "ma10",
                    "MA20": "ma20",
                    "MA30": "ma30",
                    "MA60": "ma60",
                    "MACD": "macd",
                    "MACD信号": "macd_signal",
                    "MACD柱状图": "macd_hist",
                    "RSI": "rsi",
                    "KDJ_K": "kdj_k",
                    "KDJ_D": "kdj_d",
                    "KDJ_J": "kdj_j",
                    "布林线上轨": "boll_upper",
                    "布林线中轨": "boll_middle",
                    "布林线下轨": "boll_lower",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取技术指标数据失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_account_statistics_em(self, date: str) -> pd.DataFrame:
        """
        获取股票账户统计月度 (akshare.stock_account_statistics_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取股票账户统计月度，日期: %s", date)

            @self._retry_api_call
            async def _get_account_statistics():
                return ak.stock_account_statistics_em(date=date)

            df = await _get_account_statistics()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票账户统计月度数据，日期: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票账户统计月度数据，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "日期": "date",
                    "期末总账户数": "total_accounts",
                    "期末活跃账户数": "active_accounts",
                    "新增账户数": "new_accounts",
                    "休眠账户数": "inactive_accounts",
                    "交易账户数": "trading_accounts",
                    "股票账户数": "stock_accounts",
                    "基金账户数": "fund_accounts",
                    "债券账户数": "bond_accounts",
                }
            )

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取股票账户统计月度失败，日期 %s: %s", date, e, exc_info=True)
            return pd.DataFrame()


__all__ = ["ForecastAnalysisMixin"]
