"""
监控系统 API 端点
Real-time Monitoring System
"""

import asyncio
import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import BaseModel, Field

from app.core.exceptions import BusinessException, NotFoundException
from app.core.responses import UnifiedResponse, create_unified_success_response
from app.core.security import User, get_current_user
from app.mock.unified_mock_data import get_mock_data_manager
from app.models.monitoring import (
    AlertLevel,
    AlertRecordResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleType,
    AlertRuleUpdate,
    DragonTigerListResponse,
    MonitoringSummaryResponse,
    RealtimeMonitoringResponse,
)
from app.services.monitoring_service import monitoring_service

router = APIRouter()

_RUNTIME_ALERT_TIMESTAMP = datetime(2026, 3, 13, 10, 0, 0)
_monitoring_control_state: Dict[str, Any] = {
    "task": None,
    "interval": None,
    "last_started_at": None,
}


def _success_response_spec(status_code: int, description: str, example: object) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


ALERT_RULES_LIST_RESPONSES = {
    **_error_response_spec(
        500,
        "获取告警规则列表失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "告警规则列表",
        {
            "success": True,
            "code": 200,
            "message": "获取告警规则成功",
            "data": [
                {
                    "id": 9001,
                    "rule_name": "核心仓位跌破止损线",
                    "rule_type": "technical_break",
                    "description": "关键持仓跌破止损价时触发",
                    "symbol": "600519",
                    "stock_name": "贵州茅台",
                    "parameters": {"stop_loss_price": 1750},
                    "trigger_conditions": {"operator": "<=", "field": "current_price"},
                    "notification_config": {"channels": ["ui"], "level": "critical"},
                    "is_active": True,
                    "priority": 5,
                    "created_at": "2026-03-13T10:00:00",
                    "updated_at": "2026-03-13T10:00:00",
                }
            ],
            "timestamp": "2026-04-05T12:00:00Z",
            "request_id": "req-monitoring-rules-001",
            "errors": None,
        },
    ),
}

ALERT_RULE_CREATE_RESPONSES = {
    **_error_response_spec(
        400,
        "创建告警规则请求无效",
        {"detail": "规则名称不能为空", "error_code": "INVALID_MONITORING_REQUEST"},
    ),
    **_success_response_spec(
        200,
        "告警规则创建成功",
        {
            "id": 9201,
            "rule_name": "茅台涨停监控",
            "rule_type": "limit_up",
            "description": "茅台涨停时触发提醒",
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "parameters": {"include_st": False},
            "trigger_conditions": {"field": "change_percent", "operator": ">=", "value": 9.8},
            "notification_config": {"channels": ["ui", "sound"], "level": "warning"},
            "is_active": True,
            "priority": 5,
            "created_at": "2026-04-05T12:00:00",
            "updated_at": "2026-04-05T12:00:00",
        },
    ),
}

ALERT_RULE_UPDATE_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定告警规则",
        {"detail": "未找到监控数据: 9201", "error_code": "RESOURCE_NOT_FOUND"},
    ),
    **_error_response_spec(
        400,
        "更新告警规则请求无效",
        {"detail": "优先级超出范围", "error_code": "INVALID_MONITORING_REQUEST"},
    ),
    **_success_response_spec(
        200,
        "告警规则更新成功",
        {
            "id": 9201,
            "rule_name": "茅台涨停监控",
            "rule_type": "limit_up",
            "description": "更新后的涨停提醒规则",
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "parameters": {"include_st": False},
            "trigger_conditions": {"field": "change_percent", "operator": ">=", "value": 9.8},
            "notification_config": {"channels": ["ui"], "level": "critical"},
            "is_active": True,
            "priority": 4,
            "created_at": "2026-04-05T10:00:00",
            "updated_at": "2026-04-05T12:00:00",
        },
    ),
}

ALERT_RULE_DELETE_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定告警规则",
        {"detail": "未找到监控数据: 9201", "error_code": "RESOURCE_NOT_FOUND"},
    ),
    **_error_response_spec(
        400,
        "删除告警规则请求无效",
        {"detail": "删除失败", "error_code": "INVALID_MONITORING_REQUEST"},
    ),
    **_success_response_spec(
        200,
        "告警规则删除成功",
        {"success": True, "message": "告警规则已删除"},
    ),
}

ALERT_MARK_READ_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定告警记录",
        {"detail": "未找到告警记录: 查询条件", "error_code": "RESOURCE_NOT_FOUND"},
    ),
    **_error_response_spec(
        500,
        "标记告警已读失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "告警已标记为已读",
        {"success": True, "message": "已标记为已读"},
    ),
}

