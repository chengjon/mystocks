"""
交易会话API

提供实时交易会话管理功能
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field

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

TRADING_SESSION_RESPONSE_EXAMPLE = {
    "session_id": "session_001",
    "symbol": "600519",
    "strategy_id": "svm_momentum_v1",
    "status": "active",
    "current_capital": 102500.0,
    "current_positions": 100,
    "daily_pnl": 2500.0,
    "total_pnl": 2500.0,
    "created_at": "2026-04-08T09:30:00",
    "updated_at": "2026-04-08T15:00:00",
}

TRADING_SESSION_LIST_RESPONSE_EXAMPLE = {
    "sessions": [
        TRADING_SESSION_RESPONSE_EXAMPLE,
        {
            "session_id": "session_002",
            "symbol": "0700.HK",
            "strategy_id": "hk_breakout_v2",
            "status": "paused",
            "current_capital": 208000.0,
            "current_positions": 0,
            "daily_pnl": -1200.0,
            "total_pnl": 8000.0,
            "created_at": "2026-04-07T09:30:00",
            "updated_at": "2026-04-08T11:00:00",
        },
    ],
    "total": 2,
}

TRADING_SESSION_CREATE_RESPONSE_EXAMPLE = {
    "session_id": "session_1744085700",
    "symbol": "600519",
    "strategy_id": "svm_momentum_v1",
    "status": "active",
    "current_capital": 100000.0,
    "current_positions": 0,
    "daily_pnl": 0.0,
    "total_pnl": 0.0,
    "created_at": "2026-04-08T12:25:00",
    "updated_at": "2026-04-08T12:25:00",
}

TRADING_SESSION_UPDATE_RESPONSE_EXAMPLE = {
    "session_id": "session_001",
    "symbol": "600519",
    "strategy_id": "svm_momentum_v1",
    "status": "pause",
    "current_capital": 102500.0,
    "current_positions": 100,
    "daily_pnl": 2500.0,
    "total_pnl": 2500.0,
    "created_at": "2026-04-08T09:30:00",
    "updated_at": "2026-04-08T12:25:00",
}

TRADING_SESSION_DELETE_RESPONSE_EXAMPLE = {
    "message": "Session session_001 deleted successfully",
}

TRADING_SESSION_LIST_RESPONSES = _success_response_spec("交易会话列表查询成功。", TRADING_SESSION_LIST_RESPONSE_EXAMPLE)
TRADING_SESSION_DETAIL_RESPONSES = _success_response_spec("交易会话详情查询成功。", TRADING_SESSION_RESPONSE_EXAMPLE)
TRADING_SESSION_CREATE_RESPONSES = _success_response_spec("交易会话创建成功。", TRADING_SESSION_CREATE_RESPONSE_EXAMPLE)
TRADING_SESSION_UPDATE_RESPONSES = _success_response_spec("交易会话状态更新成功。", TRADING_SESSION_UPDATE_RESPONSE_EXAMPLE)
TRADING_SESSION_DELETE_RESPONSES = _success_response_spec("交易会话删除成功。", TRADING_SESSION_DELETE_RESPONSE_EXAMPLE)


@router.get(
    "",
    response_model=TradingSessionListResponse,
    summary="List Trading Sessions",
    description="按标的或状态筛选交易会话列表，返回当前会话概览与总数。",
    responses=TRADING_SESSION_LIST_RESPONSES,
)
async def list_trading_sessions(
    symbol: Optional[str] = Query(None, description="可选的交易标的代码过滤条件。"),
    status: Optional[str] = Query(None, description="可选的会话状态过滤条件，如 active 或 paused。"),
):
    """
    获取交易会话列表

    Returns list of active trading sessions.
    """
    mock_sessions = [
        {
            "session_id": "session_001",
            "symbol": "600519",
            "strategy_id": "svm_momentum_v1",
            "status": "active",
            "current_capital": 102500.0,
            "current_positions": 100,
            "daily_pnl": 2500.0,
            "total_pnl": 2500.0,
            "created_at": "2025-01-20T09:30:00Z",
            "updated_at": "2025-01-20T15:00:00Z",
        },
    ]

    if symbol:
        mock_sessions = [s for s in mock_sessions if s["symbol"] == symbol]
    if status:
        mock_sessions = [s for s in mock_sessions if s["status"] == status]

    return {"sessions": mock_sessions, "total": len(mock_sessions)}


@router.get(
    "/{session_id}",
    response_model=TradingSessionResponse,
    summary="Get Trading Session",
    description="根据交易会话ID获取单个会话的资金、仓位和盈亏详情。",
    responses=TRADING_SESSION_DETAIL_RESPONSES,
)
async def get_trading_session(session_id: str = Path(..., description="需要查询详情的交易会话ID。")):
    """
    获取单个交易会话详情

    Returns details of a specific trading session.
    """
    return TradingSessionResponse(
        session_id=session_id,
        symbol="600519",
        strategy_id="svm_momentum_v1",
        status="active",
        current_capital=102500.0,
        current_positions=100,
        daily_pnl=2500.0,
        total_pnl=2500.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.post(
    "",
    response_model=TradingSessionResponse,
    summary="Create Trading Session",
    description="创建新的交易会话，并基于请求参数初始化资金、仓位和风险阈值。",
    responses=TRADING_SESSION_CREATE_RESPONSES,
)
async def create_trading_session(
    request: TradingSessionCreate = Body(..., openapi_examples=TRADING_SESSION_CREATE_EXAMPLES)
):
    """
    创建新的交易会话

    Creates a new trading session with specified parameters.
    """
    session_id = f"session_{int(datetime.now().timestamp())}"
    return TradingSessionResponse(
        session_id=session_id,
        symbol=request.symbol,
        strategy_id=request.strategy_id,
        status="active",
        current_capital=request.initial_capital,
        current_positions=0,
        daily_pnl=0.0,
        total_pnl=0.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.patch(
    "/{session_id}",
    response_model=TradingSessionResponse,
    summary="Update Trading Session",
    description="更新指定交易会话的运行状态，例如启动、暂停或停止。",
    responses=TRADING_SESSION_UPDATE_RESPONSES,
)
async def update_trading_session(
    session_id: str = Path(..., description="需要更新状态的交易会话ID。"),
    request: TradingSessionUpdate = Body(..., openapi_examples=TRADING_SESSION_UPDATE_EXAMPLES),
):
    """
    更新交易会话状态

    Updates the status of a trading session (start, pause, stop).
    """
    return TradingSessionResponse(
        session_id=session_id,
        symbol="600519",
        strategy_id="svm_momentum_v1",
        status=request.action,
        current_capital=102500.0,
        current_positions=100,
        daily_pnl=2500.0,
        total_pnl=2500.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.delete(
    "/{session_id}",
    response_model=TradingSessionDeleteResponse,
    summary="Delete Trading Session",
    description="删除已完成或已取消的交易会话记录，并返回本次删除操作的结果说明。",
    responses=TRADING_SESSION_DELETE_RESPONSES,
)
async def delete_trading_session(session_id: str = Path(..., description="需要删除的交易会话ID。")):
    """
    删除交易会话

    Deletes a completed or cancelled trading session.
    """
    return {"message": f"Session {session_id} deleted successfully"}
