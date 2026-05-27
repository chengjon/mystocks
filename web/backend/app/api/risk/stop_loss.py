from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.params import Depends as DependsParam

from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.openapi_config import COMMON_RESPONSES
from app.api.risk._shared import (
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


def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _resolve_history_service():
    history_service = get_stop_loss_history_service()
    if not history_service:
        raise BusinessException(detail="历史分析服务不可用", status_code=503, error_code="HISTORICAL_ANALYSIS_UNAVAILABLE")
    return history_service


def _resolve_execution_service():
    execution_service = get_stop_loss_execution_service()
    if not execution_service:
        raise BusinessException(detail="止损执行服务不可用", status_code=503, error_code="STOP_LOSS_EXECUTION_UNAVAILABLE")
    return execution_service


def get_stop_loss_history_service_provider():
    return _resolve_history_service()


def get_stop_loss_execution_service_provider():
    return _resolve_execution_service()


def _resolve_direct_call_dependency(service: Any, resolver):
    if isinstance(service, DependsParam):
        return resolver()
    return service


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

STOP_LOSS_ADD_POSITION_RESPONSE_EXAMPLE = {
    "success": True,
    "position_id": "pos-001",
    "stop_loss_price": 1590.0,
    "stop_loss_type": "volatility_adaptive",
    "monitoring_active": True,
}

STOP_LOSS_UPDATE_PRICE_RESPONSE_EXAMPLE = {
    "checked": True,
    "stop_loss_triggered": False,
    "current_price": 1662.5,
    "stop_loss_price": 1590.0,
    "distance_to_stop": 4.56,
    "position_id": "pos-001",
}

STOP_LOSS_REMOVE_POSITION_RESPONSE_EXAMPLE = {
    "success": True,
    "position_id": "pos-001",
    "message": "止损监控已移除",
}

STOP_LOSS_STATUS_RESPONSE_EXAMPLE = {
    "found": True,
    "position_id": "pos-001",
    "symbol": "600519.SH",
    "entry_price": 1688.0,
    "stop_loss_price": 1590.0,
    "stop_loss_type": "volatility_adaptive",
    "highest_price": None,
    "is_active": True,
    "last_check_time": "2026-04-08T11:25:00",
    "time_since_last_check": 18.4,
}

STOP_LOSS_OVERVIEW_RESPONSE_EXAMPLE = {
    "total_positions": 2,
    "active_positions": 2,
    "inactive_positions": 0,
    "execution_stats": {
        "total_positions_monitored": 2,
        "stop_loss_triggered": 1,
        "successful_executions": 1,
        "failed_executions": 0,
        "total_pnl_protected": 12500.0,
    },
    "positions": [
        {
            "position_id": "pos-001",
            "symbol": "600519.SH",
            "stop_loss_type": "volatility_adaptive",
            "is_active": True,
        },
        {
            "position_id": "pos-002",
            "symbol": "0700.HK",
            "stop_loss_type": "trailing_stop",
            "is_active": True,
        },
    ],
}

STOP_LOSS_BATCH_UPDATE_RESPONSE_EXAMPLE = {
    "total_checked": 2,
    "triggered_count": 1,
    "triggered_positions": ["pos-002"],
    "results": [
        {
            "checked": True,
            "stop_loss_triggered": False,
            "current_price": 1662.5,
            "stop_loss_price": 1590.0,
            "distance_to_stop": 4.56,
            "position_id": "pos-001",
        },
        {
            "checked": True,
            "stop_loss_triggered": True,
            "execution_result": {"success": True, "order_id": "sl-order-001"},
            "position_id": "pos-002",
        },
    ],
}

STOP_LOSS_PERFORMANCE_RESPONSE_EXAMPLE = {
    "total_trades": 18,
    "win_rate": 0.61,
    "total_pnl": 42800.0,
    "avg_pnl": 2377.78,
    "avg_win": 6120.0,
    "avg_loss": -3150.0,
    "max_profit": 11800.0,
    "max_loss": -6200.0,
    "profit_factor": 2.14,
    "win_loss_ratio": 1.94,
    "avg_holding_period_days": 6.2,
    "monthly_performance": {
        "2026-02": {"trades": 8, "pnl": 15400.0},
        "2026-03": {"trades": 10, "pnl": 27400.0},
    },
    "filters": {
        "strategy_type": "volatility_adaptive",
        "symbol": "600519.SH",
        "date_from": "2026-03-09T11:25:00",
        "date_to": None,
    },
    "generated_at": "2026-04-08T11:25:00",
}

STOP_LOSS_RECOMMENDATIONS_RESPONSE_EXAMPLE = {
    "recommendations": [
        "策略胜率中等，可以继续使用",
        "盈亏比较好，建议保持当前止损设置",
        "利润因子优秀，策略表现非常好",
    ],
    "performance_summary": {
        "win_rate": 0.61,
        "profit_factor": 2.14,
        "avg_holding_period": 6.2,
        "total_trades": 18,
    },
    "confidence": "high",
    "generated_at": "2026-04-08T11:25:00",
}

STOP_LOSS_CALCULATE_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "strategy_type": "volatility_adaptive_advanced",
        "entry_price": 1688.0,
        "stop_loss_price": 1590.0,
        "stop_percentage": 5.81,
        "base_atr_value": 14.4,
        "k_factor": 2.0,
        "market_adjustment": 1.02,
        "risk_tolerance": "medium",
        "use_dynamic_k": False,
        "risk_assessment": {"level": "medium", "score": 63},
        "execution_recommendation": "当前止损设置合理",
        "historical_analysis": {"max_drawdown_p95": 0.058},
        "calculated_at": "2026-04-08T11:25:00",
    },
    "strategy_type": "volatility_adaptive",
    "calculated_at": "2026-04-08T11:25:00",
    "version": "3.1",
}

