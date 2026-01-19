"""
Trading Application DTOs
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CreateOrderRequest(BaseModel):
    """创建订单请求"""

    symbol: str = Field(..., min_length=6, max_length=10, description="股票代码")
    quantity: int = Field(..., gt=0, description="数量")
    side: str = Field(..., pattern="^(BUY|SELL)$", description="方向: BUY/SELL")
    order_type: str = Field(..., pattern="^(MARKET|LIMIT)$", description="类型: MARKET/LIMIT")
    price: Optional[float] = Field(None, gt=0, description="价格 (限价单必填)")
    strategy_id: Optional[str] = None


class OrderResponse(BaseModel):
    """订单响应"""

    order_id: str
    symbol: str
    quantity: int
    filled_quantity: int
    status: str
    side: str
    price: Optional[float]
    average_fill_price: float
    created_at: datetime


class PositionResponse(BaseModel):
    """持仓响应"""

    symbol: str
    quantity: int
    average_cost: float
    current_price: float
    unrealized_pnl: float
    market_value: float
