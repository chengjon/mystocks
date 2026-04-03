"""
持仓管理API

提供交易持仓管理功能
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES

POSITION_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/positions",
    tags=["Positions"],
    responses=POSITION_ROUTE_RESPONSES,
)


class PositionResponse(BaseModel):
    """持仓响应"""

    position_id: str = Field(..., description="持仓ID。")
    symbol: str = Field(..., description="股票或交易标的代码。")
    name: str = Field(..., description="持仓名称或标的简称。")
    quantity: int = Field(..., description="当前持仓数量。")
    average_cost: float = Field(..., description="持仓平均成本价。")
    current_price: float = Field(..., description="当前市场价格。")
    market_value: float = Field(..., description="当前持仓市值。")
    unrealized_pnl: float = Field(..., description="当前未实现盈亏。")
    realized_pnl: float = Field(..., description="当前已实现盈亏。")
    weight: float = Field(..., description="该持仓占组合总资产的权重。")
    created_at: datetime = Field(..., description="持仓创建时间。")
    updated_at: datetime = Field(..., description="持仓最近更新时间。")


class PositionListResponse(BaseModel):
    """持仓列表响应"""

    positions: list[PositionResponse] = Field(..., description="符合筛选条件的持仓列表。")
    total_value: float = Field(..., description="当前返回持仓的总市值。")
    total: int = Field(..., description="当前返回持仓数量。")


class PositionCreate(BaseModel):
    """创建持仓请求"""

    symbol: str = Field(..., description="股票或交易标的代码。")
    quantity: int = Field(..., description="建仓数量。")
    price: float = Field(..., description="建仓价格。")


class PositionUpdate(BaseModel):
    """更新持仓请求"""

    quantity: Optional[int] = Field(None, description="更新后的持仓数量。")
    stop_loss: Optional[float] = Field(None, description="新的止损价格。")
    take_profit: Optional[float] = Field(None, description="新的止盈价格。")


class PositionDeleteResponse(BaseModel):
    """删除持仓响应"""

    message: str = Field(..., description="删除或平仓操作的结果说明。")


POSITION_CREATE_EXAMPLES = {
    "create_equity_position": {
        "summary": "创建持仓",
        "description": "在组合中新增一个股票持仓，记录数量和建仓价格。",
        "value": {
            "symbol": "600519",
            "quantity": 100,
            "price": 1800.0,
        },
    }
}

POSITION_UPDATE_EXAMPLES = {
    "adjust_position_risk_controls": {
        "summary": "更新持仓参数",
        "description": "调整持仓数量，并同时更新止损和止盈价格。",
        "value": {
            "quantity": 120,
            "stop_loss": 1720.0,
            "take_profit": 1950.0,
        },
    }
}


@router.get(
    "",
    response_model=PositionListResponse,
    summary="List Positions",
    description="按标的或交易会话筛选当前持仓列表，并返回总市值汇总。",
)
async def list_positions(
    symbol: Optional[str] = Query(None, description="可选的标的代码过滤条件。"),
    session_id: Optional[str] = Query(None, description="可选的交易会话ID过滤条件。"),
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


@router.get(
    "/{position_id}",
    response_model=PositionResponse,
    summary="Get Position",
    description="根据持仓ID获取单个持仓的成本、价格、市值和盈亏详情。",
)
async def get_position(position_id: str = Path(..., description="需要查询详情的持仓ID。")):
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


@router.post(
    "",
    response_model=PositionResponse,
    summary="Create Position",
    description="创建新的持仓记录，并根据建仓价格和数量初始化市值。",
)
async def create_position(request: PositionCreate = Body(..., openapi_examples=POSITION_CREATE_EXAMPLES)):
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


@router.patch(
    "/{position_id}",
    response_model=PositionResponse,
    summary="Update Position",
    description="更新指定持仓的数量或风控参数，例如止损价和止盈价。",
)
async def update_position(
    position_id: str = Path(..., description="需要更新的持仓ID。"),
    request: PositionUpdate = Body(..., openapi_examples=POSITION_UPDATE_EXAMPLES),
):
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


@router.delete(
    "/{position_id}",
    response_model=PositionDeleteResponse,
    summary="Delete Position",
    description="删除或关闭指定持仓，并返回本次持仓处理结果。",
)
async def delete_position(position_id: str = Path(..., description="需要删除或关闭的持仓ID。")):
    """
    删除持仓

    Closes and removes a position.
    """
    return {"message": f"Position {position_id} deleted successfully"}
