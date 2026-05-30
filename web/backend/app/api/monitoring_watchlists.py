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
from copy import deepcopy
from typing import Any, Dict, List, Optional

from fastapi import Body, Depends, Path, Query

from app.core.exception_handlers import handle_exceptions
from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import UnifiedResponse

logger = logging.getLogger(__name__)


from app.api._monitoring_watchlists_responses import (
    CREATE_WATCHLIST_REQUEST_EXAMPLES,
    UPDATE_WATCHLIST_REQUEST_EXAMPLES,
    ADD_STOCK_REQUEST_EXAMPLES,
    router,
    WATCHLIST_LIST_RESPONSES,
    WATCHLIST_CREATE_RESPONSES,
    WATCHLIST_DETAIL_RESPONSES,
    WATCHLIST_UPDATE_RESPONSES,
    WATCHLIST_DELETE_RESPONSES,
    WATCHLIST_STOCK_CREATE_RESPONSES,
    WATCHLIST_STOCK_DELETE_RESPONSES,
    WATCHLIST_STOCK_LIST_RESPONSES,
)


# ==================== 请求模型 ====================


from app.api._monitoring_watchlists_models import (
    CreateWatchlistRequest,
    UpdateWatchlistRequest,
    AddStockRequest,
    WatchlistResponse,
    WatchlistStockResponse
)

_runtime_watchlists: Optional[List[WatchlistResponse]] = None
_runtime_watchlist_stocks: Optional[Dict[int, List[WatchlistStockResponse]]] = None

from app.api._monitoring_watchlists_models import (
    _runtime_fallback_enabled,
    _build_runtime_watchlist_stocks,
    _RUNTIME_FALLBACK_TIMESTAMP,
)


def get_monitoring_watchlists_postgres_async():
    from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

    return get_postgres_async()


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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[WatchlistResponse]:
    """
    创建监控清单

    - **name**: 清单名称
    - **watchlist_type**: 清单类型 (manual/strategy/benchmark)
    - **risk_profile**: 风控配置 (可选)
    """
    try:
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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[List[WatchlistResponse]]:
    """
    获取用户的所有监控清单
    """
    try:
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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[WatchlistResponse]:
    """
    获取单个监控清单详情
    """
    try:
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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[None]:
    """
    删除监控清单（级联删除成员）
    """
    try:
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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[WatchlistStockResponse]:
    """
    添加股票到清单
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import StockToAdd

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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[List[WatchlistStockResponse]]:
    """
    获取清单中的所有股票
    """
    try:
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
    postgres_async=Depends(get_monitoring_watchlists_postgres_async),
) -> UnifiedResponse[None]:
    """
    从清单中移除股票
    """
    try:
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
