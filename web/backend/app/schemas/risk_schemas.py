"""
风险管理 API Pydantic 数据模型

定义风险管理相关的Pydantic模型，用于API请求和响应，增强类型校验和文档生成。

版本: 1.0.0
日期: 2025-12-26
"""

from datetime import date as date_type
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# 请求模型
# ============================================================================


class VaRCVaRRequest(BaseModel):
    """VaR/CVaR 计算请求模型"""

    entity_type: str = Field(..., description="实体类型 ('backtest', 'portfolio', 'strategy')")
    entity_id: int = Field(..., description="实体ID", ge=1)
    confidence_level: float = Field(0.95, description="置信水平 (e.g., 0.90, 0.95, 0.99)", ge=0.01, le=0.9999)

    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "portfolio",
                "entity_id": 101,
                "confidence_level": 0.95,
            }
        }


class BetaRequest(BaseModel):
    """Beta 系数计算请求模型"""

    entity_type: str = Field(..., description="实体类型 ('backtest', 'portfolio', 'strategy')")
    entity_id: int = Field(..., description="实体ID", ge=1)
    market_index: str = Field("000001", description="市场指数代码 (默认上证指数)")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "portfolio",
                "entity_id": 101,
                "market_index": "000300.SH",
            }
        }


class RiskAlertCreate(BaseModel):
    """创建风险预警规则请求模型"""

    name: str = Field(..., description="预警规则名称", min_length=1, max_length=100)
    metric_type: str = Field(..., description="监控指标类型 (e.g., 'VaR', 'MaxDrawdown', 'Beta')")
    threshold_value: float = Field(..., description="阈值")
    condition: str = Field(..., description="触发条件 (e.g., '>', '<', '=')", pattern=r"^[<>=!]+$")
    entity_type: str = Field(..., description="关联实体类型 ('portfolio', 'strategy', 'system')")
    entity_id: Optional[int] = Field(None, description="关联实体ID (可选)")
    is_active: bool = Field(True, description="是否启用")
    notification_channels: List[str] = Field(default_factory=list, description="通知渠道 (e.g., 'email', 'webhook')")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "组合VaR超限预警",
                "metric_type": "VaR",
                "threshold_value": 0.05,
                "condition": ">",
                "entity_type": "portfolio",
                "entity_id": 101,
                "is_active": True,
                "notification_channels": ["email"],
            }
        }


class RiskAlertUpdate(BaseModel):
    """更新风险预警规则请求模型"""

    name: Optional[str] = Field(None, description="预警规则名称", min_length=1, max_length=100)
    metric_type: Optional[str] = Field(None, description="监控指标类型")
    threshold_value: Optional[float] = Field(None, description="阈值")
    condition: Optional[str] = Field(None, description="触发条件", pattern=r"^[<>=!]+$")
    entity_type: Optional[str] = Field(None, description="关联实体类型")
    entity_id: Optional[int] = Field(None, description="关联实体ID")
    is_active: Optional[bool] = Field(None, description="是否启用")
    notification_channels: Optional[List[str]] = Field(None, description="通知渠道")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "组合VaR超限预警 (更新)",
                "threshold_value": 0.06,
                "is_active": False,
            }
        }


class NotificationTestRequest(BaseModel):
    """测试通知请求模型"""

    notification_type: str = Field(..., description="通知类型 (e.g., 'email', 'webhook')")
    config_data: Dict[str, Any] = Field(..., description="通知配置数据 (e.g., {'email': 'test@example.com'})")

    class Config:
        json_schema_extra = {
            "example": {
                "notification_type": "email",
                "config_data": {"email": "test@example.com", "subject": "Test", "message": "Hello"},
            }
        }


# ============================================================================
# 响应模型
# ============================================================================


class VaRCVaRResult(BaseModel):
    """VaR/CVaR 计算结果响应模型"""

    var_95_hist: Optional[float] = Field(None, description="95% 历史 VaR")
    var_95_param: Optional[float] = Field(None, description="95% 参数 VaR")
    var_99_hist: Optional[float] = Field(None, description="99% 历史 VaR")
    cvar_95: Optional[float] = Field(None, description="95% CVaR")
    cvar_99: Optional[float] = Field(None, description="99% CVaR")
    entity_type: Optional[str] = Field(None, description="实体类型")
    entity_id: Optional[int] = Field(None, description="实体ID")
    confidence_level: Optional[float] = Field(None, description="置信水平")

    class Config:
        json_schema_extra = {
            "example": {
                "var_95_hist": -0.0289,
                "var_95_param": -0.0309,
                "var_99_hist": -0.0385,
                "cvar_95": -0.0360,
                "cvar_99": -0.0432,
            }
        }


