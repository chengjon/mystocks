"""
备份恢复 API 端点

提供完整的备份、恢复、状态查询功能
"""

from fastapi import APIRouter, HTTPException, Query, Body
from datetime import datetime
from typing import Optional, List

from src.backup_recovery import (
    BackupManager,
    RecoveryManager,
    BackupScheduler,
    IntegrityChecker,
)


router = APIRouter(prefix="/api/backup-recovery", tags=["Backup & Recovery"])

# 初始化管理器
backup_manager = BackupManager()
recovery_manager = RecoveryManager()
backup_scheduler = BackupScheduler()
integrity_checker = IntegrityChecker()


# ==================== 备份端点 ====================


@router.post("/backup/tdengine/full")
async def backup_tdengine_full():
    """执行 TDengine 全量备份"""
    try:
        metadata = backup_manager.backup_tdengine_full()

        return {
            "success": metadata.status == "success",
            "backup_id": metadata.backup_id,
            "backup_type": metadata.backup_type,
            "database": metadata.database,
            "start_time": metadata.start_time,
            "end_time": metadata.end_time,
            "duration_seconds": metadata.duration_seconds,
            "tables_backed_up": metadata.tables_backed_up,
            "total_rows": metadata.total_rows,
            "backup_size_mb": metadata.backup_size_bytes / 1024 / 1024,
            "compression_ratio": metadata.compression_ratio,
            "status": metadata.status,
            "error_message": metadata.error_message,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/backup/tdengine/incremental")
async def backup_tdengine_incremental(
    since_backup_id: str = Query(..., description="上次备份的 ID")
):
    """执行 TDengine 增量备份"""
    try:
        metadata = backup_manager.backup_tdengine_incremental(since_backup_id)

        return {
            "success": metadata.status == "success",
            "backup_id": metadata.backup_id,
            "backup_type": metadata.backup_type,
            "since_backup_id": since_backup_id,
            "total_rows": metadata.total_rows,
            "backup_size_mb": metadata.backup_size_bytes / 1024 / 1024,
            "status": metadata.status,
            "error_message": metadata.error_message,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Incremental backup failed: {str(e)}"
        )


@router.post("/backup/postgresql/full")
async def backup_postgresql_full():
    """执行 PostgreSQL 全量备份"""
    try:
        metadata = backup_manager.backup_postgresql_full()

        return {
            "success": metadata.status == "success",
            "backup_id": metadata.backup_id,
            "backup_type": metadata.backup_type,
            "database": metadata.database,
            "start_time": metadata.start_time,
            "end_time": metadata.end_time,
            "duration_seconds": metadata.duration_seconds,
            "tables_backed_up": len(metadata.tables_backed_up),
            "total_rows": metadata.total_rows,
            "backup_size_mb": metadata.backup_size_bytes / 1024 / 1024,
            "compression_ratio": metadata.compression_ratio,
            "status": metadata.status,
            "error_message": metadata.error_message,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.get("/backups")
async def list_backups(
    database: Optional[str] = Query(
        None, description="数据库类型 (tdengine/postgresql)"
    ),
    backup_type: Optional[str] = Query(None, description="备份类型 (full/incremental)"),
    status: Optional[str] = Query(None, description="备份状态 (success/failed)"),
):
    """列出所有备份"""
    try:
        all_backups = backup_manager.get_backup_list()

        # 过滤
        filtered_backups = [b for b in all_backups]

        if database:
            filtered_backups = [b for b in filtered_backups if b.database == database]
        if backup_type:
            filtered_backups = [
                b for b in filtered_backups if b.backup_type == backup_type
            ]
        if status:
            filtered_backups = [b for b in filtered_backups if b.status == status]

        return {
            "total": len(filtered_backups),
            "backups": [
                {
                    "backup_id": b.backup_id,
                    "backup_type": b.backup_type,
                    "database": b.database,
                    "start_time": b.start_time,
                    "end_time": b.end_time,
                    "duration_seconds": b.duration_seconds,
                    "total_rows": b.total_rows,
                    "backup_size_mb": b.backup_size_bytes / 1024 / 1024,
                    "compression_ratio": b.compression_ratio,
                    "status": b.status,
                }
                for b in filtered_backups
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


# ==================== 恢复端点 ====================


@router.post("/recovery/tdengine/full")
async def restore_tdengine_full(
    backup_id: str = Query(..., description="备份 ID"),
    target_tables: Optional[List[str]] = Query(None, description="指定要恢复的表"),
    dry_run: bool = Query(False, description="测试运行"),
):
    """从全量备份恢复 TDengine"""
    try:
        success, message = recovery_manager.restore_tdengine_from_full_backup(
            backup_id,
            target_tables=target_tables,
            dry_run=dry_run,
        )

        if success:
            return {
                "success": True,
                "backup_id": backup_id,
                "message": message,
                "dry_run": dry_run,
            }
        else:
            raise HTTPException(status_code=500, detail=message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recovery failed: {str(e)}")


@router.post("/recovery/tdengine/pitr")
async def restore_tdengine_pitr(
    target_time: str = Query(..., description="目标恢复时间 (ISO 8601)"),
    target_tables: Optional[List[str]] = Query(None, description="指定要恢复的表"),
):
    """TDengine 点对点时间恢复 (PITR)"""
    try:
        target_dt = datetime.fromisoformat(target_time)

        success, message = recovery_manager.restore_tdengine_point_in_time(
            target_dt,
            target_tables=target_tables,
        )

        if success:
            return {
                "success": True,
                "target_time": target_time,
                "message": message,
            }
        else:
            raise HTTPException(status_code=500, detail=message)

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid target_time format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PITR recovery failed: {str(e)}")


@router.post("/recovery/postgresql/full")
async def restore_postgresql_full(
    backup_id: str = Query(..., description="备份 ID"),
    target_tables: Optional[List[str]] = Query(None, description="指定要恢复的表"),
    dry_run: bool = Query(False, description="测试运行"),
):
    """从全量备份恢复 PostgreSQL"""
    try:
        success, message = recovery_manager.restore_postgresql_from_full_backup(
            backup_id,
            target_tables=target_tables,
            dry_run=dry_run,
        )

        if success:
            return {
                "success": True,
                "backup_id": backup_id,
                "message": message,
                "dry_run": dry_run,
            }
        else:
            raise HTTPException(status_code=500, detail=message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recovery failed: {str(e)}")


@router.get("/recovery/objectives")
async def get_recovery_objectives():
    """获取恢复目标 (RTO/RPO)"""
    return recovery_manager.get_recovery_time_objective()


# ==================== 调度端点 ====================


@router.post("/scheduler/start")
async def start_scheduler():
    """启动备份调度器"""
    try:
        backup_scheduler.start()
        return {"success": True, "message": "Backup scheduler started"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
async def stop_scheduler():
    """停止备份调度器"""
    try:
        backup_scheduler.stop()
        return {"success": True, "message": "Backup scheduler stopped"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.get("/scheduler/jobs")
async def get_scheduled_jobs():
    """获取所有计划的备份任务"""
    try:
        jobs = backup_scheduler.get_scheduled_jobs()
        return {
            "total_jobs": len(jobs),
            "jobs": jobs,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get scheduled jobs: {str(e)}"
        )


# ==================== 完整性检查端点 ====================


@router.get("/integrity/verify/{backup_id}")
async def verify_backup_integrity(backup_id: str):
    """验证备份完整性"""
    try:
        # 加载元数据
        metadata = backup_manager._load_metadata(backup_id)

        if not metadata:
            raise HTTPException(
                status_code=404, detail=f"Backup not found: {backup_id}"
            )

        # 验证恢复后的数据完整性
        if metadata["database"] == "tdengine":
            is_valid, details = integrity_checker.verify_tdengine_recovery(
                metadata,
                metadata["total_rows"],
            )
        elif metadata["database"] == "postgresql":
            is_valid, details = integrity_checker.verify_postgresql_recovery(
                metadata,
                metadata["total_rows"],
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown database: {metadata['database']}"
            )

        # 生成报告
        report_file = integrity_checker.generate_integrity_report(
            backup_id,
            {"is_valid": is_valid, **details},
        )

        return {
            "backup_id": backup_id,
            "is_valid": is_valid,
            "details": details,
            "report_file": str(report_file),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Integrity verification failed: {str(e)}"
        )


@router.post("/cleanup/old-backups")
async def cleanup_old_backups(retention_days: int = Query(30, description="保留天数")):
    """清理过期备份"""
    try:
        backup_manager.retention_days = retention_days
        backup_manager.cleanup_old_backups()

        return {
            "success": True,
            "message": f"Old backups (older than {retention_days} days) removed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
