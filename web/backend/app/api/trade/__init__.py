"""
交易管理API模块
"""

from fastapi import APIRouter

from .execution_tracking_routes import router as execution_tracking_router
from .reconciliation_routes import router as reconciliation_router
from .routes import router as trade_router

router = APIRouter()
router.include_router(trade_router)
router.include_router(execution_tracking_router)
router.include_router(reconciliation_router)

__all__ = ["router"]
