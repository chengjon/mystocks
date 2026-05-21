"""Response specs extracted from monitoring_watchlists."""

from typing import Any, Dict, Optional

from fastapi import APIRouter

from app.openapi_config import COMMON_RESPONSES

def _success_response_spec(
    description: str,
    example: Any,
    extra_responses: Optional[Dict[int, Dict[str, Any]]] = None,
) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        },
        **(extra_responses or {}),
    }

MONITORING_WATCHLIST_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "依赖的监控数据库当前不可用",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "数据库未连接",
                    "error_code": "DATABASE_UNAVAILABLE",
                    "timestamp": "2026-04-03T10:30:00Z",
                }
            }
        },
    },
}

FEATURE_NOT_IMPLEMENTED_RESPONSE = {
    "description": "接口契约已预留，但后端实现尚未完成",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "message": "更新功能待实现",
                "error_code": "FEATURE_NOT_IMPLEMENTED",
                "timestamp": "2026-04-03T10:30:00Z",
            }
        }
    },
}

# Prefix is governed by the central route registry.
router = APIRouter(tags=["monitoring-watchlists"], responses=MONITORING_WATCHLIST_ROUTE_RESPONSES)

CREATE_WATCHLIST_REQUEST_EXAMPLES = {
    "manual_watchlist_with_risk_profile": {
        "summary": "创建手工监控清单",
        "description": "创建一个用于止损观察的手工清单，并附带基础风控参数。",
        "value": {
            "name": "核心止损监控",
            "watchlist_type": "manual",
            "risk_profile": {
                "max_position_size": 0.15,
                "default_stop_loss_pct": 0.08,
                "rebalance_window": "weekly",
            },
        },
    }
}

UPDATE_WATCHLIST_REQUEST_EXAMPLES = {
    "rebalance_watchlist_profile": {
        "summary": "更新清单名称与风控配置",
        "description": "调整清单展示名称、风控约束和启用状态，适用于策略切换或阶段性停用。",
        "value": {
            "name": "核心趋势监控",
            "watchlist_type": "strategy",
            "risk_profile": {
                "max_position_size": 0.12,
                "take_profit_pct": 0.18,
                "alert_threshold": "medium",
            },
            "is_active": True,
        },
    }
}

ADD_STOCK_REQUEST_EXAMPLES = {
    "add_stock_with_targets": {
        "summary": "添加带止损止盈的清单成员",
        "description": "向监控清单中加入一只股票，并同时记录建仓理由、止损价和目标价。",
        "value": {
            "stock_code": "600519",
            "entry_price": 1820.0,
            "entry_reason": "突破年线后纳入趋势跟踪",
            "stop_loss_price": 1750.0,
            "target_price": 1935.0,
            "weight": 0.2,
        },
    }
}

WATCHLIST_LIST_RESPONSES = _success_response_spec(
    "监控清单列表",
    {
        "success": True,
        "code": 200,
        "message": "获取清单列表成功",
        "data": [
            {
                "id": 1,
                "user_id": 1,
                "name": "核心止损监控",
                "watchlist_type": "manual",
                "risk_profile": {"max_position_size": 0.15, "default_stop_loss_pct": 0.08},
                "is_active": True,
                "created_at": "2026-03-13T09:30:00",
                "updated_at": "2026-03-13T09:30:00",
                "stocks_count": 2,
            }
        ],
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-001",
        "errors": None,
    },
)

WATCHLIST_DETAIL_RESPONSES = _success_response_spec(
    "监控清单详情",
    {
        "success": True,
        "code": 200,
        "message": "获取清单成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "name": "核心止损监控",
            "watchlist_type": "manual",
            "risk_profile": {"max_position_size": 0.15, "default_stop_loss_pct": 0.08},
            "is_active": True,
            "created_at": "2026-03-13T09:30:00",
            "updated_at": "2026-03-13T09:30:00",
            "stocks_count": 2,
        },
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-002",
        "errors": None,
    },
)

WATCHLIST_DELETE_RESPONSES = _success_response_spec(
    "监控清单删除成功",
    {
        "success": True,
        "code": 200,
        "message": "删除清单成功",
        "data": None,
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-003",
        "errors": None,
    },
)

WATCHLIST_STOCK_LIST_RESPONSES = _success_response_spec(
    "监控清单成员列表",
    {
        "success": True,
        "code": 200,
        "message": "获取股票列表成功",
        "data": [
            {
                "id": 1001,
                "watchlist_id": 1,
                "stock_code": "000001",
                "entry_price": 12.45,
                "entry_at": "2026-03-13T09:30:00",
                "entry_reason": "突破年线纳入观察",
                "stop_loss_price": 11.5,
                "target_price": 13.6,
                "weight": 0.4,
                "is_active": True,
            }
        ],
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-004",
        "errors": None,
    },
)

WATCHLIST_STOCK_DELETE_RESPONSES = _success_response_spec(
    "监控清单成员移除成功",
    {
        "success": True,
        "code": 200,
        "message": "移除股票成功",
        "data": None,
        "timestamp": "2026-04-05T12:00:00Z",
        "request_id": "req-monitoring-watchlists-005",
        "errors": None,
    },
)

WATCHLIST_CREATE_RESPONSES = _success_response_spec(
    "监控清单创建结果",
    {
        "success": True,
        "code": 200,
        "message": "创建清单成功",
        "data": {
            "id": 3,
            "user_id": 1,
            "name": "港股高股息观察",
            "watchlist_type": "manual",
            "risk_profile": {
                "max_position_size": 0.1,
                "default_stop_loss_pct": 0.06,
                "market_scope": ["HK"],
            },
            "is_active": True,
            "created_at": "2026-04-08T03:40:00Z",
            "updated_at": "2026-04-08T03:40:00Z",
            "stocks_count": 0,
        },
        "timestamp": "2026-04-08T03:40:00Z",
        "request_id": "req-monitoring-watchlists-create-001",
        "errors": None,
    },
)

WATCHLIST_UPDATE_RESPONSES = _success_response_spec(
    "监控清单更新结果",
    {
        "success": True,
        "code": 200,
        "message": "更新清单成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "name": "股指期货风险监控",
            "watchlist_type": "strategy",
            "risk_profile": {
                "max_position_size": 0.12,
                "take_profit_pct": 0.18,
                "alert_threshold": "medium",
                "market_scope": ["CFFEX"],
            },
            "is_active": True,
            "created_at": "2026-03-13T09:30:00Z",
            "updated_at": "2026-04-08T03:45:00Z",
            "stocks_count": 4,
        },
        "timestamp": "2026-04-08T03:45:00Z",
        "request_id": "req-monitoring-watchlists-update-001",
        "errors": None,
    },
    {501: FEATURE_NOT_IMPLEMENTED_RESPONSE},
)

WATCHLIST_STOCK_CREATE_RESPONSES = _success_response_spec(
    "监控清单成员添加结果",
    {
        "success": True,
        "code": 200,
        "message": "添加股票成功",
        "data": {
            "id": 3001,
            "watchlist_id": 3,
            "stock_code": "00700.HK",
            "entry_price": 328.6,
            "entry_at": "2026-04-08T03:50:00Z",
            "entry_reason": "港股科技龙头纳入观察",
            "stop_loss_price": 312.0,
            "target_price": 356.0,
            "weight": 0.25,
            "is_active": True,
        },
        "timestamp": "2026-04-08T03:50:00Z",
        "request_id": "req-monitoring-watchlists-stock-create-001",
        "errors": None,
    },
)
