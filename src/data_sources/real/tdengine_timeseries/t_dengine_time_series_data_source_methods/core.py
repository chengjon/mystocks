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

from src.core.exceptions import (
    DataSourceDataNotFound,
    DataSourceQueryError,
)
from src.data_access.tdengine_access import TDengineDataAccess


class TDengineTimeSeriesDataSourceCoreMixin:
    """TDengineTimeSeriesDataSource 方法集 Part 1"""

    def __init__(self, connection_pool_size: int = 10, timeout: int = 30):
        """
        初始化TDengine时序数据源

        Args:
            connection_pool_size: 连接池大小
            timeout: 查询超时时间(秒)
        """
        self.td_access = TDengineDataAccess()
        self.timeout = timeout
        self._conn_pool_size = connection_pool_size
        # 股票名称缓存，提高查询性能
        self._stock_name_cache: Dict[str, str] = {}
        # 初始化logger
        self.logger = logging.getLogger(__name__)

    def get_realtime_quotes(self, symbols: List[str], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        获取实时行情

        从minute_kline超表查询最新1分钟K线作为实时行情。

        Args:
            symbols: 股票代码列表 (如: ["600000", "000001"])
            fields: 返回字段列表

        Returns:
            实时行情列表

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            quotes = []

            for symbol in symbols:
                # 查询最新1分钟K线
                table_name = self._get_table_name("minute_kline", symbol)

                df = self.td_access.query_latest(table_name=table_name, limit=1)

                if df.empty:
                    # 没有数据时返回默认值
                    quotes.append(
                        {
                            "symbol": symbol,
                            "name": self._get_stock_name(symbol),
                            "price": 0.0,
                            "open": 0.0,
                            "high": 0.0,
                            "low": 0.0,
                            "pre_close": 0.0,
                            "change": 0.0,
                            "change_percent": 0.0,
                            "volume": 0,
                            "amount": 0.0,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                row = df.iloc[0]

                # 获取昨收价（查询前一个交易日的收盘价）
                pre_close = self._get_pre_close(symbol)

                # 计算涨跌额和涨跌幅
                change = row["close"] - pre_close
                change_pct = (change / pre_close * 100) if pre_close > 0 else 0.0

                quote = {
                    "symbol": symbol,
                    "name": self._get_stock_name(symbol),
                    "price": float(row["close"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "pre_close": float(pre_close),
                    "change": float(change),
                    "change_percent": float(change_pct),
                    "volume": int(row["volume"]),
                    "amount": float(row["amount"]),
                    "timestamp": row["ts"].isoformat() if isinstance(row["ts"], datetime) else str(row["ts"]),
                }

                quotes.append(quote)

            return quotes

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取实时行情失败: {str(e)}",
                details=f"symbols: {symbols}",
            )

    def get_kline_data(
        self,
        symbol: str,
        period: str = "daily",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000,
        adjust: str = "qfq",
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            symbol: 股票代码
            period: 周期 (1m/5m/15m/30m/60m/daily/weekly/monthly)
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量限制
            adjust: 复权类型 (qfq前复权/hfq后复权/None不复权)

        Returns:
            K线数据列表

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            # 确定查询表名
            if period == "daily":
                table_name = self._get_table_name("daily_kline", symbol)
            else:
                table_name = self._get_table_name("minute_kline", symbol)

            # 构建时间范围
            if start_date is None:
                start_date = date.today() - timedelta(days=365)
            if end_date is None:
                end_date = date.today()

            start_time = datetime.combine(start_date, datetime.min.time())
            end_time = datetime.combine(end_date, datetime.max.time())

            # 查询数据
            df = self.td_access.query_by_time_range(
                table_name=table_name,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            )

            if df.empty:
                return []

            # 转换为字典列表
            klines = []
            for _, row in df.iterrows():
                kline = {
                    "date": row["ts"].date().isoformat() if isinstance(row["ts"], datetime) else str(row["ts"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": int(row["volume"]),
                    "amount": float(row["amount"]),
                }

                # 添加可选字段
                if "change_pct" in row:
                    kline["change_percent"] = float(row["change_pct"])
                if "turn_over" in row:
                    kline["turnover"] = float(row["turn_over"])

                klines.append(kline)

            return klines

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取K线数据失败: {str(e)}",
                details=f"symbol: {symbol}, period: {period}, start_date: {start_date}, end_date: {end_date}",
            )

    def get_intraday_chart(self, symbol: str, trade_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        获取分时图数据

        从minute_kline超表获取指定交易日的分钟数据。

        Args:
            symbol: 股票代码
            trade_date: 交易日期 (None表示今天)

        Returns:
            分时数据列表

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            if trade_date is None:
                trade_date = date.today()

            # 构建时间范围 (9:30-15:00)
            start_time = datetime.combine(trade_date, datetime.min.time().replace(hour=9, minute=30))
            end_time = datetime.combine(trade_date, datetime.min.time().replace(hour=15, minute=0))

            table_name = self._get_table_name("minute_kline", symbol)

            df = self.td_access.query_by_time_range(table_name=table_name, start_time=start_time, end_time=end_time)

            if df.empty:
                return []

            # 获取昨收价
            pre_close = self._get_pre_close(symbol, trade_date)

            # 转换为分时数据
            intraday = []
            for _, row in df.iterrows():
                # 计算均价（使用成交额/成交量）
                avg_price = row["amount"] / row["volume"] if row["volume"] > 0 else row["close"]

                intraday.append(
                    {
                        "time": row["ts"].strftime("%H:%M") if isinstance(row["ts"], datetime) else str(row["ts"]),
                        "price": float(row["close"]),
                        "avg_price": float(avg_price),
                        "volume": int(row["volume"]),
                        "change_percent": float((row["close"] - pre_close) / pre_close * 100) if pre_close > 0 else 0.0,
                    }
                )

            return intraday

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取分时图数据失败: {str(e)}",
                details=f"symbol: {symbol}, trade_date: {trade_date}",
            )

    def get_fund_flow(self, symbol: str, trade_date: Optional[date] = None) -> Dict[str, Any]:
        """
        获取资金流向

        从fund_flow超表查询指定日期的资金流向数据。

        Args:
            symbol: 股票代码
            trade_date: 交易日期 (None表示最新)

        Returns:
            资金流向数据

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            table_name = self._get_table_name("fund_flow", symbol)

            if trade_date:
                # 查询指定日期
                start_time = datetime.combine(trade_date, datetime.min.time())
                end_time = datetime.combine(trade_date, datetime.max.time())

                df = self.td_access.query_by_time_range(
                    table_name=table_name,
                    start_time=start_time,
                    end_time=end_time,
                    limit=1,
                )
            else:
                # 查询最新
                df = self.td_access.query_latest(table_name=table_name, limit=1)

            if df.empty:
                raise DataSourceDataNotFound(
                    source_name="tdengine",
                    data_identifier=f"fund_flow:{symbol}",
                )

            row = df.iloc[0]

            return {
                "symbol": symbol,
                "trade_date": row["ts"].date().isoformat() if isinstance(row["ts"], datetime) else str(row["ts"]),
                "main_net_inflow": float(row["main_net_inflow"]),
                "main_inflow": float(row["main_inflow"]),
                "main_outflow": float(row["main_outflow"]),
                "super_net_inflow": float(row["super_net_inflow"]),
                "large_net_inflow": float(row["large_net_inflow"]),
                "medium_net_inflow": float(row["medium_net_inflow"]),
                "small_net_inflow": float(row["small_net_inflow"]),
                "net_inflow_rate": float(row["net_inflow_rate"]),
            }

        except DataSourceDataNotFound:
            raise
        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取资金流向失败: {str(e)}",
                details=f"symbol: {symbol}",
            )

    def get_top_fund_flow_stocks(
        self,
        trade_date: Optional[date] = None,
        flow_type: str = "main",
        direction: str = "inflow",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        获取资金流向排名

        Args:
            trade_date: 交易日期
            flow_type: 资金类型 (main/super/large/medium/small)
            direction: 方向 (inflow净流入/outflow净流出)
            limit: 返回数量

        Returns:
            资金流向排名列表

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            if trade_date is None:
                trade_date = date.today()

            # 构建字段名
            field_map = {
                "main": "main_net_inflow",
                "super": "super_net_inflow",
                "large": "large_net_inflow",
                "medium": "medium_net_inflow",
                "small": "small_net_inflow",
            }

            field = field_map.get(flow_type, "main_net_inflow")
            order = "DESC" if direction == "inflow" else "ASC"

            # 使用超表查询所有股票的资金流向
            conn = self.td_access._get_connection()
            cursor = conn.cursor()

            start_time = datetime.combine(trade_date, datetime.min.time())
            end_time = datetime.combine(trade_date, datetime.max.time())

            sql = f"""
                SELECT symbol, {field}, net_inflow_rate, ts
                FROM fund_flow
                WHERE ts >= '{start_time.strftime("%Y-%m-%d %H:%M:%S")}'
                  AND ts < '{end_time.strftime("%Y-%m-%d %H:%M:%S")}'
                ORDER BY {field} {order}
                LIMIT {limit}
            """

            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            # 转换结果
            results = []
            for idx, row in enumerate(rows, 1):
                results.append(
                    {
                        "rank": idx,
                        "symbol": row[0],
                        "name": self._get_stock_name(row[0]),
                        "trade_date": trade_date.isoformat(),
                        f"{flow_type}_net_inflow": float(row[1]),
                        "net_inflow_rate": float(row[2]),
                    }
                )

            return results

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query="get_top_fund_flow_stocks",
                details=str(e),
            )

    def get_market_overview(self) -> Dict[str, Any]:
        """
        获取市场概览

        聚合查询所有股票的最新数据，统计涨跌家数。

        Returns:
            市场概览数据

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            conn = self.td_access._get_connection()
            cursor = conn.cursor()

            # 查询所有股票的最新价格和涨跌幅
            sql = """
                SELECT symbol, last(close) as price, last(change_pct) as change_pct
                FROM daily_kline
                WHERE ts >= NOW - 1d
                GROUP BY symbol
            """

            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                return {
                    "total_stocks": 0,
                    "up_count": 0,
                    "down_count": 0,
                    "flat_count": 0,
                    "limit_up_count": 0,
                    "limit_down_count": 0,
                    "total_amount": 0.0,
                    "indices": [],
                }

            # 统计涨跌家数
            up_count = sum(1 for row in rows if row[2] > 0)
            down_count = sum(1 for row in rows if row[2] < 0)
            flat_count = sum(1 for row in rows if row[2] == 0)
            limit_up_count = sum(1 for row in rows if row[2] >= 9.9)
            limit_down_count = sum(1 for row in rows if row[2] <= -9.9)

            # 获取主要指数
            indices = self.get_index_realtime(index_codes=["sh000001", "sz399001", "sz399006", "sz399300"])

            return {
                "total_stocks": len(rows),
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "total_amount": 0.0,  # 需要单独计算
                "indices": indices,
            }

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取市场概览失败: {str(e)}",
            )

    def get_index_realtime(self, index_codes: List[str]) -> List[Dict[str, Any]]:
        """
        获取指数实时行情

        从index_realtime超表查询指数最新数据。

        Args:
            index_codes: 指数代码列表

        Returns:
            指数实时行情列表

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            indices = []

            for index_code in index_codes:
                table_name = self._get_table_name("index_realtime", index_code, is_index=True)

                df = self.td_access.query_latest(table_name=table_name, limit=1)

                if df.empty:
                    continue

                row = df.iloc[0]

                indices.append(
                    {
                        "index_code": index_code,
                        "index_name": self._get_index_name(index_code),
                        "price": float(row["price"]),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "pre_close": float(row["pre_close"]),
                        "change_percent": float(row["change_pct"]),
                        "volume": int(row["volume"]),
                        "amount": float(row["amount"]),
                        "up_count": int(row.get("up_count", 0)),
                        "down_count": int(row.get("down_count", 0)),
                        "timestamp": row["ts"].isoformat() if isinstance(row["ts"], datetime) else str(row["ts"]),
                    }
                )

            return indices

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取指数实时行情失败: {str(e)}",
                details=f"index_codes: {index_codes}",
            )

    def calculate_technical_indicators(
        self,
        symbol: str,
        indicators: List[str],
        period: str = "daily",
        count: int = 100,
    ) -> Dict[str, List[float]]:
        """
        计算技术指标

        基于K线数据计算常用技术指标。

        Args:
            symbol: 股票代码
            indicators: 指标列表 (MA5/MA10/MA20/MACD/KDJ/RSI/BOLL)
            period: K线周期
            count: 计算数据点数

        Returns:
            技术指标数据

        Raises:
            DataSourceQueryError: 查询失败
        """
        try:
            # 获取K线数据
            klines = self.get_kline_data(
                symbol=symbol,
                period=period,
                limit=count + 30,  # 多取30个数据点用于计算
            )

            if not klines:
                return {}

            # 提取收盘价
            closes = [k["close"] for k in klines]

            results = {}

            for indicator in indicators:
                if indicator.startswith("MA"):
                    # 计算移动平均
                    period_num = int(indicator[2:])
                    ma_values = self._calculate_ma(closes, period_num)
                    results[indicator] = ma_values[-count:]

                elif indicator == "MACD":
                    # 计算MACD
                    macd_data = self._calculate_macd(closes)
                    results["MACD"] = macd_data["macd"][-count:]
                    results["MACD_SIGNAL"] = macd_data["signal"][-count:]
                    results["MACD_HIST"] = macd_data["hist"][-count:]

            return results

        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"计算技术指标失败: {str(e)}",
                details=f"symbol: {symbol}, indicators: {indicators}",
            )

    def get_auction_data(
        self, symbol: str, trade_date: Optional[date] = None, auction_type: str = "open"
    ) -> Dict[str, Any]:
        """
        获取竞价数据

        Args:
            symbol: 股票代码
            trade_date: 交易日期
            auction_type: 竞价类型 (open开盘竞价/close收盘竞价)

        Returns:
            竞价数据

        Raises:
            DataSourceQueryError: 查询失败
            DataSourceDataNotFound: 数据不存在
        """
        try:
            if trade_date is None:
                trade_date = date.today()

            # 确定竞价时间范围
            if auction_type == "open":
                # 开盘竞价: 9:15-9:25
                start_time = datetime.combine(trade_date, datetime.min.time().replace(hour=9, minute=15))
                end_time = datetime.combine(trade_date, datetime.min.time().replace(hour=9, minute=25))
            else:
                # 收盘竞价: 14:57-15:00
                start_time = datetime.combine(trade_date, datetime.min.time().replace(hour=14, minute=57))
                end_time = datetime.combine(trade_date, datetime.min.time().replace(hour=15, minute=0))

            table_name = self._get_table_name("market_snapshot", symbol)

            df = self.td_access.query_by_time_range(table_name=table_name, start_time=start_time, end_time=end_time)

            if df.empty:
                raise DataSourceDataNotFound(
                    source_name="tdengine",
                    data_identifier=f"auction:{symbol}:{trade_date}:{auction_type}",
                )

            # 返回最后一个快照（竞价结果）
            row = df.iloc[-1]

            return {
                "symbol": symbol,
                "trade_date": trade_date.isoformat(),
                "auction_type": auction_type,
                "price": float(row["price"]),
                "volume": int(row.get("bid1_volume", 0) + row.get("ask1_volume", 0)),
                "bid_volumes": [int(row.get(f"bid{i}_volume", 0)) for i in range(1, 6)],
                "ask_volumes": [int(row.get(f"ask{i}_volume", 0)) for i in range(1, 6)],
                "timestamp": row["ts"].isoformat() if isinstance(row["ts"], datetime) else str(row["ts"]),
            }

        except DataSourceDataNotFound:
            raise
        except Exception as e:
            raise DataSourceQueryError(
                source_name="tdengine",
                query=f"获取竞价数据失败: {str(e)}",
                details=f"symbol: {symbol}",
            )

