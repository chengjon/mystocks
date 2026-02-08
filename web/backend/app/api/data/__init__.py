"""
数据查询 API (Facade)

Refactored to modular domain routers.
"""
from fastapi import APIRouter

# Import sub-routers
from .stocks import router as stocks_router
from .market import router as market_router
from .kline import router as kline_router
from .margin import router as margin_router
from .lhb import router as lhb_router
from .futures import router as futures_router
from .financial import router as financial_router

router = APIRouter(prefix="/api/v1/data", tags=["Data Service"])

# Include sub-routers
router.include_router(stocks_router)
router.include_router(market_router)
router.include_router(kline_router)
router.include_router(margin_router)
router.include_router(lhb_router)
router.include_router(futures_router)
router.include_router(financial_router)

__all__ = ["router"]
