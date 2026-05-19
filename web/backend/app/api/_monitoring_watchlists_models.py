"""Extracted from monitoring_watchlists."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

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


import os

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

