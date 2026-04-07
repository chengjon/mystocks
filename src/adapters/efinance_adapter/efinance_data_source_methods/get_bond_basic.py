"""
# 功能：Efinance数据源适配器
# 作者：MyStocks Project (Claude Code)
# 创建日期：2026-01-09
# 版本：1.0.0
# 依赖：efinance库，pandas, numpy等
#
# 实现的功能：
#   - Stock: 6个核心函数 (历史K线、实时行情、龙虎榜、业绩数据、资金流向)
#   - Fund: 3个函数 (历史净值、持仓信息、基本信息)
#   - Bond: 3个函数 (实时行情、基本信息、K线数据)
#   - Futures: 3个函数 (基本信息、历史行情、实时行情)
#
# 优化特性：
#   - SmartCache: 智能缓存，TTL+预刷新+软过期
#   - CircuitBreaker: 熔断器保护，防止级联故障
#   - DataQualityValidator: 数据质量验证，多层检查
"""

import logging
from typing import Any, Dict

import efinance as ef
import pandas as pd


logger = logging.getLogger(__name__)


class EfinanceDataSourceGetBondBasicMixin:
    """EfinanceDataSource 方法集 Part 2"""

    def get_bond_basic_info(self) -> pd.DataFrame:
        """
        获取可转债基本信息

        Returns:
            DataFrame: 可转债基本信息
        """
        cache_key = self._get_cache_key("get_bond_basic_info")

        def _fetch():
            try:
                # 使用efinance的可转债基本信息API
                df = ef.bond.get_all_base_info()
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "债券代码": "bond_code",
                    "债券名称": "bond_name",
                    "正股代码": "stock_code",
                    "正股名称": "stock_name",
                    "债券评级": "bond_rating",
                    "申购日期": "subscription_date",
                    "发行规模(亿)": "issue_scale",
                    "网上发行中签率(%)": "online_winning_rate",
                    "上市日期": "listing_date",
                    "到期日期": "maturity_date",
                    "期限(年)": "term_years",
                    "利率说明": "interest_rate_desc",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "bond_basic")

            except Exception:
                logger.error("Failed to get bond basic info: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)  # 基本信息缓存1小时

    def get_bond_history(self, bond_code: str) -> pd.DataFrame:
        """
        获取可转债历史K线数据

        Args:
            bond_code: 债券代码

        Returns:
            DataFrame: 可转债历史K线数据
        """
        cache_key = self._get_cache_key("get_bond_history", bond_code=bond_code)

        def _fetch():
            try:
                # 使用efinance的可转债K线API
                df = ef.bond.get_quote_history(bond_code)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "债券名称": "bond_name",
                    "债券代码": "bond_code",
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
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "bond_history")

            except Exception:
                logger.error("Failed to get bond history for %(bond_code)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch)

    def get_futures_basic_info(self) -> pd.DataFrame:
        """
        获取期货基本信息

        Returns:
            DataFrame: 期货基本信息
        """
        cache_key = self._get_cache_key("get_futures_basic_info")

        def _fetch():
            try:
                # 使用efinance的期货基本信息API
                df = ef.futures.get_futures_base_info()
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "期货代码": "futures_code",
                    "期货名称": "futures_name",
                    "行情ID": "quote_id",
                    "市场类型": "market_type",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "futures_basic")

            except Exception:
                logger.error("Failed to get futures basic info: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)  # 基本信息缓存1小时

    def get_futures_history(self, quote_id: str) -> pd.DataFrame:
        """
        获取期货历史行情

        Args:
            quote_id: 期货行情ID

        Returns:
            DataFrame: 期货历史行情数据
        """
        cache_key = self._get_cache_key("get_futures_history", quote_id=quote_id)

        def _fetch():
            try:
                # 使用efinance的期货历史行情API
                df = ef.futures.get_quote_history(quote_id)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "期货名称": "futures_name",
                    "期货代码": "futures_code",
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
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "futures_history")

            except Exception:
                logger.error("Failed to get futures history for %(quote_id)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch)

    def get_futures_realtime_quotes(self) -> pd.DataFrame:
        """
        获取期货实时行情

        Returns:
            DataFrame: 期货实时行情数据
        """
        cache_key = self._get_cache_key("get_futures_realtime_quotes")

        def _fetch():
            try:
                # 使用efinance的期货实时行情API
                df = ef.futures.get_realtime_quotes()
                if df.empty:
                    return pd.DataFrame()

                # efinance的期货实时行情API返回格式可能需要根据实际调整
                # 这里是示例列名映射
                column_mapping = {
                    "期货代码": "futures_code",
                    "期货名称": "futures_name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "行情ID": "quote_id",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "futures_quotes")

            except Exception:
                logger.error("Failed to get futures realtime quotes: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=60)  # 实时数据缓存1分钟

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if self.smart_cache:
            return self.smart_cache.get_stats()
        return {}

    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """获取熔断器统计信息"""
        if self.circuit_breaker:
            return self.circuit_breaker.get_stats()
        return {}

    def clear_cache(self):
        """清空缓存"""
        if self.smart_cache:
            self.smart_cache.clear()
            logger.info("SmartCache cleared")

    def reset_circuit_breaker(self):
        """重置熔断器"""
        if self.circuit_breaker:
            self.circuit_breaker.reset()
            logger.info("CircuitBreaker reset")

