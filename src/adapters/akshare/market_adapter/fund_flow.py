"""
AkShare Fund Flow Mixin

拆分自 src/adapters/akshare/market_data.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import akshare as ak
import pandas as pd

if TYPE_CHECKING:
    from app.services.openstock_client import OpenStockClientError


class FundFlowMixin:
    """资金流向相关方法集合"""

    # ------------------------------------------------------------------
    # OpenStock translation helpers (moved from endpoint layer, Wave 1)
    # ------------------------------------------------------------------

    @staticmethod
    def _translate_northbound_flow_row(record: dict) -> dict:
        """Translate OpenStock NORTHBOUND_FLOW row → frontend truth-source contract.

        Truth source: ``web/frontend/src/views/data/fundFlowPageData.ts`` consumes
        ``板块 / 资金方向 / 成交净买额 / 指数涨跌幅 / 交易日``.
        """
        return {
            "板块": record.get("board_name"),
            "资金方向": record.get("fund_direction"),
            "成交净买额": record.get("net_buy_amount"),
            "指数涨跌幅": record.get("index_change_pct"),
            "交易日": record.get("trade_date"),
            # Preserved extra fields for downstream observability:
            "同期上涨家数": record.get("up_count"),
            "同期下跌家数": record.get("down_count"),
            "同期平盘家数": record.get("flat_count"),
            "关联指数": record.get("related_index"),
            "资金净流入": record.get("fund_net_inflow"),
        }

    @staticmethod
    def _translate_northbound_holding_row(record: dict, symbol: str) -> dict:
        """Translate OpenStock NORTHBOUND_HOLDING row → frontend-friendly columns.

        Mirrors the akshare predecessor (Chinese wide-table) for parity with
        future consumer code and preserves OpenStock richer fields.
        """
        return {
            "symbol": symbol,
            "持股日期": record.get("trade_date"),
            "收盘价": record.get("close"),
            "涨跌幅": record.get("change_pct"),
            "持股数量": record.get("holding_shares"),
            "持股市值": record.get("holding_market_cap"),
            "持股比例": record.get("holding_shares_ratio"),
            "增持数量": record.get("add_shares"),
            "增持金额": record.get("add_amount"),
            "持股市值变化": record.get("holding_market_cap_change"),
        }

    # ------------------------------------------------------------------
    # Wave 1 — OpenStock-backed methods (NORTHBOUND_FLOW / NORTHBOUND_HOLDING)
    # ------------------------------------------------------------------

    async def get_stock_hsgt_fund_flow_summary_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取沪深港通资金流向汇总 (OpenStock NORTHBOUND_FLOW).

        Wave 1 (B4.014 Task #11): 切换至 OpenStock. 不再调用 akshare.
        翻译由 ``_translate_northbound_flow_row`` 完成,
        保持 akshare-era 中文宽表输出.
        """
        result = await self._openstock_client.fetch(
            "NORTHBOUND_FLOW",
            params={"start_date": start_date, "end_date": end_date},
        )
        records = result.data if isinstance(result.data, list) else []
        if not records:
            return pd.DataFrame()

        translated = [self._translate_northbound_flow_row(r) for r in records if isinstance(r, dict)]
        df = pd.DataFrame(translated)
        df["start_date"] = start_date
        df["end_date"] = end_date
        return df

    async def get_stock_hsgt_north_acc_flow_in_em(self, symbol: str) -> pd.DataFrame:
        """
        获取北向资金个股统计 (OpenStock NORTHBOUND_HOLDING).

        P0 fix (B4.014, 2026-06-29): akshare 1.18.60 已移除原函数;
        Wave 1 切换至 OpenStock. 返回中文宽表, 与 akshare 时代字段名兼容.
        """
        result = await self._openstock_client.fetch(
            "NORTHBOUND_HOLDING",
            params={"symbol": symbol},
        )
        records = result.data if isinstance(result.data, list) else []
        if not records:
            return pd.DataFrame()

        translated = [self._translate_northbound_holding_row(r, symbol) for r in records if isinstance(r, dict)]
        return pd.DataFrame(translated)

    # ------------------------------------------------------------------
    # Wave 2 (blocked) — still akshare-backed
    # ------------------------------------------------------------------

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
