"""
止损扩展路由 (V3.1)
"""
import structlog
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from fastapi import APIRouter

from app.core.exceptions import BusinessException, NotFoundException, ValidationException

# 导入Week 4-5的新增组件
try:
    from src.governance.risk_management.services.stop_loss_execution_service import (
        get_stop_loss_execution_service,
    )
    from src.governance.risk_management.services.stop_loss_history_service import (
        get_stop_loss_history_service,
    )
    from src.governance.risk_management import get_risk_management_core

    ENHANCED_RISK_FEATURES_AVAILABLE = True
    RISK_MANAGEMENT_V31_AVAILABLE = True
except ImportError:
    ENHANCED_RISK_FEATURES_AVAILABLE = False
    RISK_MANAGEMENT_V31_AVAILABLE = False
    get_stop_loss_execution_service = None
    get_stop_loss_history_service = None
    get_risk_management_core = None

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.post("/stop-loss/add-position", response_model=Dict[str, Any])
async def add_stop_loss_position(request: Dict[str, Any]) -> Dict[str, Any]:
    """添加止损监控持仓 (V3.1)"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(detail="增强风险功能不可用", status_code=503)

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(detail="止损执行服务不可用", status_code=503)

        result = await execution_service.add_position_monitoring(
            symbol=request["symbol"],
            position_id=request["position_id"],
            entry_price=request["entry_price"],
            quantity=request["quantity"],
            stop_loss_type=request.get("stop_loss_type", "volatility_adaptive"),
            custom_stop_price=request.get("custom_stop_price"),
        )
        return result
    except Exception as e:
        logger.error(f"添加止损监控失败: {e}")
        raise BusinessException(detail=str(e), status_code=500)

@router.post("/stop-loss/update-price", response_model=Dict[str, Any])
async def update_stop_loss_price(request: Dict[str, Any]) -> Dict[str, Any]:
    """更新持仓价格并检查止损 (V3.1)"""
    try:
        execution_service = get_stop_loss_execution_service()
        result = await execution_service.update_position_price(
            position_id=request["position_id"],
            current_price=request["current_price"],
        )
        return result
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.delete("/stop-loss/remove-position/{position_id}", response_model=Dict[str, Any])
async def remove_stop_loss_position(position_id: str) -> Dict[str, Any]:
    """移除止损监控持仓 (V3.1)"""
    try:
        execution_service = get_stop_loss_execution_service()
        success = await execution_service.remove_position_monitoring(position_id)
        if not success:
            raise NotFoundException(resource="持仓", identifier=position_id)
        return {"success": True, "position_id": position_id}
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.get("/stop-loss/status/{position_id}", response_model=Dict[str, Any])
async def get_stop_loss_status(position_id: str) -> Dict[str, Any]:
    """获取止损监控状态 (V3.1)"""
    try:
        execution_service = get_stop_loss_execution_service()
        result = await execution_service.get_monitoring_status(position_id)
        return result
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.get("/stop-loss/overview", response_model=Dict[str, Any])
async def get_stop_loss_overview() -> Dict[str, Any]:
    """获取止损监控总览 (V3.1)"""
    try:
        execution_service = get_stop_loss_execution_service()
        result = await execution_service.get_monitoring_status()
        return result
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.post("/stop-loss/calculate")
async def calculate_stop_loss_v31(request: Dict[str, Any]) -> Dict[str, Any]:
    """V3.1 智能止损策略计算"""
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(detail="V3.1风险管理系统未初始化", status_code=503)

        core = get_risk_management_core()
        strategy_type = request.get("strategy_type", "volatility_adaptive")
        
        if strategy_type == "volatility_adaptive":
            result = await core.stop_loss_engine.calculate_volatility_stop_loss(
                symbol=request.get("symbol"), entry_price=request.get("entry_price"), k=request.get("k_factor", 2.0)
            )
        else:
            result = await core.stop_loss_engine.calculate_trailing_stop_loss(
                symbol=request.get("symbol"), highest_price=request.get("entry_price"), 
                trailing_percentage=request.get("trailing_percentage", 0.08)
            )
        return {"status": "success", "data": result}
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)
