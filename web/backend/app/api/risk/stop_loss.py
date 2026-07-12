from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter

from app.api.risk._shared import (
    ENHANCED_RISK_FEATURES_AVAILABLE,
    RISK_MANAGEMENT_V31_AVAILABLE,
    get_risk_management_core,
    get_stop_loss_execution_service,
    get_stop_loss_history_service,
    logger,
)
from app.core.exceptions import BusinessException, NotFoundException, ValidationException


router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-止损"])


@router.post("/v31/stop-loss/add-position", response_model=Dict[str, Any])
async def add_stop_loss_position(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE",
            )

        result = await execution_service.add_position_monitoring(
            symbol=request["symbol"],
            position_id=request["position_id"],
            entry_price=request["entry_price"],
            quantity=request["quantity"],
            stop_loss_type=request.get("stop_loss_type", "volatility_adaptive"),
            custom_stop_price=request.get("custom_stop_price"),
        )

        if not result["success"]:
            raise BusinessException(
                detail=result.get("error", "添加监控失败"), status_code=400, error_code="MONITORING_ADDITION_FAILED",
            )
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("添加止损监控失败: %(e)s")
        raise BusinessException(
            detail=f"添加止损监控失败: {e!s}", status_code=500, error_code="STOP_LOSS_MONITORING_ADDITION_FAILED",
        )


@router.post("/v31/stop-loss/update-price", response_model=Dict[str, Any])
async def update_stop_loss_price(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE",
            )

        result = await execution_service.update_position_price(
            position_id=request["position_id"],
            current_price=request["current_price"],
        )
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("更新止损价格失败: %(e)s")
        raise BusinessException(
            detail=f"更新止损价格失败: {e!s}", status_code=500, error_code="STOP_LOSS_PRICE_UPDATE_FAILED",
        )


@router.delete("/v31/stop-loss/remove-position/{position_id}", response_model=Dict[str, Any])
async def remove_stop_loss_position(position_id: str) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE",
            )

        success = await execution_service.remove_position_monitoring(position_id)
        if not success:
            raise NotFoundException(resource="持仓", identifier="查询条件")
        return {"success": True, "position_id": position_id, "message": "止损监控已移除"}

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("移除止损监控失败: %(e)s")
        raise BusinessException(
            detail=f"移除止损监控失败: {e!s}", status_code=500, error_code="STOP_LOSS_MONITORING_REMOVAL_FAILED",
        )


@router.get("/v31/stop-loss/status/{position_id}", response_model=Dict[str, Any])
async def get_stop_loss_status(position_id: str) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE",
            )

        result = await execution_service.get_monitoring_status(position_id)
        if not result.get("found"):
            raise NotFoundException(resource="持仓", identifier="查询条件")
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取止损状态失败: %(e)s")
        raise BusinessException(
            detail=f"获取止损状态失败: {e!s}", status_code=500, error_code="STOP_LOSS_STATUS_RETRIEVAL_FAILED",
        )


@router.get("/v31/stop-loss/overview", response_model=Dict[str, Any])
async def get_stop_loss_overview() -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE",
            )

        return await execution_service.get_monitoring_status()

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取止损总览失败: %(e)s")
        raise BusinessException(
            detail=f"获取止损总览失败: {e!s}", status_code=500, error_code="STOP_LOSS_OVERVIEW_RETRIEVAL_FAILED",
        )


@router.post("/v31/stop-loss/batch-update", response_model=Dict[str, Any])
async def batch_update_stop_loss_prices(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE",
            )

        price_updates = request.get("price_updates", {})
        if not price_updates:
            raise ValidationException(detail="缺少价格更新数据", field="price_update_data")

        return await execution_service.batch_update_prices(price_updates)

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("批量更新止损价格失败: %(e)s")
        raise BusinessException(
            detail=f"批量更新止损价格失败: {e!s}", status_code=500, error_code="BATCH_STOP_LOSS_UPDATE_FAILED",
        )


