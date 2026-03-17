"""
# 功能：Efinance数据源适配器补充分片
"""

import logging

import efinance as ef
import pandas as pd

logger = logging.getLogger(__name__)


class EfinanceDataSourceBondQuoteMixin:
    """EfinanceDataSource 债券实时行情方法集"""

    def get_bond_realtime_quotes(self) -> pd.DataFrame:
        """
        获取可转债实时行情

        Returns:
            DataFrame: 可转债实时行情数据
        """
        cache_key = self._get_cache_key("get_bond_realtime_quotes")

        def _fetch():
            try:
                df = ef.bond.get_realtime_quotes()
                if df.empty:
                    return pd.DataFrame()

                column_mapping = {
                    "债券代码": "bond_code",
                    "债券名称": "bond_name",
                    "涨跌幅": "change_percent",
                    "最新价": "latest_price",
                    "最高": "high",
                    "最低": "low",
                    "涨跌额": "change_amount",
                    "换手率": "turnover_rate",
                    "动态市盈率": "pe_ratio",
                    "成交量": "volume",
                    "成交额": "amount",
                    "昨日收盘": "prev_close",
                    "总市值": "total_market_value",
                    "流通市值": "circulating_market_value",
                    "行情ID": "quote_id",
                    "市场类型": "market_type",
                }
                df = df.rename(columns=column_mapping)
                return self._apply_column_mapping(df, "bond_quotes")
            except Exception:
                logger.error("Failed to get bond realtime quotes: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=60)
