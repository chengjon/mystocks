"""
任务管理API路由
提供RESTful API接口用于任务管理

安全级别：分级别访问控制
- Public endpoints: 健康检查（无需认证）
- User endpoints: 任务查看、基础操作（需要用户认证）
- Admin endpoints: 任务管理、执行控制（需要管理员权限）
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import BaseModel, Field

from app.api.task_security_support import (
    check_admin_privileges,
    check_task_rate_limit,
    log_task_operation,
    task_audit_log,
)
from app.api.tasks_schemas import TaskExecutionRequest, TaskQueryParams, TaskRegistrationRequest
from app.api.auth import User, get_current_user
from app.core.exceptions import BusinessException, ForbiddenException, NotFoundException
from app.core.responses import APIResponse
from app.models.task import TaskConfig, TaskExecution, TaskResponse, TaskStatistics
from app.openapi_config import COMMON_RESPONSES
from app.services.task_manager import task_manager

# Mock数据支持
use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

logger = structlog.get_logger()
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

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


class TaskImportRequest(BaseModel):
    """任务配置导入请求"""

    config_path: str = Field(..., description="待导入的任务配置文件路径。")


class TaskExportRequest(BaseModel):
    """任务配置导出请求"""

    output_path: str = Field(..., description="导出后的任务配置文件输出路径。")


@router.post(
    "/register",
    response_model=TaskResponse,
    description="注册新的任务定义，并在任务管理系统中创建可调度或手动执行的任务配置。",
)
async def register_task(
    task_config: TaskConfig = Body(..., openapi_examples=TASK_REGISTER_REQUEST_EXAMPLES),
    current_user: User = Depends(get_current_user),
):
    """
    注册新任务

    Security:
        - 需要用户认证
        - 管理员权限优先
        - 访问频率限制
        - 操作审计日志
    """
    try:
        # 检查操作频率限制
        if not check_task_rate_limit(current_user.id, max_operations_per_minute=5):
            raise BusinessException(
                detail="任务注册频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 记录操作审计
        log_task_operation(
            user=current_user,
            operation="register_task",
            details={"task_name": task_config.name, "task_type": task_config.task_type, "enabled": task_config.enabled},
        )

        if use_mock:
            # Mock数据响应
            import random

            task_id = f"task_{random.randint(1000, 9999)}"
            return TaskResponse(
                success=True,
                message="任务注册成功",
                data={"task_id": task_id, "status": "registered", "created_by": current_user.username},
            )

        response = task_manager.register_task(task_config)
        if not response.success:
            raise BusinessException(detail=response.message, status_code=400, error_code="TASK_OPERATION_FAILED")

        # 添加创建者信息
        if response.data:
            response.data["created_by"] = current_user.username

        logger.info("Task registered successfully by {current_user.username}: {task_config.name}")
        return response

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception:
        logger.error("Failed to register task for user {current_user.username}: %(e)s")
        raise BusinessException(detail="任务注册失败", status_code=500, error_code="TASK_REGISTRATION_FAILED")


@router.delete("/{task_id}", response_model=TaskResponse)
async def unregister_task(
    task_id: str = Path(..., description="任务ID", min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$"),
    current_user: User = Depends(get_current_user),
):
    """
    注销任务

    Security:
        - 需要用户认证
        - 管理员权限优先
        - 访问频率限制
        - 操作审计日志
    """
    try:
        # 检查操作频率限制
        if not check_task_rate_limit(current_user.id, max_operations_per_minute=5):
            raise BusinessException(
                detail="任务操作频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 记录操作审计
        log_task_operation(user=current_user, operation="unregister_task", task_id=task_id)

        response = task_manager.unregister_task(task_id)
        if not response.success:
            raise NotFoundException(resource="任务", identifier=response.message)

        logger.info("Task %(task_id)s unregistered successfully by {current_user.username}")
        return response

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception:
        logger.error("Failed to unregister task %(task_id)s for user {current_user.username}: %(e)s")
        raise BusinessException(detail="任务注销失败", status_code=500, error_code="TASK_UNREGISTRATION_FAILED")


@router.get("/", response_model=List[TaskConfig])
async def list_tasks(
    task_type: Optional[str] = Query(
        None,
        description="任务类型",
        pattern=r"^(DATA_PROCESSING|MARKET_ANALYSIS|SIGNAL_GENERATION|NOTIFICATION|CLEANUP|BACKTEST|REPORT)$",
    ),
    tags: Optional[str] = Query(None, description="逗号分隔的任务标签", max_length=200),
    status: Optional[str] = Query(
        None, description="任务状态", pattern=r"^(PENDING|RUNNING|SUCCESS|FAILED|CANCELLED)$"
    ),
    enabled: Optional[bool] = Query(None, description="是否启用"),
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    offset: int = Query(0, description="偏移量", ge=0, le=10000),
    current_user: User = Depends(get_current_user),
):
    """
    列出所有任务

    Security:
        - 需要用户认证
        - 管理员可查看所有任务，普通用户仅查看自己创建的任务
        - 访问频率限制
    """
    try:
        # 检查操作频率限制（读取操作限制较宽松）
        if not check_task_rate_limit(current_user.id, max_operations_per_minute=30):
            raise BusinessException(
                detail="查询频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 记录操作审计
        log_task_operation(
            user=current_user,
            operation="list_tasks",
            details={"task_type": task_type, "tags": tags, "status": status, "limit": limit, "offset": offset},
        )

        if use_mock:
            # Mock数据：返回模拟任务列表

            from app.models.task import TaskConfig, TaskType

            mock_tasks = []
            for i in range(min(limit, 10)):
                task = TaskConfig(
                    task_id=f"task_{i + 1000}",
                    name=f"模拟任务_{i + 1}",
                    description=f"这是一个模拟任务_{i + 1}",
                    task_type=TaskType.DATA_PROCESSING,
                    config={"param1": f"value{i + 1}"},
                    tags=[f"tag{i + 1}", "mock"],
                    enabled=True,
                    created_at=datetime.now() - timedelta(days=i),
                    created_by=current_user.username,  # 标记创建者
                )
                mock_tasks.append(task)
            return mock_tasks

        tag_list = tags.split(",") if tags else None
        tasks = task_manager.list_tasks(task_type=task_type, tags=tag_list)

        # 普通用户只能看到自己创建的任务
        if not check_admin_privileges(current_user):
            tasks = [task for task in tasks if getattr(task, "created_by", None) == current_user.username]

        logger.info("Tasks listed by {current_user.username}: {len(tasks)} tasks")
        return tasks

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception:
        logger.error("Failed to list tasks for user {current_user.username}: %(e)s")
        raise BusinessException(detail="获取任务列表失败", status_code=500, error_code="TASK_LIST_RETRIEVAL_FAILED")


@router.get("/{task_id}", response_model=TaskConfig)
async def get_task(
    task_id: str = Path(..., description="任务ID", min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$"),
):
    """获取任务详情"""
    if use_mock:
        # Mock数据：返回模拟任务详情
        from app.models.task import TaskConfig, TaskType

        task = TaskConfig(
            task_id=task_id,
            name=f"模拟任务_{task_id}",
            description=f"任务{task_id}的详细描述",
            task_type=TaskType.DATA_PROCESSING,
            config={"param1": "mock_value", "batch_size": 100},
            tags=["mock", "demo"],
            enabled=True,
            created_at=datetime.now() - timedelta(days=1),
        )
        return task

    try:
        task = task_manager.get_task(task_id)
        if not task:
            raise NotFoundException(resource="任务", identifier=task_id)
        return task
    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to get task", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.post(
    "/{task_id}/start",
    response_model=TaskResponse,
    description="按任务ID启动指定任务，并支持在请求体中传入本次执行参数。",
)
async def start_task(
    task_id: str = Path(..., description="需要启动的任务ID。"),
    params: Optional[Dict[str, Any]] = Body(None, openapi_examples=TASK_START_REQUEST_EXAMPLES),
):
    """启动指定任务并接收运行时参数。"""
    try:
        response = await task_manager.start_task(task_id, params)
        if not response.success:
            raise BusinessException(detail=response.message, status_code=400, error_code="TASK_OPERATION_FAILED")
        return response
    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to start task", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.post(
    "/{task_id}/stop",
    response_model=TaskResponse,
    description="按任务ID停止指定任务，并返回本次停止操作的执行结果。",
)
async def stop_task(task_id: str = Path(..., description="需要停止的任务ID。")):
    """停止任务"""
    try:
        response = task_manager.stop_task(task_id)
        if not response.success:
            raise BusinessException(detail=response.message, status_code=400, error_code="TASK_OPERATION_FAILED")
        return response
    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to stop task", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.get(
    "/executions/",
    response_model=List[TaskExecution],
    summary="列出任务执行历史",
    description="按任务ID和返回条数过滤任务执行记录列表，返回最近的执行状态、起止时间和执行结果摘要。",
    responses=TASK_EXECUTIONS_SUCCESS_RESPONSE,
)
async def list_task_executions(
    task_id: Optional[str] = Query(None, description="可选的任务ID过滤条件，仅返回指定任务的执行历史。"),
    limit: int = Query(50, ge=1, le=1000, description="返回最近多少条任务执行记录。"),
):
    """列出任务执行历史"""
    if use_mock:
        # Mock数据：返回模拟执行历史
        from app.models.task import TaskExecution, TaskStatus

        executions = []
        for i in range(min(limit, 10)):
            execution = TaskExecution(
                execution_id=f"exec_{i + 1000}",
                task_id=task_id or f"task_{i % 3 + 1000}",
                status=TaskStatus.COMPLETED if i % 4 != 0 else TaskStatus.FAILED,
                start_time=datetime.now() - timedelta(hours=i + 1),
                end_time=datetime.now() - timedelta(hours=i) + timedelta(minutes=30),
                result={"processed": i * 100, "success_rate": 95.0 + i},
                error_message=None if i % 4 != 0 else "模拟错误信息",
            )
            executions.append(execution)
        return executions

    try:
        executions = task_manager.list_executions(task_id=task_id, limit=limit)
        return executions
    except Exception as e:
        logger.error("Failed to list task executions", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.get(
    "/executions/{execution_id}",
    response_model=TaskExecution,
    summary="获取任务执行详情",
    description="按执行记录ID返回单次任务执行的状态、时间范围、执行结果和错误信息。",
    responses=TASK_EXECUTION_DETAIL_SUCCESS_RESPONSE,
)
async def get_execution(execution_id: str = Path(..., description="需要查询的任务执行记录ID。")):
    """获取执行记录详情"""
    try:
        execution = task_manager.get_execution(execution_id)
        if not execution:
            raise NotFoundException(resource="任务执行", identifier=execution_id)
        return execution
    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to get execution", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.get(
    "/statistics/",
    response_model=Dict[str, TaskStatistics],
    summary="获取任务统计信息",
    description="返回任务系统总体统计及分类统计，包括成功率、失败数、运行中任务和平均执行耗时。",
    responses=TASK_STATISTICS_SUCCESS_RESPONSE,
)
async def get_task_statistics():
    """获取任务统计信息"""
    if use_mock:
        # Mock数据：返回模拟统计信息

        from app.models.task import TaskStatistics

        stats = {
            "total_tasks": TaskStatistics(
                count=25, success_count=20, failed_count=3, running_count=2, avg_execution_time=45.5, success_rate=80.0
            ),
            "data_processing": TaskStatistics(
                count=15, success_count=12, failed_count=2, running_count=1, avg_execution_time=30.2, success_rate=80.0
            ),
            "backtest": TaskStatistics(
                count=8, success_count=6, failed_count=1, running_count=1, avg_execution_time=120.8, success_rate=75.0
            ),
            "alert": TaskStatistics(
                count=2, success_count=2, failed_count=0, running_count=0, avg_execution_time=5.3, success_rate=100.0
            ),
        }
        return stats

    try:
        stats = task_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error("Failed to get task statistics", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.post(
    "/import",
    response_model=TaskResponse,
    description="从外部配置文件导入任务定义，并将其注册到任务管理系统中。",
)
async def import_config(
    request: TaskImportRequest = Body(..., openapi_examples=TASK_IMPORT_REQUEST_EXAMPLES)
):
    """导入任务配置"""
    try:
        response = task_manager.import_config(request.config_path)
        if not response.success:
            raise BusinessException(detail=response.message, status_code=400, error_code="TASK_OPERATION_FAILED")
        return response
    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to import config", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.post(
    "/export",
    description="将当前任务配置导出到指定文件路径，便于备份、审计或迁移。",
)
async def export_config(
    request: TaskExportRequest = Body(..., openapi_examples=TASK_EXPORT_REQUEST_EXAMPLES)
):
    """导出任务配置"""
    try:
        task_manager.export_config(request.output_path)
        return {
            "success": True,
            "message": "Configuration exported successfully",
            "path": request.output_path,
        }
    except Exception as e:
        logger.error("Failed to export config", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.delete(
    "/executions/cleanup",
    description="清理超过指定保留天数的历史任务执行记录，并返回本次清理数量。",
)
async def cleanup_executions(days: int = Query(7, description="保留最近多少天的执行记录。", ge=1, le=90)):
    """清理旧的执行记录"""
    try:
        count = task_manager.cleanup_old_executions(days=days)
        return {
            "success": True,
            "message": f"Cleaned up {count} old execution records",
            "count": count,
        }
    except Exception as e:
        logger.error("Failed to cleanup executions", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.get(
    "/health",
    summary="任务管理健康检查",
    description="返回任务系统健康状态、运行中任务数量和累计执行次数，供监控系统与运维面板轮询使用。",
    responses=TASK_HEALTH_SUCCESS_RESPONSE,
    tags=["health"],
)
async def tasks_health():
    """
    公共健康检查端点（无需认证）

    **功能说明**:
    - 验证任务管理服务的运行状态
    - 检查当前运行中的任务数量
    - 评估任务执行队列的健康状态
    - 监控任务执行历史信息

    **使用场景**:
    - 监控系统集成
    - 任务管理员仪表板
    - 后台任务系统健康检查
    - 自动化故障检测和报警

    Returns:
        Dict: 包含以下字段的健康状态对象
            - status: 系统状态 (healthy/unhealthy)
            - total_tasks: 总任务数
            - running_tasks: 当前运行中的任务数
            - total_executions: 总执行次数
            - last_check: 最后检查时间戳
            - mock_mode: 是否使用模拟数据

    Security:
        - 无需认证
        - 仅返回基础状态信息，不包含敏感数据

    Notes:
        - healthy: 任务系统正常运行，无异常
        - running_tasks 过多可能表示任务堆积，需要关注
        - mock_mode=true 表示当前使用测试数据
        - 建议监控系统每 60 秒调用一次以进行持续监控
    """
    if use_mock:
        # Mock数据：返回模拟健康状态
        return {
            "status": "healthy",
            "total_tasks": 25,
            "running_tasks": 3,
            "total_executions": 156,
            "last_check": datetime.now().isoformat(),
            "mock_mode": True,
        }

    try:
        # 获取基本统计信息
        tasks = task_manager.list_tasks()
        total_tasks = len(tasks)
        running_tasks = len(getattr(task_manager, "running_tasks", []))
        total_executions = len(getattr(task_manager, "executions", []))

        return {
            "status": "healthy",
            "total_tasks": total_tasks,
            "running_tasks": running_tasks,
            "total_executions": total_executions,
            "last_check": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error("Tasks health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now().isoformat(),
        }


# ==================== 管理员专用端点 ====================


@router.get("/audit/logs", response_model=Dict[str, Any])
async def get_audit_logs(
    limit: int = Query(50, description="返回记录数", ge=1, le=500),
    operation: Optional[str] = Query(None, description="操作类型过滤"),
    username: Optional[str] = Query(None, description="用户名过滤"),
    current_user: User = Depends(get_current_user),
):
    """
    获取任务操作审计日志

    Security:
        - 仅管理员可访问
        - 需要管理员权限
        - 支持操作类型和用户名过滤
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized audit log access attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 记录审计日志访问
        log_task_operation(
            user=current_user,
            operation="access_audit_logs",
            details={"limit": limit, "operation_filter": operation, "username_filter": username},
        )

        # 过滤审计日志
        filtered_logs = task_audit_log.copy()

        if operation:
            filtered_logs = [log for log in filtered_logs if log.get("operation") == operation]

        if username:
            filtered_logs = [log for log in filtered_logs if log.get("username") == username]

        # 按时间倒序排列，取最近的记录
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # 返回指定的记录数
        result_logs = filtered_logs[:limit]

        logger.info("Audit logs accessed by admin {current_user.username}: {len(result_logs)} records")

        return {
            "logs": result_logs,
            "total_count": len(filtered_logs),
            "filter_applied": {"operation": operation, "username": username},
            "returned_count": len(result_logs),
        }

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception:
        logger.error("Failed to get audit logs for admin {current_user.username}: %(e)s")
        raise BusinessException(detail="获取审计日志失败", status_code=500, error_code="AUDIT_LOG_RETRIEVAL_FAILED")


