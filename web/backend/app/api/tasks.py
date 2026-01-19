"""
任务管理API路由
提供RESTful API接口用于任务管理

安全级别：分级别访问控制
- Public endpoints: 健康检查（无需认证）
- User endpoints: 任务查看、基础操作（需要用户认证）
- Admin endpoints: 任务管理、执行控制（需要管理员权限）
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Body, Depends, Path, Query, status
from pydantic import BaseModel, Field, field_validator

from app.api.auth import User, get_current_user
from app.core.exceptions import BusinessException, NotFoundException, ForbiddenException
from app.core.responses import APIResponse
from app.models.task import TaskConfig, TaskExecution, TaskResponse, TaskStatistics
from app.services.task_manager import task_manager

# Mock数据支持
use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

logger = structlog.get_logger()
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Rate limiting for task operations
task_operation_count = {}

# Audit log for task operations
task_audit_log = []


# ============================================================================
# Enhanced Validation Models
# ============================================================================


class TaskRegistrationRequest(BaseModel):
    """任务注册请求"""

    name: str = Field(..., description="任务名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="任务描述", max_length=500)
    task_type: str = Field(
        ...,
        description="任务类型",
        pattern=r"^(DATA_PROCESSING|MARKET_ANALYSIS|SIGNAL_GENERATION|NOTIFICATION|CLEANUP|BACKTEST|REPORT)$",
    )
    config: Dict[str, Any] = Field(..., description="任务配置参数")
    tags: Optional[List[str]] = Field(None, description="任务标签")
    enabled: bool = Field(True, description="是否启用")
    schedule: Optional[str] = Field(None, description="调度表达式(cron格式)", max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证任务名称"""
        if not v.strip():
            raise ValueError("任务名称不能为空")

        # 检查是否包含特殊字符
        if re.search(r'[<>"\'/\\]', v):
            raise ValueError("任务名称不能包含特殊字符: < > \" ' / \\")

        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """验证任务描述"""
        if v is None:
            return v

        # 检查是否包含恶意脚本标签
        if re.search(r"<script|javascript:|onload=|onerror=", v, re.IGNORECASE):
            raise ValueError("任务描述包含不安全的脚本或标签")

        return v.strip()

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """验证任务配置"""
        if not v:
            raise ValueError("任务配置不能为空")

        # 限制配置大小
        if len(json.dumps(v)) > 10000:  # 10KB限制
            raise ValueError("任务配置过大，请减小配置内容")

        # 安全检查：防止命令注入
        config_str = json.dumps(v).lower()
        dangerous_patterns = [
            "__import__",
            "eval(",
            "exec(",
            "subprocess",
            "os.system",
            "popen",
            "shell=True",
            "$(",
            "&&",
            "||",
            ";",
            "><",
            "`",
        ]

        for pattern in dangerous_patterns:
            if pattern in config_str:
                raise ValueError(f"任务配置包含不安全的操作: {pattern}")

        # 检查是否有可疑的路径操作
        path_patterns = ["/etc/", "/bin/", "/usr/bin", "/var/", "system32"]
        for pattern in path_patterns:
            if pattern in config_str:
                raise ValueError(f"任务配置包含不安全的路径操作: {pattern}")

        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """验证任务标签"""
        if v is None:
            return v

        if len(v) > 10:
            raise ValueError("任务标签数量不能超过10个")

        for tag in v:
            if not tag:
                raise ValueError("标签不能为空")
            if len(tag) > 20:
                raise ValueError(f'标签 "{tag}" 长度超过限制')
            if re.search(r'[<>"\'/\\]', tag):
                raise ValueError(f'标签 "{tag}" 包含特殊字符')

        return [tag.strip() for tag in v]

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: Optional[str]) -> Optional[str]:
        """验证调度表达式"""
        if v is None:
            return v

        # 基本的cron格式验证 (分 时 日 月 周)
        cron_pattern = (
            r"^(\*|([0-9]|[1-5][0-9])\/\d+|([0-9]|[1-5][0-9])|"
            r"([0-9]|[1-5][0-9])-([0-9]|[1-5][0-9])|"
            r"([0-9]|[1-5][0-9])(,([0-9]|[1-5][0-9]))*)\s+"
            r"(\*|([0-9]|1[0-9]|2[0-3])\/\d+|([0-9]|1[0-9]|2[0-3])|"
            r"([0-9]|1[0-9]|2[0-3])-([0-9]|1[0-9]|2[0-3])|"
            r"([0-9]|1[0-9]|2[0-3])(,([0-9]|1[0-9]|2[0-3]))*)\s+"
            r"(\*|([1-9]|[1-2][0-9]|3[0-1])\/\d+|([1-9]|[1-2][0-9]|3[0-1])|"
            r"([1-9]|[1-2][0-9]|3[0-1])-([1-9]|[1-2][0-9]|3[0-1])|"
            r"([1-9]|[1-2][0-9]|3[0-1])(,([1-9]|[1-2][0-9]|3[0-1]))*)\s+"
            r"(\*|([1-9]|1[0-2])\/\d+|([1-9]|1[0-2])|"
            r"([1-9]|1[0-2])-([1-9]|1[0-2])|([1-9]|1[0-2])(,([1-9]|1[0-2]))*)\s+"
            r"(\*|([0-6])\/\d+|([0-6])|([0-6])-([0-6])|([0-6])(,([0-6]))*)$"
        )

        if not re.match(cron_pattern, v):
            raise ValueError("无效的cron表达式格式")

        return v


