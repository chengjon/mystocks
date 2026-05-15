"""
API契约管理模块
提供契约版本管理、差异检测、验证和同步功能
"""

from fastapi import APIRouter

from .impact_routes import router as impact_router
from .routes import router as legacy_router

router = APIRouter()
router.include_router(legacy_router)
router.include_router(impact_router)

__all__ = ["router"]
