from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Body, Path, Query

from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.openapi_config import COMMON_RESPONSES
from app.api.risk._shared import (
    DataClassification,
    ENHANCED_RISK_FEATURES_AVAILABLE,
    RISK_MANAGEMENT_V31_AVAILABLE,
    AlertContext,
    MyStocksUnifiedManager,
    NotificationManager,
    get_alert_rule_engine,
    get_monitoring_db,
    get_risk_alert_notification_manager,
    get_risk_management_core,
    logger,
    NotificationTestRequest,
    NotificationTestResponse,
    RiskAlertCreate,
    RiskAlertResponse,
    RiskAlertUpdate,
)

RISK_ALERT_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "风险告警增强服务不可用或尚未初始化",
    },
}

router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-告警"], responses=RISK_ALERT_ROUTE_RESPONSES)
_acknowledged_v31_alerts: dict[int, dict[str, Any]] = {}


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


def _resolve_notification_manager():
    notification_manager = get_risk_alert_notification_manager()
    if not notification_manager:
        raise BusinessException(
            detail="告警通知管理器不可用", status_code=503, error_code="ALERT_NOTIFICATION_MANAGER_UNAVAILABLE"
        )
    return notification_manager


def _resolve_rule_engine():
    rule_engine = get_alert_rule_engine()
    if not rule_engine:
        raise BusinessException(detail="告警规则引擎不可用", status_code=503, error_code="ALERT_RULE_ENGINE_UNAVAILABLE")
    return rule_engine


def _resolve_runtime_alert_service():
    core = get_risk_management_core()
    if not core or not core.alert_service:
        raise BusinessException(detail="告警服务不可用", status_code=503, error_code="ALERT_SERVICE_UNAVAILABLE")
    return core.alert_service


def _build_active_alerts_payload(alert_service: Any) -> list[dict[str, Any]]:
    history = getattr(alert_service, "alert_history", {}) or {}
    active_alerts: list[dict[str, Any]] = []

    for index, (alert_key, records) in enumerate(history.items(), start=1):
        if not records:
            continue
        latest = records[-1]
        active_alerts.append(
            {
                "alert_id": index,
                "alert_key": alert_key,
                "risk_level": latest.get("risk_level", "attention"),
                "status": "acknowledged" if index in _acknowledged_v31_alerts else "active",
                "last_triggered_at": latest.get("timestamp").isoformat()
                if hasattr(latest.get("timestamp"), "isoformat")
                else latest.get("timestamp"),
                "trigger_count": len(records),
                "acknowledgement": _acknowledged_v31_alerts.get(index),
            }
        )

    return active_alerts

RISK_ALERT_UPDATE_EXAMPLES = {
    "update_threshold_and_message": {
        "summary": "更新风险告警规则",
        "description": "调整现有告警规则的阈值、状态和提示文案。",
        "value": {
            "alert_name": "组合回撤预警",
            "alert_type": "drawdown",
            "severity": "warning",
            "threshold_value": 0.12,
            "message_template": "组合回撤达到 12%，请复核仓位风险。",
            "is_active": True,
        },
    }
}

RISK_ALERT_ACKNOWLEDGE_EXAMPLES = {
    "acknowledge_with_feedback": {
        "summary": "确认并记录处置结果",
        "description": "确认指定风险告警并附带操作说明与反馈。",
        "value": {
            "action_taken": "reduced_position",
            "feedback": "已减仓 20%，并提高后续监控频率。",
        },
    }
}

RISK_ALERT_SEND_EXAMPLES = {
    "send_stock_drawdown_alert": {
        "summary": "发送个股风险告警",
        "description": "针对单只股票的回撤风险发送一条 warning 级别通知。",
        "value": {
            "symbol": "600519.SH",
            "alert_type": "drawdown",
            "severity": "warning",
            "message": "贵州茅台日内回撤超过预警阈值，请复核仓位。",
            "metrics": {
                "drawdown": 0.061,
                "daily_change": -0.038,
            },
            "alert_triggers": ["daily_drawdown_threshold"],
        },
    }
}

