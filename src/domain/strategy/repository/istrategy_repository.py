"""
Strategy Repository Interface
策略仓储接口

定义策略持久化的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..model.strategy import Strategy
from ..value_objects.strategy_id import StrategyId


class IStrategyRepository(ABC):
    """
    策略仓储接口

    职责：
    - 定义策略持久化的抽象接口
    - 隔离具体实现（PostgreSQL, MongoDB, etc.）
    - 提供CRUD操作

    实现方式：
    - PostgreSQL实现（Infrastructure层）
    - MongoDB实现（Infrastructure层，可选）
    """

    @abstractmethod
    def save(self, strategy: Strategy) -> None:
        """
        保存策略

        Args:
            strategy: 策略聚合根
        """
        pass

    @abstractmethod
    def find_by_id(self, strategy_id: StrategyId) -> Optional[Strategy]:
        """
        根据ID查找策略

        Args:
            strategy_id: 策略ID

        Returns:
            策略聚合根，如果不存在返回None
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Strategy]:
        """
        根据名称查找策略

        Args:
            name: 策略名称

        Returns:
            策略聚合根，如果不存在返回None
        """
        pass

    @abstractmethod
    def find_all_active(self) -> List[Strategy]:
        """
        查找所有激活的策略

        Returns:
            激活的策略列表
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Strategy]:
        """
        查找所有策略

        Returns:
            所有策略列表
        """
        pass

    @abstractmethod
    def delete(self, strategy_id: StrategyId) -> None:
        """
        删除策略

        Args:
            strategy_id: 策略ID
        """
        pass

    @abstractmethod
    def exists(self, strategy_id: StrategyId) -> bool:
        """
        检查策略是否存在

        Args:
            strategy_id: 策略ID

        Returns:
            如果存在返回True，否则返回False
        """
        pass

    @abstractmethod
    def count_active(self) -> int:
        """
        统计激活的策略数量

        Returns:
            激活的策略数量
        """
        pass
