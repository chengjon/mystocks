"""Auto-extracted response constants."""

from typing import Any, Dict

def _success_response_spec(status_code: int, description: str, example: Any) -> Dict[int, Dict[str, Any]]:
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

router = APIRouter(
    prefix="/api/v1/data-sources/config",
    tags=["数据源配置管理"],
    responses={
        400: {"description": "请求参数错误"},
        404: {"description": "资源未找到"},
        409: {"description": "资源冲突"},
        500: {"description": "服务器错误"},
    },
)

DATA_SOURCE_CONFIG_DETAIL_RESPONSES = _success_response_spec(
    200,
    "数据源配置详情",
    {
        "success": True,
        "code": 200,
        "message": "获取数据源配置成功",
        "data": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "source_name": "akshare",
            "source_type": "http",
            "data_category": "DAILY_KLINE",
            "parameters": {"adjust": "qfq", "period": "daily"},
            "test_parameters": {"symbol": "600519", "start_date": "2024-01-01", "end_date": "2024-01-31"},
            "priority": 3,
            "status": "active",
            "description": "A股日线历史行情数据源",
        },
        "timestamp": "2026-04-06T15:30:00Z",
        "request_id": "req-data-source-config-001",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_LIST_RESPONSES = _success_response_spec(
    200,
    "数据源配置列表",
    {
        "success": True,
        "code": 200,
        "message": "获取数据源列表成功，共 1 个",
        "data": {
            "endpoints": [
                {
                    "endpoint_name": "akshare.stock_zh_a_hist",
                    "source_name": "akshare",
                    "source_type": "http",
                    "data_category": "DAILY_KLINE",
                    "priority": 3,
                    "status": "active",
                }
            ],
            "total": 1,
        },
        "timestamp": "2026-04-06T15:30:00Z",
        "request_id": "req-data-source-config-002",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_DELETE_RESPONSES = _success_response_spec(
    200,
    "数据源配置删除结果",
    {
        "success": True,
        "code": 200,
        "message": "数据源配置删除成功: akshare.stock_zh_a_hist",
        "data": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "version": 4,
        },
        "timestamp": "2026-04-06T15:30:00Z",
        "request_id": "req-data-source-config-003",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_VERSIONS_RESPONSES = _success_response_spec(
    200,
    "数据源配置版本历史",
    {
        "success": True,
        "code": 200,
        "message": "获取版本历史成功，共 2 个版本",
        "data": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "versions": [
                {
                    "endpoint_name": "akshare.stock_zh_a_hist",
                    "version": 4,
                    "change_type": "update",
                    "changed_by": "release-operator",
                    "changed_at": "2026-04-06T15:20:00",
                    "change_summary": "调整优先级与状态",
                    "metadata": {"priority": 3, "status": "active"},
                },
                {
                    "endpoint_name": "akshare.stock_zh_a_hist",
                    "version": 3,
                    "change_type": "create",
                    "changed_by": "system",
                    "changed_at": "2026-04-05T09:00:00",
                    "change_summary": "初始创建",
                    "metadata": {"priority": 5},
                },
            ],
            "total": 2,
        },
        "timestamp": "2026-04-06T15:30:00Z",
        "request_id": "req-data-source-config-004",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_CREATE_RESPONSES = _success_response_spec(
    201,
    "数据源配置创建结果",
    {
        "success": True,
        "code": 201,
        "message": "数据源配置创建成功: akshare.stock_zh_a_hist",
        "data": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "version": 1,
        },
        "timestamp": "2026-04-08T02:20:00Z",
        "request_id": "req-data-source-config-create-001",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_UPDATE_RESPONSES = _success_response_spec(
    200,
    "数据源配置更新结果",
    {
        "success": True,
        "code": 200,
        "message": "数据源配置更新成功: akshare.stock_zh_a_hist",
        "data": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "version": 5,
        },
        "timestamp": "2026-04-08T02:20:00Z",
        "request_id": "req-data-source-config-update-001",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_BATCH_RESPONSES = _success_response_spec(
    200,
    "数据源配置批量操作结果",
    {
        "success": True,
        "code": 200,
        "message": "批量操作完成: 成功 2/3",
        "data": {
            "total": 3,
            "succeeded": 2,
            "failed": 1,
            "results": [
                {
                    "action": "create",
                    "success": True,
                    "endpoint_name": "akshare.stock_intraday_em",
                    "version": 1,
                    "error": None,
                },
                {
                    "action": "update",
                    "success": True,
                    "endpoint_name": "akshare.stock_zh_a_hist",
                    "version": 5,
                    "error": None,
                },
                {
                    "action": "delete",
                    "success": False,
                    "error": "endpoint not found: legacy.deprecated_source",
                },
            ],
        },
        "timestamp": "2026-04-08T02:20:00Z",
        "request_id": "req-data-source-config-batch-001",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_ROLLBACK_RESPONSES = _success_response_spec(
    200,
    "数据源配置回滚结果",
    {
        "success": True,
        "code": 200,
        "message": "回滚成功: akshare.stock_zh_a_hist → 版本 3",
        "data": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "version": 6,
            "restored_from_version": 3,
        },
        "timestamp": "2026-04-08T02:20:00Z",
        "request_id": "req-data-source-config-rollback-001",
        "errors": None,
    },
)

DATA_SOURCE_CONFIG_RELOAD_RESPONSES = _success_response_spec(
    200,
    "数据源配置热重载结果",
    {
        "success": True,
        "code": 200,
        "message": "配置热重载成功: 12 → 13 个端点",
        "data": {
            "old_count": 12,
            "new_count": 13,
            "duration": 0.428,
            "reloaded_at": "2026-04-08T02:20:00Z",
        },
        "timestamp": "2026-04-08T02:20:00Z",
        "request_id": "req-data-source-config-reload-001",
        "errors": None,
    },
)

ROLLBACK_REQUEST_EXAMPLES = {
    "restore_specific_version": {
        "summary": "回滚到指定历史版本",
        "description": "将 akshare.stock_zh_a_hist 回滚到第 3 个历史版本。",
        "value": {
            "changed_by": "release-operator",
        },
    }
}

DATA_SOURCE_CREATE_EXAMPLES = {
    "create_daily_kline_source": {
        "summary": "创建日线数据源配置",
        "description": "新增一个 AkShare A 股日线接口配置。",
        "value": {
            "endpoint_name": "akshare.stock_zh_a_hist",
            "source_name": "akshare",
            "source_type": "http",
            "data_category": "DAILY_KLINE",
            "parameters": {"adjust": "qfq", "period": "daily"},
            "test_parameters": {"symbol": "600519", "start_date": "2024-01-01", "end_date": "2024-01-31"},
            "priority": 3,
            "description": "A股日线历史行情数据源",
        },
    }
}

DATA_SOURCE_UPDATE_EXAMPLES = {
    "update_priority_and_status": {
        "summary": "更新数据源优先级与状态",
        "description": "将现有数据源切换为维护态并调整优先级。",
        "value": {
            "priority": 5,
            "status": "maintenance",
            "description": "维护窗口期间降级使用",
        },
    }
}

BATCH_OPERATION_EXAMPLES = {
    "mixed_batch_operations": {
        "summary": "批量创建、更新、删除",
        "description": "一次提交多个数据源配置操作。",
        "value": {
            "operations": [
                {
                    "action": "create",
                    "config": {
                        "endpoint_name": "akshare.stock_intraday_em",
                        "source_name": "akshare",
                        "source_type": "http",
                        "data_category": "MINUTE_KLINE",
                        "parameters": {"period": "1"},
                        "test_parameters": {"symbol": "600519"},
                        "priority": 4,
                        "description": "分时行情数据源",
                    },
                },
                {
                    "action": "update",
                    "endpoint_name": "akshare.stock_zh_a_hist",
                    "updates": {"priority": 2, "description": "提升为主用数据源"},
                },
                {
                    "action": "delete",
                    "endpoint_name": "legacy.deprecated_source",
                },
            ]
        },
    }
}

RELOAD_REQUEST_EXAMPLES = {
    "reload_registry": {
        "summary": "触发配置热重载",
        "description": "通知系统重新读取 YAML 配置并刷新内存注册表。",
        "value": {
            "changed_by": "release-operator",
        },
    }
}


# ==================== Helper Functions ====================


def get_config_manager():
    """获取ConfigManager实例"""
    from src.core.data_source.config_manager import ConfigManager

    yaml_config_path = YAML_DATA_SOURCES_REGISTRY_PATH

    postgresql_access = None
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

        postgresql_access = get_postgres_async()
    except Exception:
        pass

    return ConfigManager(yaml_config_path=yaml_config_path, postgresql_access=postgresql_access)


def get_current_user(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
        description="Bearer 认证令牌，格式为 `Bearer <token>`。",
    )
) -> str:
    """获取当前用户"""
    if settings.testing:
        return "system"

    if not authorization or not authorization.startswith("Bearer "):
        raise BusinessException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "缺少或无效的认证凭据",
            ).dict(),
        )

    token = authorization.removeprefix("Bearer ").strip()
    token_data = verify_token(token) if token else None
    if token_data is None:
        raise BusinessException(
            status_code=401,
            detail=create_error_response(
                ErrorCodes.UNAUTHORIZED,
                "认证失败或令牌已过期",
            ).dict(),
        )

    return token_data.username or "system"