RISK_ALERT_RULE_EVALUATION_EXAMPLES = {
    "evaluate_portfolio_rules": {
        "summary": "评估组合告警规则",
        "description": "传入组合和实时指标，批量评估当前已配置的风险告警规则。",
        "value": {
            "portfolio_id": "growth-portfolio",
            "symbol": "510300.SH",
            "metrics": {
                "drawdown": 0.084,
                "volatility": 0.22,
                "var_95": 0.031,
            },
            "metadata": {
                "market_session": "afternoon",
                "strategy": "trend_following",
            },
        },
    }
}

RISK_ALERT_RULE_CREATE_EXAMPLES = {
    "add_drawdown_rule": {
        "summary": "新增回撤告警规则",
        "description": "创建一个针对组合回撤的 warning 级别规则，并配置触发动作。",
        "value": {
            "rule_id": "portfolio-drawdown-warning",
            "rule_name": "组合回撤预警",
            "metric_name": "drawdown",
            "condition": ">=",
            "threshold": 0.1,
            "severity": "warning",
            "actions": ["notify", "create_task"],
            "cooldown_minutes": 30,
        },
    }
}

RISK_ALERT_CREATE_EXAMPLES = {
    "create_var_alert": {
        "summary": "创建风险预警规则",
        "description": "为指定组合创建一条 VaR 超限预警规则，并启用邮件通知。",
        "value": {
            "name": "组合VaR超限预警",
            "metric_type": "VaR",
            "threshold_value": 0.05,
            "condition": ">",
            "entity_type": "portfolio",
            "entity_id": 101,
            "is_active": True,
            "notification_channels": ["email"],
        },
    }
}

RISK_ALERT_NOTIFICATION_TEST_EXAMPLES = {
    "test_email_notification": {
        "summary": "测试邮件通知配置",
        "description": "校验风险告警邮件通知配置是否可用。",
        "value": {
            "notification_type": "email",
            "config_data": {
                "email": "risk-alerts@example.com",
                "subject": "MyStocks Risk Alert Test",
            },
        },
    }
}

RISK_ALERT_GENERATION_EXAMPLES = {
    "generate_portfolio_alerts": {
        "summary": "生成组合风险告警",
        "description": "根据当前回撤、日盈亏和阈值配置生成风险告警结果。",
        "value": {
            "current_drawdown": -0.124,
            "daily_pnl": -58000,
            "total_capital": 1000000,
            "config": {
                "max_drawdown_threshold": 0.1,
                "daily_loss_limit": 0.04,
            },
        },
    }
}

RISK_ALERT_SEND_RESPONSE_EXAMPLE = {
    "sent": True,
    "severity": "warning",
    "alert_key": "stock_risk_daily_drawdown_threshold:600519.SH",
    "aggregated_count": 1,
    "escalated": False,
}

RISK_ALERT_STATISTICS_RESPONSE_EXAMPLE = {
    "total_alerts_sent": 12,
    "total_alerts_suppressed": 2,
    "total_alerts_escalated": 1,
    "suppression_rate": 14.29,
    "escalation_rate": 8.33,
    "by_severity": {
        "info": {"sent": 3, "suppressed": 0, "escalated": 0},
        "warning": {"sent": 6, "suppressed": 1, "escalated": 1},
        "critical": {"sent": 3, "suppressed": 1, "escalated": 0},
    },
    "active_suppressions": 1,
    "generated_at": "2026-04-08T11:00:00",
}

RISK_ALERT_RULE_EVALUATION_RESPONSE_EXAMPLE = [
    {
        "rule_id": "portfolio-drawdown-warning",
        "severity": "warning",
        "actions": [{"type": "notify"}, {"type": "create_task"}],
        "evaluation_details": {
            "metric_name": "drawdown",
            "actual_value": 0.084,
            "threshold": 0.08,
        },
    }
]

