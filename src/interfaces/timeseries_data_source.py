"""
时序数据源抽象接口

本模块定义时序数据源的统一接口，所有时序数据源（Mock、TDengine、API等）必须实现此接口。
时序数据主要包括：实时行情、K线数据、分时图、资金流向等高频时序数据。

适用数据库: TDengine (时序数据库)
适用场景: 市场行情、实时数据、技术分析

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import pandas as pd


class ITimeSeriesDataSource(ABC):
    """
    时序数据源抽象接口

    所有时序数据源实现必须遵循此接口规范，确保：
    1. 方法签名一致
    2. 返回数据格式统一
    3. 异常处理规范
    4. 性能要求达标

    实现类:
    - MockTimeSeriesDataSource: Mock数据实现（开发测试）
    - TDengineTimeSeriesDataSource: TDengine数据库实现（生产）
    - APITimeSeriesDataSource: 第三方API实现（备选）
    """

    # ==================== 实时行情相关 ====================

    @abstractmethod
    def get_realtime_quotes(
        self, symbols: Optional[List[str]] = None, fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取实时行情数据

        Args:
            symbols: 股票代码列表，None表示获取全市场
            fields: 需要返回的字段列表，None表示返回所有字段
                   可选字段: symbol, name, price, change, change_percent,
                            volume, amount, high, low, open, pre_close,
                            bid1_price, bid1_volume, ask1_price, ask1_volume

        Returns:
            List[Dict]: 实时行情数据列表

        示例返回格式:
            [
                {
                    "symbol": "600000",
                    "name": "浦发银行",
                    "price": 10.5,
                    "change": 0.3,
                    "change_percent": 2.94,
                    "volume": 125000000,
                    "amount": 1312500000.0,
                    "high": 10.8,
                    "low": 10.2,
                    "open": 10.3,
                    "pre_close": 10.2,
                    "timestamp": "2025-11-21 14:30:00"
                },
                ...
            ]

        性能要求:
            - 单股票查询: < 50ms
            - 批量查询(10个): < 100ms
            - 全市场查询: < 500ms

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    @abstractmethod
    def get_kline_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        获取K线数据

        Args:
            symbol: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            interval: K线周期
                     - 分钟级: "1m", "5m", "15m", "30m", "60m"
                     - 日线级: "1d"
                     - 周月级: "1w", "1M"

        Returns:
            DataFrame: K线数据，包含以下列
                      - timestamp: 时间戳
                      - open: 开盘价
                      - high: 最高价
                      - low: 最低价
                      - close: 收盘价
                      - volume: 成交量
                      - amount: 成交额

        示例返回:
            timestamp           open    high    low     close   volume      amount
            2025-11-21 09:30   10.2    10.5    10.1    10.3    1250000     12800000
            2025-11-21 09:31   10.3    10.4    10.2    10.4    1180000     12200000
            ...

        性能要求:
            - 日线数据(250天): < 200ms
            - 分钟数据(1天): < 300ms
            - 分钟数据(5天): < 500ms

        Raises:
            DataSourceException: 数据源查询失败
            ValueError: interval参数无效
        """
        pass

    @abstractmethod
    def get_intraday_chart(self, symbol: str, trade_date: Optional[date] = None) -> pd.DataFrame:
        """
        获取分时图数据

        Args:
            symbol: 股票代码
            trade_date: 交易日期，None表示今天

        Returns:
            DataFrame: 分时数据，包含以下列
                      - time: 时间 (HH:MM格式)
                      - price: 当前价格
                      - avg_price: 均价
                      - volume: 累计成交量
                      - amount: 累计成交额

        示例返回:
            time    price   avg_price   volume      amount
            09:30   10.2    10.2        125000      1275000
            09:31   10.3    10.25       250000      2562500
            ...

        性能要求: < 150ms

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    # ==================== 资金流向相关 ====================

    @abstractmethod
    def get_fund_flow(self, symbol: str, start_date: date, end_date: date, flow_type: str = "main") -> pd.DataFrame:
        """
        获取资金流向数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            flow_type: 资金类型
                      - "main": 主力资金
                      - "super": 超大单
                      - "large": 大单
                      - "medium": 中单
                      - "small": 小单
                      - "all": 所有类型

        Returns:
            DataFrame: 资金流向数据，包含以下列
                      - trade_date: 交易日期
                      - main_net_inflow: 主力净流入
                      - main_net_inflow_rate: 主力净流入率(%)
                      - super_net_inflow: 超大单净流入
                      - large_net_inflow: 大单净流入
                      - medium_net_inflow: 中单净流入
                      - small_net_inflow: 小单净流入

        示例返回:
            trade_date  main_net_inflow  main_net_inflow_rate  super_net_inflow
            2025-11-20  125000000.0      8.5                   200000000.0
            2025-11-21  -35000000.0      -2.3                  -50000000.0
            ...

        性能要求:
            - 30天数据: < 200ms
            - 90天数据: < 400ms

        Raises:
            DataSourceException: 数据源查询失败
            ValueError: flow_type参数无效
        """
        pass

    @abstractmethod
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
            trade_date: 交易日期，None表示最新交易日
            flow_type: 资金类型 (main/super/large/medium/small)
            direction: 方向
                      - "inflow": 净流入排名
                      - "outflow": 净流出排名
            limit: 返回数量限制

        Returns:
            List[Dict]: 资金流向排名列表

        示例返回:
            [
                {
                    "symbol": "600000",
                    "name": "浦发银行",
                    "trade_date": "2025-11-21",
                    "main_net_inflow": 125000000.0,
                    "main_net_inflow_rate": 8.5,
                    "change_percent": 2.94,
                    "rank": 1
                },
                ...
            ]

        性能要求: < 300ms

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    # ==================== 市场概览相关 ====================

    @abstractmethod
    def get_market_overview(self, trade_date: Optional[date] = None) -> Dict[str, Any]:
        """
        获取市场概览数据

        Args:
            trade_date: 交易日期，None表示最新交易日

        Returns:
            Dict: 市场概览数据

        示例返回:
            {
                "trade_date": "2025-11-21",
                "total_stocks": 5234,
                "up_stocks": 2845,
                "down_stocks": 2103,
                "flat_stocks": 286,
                "limit_up_stocks": 45,
                "limit_down_stocks": 12,
                "total_volume": 523400000000,
                "total_amount": 6234567890000.0,
                "avg_change_percent": 1.23,
                "indices": {
                    "sh000001": {"name": "上证指数", "close": 3250.5, "change": 1.2},
                    "sz399001": {"name": "深证成指", "close": 11234.8, "change": 0.8}
                }
            }

        性能要求: < 200ms

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    @abstractmethod
    def get_index_realtime(self, index_codes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        获取指数实时数据

        Args:
            index_codes: 指数代码列表，None表示获取主要指数
                        常用指数: sh000001(上证), sz399001(深成), sz399006(创业板)

        Returns:
            List[Dict]: 指数实时数据

        示例返回:
            [
                {
                    "code": "sh000001",
                    "name": "上证指数",
                    "close": 3250.5,
                    "change": 38.2,
                    "change_percent": 1.19,
                    "high": 3268.9,
                    "low": 3242.1,
                    "open": 3245.3,
                    "pre_close": 3212.3,
                    "volume": 234500000000,
                    "amount": 2845670000000.0,
                    "timestamp": "2025-11-21 15:00:00"
                },
                ...
            ]

        性能要求: < 100ms

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    # ==================== 技术指标相关 ====================

    @abstractmethod
    def calculate_technical_indicators(
        self, symbol: str, start_date: date, end_date: date, indicators: List[str]
    ) -> pd.DataFrame:
        """
        计算技术指标

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            indicators: 指标列表
                       支持的指标: MA, EMA, MACD, KDJ, RSI, BOLL, VOL,
                                  ATR, OBV, CCI, WR, BIAS等

        Returns:
            DataFrame: 包含技术指标的数据

        示例返回:
            date        close   MA5     MA10    MACD_DIF  MACD_DEA  MACD_MACD
            2025-11-20  10.2    10.1    10.0    0.15      0.12      0.03
            2025-11-21  10.5    10.2    10.1    0.18      0.14      0.04
            ...

        性能要求:
            - 单个指标: < 200ms
            - 5个指标: < 500ms

        Raises:
            DataSourceException: 数据源查询失败
            ValueError: 不支持的指标类型
        """
        pass

    # ==================== 竞价和盘口相关 ====================

    @abstractmethod
    def get_auction_data(
        self,
        trade_date: Optional[date] = None,
        auction_type: str = "open",
        min_amount: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        获取竞价抢筹数据

        Args:
            trade_date: 交易日期，None表示最新交易日
            auction_type: 竞价类型
                         - "open": 集合竞价
                         - "close": 尾盘竞价
            min_amount: 最小金额过滤（元）
            limit: 返回数量限制

        Returns:
            List[Dict]: 竞价数据列表

        示例返回:
            [
                {
                    "symbol": "600000",
                    "name": "浦发银行",
                    "trade_date": "2025-11-21",
                    "auction_type": "open",
                    "auction_price": 10.5,
                    "auction_volume": 1250000,
                    "auction_amount": 13125000.0,
                    "change_percent": 2.94
                },
                ...
            ]

        性能要求: < 250ms

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    # ==================== 数据质量和健康检查 ====================

    @abstractmethod
    def check_data_quality(self, symbol: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        检查时序数据质量

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict: 数据质量报告

        示例返回:
            {
                "symbol": "600000",
                "date_range": {"start": "2025-01-01", "end": "2025-11-21"},
                "total_records": 230,
                "missing_records": 5,
                "completeness_rate": 97.8,
                "data_freshness": "2025-11-21 15:00:00",
                "quality_score": 95.5,
                "issues": [
                    {"date": "2025-10-01", "issue": "missing_data"},
                    {"date": "2025-10-15", "issue": "abnormal_volume"}
                ]
            }

        Raises:
            DataSourceException: 数据源查询失败
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        时序数据源健康检查

        Returns:
            Dict: 健康状态

        示例返回:
            {
                "status": "healthy",  # healthy / degraded / unhealthy
                "data_source_type": "tdengine",
                "response_time_ms": 45,
                "last_update": "2025-11-21 15:00:00",
                "connection_status": "connected",
                "metrics": {
                    "total_queries_today": 12345,
                    "avg_response_time_ms": 52,
                    "error_rate_percent": 0.05
                }
            }

        Raises:
            DataSourceException: 健康检查失败
        """
        pass
