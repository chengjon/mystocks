from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Path, Query

from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.openapi_config import COMMON_RESPONSES
from app.api.risk._shared import (
    ENHANCED_RISK_FEATURES_AVAILABLE,
    RISK_MANAGEMENT_V31_AVAILABLE,
    get_risk_management_core,
    get_stop_loss_execution_service,
    get_stop_loss_history_service,
    logger,
)

RISK_STOP_LOSS_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "止损增强服务不可用或尚未初始化",
    },
}

router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-止损"], responses=RISK_STOP_LOSS_ROUTE_RESPONSES)

STOP_LOSS_ADD_POSITION_EXAMPLES = {
    "monitor_equity_position": {
        "summary": "添加股票止损监控",
        "value": {
            "symbol": "600519.SH",
            "position_id": "pos-001",
            "entry_price": 1688.0,
            "quantity": 100,
            "stop_loss_type": "volatility_adaptive",
            "custom_stop_price": 1590.0,
        },
    }
}

STOP_LOSS_UPDATE_PRICE_EXAMPLES = {
    "update_market_price": {
        "summary": "更新持仓现价",
        "value": {
            "position_id": "pos-001",
            "current_price": 1662.5,
        },
    }
}

STOP_LOSS_BATCH_UPDATE_EXAMPLES = {
    "batch_price_refresh": {
        "summary": "批量刷新价格",
        "value": {
            "price_updates": {
                "pos-001": 1662.5,
                "pos-002": 24.18,
            }
        },
    }
}

STOP_LOSS_CALCULATE_EXAMPLES = {
    "volatility_stop": {
        "summary": "计算波动率止损",
        "value": {
            "strategy_type": "volatility_adaptive",
            "symbol": "600519.SH",
            "entry_price": 1688.0,
            "k_factor": 2.0,
        },
    }
}

STOP_LOSS_TRIGGER_EXAMPLES = {
    "manual_trigger_check": {
        "summary": "手动执行止损检查",
        "value": {
            "symbol": "600519.SH",
            "current_price": 1588.0,
            "stop_loss_price": 1590.0,
        },
    }
}


@router.post(
    "/v31/stop-loss/add-position",
    response_model=Dict[str, Any],
    description="新增一个止损监控持仓，并为该持仓配置 V3.1 风险管理引擎使用的止损参数。",
)
async def add_stop_loss_position(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_ADD_POSITION_EXAMPLES)
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE"
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
                detail=result.get("error", "添加监控失败"), status_code=400, error_code="MONITORING_ADDITION_FAILED"
            )
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("添加止损监控失败: %(e)s")
        raise BusinessException(
            detail=f"添加止损监控失败: {str(e)}", status_code=500, error_code="STOP_LOSS_MONITORING_ADDITION_FAILED"
        )


@router.post(
    "/v31/stop-loss/update-price",
    response_model=Dict[str, Any],
    description="更新指定止损监控持仓的最新价格，并立即执行一次止损条件检查。",
)
async def update_stop_loss_price(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_UPDATE_PRICE_EXAMPLES)
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE"
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
            detail=f"更新止损价格失败: {str(e)}", status_code=500, error_code="STOP_LOSS_PRICE_UPDATE_FAILED"
        )


@router.delete(
    "/v31/stop-loss/remove-position/{position_id}",
    response_model=Dict[str, Any],
    description="移除指定止损监控持仓，并停止后续对该持仓执行自动止损检查。",
)
async def remove_stop_loss_position(
    position_id: str = Path(..., description="需要移除的止损监控持仓ID。"),
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE"
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
            detail=f"移除止损监控失败: {str(e)}", status_code=500, error_code="STOP_LOSS_MONITORING_REMOVAL_FAILED"
        )


@router.get(
    "/v31/stop-loss/status/{position_id}",
    response_model=Dict[str, Any],
    description="查询指定持仓的 V3.1 止损监控状态，包括当前止损参数与命中情况。",
)
async def get_stop_loss_status(
    position_id: str = Path(..., description="需要查询止损状态的持仓ID。"),
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE"
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
            detail=f"获取止损状态失败: {str(e)}", status_code=500, error_code="STOP_LOSS_STATUS_RETRIEVAL_FAILED"
        )


@router.get(
    "/v31/stop-loss/overview",
    response_model=Dict[str, Any],
    description="获取当前全部止损监控持仓的总览信息，用于盘中风控看板或批量巡检。",
)
async def get_stop_loss_overview() -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE"
            )

        return await execution_service.get_monitoring_status()

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取止损总览失败: %(e)s")
        raise BusinessException(
            detail=f"获取止损总览失败: {str(e)}", status_code=500, error_code="STOP_LOSS_OVERVIEW_RETRIEVAL_FAILED"
        )