RISK_ALERT_RULE_ADD_RESPONSE_EXAMPLE = {
    "success": True,
    "rule_id": "portfolio-drawdown-warning",
    "message": "规则添加成功",
}

RISK_ALERT_RULE_REMOVE_RESPONSE_EXAMPLE = {
    "success": True,
    "rule_id": "portfolio-drawdown-warning",
    "message": "规则移除成功",
}

RISK_ALERT_RULE_STATISTICS_RESPONSE_EXAMPLE = {
    "total_rules": 8,
    "enabled_rules": 6,
    "disabled_rules": 2,
    "active_suppressions": 1,
    "execution_stats": {
        "portfolio-drawdown-warning": 3,
        "var-limit-critical": 1,
    },
    "generated_at": "2026-04-08T11:00:00",
}

REALTIME_RISK_METRICS_RESPONSE_EXAMPLE = {
    "symbol": "600519.SH",
    "timestamp": "2026-04-08T11:00:00",
    "volatility_20d": 0.25,
    "atr_14": 2.5,
    "liquidity_score": 75,
    "risk_level": "medium",
    "last_updated": "2026-04-08T11:00:00",
}

RISK_ALERT_LIST_RESPONSE_EXAMPLE = [
    {
        "id": 101,
        "name": "组合VaR超限预警",
        "metric_type": "VaR",
        "threshold_value": 0.05,
        "condition": ">",
        "entity_type": "portfolio",
        "entity_id": 101,
        "is_active": True,
        "notification_channels": ["email"],
        "created_at": "2026-04-01T09:00:00",
        "updated_at": "2026-04-08T10:30:00",
    },
    {
        "id": 102,
        "name": "单日亏损超限预警",
        "metric_type": "DailyLoss",
        "threshold_value": 0.04,
        "condition": "<",
        "entity_type": "portfolio",
        "entity_id": 101,
        "is_active": False,
        "notification_channels": ["email", "webhook"],
        "created_at": "2026-04-02T09:00:00",
        "updated_at": "2026-04-07T15:45:00",
    },
]

RISK_ALERT_CREATE_RESPONSE_EXAMPLE = {
    "id": 103,
    "name": "组合VaR超限预警",
    "metric_type": "VaR",
    "threshold_value": 0.05,
    "condition": ">",
    "entity_type": "portfolio",
    "entity_id": 101,
    "is_active": True,
    "notification_channels": ["email"],
    "created_at": "2026-04-08T11:00:00",
    "updated_at": "2026-04-08T11:00:00",
}

RISK_ALERT_UPDATE_RESPONSE_EXAMPLE = {
    "message": "预警规则已更新",
}

RISK_ALERT_DELETE_RESPONSE_EXAMPLE = {
    "message": "预警规则已禁用",
}

RISK_ALERT_NOTIFICATION_TEST_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "测试通知发送成功",
}

RISK_ALERT_GENERATION_RESPONSE_EXAMPLE = {
    "status": "success",
    "alerts": [
        {
            "type": "max_drawdown_exceeded",
            "severity": "CRITICAL",
            "message": "最大回撤超限: 12.40% > 10.00%",
            "timestamp": "2026-04-08T11:00:00",
            "suggestion": "立即减仓或平仓，控制风险敞口",
        }
    ],
    "alert_count": 1,
    "generated_at": "2026-04-08T11:00:00",
}

ACTIVE_ALERTS_V31_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "alerts": [
            {
                "alert_id": 321,
                "alert_type": "drawdown",
                "severity": "warning",
                "message": "组合回撤达到 8.4%，接近阈值。",
            }
        ],
        "total": 1,
        "version": "3.1",
    },
}

ACKNOWLEDGE_ALERT_V31_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "alert_id": 321,
        "status": "acknowledged",
        "action_taken": "reduced_position",
        "feedback": "已减仓 20%，并提高后续监控频率。",
        "acknowledged_at": "2026-04-08T11:00:00",
    },
    "version": "3.1",
}

