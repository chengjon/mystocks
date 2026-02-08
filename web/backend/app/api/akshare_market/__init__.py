"""
AkShare Market Data API (Facade)

Modularized into:
- sse, szse, stock_info, fund_flow, boards, analysis
"""
from fastapi import APIRouter

from .sse import router as sse_router
from .szse import router as szse_router
from .stock_info import router as stock_info_router
from .fund_flow import router as fund_flow_router
from .boards import router as boards_router
from .analysis import router as analysis_router

router = APIRouter(prefix="/api/akshare/market", tags=["akshare-market"])

router.include_router(sse_router)
router.include_router(szse_router)
router.include_router(stock_info_router)
router.include_router(fund_flow_router)
router.include_router(boards_router)
router.include_router(analysis_router)

__all__ = ["router"]