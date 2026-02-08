"""
风险管理 API V3.1 - 扩展路由 (Facade)

Refactored to split routes into sub-modules.
"""
from fastapi import APIRouter
from .risk_v31.stop_loss import router as stop_loss_router
from .risk_v31.alerts import router as alerts_router
from .risk_v31.system import router as system_router

# 导入核心系统以支持 import 
from src.governance.risk_management import get_risk_management_core

router = APIRouter()

# 包含子路由，维持 v31 前缀
router.include_router(stop_loss_router, prefix="/v31")
router.include_router(alerts_router, prefix="/v31")
router.include_router(system_router, prefix="/v31")

__all__ = ["router", "get_risk_management_core"]