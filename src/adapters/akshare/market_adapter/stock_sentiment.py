"""
AkShare Stock Sentiment Mixin

拆分自 src/adapters/akshare/market_data.py
"""

import akshare as ak
import pandas as pd


class StockSentimentMixin:
    """个股情绪与新闻数据方法集合"""

    async def get_stock_comment_em(self, symbol: str) -> pd.DataFrame:
        """
        获取千股千评 (akshare.stock_comment_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取千股千评，股票: %s", symbol)

            @self._retry_api_call
            async def _get_comment_em():
                return ak.stock_comment_em()

            df = await _get_comment_em()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的千股千评数据", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的千股千评数据，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "分析师数量": "analyst_count",
                    "平均评级": "rating_average",
                    "买入": "rating_buy",
                    "增持": "rating_overweight",
                    "中性": "rating_hold",
                    "减持": "rating_underweight",
                    "卖出": "rating_sell",
                    "平均目标价": "target_price_avg",
                    "最高目标价": "target_price_high",
                    "最低目标价": "target_price_low",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取千股千评失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_comment_detail_zlkp_jgcyd_em(self, symbol: str) -> pd.DataFrame:
        """
        获取千股千评详情-机构评级 (akshare.stock_comment_detail_zlkp_jgcyd_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取千股千评详情-机构评级，股票: %s", symbol)

            @self._retry_api_call
            async def _get_comment_detail():
                return ak.stock_comment_detail_zlkp_jgcyd_em(symbol=symbol)

            df = await _get_comment_detail()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的千股千评详情", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的千股千评详情，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "分析师": "analyst_name",
                    "机构": "organization",
                    "评级": "rating",
                    "目标价": "target_price",
                    "报告日期": "report_date",
                    "报告标题": "report_title",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取千股千评详情失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_news_em(self, symbol: str) -> pd.DataFrame:
        """
        获取个股新闻 (akshare.stock_news_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取个股新闻，股票: %s", symbol)

            @self._retry_api_call
            async def _get_stock_news():
                return ak.stock_news_em(symbol=symbol)

            df = await _get_stock_news()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的新闻数据", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的新闻数据，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "标题": "title",
                    "内容": "content",
                    "发布时间": "publish_time",
                    "来源": "source",
                    "链接": "url",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取个股新闻失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_bid_ask_em(self, symbol: str) -> pd.DataFrame:
        """
        获取行情报价 (akshare.stock_bid_ask_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取行情报价，股票: %s", symbol)

            @self._retry_api_call
            async def _get_bid_ask():
                return ak.stock_bid_ask_em(symbol=symbol)

            df = await _get_bid_ask()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票 %s 的行情报价", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票 %s 的行情报价，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "买一价": "bid_price_1",
                    "买一量": "bid_volume_1",
                    "卖一价": "ask_price_1",
                    "卖一量": "ask_volume_1",
                    "买二价": "bid_price_2",
                    "买二量": "bid_volume_2",
                    "卖二价": "ask_price_2",
                    "卖二量": "ask_volume_2",
                    "买三价": "bid_price_3",
                    "买三量": "bid_volume_3",
                    "卖三价": "ask_price_3",
                    "卖三量": "ask_volume_3",
                    "买四价": "bid_price_4",
                    "买四量": "bid_volume_4",
                    "卖四价": "ask_price_4",
                    "卖四量": "ask_volume_4",
                    "买五价": "bid_price_5",
                    "买五量": "bid_volume_5",
                    "卖五价": "ask_price_5",
                    "卖五量": "ask_volume_5",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取行情报价失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()


__all__ = ["StockSentimentMixin"]
