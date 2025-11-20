"""Compatibility wrapper for src.storage.database.db_utils"""

# 明确导入需要的函数，避免使用 import *
from src.storage.database.db_utils import (
    create_databases_safely,
    get_database_config,
)
