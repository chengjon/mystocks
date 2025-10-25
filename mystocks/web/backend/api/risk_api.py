"""
风险监控 API

提供VaR/CVaR计算、Beta分析、风险预警等接口
使用 MyStocksUnifiedManager 统一数据访问 + MonitoringDatabase 监控集成

Author: JohnC & Claude
Version: 2.0.0 (Architecture Compliant)
Date: 2025-10-24
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 使用 MyStocksUnifiedManager 作为统一入口点
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
from analysis import ExtendedRiskMetrics
from utils import NotificationManager
from monitoring.monitoring_database import MonitoringDatabase

router = APIRouter(prefix="/api/v1/risk", tags=["风险监控"])

# 初始化监控数据库
monitoring_db = MonitoringDatabase()


# ============ 风险指标计算 ============

@router.get("/var-cvar")
async def calculate_var_cvar(
    entity_type: str,
    entity_id: int,
    confidence_level: float = 0.95
) -> Dict[str, float]:
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
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()

        # 获取收益率数据
        # 实际应该根据entity_type和entity_id从backtest_trades或其他表获取
        # returns = get_returns_data(entity_type, entity_id)

        # 模拟数据
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))

        # 计算风险指标
        metrics = ExtendedRiskMetrics.calculate_all(returns)

        # 保存到数据库（使用 UnifiedManager）
        risk_data = pd.DataFrame([{
            'entity_type': entity_type,
            'entity_id': entity_id,
            'metric_date': datetime.now().date(),
            'var_95_hist': metrics['var_95_hist'],
            'var_95_param': metrics['var_95_param'],
            'var_99_hist': metrics['var_99_hist'],
            'cvar_95': metrics['cvar_95'],
            'cvar_99': metrics['cvar_99'],
            'created_at': datetime.now()
        }])

        result = manager.save_data_by_classification(
            data=risk_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_metrics'
        )

        # 记录操作到监控数据库
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type='RISK_CALCULATION',
            table_name='risk_metrics',
            operation_name='calculate_var_cvar',
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result,
            details=f"entity_type={entity_type}, entity_id={entity_id}"
        )

        if not result:
            raise HTTPException(status_code=500, detail="保存风险指标失败")

        return metrics

    except Exception as e:
        # 记录失败操作
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type='RISK_CALCULATION',
            table_name='risk_metrics',
            operation_name='calculate_var_cvar',
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"计算VaR/CVaR失败: {str(e)}")


@router.get("/beta")
async def calculate_beta(
    entity_type: str,
    entity_id: int,
    market_index: str = "000001"  # 默认上证指数
) -> Dict[str, float]:
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
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()

        # 获取资产和市场收益率数据
        # asset_returns = get_returns_data(entity_type, entity_id)
        # market_returns = get_market_returns(market_index)

        # 模拟数据
        np.random.seed(42)
        asset_returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        market_returns = pd.Series(np.random.normal(0.0008, 0.015, 252))

        # 计算Beta
        beta = ExtendedRiskMetrics.beta(asset_returns, market_returns)

        # 计算相关系数
        correlation = float(asset_returns.corr(market_returns))

        # 更新或创建风险指标记录
        risk_data = pd.DataFrame([{
            'entity_type': entity_type,
            'entity_id': entity_id,
            'metric_date': datetime.now().date(),
            'beta': beta,
            'created_at': datetime.now()
        }])

        result = manager.save_data_by_classification(
            data=risk_data,
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_metrics',
            upsert=True
        )

        # 记录操作到监控数据库
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type='RISK_CALCULATION',
            table_name='risk_metrics',
            operation_name='calculate_beta',
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result
        )

        return {
            "beta": beta,
            "correlation": correlation
        }

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type='RISK_CALCULATION',
            table_name='risk_metrics',
            operation_name='calculate_beta',
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"计算Beta失败: {str(e)}")


@router.get("/dashboard")
async def get_risk_dashboard() -> Dict[str, Any]:
    """
    获取风险仪表盘数据

    Returns:
        {
            "metrics": {...},
            "active_alerts": [...],
            "risk_history": [...]
        }
    """
    try:
        manager = MyStocksUnifiedManager()

        # 获取最新风险指标
        metrics_df = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_metrics'
        )

        latest_metrics = None
        if metrics_df is not None and len(metrics_df) > 0:
            latest_metrics = metrics_df.sort_values('metric_date', ascending=False).iloc[0].to_dict()

        # 获取活跃预警规则
        alerts_df = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_alerts',
            filters={'is_active': True}
        )

        active_alerts = alerts_df.to_dict('records') if alerts_df is not None else []

        # 获取风险历史（最近30天）
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
        # 注意：这里简化了过滤逻辑，实际应该支持日期范围过滤
        history_df = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_metrics'
        )

        risk_history = []
        if history_df is not None:
            history_df = history_df[history_df['metric_date'] >= pd.Timestamp(thirty_days_ago)]
            risk_history = history_df.sort_values('metric_date').to_dict('records')

        return {
            "metrics": {
                "var_95_hist": latest_metrics.get('var_95_hist') if latest_metrics else None,
                "cvar_95": latest_metrics.get('cvar_95') if latest_metrics else None,
                "beta": latest_metrics.get('beta') if latest_metrics else None,
            },
            "active_alerts": [
                {
                    "id": alert['id'],
                    "name": alert['name'],
                    "metric_type": alert['metric_type'],
                    "threshold_value": alert['threshold_value']
                }
                for alert in active_alerts
            ],
            "risk_history": [
                {
                    "date": metric['metric_date'].isoformat() if hasattr(metric['metric_date'], 'isoformat') else str(metric['metric_date']),
                    "var_95_hist": metric.get('var_95_hist'),
                    "cvar_95": metric.get('cvar_95'),
                    "beta": metric.get('beta')
                }
                for metric in risk_history
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")


@router.get("/metrics/history")
async def get_risk_metrics_history(
    entity_type: str,
    entity_id: int,
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """获取风险指标历史数据"""
    try:
        manager = MyStocksUnifiedManager()

        # 获取风险指标数据
        metrics_df = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_metrics',
            filters={
                'entity_type': entity_type,
                'entity_id': entity_id
            }
        )

        if metrics_df is None or len(metrics_df) == 0:
            return []

        # 日期过滤
        metrics_df = metrics_df[
            (metrics_df['metric_date'] >= pd.Timestamp(start_date)) &
            (metrics_df['metric_date'] <= pd.Timestamp(end_date))
        ]

        return [
            {
                "date": metric['metric_date'].isoformat() if hasattr(metric['metric_date'], 'isoformat') else str(metric['metric_date']),
                "var_95_hist": metric.get('var_95_hist'),
                "var_95_param": metric.get('var_95_param'),
                "cvar_95": metric.get('cvar_95'),
                "beta": metric.get('beta')
            }
            for metric in metrics_df.sort_values('metric_date').to_dict('records')
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


# ============ 风险预警管理 ============

@router.get("/alerts")
async def list_risk_alerts(is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
    """获取风险预警规则列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active

        alerts_df = manager.load_data_by_classification(
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_alerts',
            filters=filters
        )

        return alerts_df.to_dict('records') if alerts_df is not None else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警列表失败: {str(e)}")


