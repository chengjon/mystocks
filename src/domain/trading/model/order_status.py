"""
订单状态枚举
Order Status Enumeration

表示订单的生命周期状态。
"""

from enum import Enum


class OrderStatus(Enum):
    """订单状态枚举"""

    CREATED = "created"
    """订单已创建"""

    SUBMITTED = "submitted"
    """订单已提交"""

    PARTIALLY_FILLED = "partially_filled"
    """部分成交"""

    FILLED = "filled"
    """完全成交"""

    CANCELLED = "cancelled"
    """已取消"""

    REJECTED = "rejected"
    """已拒绝"""

    def is_terminal(self) -> bool:
        """是否为终态（无法再变更）"""
        return self in {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
        }

    def __str__(self) -> str:
        return self.value
