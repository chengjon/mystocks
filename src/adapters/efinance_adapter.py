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
from datetime import datetime
from typing import Any, Dict, List, Optional

import efinance as ef
import pandas as pd

from src.core.data_source.circuit_breaker import CircuitBreaker
from src.core.data_source.data_quality_validator import DataQualityValidator
from src.core.data_source.smart_cache import SmartCache
from src.interfaces.data_source import IDataSource
from src.utils.column_mapper import ColumnMapper

logger = logging.getLogger(__name__)


class EfinanceDataSource(IDataSource):
    """
    Efinance数据源适配器

    实现基于efinance库的金融数据获取，支持：
    - 股票历史K线、实时行情、龙虎榜、业绩数据、资金流向
    - 基金历史净值、持仓信息、基本信息
    - 可转债实时行情、基本信息、K线数据
    - 期货基本信息、历史行情、实时行情

    集成优化组件：
    - SmartCache: 智能缓存系统
    - CircuitBreaker: 熔断器保护
    - DataQualityValidator: 数据质量验证
    """

    def __init__(
        self,
        use_smart_cache: bool = True,
        use_circuit_breaker: bool = True,
        use_quality_validator: bool = True,
        cache_ttl: int = 300,  # 5分钟默认TTL
        circuit_breaker_threshold: int = 3,
        enable_column_mapping: bool = True,
    ):
        """
        初始化Efinance适配器

        Args:
            use_smart_cache: 是否启用智能缓存
            use_circuit_breaker: 是否启用熔断器
            use_quality_validator: 是否启用数据质量验证
            cache_ttl: 缓存TTL(秒)
            circuit_breaker_threshold: 熔断器失败阈值
            enable_column_mapping: 是否启用列名标准化
        """
        self.enable_column_mapping = enable_column_mapping
        self.column_mapper = ColumnMapper() if enable_column_mapping else None

        # 初始化优化组件
        self.smart_cache = (
            SmartCache(maxsize=200, default_ttl=cache_ttl, refresh_threshold=0.8, soft_expiry=True)
            if use_smart_cache
            else None
        )

        self.circuit_breaker = (
            CircuitBreaker(failure_threshold=circuit_breaker_threshold, recovery_timeout=60, name="efinance_api")
            if use_circuit_breaker
            else None
        )

        self.quality_validator = (
            DataQualityValidator(
                enable_logic_check=True,
                enable_business_check=True,
                enable_statistical_check=True,
                enable_cross_source_check=False,
            )
            if use_quality_validator
            else None
        )

        logger.info(
            "EfinanceDataSource initialized with optimizations: "
            f"cache={use_smart_cache}, circuit_breaker={use_circuit_breaker}, "
            f"validator={use_quality_validator}"
        )

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [method]
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (list, tuple)):
                v = ",".join(str(x) for x in v)
            key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)

    def _apply_column_mapping(self, df: pd.DataFrame, mapping_type: str) -> pd.DataFrame:
        """应用列名映射"""
        if self.enable_column_mapping and self.column_mapper:
            return self.column_mapper.standardize_columns(df, mapping_type)
        return df

    def _validate_and_cache(self, method_name: str, data: Any, cache_key: str = None, **kwargs) -> Any:
        """统一的验证和缓存处理"""
        # 数据质量验证
        if self.quality_validator and isinstance(data, pd.DataFrame):
            summary = self.quality_validator.validate(data, data_source="efinance")
            if not summary.passed:
                logger.warning(
                    f"Data quality validation failed for {method_name}: "
                    f"{summary.failed_checks}/{summary.total_checks} checks failed"
                )

        # 缓存数据 (如果启用缓存且提供了缓存键)
        if self.smart_cache and cache_key:
            self.smart_cache.set(cache_key, data, ttl=kwargs.get("cache_ttl", 300))

        return data

    def _call_with_circuit_breaker(self, func, *args, **kwargs):
        """带熔断器保护的函数调用"""
        if self.circuit_breaker:
            return self.circuit_breaker.call(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    def _get_cached_or_fetch(self, cache_key: str, fetch_func, **kwargs):
        """智能缓存获取或重新获取"""
        if self.smart_cache:
            cached_data = self.smart_cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # 重新获取数据
        data = self._call_with_circuit_breaker(fetch_func, **kwargs)
        return self._validate_and_cache(fetch_func.__name__, data, cache_key, **kwargs)

    # ========== Stock 股票相关方法 ==========

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            DataFrame: 包含股票日线数据的DataFrame
                列包括: date, open, high, low, close, volume
        """
        cache_key = self._get_cache_key("get_stock_daily", symbol=symbol, start_date=start_date, end_date=end_date)

        def _fetch():
            try:
                # efinance使用日K线参数 klt=101
                df = ef.stock.get_quote_history(symbol, klt=101)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列以匹配接口规范
                column_mapping = {
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

                # 过滤日期范围
                df["date"] = pd.to_datetime(df["date"]).dt.date
                start = pd.to_datetime(start_date).date()
                end = pd.to_datetime(end_date).date()
                df = df[(df["date"] >= start) & (df["date"] <= end)]

                return self._apply_column_mapping(df, "stock_daily")

            except Exception as e:
                logger.error("Failed to get stock daily data for %(symbol)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch)

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            symbol: 指数代码
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            DataFrame: 包含指数日线数据的DataFrame
                列包括: date, open, high, low, close, volume
        """
        # efinance同样支持指数数据，使用相同的API
        return self.get_stock_daily(symbol, start_date, end_date)

    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict[str, Any]: 包含股票基本信息的字典
                键包括: symbol, name, industry, market, list_date等
        """
        cache_key = self._get_cache_key("get_stock_basic", symbol=symbol)

        def _fetch():
            try:
                # efinance没有直接的股票基本信息API，这里返回基本结构
                # 在实际使用中，可能需要从其他数据源补充
                return {
                    "symbol": symbol,
                    "name": f"Stock_{symbol}",  # 占位符
                    "market": "SH" if symbol.startswith(("6", "9")) else "SZ",
                    "list_date": None,  # 占位符
                    "industry": None,  # 占位符
                    "source": "efinance",
                }
            except Exception as e:
                logger.error("Failed to get stock basic info for %(symbol)s: %(e)s")
                return {}

        return self._get_cached_or_fetch(cache_key, _fetch)

    def get_index_components(self, symbol: str) -> List[str]:
        """
        获取指数成分股

        Args:
            symbol: 指数代码

        Returns:
            List[str]: 包含指数成分股代码的列表
        """
        cache_key = self._get_cache_key("get_index_components", symbol=symbol)

        def _fetch():
            try:
                # efinance没有直接的指数成分股API，返回空列表
                # 在实际使用中，可能需要从其他数据源补充
                logger.warning("Index components not available for %(symbol)s in efinance")
                return []
            except Exception as e:
                logger.error("Failed to get index components for %(symbol)s: %(e)s")
                return []

        return self._get_cached_or_fetch(cache_key, _fetch)

    def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时数据

        Args:
            symbol: 股票代码

        Returns:
            Optional[Dict[str, Any]]: 实时数据字典或None
                键包括: symbol, price, volume, timestamp等
        """
        cache_key = self._get_cache_key("get_real_time_data", symbol=symbol)

        def _fetch():
            try:
                # 使用efinance的实时行情API
                df = ef.stock.get_realtime_quotes()
                if df.empty:
                    return None

                # 查找指定股票
                stock_data = df[df["股票代码"] == symbol]
                if stock_data.empty:
                    return None

                row = stock_data.iloc[0]

                return {
                    "symbol": symbol,
                    "name": row.get("股票名称", ""),
                    "price": float(row.get("最新价", 0)),
                    "change": float(row.get("涨跌额", 0)),
                    "change_percent": float(row.get("涨跌幅", 0)),
                    "volume": int(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "open": float(row.get("今开", 0)),
                    "close": float(row.get("昨收", 0)),
                    "turnover_rate": float(row.get("换手率", 0)),
                    "timestamp": datetime.now().isoformat(),
                    "source": "efinance",
                }

            except Exception as e:
                logger.error("Failed to get real-time data for %(symbol)s: %(e)s")
                return None

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=60)  # 实时数据缓存1分钟

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            pd.DataFrame: 交易日历数据
                列包括: date, is_trading_day, market
        """
        cache_key = self._get_cache_key("get_market_calendar", start_date=start_date, end_date=end_date)

        def _fetch():
            try:
                # efinance没有直接的交易日历API，这里生成基本的交易日历
                # 周一到周五为交易日，排除节假日
                from src.utils.date_utils import get_trade_dates

                dates = get_trade_dates(start_date, end_date)

                df = pd.DataFrame(
                    {
                        "date": dates,
                        "is_trading_day": True,
                        "market": "CN",  # 中国市场
                    }
                )

                return df

            except Exception as e:
                logger.error("Failed to get market calendar: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)  # 日历数据缓存1小时

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            period: 报告期间，"annual"或"quarterly"

        Returns:
            pd.DataFrame: 财务数据
                列包括: symbol, end_date, revenue, net_profit等
        """
        cache_key = self._get_cache_key("get_financial_data", symbol=symbol, period=period)

        def _fetch():
            try:
                # 使用efinance的股票业绩数据API
                df = ef.stock.get_all_company_performance()
                if df.empty:
                    return pd.DataFrame()

                # 过滤指定股票
                stock_data = df[df["股票代码"] == symbol]
                if stock_data.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "股票代码": "symbol",
                    "股票简称": "name",
                    "公告日期": "announcement_date",
                    "营业收入": "revenue",
                    "营业收入同比增长": "revenue_yoy",
                    "营业收入季度环比": "revenue_qoq",
                    "净利润": "net_profit",
                    "净利润同比增长": "net_profit_yoy",
                    "净利润季度环比": "net_profit_qoq",
                    "每股收益": "eps",
                    "每股净资产": "bvps",
                    "净资产收益率": "roe",
                    "销售毛利率": "gross_margin",
                    "每股经营现金流量": "ocfps",
                }
                stock_data = stock_data.rename(columns=column_mapping)

                return self._apply_column_mapping(stock_data, "financial_data")

            except Exception as e:
                logger.error("Failed to get financial data for %(symbol)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=86400)  # 财务数据缓存1天

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码，为None时获取市场新闻
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 新闻数据列表
                每个字典包含: title, content, timestamp, source等
        """
        cache_key = self._get_cache_key("get_news_data", symbol=symbol, limit=limit)

        def _fetch():
            try:
                # efinance没有新闻API，返回空列表
                logger.warning("News data not available in efinance")
                return []

            except Exception as e:
                logger.error("Failed to get news data: %(e)s")
                return []

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=1800)  # 新闻数据缓存30分钟

    # ========== 扩展方法：efinance特有功能 ==========

    def get_dragon_tiger_list(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取龙虎榜数据 (efinance特有)

        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            DataFrame: 龙虎榜数据
        """
        if not start_date:
            start_date = (datetime.now() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        cache_key = self._get_cache_key("get_dragon_tiger_list", start_date=start_date, end_date=end_date)

        def _fetch():
            try:
                # 使用efinance的龙虎榜API
                df = ef.stock.get_daily_billboard(start_date=start_date, end_date=end_date)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "股票代码": "symbol",
                    "股票名称": "name",
                    "上榜日期": "list_date",
                    "解读": "analysis",
                    "收盘价": "close_price",
                    "涨跌幅": "change_percent",
                    "换手率": "turnover_rate",
                    "龙虎榜净买额": "net_buy_amount",
                    "龙虎榜买入额": "buy_amount",
                    "龙虎榜卖出额": "sell_amount",
                    "龙虎榜成交额": "trading_amount",
                    "市场总成交额": "market_trading_amount",
                    "净买额占总成交比": "net_buy_ratio",
                    "成交额占总成交比": "trading_ratio",
                    "流通市值": "circulating_market_value",
                    "上榜原因": "reason",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "dragon_tiger")

            except Exception as e:
                logger.error("Failed to get dragon tiger list: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)  # 龙虎榜数据缓存1小时

    def get_fund_flow_data(self, symbol: str) -> pd.DataFrame:
        """
        获取资金流向数据 (efinance特有)

        Args:
            symbol: 股票代码

        Returns:
            DataFrame: 资金流向数据
        """
        cache_key = self._get_cache_key("get_fund_flow_data", symbol=symbol)

        def _fetch():
            try:
                # 使用efinance的历史资金流向API
                df = ef.stock.get_history_bill(symbol)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "股票名称": "name",
                    "股票代码": "symbol",
                    "日期": "date",
                    "主力净流入": "main_force_net_inflow",
                    "小单净流入": "small_order_net_inflow",
                    "中单净流入": "medium_order_net_inflow",
                    "大单净流入": "large_order_net_inflow",
                    "超大单净流入": "super_large_order_net_inflow",
                    "主力净流入占比": "main_force_ratio",
                    "小单流入净占比": "small_order_ratio",
                    "中单流入净占比": "medium_order_ratio",
                    "大单流入净占比": "large_order_ratio",
                    "超大单流入净占比": "super_large_ratio",
                    "收盘价": "close_price",
                    "涨跌幅": "change_percent",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "fund_flow")

            except Exception as e:
                logger.error("Failed to get fund flow data for %(symbol)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=1800)  # 资金流向缓存30分钟

    def get_today_fund_flow(self, symbol: str) -> pd.DataFrame:
        """
        获取今日资金流向数据 (efinance特有)

        Args:
            symbol: 股票代码

        Returns:
            DataFrame: 今日分钟级资金流向数据
        """
        cache_key = self._get_cache_key("get_today_fund_flow", symbol=symbol)

        def _fetch():
            try:
                # 使用efinance的今日资金流向API
                df = ef.stock.get_today_bill(symbol)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "股票名称": "name",
                    "股票代码": "symbol",
                    "时间": "time",
                    "主力净流入": "main_force_net_inflow",
                    "小单净流入": "small_order_net_inflow",
                    "中单净流入": "medium_order_net_inflow",
                    "大单净流入": "large_order_net_inflow",
                    "超大单净流入": "super_large_order_net_inflow",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "today_fund_flow")

            except Exception as e:
                logger.error("Failed to get today fund flow data for %(symbol)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=300)  # 今日数据缓存5分钟

    # ========== Fund 基金相关方法 ==========

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
                # 使用efinance的基金净值API
                df = ef.fund.get_quote_history(fund_code)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
                column_mapping = {
                    "日期": "date",
                    "单位净值": "unit_nav",
                    "累计净值": "cumulative_nav",
                    "涨跌幅": "change_percent",
                }
                df = df.rename(columns=column_mapping)

                return self._apply_column_mapping(df, "fund_history")

            except Exception as e:
                logger.error("Failed to get fund history for %(fund_code)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)  # 基金净值缓存1小时

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
                # 使用efinance的基金持仓API
                df = ef.fund.get_invest_position(fund_code)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
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

            except Exception as e:
                logger.error("Failed to get fund holdings for %(fund_code)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=86400)  # 持仓数据缓存1天

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
                # 使用efinance的基金基本信息API
                df = ef.fund.get_base_info(fund_codes)
                if df.empty:
                    return pd.DataFrame()

                # 重命名列 (efinance返回的列名可能需要根据实际API调整)
                # 这里是示例列名映射
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

            except Exception as e:
                logger.error("Failed to get fund basic info: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=3600)  # 基本信息缓存1小时

    # ========== Bond 债券相关方法 ==========

    def get_bond_realtime_quotes(self) -> pd.DataFrame:
        """
        获取可转债实时行情

        Returns:
            DataFrame: 可转债实时行情数据
        """
        cache_key = self._get_cache_key("get_bond_realtime_quotes")

        def _fetch():
            try:
                # 使用efinance的可转债实时行情API
                df = ef.bond.get_realtime_quotes()
                if df.empty:
                    return pd.DataFrame()

                # 重命名列
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

            except Exception as e:
                logger.error("Failed to get bond realtime quotes: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=60)  # 实时数据缓存1分钟

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

            except Exception as e:
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

            except Exception as e:
                logger.error("Failed to get bond history for %(bond_code)s: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch)

    # ========== Futures 期货相关方法 ==========

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

            except Exception as e:
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

            except Exception as e:
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

            except Exception as e:
                logger.error("Failed to get futures realtime quotes: %(e)s")
                return pd.DataFrame()

        return self._get_cached_or_fetch(cache_key, _fetch, cache_ttl=60)  # 实时数据缓存1分钟

    # ========== 工具方法 ==========

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
