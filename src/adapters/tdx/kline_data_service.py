"""
# 功能：TDX K线数据服务
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：专门处理TDX K线数据的获取和处理
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd
from loguru import logger

from .base_tdx_adapter import BaseTdxAdapter


class KlineDataService(BaseTdxAdapter):
    """
    TDX K线数据服务

    专门处理股票和指数的K线数据获取
    """

    def __init__(self):
        super().__init__()
        logger.info("TDX K线数据服务初始化完成")

    def get_stock_daily(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "qfq",  # 前复权：qfq(前复权), hfq(后复权), none(不复权)
    ) -> pd.DataFrame:
        """获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期，格式 YYYY-MM-DD
            end_date: 结束日期，格式 YYYY-MM-DD
            adjust: 复权类型

        Returns:
            pd.DataFrame: 日线数据
        """
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")

            # 标准化股票代码
            symbol = self._normalize_symbol(symbol)

            # 设置默认日期范围
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取市场代码
            market_code = self._get_market_code(symbol)

            # 获取日线数据
            logger.info("获取股票日线数据: %s %s ~ %s", symbol, start_date, end_date)
            data = tdx_api.get_k_data(
                code=symbol,
                start_date=start_date,
                end_date=end_date,
            )

            if not data:
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame(
                data,
                columns=[
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "amount",
                    "turnover",
                    "change",
                    "change_pct",
                    "ma5",
                    "ma10",
                    "ma20",
                    "ma60",
                    "v_ma5",
                    "v_ma10",
                    "v_ma20",
                    "v_ma60",
                ],
            )

            # 验证数据
            df = self._validate_kline_data(df)

            # 标准化格式
            df = self._standardize_dataframe(df)

            # 添加额外列
            df["symbol"] = symbol
            df["market"] = "上交所" if market_code == 1 else "深交所"
            df["adjust"] = adjust

            logger.info("成功获取股票日线数据: %s, 共 %s 条记录", symbol, len(df))
            return df

        except Exception as e:
            logger.error("获取股票日线数据失败: %s", e)
            raise

    def get_index_daily(
        self,
        index_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取指数日线数据

        Args:
            index_code: 指数代码
            start_date: 开始日期，格式 YYYY-MM-DD
            end_date: 结束日期，格式 YYYY-MM-DD

        Returns:
            pd.DataFrame: 指数日线数据
        """
        try:
            if not index_code:
                raise ValueError("指数代码不能为空")

            # 标准化指数代码
            index_code = self._normalize_symbol(index_code)

            # 设置默认日期范围
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取指数日线数据
            logger.info("获取指数日线数据: %s %s ~ %s", index_code, start_date, end_date)
            data = tdx_api.get_k_data(
                code=index_code,
                start_date=start_date,
                end_date=end_date,
            )

            if not data:
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame(
                data,
                columns=[
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "amount",
                    "turnover",
                ],
            )

            # 验证数据
            df = self._validate_kline_data(df)

            # 标准化格式
            df = self._standardize_dataframe(df)

            # 添加额外列
            df["symbol"] = index_code
            df["security_type"] = "index"

            logger.info("成功获取指数日线数据: %s, 共 %s 条记录", index_code, len(df))
            return df

        except Exception as e:
            logger.error("获取指数日线数据失败: %s", e)
            raise

    def get_stock_kline(
        self,
        symbol: str,
        period: str = "d1",  # 周期：1d, 1w, 1m
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "qfq",
    ) -> Dict:
        """获取股票K线数据（多种周期）

        Args:
            symbol: 股票代码
            period: 周期类型
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            Dict: K线数据
        """
        try:
            # 周期映射
            period_mapping = {"d1": (9, "日线"), "w1": (5, "周线"), "m1": (6, "月线")}

            if period not in period_mapping:
                raise ValueError(f"不支持的周期类型: {period}")

            frequency, period_name = period_mapping[period]

            # 调用相应的日线或周线/月线获取方法
            if period == "d1":
                df = self.get_stock_daily(symbol, start_date, end_date, adjust)
            else:
                # 对于周线和月线，可以通过调整日期范围来获取
                end_date = datetime.now() if not end_date else datetime.strptime(end_date, "%Y-%m-%d")

                if period == "w1":  # 周线
                    start_date = (
                        (end_date - timedelta(weeks=265))
                        if not start_date
                        else datetime.strptime(start_date, "%Y-%m-%d")
                    )
                elif period == "m1":  # 月线
                    start_date = (
                        (end_date - timedelta(days=365))
                        if not start_date
                        else datetime.strptime(start_date, "%Y-%m-%d")
                    )

                df = self.get_stock_daily(
                    symbol,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    adjust,
                )

                # 重新采样到周线或月线
                df = self._resample_kline_data(df, period)

            result = {
                "symbol": symbol,
                "period": period,
                "period_name": period_name,
                "data": df.to_dict("records") if not df.empty else [],
                "count": len(df) if not df.empty else 0,
                "start_date": (
                    df["datetime"].min().strftime("%Y-%m-%d")
                    if not df.empty and "datetime" in df.columns
                    else start_date
                ),
                "end_date": (
                    df["datetime"].max().strftime("%Y-%m-%d") if not df.empty and "datetime" in df.columns else end_date
                ),
                "timestamp": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            logger.error("获取股票K线数据失败: %s", e)
            return {
                "symbol": symbol,
                "period": period,
                "error": str(e),
                "success": False,
            }

    def get_index_kline(
        self,
        index_code: str,
        period: str = "d1",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """获取指数K线数据（多种周期）

        Args:
            index_code: 指数代码
            period: 周期类型
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict: 指数K线数据
        """
        try:
            # 周期映射
            period_mapping = {"d1": (9, "日线"), "w1": (5, "周线"), "m1": (6, "月线")}

            if period not in period_mapping:
                raise ValueError(f"不支持的周期类型: {period}")

            frequency, period_name = period_mapping[period]

            # 调用相应的日线或周线/月线获取方法
            if period == "d1":
                df = self.get_index_daily(index_code, start_date, end_date)
            else:
                # 对于周线和月线，可以通过调整日期范围来获取
                end_date = datetime.now() if not end_date else datetime.strptime(end_date, "%Y-%m-%d")

                if period == "w1":  # 周线
                    start_date = (
                        (end_date - timedelta(weeks=265))
                        if not start_date
                        else datetime.strptime(start_date, "%Y-%m-%d")
                    )
                elif period == "m1":  # 月线
                    start_date = (
                        (end_date - timedelta(days=365))
                        if not start_date
                        else datetime.strptime(start_date, "%Y-%m-%d")
                    )

                df = self.get_index_daily(
                    index_code,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )

                # 重新采样到周线或月线
                df = self._resample_kline_data(df, period)

            result = {
                "index_code": index_code,
                "period": period,
                "period_name": period_name,
                "data": df.to_dict("records") if not df.empty else [],
                "count": len(df) if not df.empty else 0,
                "start_date": (
                    df["datetime"].min().strftime("%Y-%m-%d")
                    if not df.empty and "datetime" in df.columns
                    else start_date
                ),
                "end_date": (
                    df["datetime"].max().strftime("%Y-%m-%d") if not df.empty and "datetime" in df.columns else end_date
                ),
                "timestamp": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            logger.error("获取指数K线数据失败: %s", e)
            return {
                "index_code": index_code,
                "period": period,
                "error": str(e),
                "success": False,
            }

    def _resample_kline_data(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """重新采样K线数据到指定周期"""
        try:
            if df.empty or "datetime" not in df.columns:
                return df

            # 设置日期为索引
            df = df.copy()
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            # 根据周期重新采样
            if period == "w1":  # 周线
                resampled = df.resample("W").agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }
                )
            elif period == "m1":  # 月线
                resampled = df.resample("M").agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }
                )
            else:
                return df  # 其他周期直接返回

            # 重置索引
            resampled = resampled.reset_index()

            return resampled

        except Exception as e:
            logger.error("重新采样K线数据失败: %s", e)
            return pd.DataFrame()

    def get_minute_kline(
        self, symbol: str, period: str = "1min", count: int = 240, adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取分钟K线数据

        Args:
            symbol: 股票代码
            period: 分钟周期
            count: 获取数量
            adjust: 复权类型

        Returns:
            pd.DataFrame: 分钟K线数据
        """
        try:
            if not symbol:
                raise ValueError("股票代码不能为 empty")

            # 标准化股票代码
            symbol = self._normalize_symbol(symbol)

            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取市场代码
            market_code = self._get_market_code(symbol)

            # 分钟线周期映射
            period_mapping = {"1min": 8, "5min": 0, "15min": 1, "30min": 2, "60min": 4}

            if period not in period_mapping:
                raise ValueError(f"不支持的分钟周期: {period}")

            period_mapping[period]

            # 获取分钟线数据 (使用 get_history_minute_time_data)
            # 注意: TDX API 不支持按数量获取，这里获取最新日期的分钟数据
            logger.info("获取股票分钟K线数据: %s %s", symbol, period)
            data = tdx_api.get_history_minute_time_data(
                market=market_code,
                code=symbol,
                date=datetime.now().strftime("%Y-%m-%d"),
            )

            if not data:
                return pd.DataFrame()

            # 转换为DataFrame
            df = pd.DataFrame(
                data,
                columns=[
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "amount",
                    "change",
                    "change_pct",
                ],
            )

            # 验证数据
            df = self._validate_kline_data(df)

            # 标准化格式
            df = self._standardize_dataframe(df)

            # 添加额外列
            df["symbol"] = symbol
            df["market"] = "上交所" if market_code == 1 else "深交所"
            df["period"] = period
            df["adjust"] = adjust

            logger.info("成功获取股票分钟K线数据: %s, 共 %s 条记录", symbol, len(df))
            return df

        except Exception as e:
            logger.error("获取股票分钟K线数据失败: %s", e)
            raise

    # ==================== IDataSource接口实现（补全） ====================

    def get_stock_basic(self, symbol: str) -> Dict:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 股票基本信息

        Note:
            KlineDataService专注于K线数据，不支持股票基本信息
        """
        logger.warning("KlineDataService不支持获取股票基本信息: %s", symbol)
        return {}

    def get_index_components(self, symbol: str) -> list:
        """
        获取指数成分股

        Args:
            symbol: 指数代码

        Returns:
            list: 指数成分股代码列表

        Note:
            KlineDataService专注于K线数据，不支持指数成分股
        """
        logger.warning("KlineDataService不支持获取指数成分股: %s", symbol)
        return []

    def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """
        获取实时数据

        Args:
            symbol: 股票代码

        Returns:
            Optional[Dict]: 实时数据

        Note:
            KlineDataService专注于历史K线数据，不支持实时数据
        """
        logger.warning("KlineDataService不支持获取实时数据: %s", symbol)
        return None

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 交易日历数据

        Note:
            KlineDataService专注于K线数据，不支持交易日历
        """
        logger.warning("KlineDataService不支持获取交易日历")
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
            KlineDataService专注于K线数据，不支持财务数据
        """
        logger.warning("KlineDataService不支持获取财务数据: %s", symbol)
        return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> list:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 返回数量限制

        Returns:
            list: 新闻数据列表

        Note:
            KlineDataService专注于K线数据，不支持新闻数据
        """
        logger.warning("KlineDataService不支持获取新闻数据")
        return []
