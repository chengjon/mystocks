"""
Compatibility module for db_manager imports.
This module re-exports from src.storage.database for backward compatibility.
"""

# Re-export all submodules
from src.storage.database import connection_manager, database_manager, db_utils

# Re-export commonly used classes
from src.storage.database.connection_manager import DatabaseConnectionManager
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

__all__ = [
    "connection_manager",
    "database_manager",
    "db_utils",
    "DatabaseConnectionManager",
    "DatabaseTableManager",
    "DatabaseType",
]
