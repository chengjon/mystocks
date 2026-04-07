"""core - 向后兼容入口"""
import warnings
warnings.warn(
    "src.core is a compatibility shim. Import directly from src.core.{module} instead.",
    DeprecationWarning,
    stacklevel=2
)
from src.core.config_driven_table_manager import ConfigDrivenTableManager  # noqa: F401
from src.core.data_classification import DataClassification  # noqa: F401
from src.core.data_classification import DatabaseTarget  # noqa: F401
from src.core.deduplication_strategy import DeduplicationStrategy  # noqa: F401
from src.core.unified_manager import MyStocksUnifiedManager  # noqa: F401