class BetaResult(BaseModel):
    """Beta 系数计算结果响应模型"""

    beta: Optional[float] = Field(None, description="Beta 系数")
    correlation: Optional[float] = Field(None, description="与市场指数的相关系数")
    entity_type: Optional[str] = Field(None, description="实体类型")
    entity_id: Optional[int] = Field(None, description="实体ID")
    market_index: Optional[str] = Field(None, description="市场指数代码")

    class Config:
        json_schema_extra = {
            "example": {
                "beta": 1.23,
                "correlation": 0.85,
            }
        }


class RiskMetricsSummary(BaseModel):
    """风险指标汇总模型"""

    var_95_hist: Optional[float] = Field(None, description="最新 95% 历史 VaR")
    cvar_95: Optional[float] = Field(None, description="最新 95% CVaR")
    beta: Optional[float] = Field(None, description="最新 Beta 系数")


class ActiveAlert(BaseModel):
    """活跃预警模型"""

    id: int = Field(..., description="预警ID")
    name: str = Field(..., description="预警名称")
    metric_type: str = Field(..., description="监控指标类型")
    threshold_value: float = Field(..., description="阈值")


class RiskHistoryPoint(BaseModel):
    """风险历史数据点模型"""

    date: date_type = Field(..., description="日期")
    var_95_hist: Optional[float] = Field(None, description="95% 历史 VaR")
    cvar_95: Optional[float] = Field(None, description="95% CVaR")
    beta: Optional[float] = Field(None, description="Beta 系数")


class RiskDashboardResponse(BaseModel):
    """风险仪表盘响应模型"""

    metrics: RiskMetricsSummary = Field(..., description="风险指标汇总")
    active_alerts: List[ActiveAlert] = Field(default_factory=list, description="活跃预警列表")
    risk_history: List[RiskHistoryPoint] = Field(default_factory=list, description="风险历史数据")

    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "var_95_hist": -0.025,
                    "cvar_95": -0.03,
                    "beta": 1.1,
                },
                "active_alerts": [
                    {
                        "id": 1,
                        "name": "VaR超限",
                        "metric_type": "VaR",
                        "threshold_value": 0.03,
                    }
                ],
                "risk_history": [
                    {"date": "2024-01-01", "var_95_hist": -0.01, "cvar_95": -0.015, "beta": 1.0},
                    {"date": "2024-01-02", "var_95_hist": -0.012, "cvar_95": -0.018, "beta": 1.05},
                ],
            }
        }


class RiskMetricsHistoryResponse(BaseModel):
    """风险指标历史响应模型 (单实体)"""

    metrics_history: List[RiskHistoryPoint] = Field(default_factory=list, description="单个实体风险指标历史数据")

    class Config:
        json_schema_extra = {
            "example": {
                "metrics_history": [
                    {"date": "2024-01-01", "var_95_hist": -0.01, "cvar_95": -0.015, "beta": 1.0},
                    {"date": "2024-01-02", "var_95_hist": -0.012, "cvar_95": -0.018, "beta": 1.05},
                ]
            }
        }


class RiskAlertResponse(BaseModel):
    """风险预警规则响应模型"""

    id: int = Field(..., description="预警ID")
    name: str = Field(..., description="预警规则名称")
    metric_type: str = Field(..., description="监控指标类型")
    threshold_value: float = Field(..., description="阈值")
    condition: str = Field(..., description="触发条件")
    entity_type: str = Field(..., description="关联实体类型")
    entity_id: Optional[int] = Field(None, description="关联实体ID")
    is_active: bool = Field(..., description="是否启用")
    notification_channels: List[str] = Field(default_factory=list, description="通知渠道")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "组合VaR超限预警",
                "metric_type": "VaR",
                "threshold_value": 0.05,
                "condition": ">",
                "entity_type": "portfolio",
                "entity_id": 101,
                "is_active": True,
                "notification_channels": ["email"],
                "created_at": "2024-12-26T10:00:00",
                "updated_at": "2024-12-26T11:00:00",
            }
        }


class RiskAlertListResponse(BaseModel):
    """风险预警规则列表响应模型"""

    alerts: List[RiskAlertResponse] = Field(default_factory=list, description="风险预警规则列表")

    class Config:
        json_schema_extra = {
            "example": {
                "alerts": [
                    {
                        "id": 1,
                        "name": "组合VaR超限预警",
                        "metric_type": "VaR",
                        "threshold_value": 0.05,
                        "condition": ">",
                        "entity_type": "portfolio",
                        "entity_id": 101,
                        "is_active": True,
                        "notification_channels": ["email"],
                        "created_at": "2024-12-26T10:00:00",
                        "updated_at": "2024-12-26T11:00:00",
                    }
                ]
            }
        }


class NotificationTestResponse(BaseModel):
    """测试通知响应模型"""

    success: bool = Field(..., description="是否成功发送")
    message: str = Field(..., description="消息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "测试通知发送成功",
            }
        }