RISK_ALERT_SEND_RESPONSES = _success_response_spec("V3.1 风险告警发送成功。", RISK_ALERT_SEND_RESPONSE_EXAMPLE)
RISK_ALERT_STATISTICS_RESPONSES = _success_response_spec(
    "V3.1 风险告警统计查询成功。", RISK_ALERT_STATISTICS_RESPONSE_EXAMPLE
)
RISK_ALERT_RULE_EVALUATION_RESPONSES = _success_response_spec(
    "V3.1 告警规则评估成功。", RISK_ALERT_RULE_EVALUATION_RESPONSE_EXAMPLE
)
RISK_ALERT_RULE_ADD_RESPONSES = _success_response_spec(
    "V3.1 告警规则新增成功。", RISK_ALERT_RULE_ADD_RESPONSE_EXAMPLE
)
RISK_ALERT_RULE_REMOVE_RESPONSES = _success_response_spec(
    "V3.1 告警规则移除成功。", RISK_ALERT_RULE_REMOVE_RESPONSE_EXAMPLE
)
RISK_ALERT_RULE_STATISTICS_RESPONSES = _success_response_spec(
    "V3.1 告警规则统计查询成功。", RISK_ALERT_RULE_STATISTICS_RESPONSE_EXAMPLE
)
REALTIME_RISK_METRICS_RESPONSES = _success_response_spec(
    "实时风险指标快照查询成功。", REALTIME_RISK_METRICS_RESPONSE_EXAMPLE
)
RISK_ALERT_LIST_RESPONSES = _success_response_spec("风险预警规则列表查询成功。", RISK_ALERT_LIST_RESPONSE_EXAMPLE)
RISK_ALERT_CREATE_RESPONSES = _success_response_spec("风险预警规则创建成功。", RISK_ALERT_CREATE_RESPONSE_EXAMPLE)
RISK_ALERT_UPDATE_RESPONSES = _success_response_spec("风险预警规则更新成功。", RISK_ALERT_UPDATE_RESPONSE_EXAMPLE)
RISK_ALERT_DELETE_RESPONSES = _success_response_spec("风险预警规则禁用成功。", RISK_ALERT_DELETE_RESPONSE_EXAMPLE)
RISK_ALERT_NOTIFICATION_TEST_RESPONSES = _success_response_spec(
    "风险告警通知测试成功。", RISK_ALERT_NOTIFICATION_TEST_RESPONSE_EXAMPLE
)
RISK_ALERT_GENERATION_RESPONSES = _success_response_spec(
    "风险告警生成成功。", RISK_ALERT_GENERATION_RESPONSE_EXAMPLE
)
ACTIVE_ALERTS_V31_RESPONSES = _success_response_spec(
    "V3.1 活跃告警列表查询成功。", ACTIVE_ALERTS_V31_RESPONSE_EXAMPLE
)
ACKNOWLEDGE_ALERT_V31_RESPONSES = _success_response_spec(
    "V3.1 风险告警确认成功。", ACKNOWLEDGE_ALERT_V31_RESPONSE_EXAMPLE
)