@router.post("/alerts")
async def create_risk_alert(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建风险预警规则"""
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()

        # 添加时间戳
        alert_data['created_at'] = datetime.now()
        alert_data['is_active'] = alert_data.get('is_active', True)

        alert_df = pd.DataFrame([alert_data])

        result = manager.save_data_by_classification(
            data=alert_df,
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_alerts'
        )

        # 记录操作
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type='INSERT',
            table_name='risk_alerts',
            operation_name='create_risk_alert',
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result
        )

        if result:
            return {"message": "预警规则已创建", "data": alert_data}
        else:
            raise HTTPException(status_code=500, detail="创建预警规则失败")

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        monitoring_db.log_operation(
            operation_type='INSERT',
            table_name='risk_alerts',
            operation_name='create_risk_alert',
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"创建预警规则失败: {str(e)}")


@router.put("/alerts/{alert_id}")
async def update_risk_alert(
    alert_id: int,
    alert_update: Dict[str, Any]
) -> Dict[str, str]:
    """更新风险预警规则"""
    try:
        manager = MyStocksUnifiedManager()

        alert_update['id'] = alert_id

        alert_df = pd.DataFrame([alert_update])

        result = manager.save_data_by_classification(
            data=alert_df,
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_alerts',
            upsert=True
        )

        if result:
            return {"message": "预警规则已更新"}
        else:
            raise HTTPException(status_code=500, detail="更新预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新预警规则失败: {str(e)}")


@router.delete("/alerts/{alert_id}")
async def delete_risk_alert(alert_id: int) -> Dict[str, str]:
    """删除风险预警规则（软删除：设置为非活跃）"""
    try:
        manager = MyStocksUnifiedManager()

        # 软删除：更新is_active为False
        alert_df = pd.DataFrame([{
            'id': alert_id,
            'is_active': False
        }])

        result = manager.save_data_by_classification(
            data=alert_df,
            data_classification=DataClassification.DERIVED_DATA,
            table_name='risk_alerts',
            upsert=True
        )

        if result:
            return {"message": "预警规则已禁用"}
        else:
            raise HTTPException(status_code=500, detail="删除预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除预警规则失败: {str(e)}")


# ============ 通知管理 ============

@router.post("/notifications/test")
async def test_notification(
    notification_type: str,
    config_data: Dict[str, Any]
) -> Dict[str, Any]:
    """发送测试通知"""
    try:
        notifier = NotificationManager()

        if notification_type == 'email':
            result = notifier.send_email(
                to_addrs=[config_data.get('email')],
                subject="MyStocks 测试通知",
                message="这是一封测试邮件，您的邮件配置正常工作！"
            )
        elif notification_type == 'webhook':
            result = notifier.send_webhook(
                message="MyStocks 测试通知",
                test=True
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的通知类型")

        if result:
            return {"success": True, "message": "测试通知发送成功"}
        else:
            return {"success": False, "message": "测试通知发送失败"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")
