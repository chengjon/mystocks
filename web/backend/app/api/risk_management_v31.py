"""
风险管理 API V3.1 - 扩展路由

包含 V3.1 完整风险管理系统的 API 端点。
从 risk_management.py 拆分。

Author: Claude Code
Date: 2026-02-08
"""

import asyncio
import json
import structlog
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from unified_manager import MyStocksUnifiedManager
from src.core import DataClassification

# 导入工具
from app.utils.risk_utils import (
    connection_manager,
    ConnectionManager
)

logger = structlog.get_logger(__name__)

# 导入新的完整风险管理系统
try:
    from src.governance.risk_management import (
        get_risk_management_core,
        initialize_risk_management_system,
    )

    RISK_MANAGEMENT_V31_AVAILABLE = True
except ImportError:
    RISK_MANAGEMENT_V31_AVAILABLE = False
    get_risk_management_core = None
    initialize_risk_management_system = None

# 导入Week 4-5的新增组件
try:
    from src.governance.risk_management.services.alert_rule_engine import (
        AlertContext,
        get_alert_rule_engine,
    )
    from src.governance.risk_management.services.risk_alert_notification_manager import (
        get_risk_alert_notification_manager,
    )
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
    get_risk_alert_notification_manager = None
    get_alert_rule_engine = None
    AlertContext = None

router = APIRouter()

# ===== Week 5 新增API端点 =====


@router.post("/v31/stop-loss/add-position", response_model=Dict[str, Any])
async def add_stop_loss_position(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    添加止损监控持仓 (V3.1)

    为指定持仓添加止损监控，支持波动率自适应和跟踪止损两种策略。
    """
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
        logger.error(f"添加止损监控失败: {e}")
        raise BusinessException(
            detail=f"添加止损监控失败: {str(e)}", status_code=500, error_code="STOP_LOSS_MONITORING_ADDITION_FAILED"
        )


@router.post("/v31/stop-loss/update-price", response_model=Dict[str, Any])
async def update_stop_loss_price(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新持仓价格并检查止损 (V3.1)

    更新指定持仓的价格，自动检查是否触发止损条件。
    """
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
        logger.error(f"更新止损价格失败: {e}")
        raise BusinessException(
            detail=f"更新止损价格失败: {str(e)}", status_code=500, error_code="STOP_LOSS_PRICE_UPDATE_FAILED"
        )


@router.delete("/v31/stop-loss/remove-position/{position_id}", response_model=Dict[str, Any])
async def remove_stop_loss_position(position_id: str) -> Dict[str, Any]:
    """
    移除止损监控持仓 (V3.1)

    移除指定持仓的止损监控。
    """
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
        logger.error(f"移除止损监控失败: {e}")
        raise BusinessException(
            detail=f"移除止损监控失败: {str(e)}", status_code=500, error_code="STOP_LOSS_MONITORING_REMOVAL_FAILED"
        )


@router.get("/v31/stop-loss/status/{position_id}", response_model=Dict[str, Any])
async def get_stop_loss_status(position_id: str) -> Dict[str, Any]:
    """
    获取止损监控状态 (V3.1)

    获取指定持仓的止损监控状态信息。
    """
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
        logger.error(f"获取止损状态失败: {e}")
        raise BusinessException(
            detail=f"获取止损状态失败: {str(e)}", status_code=500, error_code="STOP_LOSS_STATUS_RETRIEVAL_FAILED"
        )


@router.get("/v31/stop-loss/overview", response_model=Dict[str, Any])
async def get_stop_loss_overview() -> Dict[str, Any]:
    """
    获取止损监控总览 (V3.1)

    获取所有持仓的止损监控总览信息。
    """
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

        result = await execution_service.get_monitoring_status()
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"获取止损总览失败: {e}")
        raise BusinessException(
            detail=f"获取止损总览失败: {str(e)}", status_code=500, error_code="STOP_LOSS_OVERVIEW_RETRIEVAL_FAILED"
        )