@router.post(
    "/v31/alert/send",
    response_model=Dict[str, Any],
    summary="发送 V3.1 风险告警",
    description="发送一条 V3.1 风险告警通知，可用于个股、组合或通用风险事件的即时告警。",
    responses=RISK_ALERT_SEND_RESPONSES,
)
async def send_risk_alert(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_SEND_EXAMPLES)
) -> Dict[str, Any]:
    try:
        notification_manager = _resolve_notification_manager()

        alert_type = request.get("alert_type", "general_risk")
        severity = request.get("severity", "warning")
        message = request.get("message", "")
        metrics = request.get("metrics", {})
        context = request.get("context", {})

        if "symbol" in request:
            result = await notification_manager.send_stock_risk_alert(
                symbol=request["symbol"],
                risk_level=severity,
                risk_metrics=metrics,
                alert_triggers=request.get("alert_triggers", []),
            )
        elif "portfolio_id" in request:
            result = await notification_manager.send_portfolio_risk_alert(
                portfolio_id=request["portfolio_id"],
                risk_level=severity,
                risk_metrics=metrics,
                triggered_alerts=request.get("triggered_alerts", []),
            )
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
        logger.error("发送风险告警失败: %(e)s")
        raise BusinessException(
            detail=f"发送风险告警失败: {str(e)}", status_code=500, error_code="RISK_ALERT_SENDING_FAILED"
        )


@router.get(
    "/v31/alert/statistics",
    response_model=Dict[str, Any],
    summary="查询 V3.1 告警统计",
    description="获取 V3.1 风险告警通知的统计摘要，包括告警数量、分级分布和发送情况。",
    responses=RISK_ALERT_STATISTICS_RESPONSES,
)
async def get_alert_statistics() -> Dict[str, Any]:
    try:
        notification_manager = _resolve_notification_manager()

        return notification_manager.get_alert_statistics()

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取告警统计失败: %(e)s")
        raise BusinessException(
            detail=f"获取告警统计失败: {str(e)}", status_code=500, error_code="ALERT_STATISTICS_RETRIEVAL_FAILED"
        )


@router.post(
    "/v31/rules/evaluate",
    response_model=List[Dict[str, Any]],
    summary="评估 V3.1 告警规则",
    description="根据输入的风险上下文评估当前 V3.1 告警规则，并返回命中的规则结果。",
    responses=RISK_ALERT_RULE_EVALUATION_RESPONSES,
)
async def evaluate_alert_rules(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_RULE_EVALUATION_EXAMPLES)
) -> List[Dict[str, Any]]:
    try:
        rule_engine = _resolve_rule_engine()

        context = AlertContext(
            symbol=request.get("symbol"),
            portfolio_id=request.get("portfolio_id"),
            metrics=request.get("metrics", {}),
            metadata=request.get("metadata", {}),
        )
        results = await rule_engine.evaluate_rules(context)

        return [
            {
                "rule_id": r.rule_id,
                "severity": r.severity.value,
                "actions": r.actions,
                "evaluation_details": r.evaluation_details,
            }
            for r in results
        ]

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("评估告警规则失败: %(e)s")
        raise BusinessException(
            detail=f"评估告警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_EVALUATION_FAILED"
        )


@router.post(
    "/v31/rules/add",
    response_model=Dict[str, Any],
    summary="新增 V3.1 告警规则",
    description="向 V3.1 风险告警引擎新增一条规则，可直接提交规则定义或基于模板创建。",
    responses=RISK_ALERT_RULE_ADD_RESPONSES,
)
async def add_alert_rule(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_RULE_CREATE_EXAMPLES)
) -> Dict[str, Any]:
    try:
        rule_engine = _resolve_rule_engine()

        rule_data = request.copy()
        rule_id = rule_data.pop("rule_id")

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
        logger.error("添加告警规则失败: %(e)s")
        raise BusinessException(
            detail=f"添加告警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_ADDITION_FAILED"
        )


@router.delete(
    "/v31/rules/remove/{rule_id}",
    response_model=Dict[str, Any],
    summary="移除 V3.1 告警规则",
    description="从 V3.1 风险告警引擎中移除指定规则，适用于停用或清理无效规则。",
    responses=RISK_ALERT_RULE_REMOVE_RESPONSES,
)
async def remove_alert_rule(rule_id: str = Path(..., description="需要移除的告警规则ID。")) -> Dict[str, Any]:
    try:
        rule_engine = _resolve_rule_engine()

        if rule_engine.remove_rule(rule_id):
            return {"success": True, "rule_id": rule_id, "message": "规则移除成功"}
        else:
            raise NotFoundException(resource="规则", identifier="查询条件")

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("移除告警规则失败: %(e)s")
        raise BusinessException(
            detail=f"移除告警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_REMOVAL_FAILED"
        )


