"""
AkShare Stock Sentiment Mixin

拆分自 src/adapters/akshare/market_data.py
"""

import akshare as ak
import pandas as pd


class StockSentimentMixin:
    """个股情绪与新闻数据方法集合"""

    async def get_stock_zt_pool_em(self, date: str) -> pd.DataFrame:
        """
        获取涨停股池 (akshare.stock_zt_pool_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取涨停股池，交易日: %s", date)

            @self._retry_api_call
            async def _get_stock_zt_pool():
                return ak.stock_zt_pool_em(date=date)

            df = await _get_stock_zt_pool()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到涨停股池数据，交易日: %s", date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取涨停股池数据，交易日 %s，共 %s 行", date, len(df))

            df = df.rename(
                columns={
                    "序号": "sequence_no",
                    "代码": "symbol",
                    "名称": "stock_name",
                    "涨跌幅": "change_percent",
                    "最新价": "latest_price",
                    "成交额": "turnover_amount",
                    "流通市值": "circulating_market_cap",
                    "总市值": "total_market_cap",
                    "换手率": "turnover_rate",
                    "封板资金": "limit_up_fund",
                    "首次封板时间": "first_limit_up_time",
                    "最后封板时间": "last_limit_up_time",
                    "炸板次数": "reopen_count",
                    "涨停统计": "limit_up_stats",
                    "连板数": "consecutive_limit_up_count",
                    "所属行业": "industry",
                }
            )

            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取涨停股池失败，交易日 %s: %s", date, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_hot_follow_xq(self, symbol: str = "最热门") -> pd.DataFrame:
        """
        获取股票热度数据 (akshare.stock_hot_follow_xq)
        """
        try:
            self.logger.info("[Akshare] 开始获取股票热度数据，范围: %s", symbol)

            @self._retry_api_call
            async def _get_stock_hot_follow():
                return ak.stock_hot_follow_xq(symbol=symbol)

            df = await _get_stock_hot_follow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到股票热度数据，范围: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取股票热度数据，范围 %s，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票简称": "stock_name",
                    "关注": "follow_count",
                    "最新价": "latest_price",
                }
            )

            df["query_scope"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取股票热度数据失败，范围 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_board_change_em(self) -> pd.DataFrame:
        """
        获取板块异动详情 (akshare.stock_board_change_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取板块异动详情")

            @self._retry_api_call
            async def _get_board_change():
                return ak.stock_board_change_em()

            df = await _get_board_change()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到板块异动详情")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取板块异动详情，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "板块名称": "board_name",
                    "涨跌幅": "change_percent",
                    "主力净流入": "main_net_inflow",
                    "板块异动总次数": "change_event_count",
                    "板块异动最频繁个股及所属类型-股票代码": "frequent_stock_symbol",
                    "板块异动最频繁个股及所属类型-股票名称": "frequent_stock_name",
                    "板块异动最频繁个股及所属类型-买卖方向": "frequent_stock_direction",
                    "板块具体异动类型列表及出现次数": "change_type_summary",
                }
            )

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取板块异动详情失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_changes_em(self, symbol: str = "大笔买入") -> pd.DataFrame:
        """
        获取盘口异动 (akshare.stock_changes_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取盘口异动，类型: %s", symbol)

            @self._retry_api_call
            async def _get_stock_changes():
                return ak.stock_changes_em(symbol=symbol)

            df = await _get_stock_changes()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到盘口异动数据，类型: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取盘口异动数据，类型 %s，共 %s 行", symbol, len(df))

            df = df.rename(
                columns={
                    "时间": "change_time",
                    "代码": "symbol",
                    "名称": "stock_name",
                    "板块": "change_type",
                    "相关信息": "related_info",
                }
            )

            df["query_type"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取盘口异动失败，类型 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

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