@router.post("/v31/stop-loss/batch-update", response_model=Dict[str, Any])
async def batch_update_stop_loss_prices(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    批量更新止损价格 (V3.1)

    批量更新多个股票的价格，并检查所有监控持仓的止损条件。
    """
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

        result = await execution_service.batch_update_prices(price_updates)
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"批量更新止损价格失败: {e}")
        raise BusinessException(
            detail=f"批量更新止损价格失败: {str(e)}", status_code=500, error_code="BATCH_STOP_LOSS_UPDATE_FAILED"
        )


@router.get("/v31/stop-loss/history/performance", response_model=Dict[str, Any])
async def get_stop_loss_performance(
    strategy_type: Optional[str] = None, symbol: Optional[str] = None, days: int = 30
) -> Dict[str, Any]:
    """
    获取止损策略历史表现 (V3.1)

    获取指定时间范围内的止损策略表现分析。
    """
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

        result = await history_service.get_strategy_performance(
            strategy_type=strategy_type,
            symbol=symbol,
            date_from=date_from,
        )

        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"获取止损表现失败: {e}")
        raise BusinessException(
            detail=f"获取止损表现失败: {str(e)}", status_code=500, error_code="STOP_LOSS_PERFORMANCE_RETRIEVAL_FAILED"
        )


@router.get("/v31/stop-loss/history/recommendations", response_model=Dict[str, Any])
async def get_stop_loss_recommendations(strategy_type: str, symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    获取止损策略优化建议 (V3.1)

    基于历史表现提供止损策略优化建议。
    """
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

        result = await history_service.get_strategy_recommendations(strategy_type, symbol)
        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"获取止损建议失败: {e}")
        raise BusinessException(
            detail=f"获取止损建议失败: {str(e)}", status_code=500, error_code="STOP_LOSS_SUGGESTIONS_RETRIEVAL_FAILED"
        )


@router.post("/v31/alert/send", response_model=Dict[str, Any])
async def send_risk_alert(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    发送风险告警 (V3.1)

    通过增强的告警通知管理器发送风险告警。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        notification_manager = get_risk_alert_notification_manager()
        if not notification_manager:
            raise BusinessException(
                detail="告警通知管理器不可用", status_code=503, error_code="ALERT_NOTIFICATION_MANAGER_UNAVAILABLE"
            )

        alert_type = request.get("alert_type", "general_risk")
        severity = request.get("severity", "warning")
        message = request.get("message", "")
        metrics = request.get("metrics", {})
        context = request.get("context", {})

        # 发送个股风险告警
        if "symbol" in request:
            result = await notification_manager.send_stock_risk_alert(
                symbol=request["symbol"],
                risk_level=severity,
                risk_metrics=metrics,
                alert_triggers=request.get("alert_triggers", []),
            )
        # 发送组合风险告警
        elif "portfolio_id" in request:
            triggered_alerts = request.get("triggered_alerts", [])
            result = await notification_manager.send_portfolio_risk_alert(
                portfolio_id=request["portfolio_id"],
                risk_level=severity,
                risk_metrics=metrics,
                triggered_alerts=triggered_alerts,
            )
        # 发送通用风险告警
        else:
            result = await notification_manager.send_risk_alert(
                alert_type=alert_type,
                severity=severity,
                message=message,
                metrics=metrics,
                context=context,
            )

        return result

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"发送风险告警失败: {e}")
        raise BusinessException(
            detail=f"发送风险告警失败: {str(e)}", status_code=500, error_code="RISK_ALERT_SENDING_FAILED"
        )


