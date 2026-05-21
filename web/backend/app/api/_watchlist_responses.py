"""Response examples and OpenAPI response specs for watchlist."""

from app.openapi_config import COMMON_RESPONSES

WATCHLIST_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}


def _success_response_spec(description: str, example: object) -> dict[int, dict]:
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


WATCHLIST_ADD_REQUEST_EXAMPLES = {
    "add_stock_to_growth_group": {
        "summary": "添加股票到成长分组",
        "value": {
            "symbol": "SZ000001",
            "display_name": "平安银行",
            "exchange": "SZSE",
            "market": "CN",
            "notes": "关注一季报和资金流",
            "group_name": "成长观察",
        },
    }
}

WATCHLIST_CREATE_GROUP_REQUEST_EXAMPLES = {
    "create_custom_group": {
        "summary": "创建自定义分组",
        "value": {"group_name": "高股息"},
    }
}

WATCHLIST_UPDATE_GROUP_REQUEST_EXAMPLES = {
    "rename_group": {
        "summary": "重命名分组",
        "value": {"group_name": "核心持仓"},
    }
}

WATCHLIST_MOVE_REQUEST_EXAMPLES = {
    "move_stock_between_groups": {
        "summary": "移动股票到新分组",
        "value": {
            "symbol": "SH600519",
            "from_group_id": 1,
            "to_group_id": 3,
        },
    }
}

WATCHLIST_NOTES_REQUEST_EXAMPLES = {
    "update_trade_note": {
        "summary": "更新自选股备注",
        "value": {"notes": "突破年线后关注回踩确认。"},
    }
}

WATCHLIST_ITEM_EXAMPLE = {
    "id": 101,
    "symbol": "SZ000001",
    "display_name": "平安银行",
    "exchange": "SZSE",
    "added_at": "2026-04-07 09:30:00",
    "notes": "关注一季报和资金流",
}

WATCHLIST_GROUP_EXAMPLE = {
    "id": 3,
    "group_name": "成长观察",
    "created_at": "2026-04-07T09:00:00",
    "stock_count": 12,
}

WATCHLIST_GROUP_STOCK_EXAMPLE = {
    "id": 101,
    "stock_code": "SZ000001",
    "stock_name": "平安银行",
    "added_at": "2026-04-07T09:30:00",
    "notes": "关注一季报和资金流",
}

WATCHLIST_LIST_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("当前用户自选股列表", [WATCHLIST_ITEM_EXAMPLE]),
}

WATCHLIST_SYMBOLS_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("当前用户自选股代码列表", ["SZ000001", "SH600519"]),
}

WATCHLIST_REMOVE_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "移除自选股结果",
        {"success": True, "message": "已从自选股移除", "symbol": "SZ000001"},
    ),
}

WATCHLIST_CHECK_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "自选股存在性检查结果",
        {"symbol": "SZ000001", "is_in_watchlist": True},
    ),
}

WATCHLIST_COUNT_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("自选股数量统计结果", {"count": 12}),
}

WATCHLIST_CLEAR_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("清空自选股结果", {"success": True, "message": "自选股列表已清空"}),
}

WATCHLIST_GROUP_LIST_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("自选股分组列表", [WATCHLIST_GROUP_EXAMPLE]),
}

WATCHLIST_GROUP_DELETE_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("删除分组结果", {"success": True, "message": "分组已删除", "group_id": 3}),
}

WATCHLIST_GROUP_DETAIL_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec("指定分组下的自选股列表", [WATCHLIST_GROUP_STOCK_EXAMPLE]),
}

WATCHLIST_WITH_GROUPS_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "分组视图下的自选股聚合结果",
        {
            "groups": [
                {
                    "id": 3,
                    "name": "成长观察",
                    "stock_count": 1,
                    "created_at": "2026-04-07T09:00:00",
                    "sort_order": 1,
                    "stocks": [WATCHLIST_GROUP_STOCK_EXAMPLE],
                }
            ]
        },
    ),
}

WATCHLIST_ADD_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "添加自选股结果",
        {
            "success": True,
            "message": "已添加到自选股",
            "symbol": "SZ000001",
            "group_name": "成长观察",
        },
    ),
}

WATCHLIST_NOTES_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "更新自选股备注结果",
        {
            "success": True,
            "message": "备注已更新",
            "symbol": "SZ000001",
        },
    ),
}

WATCHLIST_GROUP_CREATE_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "创建自选股分组结果",
        {
            "success": True,
            "message": "分组 '高股息' 创建成功",
            "group": WATCHLIST_GROUP_EXAMPLE,
        },
    ),
}

WATCHLIST_GROUP_UPDATE_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "更新自选股分组结果",
        {
            "success": True,
            "message": "分组已更新为 '核心持仓'",
            "group_id": 3,
        },
    ),
}

WATCHLIST_MOVE_RESPONSES = {
    **WATCHLIST_ROUTE_RESPONSES,
    **_success_response_spec(
        "移动自选股分组结果",
        {
            "success": True,
            "message": "股票 SH600519 已移动到新分组",
            "symbol": "SH600519",
            "to_group_id": 3,
        },
    ),
}
