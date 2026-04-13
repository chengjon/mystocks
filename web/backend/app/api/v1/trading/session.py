"""
交易会话API

提供实时交易会话管理功能
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

from app.api.v1.trading.runtime_state import SessionState, runtime_store
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

TRADING_SESSION_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/trading/sessions",
    tags=["Trading Sessions"],
    responses=TRADING_SESSION_ROUTE_RESPONSES,
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


class TradingSessionCreate(BaseModel):
    """创建交易会话请求"""

    symbol: str = Field(..., description="交易标的代码。")
    strategy_id: Optional[str] = Field(None, description="关联的策略ID。")
    initial_capital: float = Field(100000.0, description="会话初始资金。")
    position_size: float = Field(0.1, description="单次仓位比例，范围为 0 到 1。")
    risk_threshold: float = Field(0.05, description="风险阈值，超过后可触发风控动作。")


class TradingSessionResponse(BaseModel):
    """交易会话响应"""

    session_id: str = Field(..., description="交易会话ID。")
    symbol: str = Field(..., description="交易标的代码。")
    strategy_id: Optional[str] = Field(None, description="关联的策略ID。")
    status: str = Field(..., description="当前会话状态，如 active、paused、stopped。")
    current_capital: float = Field(..., description="当前剩余或可用资金。")
    current_positions: int = Field(..., description="当前持仓数量。")
    daily_pnl: float = Field(..., description="当日盈亏。")
    total_pnl: float = Field(..., description="累计盈亏。")
    created_at: datetime = Field(..., description="交易会话创建时间。")
    updated_at: datetime = Field(..., description="交易会话最近更新时间。")


class TradingSessionListResponse(BaseModel):
    """交易会话列表响应"""

    sessions: list[TradingSessionResponse] = Field(..., description="符合筛选条件的交易会话列表。")
    total: int = Field(..., description="当前返回结果对应的会话总数。")


class TradingSessionDeleteResponse(BaseModel):
    """删除交易会话响应"""

    message: str = Field(..., description="删除结果说明。")


class TradingSessionUpdate(BaseModel):
    """更新交易会话请求"""

    action: str = Field(..., description="会话动作，支持 start、pause、stop。")
    reason: Optional[str] = Field(None, description="本次状态变更的原因说明。")


TRADING_SESSION_CREATE_EXAMPLES = {
    "create_intraday_session": {
        "summary": "创建交易会话",
        "description": "创建一个绑定策略的盘中交易会话，指定初始资金、仓位和风险阈值。",
        "value": {
            "symbol": "600519",
            "strategy_id": "svm_momentum_v1",
            "initial_capital": 100000.0,
            "position_size": 0.1,
            "risk_threshold": 0.05,
        },
    }
}

TRADING_SESSION_UPDATE_EXAMPLES = {
    "pause_session_with_reason": {
        "summary": "暂停交易会话",
        "description": "将指定交易会话切换为暂停状态，并记录暂停原因。",
        "value": {
            "action": "pause",
            "reason": "日内波动超出阈值，临时暂停执行。",
        },
    }
}

TRADING_SESSION_LIST_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trading sessions retrieved",
    "data": {
        "sessions": [
            {
                "session_id": "session_demo_001",
                "symbol": "600519",
                "strategy_id": "svm_momentum_v1",
                "status": "active",
                "current_capital": 82000.0,
                "current_positions": 1,
                "daily_pnl": 0.0,
                "total_pnl": 0.0,
                "created_at": "2026-04-13T08:00:00+00:00",
                "updated_at": "2026-04-13T08:05:00+00:00",
            }
        ],
        "total": 1,
    },
}

TRADING_SESSION_DETAIL_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trading session retrieved",
    "data": {
        "session_id": "session_demo_001",
        "symbol": "600519",
        "strategy_id": "svm_momentum_v1",
        "status": "active",
        "current_capital": 82000.0,
        "current_positions": 1,
        "daily_pnl": 0.0,
        "total_pnl": 0.0,
        "created_at": "2026-04-13T08:00:00+00:00",
        "updated_at": "2026-04-13T08:05:00+00:00",
    },
}

TRADING_SESSION_CREATE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trading session created",
    "data": TRADING_SESSION_DETAIL_EXAMPLE["data"],
}

TRADING_SESSION_UPDATE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trading session updated",
    "data": {
        **TRADING_SESSION_DETAIL_EXAMPLE["data"],
        "status": "paused",
    },
}

TRADING_SESSION_DELETE_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Trading session deleted",
    "data": {
        "message": "Trading session session_demo_001 deleted",
    },
}

TRADING_SESSION_LIST_RESPONSES = _success_response_spec("交易会话列表结果。", TRADING_SESSION_LIST_EXAMPLE)
TRADING_SESSION_DETAIL_RESPONSES = _success_response_spec("交易会话详情结果。", TRADING_SESSION_DETAIL_EXAMPLE)
TRADING_SESSION_CREATE_RESPONSES = _success_response_spec("交易会话创建结果。", TRADING_SESSION_CREATE_SUCCESS_EXAMPLE)
TRADING_SESSION_UPDATE_RESPONSES = _success_response_spec("交易会话状态更新结果。", TRADING_SESSION_UPDATE_SUCCESS_EXAMPLE)
TRADING_SESSION_DELETE_RESPONSES = _success_response_spec("交易会话删除结果。", TRADING_SESSION_DELETE_SUCCESS_EXAMPLE)


def _resolve_query_value(value: Any) -> Any:
    return getattr(value, "default", value)


def _serialize_session(session: SessionState) -> dict[str, Any]:
    return TradingSessionResponse(
        session_id=session.session_id,
        symbol=session.symbol,
        strategy_id=session.strategy_id,
        status=session.status,
        current_capital=session.current_capital,
        current_positions=session.current_positions,
        daily_pnl=session.daily_pnl,
        total_pnl=session.total_pnl,
        created_at=session.created_at,
        updated_at=session.updated_at,
    ).model_dump()


@router.get(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="List Trading Sessions",
    description="按标的或状态筛选交易会话列表，当前实现接入进程内运行时状态，返回真实会话数据。",
    responses=TRADING_SESSION_LIST_RESPONSES,
)
async def list_trading_sessions(
    symbol: Optional[str] = Query(None, description="可选的交易标的代码过滤条件。"),
    status: Optional[str] = Query(None, description="可选的会话状态过滤条件，如 active 或 paused。"),
):
    sessions = runtime_store.list_sessions(symbol=_resolve_query_value(symbol), status=_resolve_query_value(status))
    return UnifiedResponse(
        success=True,
        code=200,
        message="Trading sessions retrieved",
        data={"sessions": [_serialize_session(item) for item in sessions], "total": len(sessions)},
    )


@router.get(
    "/{session_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Trading Session",
    description="根据交易会话ID获取会话详情，当前实现读取共享运行时状态。",
    responses=TRADING_SESSION_DETAIL_RESPONSES,
)
async def get_trading_session(session_id: str = Path(..., description="需要查询详情的交易会话ID。")):
    session = runtime_store.get_session(session_id)
    if session is None:
        return UnifiedResponse(success=False, code=404, message="Trading session not found", data={"session_id": session_id})
    return UnifiedResponse(success=True, code=200, message="Trading session retrieved", data=_serialize_session(session))


@router.post(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Create Trading Session",
    description="创建新的交易会话，当前实现会把会话写入共享运行时，并成为默认活动会话。",
    responses=TRADING_SESSION_CREATE_RESPONSES,
)
async def create_trading_session(
    request: TradingSessionCreate = Body(..., openapi_examples=TRADING_SESSION_CREATE_EXAMPLES)
):
    session = runtime_store.create_session(
        symbol=request.symbol,
        strategy_id=request.strategy_id,
        initial_capital=request.initial_capital,
        position_size=request.position_size,
        risk_threshold=request.risk_threshold,
    )
    return UnifiedResponse(success=True, code=200, message="Trading session created", data=_serialize_session(session))


@router.patch(
    "/{session_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Update Trading Session",
    description="更新指定交易会话的运行状态，当前实现支持 active/paused/stopped 状态切换。",
    responses=TRADING_SESSION_UPDATE_RESPONSES,
)
async def update_trading_session(
    session_id: str = Path(..., description="需要更新状态的交易会话ID。"),
    request: TradingSessionUpdate = Body(..., openapi_examples=TRADING_SESSION_UPDATE_EXAMPLES),
):
    session = runtime_store.update_session(session_id, request.action)
    if session is None:
        return UnifiedResponse(success=False, code=404, message="Trading session not found", data={"session_id": session_id})
    return UnifiedResponse(success=True, code=200, message="Trading session updated", data=_serialize_session(session))


@router.delete(
    "/{session_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Delete Trading Session",
    description="删除已完成或已取消的交易会话记录，当前实现会同时清理绑定持仓。",
    responses=TRADING_SESSION_DELETE_RESPONSES,
)
async def delete_trading_session(session_id: str = Path(..., description="需要删除的交易会话ID。")):
    deleted = runtime_store.delete_session(session_id)
    if not deleted:
        return UnifiedResponse(success=False, code=404, message="Trading session not found", data={"session_id": session_id})
    return UnifiedResponse(
        success=True,
        code=200,
        message="Trading session deleted",
        data=TradingSessionDeleteResponse(message=f"Trading session {session_id} deleted").model_dump(),
    )
