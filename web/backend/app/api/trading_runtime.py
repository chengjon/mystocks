"""
Lightweight trading runtime endpoints for frontend runtime availability.

This module intentionally avoids importing heavy trading engine dependencies,
so the API remains available in non-trading environments.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Header, HTTPException, Path
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.responses import APIResponse, ErrorCodes, create_error_response, create_success_response
from app.core.security import verify_token
from app.openapi_config import COMMON_RESPONSES

router = APIRouter(tags=["trading-runtime"])


class AddStrategyRequest(BaseModel):
    """向运行时会话添加策略实例的请求。"""

    strategy_name: str = Field(..., min_length=1, max_length=100, description="待加入运行时会话的策略名称。")


def _success_response_spec(description: str, message: str, data: Any) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": message,
                        "data": data,
                        "timestamp": "2026-04-04T09:30:00Z",
                    }
                }
            },
        }
    }


TRADING_RUNTIME_ERROR_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

TRADING_RUNTIME_WRITE_ERROR_RESPONSES = {
    401: {
        "description": "缺少 Bearer 令牌，或令牌无效/已过期，写操作被拒绝。",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "缺少或无效的认证凭据",
                    },
                    "message": "缺少或无效的认证凭据",
                    "timestamp": "2026-04-04T09:30:00Z",
                    "request_id": None,
                }
            }
        },
    },
    **TRADING_RUNTIME_ERROR_RESPONSES,
}

TRADING_RUNTIME_STATUS_RESPONSE = {
    **TRADING_RUNTIME_ERROR_RESPONSES,
    **_success_response_spec(
        "交易运行时状态快照",
        "获取交易状态成功",
        {
            "session_id": "runtime-1712203200",
            "active_positions": 3,
            "total_pnl": 12500.5,
            "daily_pnl": 850.2,
            "current_drawdown": 0.032,
            "is_running": True,
            "last_updated": "2026-04-04T09:30:00Z",
        },
    ),
}

TRADING_RUNTIME_STRATEGY_PERFORMANCE_RESPONSE = {
    **TRADING_RUNTIME_ERROR_RESPONSES,
    **_success_response_spec(
        "运行时策略绩效列表",
        "获取策略绩效成功",
        [
            {
                "id": "demo-momentum",
                "name": "Demo Momentum",
                "type": "momentum",
                "pnl": 12500.5,
                "win_rate": 0.63,
            },
            {
                "id": "demo-mean-reversion",
                "name": "Demo Mean Reversion",
                "type": "mean_reversion",
                "pnl": 4200.0,
                "win_rate": 0.57,
            },
        ],
    ),
}

TRADING_RUNTIME_MARKET_SNAPSHOT_RESPONSE = {
    **TRADING_RUNTIME_ERROR_RESPONSES,
    **_success_response_spec(
        "交易运行时市场快照",
        "获取市场快照成功",
        {
            "timestamp": "2026-04-04T09:30:00Z",
            "market_status": "open",
            "data": {
                "000001.SH": {"price": 12.5, "change": 0.08, "change_percent": 0.64},
                "600519.SH": {"price": 1710.88, "change": -5.12, "change_percent": -0.3},
            },
        },
    ),
}

TRADING_RUNTIME_RISK_METRICS_RESPONSE = {
    **TRADING_RUNTIME_ERROR_RESPONSES,
    **_success_response_spec(
        "交易运行时风险指标",
        "获取风险指标成功",
        {
            "risk_status": "warning",
            "current_drawdown": 0.061,
            "daily_pnl": -3200.0,
            "active_positions": 5,
            "last_updated": "2026-04-04T09:30:00Z",
        },
    ),
}

TRADING_RUNTIME_START_RESPONSE = {
    **TRADING_RUNTIME_WRITE_ERROR_RESPONSES,
    **_success_response_spec(
        "交易运行时会话启动结果",
        "交易会话已启动",
        {
            "session_id": "runtime-1712203200",
            "is_running": True,
        },
    ),
}

TRADING_RUNTIME_STOP_RESPONSE = {
    **TRADING_RUNTIME_WRITE_ERROR_RESPONSES,
    **_success_response_spec(
        "交易运行时会话停止结果",
        "交易会话已停止",
        {
            "is_running": False,
            "total_pnl": 12500.5,
            "daily_pnl": 850.2,
        },
    ),
}

TRADING_RUNTIME_ADD_STRATEGY_RESPONSE = {
    **TRADING_RUNTIME_WRITE_ERROR_RESPONSES,
    **_success_response_spec(
        "运行时策略注册结果",
        "策略添加成功",
        {
            "name": "Breakout Sentinel",
        },
    ),
}

TRADING_RUNTIME_REMOVE_STRATEGY_RESPONSE = {
    **TRADING_RUNTIME_WRITE_ERROR_RESPONSES,
    **_success_response_spec(
        "运行时策略移除结果",
        "策略移除成功",
        {
            "strategy_name": "Breakout Sentinel",
            "removed": True,
        },
    ),
}


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
        }
    ],
    "market_data": {
        "000001.SH": {
            "price": 12.50,
            "change": 0.08,
            "change_percent": 0.64,
        }
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


@router.get(
    "/status",
    response_model=APIResponse,
    summary="Get trading runtime status",
    description="返回轻量交易运行时当前会话、持仓数量、盈亏和回撤摘要，用于前端运行时面板轮询展示。",
    responses=TRADING_RUNTIME_STATUS_RESPONSE,
)
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


@router.post(
    "/start",
    response_model=APIResponse,
    summary="Start trading runtime session",
    description="启动轻量交易运行时会话，返回当前会话标识和运行态，供前端运行时面板刷新状态。",
    responses=TRADING_RUNTIME_START_RESPONSE,
)
async def start_session(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    )
):
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


@router.post(
    "/stop",
    response_model=APIResponse,
    summary="Stop trading runtime session",
    description="停止轻量交易运行时会话，并返回停止后的运行状态与盈亏摘要信息。",
    responses=TRADING_RUNTIME_STOP_RESPONSE,
)
async def stop_session(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    )
):
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


@router.get(
    "/strategies/performance",
    response_model=APIResponse,
    summary="Get strategy performance list",
    description="返回运行时当前已注册策略的收益、胜率等绩效摘要，供运行时策略列表和绩效面板展示。",
    responses=TRADING_RUNTIME_STRATEGY_PERFORMANCE_RESPONSE,
)
async def get_strategies_performance():
    strategies: List[Dict[str, Any]] = _RUNTIME_STATE["strategies"]
    return create_success_response(data=strategies, message="获取策略绩效成功")


@router.post(
    "/strategies/add",
    response_model=APIResponse,
    summary="Add strategy to runtime list",
    description="向轻量交易运行时注册一个前端可见的策略条目，便于在运行时面板中展示新增策略。",
    responses=TRADING_RUNTIME_ADD_STRATEGY_RESPONSE,
)
async def add_strategy(
    request: AddStrategyRequest = Body(
        ...,
        openapi_examples={
            "custom_strategy": {
                "summary": "添加自定义运行时策略",
                "value": {"strategy_name": "Breakout Sentinel"},
            }
        },
    ),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    ),
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
        }
    )
    return create_success_response(data={"name": name}, message="策略添加成功")


@router.delete(
    "/strategies/{strategy_name}",
    response_model=APIResponse,
    summary="Remove strategy",
    description="从轻量交易运行时中移除指定策略条目，并返回是否成功删除该策略。",
    responses=TRADING_RUNTIME_REMOVE_STRATEGY_RESPONSE,
)
async def remove_strategy(
    strategy_name: str = Path(..., description="要从运行时列表中移除的策略名称。"),
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 令牌。非测试环境下写操作必填，格式为 `Bearer <token>`。",
    ),
):
    _require_write_auth(authorization)
    before = len(_RUNTIME_STATE["strategies"])
    _RUNTIME_STATE["strategies"] = [item for item in _RUNTIME_STATE["strategies"] if item["name"] != strategy_name]
    removed = len(_RUNTIME_STATE["strategies"]) < before
    return create_success_response(
        data={"strategy_name": strategy_name, "removed": removed},
        message="策略移除成功" if removed else "策略不存在",
    )


@router.get(
    "/market/snapshot",
    response_model=APIResponse,
    summary="Get market snapshot",
    description="返回交易运行时缓存的市场状态与关键标的快照，供运行时首页刷新行情卡片。",
    responses=TRADING_RUNTIME_MARKET_SNAPSHOT_RESPONSE,
)
async def get_market_snapshot():
    payload = {
        "timestamp": _now_iso(),
        "market_status": "open" if _RUNTIME_STATE["is_running"] else "idle",
        "data": _RUNTIME_STATE["market_data"],
    }
    return create_success_response(data=payload, message="获取市场快照成功")


@router.get(
    "/risk/metrics",
    response_model=APIResponse,
    summary="Get risk metrics",
    description="返回交易运行时当前回撤、日内盈亏和持仓数量等核心风险指标，用于风控面板快速预警。",
    responses=TRADING_RUNTIME_RISK_METRICS_RESPONSE,
)
async def get_risk_metrics():
    payload = {
        "risk_status": "warning" if _RUNTIME_STATE["current_drawdown"] > 0.05 else "normal",
        "current_drawdown": _RUNTIME_STATE["current_drawdown"],
        "daily_pnl": _RUNTIME_STATE["daily_pnl"],
        "active_positions": _RUNTIME_STATE["active_positions"],
        "last_updated": _now_iso(),
    }
    return create_success_response(data=payload, message="获取风险指标成功")
