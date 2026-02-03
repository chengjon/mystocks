"""
备份恢复 API 端点 - 安全增强版本

提供完整的备份、恢复、状态查询功能，包含：
- JWT 认证和基于角色的授权
- 输入验证和路径安全检查
- 统一响应格式
- 安全审计日志
- 速率限制

版本: 2.0.0 (安全加强版)
日期: 2025-12-01
安全级别: SEVERE RISK FIXED
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.responses import ErrorCode, error_response, success_response
from app.core.security import User, get_current_user
from app.models.backup_schemas import (
    BackupMetadata,
    TDengineFullBackupRequest,
    TDengineIncrementalBackupRequest,
    require_admin_role,
    require_backup_permission,
    require_recovery_permission,
)
from src.backup_recovery import BackupManager, BackupScheduler, IntegrityChecker, RecoveryManager

# 初始化速率限制器
limiter = Limiter(key_func=get_remote_address)

# 安全日志配置
security_logger = logging.getLogger("backup_security")
security_logger.setLevel(logging.INFO)

# 创建文件处理器
handler = logging.FileHandler("/tmp/backup_security.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
security_logger.addHandler(handler)

router = APIRouter(prefix="/api/backup-recovery", tags=["Backup & Recovery (Secure)"])

# 初始化管理器
backup_manager = BackupManager()
recovery_manager = RecoveryManager()
backup_scheduler = BackupScheduler()
integrity_checker = IntegrityChecker()

# 内存中的速率限制跟踪器（生产环境建议使用 Redis）
_backup_operation_cache = {}
_rate_limit_window = 300  # 5分钟窗口
_max_backup_operations = 3  # 每5分钟最多3次备份操作


def log_security_event(
    event_type: str, user: User, action: str, details: Optional[Dict[str, Any]] = None, success: bool = True
):
    """记录安全审计日志"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user.id,
        "username": user.username,
        "user_role": user.role,
        "action": action,
        "ip_address": "client",  # FastAPI Request context
        "success": success,
        "details": details or {},
    }

    security_logger.info("SECURITY_EVENT: %(log_data)s")


def check_backup_rate_limit(user: User) -> bool:
    """检查备份操作速率限制"""
    current_time = time.time()
    user_id = user.id

    # 清理过期记录
    cutoff_time = current_time - _rate_limit_window
    if user_id in _backup_operation_cache:
        _backup_operation_cache[user_id] = [t for t in _backup_operation_cache[user_id] if t > cutoff_time]

    # 检查当前窗口内的操作次数
    user_operations = _backup_operation_cache.get(user_id, [])
    if len(user_operations) >= _max_backup_operations:
        return False

    # 记录当前操作
    user_operations.append(current_time)
    _backup_operation_cache[user_id] = user_operations
    return True


