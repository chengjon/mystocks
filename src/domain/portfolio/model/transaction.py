"""
Transaction Entity
交易流水实体

记录投资组合中的所有交易流水。
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from src.domain.trading.value_objects import OrderSide

@dataclass
class Transaction:
    """
    交易流水实体

    职责：
    - 记录交易详情
    - 计算交易金额
    - 支持交易类型识别

    不变量：
    - 数量必须为正数
    - 价格必须为正数
    - 交易金额 = 价格 × 数量
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    portfolio_id: str = ""
    symbol: str = ""
    side: OrderSide = OrderSide.BUY  # 使用 OrderSide 枚举
    quantity: int = 0
    price: float = 0.0
    commission: float = 0.0  # 手续费
    total_amount: float = 0.0 # 总金额
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, portfolio_id: str, symbol: str, side: OrderSide, 
               quantity: int, price: float, commission: float) -> 'Transaction':
        
        amount = quantity * price
        total = amount + commission if side == OrderSide.BUY else amount - commission
        
        return cls(
            id=str(uuid4()),
            portfolio_id=portfolio_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            commission=commission,
            total_amount=total,
            timestamp=datetime.now()
        )

    def __post_init__(self):
        """验证交易"""
        if self.quantity < 0:
            raise ValueError(f"Quantity cannot be negative: {self.quantity}")

        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")

        if self.commission < 0:
            raise ValueError(f"Commission cannot be negative: {self.commission}")