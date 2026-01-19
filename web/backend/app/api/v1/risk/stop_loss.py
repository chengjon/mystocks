"""
止损管理 API - V3.1

提供智能止损功能:
- 止损监控持仓管理
- 止损价格更新和检查
- 止损策略历史表现分析
- 止损优化建议

Author: Claude Code
Version: 3.1.0
Date: 2026-01-10
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
import sys
import os

logger = structlog.get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

router = APIRouter(prefix="/api/v1/risk/stop-loss", tags=["止损管理"])

try:
    from src.governance.risk_management.services.stop_loss_execution_service import (
        get_stop_loss_execution_service,
    )
    from src.governance.risk_management.services.stop_loss_history_service import (
        get_stop_loss_history_service,
    )

    ENHANCED_RISK_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_RISK_FEATURES_AVAILABLE = False
    get_stop_loss_execution_service = None
    get_stop_loss_history_service = None


@router.post("/add-position", response_model=Dict[str, Any])
async def add_stop_loss_position(request: Dict[str, Any]) -> Dict[str, Any]:
    """添加止损监控持仓"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise HTTPException(status_code=503, detail="止损执行服务不可用")

        result = await execution_service.add_position_monitoring(
            symbol=request["symbol"],
            position_id=request["position_id"],
            entry_price=request["entry_price"],
            quantity=request["quantity"],
            stop_loss_type=request.get("stop_loss_type", "volatility_adaptive"),
            custom_stop_price=request.get("custom_stop_price"),
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "添加监控失败"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加止损监控失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加止损监控失败: {str(e)}")


@router.post("/update-price", response_model=Dict[str, Any])
async def update_stop_loss_price(request: Dict[str, Any]) -> Dict[str, Any]:
    """更新持仓价格并检查止损"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise HTTPException(status_code=503, detail="止损执行服务不可用")

        result = await execution_service.update_position_price(
            position_id=request["position_id"],
            current_price=request["current_price"],
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新止损价格失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新止损价格失败: {str(e)}")


@router.delete("/remove-position/{position_id}", response_model=Dict[str, Any])
async def remove_stop_loss_position(position_id: str) -> Dict[str, Any]:
    """移除止损监控持仓"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise HTTPException(status_code=503, detail="止损执行服务不可用")

        success = await execution_service.remove_position_monitoring(position_id)

        if not success:
            raise HTTPException(status_code=404, detail="持仓不存在或已移除")

        return {
            "success": True,
            "position_id": position_id,
            "message": "止损监控已移除",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除止损监控失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除止损监控失败: {str(e)}")


@router.get("/status/{position_id}", response_model=Dict[str, Any])
async def get_stop_loss_status(position_id: str) -> Dict[str, Any]:
    """获取止损监控状态"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise HTTPException(status_code=503, detail="止损执行服务不可用")

        result = await execution_service.get_monitoring_status(position_id)

        if not result.get("found"):
            raise HTTPException(status_code=404, detail="持仓不存在")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取止损状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取止损状态失败: {str(e)}")


@router.get("/overview", response_model=Dict[str, Any])
async def get_stop_loss_overview() -> Dict[str, Any]:
    """获取止损监控总览"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise HTTPException(status_code=503, detail="止损执行服务不可用")

        result = await execution_service.get_monitoring_status()
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取止损总览失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取止损总览失败: {str(e)}")


@router.post("/batch-update", response_model=Dict[str, Any])
async def batch_update_stop_loss_prices(request: Dict[str, Any]) -> Dict[str, Any]:
    """批量更新止损价格"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise HTTPException(status_code=503, detail="止损执行服务不可用")

        price_updates = request.get("price_updates", {})
        if not price_updates:
            raise HTTPException(status_code=400, detail="缺少价格更新数据")

        result = await execution_service.batch_update_prices(price_updates)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量更新止损价格失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新止损价格失败: {str(e)}")


@router.get("/history/performance", response_model=Dict[str, Any])
async def get_stop_loss_performance(
    strategy_type: Optional[str] = None, symbol: Optional[str] = None, days: int = 30
) -> Dict[str, Any]:
    """获取止损策略历史表现"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        history_service = get_stop_loss_history_service()
        if not history_service:
            raise HTTPException(status_code=503, detail="历史分析服务不可用")

        date_from = datetime.now() - timedelta(days=days)

        result = await history_service.get_strategy_performance(
            strategy_type=strategy_type,
            symbol=symbol,
            date_from=date_from,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取止损表现失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取止损表现失败: {str(e)}")


@router.get("/history/recommendations", response_model=Dict[str, Any])
async def get_stop_loss_recommendations(strategy_type: str, symbol: Optional[str] = None) -> Dict[str, Any]:
    """获取止损策略优化建议"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        history_service = get_stop_loss_history_service()
        if not history_service:
            raise HTTPException(status_code=503, detail="历史分析服务不可用")

        result = await history_service.get_strategy_recommendations(strategy_type, symbol)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取止损建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取止损建议失败: {str(e)}")
