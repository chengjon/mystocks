"""backup_recovery_secure 拆分包"""
from fastapi import APIRouter

from .log_security_event import router as log_security_router
from .cleanup_old_backups import router as cleanup_router

from .log_security_event import log_security_event  # noqa: F401
from .log_security_event import check_backup_rate_limit  # noqa: F401
from .log_security_event import check_recovery_rate_limit  # noqa: F401
from .log_security_event import verify_admin_permission  # noqa: F401
from .log_security_event import verify_backup_permission  # noqa: F401
from .log_security_event import verify_recovery_permission  # noqa: F401
from .log_security_event import backup_tdengine_full  # noqa: F401
from .log_security_event import backup_tdengine_incremental  # noqa: F401
from .log_security_event import backup_postgresql_full  # noqa: F401
from .log_security_event import list_backups  # noqa: F401
from .log_security_event import restore_tdengine_full  # noqa: F401
from .log_security_event import restore_tdengine_pitr  # noqa: F401
from .log_security_event import restore_postgresql_full  # noqa: F401
from .log_security_event import get_recovery_objectives  # noqa: F401
from .log_security_event import scheduler_control  # noqa: F401
from .log_security_event import get_scheduled_jobs  # noqa: F401
from .log_security_event import verify_backup_integrity  # noqa: F401
from .cleanup_old_backups import cleanup_old_backups  # noqa: F401
from .cleanup_old_backups import backup_service_health  # noqa: F401

router = APIRouter(tags=["Backup & Recovery (Secure)"])
router.include_router(log_security_router)
router.include_router(cleanup_router)

__all__ = ['router', 'log_security_event', 'check_backup_rate_limit', 'check_recovery_rate_limit', 'verify_admin_permission', 'verify_backup_permission', 'verify_recovery_permission', 'backup_tdengine_full', 'backup_tdengine_incremental', 'backup_postgresql_full', 'list_backups', 'restore_tdengine_full', 'restore_tdengine_pitr', 'restore_postgresql_full', 'get_recovery_objectives', 'scheduler_control', 'get_scheduled_jobs', 'verify_backup_integrity', 'cleanup_old_backups', 'backup_service_health']