STOP_LOSS_TRIGGER_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "triggered": True,
        "execution_result": {
            "symbol": "600519.SH",
            "triggered_at": "2026-04-08T11:25:00",
            "current_price": 1588.0,
            "stop_loss_price": 1590.0,
            "loss_amount": 2.0,
        },
        "symbol": "600519.SH",
        "current_price": 1588.0,
        "stop_loss_price": 1590.0,
    },
    "executed_at": "2026-04-08T11:25:00",
    "version": "3.1",
}

STOP_LOSS_ADD_POSITION_RESPONSES = _success_response_spec(
    "V3.1 止损监控持仓新增成功。", STOP_LOSS_ADD_POSITION_RESPONSE_EXAMPLE
)
STOP_LOSS_UPDATE_PRICE_RESPONSES = _success_response_spec(
    "V3.1 止损价格更新成功。", STOP_LOSS_UPDATE_PRICE_RESPONSE_EXAMPLE
)
STOP_LOSS_REMOVE_POSITION_RESPONSES = _success_response_spec(
    "V3.1 止损监控移除成功。", STOP_LOSS_REMOVE_POSITION_RESPONSE_EXAMPLE
)
STOP_LOSS_STATUS_RESPONSES = _success_response_spec(
    "V3.1 止损监控状态查询成功。", STOP_LOSS_STATUS_RESPONSE_EXAMPLE
)
STOP_LOSS_OVERVIEW_RESPONSES = _success_response_spec(
    "V3.1 止损监控总览查询成功。", STOP_LOSS_OVERVIEW_RESPONSE_EXAMPLE
)
STOP_LOSS_BATCH_UPDATE_RESPONSES = _success_response_spec(
    "V3.1 止损价格批量更新成功。", STOP_LOSS_BATCH_UPDATE_RESPONSE_EXAMPLE
)
STOP_LOSS_PERFORMANCE_RESPONSES = _success_response_spec(
    "V3.1 止损历史表现查询成功。", STOP_LOSS_PERFORMANCE_RESPONSE_EXAMPLE
)
STOP_LOSS_RECOMMENDATIONS_RESPONSES = _success_response_spec(
    "V3.1 止损策略建议生成成功。", STOP_LOSS_RECOMMENDATIONS_RESPONSE_EXAMPLE
)
STOP_LOSS_CALCULATE_RESPONSES = _success_response_spec(
    "V3.1 止损位计算成功。", STOP_LOSS_CALCULATE_RESPONSE_EXAMPLE
)
STOP_LOSS_TRIGGER_RESPONSES = _success_response_spec(
    "V3.1 止损触发检查成功。", STOP_LOSS_TRIGGER_RESPONSE_EXAMPLE
)


