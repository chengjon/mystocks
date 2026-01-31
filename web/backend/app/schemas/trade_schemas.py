"""
交易执行API Schemas (Pydantic模型)

用于FastAPI请求验证和响应序列化:
- OrderRequest: 下单请求
- OrderResponse: 委托响应
- Position: 持仓信息
- Account: 账户信息
- TradeHistory: 交易历史
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# ==================== Order Request ====================


class OrderRequest(BaseModel):
    """下单请求"""

    symbol: str = Field(
        ..., description="股票代码", examples=["000001.SZ", "600519.SH"], pattern=r"^[0-9]{6}\.[A-Z]{2}$"
    )
    direction: str = Field(..., description="交易方向", pattern=r"^(buy|sell)$")
    order_type: str = Field(
        default="limit", description="订单类型 (limit=限价, market=市价)", pattern=r"^(limit|market)$"
    )
    price: Optional[Decimal] = Field(None, ge=0.01, description="委托价格 (限价单必填)", examples=[10.50])
    quantity: int = Field(..., gt=0, description="委托数量 (100的整数倍)", examples=[100, 200, 500])

    @field_validator("price")
    @classmethod
    def validate_price(cls, v, values):
        """验证价格字段"""
        if values.get("order_type") == "limit" and v is None:
            raise ValueError("限价单必须指定价格")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        """验证数量 (A股必须是100的整数倍)"""
        if v % 100 != 0:
            raise ValueError("委托数量必须是100的整数倍")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "000001.SZ",
                "direction": "buy",
                "order_type": "limit",
                "price": 10.50,
                "quantity": 100,
            }
        }


# ==================== Order Response ====================


class OrderResponse(BaseModel):
    """委托响应"""

    order_id: str = Field(description="委托ID")
    symbol: str = Field(description="股票代码")
    direction: str = Field(description="交易方向 (buy/sell)")
    order_type: str = Field(description="订单类型 (limit/market)")
    price: Optional[Decimal] = Field(None, description="委托价格")
    quantity: int = Field(description="委托数量")
    filled_quantity: int = Field(default=0, description="成交数量")
    average_price: Optional[Decimal] = Field(None, description="成交均价")
    status: str = Field(
        description="委托状态 (pending=待成交, partial=部分成交, filled=完全成交, cancelled=已撤销, rejected=已拒绝)"
    )
    commission: Optional[Decimal] = Field(None, description="手续费")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORDER_20251229123456",
                "symbol": "000001.SZ",
                "direction": "buy",
                "order_type": "limit",
                "price": Decimal("10.50"),
                "quantity": 100,
                "filled_quantity": 100,
                "average_price": Decimal("10.52"),
                "status": "filled",
                "commission": Decimal("0.52"),
                "created_at": "2025-12-29T15:30:00",
            }
        }


# ==================== Position ====================


class Position(BaseModel):
    """持仓信息"""

    symbol: str = Field(description="股票代码")
    symbol_name: Optional[str] = Field(None, description="股票名称")
    quantity: int = Field(description="持仓数量")
    available_quantity: int = Field(description="可用数量")
    cost_price: Decimal = Field(description="成本价")
    current_price: Optional[Decimal] = Field(None, description="当前价")
    market_value: Decimal = Field(description="市值")
    profit_loss: Decimal = Field(description="浮动盈亏")
    profit_loss_percent: float = Field(description="盈亏比例(%)")
    last_update: datetime = Field(description="最后更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "000001.SZ",
                "symbol_name": "平安银行",
                "quantity": 1000,
                "available_quantity": 1000,
                "cost_price": Decimal("10.00"),
                "current_price": Decimal("10.50"),
                "market_value": Decimal("10500.00"),
                "profit_loss": Decimal("500.00"),
                "profit_loss_percent": 5.0,
                "last_update": "2025-12-29T15:30:00",
            }
        }


class PositionsResponse(BaseModel):
    """持仓列表响应"""

    positions: List[Position] = Field(description="持仓列表")
    total_count: int = Field(description="持仓数量")
    total_market_value: Decimal = Field(description="总市值")
    total_profit_loss: Decimal = Field(description="总浮动盈亏")
    total_profit_loss_percent: float = Field(description="总盈亏比例(%)")


# ==================== Account ====================


class AccountInfo(BaseModel):
    """账户信息"""

    account_id: str = Field(description="账户ID")
    account_type: str = Field(description="账户类型 (stock/derivatives)")
    total_assets: Decimal = Field(description="总资产")
    cash: Decimal = Field(description="可用资金")
    market_value: Decimal = Field(description="证券市值")
    frozen_cash: Optional[Decimal] = Field(None, description="冻结资金")
    total_profit_loss: Decimal = Field(description="总盈亏")
    profit_loss_percent: float = Field(description="盈亏比例(%)")
    risk_level: str = Field(default="low", description="风险等级 (low/medium/high)")
    last_update: datetime = Field(description="最后更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "ACC_123456",
                "account_type": "stock",
                "total_assets": Decimal("100000.00"),
                "cash": Decimal("50000.00"),
                "market_value": Decimal("50000.00"),
                "frozen_cash": None,
                "total_profit_loss": Decimal("5000.00"),
                "profit_loss_percent": 5.0,
                "risk_level": "low",
                "last_update": "2025-12-29T15:30:00",
            }
        }


# ==================== Trade History ====================


class TradeHistoryItem(BaseModel):
    """成交记录"""

    trade_id: str = Field(description="成交ID")
    order_id: str = Field(description="委托ID")
    symbol: str = Field(description="股票代码")
    direction: str = Field(description="交易方向 (buy/sell)")
    price: Decimal = Field(description="成交价格")
    quantity: int = Field(description="成交数量")
    amount: Decimal = Field(description="成交金额")
    commission: Decimal = Field(description="手续费")
    trade_time: datetime = Field(description="成交时间")
    trade_type: str = Field(description="成交类型 (normal/issue/transfer)")


class TradeHistoryRequest(BaseModel):
    """交易历史查询请求"""

    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    symbol: Optional[str] = Field(None, description="股票代码 (可选)")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class TradeHistoryResponse(BaseModel):
    """交易历史响应"""

    trades: List[TradeHistoryItem] = Field(description="成交记录列表")
    total_count: int = Field(description="总记录数")
    total_amount: Decimal = Field(description="总成交金额")
    total_commission: Decimal = Field(description="总手续费")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")


# ==================== Order Cancellation ====================


class CancelOrderRequest(BaseModel):
    """撤单请求"""

    order_id: str = Field(..., description="委托ID")

    class Config:
        json_schema_extra = {"example": {"order_id": "ORDER_20251229123456"}}


class CancelOrderResponse(BaseModel):
    """撤单响应"""

    order_id: str = Field(description="委托ID")
    success: bool = Field(description="是否成功")
    message: str = Field(description="提示信息")
    cancelled_quantity: int = Field(description="撤单数量")
    remaining_quantity: int = Field(description="剩余数量")
    cancelled_at: datetime = Field(default_factory=datetime.now, description="撤单时间")
