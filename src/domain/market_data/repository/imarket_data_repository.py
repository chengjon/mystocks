"""
Market Data Repository Interface
市场数据仓储接口

定义市场数据持久化和查询的抽象接口。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..value_objects.bar import Bar
from ..value_objects.quote import Quote
from ..value_objects.tick import Tick


class IMarketDataRepository(ABC):
    """
    市场数据仓储接口

    职责：
    - 定义市场数据查询的抽象接口
    - 提供K线、分笔、报价查询方法
    - 支持按标的、时间范围查询

    实现方式：
    - TDengine实现（高频时序数据：tick, minute数据）
    - PostgreSQL实现（日线数据、参考数据）
    """

    # ========== K线数据查询 ==========

    @abstractmethod
    def get_bars(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        period: str = "daily",
    ) -> List[Bar]:
        """
        获取K线数据

        Args:
            symbol: 标的代码
            start_time: 开始时间
            end_time: 结束时间
            period: 时间周期（1min, 5min, 15min, 30min, 60min, daily, weekly, monthly）

        Returns:
            K线数据列表，按时间升序排列
        """

    @abstractmethod
    def get_latest_bar(
        self,
        symbol: str,
        period: str = "daily",
    ) -> Optional[Bar]:
        """
        获取最新K线数据

        Args:
            symbol: 标的代码
            period: 时间周期

        Returns:
            最新K线数据，如果不存在返回None
        """

    @abstractmethod
    def save_bars(self, bars: List[Bar]) -> None:
        """
        保存K线数据

        Args:
            bars: K线数据列表
        """

    # ========== 分笔数据查询 ==========

    @abstractmethod
    def get_ticks(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[Tick]:
        """
        获取分笔数据

        Args:
            symbol: 标的代码
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制

        Returns:
            分笔数据列表，按时间升序排列
        """

    @abstractmethod
    def save_ticks(self, ticks: List[Tick]) -> None:
        """
        保存分笔数据

        Args:
            ticks: 分笔数据列表
        """

    # ========== 实时报价查询 ==========

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """
        获取实时报价

        Args:
            symbol: 标的代码

        Returns:
            实时报价，如果不存在返回None
        """

    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> List[Quote]:
        """
        批量获取实时报价

        Args:
            symbols: 标的代码列表

        Returns:
            实时报价列表
        """

    @abstractmethod
    def save_quote(self, quote: Quote) -> None:
        """
        保存实时报价

        Args:
            quote: 实时报价
        """

    # ========== 数据可用性检查 ==========

    @abstractmethod
    def has_bars(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        period: str = "daily",
    ) -> bool:
        """
        检查是否有K线数据

        Args:
            symbol: 标的代码
            start_time: 开始时间
            end_time: 结束时间
            period: 时间周期

        Returns:
            如果有数据返回True，否则返回False
        """

    @abstractmethod
    def has_ticks(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        """
        检查是否有分笔数据

        Args:
            symbol: 标的代码
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            如果有数据返回True，否则返回False
        """