@router.post(
    "/v31/stop-loss/add-position",
    response_model=Dict[str, Any],
    summary="新增 V3.1 止损监控",
    description="新增一个止损监控持仓，并为该持仓配置 V3.1 风险管理引擎使用的止损参数。",
    responses=STOP_LOSS_ADD_POSITION_RESPONSES,
)
async def add_stop_loss_position(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_ADD_POSITION_EXAMPLES),
    execution_service: Any = Depends(get_stop_loss_execution_service_provider),
) -> Dict[str, Any]:
    try:
        execution_service = _resolve_direct_call_dependency(execution_service, _resolve_execution_service)

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
    summary="更新 V3.1 止损价格",
    description="更新指定止损监控持仓的最新价格，并立即执行一次止损条件检查。",
    responses=STOP_LOSS_UPDATE_PRICE_RESPONSES,
)
async def update_stop_loss_price(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_UPDATE_PRICE_EXAMPLES),
    execution_service: Any = Depends(get_stop_loss_execution_service_provider),
) -> Dict[str, Any]:
    try:
        execution_service = _resolve_direct_call_dependency(execution_service, _resolve_execution_service)

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
    summary="移除 V3.1 止损监控",
    description="移除指定止损监控持仓，并停止后续对该持仓执行自动止损检查。",
    responses=STOP_LOSS_REMOVE_POSITION_RESPONSES,
)
async def remove_stop_loss_position(
    position_id: str = Path(..., description="需要移除的止损监控持仓ID。"),
    execution_service: Any = Depends(get_stop_loss_execution_service_provider),
) -> Dict[str, Any]:
    try:
        execution_service = _resolve_direct_call_dependency(execution_service, _resolve_execution_service)

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
    summary="查询 V3.1 止损状态",
    description="查询指定持仓的 V3.1 止损监控状态，包括当前止损参数与命中情况。",
    responses=STOP_LOSS_STATUS_RESPONSES,
)
async def get_stop_loss_status(
    position_id: str = Path(..., description="需要查询止损状态的持仓ID。"),
    execution_service: Any = Depends(get_stop_loss_execution_service_provider),
) -> Dict[str, Any]:
    try:
        execution_service = _resolve_direct_call_dependency(execution_service, _resolve_execution_service)

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
    summary="查询 V3.1 止损总览",
    description="获取当前全部止损监控持仓的总览信息，用于盘中风控看板或批量巡检。",
    responses=STOP_LOSS_OVERVIEW_RESPONSES,
)
async def get_stop_loss_overview(
    execution_service: Any = Depends(get_stop_loss_execution_service_provider),
) -> Dict[str, Any]:
    try:
        execution_service = _resolve_direct_call_dependency(execution_service, _resolve_execution_service)

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
    summary="批量更新 V3.1 止损价格",
    description="批量更新多个止损监控持仓的市场价格，适用于盘中统一刷新止损监控状态。",
    responses=STOP_LOSS_BATCH_UPDATE_RESPONSES,
)
async def batch_update_stop_loss_prices(
    request: Dict[str, Any] = Body(..., openapi_examples=STOP_LOSS_BATCH_UPDATE_EXAMPLES),
    execution_service: Any = Depends(get_stop_loss_execution_service_provider),
) -> Dict[str, Any]:
    try:
        execution_service = _resolve_direct_call_dependency(execution_service, _resolve_execution_service)

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
    summary="查询 V3.1 止损历史表现",
    description="按策略类型、股票和时间窗口查询 V3.1 止损历史表现与执行效果统计。",
    responses=STOP_LOSS_PERFORMANCE_RESPONSES,
)
async def get_stop_loss_performance(
    strategy_type: Optional[str] = Query(None, description="可选的止损策略类型，用于筛选指定策略表现。"),
    symbol: Optional[str] = Query(None, description="可选的股票代码，用于筛选单一标的止损表现。"),
    days: int = Query(30, description="回溯统计的天数窗口，默认 30 天。"),
    history_service: Any = Depends(get_stop_loss_history_service_provider),
) -> Dict[str, Any]:
    try:
        history_service = _resolve_direct_call_dependency(history_service, _resolve_history_service)

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
    summary="获取 V3.1 止损建议",
    description="基于指定止损策略的历史执行结果，生成后续参数优化与使用建议。",
    responses=STOP_LOSS_RECOMMENDATIONS_RESPONSES,
)
async def get_stop_loss_recommendations(
    strategy_type: str = Query(..., description="用于生成推荐结论的止损策略类型。"),
    symbol: Optional[str] = Query(None, description="可选的股票代码，用于生成单一标的建议。"),
    history_service: Any = Depends(get_stop_loss_history_service_provider),
) -> Dict[str, Any]:
    try:
        history_service = _resolve_direct_call_dependency(history_service, _resolve_history_service)

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
    summary="计算 V3.1 止损位",
    description="按指定的 V3.1 止损策略参数计算建议止损位，并返回带版本标记的计算结果。",
    responses=STOP_LOSS_CALCULATE_RESPONSES,
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
        symbol = request.get("symbol")
        entry_price = request.get("entry_price")

        if not symbol:
            raise ValidationException(detail="缺少必要参数: symbol", field="symbol")
        if entry_price is None:
            raise ValidationException(detail="缺少必要参数: entry_price", field="entry_price")

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
    summary="触发 V3.1 止损检查",
    description="基于当前价格和止损价手动触发一次 V3.1 止损检查，并返回执行结果明细。",
    responses=STOP_LOSS_TRIGGER_RESPONSES,
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
