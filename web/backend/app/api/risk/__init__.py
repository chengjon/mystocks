from fastapi import APIRouter

from .metrics import router as metrics_router
from .stop_loss import router as stop_loss_router
from .alerts import router as alerts_router
from .v31 import router as v31_router

router = APIRouter()
router.include_router(metrics_router)
router.include_router(stop_loss_router)
router.include_router(alerts_router)
router.include_router(v31_router)

__all__ = ["router"]
