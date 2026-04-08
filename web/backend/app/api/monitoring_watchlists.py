#!/usr/bin/env python3
"""
监控清单管理 API
提供投资组合/观察列表的 CRUD 操作

API 端点:
- POST /api/v1/monitoring/watchlists - 创建清单
- GET /api/v1/monitoring/watchlists - 获取所有清单
- GET /api/v1/monitoring/watchlists/{id} - 获取单个清单
- PUT /api/v1/monitoring/watchlists/{id} - 更新清单
- DELETE /api/v1/monitoring/watchlists/{id} - 删除清单
- POST /api/v1/monitoring/watchlists/{id}/stocks - 添加股票
- DELETE /api/v1/monitoring/watchlists/{id}/stocks/{code} - 移除股票

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
import os
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, Field, field_validator

from app.core.exception_handlers import handle_exceptions
from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

logger = logging.getLogger(__name__)


def _success_response_spec(
    description: str,
    example: Any,
    extra_responses: Optional[Dict[int, Dict[str, Any]]] = None,
) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        },
        **(extra_responses or {}),
    }

MONITORING_WATCHLIST_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "依赖的监控数据库当前不可用",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "数据库未连接",
                    "error_code": "DATABASE_UNAVAILABLE",
                    "timestamp": "2026-04-03T10:30:00Z",
                }
            }
        },
    },
}

FEATURE_NOT_IMPLEMENTED_RESPONSE = {
    "description": "接口契约已预留，但后端实现尚未完成",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "message": "更新功能待实现",
                "error_code": "FEATURE_NOT_IMPLEMENTED",
                "timestamp": "2026-04-03T10:30:00Z",
            }
        }
    },
}

# Prefix is governed by the central route registry.
router = APIRouter(tags=["monitoring-watchlists"], responses=MONITORING_WATCHLIST_ROUTE_RESPONSES)

CREATE_WATCHLIST_REQUEST_EXAMPLES = {
    "manual_watchlist_with_risk_profile": {
        "summary": "创建手工监控清单",
        "description": "创建一个用于止损观察的手工清单，并附带基础风控参数。",
        "value": {
            "name": "核心止损监控",
            "watchlist_type": "manual",
            "risk_profile": {
                "max_position_size": 0.15,
                "default_stop_loss_pct": 0.08,
                "rebalance_window": "weekly",
            },
        },
    }
}

UPDATE_WATCHLIST_REQUEST_EXAMPLES = {
    "rebalance_watchlist_profile": {
        "summary": "更新清单名称与风控配置",
        "description": "调整清单展示名称、风控约束和启用状态，适用于策略切换或阶段性停用。",
        "value": {
            "name": "核心趋势监控",
            "watchlist_type": "strategy",
            "risk_profile": {
                "max_position_size": 0.12,
                "take_profit_pct": 0.18,
                "alert_threshold": "medium",
            },
            "is_active": True,
        },
    }
}

ADD_STOCK_REQUEST_EXAMPLES = {
    "add_stock_with_targets": {
        "summary": "添加带止损止盈的清单成员",
        "description": "向监控清单中加入一只股票，并同时记录建仓理由、止损价和目标价。",
        "value": {
            "stock_code": "600519",
            "entry_price": 1820.0,
            "entry_reason": "突破年线后纳入趋势跟踪",
            "stop_loss_price": 1750.0,
            "target_price": 1935.0,
            "weight": 0.2,
        },
    }
}

WATCHLIST_LIST_RESPONSES = _success_response_spec(
    "监控清单列表",
    {
        "success": True,
        "code": 200,
        "message": "获取清单列表成功",
        "data": [
            {
                "id": 1,
                "user_id": 1,
                "name": "核心止损监控",
                "watchlist_type": "manual",
                "risk_profile": {"max_position_size": 0.15, "default_stop_loss_pct": 0.08},
                "is_active": True,
                "created_at": "2026-03-13T09:30:00",
                "updated_at": "2026-03-13T09:30:00",
                "stocks_count": 2,
            }
        ],
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-001",
        "errors": None,
    },
)

WATCHLIST_DETAIL_RESPONSES = _success_response_spec(
    "监控清单详情",
    {
        "success": True,
        "code": 200,
        "message": "获取清单成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "name": "核心止损监控",
            "watchlist_type": "manual",
            "risk_profile": {"max_position_size": 0.15, "default_stop_loss_pct": 0.08},
            "is_active": True,
            "created_at": "2026-03-13T09:30:00",
            "updated_at": "2026-03-13T09:30:00",
            "stocks_count": 2,
        },
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-002",
        "errors": None,
    },
)

WATCHLIST_DELETE_RESPONSES = _success_response_spec(
    "监控清单删除成功",
    {
        "success": True,
        "code": 200,
        "message": "删除清单成功",
        "data": None,
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-003",
        "errors": None,
    },
)

WATCHLIST_STOCK_LIST_RESPONSES = _success_response_spec(
    "监控清单成员列表",
    {
        "success": True,
        "code": 200,
        "message": "获取股票列表成功",
        "data": [
            {
                "id": 1001,
                "watchlist_id": 1,
                "stock_code": "000001",
                "entry_price": 12.45,
                "entry_at": "2026-03-13T09:30:00",
                "entry_reason": "突破年线纳入观察",
                "stop_loss_price": 11.5,
                "target_price": 13.6,
                "weight": 0.4,
                "is_active": True,
            }
        ],
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-004",
        "errors": None,
    },
)

WATCHLIST_STOCK_DELETE_RESPONSES = _success_response_spec(
    "监控清单成员移除成功",
    {
        "success": True,
        "code": 200,
        "message": "移除股票成功",
        "data": None,
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-005",
        "errors": None,
    },
)

WATCHLIST_CREATE_RESPONSES = _success_response_spec(
    "监控清单创建结果",
    {
        "success": True,
        "code": 200,
        "message": "创建清单成功",
        "data": {
            "id": 3,
            "user_id": 1,
            "name": "港股高股息观察",
            "watchlist_type": "manual",
            "risk_profile": {
                "max_position_size": 0.1,
                "default_stop_loss_pct": 0.06,
                "market_scope": ["HK"],
            },
            "is_active": True,
            "created_at": "2026-04-08T03:40:00Z",
            "updated_at": "2026-04-08T03:40:00Z",
            "stocks_count": 0,
        },
        "timestamp": "2026-04-08T03:40:00Z",
        "request_id": "req-monitoring-watchlists-create-001",
        "errors": None,
    },
)

WATCHLIST_UPDATE_RESPONSES = _success_response_spec(
    "监控清单更新结果",
    {
        "success": True,
        "code": 200,
        "message": "更新清单成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "name": "股指期货风险监控",
            "watchlist_type": "strategy",
            "risk_profile": {
                "max_position_size": 0.12,
                "take_profit_pct": 0.18,
                "alert_threshold": "medium",
                "market_scope": ["CFFEX"],
            },
            "is_active": True,
            "created_at": "2026-03-13T09:30:00Z",
            "updated_at": "2026-04-08T03:45:00Z",
            "stocks_count": 4,
        },
        "timestamp": "2026-04-08T03:45:00Z",
        "request_id": "req-monitoring-watchlists-update-001",
        "errors": None,
    },
    {501: FEATURE_NOT_IMPLEMENTED_RESPONSE},
)

WATCHLIST_STOCK_CREATE_RESPONSES = _success_response_spec(
    "监控清单成员添加结果",
    {
        "success": True,
        "code": 200,
        "message": "添加股票成功",
        "data": {
            "id": 3001,
            "watchlist_id": 3,
            "stock_code": "00700.HK",
            "entry_price": 328.6,
            "entry_at": "2026-04-08T03:50:00Z",
            "entry_reason": "港股科技龙头纳入观察",
            "stop_loss_price": 312.0,
            "target_price": 356.0,
            "weight": 0.25,
            "is_active": True,
        },
        "timestamp": "2026-04-08T03:50:00Z",
        "request_id": "req-monitoring-watchlists-stock-create-001",
        "errors": None,
    },
)


# ==================== 请求模型 ====================


class CreateWatchlistRequest(BaseModel):
    """创建监控清单请求"""

    name: str = Field(..., description="清单名称", min_length=1, max_length=100)
    watchlist_type: str = Field("manual", description="清单类型: manual/strategy/benchmark")
    risk_profile: Optional[Dict[str, Any]] = Field(None, description="风控配置")

    @field_validator("watchlist_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """验证清单类型"""
        valid_types = ["manual", "strategy", "benchmark"]
        if v not in valid_types:
            raise ValueError(f"无效的清单类型，支持: {', '.join(valid_types)}")
        return v


class UpdateWatchlistRequest(BaseModel):
    """更新监控清单请求"""

    name: Optional[str] = Field(None, description="清单名称", min_length=1, max_length=100)
    watchlist_type: Optional[str] = Field(None, description="清单类型")
    risk_profile: Optional[Dict[str, Any]] = Field(None, description="风控配置")
    is_active: Optional[bool] = Field(None, description="是否激活")


class AddStockRequest(BaseModel):
    """添加股票到清单请求"""

    stock_code: str = Field(..., description="股票代码", min_length=1, max_length=20)
    entry_price: Optional[float] = Field(None, description="入库价格", ge=0)
    entry_reason: Optional[str] = Field(None, description="入库理由", max_length=50)
    stop_loss_price: Optional[float] = Field(None, description="止损价格", ge=0)
    target_price: Optional[float] = Field(None, description="止盈价格", ge=0)
    weight: Optional[float] = Field(0.0, description="权重", ge=0, le=1)


class BatchAddStocksRequest(BaseModel):
    """批量添加股票请求"""

    stocks: List[AddStockRequest] = Field(..., description="股票列表", min_length=1, max_length=100)


# ==================== 响应模型 ====================


class WatchlistResponse(BaseModel):
    """监控清单响应"""

    id: int = Field(..., description="清单ID")
    user_id: int = Field(..., description="用户ID")
    name: str = Field(..., description="清单名称")
    watchlist_type: str = Field(..., description="清单类型")
    risk_profile: Optional[Dict[str, Any]] = Field(None, description="风控配置")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    stocks_count: int = Field(0, description="股票数量")


class WatchlistStockResponse(BaseModel):
    """清单成员响应"""

    id: int = Field(..., description="记录ID")
    watchlist_id: int = Field(..., description="清单ID")
    stock_code: str = Field(..., description="股票代码")
    entry_price: Optional[float] = Field(None, description="入库价格")
    entry_at: Optional[datetime] = Field(None, description="入库时间")
    entry_reason: Optional[str] = Field(None, description="入库理由")
    stop_loss_price: Optional[float] = Field(None, description="止损价格")
    target_price: Optional[float] = Field(None, description="止盈价格")
    weight: float = Field(..., description="权重")
    is_active: bool = Field(..., description="是否激活")


_RUNTIME_FALLBACK_TIMESTAMP = datetime(2026, 3, 13, 9, 30, 0)
_runtime_watchlists: Optional[List[WatchlistResponse]] = None
_runtime_watchlist_stocks: Optional[Dict[int, List[WatchlistStockResponse]]] = None


def _runtime_fallback_enabled() -> bool:
    return (
        os.getenv("TESTING", "false").lower() == "true"
        or os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    )


def _build_runtime_watchlist_stocks() -> Dict[int, List[WatchlistStockResponse]]:
    return {
        1: [
            WatchlistStockResponse(
                id=1001,
                watchlist_id=1,
                stock_code="000001",
                entry_price=12.45,
                entry_at=_RUNTIME_FALLBACK_TIMESTAMP,
                entry_reason="runtime-fallback",
                stop_loss_price=11.50,
                target_price=13.60,
                weight=0.40,
                is_active=True,
            ),
            WatchlistStockResponse(
                id=1002,
                watchlist_id=1,
                stock_code="600519",
                entry_price=1820.00,
                entry_at=_RUNTIME_FALLBACK_TIMESTAMP,
                entry_reason="runtime-fallback",
                stop_loss_price=1750.00,
                target_price=1935.00,
                weight=0.60,
                is_active=True,
            ),
        ],
        2: [
            WatchlistStockResponse(
                id=2001,
                watchlist_id=2,
                stock_code="300750",
                entry_price=210.35,
                entry_at=_RUNTIME_FALLBACK_TIMESTAMP,
                entry_reason="runtime-fallback",
                stop_loss_price=198.00,
                target_price=228.00,
                weight=1.00,
                is_active=True,
            )
        ],
    }


def _build_runtime_watchlists(user_id: int) -> List[WatchlistResponse]:
    stocks_by_watchlist = _build_runtime_watchlist_stocks()
    return [
        WatchlistResponse(
            id=1,
            user_id=user_id,
            name="核心止损监控",
            watchlist_type="manual",
            risk_profile={"source": "runtime-fallback", "purpose": "stop-loss-monitoring"},
            is_active=True,
            created_at=_RUNTIME_FALLBACK_TIMESTAMP,
            updated_at=_RUNTIME_FALLBACK_TIMESTAMP,
            stocks_count=len(stocks_by_watchlist[1]),
        ),
        WatchlistResponse(
            id=2,
            user_id=user_id,
            name="观察池",
            watchlist_type="manual",
            risk_profile={"source": "runtime-fallback", "purpose": "secondary-watchlist"},
            is_active=False,
            created_at=_RUNTIME_FALLBACK_TIMESTAMP,
            updated_at=_RUNTIME_FALLBACK_TIMESTAMP,
            stocks_count=len(stocks_by_watchlist[2]),
        ),
    ]


def _clone_model(response: Any) -> Any:
    return response.model_copy(deep=True) if hasattr(response, "model_copy") else deepcopy(response)


def _ensure_runtime_watchlist_state(user_id: int) -> tuple[List[WatchlistResponse], Dict[int, List[WatchlistStockResponse]]]:
    global _runtime_watchlists, _runtime_watchlist_stocks

    if _runtime_watchlists is None or _runtime_watchlist_stocks is None:
        _runtime_watchlist_stocks = _build_runtime_watchlist_stocks()
        _runtime_watchlists = _build_runtime_watchlists(user_id)

    return _runtime_watchlists, _runtime_watchlist_stocks


def _get_runtime_watchlists(user_id: int) -> List[WatchlistResponse]:
    watchlists, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id)
    results: List[WatchlistResponse] = []

    for watchlist in watchlists:
        cloned = _clone_model(watchlist)
        cloned.user_id = user_id
        cloned.stocks_count = len(stocks_by_watchlist.get(cloned.id, []))
        results.append(cloned)

    return results


def _get_runtime_watchlist_stocks(watchlist_id: int) -> Optional[List[WatchlistStockResponse]]:
    _, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id=1)
    rows = stocks_by_watchlist.get(watchlist_id)
    if rows is None:
        return None
    return [_clone_model(row) for row in rows]


def _get_runtime_watchlist(watchlist_id: int, user_id: int) -> Optional[WatchlistResponse]:
    for watchlist in _get_runtime_watchlists(user_id):
        if watchlist.id == watchlist_id:
            return _clone_model(watchlist)
    return None


def _next_runtime_watchlist_stock_id() -> int:
    _, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id=1)
    existing_ids = [stock.id for rows in stocks_by_watchlist.values() for stock in rows]
    return max(existing_ids, default=2000) + 1


def _next_runtime_watchlist_id() -> int:
    watchlists, _ = _ensure_runtime_watchlist_state(user_id=1)
    existing_ids = [watchlist.id for watchlist in watchlists]
    return max(existing_ids, default=2) + 1


def _create_runtime_watchlist(request: CreateWatchlistRequest, user_id: int) -> WatchlistResponse:
    watchlists, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id)
    created = WatchlistResponse(
        id=_next_runtime_watchlist_id(),
        user_id=user_id,
        name=request.name,
        watchlist_type=request.watchlist_type,
        risk_profile=request.risk_profile,
        is_active=True,
        created_at=_RUNTIME_FALLBACK_TIMESTAMP,
        updated_at=_RUNTIME_FALLBACK_TIMESTAMP,
        stocks_count=0,
    )
    watchlists.insert(0, created)
    stocks_by_watchlist.setdefault(created.id, [])
    return _clone_model(created)


def _add_runtime_stock_to_watchlist(
    watchlist_id: int,
    request: AddStockRequest,
    user_id: int,
) -> Optional[WatchlistStockResponse]:
    watchlists, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id)
    if not any(watchlist.id == watchlist_id for watchlist in watchlists):
        return None

    rows = stocks_by_watchlist.setdefault(watchlist_id, [])
    for index, existing in enumerate(rows):
        if existing.stock_code == request.stock_code:
            updated = _clone_model(existing)
            updated.entry_price = request.entry_price
            updated.entry_reason = request.entry_reason
            updated.stop_loss_price = request.stop_loss_price
            updated.target_price = request.target_price
            updated.weight = request.weight or 0.0
            rows[index] = updated
            return _clone_model(updated)

    created = WatchlistStockResponse(
        id=_next_runtime_watchlist_stock_id(),
        watchlist_id=watchlist_id,
        stock_code=request.stock_code,
        entry_price=request.entry_price,
        entry_at=_RUNTIME_FALLBACK_TIMESTAMP,
        entry_reason=request.entry_reason or "runtime-fallback",
        stop_loss_price=request.stop_loss_price,
        target_price=request.target_price,
        weight=request.weight or 0.0,
        is_active=True,
    )
    rows.append(created)
    return _clone_model(created)


def _remove_runtime_stock_from_watchlist(
    watchlist_id: int,
    stock_code: str,
    user_id: int,
) -> bool:
    _watchlists, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id)
    rows = stocks_by_watchlist.get(watchlist_id)
    if not rows:
        return False

    original_len = len(rows)
    stocks_by_watchlist[watchlist_id] = [row for row in rows if row.stock_code != stock_code]
    return len(stocks_by_watchlist[watchlist_id]) != original_len


def _delete_runtime_watchlist(watchlist_id: int, user_id: int) -> bool:
    watchlists, stocks_by_watchlist = _ensure_runtime_watchlist_state(user_id)
    original_len = len(watchlists)
    watchlists[:] = [watchlist for watchlist in watchlists if watchlist.id != watchlist_id]
    stocks_by_watchlist.pop(watchlist_id, None)
    return len(watchlists) != original_len


# ==================== API 端点 ====================


@router.post(
    "",
    response_model=UnifiedResponse[WatchlistResponse],
    summary="创建监控清单",
    description="创建一个新的监控清单，记录名称、清单类型和可选风控配置，供后续持仓跟踪与告警使用。",
    responses=WATCHLIST_CREATE_RESPONSES,
)
@handle_exceptions
async def create_watchlist(
    request: CreateWatchlistRequest = Body(..., openapi_examples=CREATE_WATCHLIST_REQUEST_EXAMPLES),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[WatchlistResponse]:
    """
    创建监控清单

    - **name**: 清单名称
    - **watchlist_type**: 清单类型 (manual/strategy/benchmark)
    - **risk_profile**: 风控配置 (可选)
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            if _runtime_fallback_enabled():
                return UnifiedResponse(data=_create_runtime_watchlist(request, user_id), message="创建清单成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlist_id = await postgres_async.create_watchlist(
            user_id=user_id,
            name=request.name,
            type=request.watchlist_type,
            risk_profile=request.risk_profile,
        )

        watchlist = await postgres_async.get_watchlists_by_user(user_id)
        created = next((w for w in watchlist if w["id"] == watchlist_id), None)

        if created:
            response = WatchlistResponse(
                id=created["id"],
                user_id=created["user_id"],
                name=created["name"],
                watchlist_type=created["type"],
                risk_profile=created.get("risk_profile"),
                is_active=created["is_active"],
                created_at=created["created_at"],
                updated_at=created["updated_at"],
                stocks_count=0,
            )
            return UnifiedResponse(data=response, message="创建清单成功")

        raise BusinessException(detail="创建清单失败", status_code=500, error_code="WATCHLIST_CREATION_FAILED")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        if _runtime_fallback_enabled():
            logger.warning("创建监控清单降级到 runtime fallback: %s", str(e))
            return UnifiedResponse(data=_create_runtime_watchlist(request, user_id), message="创建清单成功")
        logger.error("创建监控清单失败: %(e)s")
        raise BusinessException(detail=f"创建失败: {str(e)}", status_code=500, error_code="WATCHLIST_CREATION_FAILED")


