"""
风险监控 API

提供VaR/CVaR计算、Beta分析、风险预警、通知管理等接口

Author: JohnC & Claude
Version: 1.0.0
Date: 2025-10-24
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_db
from ..models import RiskMetric, RiskAlert, AlertHistory, NotificationConfig
from ..schemas.risk import RiskAlertCreate, RiskAlertUpdate, NotificationConfigCreate
from ...analysis import ExtendedRiskMetrics
from ...utils import NotificationManager

router = APIRouter(prefix="/api/v1/risk", tags=["风险监控"])


# ============ 风险指标计算 ============


@router.get("/var-cvar")
async def calculate_var_cvar(
    entity_type: str,
    entity_id: int,
    confidence_level: float = 0.95,
    db: Session = Depends(get_db),
):
    """
    计算VaR和CVaR

    Args:
        entity_type: 实体类型 ('backtest', 'portfolio', 'strategy')
        entity_id: 实体ID
        confidence_level: 置信水平 (0.90, 0.95, 0.99)

    Returns:
        {
            "var_95_hist": -0.0289,
            "var_95_param": -0.0309,
            "var_99_hist": -0.0385,
            "cvar_95": -0.0360,
            "cvar_99": -0.0432
        }
    """
    # 获取收益率数据（这里需要根据entity_type和entity_id获取）
    # returns = get_returns_data(entity_type, entity_id)

    # 模拟数据
    import numpy as np

    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))

    # 计算风险指标
    metrics = ExtendedRiskMetrics.calculate_all(returns)

    # 保存到数据库
    risk_metric = RiskMetric(
        entity_type=entity_type,
        entity_id=entity_id,
        metric_date=datetime.now().date(),
        var_95_hist=metrics["var_95_hist"],
        var_95_param=metrics["var_95_param"],
        var_99_hist=metrics["var_99_hist"],
        cvar_95=metrics["cvar_95"],
        cvar_99=metrics["cvar_99"],
    )
    db.add(risk_metric)
    db.commit()

    return metrics


@router.get("/beta")
async def calculate_beta(
    entity_type: str,
    entity_id: int,
    market_index: str = "000001",  # 默认上证指数
    db: Session = Depends(get_db),
):
    """
    计算Beta系数

    Args:
        entity_type: 实体类型
        entity_id: 实体ID
        market_index: 市场指数代码

    Returns:
        {
            "beta": 1.23,
            "correlation": 0.85
        }
    """
    # 获取资产和市场收益率数据
    # asset_returns = get_returns_data(entity_type, entity_id)
    # market_returns = get_market_returns(market_index)

    # 模拟数据
    import numpy as np

    np.random.seed(42)
    asset_returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    market_returns = pd.Series(np.random.normal(0.0008, 0.015, 252))

    # 计算Beta
    beta = ExtendedRiskMetrics.beta(asset_returns, market_returns)

    # 计算相关系数
    correlation = asset_returns.corr(market_returns)

    # 保存到数据库
    risk_metric = (
        db.query(RiskMetric)
        .filter(
            RiskMetric.entity_type == entity_type,
            RiskMetric.entity_id == entity_id,
            RiskMetric.metric_date == datetime.now().date(),
        )
        .first()
    )

    if risk_metric:
        risk_metric.beta = beta
    else:
        risk_metric = RiskMetric(
            entity_type=entity_type,
            entity_id=entity_id,
            metric_date=datetime.now().date(),
            beta=beta,
        )
        db.add(risk_metric)

    db.commit()

    return {"beta": beta, "correlation": correlation}


@router.get("/dashboard")
async def get_risk_dashboard(db: Session = Depends(get_db)):
    """
    获取风险仪表盘数据

    Returns:
        {
            "metrics": {...},
            "active_alerts": [...],
            "recent_alerts": [...],
            "risk_history": [...]
        }
    """
    # 获取最新风险指标
    latest_metrics = (
        db.query(RiskMetric).order_by(RiskMetric.metric_date.desc()).first()
    )

    # 获取活跃预警规则
    active_alerts = db.query(RiskAlert).filter(RiskAlert.is_active == True).all()

    # 获取最近告警（最近7天）
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_alerts = (
        db.query(AlertHistory)
        .filter(AlertHistory.triggered_at >= seven_days_ago)
        .order_by(AlertHistory.triggered_at.desc())
        .limit(10)
        .all()
    )

    # 获取风险历史（最近30天）
    thirty_days_ago = datetime.now() - timedelta(days=30)
    risk_history = (
        db.query(RiskMetric)
        .filter(RiskMetric.metric_date >= thirty_days_ago.date())
        .order_by(RiskMetric.metric_date.asc())
        .all()
    )

    return {
        "metrics": {
            "var_95_hist": latest_metrics.var_95_hist if latest_metrics else None,
            "cvar_95": latest_metrics.cvar_95 if latest_metrics else None,
            "beta": latest_metrics.beta if latest_metrics else None,
        },
        "active_alerts": [
            {
                "id": alert.id,
                "name": alert.name,
                "metric_type": alert.metric_type,
                "threshold_value": alert.threshold_value,
            }
            for alert in active_alerts
        ],
        "recent_alerts": [
            {
                "id": history.id,
                "alert_id": history.alert_id,
                "triggered_at": history.triggered_at.isoformat(),
                "metric_value": history.metric_value,
            }
            for history in recent_alerts
        ],
        "risk_history": [
            {
                "date": metric.metric_date.isoformat(),
                "var_95_hist": metric.var_95_hist,
                "cvar_95": metric.cvar_95,
                "beta": metric.beta,
            }
            for metric in risk_history
        ],
    }


@router.get("/metrics/history")
async def get_risk_metrics_history(
    entity_type: str,
    entity_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
):
    """获取风险指标历史数据"""
    metrics = (
        db.query(RiskMetric)
        .filter(
            RiskMetric.entity_type == entity_type,
            RiskMetric.entity_id == entity_id,
            RiskMetric.metric_date >= start_date,
            RiskMetric.metric_date <= end_date,
        )
        .order_by(RiskMetric.metric_date.asc())
        .all()
    )

    return [
        {
            "date": metric.metric_date.isoformat(),
            "var_95_hist": metric.var_95_hist,
            "var_95_param": metric.var_95_param,
            "cvar_95": metric.cvar_95,
            "beta": metric.beta,
        }
        for metric in metrics
    ]


# ============ 风险预警管理 ============


@router.get("/alerts")
async def list_risk_alerts(
    is_active: Optional[bool] = None, db: Session = Depends(get_db)
):
    """获取风险预警规则列表"""
    query = db.query(RiskAlert)

    if is_active is not None:
        query = query.filter(RiskAlert.is_active == is_active)

    alerts = query.order_by(RiskAlert.created_at.desc()).all()

    return [
        {
            "id": alert.id,
            "name": alert.name,
            "metric_type": alert.metric_type,
            "threshold_value": alert.threshold_value,
            "comparison_operator": alert.comparison_operator,
            "is_active": alert.is_active,
            "notification_channels": alert.notification_channels,
        }
        for alert in alerts
    ]


@router.post("/alerts")
async def create_risk_alert(alert: RiskAlertCreate, db: Session = Depends(get_db)):
    """创建风险预警规则"""
    db_alert = RiskAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    return {"id": db_alert.id, "message": "预警规则已创建"}


@router.put("/alerts/{alert_id}")
async def update_risk_alert(
    alert_id: int, alert_update: RiskAlertUpdate, db: Session = Depends(get_db)
):
    """更新风险预警规则"""
    alert = db.query(RiskAlert).filter(RiskAlert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="预警规则不存在")

    for key, value in alert_update.dict(exclude_unset=True).items():
        setattr(alert, key, value)

    db.commit()
    db.refresh(alert)

    return {"message": "预警规则已更新"}


@router.delete("/alerts/{alert_id}")
async def delete_risk_alert(alert_id: int, db: Session = Depends(get_db)):
    """删除风险预警规则"""
    alert = db.query(RiskAlert).filter(RiskAlert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="预警规则不存在")

    db.delete(alert)
    db.commit()

    return {"message": "预警规则已删除"}


@router.get("/alerts/history")
async def get_alert_history(
    alert_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
):
    """获取预警触发历史"""
    query = db.query(AlertHistory)

    if alert_id:
        query = query.filter(AlertHistory.alert_id == alert_id)

    total = query.count()
    items = (
        query.order_by(AlertHistory.triggered_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": item.id,
                "alert_id": item.alert_id,
                "triggered_at": item.triggered_at.isoformat(),
                "metric_value": item.metric_value,
                "notification_sent": item.notification_sent,
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ============ 通知管理 ============


@router.get("/notifications/config")
async def get_notification_configs(db: Session = Depends(get_db)):
    """获取通知配置列表"""
    configs = db.query(NotificationConfig).all()

    return [
        {
            "id": config.id,
            "config_type": config.config_type,
            "is_enabled": config.is_enabled,
            "config_data": config.config_data,
        }
        for config in configs
    ]


@router.post("/notifications/config")
async def create_notification_config(
    config: NotificationConfigCreate, db: Session = Depends(get_db)
):
    """创建通知配置"""
    db_config = NotificationConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    return {"id": db_config.id, "message": "通知配置已创建"}


@router.put("/notifications/config/{config_id}")
async def update_notification_config(
    config_id: int, config_update: dict, db: Session = Depends(get_db)
):
    """更新通知配置"""
    config = (
        db.query(NotificationConfig).filter(NotificationConfig.id == config_id).first()
    )

    if not config:
        raise HTTPException(status_code=404, detail="通知配置不存在")

    for key, value in config_update.items():
        setattr(config, key, value)

    config.updated_at = datetime.now()
    db.commit()

    return {"message": "通知配置已更新"}


@router.post("/notifications/test/{config_id}")
async def test_notification(config_id: int, db: Session = Depends(get_db)):
    """发送测试通知"""
    config = (
        db.query(NotificationConfig).filter(NotificationConfig.id == config_id).first()
    )

    if not config:
        raise HTTPException(status_code=404, detail="通知配置不存在")

    try:
        notifier = NotificationManager()

        if config.config_type == "email":
            result = notifier.send_email(
                to_addrs=[config.config_data.get("email")],
                subject="MyStocks 测试通知",
                message="这是一封测试邮件，您的邮件配置正常工作！",
            )
        elif config.config_type == "webhook":
            result = notifier.send_webhook(message="MyStocks 测试通知", test=True)
        else:
            raise HTTPException(status_code=400, detail="不支持的通知类型")

        if result:
            return {"success": True, "message": "测试通知发送成功"}
        else:
            return {"success": False, "message": "测试通知发送失败"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")
