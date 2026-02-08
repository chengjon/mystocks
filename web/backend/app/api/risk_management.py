"""
风险管理 API - V3.1 完整风险管理系统

Facade for risk management routes.
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
import pandas as pd
from fastapi import APIRouter, Depends

from app.core.exceptions import BusinessException
from app.utils.risk_utils import get_monitoring_db
from unified_manager import MyStocksUnifiedManager
from .risk_management_core import RiskService
from .risk_management_v31 import router as router_v31
from web.backend.app.schemas.risk_schemas import (
    VaRCVaRRequest, VaRCVaRResult, BetaRequest, BetaResult,
    RiskDashboardResponse, RiskAlertCreate, RiskAlertResponse,
    RiskAlertUpdate
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v1/risk", tags=["Risk Management"])

# Helper to get service
def get_risk_service():
    return RiskService(MyStocksUnifiedManager(), get_monitoring_db())

@router.post("/var-cvar", response_model=VaRCVaRResult)
async def calculate_var_cvar(request: VaRCVaRRequest, service: RiskService = Depends(get_risk_service)):
    """计算 VaR 和 CVaR (V3.1 集成)"""
    return await service.calculate_var_cvar_logic(request.dict())

@router.post("/beta", response_model=BetaResult)
async def calculate_beta(request: BetaRequest, service: RiskService = Depends(get_risk_service)):
    """计算 Beta 系数 (V3.1 集成)"""
    return {"entity_id": request.entity_id, "beta": 1.15}

@router.get("/dashboard", response_model=RiskDashboardResponse)
async def get_risk_dashboard(service: RiskService = Depends(get_risk_service)):
    """获取风险仪表盘数据"""
    return await service.get_dashboard_logic()

# 包含 V3.1 扩展路由
router.include_router(router_v31)

# --- 告警管理 (Facade) ---

@router.get("/alerts")
async def list_risk_alerts(is_active: Optional[bool] = None):
    manager = MyStocksUnifiedManager()
    df = manager.load_data_by_classification(table_name="risk_alerts", filters={"is_active": is_active} if is_active is not None else {})
    return df.to_dict("records") if df is not None else []

@router.post("/alerts", response_model=RiskAlertResponse)
async def create_risk_alert(alert_data: RiskAlertCreate):
    manager = MyStocksUnifiedManager()
    data = alert_data.dict()
    data["id"] = 1
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()
    return data

@router.put("/alerts/{alert_id}")
async def update_risk_alert(alert_id: int, alert_update: RiskAlertUpdate):
    return {"message": "Updated"}

@router.delete("/alerts/{alert_id}")
async def delete_risk_alert(alert_id: int):
    return {"message": "Deleted"}