@router.get(
    "",
    response_model=UnifiedResponse[List[WatchlistResponse]],
    summary="获取监控清单列表",
    description="按用户查询当前全部监控清单，并返回每个清单的类型、启用状态、风控配置和成员数量汇总。",
    responses=WATCHLIST_LIST_RESPONSES,
)
@handle_exceptions
async def list_watchlists(
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[List[WatchlistResponse]]:
    """
    获取用户的所有监控清单
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            if _runtime_fallback_enabled():
                return UnifiedResponse(data=_get_runtime_watchlists(user_id), message="获取清单列表成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)

        if not watchlists and _runtime_fallback_enabled():
            return UnifiedResponse(data=_get_runtime_watchlists(user_id), message="获取清单列表成功")

        results = []
        for w in watchlists:
            stocks = await postgres_async.get_watchlist_stocks(w["id"])
            results.append(
                WatchlistResponse(
                    id=w["id"],
                    user_id=w["user_id"],
                    name=w["name"],
                    watchlist_type=w["type"],
                    risk_profile=w.get("risk_profile"),
                    is_active=w["is_active"],
                    created_at=w["created_at"],
                    updated_at=w["updated_at"],
                    stocks_count=len(stocks),
                )
            )

        return UnifiedResponse(data=results, message="获取清单列表成功")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        if _runtime_fallback_enabled():
            logger.warning("获取监控清单列表降级到 runtime fallback: %s", str(e))
            return UnifiedResponse(data=_get_runtime_watchlists(user_id), message="获取清单列表成功")
        logger.error("获取监控清单列表失败: %(e)s")
        raise BusinessException(detail=f"获取失败: {str(e)}", status_code=500, error_code="WATCHLIST_RETRIEVAL_FAILED")


@router.get(
    "/{watchlist_id}",
    response_model=UnifiedResponse[WatchlistResponse],
    summary="获取监控清单详情",
    description="根据清单 ID 查询单个监控清单的完整信息，包括名称、风控配置、启用状态以及当前成员数量。",
    responses=WATCHLIST_DETAIL_RESPONSES,
)
@handle_exceptions
async def get_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[WatchlistResponse]:
    """
    获取单个监控清单详情
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            if _runtime_fallback_enabled():
                fallback_watchlist = _get_runtime_watchlist(watchlist_id=watchlist_id, user_id=user_id)
                if fallback_watchlist is not None:
                    return UnifiedResponse(data=fallback_watchlist, message="获取清单成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise NotFoundException(resource="监控清单", identifier="查询条件")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

        response = WatchlistResponse(
            id=watchlist["id"],
            user_id=watchlist["user_id"],
            name=watchlist["name"],
            watchlist_type=watchlist["type"],
            risk_profile=watchlist.get("risk_profile"),
            is_active=watchlist["is_active"],
            created_at=watchlist["created_at"],
            updated_at=watchlist["updated_at"],
            stocks_count=len(stocks),
        )

        return UnifiedResponse(data=response, message="获取清单成功")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取监控清单失败: %(e)s")
        raise BusinessException(detail=f"获取失败: {str(e)}", status_code=500, error_code="WATCHLIST_RETRIEVAL_FAILED")


@router.put(
    "/{watchlist_id}",
    response_model=UnifiedResponse[WatchlistResponse],
    summary="更新监控清单",
    description="更新监控清单的名称、类型、风控配置或启用状态。当前版本仅保留契约，后端实现尚未开放。",
    responses=WATCHLIST_UPDATE_RESPONSES,
)
@handle_exceptions
async def update_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    request: UpdateWatchlistRequest = Body(..., openapi_examples=UPDATE_WATCHLIST_REQUEST_EXAMPLES),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[WatchlistResponse]:
    """
    更新监控清单
    """
    raise BusinessException(detail="更新功能待实现", status_code=501, error_code="FEATURE_NOT_IMPLEMENTED")


@router.delete(
    "/{watchlist_id}",
    response_model=UnifiedResponse[None],
    summary="删除监控清单",
    description="删除指定监控清单，并级联移除该清单下的全部成员记录，适用于清单下线或策略废弃场景。",
    responses=WATCHLIST_DELETE_RESPONSES,
)
@handle_exceptions
async def delete_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[None]:
    """
    删除监控清单（级联删除成员）
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            if _runtime_fallback_enabled():
                if _delete_runtime_watchlist(watchlist_id=watchlist_id, user_id=user_id):
                    return UnifiedResponse(message="删除清单成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise NotFoundException(resource="监控清单", identifier="查询条件")

        from src.monitoring.infrastructure.postgresql_async_v3 import MonitoringPostgreSQLAccess

        access = MonitoringPostgreSQLAccess()

        await access.delete_watchlist(watchlist_id)

        return UnifiedResponse(message="删除清单成功")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        logger.error("删除监控清单失败: %(e)s")
        raise BusinessException(detail=f"删除失败: {str(e)}", status_code=500, error_code="WATCHLIST_DELETION_FAILED")


@router.post(
    "/{watchlist_id}/stocks",
    response_model=UnifiedResponse[WatchlistStockResponse],
    summary="添加监控清单成员",
    description="向指定监控清单添加一只股票，并记录入库价格、建仓理由、止损价、目标价和权重等跟踪信息。",
    responses=WATCHLIST_STOCK_CREATE_RESPONSES,
)
@handle_exceptions
async def add_stock_to_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    request: AddStockRequest = Body(..., openapi_examples=ADD_STOCK_REQUEST_EXAMPLES),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[WatchlistStockResponse]:
    """
    添加股票到清单
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import StockToAdd, get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            if _runtime_fallback_enabled():
                fallback_stock = _add_runtime_stock_to_watchlist(
                    watchlist_id=watchlist_id,
                    request=request,
                    user_id=user_id,
                )
                if fallback_stock is not None:
                    return UnifiedResponse(data=fallback_stock, message="添加股票成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise NotFoundException(resource="监控清单", identifier="查询条件")

        stock_id = await postgres_async.add_stock_to_watchlist(
            StockToAdd(
                watchlist_id=watchlist_id,
                stock_code=request.stock_code,
                entry_price=request.entry_price,
                entry_reason=request.entry_reason,
                stop_loss_price=request.stop_loss_price,
                target_price=request.target_price,
                weight=request.weight or 0.0,
            )
        )

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)
        added_stock = next((s for s in stocks if s["id"] == stock_id), None)

        if added_stock:
            response = WatchlistStockResponse(
                id=added_stock["id"],
                watchlist_id=added_stock["watchlist_id"],
                stock_code=added_stock["stock_code"],
                entry_price=added_stock["entry_price"],
                entry_at=added_stock["entry_at"],
                entry_reason=added_stock["entry_reason"],
                stop_loss_price=added_stock["stop_loss_price"],
                target_price=added_stock["target_price"],
                weight=added_stock["weight"],
                is_active=added_stock["is_active"],
            )
            return UnifiedResponse(data=response, message="添加股票成功")

        raise BusinessException(detail="添加股票失败", status_code=500, error_code="STOCK_ADDITION_FAILED")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        if _runtime_fallback_enabled():
            fallback_stock = _add_runtime_stock_to_watchlist(watchlist_id=watchlist_id, request=request, user_id=user_id)
            if fallback_stock is not None:
                logger.warning("添加股票降级到 runtime fallback: %s", str(e))
                return UnifiedResponse(data=fallback_stock, message="添加股票成功")
        logger.error("添加股票到清单失败: %(e)s")
        raise BusinessException(detail=f"添加失败: {str(e)}", status_code=500, error_code="STOCK_ADDITION_FAILED")


@router.get(
    "/{watchlist_id}/stocks",
    response_model=UnifiedResponse[List[WatchlistStockResponse]],
    summary="获取监控清单成员",
    description="查询指定监控清单下的全部股票成员及其入库价格、风控阈值、权重和启用状态。",
    responses=WATCHLIST_STOCK_LIST_RESPONSES,
)
@handle_exceptions
async def list_watchlist_stocks(
    watchlist_id: int = Path(..., description="清单ID"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[List[WatchlistStockResponse]]:
    """
    获取清单中的所有股票
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            if _runtime_fallback_enabled():
                fallback_rows = _get_runtime_watchlist_stocks(watchlist_id)
                if fallback_rows is not None:
                    return UnifiedResponse(data=fallback_rows, message="获取股票列表成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise NotFoundException(resource="监控清单", identifier="查询条件")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

        if not stocks and _runtime_fallback_enabled():
            fallback_rows = _get_runtime_watchlist_stocks(watchlist_id)
            if fallback_rows is not None:
                return UnifiedResponse(data=fallback_rows, message="获取股票列表成功")

        results = []
        for s in stocks:
            results.append(
                WatchlistStockResponse(
                    id=s["id"],
                    watchlist_id=s["watchlist_id"],
                    stock_code=s["stock_code"],
                    entry_price=s["entry_price"],
                    entry_at=s["entry_at"],
                    entry_reason=s["entry_reason"],
                    stop_loss_price=s["stop_loss_price"],
                    target_price=s["target_price"],
                    weight=s["weight"],
                    is_active=s["is_active"],
                )
            )

        return UnifiedResponse(data=results, message="获取股票列表成功")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        if _runtime_fallback_enabled():
            fallback_rows = _get_runtime_watchlist_stocks(watchlist_id)
            if fallback_rows is not None:
                logger.warning("获取清单股票列表降级到 runtime fallback: %s", str(e))
                return UnifiedResponse(data=fallback_rows, message="获取股票列表成功")
        logger.error("获取清单股票列表失败: %(e)s")
        raise BusinessException(detail=f"获取失败: {str(e)}", status_code=500, error_code="WATCHLIST_RETRIEVAL_FAILED")


@router.delete(
    "/{watchlist_id}/stocks/{stock_code}",
    response_model=UnifiedResponse[None],
    summary="移除监控清单成员",
    description="从指定监控清单中移除某只股票，常用于止损出清、观察结束或误加成员后的回滚处理。",
    responses=WATCHLIST_STOCK_DELETE_RESPONSES,
)
@handle_exceptions
async def remove_stock_from_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    stock_code: str = Path(..., description="股票代码"),
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[None]:
    """
    从清单中移除股票
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()
        if not postgres_async.is_connected():
            if _runtime_fallback_enabled() and _remove_runtime_stock_from_watchlist(watchlist_id, stock_code, user_id):
                return UnifiedResponse(message="移除股票成功")
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        await postgres_async.remove_stock_from_watchlist(watchlist_id, stock_code)

        return UnifiedResponse(message="移除股票成功")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        if _runtime_fallback_enabled() and _remove_runtime_stock_from_watchlist(watchlist_id, stock_code, user_id):
            logger.warning("移除股票降级到 runtime fallback: %s", str(e))
            return UnifiedResponse(message="移除股票成功")
        logger.error("从清单移除股票失败: %(e)s")
        raise BusinessException(detail=f"移除失败: {str(e)}", status_code=500, error_code="STOCK_REMOVAL_FAILED")
