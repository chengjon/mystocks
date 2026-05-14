"""OpenAPI response specs for monitoring routes."""

from __future__ import annotations

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
