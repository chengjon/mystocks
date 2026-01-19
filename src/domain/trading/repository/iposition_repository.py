"""
Position Repository Interface
持仓仓储接口

定义持仓持久化的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..model.position import Position


class IPositionRepository(ABC):
    """
    持仓仓储接口

    职责：
    - 定义持仓持久化的抽象接口
    - 提供持仓查询方法
    - 支持按投资组合、标的查询

    实现方式：
    - PostgreSQL实现（Infrastructure层）
    """

    @abstractmethod
    def save(self, position: Position) -> None:
        """
        保存持仓

        Args:
            position: 持仓聚合根
        """
        pass

    @abstractmethod
    def find_by_id(self, position_id: str) -> Optional[Position]:
        """
        根据ID查找持仓

        Args:
            position_id: 持仓ID

        Returns:
            持仓聚合根，如果不存在返回None
        """
        pass

    @abstractmethod
    def find_by_portfolio(self, portfolio_id: str) -> List[Position]:
        """
        查找投资组合的所有持仓

        Args:
            portfolio_id: 投资组合ID

        Returns:
            持仓列表
        """
        pass

    @abstractmethod
    def find_by_portfolio_and_symbol(self, portfolio_id: str, symbol: str) -> Optional[Position]:
        """
        查找投资组合中特定标的的持仓

        Args:
            portfolio_id: 投资组合ID
            symbol: 标的代码

        Returns:
            持仓聚合根，如果不存在返回None
        """
        pass

    @abstractmethod
    def find_open_positions(self, portfolio_id: str) -> List[Position]:
        """
        查找投资组合的所有开仓持仓（数量不为零）

        Args:
            portfolio_id: 投资组合ID

        Returns:
            开仓持仓列表
        """
        pass

    @abstractmethod
    def find_by_symbol(self, symbol: str) -> List[Position]:
        """
        查找特定标的的所有持仓

        Args:
            symbol: 标的代码

        Returns:
            持仓列表
        """
        pass

    @abstractmethod
    def delete(self, position_id: str) -> None:
        """
        删除持仓

        Args:
            position_id: 持仓ID
        """
        pass

    @abstractmethod
    def exists(self, position_id: str) -> bool:
        """
        检查持仓是否存在

        Args:
            position_id: 持仓ID

        Returns:
            如果存在返回True，否则返回False
        """
        pass

    @abstractmethod
    def count_by_portfolio(self, portfolio_id: str) -> int:
        """
        统计投资组合的持仓数量

        Args:
            portfolio_id: 投资组合ID

        Returns:
            持仓数量
        """
        pass
