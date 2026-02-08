"""
风险告警与规则扩展路由 (V3.1)
"""
import structlog
from typing import Any, Dict, List, Optional
from fastapi import APIRouter

from app.core.exceptions import BusinessException, NotFoundException, ValidationException

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

@router.post("/alert/send", response_model=Dict[str, Any])
async def send_risk_alert(request: Dict[str, Any]) -> Dict[str, Any]:
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

@router.post("/rules/evaluate", response_model=List[Dict[str, Any]])
async def evaluate_alert_rules(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """评估告警规则 (V3.1)"""
    context = AlertContext(
        symbol=request.get("symbol"),
        portfolio_id=request.get("portfolio_id"),
        metrics=request.get("metrics", {})
    )
    results = await get_alert_rule_engine().evaluate_rules(context)
    return [{"rule_id": r.rule_id, "severity": r.severity.value} for r in results]

@router.post("/rules/add", response_model=Dict[str, Any])
async def add_alert_rule(request: Dict[str, Any]) -> Dict[str, Any]:
    """添加告警规则 (V3.1)"""
    from src.governance.risk_management.services.alert_rule_engine import AlertRule
    rule = AlertRule(**request)
    if get_alert_rule_engine().add_rule(rule):
        return {"success": True, "rule_id": rule.rule_id}
    raise BusinessException(detail="添加失败", status_code=400)