ALERT_MARK_ALL_READ_RESPONSES = {
    **_error_response_spec(
        500,
        "批量标记告警已读失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "批量标记全部告警已读结果",
        {
            "success": True,
            "code": 200,
            "message": "全部告警已标记为已读",
            "data": {
                "status": "updated",
                "scope": "all_alerts",
                "updated_count": 5,
            },
        },
    ),
}

ALERT_RECORDS_LIST_RESPONSES = {
    **_error_response_spec(
        500,
        "获取告警记录列表失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "告警记录列表",
        {
            "success": True,
            "data": [
                {
                    "id": 9101,
                    "rule_id": 9001,
                    "rule_name": "核心仓位跌破止损线",
                    "symbol": "600519",
                    "stock_name": "贵州茅台",
                    "alert_time": "2026-04-05T14:31:00",
                    "alert_type": "technical_break",
                    "alert_level": "critical",
                    "alert_title": "止损预警",
                    "alert_message": "当前价格接近止损线，请优先复核仓位",
                    "alert_details": {"stop_loss_price": 1750.0},
                    "snapshot_data": {"current_price": 1762.0, "distance_to_stop": 0.69},
                    "is_read": False,
                    "is_handled": False,
                    "created_at": "2026-04-05T14:31:00",
                }
            ],
            "total": 1,
            "limit": 100,
            "offset": 0,
        },
    ),
}

REALTIME_MONITORING_DETAIL_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的实时监控数据",
        {"detail": "未找到股票监控数据: 查询条件", "error_code": "RESOURCE_NOT_FOUND"},
    ),
    **_error_response_spec(
        500,
        "获取实时监控数据失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "单只股票的最新实时监控数据",
        {
            "id": 3101,
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "timestamp": "2026-04-05T14:30:00",
            "trade_date": "2026-04-05",
            "price": 1718.5,
            "change_percent": 2.31,
            "volume": 328700,
            "amount": 564321000.0,
            "indicators": {"macd": 1.25, "rsi": 63.4},
            "market_strength": "strong",
            "is_limit_up": False,
            "is_limit_down": False,
        },
    ),
}

REALTIME_MONITORING_LIST_RESPONSES = {
    **_error_response_spec(
        500,
        "获取实时监控列表失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "实时监控数据列表",
        [
            {
                "id": 3101,
                "symbol": "600519",
                "stock_name": "贵州茅台",
                "timestamp": "2026-04-05T14:30:00",
                "trade_date": "2026-04-05",
                "price": 1718.5,
                "change_percent": 2.31,
                "volume": 328700,
                "amount": 564321000.0,
                "indicators": {"macd": 1.25, "rsi": 63.4},
                "market_strength": "strong",
                "is_limit_up": False,
                "is_limit_down": False,
            },
            {
                "id": 3102,
                "symbol": "000001",
                "stock_name": "平安银行",
                "timestamp": "2026-04-05T14:30:00",
                "trade_date": "2026-04-05",
                "price": 12.86,
                "change_percent": -0.72,
                "volume": 512600,
                "amount": 65910400.0,
                "indicators": {"macd": -0.12, "rsi": 46.1},
                "market_strength": "neutral",
                "is_limit_up": False,
                "is_limit_down": False,
            },
        ],
    ),
}

FETCH_REALTIME_DATA_RESPONSES = {
    **_error_response_spec(
        500,
        "触发实时数据抓取失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "实时数据抓取任务执行结果",
        {
            "success": True,
            "message": "实时数据获取成功",
            "data": {"stocks_count": 3, "saved_count": 3, "alerts_triggered": 1},
        },
    ),
}

FETCH_DRAGON_TIGER_DATA_RESPONSES = {
    **_error_response_spec(
        500,
        "触发龙虎榜数据抓取失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "龙虎榜数据抓取结果",
        {
            "success": True,
            "message": "龙虎榜数据获取成功",
            "data": {"trade_date": "2026-04-05", "count": 12},
        },
    ),
}

DRAGON_TIGER_LIST_RESPONSES = {
    **_error_response_spec(
        500,
        "获取龙虎榜列表失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "龙虎榜记录列表",
        [
            {
                "id": 7101,
                "symbol": "600519",
                "stock_name": "贵州茅台",
                "trade_date": "2026-04-05",
                "reason": "日涨幅偏离值达到 7%",
                "total_buy_amount": 356000000.0,
                "total_sell_amount": 210000000.0,
                "net_amount": 146000000.0,
                "institution_buy_count": 3,
                "institution_sell_count": 1,
                "institution_net_amount": 92000000.0,
                "detail_data": {"top_buy_seat": "机构专用", "top_sell_seat": "沪股通专用"},
                "impact_score": 8,
            }
        ],
    ),
}

