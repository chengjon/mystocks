"""
Trading Context Repository Interfaces
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..model.order import Order
from ..model.position import Position
from ..value_objects import OrderId, PositionId


class IOrderRepository(ABC):
    """订单仓储接口"""

    @abstractmethod
    def save(self, order: Order) -> None:
        """保存订单"""
        pass

    @abstractmethod
    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """根据ID获取订单"""
        pass

    @abstractmethod
    def get_by_symbol(self, symbol: str) -> List[Order]:
        """获取某标的的所有订单"""
        pass

    @abstractmethod
    def get_active_orders(self) -> List[Order]:
        """获取所有未结订单"""
        pass


class IPositionRepository(ABC):
    """持仓仓储接口"""

    @abstractmethod
    def save(self, position: Position) -> None:
        """保存持仓"""
        pass

    @abstractmethod
    def get_by_symbol(self, symbol: str) -> Optional[Position]:
        """获取某标的持仓"""
        pass

    @abstractmethod
    def get_all(self) -> List[Position]:
        """获取所有持仓"""
        pass
