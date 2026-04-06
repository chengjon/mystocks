from __future__ import annotations

"""Legacy monitoring_service compatibility shim.

Single source of truth is ``src.monitoring.monitoring_database.MonitoringDatabase``.
This private module stays only to preserve historical import paths while
retiring the stale ``table_operation_log`` implementation.
"""

from dotenv import load_dotenv

from src.monitoring.monitoring_database import MonitoringDatabase

__all__ = ["MonitoringDatabase", "load_dotenv"]
