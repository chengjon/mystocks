"""
持仓管理API

提供交易持仓管理功能
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/positions",
    tags=["Positions"],
)


class PositionResponse(BaseModel):
    """持仓响应"""

    position_id: str
    symbol: str
    name: str
    quantity: int
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    weight: float
    created_at: datetime
    updated_at: datetime


class PositionCreate(BaseModel):
    """创建持仓请求"""

    symbol: str = Field(..., description="Stock symbol")
    quantity: int = Field(..., description="Position quantity")
    price: float = Field(..., description="Entry price")


class PositionUpdate(BaseModel):
    """更新持仓请求"""

    quantity: Optional[int] = Field(None, description="New quantity")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")


@router.get("", response_model=Dict[str, Any], summary="List Positions")
async def list_positions(
    symbol: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """
    获取持仓列表

    Returns list of current positions.
    """
    mock_positions = [
        {
            "position_id": "pos_001",
            "symbol": "600519",
            "name": "贵州茅台",
            "quantity": 100,
            "average_cost": 1800.0,
            "current_price": 1850.0,
            "market_value": 185000.0,
            "unrealized_pnl": 5000.0,
            "realized_pnl": 0.0,
            "weight": 0.35,
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-20T15:00:00Z",
        },
        {
            "position_id": "pos_002",
            "symbol": "000001",
            "name": "平安银行",
            "quantity": 500,
            "average_cost": 12.5,
            "current_price": 12.8,
            "market_value": 6400.0,
            "unrealized_pnl": 150.0,
            "realized_pnl": 0.0,
            "weight": 0.12,
            "created_at": "2025-01-16T14:00:00Z",
            "updated_at": "2025-01-20T15:00:00Z",
        },
    ]

    if symbol:
        mock_positions = [p for p in mock_positions if p["symbol"] == symbol]
    if session_id:
        mock_positions = [p for p in mock_positions if p.get("session_id") == session_id]

    total_value = sum(p["market_value"] for p in mock_positions)
    for p in mock_positions:
        p["weight"] = p["market_value"] / total_value if total_value > 0 else 0

    return {
        "positions": mock_positions,
        "total_value": total_value,
        "total": len(mock_positions),
    }


@router.get("/{position_id}", response_model=PositionResponse, summary="Get Position")
async def get_position(position_id: str):
    """
    获取单个持仓详情

    Returns details of a specific position.
    """
    return PositionResponse(
        position_id=position_id,
        symbol="600519",
        name="贵州茅台",
        quantity=100,
        average_cost=1800.0,
        current_price=1850.0,
        market_value=185000.0,
        unrealized_pnl=5000.0,
        realized_pnl=0.0,
        weight=0.35,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.post("", response_model=PositionResponse, summary="Create Position")
async def create_position(request: PositionCreate):
    """
    创建新持仓

    Creates a new position.
    """
    position_id = f"pos_{int(datetime.now().timestamp())}"
    market_value = request.quantity * request.price
    return PositionResponse(
        position_id=position_id,
        symbol=request.symbol,
        name=request.symbol,
        quantity=request.quantity,
        average_cost=request.price,
        current_price=request.price,
        market_value=market_value,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        weight=0.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.patch("/{position_id}", response_model=PositionResponse, summary="Update Position")
async def update_position(position_id: str, request: PositionUpdate):
    """
    更新持仓

    Updates position parameters (quantity, stop loss, take profit).
    """
    return PositionResponse(
        position_id=position_id,
        symbol="600519",
        name="贵州茅台",
        quantity=request.quantity or 100,
        average_cost=1800.0,
        current_price=1850.0,
        market_value=185000.0,
        unrealized_pnl=5000.0,
        realized_pnl=0.0,
        weight=0.35,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.delete("/{position_id}", summary="Delete Position")
async def delete_position(position_id: str):
    """
    删除持仓

    Closes and removes a position.
    """
    return {"message": f"Position {position_id} deleted successfully"}
