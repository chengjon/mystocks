"""
备份完整性验证实现。
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.api.backup_recovery_secure.backup_security_support import log_security_event, verify_backup_permission
from app.core.responses import ErrorCode, error_response, success_response
from app.models.backup_schemas import IntegrityVerificationResult


async def verify_backup_integrity_impl(backup_id: str, current_user, backup_manager, integrity_checker):
    """验证备份完整性实现。"""
    try:
        verify_backup_permission(current_user)

        if not re.match(r"^[a-zA-Z0-9_-]+$", backup_id):
            log_security_event(
                "INVALID_BACKUP_ID",
                current_user,
                "verify_backup_integrity",
                {"backup_id": backup_id},
                success=False,
            )
            return error_response(message="无效的备份ID格式", error_code=ErrorCode.INVALID_PARAMETER)

        log_security_event("INTEGRITY_CHECK_START", current_user, "verify_backup_integrity", {"backup_id": backup_id})

        metadata = backup_manager._load_metadata(backup_id)
        if not metadata:
            log_security_event(
                "BACKUP_NOT_FOUND",
                current_user,
                "verify_backup_integrity",
                {"backup_id": backup_id},
                success=False,
            )
            return error_response(message=f"备份文件不存在: {backup_id}", error_code=ErrorCode.RESOURCE_NOT_FOUND)

        if metadata["database"] == "tdengine":
            is_valid, details = integrity_checker.verify_tdengine_recovery(metadata, metadata["total_rows"])
        elif metadata["database"] == "postgresql":
            is_valid, details = integrity_checker.verify_postgresql_recovery(metadata, metadata["total_rows"])
        else:
            return error_response(
                message=f"不支持的数据库类型: {metadata['database']}",
                error_code=ErrorCode.INVALID_PARAMETER,
            )

        report_file = integrity_checker.generate_integrity_report(backup_id, {"is_valid": is_valid, **details})
        integrity_result = IntegrityVerificationResult(
            backup_id=backup_id,
            is_valid=is_valid,
            verification_details=details,
            report_file_path=str(report_file),
            verification_time=datetime.now(timezone.utc).isoformat(),
        )
        log_security_event(
            "INTEGRITY_CHECK_COMPLETE",
            current_user,
            "verify_backup_integrity",
            {"backup_id": backup_id, "is_valid": is_valid, "verification_details": details},
            success=is_valid,
        )
        return success_response(data=integrity_result.model_dump(), message="备份完整性验证完成")
    except Exception as error:
        log_security_event(
            "INTEGRITY_CHECK_ERROR",
            current_user,
            "verify_backup_integrity",
            {"error": str(error), "backup_id": backup_id},
            success=False,
        )
        return error_response(
            message="备份完整性验证失败",
            error_code=ErrorCode.INTERNAL_ERROR,
            details={"backup_id": backup_id},
        )
