"""Response examples and OpenAPI response specs for alerts."""

from typing import Any, Dict, List, Optional
from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.openapi_config import COMMON_RESPONSES

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
