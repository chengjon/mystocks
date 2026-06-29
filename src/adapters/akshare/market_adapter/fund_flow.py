"""
AkShare Fund Flow Mixin

拆分自 src/adapters/akshare/market_data.py
"""

import akshare as ak
import pandas as pd


class FundFlowMixin:
    """资金流向相关方法集合"""

    async def get_stock_hsgt_fund_flow_summary_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取沪深港通资金流向汇总 (akshare.stock_hsgt_fund_flow_summary_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取沪深港通资金流向汇总，日期范围: %s 到 %s", start_date, end_date)

            @self._retry_api_call
            async def _get_hsgt_summary():
                return ak.stock_hsgt_fund_flow_summary_em()

            df = await _get_hsgt_summary()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到沪深港通资金流向汇总，日期范围: %s 到 %s", start_date, end_date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取沪深港通资金流向汇总，共 %s 行", len(df))

            # P0 fix (B4.014, 2026-06-29): 上方 rename 基于陈年 akshare 字段
            # (北向资金/南向资金/当日额度/当日余额/当日使用额度), 在 akshare 1.18.60
            # 已完全不存在; 原始接口实际返回 13 列中文宽表, 含前端期望的
            # 板块/资金方向/成交净买额/指数涨跌幅/交易日. 直接透传原始字段.
            # 真相源: web/frontend/src/views/data/fundFlowPageData.ts (前端 mock 契约).
            df["start_date"] = start_date
            df["end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取沪深港通资金流向汇总失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_hsgt_fund_flow_detail_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取沪深港通资金流向明细 (akshare.stock_hsgt_fund_flow_detail_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取沪深港通资金流向明细，日期范围: %s 到 %s", start_date, end_date)

            @self._retry_api_call
            async def _get_hsgt_detail():
                return ak.stock_hsgt_fund_flow_detail_em(start_date=start_date, end_date=end_date)

            df = await _get_hsgt_detail()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到沪深港通资金流向明细，日期范围: %s 到 %s", start_date, end_date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取沪深港通资金流向明细，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "日期": "date",
                    "市场": "market",
                    "资金方向": "direction",
                    "资金金额": "amount",
                    "买入金额": "buy_amount",
                    "卖出金额": "sell_amount",
                    "净流入": "net_inflow",
                }
            )

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取沪深港通资金流向明细失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_hsgt_north_net_flow_in_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取北向资金每日统计 (akshare.stock_hsgt_north_net_flow_in_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取北向资金每日统计，日期范围: %s 到 %s", start_date, end_date)

            @self._retry_api_call
            async def _get_north_flow():
                return ak.stock_hsgt_north_net_flow_in_em(start_date=start_date, end_date=end_date)

            df = await _get_north_flow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到北向资金每日统计，日期范围: %s 到 %s", start_date, end_date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取北向资金每日统计，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "日期": "date",
                    "净流入": "net_flow",
                    "买入金额": "buy_amount",
                    "卖出金额": "sell_amount",
                    "累计净流入": "net_flow_total",
                }
            )

            df["fund_direction"] = "north"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取北向资金每日统计失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_hsgt_south_net_flow_in_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取南向资金每日统计 (akshare.stock_hsgt_south_net_flow_in_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取南向资金每日统计，日期范围: %s 到 %s", start_date, end_date)

            @self._retry_api_call
            async def _get_south_flow():
                return ak.stock_hsgt_south_net_flow_in_em(start_date=start_date, end_date=end_date)

            df = await _get_south_flow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到南向资金每日统计，日期范围: %s 到 %s", start_date, end_date)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取南向资金每日统计，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "日期": "date",
                    "净流入": "net_flow",
                    "买入金额": "buy_amount",
                    "卖出金额": "sell_amount",
                    "累计净流入": "net_flow_total",
                }
            )

            df["fund_direction"] = "south"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取南向资金每日统计失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_hsgt_north_acc_flow_in_em(self, symbol: str) -> pd.DataFrame:
        """
        获取北向资金个股统计.

        P0 fix (B4.014, 2026-06-29): akshare.stock_hsgt_north_acc_flow_in_em 在
        akshare 1.18.60 已被移除 (AttributeError). 待 OpenStock NORTHBOUND_HOLDING
        类别切换时由 Phase 1.1 第二批接管 (见 DOMAIN_MIGRATION_PLAYBOOK.md §三).
        当前返回空 DataFrame, 对应 endpoint 返回 501.
        """
        self.logger.warning(
            "[Akshare] stock_hsgt_north_acc_flow_in_em 在 akshare 1.18.60 已移除, "
            "symbol=%s 的北向个股统计需切换 OpenStock NORTHBOUND_HOLDING", symbol
        )
        return pd.DataFrame()

    async def get_stock_hsgt_south_acc_flow_in_em(self, symbol: str) -> pd.DataFrame:
        """
        获取南向资金个股统计 (akshare.stock_hsgt_south_acc_flow_in_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取南向资金个股统计，股票: %s", symbol)

            @self._retry_api_call
            async def _get_south_acc():
                return ak.stock_hsgt_south_acc_flow_in_em(symbol=symbol)

            df = await _get_south_acc()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到南向资金个股统计，股票: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取南向资金个股统计，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "持股数量": "hold_amount",
                    "持股市值": "hold_market_value",
                    "持股变化数量": "hold_change_amount",
                    "持股变化市值": "hold_change_value",
                }
            )

            df["fund_direction"] = "south"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取南向资金个股统计失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_hsgt_hold_stock_em(self, symbol: str) -> pd.DataFrame:
        """
        获取沪深港通持股明细 (akshare.stock_hsgt_hold_stock_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取沪深港通持股明细，股票: %s", symbol)

            @self._retry_api_call
            async def _get_hsgt_hold():
                return ak.stock_hsgt_hold_stock_em()

            df = await _get_hsgt_hold()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到沪深港通持股明细，股票: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取沪深港通持股明细，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "参与者名称": "participant_name",
                    "持股数量": "hold_amount",
                    "持股比例": "hold_ratio",
                    "市场类型": "market_type",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取沪深港通持股明细失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_fund_flow_big_deal(self) -> pd.DataFrame:
        """
        获取资金流向大单统计 (akshare.stock_fund_flow_big_deal)
        """
        try:
            self.logger.info("[Akshare] 开始获取资金流向大单统计")

            @self._retry_api_call
            async def _get_big_deal():
                return ak.stock_fund_flow_big_deal()

            df = await _get_big_deal()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到资金流向大单统计")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取资金流向大单统计，共 %s 行", len(df))

            # P0 fix (B4.014, 2026-06-29): 上方 rename 基于陈年 akshare 字段
            # (股票名称/大单成交金额/大单买入金额/...), 在 akshare 1.18.60 已不存在;
            # 原始接口返回 9 列含前端 buildStockRanking 期望的
            # 股票简称/成交价格/成交额/大单性质/涨跌幅. 仅做最小 rename
            # (股票代码→symbol) 对齐前端期望, 其余字段保持中文.
            # 真相源: web/frontend/src/views/data/fundFlowPageData.ts buildStockRanking.
            df = df.rename(columns={"股票代码": "symbol"})

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取资金流向大单统计失败: %s", e, exc_info=True)
            return pd.DataFrame()

    async def get_stock_cyq_em(self, symbol: str) -> pd.DataFrame:
        """
        获取筹码分布数据 (akshare.stock_cyq_em)
        """
        try:
            self.logger.info("[Akshare] 开始获取筹码分布数据，股票: %s", symbol)

            @self._retry_api_call
            async def _get_cyq():
                return ak.stock_cyq_em(symbol=symbol)

            df = await _get_cyq()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到筹码分布数据，股票: %s", symbol)
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取筹码分布数据，共 %s 行", len(df))

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "价格区间": "price_range",
                    "筹码数量": "chip_amount",
                    "筹码占比": "chip_ratio",
                    "集中度": "concentration",
                }
            )

            if "symbol" not in df.columns:
                df["symbol"] = symbol

            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except Exception as e:
            self.logger.error("[Akshare] 获取筹码分布数据失败，股票 %s: %s", symbol, e, exc_info=True)
            return pd.DataFrame()


__all__ = ["FundFlowMixin"]