@router.get("/v31/alert/statistics", response_model=Dict[str, Any])
async def get_alert_statistics() -> Dict[str, Any]:
    """
    获取告警统计信息 (V3.1)

    获取告警系统的统计信息，包括发送成功率、抑制率等。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        notification_manager = get_risk_alert_notification_manager()
        if not notification_manager:
            raise BusinessException(
                detail="告警通知管理器不可用", status_code=503, error_code="ALERT_NOTIFICATION_MANAGER_UNAVAILABLE"
            )

        stats = notification_manager.get_alert_statistics()
        return stats

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"获取告警统计失败: {e}")
        raise BusinessException(
            detail=f"获取告警统计失败: {str(e)}", status_code=500, error_code="ALERT_STATISTICS_RETRIEVAL_FAILED"
        )


@router.post("/v31/rules/evaluate", response_model=List[Dict[str, Any]])
async def evaluate_alert_rules(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    评估告警规则 (V3.1)

    基于提供的上下文数据评估所有告警规则，返回触发的告警。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise BusinessException(
                detail="告警规则引擎不可用", status_code=503, error_code="ALERT_RULE_ENGINE_UNAVAILABLE"
            )

        # 创建告警上下文
        context = AlertContext(
            symbol=request.get("symbol"),
            portfolio_id=request.get("portfolio_id"),
            metrics=request.get("metrics", {}),
            metadata=request.get("metadata", {}),
        )

        # 评估规则
        results = await rule_engine.evaluate_rules(context)

        # 转换为API响应格式
        response = []
        for result in results:
            response.append(
                {
                    "rule_id": result.rule_id,
                    "severity": result.severity.value,
                    "actions": result.actions,
                    "evaluation_details": result.evaluation_details,
                }
            )

        return response

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"评估告警规则失败: {e}")
        raise BusinessException(
            detail=f"评估告警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_EVALUATION_FAILED"
        )


@router.post("/v31/rules/add", response_model=Dict[str, Any])
async def add_alert_rule(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    添加告警规则 (V3.1)

    添加新的告警规则到规则引擎。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise BusinessException(
                detail="告警规则引擎不可用", status_code=503, error_code="ALERT_RULE_ENGINE_UNAVAILABLE"
            )

        # 从请求数据创建规则
        rule_data = request.copy()
        rule_id = rule_data.pop("rule_id")

        # 这里可以根据模板创建或直接创建规则
        if "template_name" in request:
            rule = await rule_engine.create_rule_from_template(request["template_name"], rule_id, rule_data)
        else:
            from src.governance.risk_management.services.alert_rule_engine import AlertRule

            rule = AlertRule(rule_id=rule_id, **rule_data)

        if rule_engine.add_rule(rule):
            return {"success": True, "rule_id": rule_id, "message": "规则添加成功"}
        else:
            raise BusinessException(detail="规则添加失败", status_code=400, error_code="RULE_ADDITION_FAILED")

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"添加告警规则失败: {e}")
        raise BusinessException(
            detail=f"添加告警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_ADDITION_FAILED"
        )


@router.delete("/v31/rules/remove/{rule_id}", response_model=Dict[str, Any])
async def remove_alert_rule(rule_id: str) -> Dict[str, Any]:
    """
    移除告警规则 (V3.1)

    从规则引擎中移除指定的告警规则。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise BusinessException(
                detail="告警规则引擎不可用", status_code=503, error_code="ALERT_RULE_ENGINE_UNAVAILABLE"
            )

        if rule_engine.remove_rule(rule_id):
            return {"success": True, "rule_id": rule_id, "message": "规则移除成功"}
        else:
            raise NotFoundException(resource="规则", identifier="查询条件")

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"移除告警规则失败: {e}")
        raise BusinessException(
            detail=f"移除告警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_REMOVAL_FAILED"
        )