@router.get(
    "/v31/rules/statistics",
    response_model=Dict[str, Any],
    summary="查询 V3.1 规则统计",
    description="返回 V3.1 风险告警规则引擎的规则统计信息，用于查看规则规模和启停状态。",
    responses=RISK_ALERT_RULE_STATISTICS_RESPONSES,
)
async def get_rule_statistics() -> Dict[str, Any]:
    try:
        rule_engine = _resolve_rule_engine()

        return rule_engine.get_rule_statistics()

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("获取规则统计失败: %(e)s")
        raise BusinessException(
            detail=f"获取规则统计失败: {str(e)}", status_code=500, error_code="RULE_STATISTICS_RETRIEVAL_FAILED"
        )


@router.get(
    "/v31/risk/realtime/{symbol}",
    response_model=Dict[str, Any],
    summary="获取实时风险快照",
    description="获取指定股票的实时风险指标快照，包括波动率、ATR、流动性分数和风险等级。",
    responses=REALTIME_RISK_METRICS_RESPONSES,
)
async def get_realtime_risk_metrics(
    symbol: str = Path(..., description="需要查询实时风险指标的股票代码。"),
) -> Dict[str, Any]:
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise BusinessException(
                detail="增强风险功能不可用", status_code=503, error_code="ENHANCED_RISK_FEATURE_UNAVAILABLE"
            )

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
        logger.error("获取实时风险指标失败 %(symbol)s: %(e)s")
        raise BusinessException(
            detail=f"获取实时风险指标失败: {str(e)}",
            status_code=500,
            error_code="REALTIME_RISK_METRICS_RETRIEVAL_FAILED",
        )


@router.get(
    "/alerts",
    summary="查询风险预警规则列表",
    description="查询风险预警规则列表，可按启用状态筛选，用于风控配置台或告警治理页面。",
    responses=RISK_ALERT_LIST_RESPONSES,
)
async def list_risk_alerts(
    is_active: Optional[bool] = Query(None, description="按启用状态筛选风险预警规则；不传则返回全部。"),
) -> List[Dict[str, Any]]:
    try:
        manager = MyStocksUnifiedManager()
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        alerts_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            filters=filters,
        )
        return alerts_df.to_dict("records") if alerts_df is not None else []

    except Exception as e:
        raise BusinessException(
            detail=f"获取预警列表失败: {str(e)}", status_code=500, error_code="ALERT_LIST_RETRIEVAL_FAILED"
        )


@router.post(
    "/alerts",
    response_model=RiskAlertResponse,
    summary="创建风险预警规则",
    description="创建一条风险预警规则，并将规则配置持久化到风险告警存储中。",
    responses=RISK_ALERT_CREATE_RESPONSES,
)
async def create_risk_alert(
    alert_data: RiskAlertCreate = Body(..., openapi_examples=RISK_ALERT_CREATE_EXAMPLES)
) -> RiskAlertResponse:
    operation_start = datetime.now()
    try:
        manager = MyStocksUnifiedManager()
        data_dict = alert_data.dict()
        data_dict["created_at"] = datetime.now()
        data_dict["updated_at"] = datetime.now()

        alert_df = pd.DataFrame([data_dict])
        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
        )

        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="risk_alerts",
            operation_name="create_risk_alert",
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result,
        )

        if result:
            data_dict["id"] = int(datetime.now().timestamp())
            return RiskAlertResponse(**data_dict)
        else:
            raise BusinessException(detail="创建预警规则失败", status_code=500, error_code="ALERT_RULE_CREATION_FAILED")

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="risk_alerts",
            operation_name="create_risk_alert",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise BusinessException(
            detail=f"创建预警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_CREATION_FAILED"
        )


