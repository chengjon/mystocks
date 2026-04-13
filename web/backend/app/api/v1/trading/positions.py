"""
持仓管理API

提供交易持仓管理功能
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

from app.api.v1.trading.runtime_state import PositionState, runtime_store
from app.core.responses import UnifiedResponse
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


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


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

POSITION_LIST_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Positions retrieved",
    "data": {
        "positions": [
            {
                "position_id": "pos_demo_001",
                "symbol": "600519",
                "name": "600519",
                "quantity": 100,
                "average_cost": 1800.0,
                "current_price": 1800.0,
                "market_value": 180000.0,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "weight": 1.0,
                "created_at": "2026-04-13T08:00:00+00:00",
                "updated_at": "2026-04-13T08:00:00+00:00",
            }
        ],
        "total_value": 180000.0,
        "total": 1,
    },
}

POSITION_DETAIL_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position retrieved",
    "data": POSITION_LIST_EXAMPLE["data"]["positions"][0],
}

POSITION_CREATE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position created",
    "data": POSITION_DETAIL_EXAMPLE["data"],
}

POSITION_UPDATE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position updated",
    "data": {**POSITION_DETAIL_EXAMPLE["data"], "quantity": 120, "market_value": 216000.0},
}

POSITION_DELETE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Position deleted",
    "data": {"message": "Position pos_demo_001 deleted"},
}

POSITION_LIST_RESPONSES = _success_response_spec("持仓列表结果。", POSITION_LIST_EXAMPLE)
POSITION_DETAIL_RESPONSES = _success_response_spec("持仓详情结果。", POSITION_DETAIL_EXAMPLE)
POSITION_CREATE_RESPONSES = _success_response_spec("持仓创建结果。", POSITION_CREATE_SUCCESS_EXAMPLE)
POSITION_UPDATE_RESPONSES = _success_response_spec("持仓更新结果。", POSITION_UPDATE_SUCCESS_EXAMPLE)
POSITION_DELETE_RESPONSES = _success_response_spec("持仓删除结果。", POSITION_DELETE_SUCCESS_EXAMPLE)


def _resolve_query_value(value: Any) -> Any:
    return getattr(value, "default", value)


def _serialize_position(position: PositionState) -> dict[str, Any]:
    return PositionResponse(
        position_id=position.position_id,
        symbol=position.symbol,
        name=position.name,
        quantity=position.quantity,
        average_cost=position.average_cost,
        current_price=position.current_price,
        market_value=position.market_value,
        unrealized_pnl=position.unrealized_pnl,
        realized_pnl=position.realized_pnl,
        weight=position.weight,
        created_at=position.created_at,
        updated_at=position.updated_at,
    ).model_dump()


@router.get(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="List Positions",
    description="按标的或交易会话筛选当前持仓列表，当前实现读取与交易会话共享的运行时状态。",
    responses=POSITION_LIST_RESPONSES,
)
async def list_positions(
    symbol: Optional[str] = Query(None, description="可选的标的代码过滤条件。"),
    session_id: Optional[str] = Query(None, description="可选的交易会话ID过滤条件。"),
):
    positions = runtime_store.list_positions(
        symbol=_resolve_query_value(symbol), session_id=_resolve_query_value(session_id)
    )
    total_value = round(sum(item.market_value for item in positions), 4)
    return UnifiedResponse(
        success=True,
        code=200,
        message="Positions retrieved",
        data={
            "positions": [_serialize_position(item) for item in positions],
            "total_value": total_value,
            "total": len(positions),
        },
    )


@router.get(
    "/{position_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Position",
    description="根据持仓ID获取单个持仓详情，当前实现读取共享运行时中的真实持仓数据。",
    responses=POSITION_DETAIL_RESPONSES,
)
async def get_position(position_id: str = Path(..., description="需要查询详情的持仓ID。")):
    position = runtime_store.get_position(position_id)
    if position is None:
        return UnifiedResponse(success=False, code=404, message="Position not found", data={"position_id": position_id})
    return UnifiedResponse(success=True, code=200, message="Position retrieved", data=_serialize_position(position))


@router.post(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Create Position",
    description="创建新的持仓记录，当前实现会把持仓写入当前活动交易会话。",
    responses=POSITION_CREATE_RESPONSES,
)
async def create_position(request: PositionCreate = Body(..., openapi_examples=POSITION_CREATE_EXAMPLES)):
    try:
        position = runtime_store.create_position(symbol=request.symbol, quantity=request.quantity, price=request.price)
    except ValueError as exc:
        return UnifiedResponse(success=False, code=404, message=str(exc), data={"symbol": request.symbol})
    return UnifiedResponse(success=True, code=200, message="Position created", data=_serialize_position(position))


@router.patch(
    "/{position_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Update Position",
    description="更新指定持仓的数量或风控参数，当前实现会回写共享运行时状态。",
    responses=POSITION_UPDATE_RESPONSES,
)
async def update_position(
    position_id: str = Path(..., description="需要更新的持仓ID。"),
    request: PositionUpdate = Body(..., openapi_examples=POSITION_UPDATE_EXAMPLES),
):
    position = runtime_store.update_position(
        position_id,
        quantity=request.quantity,
        stop_loss=request.stop_loss,
        take_profit=request.take_profit,
    )
    if position is None:
        return UnifiedResponse(success=False, code=404, message="Position not found", data={"position_id": position_id})
    return UnifiedResponse(success=True, code=200, message="Position updated", data=_serialize_position(position))


@router.delete(
    "/{position_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Delete Position",
    description="删除或关闭指定持仓，当前实现会同步释放对应会话的占用资金。",
    responses=POSITION_DELETE_RESPONSES,
)
async def delete_position(position_id: str = Path(..., description="需要删除或关闭的持仓ID。")):
    deleted = runtime_store.delete_position(position_id)
    if not deleted:
        return UnifiedResponse(success=False, code=404, message="Position not found", data={"position_id": position_id})
    return UnifiedResponse(
        success=True,
        code=200,
        message="Position deleted",
        data=PositionDeleteResponse(message=f"Position {position_id} deleted").model_dump(),
    )
