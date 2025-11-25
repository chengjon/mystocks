"""Compatibility wrapper for src.storage.database.database_manager"""

# 明确导入需要的类和函数，避免使用 import *
from src.storage.database.database_manager import (
    DatabaseTableManager,
    DatabaseType,
    TableCreationLog,
    ColumnDefinitionLog,
    TableOperationLog,
    TableValidationLog,
    Base,
)