MONITORING_SUMMARY_RESPONSES = {
    **_error_response_spec(
        500,
        "获取监控摘要失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "监控摘要信息",
        {
            "total_stocks": 1568,
            "limit_up_count": 23,
            "limit_down_count": 5,
            "strong_up_count": 127,
            "strong_down_count": 89,
            "avg_change_percent": 0.85,
            "total_amount": 2456789000.0,
            "active_alerts": 12,
            "unread_alerts": 5,
        },
    ),
}

TODAY_STATS_RESPONSES = {
    **_error_response_spec(
        500,
        "获取今日监控统计失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "今日监控统计结果",
        {
            "success": True,
            "data": {
                "alerts_summary": [{"alert_level": "warning", "alert_count": 8}],
                "active_rules": [{"id": 9001, "rule_name": "核心仓位跌破止损线", "priority": 5}],
                "realtime_summary": {
                    "total_stocks": 1568,
                    "limit_up_count": 23,
                    "limit_down_count": 5,
                    "active_alerts": 12,
                },
            },
        },
    ),
}

START_MONITORING_RESPONSES = {
    **_error_response_spec(
        500,
        "启动监控失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "监控启动结果",
        {
            "success": True,
            "code": 200,
            "message": "监控已启动",
            "data": {
                "is_monitoring": True,
                "monitored_symbols": ["600519", "000001"],
                "monitored_count": 2,
                "interval": 30,
            },
        },
    ),
}

STOP_MONITORING_RESPONSES = {
    **_error_response_spec(
        500,
        "停止监控失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "监控已停止",
        {
            "success": True,
            "code": 200,
            "message": "监控已停止",
            "data": {
                "is_monitoring": False,
                "monitored_symbols": [],
                "monitored_count": 0,
            },
        },
    ),
}

