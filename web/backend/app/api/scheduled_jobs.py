"""
Scheduled Jobs API
定时任务管理API

Provides endpoints to:
- 查看定时任务状态
- 手动触发数据更新
- 查看下次执行时间
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import structlog

from app.core.security import get_current_user, User, require_admin
from app.services.scheduled_data_update import scheduler_service

router = APIRouter()
logger = structlog.get_logger()


@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取定时任务状态

    Returns:
        {
            "status": "active" | "not_scheduled",
            "job_id": "daily_fund_flow_update",
            "job_name": "Daily Fund Flow Data Update",
            "next_run_time": "2025-10-31 15:30:00",
            "trigger": "cron[day_of_week='mon-fri', hour='15', minute='30']",
            "industry_types": ["csrc", "sw_l1", "sw_l2"],
            "max_retries": 3
        }
    """
    try:
        status = scheduler_service.get_job_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger")
async def trigger_manual_update(
    current_user: User = Depends(require_admin),
) -> Dict[str, Any]:
    """
    手动触发数据更新

    Requires: Admin权限

    Returns:
        {
            "success": true,
            "message": "Manual update triggered",
            "results": {
                "csrc": 86,
                "sw_l1": 100,
                "sw_l2": 31
            }
        }
    """
    try:
        logger.info(f"Manual data update triggered by user: {current_user.username}")
        results = scheduler_service.trigger_manual_update()

        total_records = sum(results.values())
        return {
            "success": True,
            "message": "Manual update completed",
            "results": results,
            "total_records": total_records,
        }
    except Exception as e:
        logger.error(f"Manual update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.get("/next-run")
async def get_next_run_time(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取下次执行时间

    Returns:
        {
            "success": true,
            "next_run_time": "2025-10-31 15:30:00",
            "time_until_next_run": "23h 45m"
        }
    """
    try:
        from datetime import datetime

        next_run = scheduler_service.get_next_run_time()

        if next_run == "N/A":
            return {
                "success": True,
                "next_run_time": None,
                "time_until_next_run": "Not scheduled",
            }

        # 计算距离下次执行的时间
        next_run_dt = datetime.strptime(next_run, "%Y-%m-%d %H:%M:%S")
        time_until = next_run_dt - datetime.now()
        hours, remainder = divmod(int(time_until.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        time_until_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        return {
            "success": True,
            "next_run_time": next_run,
            "time_until_next_run": time_until_str,
        }
    except Exception as e:
        logger.error(f"Failed to get next run time: {e}")
        raise HTTPException(status_code=500, detail=str(e))
