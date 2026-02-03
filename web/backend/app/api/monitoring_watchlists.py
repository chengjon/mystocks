#!/usr/bin/env python3
"""
监控清单管理 API
提供投资组合/观察列表的 CRUD 操作

API 端点:
- POST /api/monitoring/watchlists - 创建清单
- GET /api/monitoring/watchlists - 获取所有清单
- GET /api/monitoring/watchlists/{id} - 获取单个清单
- PUT /api/monitoring/watchlists/{id} - 更新清单
- DELETE /api/monitoring/watchlists/{id} - 删除清单
- POST /api/monitoring/watchlists/{id}/stocks - 添加股票
- DELETE /api/monitoring/watchlists/{id}/stocks/{code} - 移除股票

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field, field_validator

from app.core.exception_handlers import handle_exceptions
from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import UnifiedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring/watchlists", tags=["monitoring-watchlists"])


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


# ==================== API 端点 ====================


@router.post("", response_model=UnifiedResponse[WatchlistResponse])
@handle_exceptions
async def create_watchlist(
    request: CreateWatchlistRequest,
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
        logger.error("创建监控清单失败: %(e)s")
        raise BusinessException(detail=f"创建失败: {str(e)}", status_code=500, error_code="WATCHLIST_CREATION_FAILED")


@router.get("", response_model=UnifiedResponse[List[WatchlistResponse]])
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
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)

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
        logger.error("获取监控清单列表失败: %(e)s")
        raise BusinessException(detail=f"获取失败: {str(e)}", status_code=500, error_code="WATCHLIST_RETRIEVAL_FAILED")


@router.get("/{watchlist_id}", response_model=UnifiedResponse[WatchlistResponse])
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


@router.put("/{watchlist_id}", response_model=UnifiedResponse[WatchlistResponse])
@handle_exceptions
async def update_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    request: UpdateWatchlistRequest = None,
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[WatchlistResponse]:
    """
    更新监控清单
    """
    raise BusinessException(detail="更新功能待实现", status_code=501, error_code="FEATURE_NOT_IMPLEMENTED")


@router.delete("/{watchlist_id}", response_model=UnifiedResponse[None])
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


@router.post("/{watchlist_id}/stocks", response_model=UnifiedResponse[WatchlistStockResponse])
@handle_exceptions
async def add_stock_to_watchlist(
    watchlist_id: int = Path(..., description="清单ID"),
    request: AddStockRequest = None,
    user_id: int = Query(1, description="用户ID"),
) -> UnifiedResponse[WatchlistStockResponse]:
    """
    添加股票到清单
    """
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgres_async = get_postgres_async()

        if not postgres_async.is_connected():
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise NotFoundException(resource="监控清单", identifier="查询条件")

        stock_id = await postgres_async.add_stock_to_watchlist(
            watchlist_id=watchlist_id,
            stock_code=request.stock_code,
            entry_price=request.entry_price,
            entry_reason=request.entry_reason,
            stop_loss_price=request.stop_loss_price,
            target_price=request.target_price,
            weight=request.weight,
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
        logger.error("添加股票到清单失败: %(e)s")
        raise BusinessException(detail=f"添加失败: {str(e)}", status_code=500, error_code="STOCK_ADDITION_FAILED")


@router.get("/{watchlist_id}/stocks", response_model=UnifiedResponse[List[WatchlistStockResponse]])
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
            raise BusinessException(detail="数据库未连接", status_code=503, error_code="DATABASE_UNAVAILABLE")

        watchlists = await postgres_async.get_user_watchlists(user_id)
        watchlist = next((w for w in watchlists if w["id"] == watchlist_id), None)

        if not watchlist:
            raise NotFoundException(resource="监控清单", identifier="查询条件")

        stocks = await postgres_async.get_watchlist_stocks(watchlist_id)

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
        logger.error("获取清单股票列表失败: %(e)s")
        raise BusinessException(detail=f"获取失败: {str(e)}", status_code=500, error_code="WATCHLIST_RETRIEVAL_FAILED")


@router.delete("/{watchlist_id}/stocks/{stock_code}", response_model=UnifiedResponse[None])
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
        from src.monitoring.infrastructure.postgresql_async_v3 import MonitoringPostgreSQLAccess

        access = MonitoringPostgreSQLAccess()

        await access.remove_stock_from_watchlist(watchlist_id, stock_code)

        return UnifiedResponse(message="移除股票成功")

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        logger.error("从清单移除股票失败: %(e)s")
        raise BusinessException(detail=f"移除失败: {str(e)}", status_code=500, error_code="STOCK_REMOVAL_FAILED")
