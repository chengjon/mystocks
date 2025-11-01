"""
任务管理API路由
提供RESTful API接口用于任务管理
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
import structlog

from app.models.task import (
    TaskConfig, TaskExecution, TaskStatus, TaskType,
    TaskStatistics, TaskResponse
)
from app.services.task_manager import task_manager

logger = structlog.get_logger()
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/register", response_model=TaskResponse)
async def register_task(task_config: TaskConfig):
    """注册新任务"""
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
    tags: Optional[str] = Query(None, description="Comma-separated tags")
):
    """列出所有任务"""
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
async def start_task(
    task_id: str,
    params: Optional[Dict[str, Any]] = Body(None)
):
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
async def list_executions(
    task_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """列出执行记录"""
    try:
        executions = task_manager.list_executions(task_id=task_id, limit=limit)
        return executions
    except Exception as e:
        logger.error("Failed to list executions", error=str(e))
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
async def get_statistics(task_id: Optional[str] = None):
    """获取任务统计信息"""
    try:
        statistics = task_manager.get_statistics(task_id=task_id)
        return statistics
    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
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
        return {"success": True, "message": "Configuration exported successfully", "path": output_path}
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
            "count": count
        }
    except Exception as e:
        logger.error("Failed to cleanup executions", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """任务管理器健康检查"""
    try:
        total_tasks = len(task_manager.tasks)
        running_tasks = len(task_manager.running_tasks)
        total_executions = len(task_manager.executions)

        return {
            "status": "healthy",
            "total_tasks": total_tasks,
            "running_tasks": running_tasks,
            "total_executions": total_executions
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