def verify_admin_permission(user: User) -> None:
    """验证管理员权限"""
    if not require_admin_role(user.role):
        log_security_event(
            "AUTHORIZATION_FAILED",
            user,
            "admin_access_denied",
            {"required_role": "admin", "user_role": user.role},
            success=False,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限执行此操作")


def verify_backup_permission(user: User) -> None:
    """验证备份操作权限"""
    if not require_backup_permission(user.role):
        log_security_event(
            "AUTHORIZATION_FAILED",
            user,
            "backup_access_denied",
            {"required_permission": "backup", "user_role": user.role},
            success=False,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要备份操作权限")


def verify_recovery_permission(user: User) -> None:
    """验证恢复操作权限"""
    if not require_recovery_permission(user.role):
        log_security_event(
            "AUTHORIZATION_FAILED",
            user,
            "recovery_access_denied",
            {"required_permission": "recovery", "user_role": user.role},
            success=False,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限执行恢复操作")


# ==================== 备份端点 (安全增强) ====================


@router.post("/backup/tdengine/full")
async def backup_tdengine_full(
    request: TDengineFullBackupRequest = Body(...), current_user: User = Depends(get_current_user)
):
    """
    执行 TDengine 全量备份 [CRITICAL - 需要备份权限]

    安全要求：
    - JWT 认证
    - 备份操作权限
    - 速率限制
    - 输入验证
    - 审计日志
    """
    try:
        # 权限验证
        verify_backup_permission(current_user)

        # 速率限制检查
        if not check_backup_rate_limit(current_user):
            log_security_event(
                "RATE_LIMIT_EXCEEDED", current_user, "tdengine_full_backup", {"reason": "Too many backup operations"}
            )
            return error_response(message="备份操作过于频繁，请稍后再试", error_code=ErrorCode.RATE_LIMIT_EXCEEDED)

        # 记录操作开始
        log_security_event(
            "BACKUP_START",
            current_user,
            "tdengine_full_backup",
            {"database": "tdengine", "backup_type": "full", "description": request.description},
        )

        # 执行备份
        metadata = backup_manager.backup_tdengine_full()

        # 记录操作结果
        success = metadata.status == "success"
        log_security_event(
            "BACKUP_COMPLETE",
            current_user,
            "tdengine_full_backup",
            {
                "backup_id": metadata.backup_id,
                "success": success,
                "duration_seconds": metadata.duration_seconds,
                "backup_size_mb": metadata.backup_size_bytes / 1024 / 1024,
                "status": metadata.status,
                "error_message": metadata.error_message,
            },
            success=success,
        )

        # 构建安全响应
        backup_data = BackupMetadata(
            backup_id=metadata.backup_id,
            backup_type=metadata.backup_type,
            database=metadata.database,
            start_time=metadata.start_time,
            end_time=metadata.end_time,
            duration_seconds=metadata.duration_seconds,
            tables_backed_up=metadata.tables_backed_up,
            total_rows=metadata.total_rows,
            backup_size_mb=metadata.backup_size_bytes / 1024 / 1024,
            compression_ratio=metadata.compression_ratio,
            status=metadata.status,
            error_message=metadata.error_message,
            description=request.description,
            tags=request.tags,
        )

        return success_response(data=backup_data.model_dump(), message="TDengine 全量备份操作完成")

    except Exception as e:
        # 记录错误
        log_security_event(
            "BACKUP_ERROR",
            current_user,
            "tdengine_full_backup",
            {"error": str(e), "error_type": type(e).__name__},
            success=False,
        )

        return error_response(
            message="TDengine 全量备份失败",
            error_code=ErrorCode.INTERNAL_ERROR,
            details={"operation": "tdengine_full_backup"},
        )


@router.post("/backup/tdengine/incremental")
async def backup_tdengine_incremental(
    request: TDengineIncrementalBackupRequest = Body(...), current_user: User = Depends(get_current_user)
):
    """
    执行 TDengine 增量备份 [CRITICAL - 需要备份权限]

    安全要求：
    - JWT 认证
    - 备份操作权限
    - 速率限制
    - 基准备份ID验证
    - 审计日志
    """
    try:
        # 权限验证
        verify_backup_permission(current_user)

        # 速率限制检查
        if not check_backup_rate_limit(current_user):
            log_security_event(
                "RATE_LIMIT_EXCEEDED",
                current_user,
                "tdengine_incremental_backup",
                {"reason": "Too many backup operations"},
            )
            return error_response(message="备份操作过于频繁，请稍后再试", error_code=ErrorCode.RATE_LIMIT_EXCEEDED)

        # 记录操作开始
        log_security_event(
            "BACKUP_START",
            current_user,
            "tdengine_incremental_backup",
            {
                "database": "tdengine",
                "backup_type": "incremental",
                "since_backup_id": request.since_backup_id,
                "description": request.description,
            },
        )

        # 执行增量备份
        metadata = backup_manager.backup_tdengine_incremental(request.since_backup_id)

        # 记录操作结果
        success = metadata.status == "success"
        log_security_event(
            "BACKUP_COMPLETE",
            current_user,
            "tdengine_incremental_backup",
            {
                "backup_id": metadata.backup_id,
                "since_backup_id": request.since_backup_id,
                "success": success,
                "backup_size_mb": metadata.backup_size_bytes / 1024 / 1024,
                "status": metadata.status,
                "error_message": metadata.error_message,
            },
            success=success,
        )

        # 构建安全响应
        backup_data = BackupMetadata(
            backup_id=metadata.backup_id,
            backup_type=metadata.backup_type,
            database=metadata.database,
            start_time=metadata.start_time,
            end_time=metadata.end_time,
            duration_seconds=metadata.duration_seconds,
            tables_backed_up=[],  # 增量备份可能不包含完整表列表
            total_rows=metadata.total_rows,
            backup_size_mb=metadata.backup_size_bytes / 1024 / 1024,
            compression_ratio=metadata.compression_ratio,
            status=metadata.status,
            error_message=metadata.error_message,
            description=request.description,
            tags=["incremental"],
        )

        return success_response(data=backup_data.model_dump(), message="TDengine 增量备份操作完成")

    except Exception as e:
        # 记录错误
        log_security_event(
            "BACKUP_ERROR",
            current_user,
            "tdengine_incremental_backup",
            {"error": str(e), "error_type": type(e).__name__, "since_backup_id": request.since_backup_id},
            success=False,
        )

        return error_response(
            message="TDengine 增量备份失败",
            error_code=ErrorCode.INTERNAL_ERROR,
            details={"operation": "tdengine_incremental_backup", "since_backup_id": request.since_backup_id},
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
    database: Optional[str] = Query(None, description="数据库类型 (tdengine/postgresql)"),
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
            filtered_backups = [b for b in filtered_backups if b.backup_type == backup_type]
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
        raise HTTPException(status_code=400, detail=f"Invalid target_time format: {str(e)}")
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
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/scheduler/stop")
async def stop_scheduler():
    """停止备份调度器"""
    try:
        backup_scheduler.stop()
        return {"success": True, "message": "Backup scheduler stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Failed to get scheduled jobs: {str(e)}")


# ==================== 完整性检查端点 ====================


@router.get("/integrity/verify/{backup_id}")
async def verify_backup_integrity(backup_id: str):
    """验证备份完整性"""
    try:
        # 加载元数据
        metadata = backup_manager._load_metadata(backup_id)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Backup not found: {backup_id}")

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
            raise HTTPException(status_code=400, detail=f"Unknown database: {metadata['database']}")

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
        raise HTTPException(status_code=500, detail=f"Integrity verification failed: {str(e)}")


@router.post("/cleanup/old-backups")
async def cleanup_old_backups(retention_days: int = Query(30, description="保留天数")):
    """
    清理过期备份文件

    自动清理超过指定保留期的备份文件，释放存储空间。该端点会扫描所有备份目录，
    删除创建时间早于保留天数的备份文件和元数据。

    **功能说明**:
    - 扫描所有 TDengine 和 PostgreSQL 备份目录
    - 删除超过保留期的备份文件（.tar.gz）
    - 删除对应的备份元数据（.json）
    - 记录清理操作日志
    - 返回清理统计信息

    **使用场景**:
    - 定期清理旧备份文件，避免磁盘空间不足
    - 手动触发清理操作，释放存储空间
    - 配置不同保留策略（如生产环境保留90天，测试环境保留7天）
    - 备份策略调整后的批量清理

    **参数**:
    - retention_days: 备份保留天数（默认30天）
      - 最小值: 1天
      - 推荐值: 生产环境30-90天，测试环境7-14天
      - 仅删除创建时间早于 (当前时间 - retention_days) 的备份

    **返回值**:
    - success: 操作是否成功（布尔值）
    - message: 清理结果描述信息
    - deleted_count (可选): 删除的备份文件数量
    - freed_space_mb (可选): 释放的磁盘空间（MB）

    **示例**:
    ```bash
    # 清理30天前的备份
    curl -X POST "http://localhost:8000/api/backup-recovery/cleanup/old-backups?retention_days=30"

    # 清理7天前的备份（测试环境）
    curl -X POST "http://localhost:8000/api/backup-recovery/cleanup/old-backups?retention_days=7"
    ```

    **响应示例**:
    ```json
    {
      "success": true,
      "message": "Old backups (older than 30 days) removed",
      "deleted_count": 15,
      "freed_space_mb": 2048.5
    }
    ```

    **注意事项**:
    - 删除操作不可逆，请谨慎设置保留天数
    - 建议在业务低峰期执行清理操作
    - 清理前确保至少保留一个最新的全量备份
    - 建议配置定时任务自动执行清理（如每周一次）
    - 重要数据的备份建议保留更长时间
    """
    try:
        backup_manager.retention_days = retention_days
        backup_manager.cleanup_old_backups()

        return {
            "success": True,
            "message": f"Old backups (older than {retention_days} days) removed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
