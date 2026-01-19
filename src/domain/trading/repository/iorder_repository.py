"""
Order Repository Interface
订单仓储接口

定义订单持久化的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..model.order import Order
from ..value_objects.order_side import OrderSide
from ..model.order_status import OrderStatus


class IOrderRepository(ABC):
    """
    订单仓储接口

    职责：
    - 定义订单持久化的抽象接口
    - 提供订单查询方法
    - 支持按状态、标的、投资组合查询

    实现方式：
    - PostgreSQL实现（Infrastructure层）
    """

    @abstractmethod
    def save(self, order: Order) -> None:
        """
        保存订单

        Args:
            order: 订单聚合根
        """
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """
        根据ID查找订单

        Args:
            order_id: 订单ID

        Returns:
            订单聚合根，如果不存在返回None
        """
        pass

    @abstractmethod
    def find_by_portfolio(self, portfolio_id: str, limit: int = 100) -> List[Order]:
        """
        查找投资组合的所有订单

        Args:
            portfolio_id: 投资组合ID
            limit: 返回数量限制

        Returns:
            订单列表
        """
        pass

    @abstractmethod
    def find_by_symbol(self, symbol: str, limit: int = 100) -> List[Order]:
        """
        查找标的的所有订单

        Args:
            symbol: 标的代码
            limit: 返回数量限制

        Returns:
            订单列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: OrderStatus, limit: int = 100) -> List[Order]:
        """
        查找特定状态的订单

        Args:
            status: 订单状态
            limit: 返回数量限制

        Returns:
            订单列表
        """
        pass

    @abstractmethod
    def find_pending_orders(self) -> List[Order]:
        """
        查找所有待处理订单

        Returns:
            待处理订单列表（SUBMITTED, PARTIALLY_FILLED）
        """
        pass

    @abstractmethod
    def find_recent_orders(self, hours: int = 24, limit: int = 100) -> List[Order]:
        """
        查找最近的订单

        Args:
            hours: 时间范围（小时）
            limit: 返回数量限制

        Returns:
            订单列表
        """
        pass

    @abstractmethod
    def delete(self, order_id: str) -> None:
        """
        删除订单

        Args:
            order_id: 订单ID
        """
        pass

    @abstractmethod
    def exists(self, order_id: str) -> bool:
        """
        检查订单是否存在

        Args:
            order_id: 订单ID

        Returns:
            如果存在返回True，否则返回False
        """
        pass

    @abstractmethod
    def count_by_status(self, status: OrderStatus) -> int:
        """
        统计特定状态的订单数量

        Args:
            status: 订单状态

        Returns:
            订单数量
        """
        pass