@router.get("/v31/rules/statistics", response_model=Dict[str, Any])
async def get_rule_statistics() -> Dict[str, Any]:
    """
    获取规则统计信息 (V3.1)

    获取告警规则引擎的统计信息。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        rule_engine = get_alert_rule_engine()
        if not rule_engine:
            raise BusinessException(
                detail="告警规则引擎不可用", status_code=503, error_code="ALERT_RULE_ENGINE_UNAVAILABLE"
            )

        stats = rule_engine.get_rule_statistics()
        return stats

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"获取规则统计失败: {e}")
        raise BusinessException(
            detail=f"获取规则统计失败: {str(e)}", status_code=500, error_code="RULE_STATISTICS_RETRIEVAL_FAILED"
        )


@router.get("/v31/risk/realtime/{symbol}", response_model=Dict[str, Any])
async def get_realtime_risk_metrics(symbol: str) -> Dict[str, Any]:
    """
    获取实时风险指标 (V3.1)

    获取指定股票的实时风险指标计算结果。
    """
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

        # 这里应该集成实时风险计算
        # 暂时返回模拟数据
        return {
            "symbol": symbol,
            "timestamp": datetime.now(),
            "volatility_20d": 0.25,
            "atr_14": 2.5,
            "liquidity_score": 75,
            "risk_level": "medium",
            "last_updated": datetime.now(),
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"获取实时风险指标失败 {symbol}: {e}")
        raise BusinessException(
            detail=f"获取实时风险指标失败: {str(e)}",
            status_code=500,
            error_code="REALTIME_RISK_METRICS_RETRIEVAL_FAILED",
        )


# ============ V3.1 新增功能 - 完整风险管理系统 ============


@router.get("/v31/stock/{symbol}")
async def get_stock_risk_v31(symbol: str) -> Dict[str, Any]:
    """
    V3.1 个股风险监控 - GPU加速版本

    复用现有的风险管理系统，提供完整的个股风险指标。
    """
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

        # 计算个股风险指标
        risk_metrics = await core.calculate_stock_risk(symbol)

        # 异步记录到监控系统
        await core._publish_risk_event("stock_risk_calculated", {"symbol": symbol, "metrics": risk_metrics.__dict__})

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "risk_metrics": risk_metrics.__dict__,
                "calculated_at": datetime.now().isoformat(),
                "version": "3.1",
            },
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"V3.1个股风险计算失败 {symbol}: {e}")
        raise BusinessException(
            detail=f"个股风险计算失败: {str(e)}", status_code=500, error_code="INDIVIDUAL_STOCK_RISK_CALCULATION_FAILED"
        )


@router.get("/v31/portfolio/{portfolio_id}")
async def get_portfolio_risk_v31(portfolio_id: str) -> Dict[str, Any]:
    """
    V3.1 组合风险监控 - GPU加速版本

    复用现有的风险管理系统，提供完整的组合风险指标。
    """
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

        # 计算组合风险指标
        risk_metrics = await core.calculate_portfolio_risk(portfolio_id)

        # 异步记录到监控系统
        await core._publish_risk_event(
            "portfolio_risk_calculated", {"portfolio_id": portfolio_id, "metrics": risk_metrics.__dict__}
        )

        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "risk_metrics": risk_metrics.__dict__,
                "calculated_at": datetime.now().isoformat(),
                "version": "3.1",
            },
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"V3.1组合风险计算失败 {portfolio_id}: {e}")
        raise BusinessException(
            detail=f"组合风险计算失败: {str(e)}", status_code=500, error_code="PORTFOLIO_RISK_CALCULATION_FAILED"
        )


@router.post("/v31/stop-loss/calculate")
async def calculate_stop_loss_v31(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    V3.1 智能止损策略计算

    支持波动率自适应止损和跟踪止损两种策略。
    """
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
                highest_price=entry_price,  # 假设最高价等于入场价
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
        logger.error(f"V3.1止损计算失败: {e}")
        raise BusinessException(
            detail=f"止损计算失败: {str(e)}", status_code=500, error_code="STOP_LOSS_CALCULATION_FAILED"
        )


