"""
Efinance fund helper functions.
"""

from __future__ import annotations

import logging
from typing import List

import efinance as ef
import pandas as pd

logger = logging.getLogger(__name__)


def get_fund_history(self, fund_code: str) -> pd.DataFrame:
    """
    获取基金历史净值数据

    Args:
        fund_code: 基金代码

    Returns:
        DataFrame: 基金历史净值数据
    """
    cache_key = self._get_cache_key("get_fund_history", fund_code=fund_code)

    def _fetch():
        try:
            df = ef.fund.get_quote_history(fund_code)
            if df.empty:
                return pd.DataFrame()

            column_mapping = {
                "日期": "date",
                "单位净值": "unit_nav",
                "累计净值": "cumulative_nav",
                "涨跌幅": "change_percent",
            }
            df = df.rename(columns=column_mapping)

            return self._apply_column_mapping(df, "fund_history")

        except Exception:
            logger.error("Failed to get fund history for %(fund_code)s: %(e)s")
            return pd.DataFrame()

    return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)


def get_fund_holdings(self, fund_code: str) -> pd.DataFrame:
    """
    获取基金持仓信息

    Args:
        fund_code: 基金代码

    Returns:
        DataFrame: 基金持仓信息
    """
    cache_key = self._get_cache_key("get_fund_holdings", fund_code=fund_code)

    def _fetch():
        try:
            df = ef.fund.get_invest_position(fund_code)
            if df.empty:
                return pd.DataFrame()

            column_mapping = {
                "基金代码": "fund_code",
                "股票代码": "stock_code",
                "股票简称": "stock_name",
                "持仓占比": "holding_ratio",
                "较上期变化": "change_from_last",
                "公开日期": "publish_date",
            }
            df = df.rename(columns=column_mapping)

            return self._apply_column_mapping(df, "fund_holdings")

        except Exception:
            logger.error("Failed to get fund holdings for %(fund_code)s: %(e)s")
            return pd.DataFrame()

    return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=86400)


def get_fund_basic_info(self, fund_codes: List[str]) -> pd.DataFrame:
    """
    获取多只基金基本信息

    Args:
        fund_codes: 基金代码列表

    Returns:
        DataFrame: 基金基本信息
    """
    cache_key = self._get_cache_key("get_fund_basic_info", fund_codes=",".join(fund_codes))

    def _fetch():
        try:
            df = ef.fund.get_base_info(fund_codes)
            if df.empty:
                return pd.DataFrame()

            column_mapping = {
                "基金代码": "fund_code",
                "基金名称": "fund_name",
                "成立日期": "establishment_date",
                "最新净值": "latest_nav",
                "净值日期": "nav_date",
                "基金类型": "fund_type",
                "基金经理": "fund_manager",
            }
            df = df.rename(columns=column_mapping)

            return self._apply_column_mapping(df, "fund_basic")

        except Exception:
            logger.error("Failed to get fund basic info: %(e)s")
            return pd.DataFrame()

    return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)
