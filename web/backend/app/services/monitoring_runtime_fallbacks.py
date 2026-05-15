"""Runtime fallback fixtures for monitoring development and tests."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

from app.models.monitoring import AlertRecordResponse, AlertRuleResponse


_RUNTIME_ALERT_TIMESTAMP = datetime(2026, 3, 13, 10, 0, 0)


def runtime_fallback_enabled() -> bool:
    return (
        os.getenv("TESTING", "false").lower() == "true"
        or os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    )


def build_runtime_alert_rules() -> List[AlertRuleResponse]:
    return [
        AlertRuleResponse(
            id=9001,
            rule_name="核心仓位跌破止损线",
            rule_type="technical_break",
            description="开发态 fallback: 关键持仓跌破止损价时触发",
            symbol="600519",
            stock_name="贵州茅台",
            parameters={"source": "runtime-fallback", "stop_loss_price": 1750},
            trigger_conditions={"operator": "<=", "field": "current_price"},
            notification_config={"channels": ["ui"], "level": "critical"},
            is_active=True,
            priority=5,
            created_at=_RUNTIME_ALERT_TIMESTAMP,
            updated_at=_RUNTIME_ALERT_TIMESTAMP,
        ),
        AlertRuleResponse(
            id=9002,
            rule_name="北向资金快速回落",
            rule_type="price_change",
            description="开发态 fallback: 北向资金与情绪联动观察",
            symbol="000001",
            stock_name="上证指数",
            parameters={"source": "runtime-fallback", "threshold_percent": 1.5},
            trigger_conditions={"operator": "<=", "field": "change_percent"},
            notification_config={"channels": ["ui"], "level": "warning"},
            is_active=True,
            priority=3,
            created_at=_RUNTIME_ALERT_TIMESTAMP,
            updated_at=_RUNTIME_ALERT_TIMESTAMP,
        ),
    ]


def build_runtime_alert_records() -> List[AlertRecordResponse]:
    return [
        AlertRecordResponse(
            id=9101,
            rule_id=9001,
            rule_name="核心仓位跌破止损线",
            symbol="600519",
            stock_name="贵州茅台",
            alert_time=_RUNTIME_ALERT_TIMESTAMP,
            alert_type="technical_break",
            alert_level="critical",
            alert_title="止损预警",
            alert_message="当前价格接近止损线，请优先复核仓位",
            alert_details={"source": "runtime-fallback", "stop_loss_price": 1750},
            snapshot_data={"current_price": 1762.0, "distance_to_stop": 0.69},
            is_read=False,
            is_handled=False,
            created_at=_RUNTIME_ALERT_TIMESTAMP,
        ),
        AlertRecordResponse(
            id=9102,
            rule_id=9002,
            rule_name="北向资金快速回落",
            symbol="000001",
            stock_name="上证指数",
            alert_time=_RUNTIME_ALERT_TIMESTAMP,
            alert_type="price_change",
            alert_level="warning",
            alert_title="资金波动提醒",
            alert_message="指数回撤超出监控阈值，建议关注板块扩散风险",
            alert_details={"source": "runtime-fallback", "threshold_percent": 1.5},
            snapshot_data={"change_percent": -1.21},
            is_read=False,
            is_handled=False,
            created_at=_RUNTIME_ALERT_TIMESTAMP,
        ),
    ]


def resolve_query_int(value: object, default: int) -> int:
    if isinstance(value, int):
        return value
    return int(getattr(value, "default", default))