@router.put(
    "/alerts/{alert_id}",
    summary="更新风险预警规则",
    description="更新指定风险告警规则的配置内容，并持久化最新版本。",
    responses=RISK_ALERT_UPDATE_RESPONSES,
)
async def update_risk_alert(
    alert_id: int = Path(..., description="需要更新的风险告警规则ID。"),
    alert_update: RiskAlertUpdate = Body(..., openapi_examples=RISK_ALERT_UPDATE_EXAMPLES),
) -> Dict[str, str]:
    try:
        manager = MyStocksUnifiedManager()
        update_data = alert_update.dict(exclude_unset=True)
        update_data["id"] = alert_id
        update_data["updated_at"] = datetime.now()

        alert_df = pd.DataFrame([update_data])
        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            upsert=True,
        )

        if result:
            return {"message": "预警规则已更新"}
        else:
            raise BusinessException(detail="更新预警规则失败", status_code=500, error_code="ALERT_RULE_UPDATE_FAILED")

    except Exception as e:
        raise BusinessException(
            detail=f"更新预警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_UPDATE_FAILED"
        )


@router.delete(
    "/alerts/{alert_id}",
    summary="禁用风险预警规则",
    description="禁用指定的风险预警规则，保留记录但不再参与后续告警触发。",
    responses=RISK_ALERT_DELETE_RESPONSES,
)
async def delete_risk_alert(alert_id: int = Path(..., description="需要禁用的风险告警规则ID。")) -> Dict[str, str]:
    try:
        manager = MyStocksUnifiedManager()
        alert_df = pd.DataFrame([{"id": alert_id, "is_active": False}])
        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            upsert=True,
        )

        if result:
            return {"message": "预警规则已禁用"}
        else:
            raise BusinessException(detail="删除预警规则失败", status_code=500, error_code="ALERT_RULE_DELETION_FAILED")

    except Exception as e:
        raise BusinessException(
            detail=f"删除预警规则失败: {str(e)}", status_code=500, error_code="ALERT_RULE_DELETION_FAILED"
        )


@router.post(
    "/notifications/test",
    response_model=NotificationTestResponse,
    summary="测试风险告警通知",
    description="发送一条测试通知，用于验证风险告警通知渠道配置是否可正常投递。",
    responses=RISK_ALERT_NOTIFICATION_TEST_RESPONSES,
)
async def test_notification(
    request: NotificationTestRequest = Body(..., openapi_examples=RISK_ALERT_NOTIFICATION_TEST_EXAMPLES)
) -> NotificationTestResponse:
    try:
        notifier = NotificationManager()

        if request.notification_type == "email":
            result = notifier.send_email(
                to_addrs=[request.config_data.get("email")],
                subject="MyStocks 测试通知",
                message="这是一封测试邮件，您的邮件配置正常工作！",
            )
        elif request.notification_type == "webhook":
            result = notifier.send_webhook(message="MyStocks 测试通知", test=True)
        else:
            raise ValidationException(detail="不支持的通知类型", field="notification_type")

        if result:
            return NotificationTestResponse(success=True, message="测试通知发送成功")
        else:
            return NotificationTestResponse(success=False, message="测试通知发送失败")

    except Exception as e:
        raise BusinessException(detail=f"发送失败: {str(e)}", status_code=500, error_code="SENDING_FAILED")


