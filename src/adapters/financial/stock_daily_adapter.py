# pylint: disable=import-error,no-name-in-module
"""
# 功能：股票日线数据适配器
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：专门处理股票日线数据的获取和处理
"""

import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from loguru import logger

from .base_financial_adapter import BaseFinancialAdapter


class StockDailyAdapter(BaseFinancialAdapter):
    """
    股票日线数据适配器

    专门处理股票日线数据的获取、验证和格式化
    """

    def __init__(self):
        super().__init__()
        self._efinance_available = False
        self._easyquotation_available = False

    def _check_dependency_availability(self) -> None:
        """检查依赖库的可用性"""
        import importlib.util

        # 检查 efinance 可用性
        if importlib.util.find_spec("efinance"):
            self._efinance_available = True
            logger.info("efinance 库可用")
        else:
            logger.warning("efinance 库不可用")

        # 检查 easyquotation 可用性
        if importlib.util.find_spec("easyquotation"):
            self._easyquotation_available = True
            logger.info("easyquotation 库可用")
        else:
            logger.warning("easyquotation 库不可用")

    def _validate_stock_daily_params(self, symbol: str, start_date: str, end_date: str) -> Tuple[str, str, str]:
        """验证股票日线数据参数"""
        if not symbol:
            raise ValueError("股票代码不能为空")

        if not self._validate_symbol(symbol):
            raise ValueError(f"无效的股票代码格式: {symbol}")

        if not self._validate_date_range(start_date, end_date):
            raise ValueError(f"无效的日期范围: {start_date} 到 {end_date}")

        # 标准化日期格式
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"日期格式错误，应为 YYYY-MM-DD: {e}")

        return symbol, start_date, end_date

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据"""
        symbol, start_date, end_date = self._validate_stock_daily_params(symbol, start_date, end_date)

        cache_key = self._get_cache_key(symbol, "stock_daily", start_date=start_date, end_date=end_date)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info("从缓存获取股票日线数据: %s", symbol)
            return cached_data

        # 按优先级尝试不同的数据源
        data_sources = [
            ("efinance", self._fetch_stock_daily_from_efinance),
            ("easyquotation", self._fetch_stock_daily_from_easyquotation),
        ]

        for source_name, fetch_func in data_sources:
            try:
                data = fetch_func(symbol, start_date, end_date)
                if data is not None and not data.empty:
                    data = self._standardize_column_names(data)
                    self._save_to_cache(cache_key, data)
                    logger.info("通过 %s 获取股票日线数据成功: %s", source_name, symbol)
                    return data
            except Exception as e:
                logger.warning("通过 %s 获取股票日线数据失败: %s", source_name, e)
                continue

        raise Exception(f"所有数据源都无法获取股票 {symbol} 的日线数据")

    def _fetch_stock_daily_from_efinance(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """通过 efinance 获取股票日线数据"""
        if not self._efinance_available:
            raise Exception("efinance 库不可用")

        try:
            import efinance

            # 扩展日期范围以提高成功率
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            # 扩展7天的缓冲期
            buffer_start = (start_dt - timedelta(days=7)).strftime("%Y-%m-%d")
            buffer_end = (end_dt + timedelta(days=7)).strftime("%Y-%m-%d")

            data = efinance.stock.get_quote_history(stock_codes=symbol, beg=buffer_start, end=buffer_end)

            if data is None or data.empty:
                return pd.DataFrame()

            # 过滤到实际需要的日期范围
            data = self._filter_broader_data_by_date(data, start_date, end_date)

            return self._process_efinance_stock_daily_data(data)

        except Exception as e:
            logger.error("efinance 获取股票日线数据失败: %s", e)
            raise

    def _fetch_stock_daily_from_easyquotation(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """通过 easyquotation 获取股票日线数据"""
        if not self._easyquotation_available:
            raise Exception("easyquotation 库不可用")

        try:
            import easyquotation

            # easyquotation 主要用于实时数据，对于历史数据支持有限
            # 这里作为备用数据源，提供当日数据
            quotation = easyquotation.use("sina")
            data = quotation.stocks([symbol])

            if not data or symbol not in data:
                return pd.DataFrame()

            stock_data = data[symbol]

            # 构造当日数据
            today = datetime.now().strftime("%Y-%m-%d")
            df_data = {
                "trade_date": [today],
                "symbol": [symbol],
                "open": [stock_data.get("open", 0)],
                "high": [stock_data.get("high", 0)],
                "low": [stock_data.get("low", 0)],
                "close": [stock_data.get("now", stock_data.get("close", 0))],
                "volume": [stock_data.get("volume", 0)],
                "amount": [stock_data.get("amount", 0)],
            }

            return pd.DataFrame(df_data)

        except Exception as e:
            logger.error("easyquotation 获取股票日线数据失败: %s", e)
            raise

    def _filter_broader_data_by_date(self, data: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """过滤扩展范围数据到指定日期范围"""
        date_col = None

        # 查找日期列
        for col in ["日期", "trade_date", "date", "time"]:
            if col in data.columns:
                date_col = col
                break

        if date_col is None:
            logger.warning("未找到日期列，返回原始数据")
            return data

        try:
            # 确保日期列是datetime类型
            data[date_col] = pd.to_datetime(data[date_col])

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            # 过滤日期范围
            mask = (data[date_col] >= start_dt) & (data[date_col] <= end_dt)
            filtered_data = data[mask].copy()

            logger.info("日期过滤: %s -> %s 条记录", len(data), len(filtered_data))
            return filtered_data

        except Exception as e:
            logger.error("日期过滤失败: %s", e)
            return data

    def _process_efinance_stock_daily_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理 efinance 获取的股票日线数据"""
        if data is None or data.empty:
            return pd.DataFrame()

        try:
            # 检查必要的列是否存在
            required_columns = [
                "股票代码",
                "日期",
                "开盘",
                "最高",
                "最低",
                "收盘",
                "成交量",
            ]
            missing_columns = [col for col in required_columns if col not in data.columns]

            if missing_columns:
                logger.warning("缺少必要的列: %s", missing_columns)
                # 尝试使用备用的列名映射
                column_mapping = {
                    "股票代码": ["代码", "symbol", "code"],
                    "日期": ["trade_date", "date", "时间"],
                    "开盘": ["open", "开盘价"],
                    "最高": ["high", "最高价"],
                    "最低": ["low", "最低价"],
                    "收盘": ["close", "收盘价", "now", "现价"],
                    "成交量": ["volume", "成交量", "成交数量"],
                }

                for required_col in missing_columns:
                    for alt_col in column_mapping.get(required_col, []):
                        if alt_col in data.columns:
                            data = data.rename(columns={alt_col: required_col})
                            break

            # 重新检查是否有必要的列
            final_missing = [col for col in required_columns if col not in data.columns]
            if final_missing:
                logger.error("仍然缺少必要的列: %s", final_missing)
                return pd.DataFrame()

            # 选择需要的列并重命名
            result_data = data[required_columns].copy()

            # 确保数值列是数值类型
            numeric_columns = ["开盘", "最高", "最低", "收盘", "成交量"]
            for col in numeric_columns:
                if col in result_data.columns:
                    result_data[col] = pd.to_numeric(result_data[col], errors="coerce")

            # 删除空值行
            result_data = result_data.dropna()

            logger.info("处理成功，返回 %s 条记录", len(result_data))
            return result_data

        except Exception as e:
            logger.error("处理 efinance 股票日线数据失败: %s", e)
            return pd.DataFrame()

    def get_financial_report(self, symbol: str, report_type: str, period: str) -> dict:
        """获取财务报告 - 此适配器不实现财务报告功能"""
        raise NotImplementedError("StockDailyAdapter 不支持财务报告获取")

    # ==================== IDataSource接口实现（补全） ====================

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            symbol: 指数代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 日线数据

        Note:
            StockDailyAdapter专注于股票日线数据，不支持指数数据
        """
        logger.warning("StockDailyAdapter不支持获取指数日线数据: %s", symbol)
        return pd.DataFrame()

    def get_stock_basic(self, symbol: str) -> Dict:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 股票基本信息

        Note:
            StockDailyAdapter专注于历史日线数据，建议使用其他数据源获取基本信息
        """
        logger.warning("StockDailyAdapter不支持获取股票基本信息: %s", symbol)
        return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """
        获取指数成分股

        Args:
            symbol: 指数代码

        Returns:
            List[str]: 指数成分股代码列表

        Note:
            StockDailyAdapter专注于股票日线数据，不支持指数成分股
        """
        logger.warning("StockDailyAdapter不支持获取指数成分股: %s", symbol)
        return []

    def get_real_time_data(self, symbol: str) -> Dict:
        """
        获取实时数据

        Args:
            symbol: 股票代码

        Returns:
            Dict: 实时数据

        Note:
            StockDailyAdapter专注于历史日线数据，不支持实时数据
        """
        logger.warning("StockDailyAdapter不支持获取实时数据: %s", symbol)
        return {}

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 交易日历数据

        Note:
            StockDailyAdapter专注于股票日线数据，不支持交易日历
        """
        logger.warning("StockDailyAdapter不支持获取交易日历")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            period: 报告期间

        Returns:
            pd.DataFrame: 财务数据

        Note:
            StockDailyAdapter专注于股票日线数据，不支持财务数据
        """
        logger.warning("StockDailyAdapter不支持获取财务数据: %s", symbol)
        return pd.DataFrame()

    def get_news_data(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 返回数量限制

        Returns:
            List[Dict]: 新闻数据列表

        Note:
            StockDailyAdapter专注于股票日线数据，不支持新闻数据
        """
        logger.warning("StockDailyAdapter不支持获取新闻数据")
        return []