@router.post(
    "/v31/stop-loss/batch-update",
    response_model=Dict[str, Any],
    description="批量更新多个止损监控持仓的市场价格，适用于盘中统一刷新止损监控状态。",
)
async def batch_update_stop_loss_prices(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_BATCH_UPDATE_EXAMPLES)
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        execution_service = get_stop_loss_execution_service()
        if not execution_service:
            raise BusinessException(
                detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE"
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
            detail=f"批量更新止损价格失败: {str(e)}", status_code=500, error_code="BATCH_STOP_LOSS_UPDATE_FAILED"
        )


@router.get(
    "/v31/stop-loss/history/performance",
    response_model=Dict[str, Any],
    description="按策略类型、股票和时间窗口查询 V3.1 止损历史表现与执行效果统计。",
)
async def get_stop_loss_performance(
    strategy_type: Optional[str] = Query(None, description="可选的止损策略类型，用于筛选指定策略表现。"),
    symbol: Optional[str] = Query(None, description="可选的股票代码，用于筛选单一标的止损表现。"),
    days: int = Query(30, description="回溯统计的天数窗口，默认 30 天。"),
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        history_service = get_stop_loss_history_service()
        if not history_service:
            raise BusinessException(
                detail="历史分析服务不可用", status_code=503, error_code="HISTORICAL_ANALYSIS_UNAVAILABLE"
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
            detail=f"获取止损表现失败: {str(e)}", status_code=500, error_code="STOP_LOSS_PERFORMANCE_RETRIEVAL_FAILED"
        )


@router.get(
    "/v31/stop-loss/history/recommendations",
    response_model=Dict[str, Any],
    description="基于指定止损策略的历史执行结果，生成后续参数优化与使用建议。",
)
async def get_stop_loss_recommendations(
    strategy_type: str = Query(..., description="用于生成推荐结论的止损策略类型。"),
    symbol: Optional[str] = Query(None, description="可选的股票代码，用于生成单一标的建议。"),
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        history_service = get_stop_loss_history_service()
        if not history_service:
            raise BusinessException(
                detail="历史分析服务不可用", status_code=503, error_code="HISTORICAL_ANALYSIS_UNAVAILABLE"
            )

        return await history_service.get_strategy_recommendations(strategy_type, symbol)

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取止损建议失败: %(e)s")
        raise BusinessException(
            detail=f"获取止损建议失败: {str(e)}", status_code=500, error_code="STOP_LOSS_SUGGESTIONS_RETRIEVAL_FAILED"
        )


@router.post(
    "/v31/stop-loss/calculate",
    description="按指定的 V3.1 止损策略参数计算建议止损位，并返回带版本标记的计算结果。",
)
async def calculate_stop_loss_v31(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_CALCULATE_EXAMPLES)
) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        core = get_risk_management_core()
        if not core or not core.stop_loss_engine:
            raise BusinessException(detail="止损引擎不可用", status_code=503, error_code="STOP_LOSS_ENGINE_UNAVAILABLE")

        strategy_type = request.get("strategy_type", "volatility_adaptive")
        symbol = request.get("symbol", "placeholder")
        entry_price = request.get("entry_price", 100.0)

        if strategy_type == "volatility_adaptive":
            result = await core.stop_loss_engine.calculate_volatility_stop_loss(
                symbol=symbol, entry_price=entry_price, k=request.get("k_factor", 2.0)
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
            detail=f"止损计算失败: {str(e)}", status_code=500, error_code="STOP_LOSS_CALCULATION_FAILED"
        )


@router.post(
    "/v31/stop-loss/trigger",
    description="基于当前价格和止损价手动触发一次 V3.1 止损检查，并返回执行结果明细。",
)
async def trigger_stop_loss_v31(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_TRIGGER_EXAMPLES)
) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        core = get_risk_management_core()
        if not core:
            raise BusinessException(
                detail="风险管理核心不可用", status_code=503, error_code="RISK_MANAGEMENT_CORE_UNAVAILABLE"
            )

        symbol = request.get("symbol")
        current_price = request.get("current_price")
        stop_loss_price = request.get("stop_loss_price")

        if not all([symbol, current_price, stop_loss_price]):
            raise ValidationException(detail="缺少必要参数: symbol, current_price, stop_loss_price", field="parameters")

        triggered, execution_result = await core.execute_stop_loss_check(
            symbol, current_price, {"stop_loss_price": stop_loss_price}
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
            detail=f"止损执行失败: {str(e)}", status_code=500, error_code="STOP_LOSS_EXECUTION_FAILED"
        )