@router.post("/v31/stop-loss/trigger")
async def trigger_stop_loss_v31(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    V3.1 止损执行

    检查并执行止损逻辑。
    """
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

        # 执行止损检查
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
        logger.error(f"V3.1止损执行失败: {e}")
        raise BusinessException(
            detail=f"止损执行失败: {str(e)}", status_code=500, error_code="STOP_LOSS_EXECUTION_FAILED"
        )


@router.get("/v31/alerts/active")
async def get_active_alerts_v31() -> Dict[str, Any]:
    """
    V3.1 获取活跃风险告警

    复用现有的告警服务，支持智能去重。
    """
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        core = get_risk_management_core()
        if not core or not core.alert_service:
            raise BusinessException(detail="告警服务不可用", status_code=503, error_code="ALERT_SERVICE_UNAVAILABLE")

        # 这里应该从数据库查询活跃告警
        # 暂时返回模拟数据
        alerts = []

        return {"status": "success", "data": {"alerts": alerts, "total": len(alerts), "version": "3.1"}}

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"V3.1获取活跃告警失败: {e}")
        raise BusinessException(
            detail=f"获取活跃告警失败: {str(e)}", status_code=500, error_code="ACTIVE_ALERTS_RETRIEVAL_FAILED"
        )


@router.post("/v31/alerts/{alert_id}/acknowledge")
async def acknowledge_alert_v31(alert_id: int, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    V3.1 确认风险告警

    用户确认并记录处理结果。
    """
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        core = get_risk_management_core()
        if not core or not core.alert_service:
            raise BusinessException(detail="告警服务不可用", status_code=503, error_code="ALERT_SERVICE_UNAVAILABLE")

        action_taken = request.get("action_taken", "")
        feedback = request.get("feedback", "")

        # 这里应该更新数据库中的告警状态
        # 暂时返回成功响应

        return {
            "status": "success",
            "data": {
                "alert_id": alert_id,
                "status": "acknowledged",
                "action_taken": action_taken,
                "feedback": feedback,
                "acknowledged_at": datetime.now().isoformat(),
            },
            "version": "3.1",
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"V3.1确认告警失败 {alert_id}: {e}")
        raise BusinessException(
            detail=f"确认告警失败: {str(e)}", status_code=500, error_code="ALERT_CONFIRMATION_FAILED"
        )


@router.get("/v31/health")
async def get_risk_management_health() -> Dict[str, Any]:
    """
    V3.1 风险管理系统健康检查

    检查各个组件的运行状态。
    """
    try:
        health_status = {
            "status": "healthy",
            "version": "3.1",
            "components": {},
            "checked_at": datetime.now().isoformat(),
        }

        # 检查V3.1系统是否可用
        health_status["components"]["v31_system"] = {
            "status": "available" if RISK_MANAGEMENT_V31_AVAILABLE else "unavailable",
            "available": RISK_MANAGEMENT_V31_AVAILABLE,
        }

        # 检查核心组件
        if RISK_MANAGEMENT_V31_AVAILABLE:
            core = get_risk_management_core()
            health_status["components"]["core"] = {
                "status": "initialized" if core else "uninitialized",
                "available": core is not None,
            }

            if core:
                health_status["components"]["gpu_calculator"] = {
                    "status": "available" if core.risk_calculator else "unavailable",
                    "available": core.risk_calculator is not None,
                }
                health_status["components"]["stop_loss_engine"] = {
                    "status": "available" if core.stop_loss_engine else "unavailable",
                    "available": core.stop_loss_engine is not None,
                }
                health_status["components"]["alert_service"] = {
                    "status": "available" if core.alert_service else "unavailable",
                    "available": core.alert_service is not None,
                }
        else:
            health_status["status"] = "degraded"
            health_status["components"]["core"] = {"status": "unavailable", "available": False}

        return health_status

    except Exception as e:
        logger.error(f"V3.1健康检查失败: {e}")
        return {"status": "unhealthy", "error": str(e), "version": "3.1", "checked_at": datetime.now().isoformat()}


# ===== WebSocket 实时风险数据推送 =====


@router.websocket("/v31/ws/risk-updates")
async def websocket_risk_updates(websocket: WebSocket, topics: str = "portfolio_risk,stock_risk,alerts"):
    """
    WebSocket实时风险数据推送 (V3.1)

    支持订阅以下主题:
    - portfolio_risk: 组合风险指标更新
    - stock_risk: 个股风险指标更新
    - alerts: 风险告警通知
    - stop_loss: 止损执行通知

    使用示例:
    ws://localhost:8000/api/risk-management/v31/ws/risk-updates?topics=portfolio_risk,alerts
    """
    try:
        # 解析订阅主题
        topic_list = [t.strip() for t in topics.split(",") if t.strip()]

        # 建立连接
        await connection_manager.connect(websocket, topic_list)

        try:
            # 发送欢迎消息
            welcome_message = {
                "type": "welcome",
                "message": "已连接到MyStocks风险管理系统实时数据流",
                "subscribed_topics": topic_list,
                "timestamp": datetime.now().isoformat(),
            }
            await connection_manager.send_personal_message(welcome_message, websocket)

            # 保持连接并处理客户端消息
            while True:
                # 接收客户端消息 (支持心跳或其他控制消息)
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)

                    # 处理心跳消息
                    if message.get("type") == "ping":
                        pong_message = {
                            "type": "pong",
                            "timestamp": datetime.now().isoformat(),
                        }
                        await connection_manager.send_personal_message(pong_message, websocket)

                    # 处理订阅更新
                    elif message.get("type") == "subscribe":
                        new_topics = message.get("topics", [])
                        # 这里可以实现动态订阅更新
                        logger.info(f"客户端请求更新订阅: {new_topics}")

                    # 处理取消订阅
                    elif message.get("type") == "unsubscribe":
                        remove_topics = message.get("topics", [])
                        # 这里可以实现动态取消订阅
                        logger.info(f"客户端请求取消订阅: {remove_topics}")

                except json.JSONDecodeError:
                    # 忽略无效的JSON消息
                    pass

        except WebSocketDisconnect:
            connection_manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}")
        if websocket in connection_manager.active_connections:
            connection_manager.disconnect(websocket)