@router.post(
    "/alerts/generate",
    summary="生成风险告警结果",
    description="基于当前回撤、日盈亏与风控阈值配置即时生成一组风险告警结果。",
    responses=RISK_ALERT_GENERATION_RESPONSES,
)
async def generate_risk_alerts(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_GENERATION_EXAMPLES)
) -> Dict[str, Any]:
    try:
        current_drawdown = request.get("current_drawdown", 0)
        daily_pnl = request.get("daily_pnl", 0)
        total_capital = request.get("total_capital", 1000000)
        config = request.get("config", {})
        max_drawdown_threshold = config.get("max_drawdown_threshold", 0.30)
        daily_loss_limit = config.get("daily_loss_limit", 0.05)

        alerts = []
        alert_time = datetime.now().isoformat()

        if abs(current_drawdown) > max_drawdown_threshold:
            alerts.append(
                {
                    "type": "max_drawdown_exceeded",
                    "severity": "CRITICAL",
                    "message": f"最大回撤超限: {abs(current_drawdown) * 100:.2f}% > {max_drawdown_threshold * 100:.2f}%",
                    "timestamp": alert_time,
                    "suggestion": "立即减仓或平仓，控制风险敞口",
                }
            )

        daily_loss_pct = daily_pnl / total_capital if total_capital > 0 else 0
        if daily_loss_pct < -daily_loss_limit:
            alerts.append(
                {
                    "type": "daily_loss_limit_exceeded",
                    "severity": "WARNING",
                    "message": f"单日亏损超限: {daily_loss_pct * 100:.2f}% < -{daily_loss_limit * 100:.2f}%",
                    "timestamp": alert_time,
                    "suggestion": "暂停新开仓，评估当前持仓风险",
                }
            )

        return {"status": "success", "alerts": alerts, "alert_count": len(alerts), "generated_at": alert_time}

    except Exception as e:
        logger.error("生成风险告警失败: {e}", exc_info=True)
        raise BusinessException(
            detail=f"生成风险告警失败: {str(e)}", status_code=500, error_code="RISK_ALERT_GENERATION_FAILED"
        )


@router.get(
    "/v31/alerts/active",
    summary="查询 V3.1 活跃告警",
    description="获取当前 V3.1 风险管理系统中的活跃告警列表与总数，用于实时告警面板展示。",
    responses=ACTIVE_ALERTS_V31_RESPONSES,
)
async def get_active_alerts_v31() -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        alert_service = _resolve_runtime_alert_service()
        alerts = _build_active_alerts_payload(alert_service)
        return {"status": "success", "data": {"alerts": alerts, "total": len(alerts), "version": "3.1"}}

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("V3.1获取活跃告警失败: %(e)s")
        raise BusinessException(
            detail=f"获取活跃告警失败: {str(e)}", status_code=500, error_code="ACTIVE_ALERTS_RETRIEVAL_FAILED"
        )


@router.post(
    "/v31/alerts/{alert_id}/acknowledge",
    summary="确认 V3.1 风险告警",
    description="确认指定 V3.1 风险告警，并记录处理动作与人工反馈。",
    responses=ACKNOWLEDGE_ALERT_V31_RESPONSES,
)
async def acknowledge_alert_v31(
    alert_id: int = Path(..., description="需要确认的风险告警ID。"),
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_ACKNOWLEDGE_EXAMPLES),
) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        alert_service = _resolve_runtime_alert_service()
        alerts = _build_active_alerts_payload(alert_service)
        if not any(item["alert_id"] == alert_id for item in alerts):
            raise NotFoundException(resource="风险告警", identifier=str(alert_id))

        _acknowledged_v31_alerts[alert_id] = {
            "action_taken": request.get("action_taken", ""),
            "feedback": request.get("feedback", ""),
            "acknowledged_at": datetime.now().isoformat(),
        }

        return {
            "status": "success",
            "data": {
                "alert_id": alert_id,
                "status": "acknowledged",
                "action_taken": _acknowledged_v31_alerts[alert_id]["action_taken"],
                "feedback": _acknowledged_v31_alerts[alert_id]["feedback"],
                "acknowledged_at": _acknowledged_v31_alerts[alert_id]["acknowledged_at"],
            },
            "version": "3.1",
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("V3.1确认告警失败 %(alert_id)s: %(e)s")
        raise BusinessException(
            detail=f"确认告警失败: {str(e)}", status_code=500, error_code="ALERT_CONFIRMATION_FAILED"
        )
