# Root-level entry point for backward compatibility
# Re-export from src.core

from src.core.data_classification import (
    DataClassification,
    DatabaseTarget,
    DeduplicationStrategy,
)
from src.core.data_manager import DataManager
from src.core.config_driven_table_manager import ConfigDrivenTableManager
from src.core.unified_manager import MyStocksUnifiedManager

__all__ = [
    "DataClassification",
    "DatabaseTarget",
    "DeduplicationStrategy",
    "DataManager",
    "ConfigDrivenTableManager",
    "MyStocksUnifiedManager",
]