# ============================================================================
# Security Helper Functions
# ============================================================================


def check_task_rate_limit(user_id: int, max_operations_per_minute: int = 10) -> bool:
    """
    检查任务操作频率限制

    Args:
        user_id: 用户ID
        max_operations_per_minute: 每分钟最大操作数

    Returns:
        bool: 是否允许操作
    """
    current_time = int(time.time() / 60)  # 分钟级时间窗口

    if user_id not in task_operation_count:
        task_operation_count[user_id] = {}

    if current_time not in task_operation_count[user_id]:
        task_operation_count[user_id][current_time] = 0

    task_operation_count[user_id][current_time] += 1

    # 清理过期的时间窗口
    for old_time in list(task_operation_count[user_id].keys()):
        if current_time - old_time > 5:  # 保留5分钟内的记录
            del task_operation_count[user_id][old_time]

    return task_operation_count[user_id][current_time] <= max_operations_per_minute


def check_admin_privileges(user: User) -> bool:
    """检查管理员权限"""
    return user.role in ["admin", "backup_operator"]


def log_task_operation(user: User, operation: str, task_id: Optional[str] = None, details: Optional[Dict] = None):
    """
    记录任务操作审计日志

    Args:
        user: 操作用户
        operation: 操作类型
        task_id: 任务ID（可选）
        details: 操作详情（可选）
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user.id,
        "username": user.username,
        "operation": operation,
        "task_id": task_id,
        "details": details,
        "ip_address": getattr(user, "ip_address", "unknown"),
    }

    task_audit_log.append(audit_entry)

    # 限制审计日志大小，保留最近1000条记录
    if len(task_audit_log) > 1000:
        task_audit_log.pop(0)

    logger.info(f"Task operation logged: {operation} by {user.username}", audit_data=audit_entry)


class TaskQueryParams(BaseModel):
    """任务查询参数"""

    task_type: Optional[str] = Field(
        None,
        description="任务类型",
        pattern=r"^(DATA_PROCESSING|MARKET_ANALYSIS|SIGNAL_GENERATION|NOTIFICATION|CLEANUP|BACKTEST|REPORT)$",
    )
    tags: Optional[str] = Field(None, description="逗号分隔的任务标签", max_length=200)
    status: Optional[str] = Field(None, description="任务状态", pattern=r"^(PENDING|RUNNING|SUCCESS|FAILED|CANCELLED)$")
    enabled: Optional[bool] = Field(None, description="是否启用")
    limit: int = Field(50, description="返回数量", ge=1, le=200)
    offset: int = Field(0, description="偏移量", ge=0, le=10000)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        """验证标签参数"""
        if v is None:
            return v

        tags = v.split(",")
        if len(tags) > 10:
            raise ValueError("查询标签数量不能超过10个")

        for tag in tags:
            tag = tag.strip()
            if not tag:
                raise ValueError("标签不能为空")
            if len(tag) > 20:
                raise ValueError(f'标签 "{tag}" 长度超过限制')

        return v


class TaskExecutionRequest(BaseModel):
    """任务执行请求"""

    task_id: str = Field(..., description="任务ID", min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    force: bool = Field(False, description="是否强制执行")
    params: Optional[Dict[str, Any]] = Field(None, description="执行参数")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """验证任务ID"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("任务ID只能包含字母、数字、下划线和连字符")
        return v