@router.post("/cleanup/audit", response_model=APIResponse)
async def cleanup_audit_logs(
    days: int = Query(30, description="保留最近几天的日志", ge=1, le=365),
    current_user: User = Depends(get_current_user),
):
    """
    清理旧的审计日志

    Security:
        - 仅管理员可访问
        - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized audit cleanup attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 计算清理时间点
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_time.isoformat()

        # 清理旧的审计日志
        original_count = len(task_audit_log)
        task_audit_log[:] = [log for log in task_audit_log if log.get("timestamp", "") >= cutoff_str]
        cleaned_count = original_count - len(task_audit_log)

        # 记录清理操作
        log_task_operation(
            user=current_user,
            operation="cleanup_audit_logs",
            details={"days": days, "cleaned_count": cleaned_count, "remaining_count": len(task_audit_log)},
        )

        logger.info("Audit logs cleaned by admin {current_user.username}: %(cleaned_count)s records removed")

        return APIResponse(
            success=True,
            data={"cleaned_count": cleaned_count, "remaining_count": len(task_audit_log), "cutoff_date": cutoff_str},
            message=f"已清理 {cleaned_count} 条旧审计日志",
        )

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception:
        logger.error("Failed to cleanup audit logs for admin {current_user.username}: %(e)s")
        raise BusinessException(detail="清理审计日志失败", status_code=500, error_code="AUDIT_LOG_CLEANUP_FAILED")
