"""Task route response examples and OpenAPI response specs."""

from typing import Any

from pydantic import BaseModel, Field

from app.openapi_config import COMMON_RESPONSES

TASK_REGISTER_REQUEST_EXAMPLES = {
    "manual_task": {
        "summary": "注册手动执行任务",
        "description": "创建一个可手动触发的数据同步任务。",
        "value": {
            "task_id": "daily_sync_job",
            "task_name": "日终同步任务",
            "task_type": "manual",
            "task_module": "app.jobs.daily_sync",
            "task_function": "run_daily_sync",
            "description": "收盘后执行多源行情同步",
            "priority": 500,
            "schedule": None,
            "params": {"market": "CN", "full_refresh": False},
            "timeout": 3600,
            "retry_count": 2,
            "retry_delay": 60,
            "dependencies": [],
            "tags": ["sync", "daily"],
            "auto_restart": False,
            "stop_on_error": True,
        },
    }
}

TASK_START_REQUEST_EXAMPLES = {
    "start_with_runtime_params": {
        "summary": "携带运行参数启动任务",
        "description": "按任务ID启动任务，并覆盖本次执行所需的批量大小和优先级参数。",
        "value": {
            "batch_size": 100,
            "priority": "high",
            "dry_run": False,
        },
    }
}

TASK_IMPORT_REQUEST_EXAMPLES = {
    "import_yaml_config": {
        "summary": "导入任务配置文件",
        "description": "从指定的 YAML 配置文件导入任务定义。",
        "value": {"config_path": "/tmp/task-configs/daily-jobs.yaml"},
    }
}

TASK_EXPORT_REQUEST_EXAMPLES = {
    "export_yaml_config": {
        "summary": "导出任务配置文件",
        "description": "将当前任务配置导出到指定路径，便于备份或迁移。",
        "value": {"output_path": "/tmp/task-configs/exported-jobs.yaml"},
    }
}


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


TASK_READ_ERROR_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

TASK_DETAIL_ERROR_RESPONSES = {
    404: COMMON_RESPONSES[404],
    500: COMMON_RESPONSES[500],
}

TASK_EXECUTIONS_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务执行历史列表",
        [
            {
                "execution_id": "exec_1001",
                "task_id": "daily_sync_job",
                "status": "COMPLETED",
                "start_time": "2026-04-04T08:00:00Z",
                "end_time": "2026-04-04T08:05:00Z",
                "result": {"processed": 320, "success_rate": 99.1},
                "error_message": None,
            }
        ],
    ),
}

TASK_EXECUTION_DETAIL_SUCCESS_RESPONSE = {
    **TASK_DETAIL_ERROR_RESPONSES,
    **_success_response_spec(
        "任务执行详情",
        {
            "execution_id": "exec_1001",
            "task_id": "daily_sync_job",
            "status": "COMPLETED",
            "start_time": "2026-04-04T08:00:00Z",
            "end_time": "2026-04-04T08:05:00Z",
            "result": {"processed": 320, "success_rate": 99.1},
            "error_message": None,
        },
    ),
}

TASK_STATISTICS_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务统计摘要",
        {
            "total_tasks": {
                "count": 25,
                "success_count": 20,
                "failed_count": 3,
                "running_count": 2,
                "avg_execution_time": 45.5,
                "success_rate": 80.0,
            },
            "backtest": {
                "count": 8,
                "success_count": 6,
                "failed_count": 1,
                "running_count": 1,
                "avg_execution_time": 120.8,
                "success_rate": 75.0,
            },
        },
    ),
}

TASK_HEALTH_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务系统健康状态",
        {
            "status": "healthy",
            "total_tasks": 25,
            "running_tasks": 3,
            "total_executions": 156,
            "last_check": "2026-04-04T08:30:00Z",
            "mock_mode": False,
        },
    ),
}

TASK_CONFIG_EXAMPLE = {
    "task_id": "daily_sync_job",
    "task_name": "日终同步任务",
    "task_type": "data_sync",
    "task_module": "app.jobs.daily_sync",
    "task_function": "run_daily_sync",
    "description": "收盘后执行 A 股、港股与股指期货相关数据同步",
    "priority": 500,
    "schedule": None,
    "params": {"market": "CN", "full_refresh": False},
    "timeout": 3600,
    "retry_count": 2,
    "retry_delay": 60,
    "dependencies": [],
    "tags": ["sync", "daily"],
    "auto_restart": False,
    "stop_on_error": True,
}

