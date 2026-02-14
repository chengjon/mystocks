"""
TDengine时序数据源实现

基于TDengine超表实现ITimeSeriesDataSource接口。
专门处理高频时序数据的查询和存储。

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from src.core import DataClassification
from src.core.exceptions import (
    DataSourceDataNotFound,
    DataSourceQueryError,
)
from src.data_access.tdengine_access import TDengineDataAccess
from src.interfaces.timeseries_data_source import ITimeSeriesDataSource


class TDengineTimeSeriesDataSourceCheckDataQualityMixin:
    """TDengineTimeSeriesDataSource 方法集 Part 2"""

    def check_data_quality(self, symbol: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        检查时序数据质量

        检查指定时间范围内的数据完整性、准确性和新鲜度。

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            数据质量报告

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            table_name = self._get_table_name("daily_kline", symbol)

            # 查询该时间范围的数据
            start_time = datetime.combine(start_date, datetime.min.time())
            end_time = datetime.combine(end_date, datetime.max.time())

            df = self.td_access.query_by_time_range(table_name=table_name, start_time=start_time, end_time=end_time)

            # 计算交易日数量（简化：按5天一周，去掉周末）
            total_days = (end_date - start_date).days + 1
            expected_records = int(total_days * 5 / 7)  # 简化估算

            actual_records = len(df)
            missing_records = max(0, expected_records - actual_records)
            completeness_rate = (actual_records / expected_records * 100) if expected_records > 0 else 0

            # 检查数据新鲜度
            if not df.empty:
                latest_ts = df["ts"].max()
                data_freshness = latest_ts.isoformat() if isinstance(latest_ts, datetime) else str(latest_ts)
            else:
                data_freshness = None

            # 检查数据异常
            issues = []
            if not df.empty:
                # 检查成交量异常（零成交量）
                zero_volume = df[df["volume"] == 0]
                for _, row in zero_volume.iterrows():
                    issues.append(
                        {
                            "date": row["ts"].date().isoformat() if isinstance(row["ts"], datetime) else str(row["ts"]),
                            "issue": "zero_volume",
                        }
                    )

                # 检查价格异常（涨跌幅超过20%）
                if "change_pct" in df.columns:
                    abnormal_change = df[abs(df["change_pct"]) > 20]
                    for _, row in abnormal_change.iterrows():
                        issues.append(
                            {
                                "date": (
                                    row["ts"].date().isoformat() if isinstance(row["ts"], datetime) else str(row["ts"])
                                ),
                                "issue": f"abnormal_change_{row['change_pct']:.2f}%",
                            }
                        )

            # 计算质量评分
            quality_score = completeness_rate * 0.7  # 完整性占70%
            if data_freshness:
                quality_score += 20  # 有数据加20分
            quality_score = min(100, max(0, quality_score - len(issues) * 2))  # 每个问题扣2分

            return {
                "symbol": symbol,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "total_records": actual_records,
                "expected_records": expected_records,
                "missing_records": missing_records,
                "completeness_rate": round(completeness_rate, 2),
                "data_freshness": data_freshness,
                "quality_score": round(quality_score, 2),
                "issues": issues[:10],  # 最多返回10个问题
            }

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query="check_data_quality",
                details=str(e),
            )

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康状态信息
        """
        try:
            start_time = datetime.now()

            # 测试连接
            conn = self.td_access._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT SERVER_VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "source_type": "tdengine",
                "version": version,
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "source_type": "tdengine",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _get_table_name(self, stable_name: str, symbol: str, is_index: bool = False) -> str:
        """
        获取子表名称

        Args:
            stable_name: 超表名
            symbol: 股票/指数代码
            is_index: 是否为指数

        Returns:
            子表名称
        """
        # 确定交易所后缀
        if is_index:
            exchange = "INDEX"
        elif symbol.startswith("6"):
            exchange = "SH"
        elif symbol.startswith("0") or symbol.startswith("3"):
            exchange = "SZ"
        else:
            exchange = "UNKNOWN"

        return f"{stable_name}_{symbol}_{exchange}"

    def _get_stock_name(self, symbol: str) -> str:
        """
        获取股票名称（从缓存或数据库）

        Args:
            symbol: 股票代码

        Returns:
            股票名称
        """
        try:
            # 首先检查缓存
            if symbol in self._stock_name_cache:
                return self._stock_name_cache[symbol]

            # 从PostgreSQL stock_info表查询
            from src.data_access import PostgreSQLDataAccess

            pg_access = PostgreSQLDataAccess()
            result = pg_access.load_data_by_classification(
                classification=DataClassification.STOCK_INFO,
                filters={"symbol": symbol},
                limit=1,
            )

            if result and len(result) > 0 and "name" in result[0]:
                stock_name = result[0]["name"]
                # 缓存结果以提高性能
                self._stock_name_cache[symbol] = stock_name
                return stock_name
            else:
                # 如果没有找到，使用默认命名规则
                default_name = f"股票{symbol}"
                self._stock_name_cache[symbol] = default_name
                return default_name

        except Exception as e:
            self.logger.warning("获取股票名称失败 %s: %s", symbol, e)
            # 出错时返回默认值
            return f"股票{symbol}"

    def _get_index_name(self, index_code: str) -> str:
        """
        获取指数名称

        Args:
            index_code: 指数代码

        Returns:
            指数名称
        """
        index_map = {
            "sh000001": "上证指数",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
            "sz399300": "沪深300",
        }
        return index_map.get(index_code, index_code)

    def _get_pre_close(self, symbol: str, trade_date: Optional[date] = None) -> float:
        """
        获取昨收价

        Args:
            symbol: 股票代码
            trade_date: 交易日期

        Returns:
            昨收价
        """
        try:
            if trade_date is None:
                trade_date = date.today()

            # 查询前一个交易日的收盘价
            table_name = self._get_table_name("daily_kline", symbol)

            end_time = datetime.combine(trade_date, datetime.min.time())
            start_time = end_time - timedelta(days=7)  # 查询前7天

            df = self.td_access.query_by_time_range(
                table_name=table_name,
                start_time=start_time,
                end_time=end_time,
                limit=1,
            )

            if df.empty:
                return 0.0

            return float(df.iloc[-1]["close"])

        except (IndexError, ValueError, TypeError, KeyError) as e:
            self.logger.error("Failed to get latest price for %s: %s", symbol, e)
            return 0.0

    def _calculate_ma(self, data: List[float], period: int) -> List[float]:
        """
        计算移动平均

        Args:
            data: 价格数据
            period: 周期

        Returns:
            MA值列表
        """
        if len(data) < period:
            return []

        ma_values = []
        for i in range(len(data)):
            if i < period - 1:
                ma_values.append(None)
            else:
                ma = sum(data[i - period + 1 : i + 1]) / period
                ma_values.append(ma)

        return ma_values

    def _calculate_macd(
        self, data: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, List[float]]:
        """
        计算MACD指标

        Args:
            data: 价格数据
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            MACD数据
        """
        if len(data) < slow:
            return {"macd": [], "signal": [], "hist": []}

        # 计算EMA
        ema_fast = self._calculate_ema(data, fast)
        ema_slow = self._calculate_ema(data, slow)

        # 计算MACD = EMA(fast) - EMA(slow)
        macd_line = [f - s if f is not None and s is not None else None for f, s in zip(ema_fast, ema_slow)]

        # 计算Signal = EMA(MACD, signal)
        macd_values = [v for v in macd_line if v is not None]
        signal_line_values = self._calculate_ema(macd_values, signal)

        # 对齐Signal线
        signal_line = [None] * (len(macd_line) - len(signal_line_values)) + signal_line_values

        # 计算柱状图 = MACD - Signal
        hist = [m - s if m is not None and s is not None else None for m, s in zip(macd_line, signal_line)]

        return {"macd": macd_line, "signal": signal_line, "hist": hist}

    def _calculate_ema(self, data: List[float], period: int) -> List[float]:
        """
        计算指数移动平均

        Args:
            data: 价格数据
            period: 周期

        Returns:
            EMA值列表
        """
        if len(data) < period:
            return []

        multiplier = 2 / (period + 1)
        ema_values = []

        # 第一个EMA = SMA
        ema = sum(data[:period]) / period
        ema_values.append(ema)

        # 后续EMA = (Close - EMA_prev) * multiplier + EMA_prev
        for price in data[period:]:
            ema = (price - ema) * multiplier + ema
            ema_values.append(ema)

        return [None] * (period - 1) + ema_values