@router.post("/register", response_model=TaskResponse)
async def register_task(task_config: TaskConfig, current_user: User = Depends(get_current_user)):
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

        logger.info(f"Task registered successfully by {current_user.username}: {task_config.name}")
        return response

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Failed to register task for user {current_user.username}: {e}")
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

        logger.info(f"Task {task_id} unregistered successfully by {current_user.username}")
        return response

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Failed to unregister task {task_id} for user {current_user.username}: {e}")
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

        logger.info(f"Tasks listed by {current_user.username}: {len(tasks)} tasks")
        return tasks

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Failed to list tasks for user {current_user.username}: {e}")
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


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(task_id: str, params: Optional[Dict[str, Any]] = Body(None)):
    """启动任务"""
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


@router.post("/{task_id}/stop", response_model=TaskResponse)
async def stop_task(task_id: str):
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


@router.get("/executions/", response_model=List[TaskExecution])
async def list_task_executions(
    task_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
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


@router.get("/executions/{execution_id}", response_model=TaskExecution)
async def get_execution(execution_id: str):
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


@router.get("/statistics/", response_model=Dict[str, TaskStatistics])
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


@router.post("/import", response_model=TaskResponse)
async def import_config(config_path: str = Body(..., embed=True)):
    """导入任务配置"""
    try:
        response = task_manager.import_config(config_path)
        if not response.success:
            raise BusinessException(detail=response.message, status_code=400, error_code="TASK_OPERATION_FAILED")
        return response
    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to import config", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.post("/export")
async def export_config(output_path: str = Body(..., embed=True)):
    """导出任务配置"""
    try:
        task_manager.export_config(output_path)
        return {
            "success": True,
            "message": "Configuration exported successfully",
            "path": output_path,
        }
    except Exception as e:
        logger.error("Failed to export config", error=str(e))
        raise BusinessException(detail=str(e), status_code=500, error_code="TASK_OPERATION_FAILED")


@router.delete("/executions/cleanup")
async def cleanup_executions(days: int = Query(7, ge=1, le=90)):
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


@router.get("/health", summary="任务管理健康检查", description="检查后台任务系统的运行状态", tags=["health"])
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
            logger.warning(f"Unauthorized audit log access attempt by user: {current_user.username}")
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

        logger.info(f"Audit logs accessed by admin {current_user.username}: {len(result_logs)} records")

        return {
            "logs": result_logs,
            "total_count": len(filtered_logs),
            "filter_applied": {"operation": operation, "username": username},
            "returned_count": len(result_logs),
        }

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Failed to get audit logs for admin {current_user.username}: {e}")
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
            logger.warning(f"Unauthorized audit cleanup attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 计算清理时间点
        cutoff_time = datetime.utcnow() - timedelta(days=days)
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

        logger.info(f"Audit logs cleaned by admin {current_user.username}: {cleaned_count} records removed")

        return APIResponse(
            success=True,
            data={"cleaned_count": cleaned_count, "remaining_count": len(task_audit_log), "cutoff_date": cutoff_str},
            message=f"已清理 {cleaned_count} 条旧审计日志",
        )

    except (BusinessException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup audit logs for admin {current_user.username}: {e}")
        raise BusinessException(detail="清理审计日志失败", status_code=500, error_code="AUDIT_LOG_CLEANUP_FAILED")
