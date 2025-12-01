"""
任务管理API路由
提供RESTful API接口用于任务管理
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Body, HTTPException, Query

from app.models.task import TaskConfig, TaskExecution, TaskResponse, TaskStatistics, TaskStatus, TaskType
from app.services.task_manager import task_manager

# Mock数据支持
use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

logger = structlog.get_logger()
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/register", response_model=TaskResponse)
async def register_task(task_config: TaskConfig):
    """注册新任务"""
    if use_mock:
        # Mock数据响应
        import random

        task_id = f"task_{random.randint(1000, 9999)}"
        return TaskResponse(success=True, message="任务注册成功", data={"task_id": task_id, "status": "registered"})

    try:
        response = task_manager.register_task(task_config)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        logger.error("Failed to register task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", response_model=TaskResponse)
async def unregister_task(task_id: str):
    """注销任务"""
    try:
        response = task_manager.unregister_task(task_id)
        if not response.success:
            raise HTTPException(status_code=404, detail=response.message)
        return response
    except Exception as e:
        logger.error("Failed to unregister task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TaskConfig])
async def list_tasks(
    task_type: Optional[TaskType] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
):
    """列出所有任务"""
    if use_mock:
        # Mock数据：返回模拟任务列表
        import random

        from app.models.task import TaskConfig, TaskType

        mock_tasks = []
        for i in range(5):
            task = TaskConfig(
                task_id=f"task_{i+1000}",
                name=f"模拟任务_{i+1}",
                description=f"这是一个模拟任务_{i+1}",
                task_type=TaskType.DATA_PROCESSING,
                config={"param1": f"value{i+1}"},
                tags=[f"tag{i+1}", "mock"],
                enabled=True,
                created_at=datetime.now() - timedelta(days=i),
            )
            mock_tasks.append(task)
        return mock_tasks

    try:
        tag_list = tags.split(",") if tags else None
        tasks = task_manager.list_tasks(task_type=task_type, tags=tag_list)
        return tasks
    except Exception as e:
        logger.error("Failed to list tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskConfig)
async def get_task(task_id: str):
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
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(task_id: str, params: Optional[Dict[str, Any]] = Body(None)):
    """启动任务"""
    try:
        response = await task_manager.start_task(task_id, params)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/stop", response_model=TaskResponse)
async def stop_task(task_id: str):
    """停止任务"""
    try:
        response = task_manager.stop_task(task_id)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to stop task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


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
                execution_id=f"exec_{i+1000}",
                task_id=task_id or f"task_{i%3+1000}",
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}", response_model=TaskExecution)
async def get_execution(execution_id: str):
    """获取执行记录详情"""
    try:
        execution = task_manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get execution", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/", response_model=Dict[str, TaskStatistics])
async def get_task_statistics():
    """获取任务统计信息"""
    if use_mock:
        # Mock数据：返回模拟统计信息
        import random

        from app.models.task import TaskStatistics, TaskStatus

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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=TaskResponse)
async def import_config(config_path: str = Body(..., embed=True)):
    """导入任务配置"""
    try:
        response = task_manager.import_config(config_path)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to import config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="任务管理健康检查", description="检查后台任务系统的运行状态", tags=["health"])
async def tasks_health():
    """
    检查后台任务管理系统的健康状态

    此端点用于监控任务调度系统、任务执行队列和相关服务的运行情况。

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

    Examples:
        获取任务系统健康状态:
        ```bash
        curl -H "Authorization: Bearer TOKEN" \\
             http://localhost:8000/api/tasks/health
        ```

        正常响应示例:
        ```json
        {
            "status": "healthy",
            "total_tasks": 25,
            "running_tasks": 3,
            "total_executions": 156,
            "last_check": "2025-11-30T21:06:45.123456",
            "mock_mode": false
        }
        ```

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
        running_tasks = len(task_manager.running_tasks)
        total_executions = len(task_manager.executions)

        return {
            "status": "healthy",
            "total_tasks": total_tasks,
            "running_tasks": running_tasks,
            "total_executions": total_executions,
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
