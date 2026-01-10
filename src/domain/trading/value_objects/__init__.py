from .order_side import OrderSide
# ... 其他导出 ...
from enum import Enum, unique
from dataclasses import dataclass
from typing import Optional

@unique
class OrderType(str, Enum):
    """订单类型"""
    MARKET = "MARKET"  # 市价单
    LIMIT = "LIMIT"    # 限价单
    STOP = "STOP"      # 止损单

@unique
class OrderStatus(str, Enum):
    """订单状态机"""
    CREATED = "CREATED"             # 已创建，未提交
    SUBMITTED = "SUBMITTED"         # 已提交到交易所/柜台
    PARTIALLY_FILLED = "PARTIALLY_FILLED" # 部分成交
    FILLED = "FILLED"               # 全部成交
    CANCELLED = "CANCELLED"         # 已撤单
    REJECTED = "REJECTED"           # 被拒绝
    EXPIRED = "EXPIRED"             # 已过期

@unique
class TimeInForce(str, Enum):
    """订单有效期"""
    DAY = "DAY"  # 当日有效
    GTC = "GTC"  # 撤销前有效 (Good Till Cancelled)
    IOC = "IOC"  # 立即成交或取消 (Immediate Or Cancel)

@dataclass(frozen=True)
class OrderId:
    """订单ID值对象"""
    value: str

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class PositionId:
    """持仓ID值对象"""
    value: str

    def __str__(self):
        return self.value