MONITORING_STATUS_RESPONSES = {
    **_error_response_spec(
        500,
        "获取监控运行状态失败",
        {"detail": "监控服务不可用", "error_code": "MONITORING_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        200,
        "监控运行状态",
        {
            "success": True,
            "code": 200,
            "message": "获取监控状态成功",
            "data": {
                "is_monitoring": True,
                "monitored_symbols": ["600519", "000001", "601318"],
                "monitored_count": 3,
                "update_interval": 30,
            },
        },
    ),
}


def _runtime_fallback_enabled() -> bool:
    return (
        os.getenv("TESTING", "false").lower() == "true"
        or os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    )


def _build_runtime_alert_rules() -> List[AlertRuleResponse]:
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


def _build_runtime_alert_records() -> List[AlertRecordResponse]:
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


def _resolve_query_int(value: object, default: int) -> int:
    if isinstance(value, int):
        return value
    return int(getattr(value, "default", default))


def _build_monitoring_control_payload(*, include_interval_key: Optional[str] = None) -> Dict[str, Any]:
    symbols = list(monitoring_service.monitored_symbols or [])
    payload: Dict[str, Any] = {
        "is_monitoring": bool(monitoring_service.is_monitoring),
        "monitored_symbols": symbols,
        "monitored_count": len(symbols),
    }
    if include_interval_key:
        payload[include_interval_key] = _monitoring_control_state["interval"]
    return payload


def _get_monitoring_task() -> Optional[asyncio.Task]:
    task = _monitoring_control_state["task"]
    if task is not None and task.done() and not monitoring_service.is_monitoring:
        _monitoring_control_state["task"] = None
        return None
    return task


# ============================================================================
# 告警规则管理
# ============================================================================


@router.get(
    "/alert-rules",
    response_model=UnifiedResponse[List[AlertRuleResponse]],
    summary="获取告警规则列表",
    description="查询监控告警规则列表，支持按规则类型和启用状态过滤。",
    responses=ALERT_RULES_LIST_RESPONSES,
)
async def get_alert_rules(
    rule_type: Optional[AlertRuleType] = Query(None, description="规则类型过滤条件，例如 limit_up 或 technical_break。"),
    is_active: Optional[bool] = Query(None, description="按启用状态过滤，true 表示仅返回启用规则。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取告警规则列表

    参数:
    - rule_type: 规则类型 (可选)
    - is_active: 是否启用 (可选)
    """
    try:
        rules = monitoring_service.get_alert_rules(
            rule_type=rule_type.value if rule_type else None, is_active=is_active
        )
        return create_unified_success_response(
            data=[AlertRuleResponse.from_orm(rule) for rule in rules],
            message="获取告警规则成功",
        )
    except Exception as e:
        if _runtime_fallback_enabled():
            return create_unified_success_response(
                data=_build_runtime_alert_rules(),
                message="获取告警规则成功",
            )
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/alert-rules",
    response_model=AlertRuleResponse,
    summary="创建告警规则",
    description="创建新的监控告警规则，定义触发条件、通知方式和优先级。",
    responses=ALERT_RULE_CREATE_RESPONSES,
)
async def create_alert_rule(
    rule: AlertRuleCreate = Body(
        ...,
        example={
            "rule_name": "茅台涨停监控",
            "rule_type": "limit_up",
            "description": "茅台涨停时触发提醒",
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "parameters": {"include_st": False},
            "trigger_conditions": {"field": "change_percent", "operator": ">=", "value": 9.8},
            "notification_config": {"channels": ["ui", "sound"], "level": "warning"},
            "priority": 5,
            "is_active": True,
        },
    ),
    current_user: User = Depends(get_current_user),
):
    """
    创建告警规则

    示例:
    ```json
    {
      "rule_name": "茅台涨停监控",
      "rule_type": "limit_up",
      "symbol": "600519",
      "stock_name": "贵州茅台",
      "parameters": {"include_st": false},
      "notification_config": {"channels": ["ui", "sound"], "level": "warning"},
      "priority": 5,
      "is_active": true
    }
    ```
    """
    try:
        rule_data = rule.dict()
        created_rule = monitoring_service.create_alert_rule(rule_data)
        return AlertRuleResponse.from_orm(created_rule)
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="INVALID_MONITORING_REQUEST")


@router.put(
    "/alert-rules/{rule_id}",
    response_model=AlertRuleResponse,
    summary="更新告警规则",
    description="按规则 ID 更新告警规则的部分字段，例如通知配置、优先级或启用状态。",
    responses=ALERT_RULE_UPDATE_RESPONSES,
)
async def update_alert_rule(
    rule_id: int = Path(..., description="告警规则 ID。"),
    updates: AlertRuleUpdate = Body(
        ...,
        example={
            "description": "更新后的涨停提醒规则",
            "notification_config": {"channels": ["ui"], "level": "critical"},
            "priority": 4,
            "is_active": True,
        },
    ),
    current_user: User = Depends(get_current_user),
):
    """
    更新告警规则

    参数:
    - rule_id: 规则ID
    - updates: 要更新的字段
    """
    try:
        update_data = updates.dict(exclude_unset=True)
        updated_rule = monitoring_service.update_alert_rule(rule_id, update_data)
        return AlertRuleResponse.from_orm(updated_rule)
    except ValueError as e:
        raise NotFoundException(resource="监控数据", identifier=str(e))
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="INVALID_MONITORING_REQUEST")


@router.delete(
    "/alert-rules/{rule_id}",
    summary="删除告警规则",
    description="按规则 ID 删除指定告警规则，用于停用不再需要的监控配置。",
    responses=ALERT_RULE_DELETE_RESPONSES,
)
async def delete_alert_rule(
    rule_id: int = Path(..., description="告警规则 ID。"),
    current_user: User = Depends(get_current_user),
):
    """
    删除告警规则

    参数:
    - rule_id: 规则ID
    """
    try:
        success = monitoring_service.delete_alert_rule(rule_id)
        return {"success": success, "message": "告警规则已删除"}
    except ValueError as e:
        raise NotFoundException(resource="监控数据", identifier=str(e))
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=400, error_code="INVALID_MONITORING_REQUEST")


# ============================================================================
# 告警记录查询
# ============================================================================


class AlertRecordsResponse(BaseModel):
    """告警记录列表响应"""

    success: bool = Field(True, description="查询是否成功。")
    data: List[AlertRecordResponse] = Field(..., description="告警记录列表。")
    total: int = Field(..., description="符合筛选条件的告警总数。")
    limit: int = Field(..., description="当前请求返回上限。")
    offset: int = Field(..., description="当前分页偏移量。")


@router.get(
    "/alerts",
    response_model=AlertRecordsResponse,
    summary="获取告警记录列表",
    description="查询监控告警记录，支持按股票、告警类型、等级、已读状态和日期区间进行筛选分页。",
    responses=ALERT_RECORDS_LIST_RESPONSES,
)
async def get_alert_records(
    symbol: Optional[str] = Query(None, description="按股票代码筛选告警记录。"),
    alert_type: Optional[str] = Query(None, description="按告警类型筛选，例如 limit_up 或 volume_spike。"),
    alert_level: Optional[AlertLevel] = Query(None, description="按告警等级筛选，例如 info、warning 或 critical。"),
    is_read: Optional[bool] = Query(None, description="按已读状态筛选告警记录。"),
    start_date: Optional[date] = Query(None, description="限制返回结果的开始日期，包含当天。"),
    end_date: Optional[date] = Query(None, description="限制返回结果的结束日期，包含当天。"),
    limit: int = Query(100, ge=1, le=1000, description="单次请求返回的最大告警记录数。"),
    offset: int = Query(0, ge=0, description="分页偏移量，用于配合 limit 翻页。"),
    current_user: User = Depends(get_current_user),
):
    """
    查询告警记录

    参数:
    - symbol: 股票代码 (可选)
    - alert_type: 告警类型 (可选)
    - alert_level: 告警级别 (可选)
    - is_read: 是否已读 (可选)
    - start_date: 开始日期 (可选)
    - end_date: 结束日期 (可选)
    - limit: 返回数量限制
    - offset: 偏移量

    示例:
    - GET /api/monitoring/alerts?is_read=false&limit=50
    - GET /api/monitoring/alerts?symbol=600519&alert_type=limit_up
    - GET /api/monitoring/alerts?alert_level=critical
    """
    limit_value = _resolve_query_int(limit, 100)
    offset_value = _resolve_query_int(offset, 0)

    try:
        records, total = monitoring_service.get_alert_records(
            symbol=symbol,
            alert_type=alert_type,
            alert_level=alert_level.value if alert_level else None,
            is_read=is_read,
            start_date=start_date,
            end_date=end_date,
            limit=limit_value,
            offset=offset_value,
        )

        return AlertRecordsResponse(
            data=[AlertRecordResponse.from_orm(r) for r in records],
            total=total,
            limit=limit_value,
            offset=offset_value,
        )
    except Exception as e:
        if _runtime_fallback_enabled():
            fallback_records = _build_runtime_alert_records()
            return AlertRecordsResponse(
                data=fallback_records[offset_value : offset_value + limit_value],
                total=len(fallback_records),
                limit=limit_value,
                offset=offset_value,
            )
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/alerts/{alert_id}/mark-read",
    summary="标记告警为已读",
    description="按告警记录 ID 将单条告警标记为已读，便于前端清理未读提醒。",
    responses=ALERT_MARK_READ_RESPONSES,
)
async def mark_alert_read(
    alert_id: int = Path(..., description="告警记录 ID。"),
    current_user: User = Depends(get_current_user),
):
    """
    标记告警为已读

    参数:
    - alert_id: 告警记录ID
    """
    try:
        success = monitoring_service.mark_alert_read(alert_id)
        if not success:
            raise NotFoundException(resource="告警记录", identifier="查询条件")
        return {"success": True, "message": "已标记为已读"}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/alerts/mark-all-read",
    summary="批量标记全部告警已读",
    description="批量将当前用户可见的未读告警标记为已读，用于监控中心一键清空提醒。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=ALERT_MARK_ALL_READ_RESPONSES,
)
async def mark_all_alerts_read(current_user: User = Depends(get_current_user)):
    """批量标记所有未读告警为已读。"""
    try:
        if _runtime_fallback_enabled():
            fallback_records = _build_runtime_alert_records()
            updated_count = sum(1 for record in fallback_records if not record.is_read)
            return UnifiedResponse(
                success=True,
                code=200,
                message="全部告警已标记为已读",
                data={
                    "status": "updated",
                    "scope": "all_alerts",
                    "updated_count": updated_count,
                },
            )

        records, _ = monitoring_service.get_alert_records(is_read=False, limit=1000, offset=0)
        updated_count = 0
        for record in records:
            if monitoring_service.mark_alert_read(record.id):
                updated_count += 1

        return UnifiedResponse(
            success=True,
            code=200,
            message="全部告警已标记为已读",
            data={
                "status": "updated",
                "scope": "all_alerts",
                "updated_count": updated_count,
            },
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


# ============================================================================
# 实时监控数据
# ============================================================================


@router.get(
    "/realtime/{symbol}",
    response_model=RealtimeMonitoringResponse,
    summary="获取单只股票实时监控数据",
    description="查询指定股票的最新实时监控快照，返回行情、指标和涨跌停状态等监控字段。",
    responses=REALTIME_MONITORING_DETAIL_RESPONSES,
)
async def get_realtime_monitoring(
    symbol: str = Path(..., description="待查询的股票代码，例如 600519。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取单只股票的最新实时监控数据

    参数:
    - symbol: 股票代码

    示例:
    - GET /api/monitoring/realtime/600519
    """
    try:
        session = monitoring_service.get_session()
        try:
            from app.models.monitoring import RealtimeMonitoring

            record = (
                session.query(RealtimeMonitoring)
                .filter(RealtimeMonitoring.symbol == symbol)
                .order_by(RealtimeMonitoring.timestamp.desc())
                .first()
            )

            if not record:
                raise NotFoundException(resource="股票监控数据", identifier="查询条件")

            return RealtimeMonitoringResponse.from_orm(record)
        finally:
            session.close()
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.get(
    "/realtime",
    response_model=List[RealtimeMonitoringResponse],
    summary="获取实时监控数据列表",
    description="批量查询当日实时监控记录，支持按股票列表、涨停状态和跌停状态筛选。",
    responses=REALTIME_MONITORING_LIST_RESPONSES,
)
async def get_realtime_monitoring_list(
    symbols: Optional[str] = Query(None, description="逗号分隔的股票代码列表，例如 600519,000001。"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最新实时监控记录上限。"),
    is_limit_up: Optional[bool] = Query(None, description="是否仅返回涨停股票，true 表示只保留涨停记录。"),
    is_limit_down: Optional[bool] = Query(None, description="是否仅返回跌停股票，true 表示只保留跌停记录。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取实时监控数据列表

    参数:
    - symbols: 股票代码列表，逗号分隔 (可选，如: "600519,000001")
    - limit: 返回数量限制
    - is_limit_up: 仅返回涨停股票 (可选)
    - is_limit_down: 仅返回跌停股票 (可选)

    示例:
    - GET /api/monitoring/realtime?limit=20
    - GET /api/monitoring/realtime?is_limit_up=true
    - GET /api/monitoring/realtime?symbols=600519,000001,600000
    """
    try:
        session = monitoring_service.get_session()
        try:
            from app.models.monitoring import RealtimeMonitoring

            query = session.query(RealtimeMonitoring).filter(RealtimeMonitoring.trade_date == date.today())

            # 筛选指定股票
            if symbols:
                symbol_list = [s.strip() for s in symbols.split(",")]
                query = query.filter(RealtimeMonitoring.symbol.in_(symbol_list))

            # 筛选涨跌停
            if is_limit_up is not None:
                query = query.filter(RealtimeMonitoring.is_limit_up == is_limit_up)
            if is_limit_down is not None:
                query = query.filter(RealtimeMonitoring.is_limit_down == is_limit_down)

            # 对于每只股票，只取最新的记录
            # 这里简化处理，实际应该用子查询
            records = query.order_by(RealtimeMonitoring.timestamp.desc()).limit(limit).all()

            return [RealtimeMonitoringResponse.from_orm(r) for r in records]
        finally:
            session.close()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/realtime/fetch",
    summary="手动触发实时行情抓取",
    description="手动刷新实时监控行情数据，可按股票代码列表定向抓取并同步评估告警规则。",
    responses=FETCH_REALTIME_DATA_RESPONSES,
)
async def fetch_realtime_data(
    symbols: Optional[List[str]] = Body(
        default=None,
        description="需要立即刷新的股票代码数组；为空时抓取当前监控范围内的全量实时数据。",
        example=["600519", "000001", "601318"],
    ),
    current_user: User = Depends(get_current_user),
):
    """
    手动触发获取实时数据

    参数:
    - symbols: 股票代码列表 (可选，不提供则获取全市场)

    请求体示例:
    ```json
    ["600519", "000001", "601318"]
    ```
    """
    try:
        df = monitoring_service.fetch_realtime_data(symbols)
        if df.empty:
            return {"success": False, "message": "未获取到数据"}

        # 保存数据
        count = monitoring_service.save_realtime_data(df)

        # 评估告警规则
        alerts = monitoring_service.evaluate_alert_rules(df)

        return {
            "success": True,
            "message": "实时数据获取成功",
            "data": {
                "stocks_count": len(df),
                "saved_count": count,
                "alerts_triggered": len(alerts),
            },
        }
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


# ============================================================================
# 龙虎榜数据
# ============================================================================


@router.get(
    "/dragon-tiger",
    response_model=List[DragonTigerListResponse],
    summary="获取龙虎榜列表",
    description="查询监控模块内的龙虎榜记录，支持按交易日、股票代码和净买入额阈值进行过滤。",
    responses=DRAGON_TIGER_LIST_RESPONSES,
)
async def get_dragon_tiger_list(
    trade_date: Optional[date] = Query(None, description="按交易日期筛选龙虎榜数据，默认当天。"),
    symbol: Optional[str] = Query(None, description="按股票代码筛选龙虎榜数据。"),
    min_net_amount: Optional[float] = Query(None, description="按最小净买入额筛选龙虎榜记录。"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数量上限。"),
    current_user: User = Depends(get_current_user),
):
    """
    获取龙虎榜数据

    参数:
    - trade_date: 交易日期 (可选，默认今天)
    - symbol: 股票代码 (可选)
    - min_net_amount: 最小净买入额 (可选)
    - limit: 返回数量限制

    示例:
    - GET /api/monitoring/dragon-tiger
    - GET /api/monitoring/dragon-tiger?trade_date=2025-10-23
    - GET /api/monitoring/dragon-tiger?symbol=600519
    """
    try:
        session = monitoring_service.get_session()
        try:
            from app.models.monitoring import DragonTigerList

            if trade_date is None:
                trade_date = date.today()

            query = session.query(DragonTigerList).filter(DragonTigerList.trade_date == trade_date)

            if symbol:
                query = query.filter(DragonTigerList.symbol == symbol)
            if min_net_amount is not None:
                query = query.filter(DragonTigerList.net_amount >= min_net_amount)

            records = query.order_by(DragonTigerList.net_amount.desc()).limit(limit).all()

            return [DragonTigerListResponse.from_orm(r) for r in records]
        finally:
            session.close()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/dragon-tiger/fetch",
    summary="手动触发龙虎榜数据抓取",
    description="手动抓取指定交易日的龙虎榜数据，并写入监控侧使用的龙虎榜数据表。",
    responses=FETCH_DRAGON_TIGER_DATA_RESPONSES,
)
async def fetch_dragon_tiger_data(
    trade_date: Optional[date] = Query(None, description="需要抓取的交易日期，默认使用当天交易日。"),
    current_user: User = Depends(get_current_user),
):
    """
    手动触发获取龙虎榜数据

    参数:
    - trade_date: 交易日期 (可选，默认今天)
    """
    try:
        if trade_date is None:
            trade_date = date.today()

        df = monitoring_service.fetch_dragon_tiger_list(trade_date)
        if df.empty:
            return {"success": False, "message": f"{trade_date} 无龙虎榜数据"}

        count = monitoring_service.save_dragon_tiger_data(df, trade_date)

        return {
            "success": True,
            "message": "龙虎榜数据获取成功",
            "data": {"trade_date": trade_date.isoformat(), "count": count},
        }
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


# ============================================================================
# 监控摘要和统计
# ============================================================================


@router.get(
    "/analyze",
    response_model=MonitoringSummaryResponse,
    summary="获取监控分析摘要",
    description="兼容旧版调用方的监控分析入口，返回与摘要接口一致的监控汇总结果。",
    responses=MONITORING_SUMMARY_RESPONSES,
)
async def analyze_monitoring(current_user: User = Depends(get_current_user)):
    """
    监控分析 (Alias for summary)

    Compatible with Phase 2.8 requirements
    """
    return await get_monitoring_summary(current_user)


@router.get(
    "/summary",
    response_model=MonitoringSummaryResponse,
    summary="获取监控系统摘要",
    description="返回监控系统的核心汇总指标，包括涨跌停数量、活跃告警数与市场强弱概览。",
    responses=MONITORING_SUMMARY_RESPONSES,
)
async def get_monitoring_summary(current_user: User = Depends(get_current_user)):
    """
    获取监控系统摘要

    返回:
    - 总监控股票数
    - 涨停/跌停数量
    - 大涨/大跌数量
    - 平均涨跌幅
    - 总成交额
    - 活跃告警数
    - 未读告警数
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            mock_manager = get_mock_data_manager()
            mock_manager.get_data("monitoring", alert_type="all")

            # 构建返回的监控摘要数据
            summary = {
                "total_stocks": 1568,
                "limit_up_count": 23,
                "limit_down_count": 5,
                "strong_up_count": 127,
                "strong_down_count": 89,
                "avg_change_percent": 0.85,
                "total_amount": 2456789000.0,
                "active_alerts": 12,
                "unread_alerts": 5,
            }
            return MonitoringSummaryResponse(**summary)
        else:
            # 使用真实数据库
            summary = monitoring_service.get_monitoring_summary()
            return MonitoringSummaryResponse(**summary)
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.get(
    "/stats/today",
    summary="获取今日监控统计",
    description="查询当日告警摘要、活跃规则与实时监控总览，供监控中心首页与值班看板展示。",
    responses=TODAY_STATS_RESPONSES,
)
async def get_today_statistics(current_user: User = Depends(get_current_user)):
    """获取今日监控统计聚合结果。"""
    try:
        session = monitoring_service.get_session()
        try:
            # 使用视图查询
            from sqlalchemy import text

            # 今日告警摘要
            alerts_summary = session.execute(text("SELECT * FROM v_today_alerts_summary")).fetchall()

            # 活跃规则
            active_rules = session.execute(text("SELECT * FROM v_active_alert_rules LIMIT 10")).fetchall()

            # 实时监控摘要
            realtime_summary = session.execute(text("SELECT * FROM v_realtime_summary")).fetchone()

            return {
                "success": True,
                "data": {
                    "alerts_summary": [dict(row._mapping) for row in alerts_summary],
                    "active_rules": [dict(row._mapping) for row in active_rules],
                    "realtime_summary": (dict(realtime_summary._mapping) if realtime_summary else {}),
                },
            }
        finally:
            session.close()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


# ============================================================================
# 监控控制
# ============================================================================


class MonitoringControlRequest(BaseModel):
    """监控控制请求"""

    symbols: Optional[List[str]] = Field(None, description="需要纳入监控的股票代码列表；为空表示使用默认监控池。")
    interval: int = Field(60, description="监控轮询间隔，单位秒。")


@router.post(
    "/control/start",
    summary="启动实时监控任务",
    description="提交监控启动请求，指定监控股票范围和刷新间隔，用于监控面板手动拉起任务。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=START_MONITORING_RESPONSES,
)
async def start_monitoring(
    request: MonitoringControlRequest = Body(
        ...,
        example={"symbols": ["600519", "000001", "601318"], "interval": 30},
    ),
    current_user: User = Depends(get_current_user),
):
    """
    启动监控

    参数:
    - symbols: 要监控的股票代码列表 (可选，不提供则监控全市场)
    - interval: 更新间隔(秒)，默认60秒
    """
    try:
        current_task = _get_monitoring_task()
        if not monitoring_service.is_monitoring or current_task is None:
            _monitoring_control_state["interval"] = request.interval
            _monitoring_control_state["last_started_at"] = datetime.now()
            _monitoring_control_state["task"] = asyncio.create_task(
                monitoring_service.start_monitoring(symbols=request.symbols, interval=request.interval)
            )
            await asyncio.sleep(0)
        return create_unified_success_response(
            data=_build_monitoring_control_payload(include_interval_key="interval"),
            message="监控已启动",
        )
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.post(
    "/control/stop",
    summary="停止实时监控任务",
    description="停止当前运行中的监控任务，并返回停止结果给监控控制面板。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=STOP_MONITORING_RESPONSES,
)
async def stop_monitoring(current_user: User = Depends(get_current_user)):
    """停止当前监控任务并返回结果。"""
    try:
        monitoring_service.stop_monitoring()
        monitoring_service.monitored_symbols = []
        task = _get_monitoring_task()
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        _monitoring_control_state["task"] = None
        _monitoring_control_state["interval"] = None
        _monitoring_control_state["last_started_at"] = None
        return create_unified_success_response(
            data=_build_monitoring_control_payload(),
            message="监控已停止",
        ).model_dump()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")


@router.get(
    "/control/status",
    summary="获取监控运行状态",
    description="查询实时监控系统的运行状态、监控范围和当前监控股票数量，用于面板状态展示。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=MONITORING_STATUS_RESPONSES,
)
async def get_monitoring_status():
    """
    获取实时监控系统运行状态

    查询当前监控系统的运行状态、监控范围和统计信息。该端点用于检查监控服务是否
    正常运行，以及正在监控的股票列表。

    **功能说明**:
    - 返回监控服务运行状态（运行中/已停止）
    - 提供当前监控的股票代码列表
    - 统计监控股票数量
    - 显示监控配置信息（更新间隔、告警规则数量等）
    - 支持监控面板状态展示

    **使用场景**:
    - 监控面板实时状态展示
    - 健康检查和服务可用性监测
    - 调试监控服务启停状态
    - 确认特定股票是否在监控范围内
    - 运维监控系统状态查询

    **返回值**:
    - success: 请求是否成功（布尔值）
    - data: 监控状态数据对象
      - is_monitoring: 是否正在监控（布尔值）
      - monitored_symbols: 监控的股票代码列表（数组）
      - monitored_count: 监控股票数量（整数）
      - update_interval (可选): 更新间隔秒数
      - active_rules_count (可选): 活跃告警规则数量
      - last_update_time (可选): 最后更新时间

    **示例**:
    ```bash
    # 查询监控状态
    curl -X GET "http://localhost:${BACKEND_PORT}/api/monitoring/control/status"
    ```

    **响应示例**:
    ```json
    {
      "success": true,
      "data": {
        "is_monitoring": true,
        "monitored_symbols": ["600519", "000001", "600036", "601318"],
        "monitored_count": 4,
        "update_interval": 60,
        "active_rules_count": 12,
        "last_update_time": "2025-11-30T10:30:45"
      }
    }
    ```

    **监控停止状态响应**:
    ```json
    {
      "success": true,
      "data": {
        "is_monitoring": false,
        "monitored_symbols": [],
        "monitored_count": 0
      }
    }
    ```

    **注意事项**:
    - 该端点不需要认证即可访问（用于健康检查）
    - 频繁调用不会影响监控性能
    - 返回的股票列表可能很长，建议配合分页展示
    - 监控状态变更后立即生效
    - 配合 /control/start 和 /control/stop 端点使用
    """
    try:
        return create_unified_success_response(
            data=_build_monitoring_control_payload(include_interval_key="update_interval"),
            message="获取监控状态成功",
        ).model_dump()
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="MONITORING_OPERATION_FAILED")