@router.get("/v31/stop-loss/history/performance", response_model=Dict[str, Any])
async def get_stop_loss_performance(
    strategy_type: Optional[str] = None, symbol: Optional[str] = None, days: int = 30,
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        history_service = get_stop_loss_history_service()
        if not history_service:
            raise BusinessException(
                detail="历史分析服务不可用", status_code=503, error_code="HISTORICAL_ANALYSIS_UNAVAILABLE",
            )

        date_from = datetime.now() - timedelta(days=days)
        return await history_service.get_strategy_performance(
            strategy_type=strategy_type,
            symbol=symbol,
            date_from=date_from,
        )

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取止损表现失败: %(e)s")
        raise BusinessException(
            detail=f"获取止损表现失败: {e!s}", status_code=500, error_code="STOP_LOSS_PERFORMANCE_RETRIEVAL_FAILED",
        )


@router.get("/v31/stop-loss/history/recommendations", response_model=Dict[str, Any])
async def get_stop_loss_recommendations(strategy_type: str, symbol: Optional[str] = None) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE",
            )

        history_service = get_stop_loss_history_service()
        if not history_service:
            raise BusinessException(
                detail="历史分析服务不可用", status_code=503, error_code="HISTORICAL_ANALYSIS_UNAVAILABLE",
            )

        return await history_service.get_strategy_recommendations(strategy_type, symbol)

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取止损建议失败: %(e)s")
        raise BusinessException(
            detail=f"获取止损建议失败: {e!s}", status_code=500, error_code="STOP_LOSS_SUGGESTIONS_RETRIEVAL_FAILED",
        )


@router.post("/v31/stop-loss/calculate")
async def calculate_stop_loss_v31(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED",
            )

        core = get_risk_management_core()
        if not core or not core.stop_loss_engine:
            raise BusinessException(detail="止损引擎不可用", status_code=503, error_code="STOP_LOSS_ENGINE_UNAVAILABLE")

        strategy_type = request.get("strategy_type", "volatility_adaptive")
        symbol = request.get("symbol", "placeholder")
        entry_price = request.get("entry_price", 100.0)

        if strategy_type == "volatility_adaptive":
            result = await core.stop_loss_engine.calculate_volatility_stop_loss(
                symbol=symbol, entry_price=entry_price, k=request.get("k_factor", 2.0),
            )
        elif strategy_type == "trailing_stop":
            result = await core.stop_loss_engine.calculate_trailing_stop_loss(
                symbol=symbol,
                highest_price=entry_price,
                trailing_percentage=request.get("trailing_percentage", 0.08),
            )
        else:
            raise ValidationException(detail=f"不支持的止损策略类型: {strategy_type}", field="strategy_type")

        return {
            "status": "success",
            "data": result,
            "strategy_type": strategy_type,
            "calculated_at": datetime.now().isoformat(),
            "version": "3.1",
        }

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        logger.error("V3.1止损计算失败: %(e)s")
        raise BusinessException(
            detail=f"止损计算失败: {e!s}", status_code=500, error_code="STOP_LOSS_CALCULATION_FAILED",
        )


@router.post("/v31/stop-loss/trigger")
async def trigger_stop_loss_v31(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED",
            )

        core = get_risk_management_core()
        if not core:
            raise BusinessException(
                detail="风险管理核心不可用", status_code=503, error_code="RISK_MANAGEMENT_CORE_UNAVAILABLE",
            )

        symbol = request.get("symbol")
        current_price = request.get("current_price")
        stop_loss_price = request.get("stop_loss_price")

        if not all([symbol, current_price, stop_loss_price]):
            raise ValidationException(detail="缺少必要参数: symbol, current_price, stop_loss_price", field="parameters")

        triggered, execution_result = await core.execute_stop_loss_check(
            symbol, current_price, {"stop_loss_price": stop_loss_price},
        )

        return {
            "status": "success",
            "data": {
                "triggered": triggered,
                "execution_result": execution_result,
                "symbol": symbol,
                "current_price": current_price,
                "stop_loss_price": stop_loss_price,
            },
            "executed_at": datetime.now().isoformat(),
            "version": "3.1",
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("V3.1止损执行失败: %(e)s")
        raise BusinessException(
            detail=f"止损执行失败: {e!s}", status_code=500, error_code="STOP_LOSS_EXECUTION_FAILED",
        )
