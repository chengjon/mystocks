"""Backup integrity verification route support."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from app.api.backup_recovery_secure.backup_security_support import log_security_event
from app.core.responses import create_error_response, create_success_response


def _metadata_to_dict(metadata: Any) -> dict[str, Any]:
    if is_dataclass(metadata):
        return asdict(metadata)
    if isinstance(metadata, dict):
        return dict(metadata)
    if hasattr(metadata, "model_dump"):
        return metadata.model_dump()
    return dict(vars(metadata))


def _find_backup_metadata(backup_id: str, backup_manager: Any) -> tuple[Any | None, dict[str, Any]]:
    for metadata in backup_manager.get_backup_list():
        metadata_dict = _metadata_to_dict(metadata)
        if metadata_dict.get("backup_id") == backup_id:
            return metadata, metadata_dict
    return None, {}


def _resolve_backup_path(backup_id: str, backup_manager: Any, metadata: dict[str, Any]) -> Path:
    database = str(metadata.get("database", ""))
    if database == "postgresql":
        base_dir = Path(getattr(backup_manager, "postgresql_backup_dir"))
        candidates = [base_dir / f"{backup_id}.sql.gz", base_dir / f"{backup_id}.sql"]
    elif database == "tdengine":
        base_dir = Path(getattr(backup_manager, "tdengine_backup_dir"))
        candidates = [base_dir / f"{backup_id}.tar.gz", base_dir / backup_id]
    else:
        base_dir = Path(getattr(backup_manager, "backup_base_path", "."))
        candidates = [base_dir / backup_id, base_dir / f"{backup_id}.tar.gz", base_dir / f"{backup_id}.sql.gz"]

    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


async def verify_backup_integrity_impl(
    backup_id: str,
    current_user: Any,
    backup_manager: Any,
    integrity_checker: Any,
):
    """Verify a backup by ID using stored metadata and the configured integrity checker."""
    try:
        _metadata, metadata = _find_backup_metadata(backup_id, backup_manager)
        if not metadata:
            log_security_event(
                "BACKUP_INTEGRITY_NOT_FOUND",
                current_user,
                "verify_backup_integrity",
                {"backup_id": backup_id},
                success=False,
            )
            return create_error_response(
                error_code="NOT_FOUND",
                message="备份不存在",
                details={"backup_id": backup_id},
            )

        backup_path = _resolve_backup_path(backup_id, backup_manager, metadata)
        expected_row_count = int(metadata.get("total_rows") or 0)

        if metadata.get("database") == "tdengine" and hasattr(integrity_checker, "verify_tdengine_backup_integrity"):
            is_valid, details = integrity_checker.verify_tdengine_backup_integrity(
                str(backup_path),
                metadata,
                expected_row_count=expected_row_count,
            )
        else:
            is_valid, details = integrity_checker.verify_backup_integrity(
                str(backup_path),
                metadata,
                expected_row_count=expected_row_count,
            )

        data = {
            "backup_id": backup_id,
            "backup_path": str(backup_path),
            "valid": is_valid,
            "details": details,
        }
        log_security_event(
            "BACKUP_INTEGRITY_VERIFIED",
            current_user,
            "verify_backup_integrity",
            {"backup_id": backup_id, "valid": is_valid},
            success=is_valid,
        )
        message = "备份完整性验证通过" if is_valid else "备份完整性验证未通过"
        return create_success_response(data=data, message=message)
    except Exception as exc:
        log_security_event(
            "BACKUP_INTEGRITY_ERROR",
            current_user,
            "verify_backup_integrity",
            {"backup_id": backup_id, "error": str(exc)},
            success=False,
        )
        return create_error_response(
            error_code="INTERNAL_ERROR",
            message="备份完整性验证失败",
            details={"backup_id": backup_id, "error": str(exc)},
        )
