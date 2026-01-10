"""
Initialize Indicator Schedule
=============================

Sets up the daily indicator calculation cron job.
"""
import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.join(os.getcwd(), "web", "backend"))

from app.models.task import TaskConfig, TaskSchedule, TaskType
from app.services.task_manager import task_manager
from app.services.task_scheduler import task_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_schedule():
    logger.info("Initializing daily indicator schedule...")
    
    config = TaskConfig(
        task_id="daily_indicator_calc",
        task_name="Daily Indicator Calculation (Batch)",
        task_type=TaskType.INDICATOR_CALC,
        task_module="app.tasks.indicator_tasks",
        task_function="batch_calculate_indicators",
        description="Calculates SMA, MACD, RSI etc. for all stocks daily at 02:00",
        schedule=TaskSchedule(
            schedule_type="cron",
            cron_expression="0 2 * * *", # 2:00 AM
            enabled=True
        ),
        timeout=3600 * 2 # 2 hours
    )
    
    # Register Task
    resp = task_manager.register_task(config)
    if resp.success:
        logger.info(f"Task registered: {resp.message}")
        
        # Schedule it
        if task_scheduler.schedule_task(config):
             logger.info("Task scheduled successfully!")
        else:
             logger.error("Failed to schedule task.")
    else:
        logger.warning(f"Task registration failed: {resp.message}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_schedule())
