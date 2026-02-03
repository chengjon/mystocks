"""
风险告警管理 API - V3.1

提供风险告警功能:
- 风险告警发送
- 告警统计信息
- 告警规则评估和管理
- 实时风险指标

Author: Claude Code
Version: 3.1.0
Date: 2026-01-10
"""

import os
import sys
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException

logger = structlog.get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core import DataClassification  # noqa: E402
from unified_manager import MyStocksUnifiedManager as UM  # noqa: E402,F401

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

router = APIRouter(prefix="/api/v1/risk/alerts", tags=["风险告警管理"])

from app.schemas.risk_schemas import (  # noqa: E402
    RiskAlertCreate,
    RiskAlertResponse,
    RiskAlertUpdate,
)


@router.get("/")
async def list_risk_alerts(is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
    """获取风险预警规则列表"""
    try:
        manager = MyStocksUnifiedManager()  # noqa: F821

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
        raise HTTPException(status_code=500, detail=f"获取预警列表失败: {str(e)}")


@router.post("/", response_model=RiskAlertResponse)
async def create_risk_alert(alert_data: RiskAlertCreate) -> RiskAlertResponse:
    """创建风险预警规则"""
    from datetime import datetime as dt

    try:
        manager = MyStocksUnifiedManager()  # noqa: F821

        data_dict = alert_data.dict()
        data_dict["created_at"] = dt.now()
        data_dict["updated_at"] = dt.now()

        import pandas as pd

        alert_df = pd.DataFrame([data_dict])

        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
        )

        if result:
            data_dict["id"] = int(dt.now().timestamp())
            return RiskAlertResponse(**data_dict)
        else:
            raise HTTPException(status_code=500, detail="创建预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建预警规则失败: {str(e)}")


@router.put("/{alert_id}")
async def update_risk_alert(alert_id: int, alert_update: RiskAlertUpdate) -> Dict[str, str]:
    """更新风险预警规则"""
    from datetime import datetime as dt

    try:
        manager = MyStocksUnifiedManager()  # noqa: F821

        update_data = alert_update.dict(exclude_unset=True)
        update_data["id"] = alert_id
        update_data["updated_at"] = dt.now()

        import pandas as pd

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
            raise HTTPException(status_code=500, detail="更新预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新预警规则失败: {str(e)}")


@router.delete("/{alert_id}")
async def delete_risk_alert(alert_id: int) -> Dict[str, str]:
    """删除风险预警规则（软删除）"""
    try:
        manager = MyStocksUnifiedManager()  # noqa: F821

        import pandas as pd

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
            raise HTTPException(status_code=500, detail="删除预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除预警规则失败: {str(e)}")


@router.post("/send", response_model=Dict[str, Any])
async def send_risk_alert(request: Dict[str, Any]) -> Dict[str, Any]:
    """发送风险告警"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        notification_manager = get_risk_alert_notification_manager()
        if not notification_manager:
            raise HTTPException(status_code=503, detail="告警通知管理器不可用")

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
            triggered_alerts = request.get("triggered_alerts", [])
            result = await notification_manager.send_portfolio_risk_alert(
                portfolio_id=request["portfolio_id"],
                risk_level=severity,
                risk_metrics=metrics,
                triggered_alerts=triggered_alerts,
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("发送风险告警失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"发送风险告警失败: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_alert_statistics() -> Dict[str, Any]:
    """获取告警统计信息"""
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            raise HTTPException(status_code=503, detail="增强风险功能不可用")

        notification_manager = get_risk_alert_notification_manager()
        if not notification_manager:
            raise HTTPException(status_code=503, detail="告警通知管理器不可用")

        stats = notification_manager.get_alert_statistics()
        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取告警统计失败: %(e)s")
        raise HTTPException(status_code=500, detail=f"获取告警统计失败: {str(e)}")