@router.post("/v31/ws/broadcast/{topic}")
async def broadcast_risk_update(topic: str, message: Dict[str, Any]):
    """
    广播风险数据更新 (V3.1)

    向订阅指定主题的WebSocket客户端广播消息。

    支持的主题:
    - portfolio_risk: 组合风险指标
    - stock_risk: 个股风险指标
    - alerts: 风险告警
    - stop_loss: 止损执行
    """
    try:
        if topic not in connection_manager.subscriptions:
            raise ValidationException(detail=f"不支持的主题: {topic}", field="topic")

        # 添加时间戳和消息类型
        broadcast_message = {
            "type": "update",
            "topic": topic,
            "data": message,
            "timestamp": datetime.now().isoformat(),
        }

        # 广播消息
        await connection_manager.broadcast_to_topic(topic, broadcast_message)

        return {
            "status": "success",
            "message": f"消息已广播到主题 '{topic}'",
            "topic": topic,
            "broadcast_at": datetime.now().isoformat(),
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error(f"广播风险更新失败 {topic}: {e}")
        raise BusinessException(detail=f"广播失败: {str(e)}", status_code=500, error_code="BROADCAST_FAILED")


@router.get("/v31/ws/connections")
async def get_websocket_connections():
    """
    获取WebSocket连接统计 (V3.1)

    返回当前活跃的WebSocket连接和订阅统计。
    """
    try:
        connection_stats = {
            "total_connections": len(connection_manager.active_connections),
            "topic_subscriptions": {
                topic: len(connections) for topic, connections in connection_manager.subscriptions.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

        return {
            "status": "success",
            "data": connection_stats,
        }

    except Exception as e:
        logger.error(f"获取WebSocket连接统计失败: {e}")
        raise BusinessException(
            detail=f"获取统计失败: {str(e)}", status_code=500, error_code="STATISTICS_RETRIEVAL_FAILED"
        )
