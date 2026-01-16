# Root-level entry point for backward compatibility
# Re-export from src.data_access

from src.data_access.tdengine_access import TDengineDataAccess
from src.data_access.postgresql_access import PostgreSQLDataAccess

__all__ = [
    "TDengineDataAccess",
    "PostgreSQLDataAccess",
]