TASK_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "任务操作成功",
    "data": {"status": "ok"},
    "task_id": "daily_sync_job",
    "execution_id": None,
}

TASK_LIST_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务列表查询成功",
        [
            TASK_CONFIG_EXAMPLE,
            {
                "task_id": "hk_close_sync",
                "task_name": "港股收盘同步任务",
                "task_type": "market_sync",
                "task_module": "app.jobs.hk_sync",
                "task_function": "run_hk_sync",
                "description": "港股收盘后同步行情和成交统计",
                "priority": 500,
                "schedule": None,
                "params": {"market": "HK", "full_refresh": True},
                "timeout": 2400,
                "retry_count": 1,
                "retry_delay": 30,
                "dependencies": [],
                "tags": ["sync", "hk"],
                "auto_restart": False,
                "stop_on_error": True,
            },
        ],
    ),
}

TASK_CONFIG_DETAIL_SUCCESS_RESPONSE = {
    **TASK_DETAIL_ERROR_RESPONSES,
    **_success_response_spec("任务详情查询成功", TASK_CONFIG_EXAMPLE),
}

TASK_UNREGISTER_SUCCESS_RESPONSE = {
    **TASK_DETAIL_ERROR_RESPONSES,
    **_success_response_spec(
        "任务注销成功",
        {
            "success": True,
            "message": "任务注销成功",
            "data": {"removed": True},
            "task_id": "daily_sync_job",
            "execution_id": None,
        },
    ),
}

TASK_REGISTER_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    400: COMMON_RESPONSES[400],
    **_success_response_spec(
        "任务注册成功",
        {
            "success": True,
            "message": "任务注册成功",
            "data": {
                "task_id": "daily_sync_job",
                "status": "registered",
                "created_by": "admin",
            },
            "task_id": "daily_sync_job",
            "execution_id": None,
        },
    ),
}

TASK_START_SUCCESS_RESPONSE = {
    **TASK_DETAIL_ERROR_RESPONSES,
    400: COMMON_RESPONSES[400],
    **_success_response_spec(
        "任务启动成功",
        {
            "success": True,
            "message": "任务启动成功",
            "data": {"status": "running"},
            "task_id": "daily_sync_job",
            "execution_id": "exec_1001",
        },
    ),
}

TASK_STOP_SUCCESS_RESPONSE = {
    **TASK_DETAIL_ERROR_RESPONSES,
    **_success_response_spec(
        "任务停止成功",
        {
            "success": True,
            "message": "任务停止成功",
            "data": {"status": "stopped"},
            "task_id": "daily_sync_job",
            "execution_id": "exec_1001",
        },
    ),
}

TASK_IMPORT_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    400: COMMON_RESPONSES[400],
    **_success_response_spec(
        "任务配置导入成功",
        {
            "success": True,
            "message": "任务配置导入成功",
            "data": {"imported": 3, "failed": 0},
            "task_id": None,
            "execution_id": None,
        },
    ),
}

TASK_EXPORT_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务配置导出成功",
        {
            "success": True,
            "message": "Configuration exported successfully",
            "path": "/tmp/task-configs/exported-jobs.yaml",
        },
    ),
}

TASK_EXECUTION_CLEANUP_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务执行记录清理成功",
        {
            "success": True,
            "message": "Cleaned up 12 old execution records",
            "count": 12,
        },
    ),
}

TASK_AUDIT_LOGS_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务审计日志查询成功",
        {
            "logs": [
                {
                    "timestamp": "2026-04-04T08:00:00Z",
                    "username": "admin",
                    "operation": "register_task",
                    "task_id": "daily_sync_job",
                    "details": {"task_type": "data_sync", "enabled": True},
                }
            ],
            "total_count": 1,
            "filter_applied": {"operation": "register_task", "username": "admin"},
            "returned_count": 1,
        },
    ),
}

TASK_AUDIT_CLEANUP_SUCCESS_RESPONSE = {
    **TASK_READ_ERROR_RESPONSES,
    **_success_response_spec(
        "任务审计日志清理成功",
        {
            "success": True,
            "message": "已清理 8 条旧审计日志",
            "data": {
                "cleaned_count": 8,
                "remaining_count": 42,
                "cutoff_date": "2026-03-05T00:00:00+00:00",
            },
        },
    ),
}


class TaskImportRequest(BaseModel):
    """任务配置导入请求"""

    config_path: str = Field(..., description="待导入的任务配置文件路径。")


class TaskExportRequest(BaseModel):
    """任务配置导出请求"""

    output_path: str = Field(..., description="导出后的任务配置文件输出路径。")
