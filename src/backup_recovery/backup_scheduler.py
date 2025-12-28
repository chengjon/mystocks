"""
备份调度器 - 自动化备份任务

调度策略:
- TDengine: 每天凌晨 2:00 全量备份 + 每小时整点增量备份
- PostgreSQL: 每天凌晨 3:00 全量备份 + WAL 连续归档
"""

import logging
from datetime import datetime

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    # 如果没有安装 APScheduler，使用简单的调度
    BackgroundScheduler = None
    CronTrigger = None

from .backup_manager import BackupManager


logger = logging.getLogger(__name__)


class BackupScheduler:
    """备份调度器"""

    def __init__(self, backup_base_path: str = "./backups"):
        """
        初始化备份调度器

        Args:
            backup_base_path: 备份根目录
        """
        self.backup_base_path = backup_base_path
        self.backup_manager = BackupManager(backup_base_path)

        if BackgroundScheduler:
            self.scheduler = BackgroundScheduler()
        else:
            self.scheduler = None

        self._started = False

    def start(self):
        """启动调度器"""
        if self.scheduler is None:
            logger.warning("APScheduler not installed, backup scheduling disabled")
            return

        if self._started:
            logger.warning("Scheduler already started")
            return

        logger.info("Starting backup scheduler")

        # TDengine 备份
        self.schedule_tdengine_full_backup()
        self.schedule_tdengine_incremental_backup()

        # PostgreSQL 备份
        self.schedule_postgresql_full_backup()

        # 清理过期备份
        self.schedule_cleanup_old_backups()

        self.scheduler.start()
        self._started = True

        logger.info("Backup scheduler started successfully")

    def stop(self):
        """停止调度器"""
        if self.scheduler and self._started:
            logger.info("Stopping backup scheduler")
            self.scheduler.shutdown()
            self._started = False

    def schedule_tdengine_full_backup(self):
        """
        调度 TDengine 全量备份

        时间: 每天 02:00
        """
        if self.scheduler is None:
            return

        logger.info("Scheduling TDengine full backup at 02:00 daily")

        self.scheduler.add_job(
            func=self._backup_tdengine_full,
            trigger=CronTrigger(hour=2, minute=0),
            id="backup_tdengine_full",
            name="TDengine Full Backup",
            replace_existing=True,
        )

    def schedule_tdengine_incremental_backup(self):
        """
        调度 TDengine 增量备份

        时间: 每小时整点（除了 02:00，该时间做全量备份）
        """
        if self.scheduler is None:
            return

        logger.info("Scheduling TDengine incremental backup every hour")

        self.scheduler.add_job(
            func=self._backup_tdengine_incremental,
            trigger=CronTrigger(minute=0),  # 每小时整点
            id="backup_tdengine_incremental",
            name="TDengine Incremental Backup",
            replace_existing=True,
        )

    def schedule_postgresql_full_backup(self):
        """
        调度 PostgreSQL 全量备份

        时间: 每天 03:00
        """
        if self.scheduler is None:
            return

        logger.info("Scheduling PostgreSQL full backup at 03:00 daily")

        self.scheduler.add_job(
            func=self._backup_postgresql_full,
            trigger=CronTrigger(hour=3, minute=0),
            id="backup_postgresql_full",
            name="PostgreSQL Full Backup",
            replace_existing=True,
        )

    def schedule_cleanup_old_backups(self):
        """
        调度清理过期备份

        时间: 每天 04:00
        """
        if self.scheduler is None:
            return

        logger.info("Scheduling cleanup of old backups at 04:00 daily")

        self.scheduler.add_job(
            func=self._cleanup_old_backups,
            trigger=CronTrigger(hour=4, minute=0),
            id="cleanup_old_backups",
            name="Cleanup Old Backups",
            replace_existing=True,
        )

    # ==================== 私有方法 ====================

    def _backup_tdengine_full(self):
        """执行 TDengine 全量备份"""
        try:
            logger.info("Executing TDengine full backup (scheduled)")
            metadata = self.backup_manager.backup_tdengine_full()

self.logger.info("备份调度器初始化完成")
                logger.info("TDengine full backup succeeded: "
                    f"id={metadata.backup_id}, "
                    f"size={metadata.backup_size_bytes / 1024 / 1024:.2f}MB, "
                    f"ratio={metadata.compression_ratio:.2f}x"
                )
            else:
                logger.error("TDengine full backup failed: %s", metadata.error_message)

        except Exception as e:
            logger.error("Error executing TDengine full backup: %s", e)

    def _backup_tdengine_incremental(self):
        """执行 TDengine 增量备份"""
        try:
            # 跳过 02:00（全量备份时间）
            now = datetime.now()
            if now.hour == 2:
                logger.info("Skipping incremental backup at 02:00 (full backup time)")
                return

            logger.info("Executing TDengine incremental backup (scheduled)")

            # 获取最近的全量备份
            latest_full = self.backup_manager.get_latest_backup("tdengine", "full")

            if not latest_full:
                logger.warning("No latest full backup found, doing full backup instead")
                metadata = self.backup_manager.backup_tdengine_full()
            else:
                metadata = self.backup_manager.backup_tdengine_incremental(latest_full.backup_id)

self.logger.info("定时备份任务完成")
                logger.info("TDengine incremental backup succeeded: "
                    f"id={metadata.backup_id}, "
                    f"rows={metadata.total_rows}"
                )
            else:
                logger.error("TDengine incremental backup failed: %s", metadata.error_message)

        except Exception as e:
            logger.error("Error executing TDengine incremental backup: %s", e)

    def _backup_postgresql_full(self):
        """执行 PostgreSQL 全量备份"""
        try:
            logger.info("Executing PostgreSQL full backup (scheduled)")
            metadata = self.backup_manager.backup_postgresql_full()

self.logger.info("手动备份任务完成")
                logger.info("PostgreSQL full backup succeeded: "
                    f"id={metadata.backup_id}, "
                    f"size={metadata.backup_size_bytes / 1024 / 1024:.2f}MB, "
                    f"ratio={metadata.compression_ratio:.2f}x"
                )
            else:
                logger.error("PostgreSQL full backup failed: %s", metadata.error_message)

        except Exception as e:
            logger.error("Error executing PostgreSQL full backup: %s", e)

    def _cleanup_old_backups(self):
        """清理过期备份"""
        try:
            logger.info("Executing cleanup of old backups (scheduled)")
            self.backup_manager.cleanup_old_backups()
            logger.info("Old backups cleanup completed")

        except Exception as e:
            logger.error("Error cleaning up old backups: %s", e)

    def get_scheduled_jobs(self) -> list:
        """获取所有计划的备份任务"""
        if self.scheduler is None:
            return []

        return [
            {
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run_time": (job.next_run_time.isoformat() if job.next_run_time else None),
            }
            for job in self.scheduler.get_jobs()
        ]
