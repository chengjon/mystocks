"""
风险告警与规则扩展路由 (V3.1)
"""
import structlog
from typing import Any, Dict, List
from fastapi import APIRouter, Body

from app.core.exceptions import BusinessException

# 导入Week 4-5的新增组件
try:
    from src.governance.risk_management.services.alert_rule_engine import (
        AlertContext,
        get_alert_rule_engine,
    )
    from src.governance.risk_management.services.risk_alert_notification_manager import (
        get_risk_alert_notification_manager,
    )

    ENHANCED_RISK_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_RISK_FEATURES_AVAILABLE = False
    get_risk_alert_notification_manager = None
    get_alert_rule_engine = None
    AlertContext = None

logger = structlog.get_logger(__name__)
router = APIRouter()

RISK_ALERT_SEND_EXAMPLES = {
    "stock_risk_alert": {
        "summary": "发送股票风险告警",
        "value": {
            "symbol": "600519.SH",
            "alert_type": "price_drawdown",
            "severity": "warning",
            "message": "价格接近风控阈值",
            "metrics": {"drawdown": 0.074, "volatility": 0.23},
        },
    }
}

RISK_ALERT_RULE_EVALUATE_EXAMPLES = {
    "evaluate_symbol_context": {
        "summary": "评估股票告警规则",
        "value": {
            "symbol": "600519.SH",
            "portfolio_id": "core-book",
            "metrics": {"drawdown": 0.082, "var_95": 125000},
        },
    }
}

RISK_ALERT_RULE_ADD_EXAMPLES = {
    "add_drawdown_rule": {
        "summary": "新增回撤告警规则",
        "value": {
            "rule_id": "drawdown-08",
            "name": "大回撤预警",
            "description": "当组合回撤超过 8% 时触发预警",
            "severity": "critical",
            "condition_type": "threshold",
            "metric_name": "drawdown",
            "operator": ">=",
            "threshold": 0.08,
            "enabled": True,
        },
    }
}

@router.post(
    "/alert/send",
    response_model=Dict[str, Any],
    description="发送一条 V3.1 风险告警消息，可按股票维度或通用风险事件维度推送给通知管理器。",
)
async def send_risk_alert(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_SEND_EXAMPLES)
) -> Dict[str, Any]:
    """发送风险告警 (V3.1)"""
    try:
        notification_manager = get_risk_alert_notification_manager()
        alert_type = request.get("alert_type", "general_risk")
        severity = request.get("severity", "warning")

        if "symbol" in request:
            result = await notification_manager.send_stock_risk_alert(
                symbol=request["symbol"], risk_level=severity, risk_metrics=request.get("metrics", {})
            )
        else:
            result = await notification_manager.send_risk_alert(
                alert_type=alert_type, severity=severity, message=request.get("message", "")
            )
        return result
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.get("/alert/statistics", response_model=Dict[str, Any])
async def get_alert_statistics() -> Dict[str, Any]:
    """获取告警统计信息 (V3.1)"""
    return get_risk_alert_notification_manager().get_alert_statistics()

@router.post(
    "/rules/evaluate",
    response_model=List[Dict[str, Any]],
    description="基于当前风险上下文评估 V3.1 告警规则，并返回命中的规则与严重级别。",
)
async def evaluate_alert_rules(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_RULE_EVALUATE_EXAMPLES)
) -> List[Dict[str, Any]]:
    """评估告警规则 (V3.1)"""
    context = AlertContext(
        symbol=request.get("symbol"),
        portfolio_id=request.get("portfolio_id"),
        metrics=request.get("metrics", {})
    )
    results = await get_alert_rule_engine().evaluate_rules(context)
    return [{"rule_id": r.rule_id, "severity": r.severity.value} for r in results]

@router.post(
    "/rules/add",
    response_model=Dict[str, Any],
    description="向 V3.1 告警规则引擎新增一条规则，用于后续风险事件自动评估与触发。",
)
async def add_alert_rule(
    request: Dict[str, Any] = Body(..., openapi_examples=RISK_ALERT_RULE_ADD_EXAMPLES)
) -> Dict[str, Any]:
    """添加告警规则 (V3.1)"""
    from src.governance.risk_management.services.alert_rule_engine import AlertRule
    rule = AlertRule(**request)
    if get_alert_rule_engine().add_rule(rule):
        return {"success": True, "rule_id": rule.rule_id}
    raise BusinessException(detail="添加失败", status_code=400)
