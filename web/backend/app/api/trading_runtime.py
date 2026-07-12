"""Lightweight trading runtime endpoints for frontend runtime availability.

This module intentionally avoids importing heavy trading engine dependencies,
so the API remains available in non-trading environments.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.responses import APIResponse, ErrorCodes, create_error_response, create_success_response
from app.core.security import verify_token


router = APIRouter(tags=["trading-runtime"])


class AddStrategyRequest(BaseModel):
    strategy_name: str = Field(..., min_length=1, max_length=100)


_RUNTIME_STATE: Dict[str, Any] = {
    "is_running": False,
    "session_id": None,
    "active_positions": 0,
    "total_pnl": 0.0,
    "daily_pnl": 0.0,
    "current_drawdown": 0.0,
    "strategies": [
        {
            "id": "demo-momentum",
            "name": "Demo Momentum",
            "type": "momentum",
            "pnl": 0.0,
            "win_rate": 0.0,
        },
    ],
    "market_data": {
        "000001.SH": {
            "price": 12.50,
            "change": 0.08,
            "change_percent": 0.64,
        },
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_write_auth(authorization: Optional[str]) -> None:
    if settings.testing:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "缺少或无效的认证凭据",
            ).dict(),
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token or verify_token(token) is None:
        raise HTTPException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "认证失败或令牌已过期",
            ).dict(),
        )


@router.get("/status", response_model=APIResponse, summary="Get trading runtime status")
async def get_status():
    return create_success_response(
        data={
            "session_id": _RUNTIME_STATE["session_id"],
            "active_positions": _RUNTIME_STATE["active_positions"],
            "total_pnl": _RUNTIME_STATE["total_pnl"],
            "daily_pnl": _RUNTIME_STATE["daily_pnl"],
            "current_drawdown": _RUNTIME_STATE["current_drawdown"],
            "is_running": _RUNTIME_STATE["is_running"],
            "last_updated": _now_iso(),
        },
        message="获取交易状态成功",
    )


@router.post("/start", response_model=APIResponse, summary="Start trading runtime session")
async def start_session(authorization: Optional[str] = Header(default=None, alias="Authorization")):
    _require_write_auth(authorization)
    if not _RUNTIME_STATE["is_running"]:
        _RUNTIME_STATE["is_running"] = True
        _RUNTIME_STATE["session_id"] = f"runtime-{int(datetime.now(timezone.utc).timestamp())}"

    return create_success_response(
        data={
            "session_id": _RUNTIME_STATE["session_id"],
            "is_running": _RUNTIME_STATE["is_running"],
        },
        message="交易会话已启动",
    )


@router.post("/stop", response_model=APIResponse, summary="Stop trading runtime session")
async def stop_session(authorization: Optional[str] = Header(default=None, alias="Authorization")):
    _require_write_auth(authorization)
    _RUNTIME_STATE["is_running"] = False
    _RUNTIME_STATE["session_id"] = None

    return create_success_response(
        data={
            "is_running": _RUNTIME_STATE["is_running"],
            "total_pnl": _RUNTIME_STATE["total_pnl"],
            "daily_pnl": _RUNTIME_STATE["daily_pnl"],
        },
        message="交易会话已停止",
    )


@router.get("/strategies/performance", response_model=APIResponse, summary="Get strategy performance list")
async def get_strategies_performance():
    strategies: List[Dict[str, Any]] = _RUNTIME_STATE["strategies"]
    return create_success_response(data=strategies, message="获取策略绩效成功")


@router.post("/strategies/add", response_model=APIResponse, summary="Add strategy to runtime list")
async def add_strategy(
    request: AddStrategyRequest,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
):
    _require_write_auth(authorization)
    name = request.strategy_name.strip()
    if any(item["name"] == name for item in _RUNTIME_STATE["strategies"]):
        return create_success_response(data={"name": name}, message="策略已存在")

    _RUNTIME_STATE["strategies"].append(
        {
            "id": f"strategy-{len(_RUNTIME_STATE['strategies']) + 1}",
            "name": name,
            "type": "custom",
            "pnl": 0.0,
            "win_rate": 0.0,
        },
    )
    return create_success_response(data={"name": name}, message="策略添加成功")


@router.delete("/strategies/{strategy_name}", response_model=APIResponse, summary="Remove strategy")
async def remove_strategy(
    strategy_name: str,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
):
    _require_write_auth(authorization)
    before = len(_RUNTIME_STATE["strategies"])
    _RUNTIME_STATE["strategies"] = [item for item in _RUNTIME_STATE["strategies"] if item["name"] != strategy_name]
    removed = len(_RUNTIME_STATE["strategies"]) < before
    return create_success_response(
        data={"strategy_name": strategy_name, "removed": removed},
        message="策略移除成功" if removed else "策略不存在",
    )


@router.get("/market/snapshot", response_model=APIResponse, summary="Get market snapshot")
async def get_market_snapshot():
    payload = {
        "timestamp": _now_iso(),
        "market_status": "open" if _RUNTIME_STATE["is_running"] else "idle",
        "data": _RUNTIME_STATE["market_data"],
    }
    return create_success_response(data=payload, message="获取市场快照成功")


@router.get("/risk/metrics", response_model=APIResponse, summary="Get risk metrics")
async def get_risk_metrics():
    payload = {
        "risk_status": "warning" if _RUNTIME_STATE["current_drawdown"] > 0.05 else "normal",
        "current_drawdown": _RUNTIME_STATE["current_drawdown"],
        "daily_pnl": _RUNTIME_STATE["daily_pnl"],
        "active_positions": _RUNTIME_STATE["active_positions"],
        "last_updated": _now_iso(),
    }
    return create_success_response(data=payload, message="获取风险指标成功")
